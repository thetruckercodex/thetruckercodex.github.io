#!/usr/bin/env python3
"""
publish_fb_post.py

The Trucker Codex — Facebook otomasyon pipeline'ı, Faz 4 (Facebook Yayın
Katmanı).

Faz 3 çıktısını (varsayılan: /tmp/fb_post_draft.json — artık `image_path`
alanını da içeriyor) okuyup Meta Graph API v25.0 üzerinden
`/{page-id}/photos` endpoint'ine tek istekte foto+caption post eder.

ÜRÜN ETİKETLEME NOTU (Faz 0 / Faz 4.5'te "açık nokta" olarak işaretlenmişti,
burada KESİN OLARAK KAPATILDI): Meta'nın resmi Graph API v25.0 "Page Photos"
referans dokümanı (developers.facebook.com/docs/graph-api/reference/page/
photos) tam olarak tarandı — dokümanda "product" kelimesi hiç geçmiyor.
POST parametreleri arasındaki tek `tags` alanı KİŞİ etiketleme için
(`tag_uid`: etiketlenen kullanıcının user_id'si, `x`/`y`: koordinat,
`tag_text`: serbest metin) — bir ürün katalog ID'si kabul eden bir alan
YOK. Sonuç: Page /photos endpoint'i üzerinden native ürün etiketleme
mümkün değil. Bu yüzden ürün odaklı post'larda tek native yönlendirme
mekanizması, Faz 2'de gerçek manuel post'lardan gözlemlenen "link ilk
yorumda" kalıbıdır — bu script bunu otomatik uyguluyor (adım 2).

HATA DAVRANIŞI (Faz 4.4): Hiçbir adımda sessiz başarısızlık yok — Graph
API bir hata döndürürse (token expiry, rate limit, vs.) script exception
fırlatıp nonzero exit code ile çıkar; GitHub Actions job'u FAIL olarak
işaretlenir ve iş akışı orada durur.
"""

import json
import os
import sys
from datetime import datetime, timezone

import requests

GRAPH_API_VERSION = "v25.0"
GRAPH_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

INPUT_FILE = os.environ.get("FB_POST_INPUT", "/tmp/fb_post_draft.json")
LOG_FILE = os.environ.get("FB_PUBLISH_LOG", "/tmp/fb_publish_log.json")

FB_PAGE_ID = os.environ["FB_PAGE_ID"]
FB_PAGE_ACCESS_TOKEN = os.environ["FB_PAGE_ACCESS_TOKEN"]


class PublishError(RuntimeError):
    """Graph API'den beklenmeyen/hatalı bir yanıt geldiğinde fırlatılır.
    Bilinçli olarak yakalanmıyor — GH Actions job'unun FAIL olması isteniyor."""


def build_caption(post: dict) -> str:
    caption = post["caption"].strip()
    hashtags = post.get("hashtags") or []
    if hashtags:
        tag_line = " ".join(f"#{t}" for t in hashtags)
        return f"{caption}\n\n{tag_line}"
    return caption


def post_photo(image_path: str, caption: str) -> dict:
    url = f"{GRAPH_BASE}/{FB_PAGE_ID}/photos"
    with open(image_path, "rb") as f:
        resp = requests.post(
            url,
            data={"caption": caption, "access_token": FB_PAGE_ACCESS_TOKEN},
            files={"source": f},
            timeout=60,
        )
    body = resp.json()
    if resp.status_code != 200 or "id" not in body:
        raise PublishError(
            f"Photo post başarısız (HTTP {resp.status_code}): {json.dumps(body, ensure_ascii=False)}"
        )
    return body  # {"id": "<photo_id>", "post_id": "<page_post_id>"}


def post_comment(object_id: str, message: str) -> dict:
    url = f"{GRAPH_BASE}/{object_id}/comments"
    resp = requests.post(
        url,
        data={"message": message, "access_token": FB_PAGE_ACCESS_TOKEN},
        timeout=30,
    )
    body = resp.json()
    if resp.status_code != 200 or "id" not in body:
        raise PublishError(
            f"Yorum post başarısız (HTTP {resp.status_code}): {json.dumps(body, ensure_ascii=False)}"
        )
    return body  # {"id": "<comment_id>"}


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        post = json.load(f)

    if "image_path" not in post:
        raise PublishError("fb_post_draft.json içinde 'image_path' yok — Faz 3 (görsel üretimi) önce çalışmalı.")
    if not os.path.exists(post["image_path"]):
        raise PublishError(f"Görsel dosyası bulunamadı: {post['image_path']}")

    caption = build_caption(post)
    photo_result = post_photo(post["image_path"], caption)
    # /{page-id}/photos yanıtı bazen sadece 'id' (foto id) döndürür, 'post_id'
    # (sayfa gönderisi id'si) ayrı bir alan olabilir — yorum atarken post_id
    # varsa onu, yoksa foto id'sini kullan.
    target_id = photo_result.get("post_id", photo_result["id"])

    comment_result = None
    if post.get("content_type") == "product" and post.get("link_comment"):
        comment_result = post_comment(target_id, post["link_comment"])

    log_entry = {
        "published_at": datetime.now(timezone.utc).isoformat(),
        "source_id": post.get("source_id"),
        "content_type": post.get("content_type"),
        "category": post.get("category"),
        "photo_id": photo_result["id"],
        "post_id": photo_result.get("post_id"),
        "comment_id": comment_result["id"] if comment_result else None,
        "graph_api_version": GRAPH_API_VERSION,
    }

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log_entry, f, indent=2, ensure_ascii=False)

    print(f"OK: Facebook'a yayınlandı -> photo_id={photo_result['id']} post_id={photo_result.get('post_id')}"
          + (f" comment_id={comment_result['id']}" if comment_result else ""))


if __name__ == "__main__":
    main()
