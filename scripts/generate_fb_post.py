#!/usr/bin/env python3
"""
generate_fb_post.py

The Trucker Codex — Facebook otomasyon pipeline'ı, Faz 2 (Metin Üretim Katmanı).

_data/fb_content_map.json içindeki slot_pattern'e göre (educational/product,
2+2 gunluk rotasyon) sıradaki içeriği seçer, Anthropic API ile Faz 2.1-2.5
kurallarına sadık bir JSON brief üretir ve _data/fb_content_map.json'daki
used/next_* alanlarını günceller.

Kalıp, The Trucker Codex Facebook sayfasında zaten yayınlanmış 2 manuel
post gözlemlenerek çıkarıldı (bkz. Faz 2.2 notu):
  - Educational post: başlık (çarpıcı ifade + iki nokta + açıklama) -> veri/
    istatistik dayanaklı giriş -> 3 alt-başlık (Label: içgörü) -> risk/sonuç
    cümlesi + yumuşak CTA -> ~15-18 hashtag, LİNK YOK.
  - Product/lead-magnet post: acı-noktası kancası + emoji -> "I put
    together a FREE/ürün X" teklifi -> "link in the first comment" CTA'sı
    (caption içinde ASLA çıplak link yok) -> etkileşim sorusu + madde
    işaretli seçenekler -> hashtag YOK.

Bu gözlem, planın Faz 2.5 kuralını (çıplak URL yasağı) doğruluyor VE önemli
bir mimari sonuç doğuruyor: ürün odaklı post'larda gerçek link, foto
post'unun caption'ında değil, hemen ardından atılan İLK YORUM'da olmalı.
Bu yüzden çıktı JSON'unda ürün post'ları için ayrı bir `link_comment` alanı
var; Faz 4 (yayın katmanı) bunu foto post'undan hemen sonra ayrı bir yorum
olarak paylaşmalı.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

import anthropic

CONTENT_MAP_FILE = "_data/fb_content_map.json"
OUTPUT_FILE = os.environ.get("FB_POST_OUTPUT", "/tmp/fb_post_draft.json")
BLOG_BASE = "https://blog.thetruckercodex.com"
ETSY_SHOP_BASE = "https://www.etsy.com/shop/TheTruckerCodex"

MODEL = "claude-sonnet-4-6"  # repo genelinde generate_post.py ile aynı model, tutarlılık için

# ---------------------------------------------------------------------------
# Kategori -> illustrasyon nesnesi (Faz 1.3'ten, görsel katmanına da beslenecek)
# ---------------------------------------------------------------------------
CATEGORY_ICON = {
    "hos-eld": "analog clock face merged with a logbook page",
    "dqf": "manila folder with a certification badge/seal",
    "maintenance": "brake disc paired with a tire tread cross-section",
    "audits-violations": "inspection clipboard with a checkmark and a red OOS tag",
    "fmcsa-basics": "open compliance handbook with a shield emblem",
    "recordkeeping": "filing cabinet drawer with a document archive box",
}

EDUCATIONAL_SYSTEM_PROMPT = """You are the social media copywriter for The Trucker Codex, a DOT/FMCSA compliance brand for owner-operators and small carriers. You write ONE Facebook post based on an existing blog article.

SOURCE ARTICLE
Title: {title}
Category: {category}
URL: {url}

LOCKED STRUCTURAL PATTERN (extracted from this Page's own published posts — follow it exactly):
1. HEADLINE: a punchy phrase, optionally followed by a colon and a short explainer of the topic. Max 6-8 words total for the punchy part.
2. SUBHEADLINE: one sentence, max 10-12 words, restates the stakes or the core tension of the topic.
3. CAPTION BODY:
   - Opens with a data- or context-driven sentence that sets up why this matters right now (no generic greetings).
   - Followed by 3-4 short sub-points, each formatted as "Label: one-sentence insight" (a category, vehicle type, violation type, or scenario relevant to the topic — pick whatever grouping makes sense for THIS topic).
   - Closes with a risk/consequence statement and a soft imperative call to action (e.g., "Audit X today", "Review your Y this week"). Do NOT use a hard sales pitch here.
4. HASHTAGS: 15-18 hashtags, mixing broad industry tags (#TruckingCompliance, #DOTCompliance, #FMCSR), niche topic tags derived from the article's specific subject, and audience tags (#TruckDrivers, #OwnerOperator, #FleetSafety). No spaces inside a tag, no punctuation.
5. ABSOLUTE RULE: The caption must NEVER contain the substrings "http", "https", or "www." — no bare links, ever. Refer to the blog only in natural language if needed (e.g., "our latest breakdown"), never with a URL.
6. Tone: authoritative, data-grounded, written for a working driver/owner-operator audience — not corporate marketing voice. First person singular ("I") is acceptable, matching this Page's existing voice.

Return ONLY a single JSON object, no markdown fences, no commentary, with EXACTLY these keys:
{{
  "headline": "...",
  "subheadline": "...",
  "bullets": ["Label: insight", "Label: insight", "Label: insight"],
  "footer_tags": ["short tag", "short tag"],
  "caption": "the full caption text exactly as it should be posted, including the closing CTA sentence but EXCLUDING the hashtag block",
  "hashtags": ["TruckingCompliance", "DOTCompliance", "..."],
  "content_type": "educational",
  "link_comment": null
}}
"""

PRODUCT_SYSTEM_PROMPT = """You are the social media copywriter for The Trucker Codex, a DOT/FMCSA compliance brand for owner-operators and small carriers. You write ONE Facebook post promoting a digital compliance product sold on Etsy.

PRODUCT
Title: {title}
Category: {category}
Price: {price}
Etsy listing URL: {etsy_url}

LOCKED STRUCTURAL PATTERN (extracted from this Page's own published posts — follow it exactly):
1. HOOK: opens with a relatable pain point or frustration a trucker/owner-operator has, ending in an ellipsis, followed by a single relevant emoji (e.g., a truck, warning, or document emoji).
2. OFFER: one sentence, first person, "I put together a [product framing] to help you [concrete benefit]." Do not say "FREE" unless the product is actually free — this product costs {price}, so frame it as a paid system/kit instead (e.g., "I put together a [kit] to help you stop guessing at [pain point].").
3. CTA LINE: exactly this style — a short sentence directing the reader to the link in the FIRST COMMENT (never a bare link in the caption). Example phrasing to adapt: "Link in the first comment 👇" or "Grab it — link in the comments 👇".
4. ENGAGEMENT HOOK: one question inviting the reader to comment (e.g., asking which part of their compliance process gives them the most trouble).
5. OPTIONS: 2-4 short bulleted options (using "•") answering that question, relevant to this product's category.
6. CLOSING: one short line inviting comments/replies.
7. ABSOLUTE RULE: The caption must NEVER contain the substrings "http", "https", or "www." — no bare links, ever, anywhere in the caption.
8. NO HASHTAGS on this post type (matches observed pattern — product posts prioritize comment engagement over hashtag discovery).
9. Tone: first person, casual-authoritative, matching a working owner-operator voice — not corporate marketing.

Return ONLY a single JSON object, no markdown fences, no commentary, with EXACTLY these keys:
{{
  "headline": "...",
  "subheadline": "...",
  "bullets": ["option 1", "option 2", "option 3"],
  "footer_tags": [],
  "caption": "the full caption text exactly as it should be posted, following the locked pattern above, with NO link inside it",
  "hashtags": [],
  "content_type": "product",
  "link_comment": "the exact text of the first comment to post immediately after the photo, containing the real Etsy link: {etsy_url}"
}}
"""


def load_content_map():
    with open(CONTENT_MAP_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_content_map(data):
    with open(CONTENT_MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def pick_next_educational(data):
    for item in data["educational"]:
        if not item["used"]:
            return item
    return None  # havuz tükendi — Faz 5'te döngü/uyarı gerekir


def pick_next_product(data):
    for item in data["product"]:
        if not item["used"]:
            return item
    return None


def validate_no_bare_url(caption: str):
    banned = ["http://", "https://", "www."]
    lowered = caption.lower()
    for token in banned:
        if token in lowered:
            raise ValueError(
                f"Caption çıplak URL/URL parçası içeriyor ('{token}') — Faz 2.5 kuralı ihlal edildi:\n{caption}"
            )


def call_claude(system_prompt: str) -> dict:
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1200,
        messages=[{"role": "user", "content": system_prompt}],
    )
    raw = response.content[0].text.strip()
    # Model bazen ```json ... ``` ile sarabilir — temizle
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


def main():
    data = load_content_map()
    slot_pattern = data["_meta"]["slot_pattern"]
    slot_index = data["next_slot_index"] % len(slot_pattern)
    slot_type = slot_pattern[slot_index]

    if slot_type == "educational":
        item = pick_next_educational(data)
        if item is None:
            print("UYARI: educational havuzu tükendi (153/153 used). Faz 5'te resetleme veya genişletme mantığı gerekli.", file=sys.stderr)
            sys.exit(1)
        prompt = EDUCATIONAL_SYSTEM_PROMPT.format(
            title=item["title"], category=item["category"], url=item["url"]
        )
    else:
        item = pick_next_product(data)
        if item is None:
            print("UYARI: product havuzu tükendi (12/12 used). Faz 5'te resetleme veya genişletme mantığı gerekli.", file=sys.stderr)
            sys.exit(1)
        prompt = PRODUCT_SYSTEM_PROMPT.format(
            title=item["title"], category=item["category"],
            price=item["price"], etsy_url=item["etsy_url"]
        )

    result = call_claude(prompt)

    # Sözleşme (contract) doğrulaması — sessiz başarısızlık yok (Faz 4.4 ilkesiyle tutarlı)
    required_keys = {"headline", "subheadline", "bullets", "footer_tags", "caption",
                      "hashtags", "content_type", "link_comment"}
    missing = required_keys - set(result.keys())
    if missing:
        raise ValueError(f"Model çıktısında eksik alan(lar): {missing}")

    validate_no_bare_url(result["caption"])
    if result["link_comment"]:
        validate_no_bare_url(result["link_comment"].replace(item.get("etsy_url", ""), ""))

    result["source_id"] = item["id"]
    result["category"] = item["category"]
    result["icon_object"] = CATEGORY_ICON[item["category"]]
    result["generated_at"] = datetime.now(timezone.utc).isoformat()

    # state güncelle
    item["used"] = True
    data["next_slot_index"] = slot_index + 1
    if slot_type == "educational":
        data["next_educational_index"] += 1
    else:
        data["next_product_index"] += 1

    save_content_map(data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"OK: {slot_type} post üretildi (id={item['id']}, category={item['category']}) -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
