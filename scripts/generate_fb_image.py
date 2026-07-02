#!/usr/bin/env python3
"""
generate_fb_image.py

The Trucker Codex — Facebook otomasyon pipeline'ı, Faz 3 (Görsel Üretim
Katmanı, Gemini 3 Pro Image / "Nano Banana Pro").

Faz 2 çıktısını (varsayılan: /tmp/fb_post_draft.json) okur, Faz 3.1-3.2'de
kilitlenen iki kurala harfiyen uyan bir prompt üretir, Gemini API ile 1080x1080
PNG üretir ve assets/fb-posts/ altına kaydeder.

KİLİTLİ KURALLAR (bu konuşmada n=5 ampirik testle doğrulanmış, Faz 3 notu):
  (a) Her metin alanı (headline, subheadline, bullet'lar, footer_tags) modele
      TAM OLARAK verilen string olarak geçirilir — model hiçbir alanı kendi
      "kompoze etmez"; bu, metin hatası riskini pratikte sıfıra indiriyor.
  (b) Merkezdeki illüstrasyon nesnesi (kategori ikonu) üzerinde metin/rakam
      taşıyabilecek hiçbir yüzey bırakılmaz (boş ekran, tabela, pano yok) —
      bu da hem metin hatası riskini hem kompozisyon karmaşasını azaltıyor.
  (c) Sabit renk paleti: #001830 (koyu lacivert zemin), #e8e8e8 (açık gri
      metin/kontrast yüzey), #00adb5 (teal vurgu rengi).
  (d) Flat vector infografik stili — izometrik veya 3D DEĞİL.
  (e) OCR güvenlik ağı YOK (Faz 3.5 kararı) — kısa/kesin brief standardı
      (Faz 2.1) tek başına yeterli görüldü.

API DETAYI (google-genai SDK v2.10+ kaynak koddan doğrulandı — resmi
dokümandaki bir örnek snippet'te GenerateContentConfig alanı hatalı
yazılmıştı; burada gerçek SDK'nın types.GenerateContentConfig /
types.ImageConfig alanları kullanılıyor):
  model = "gemini-3-pro-image"  (Nano Banana Pro)
  config = types.GenerateContentConfig(
      response_modalities=["TEXT", "IMAGE"],
      image_config=types.ImageConfig(aspect_ratio="1:1", image_size="2K"),
  )
API "image_size" için ayrık ön ayarlar sunuyor (512/1K/2K/4K), tam olarak
1080x1080 bir seçenek değil. Planın istediği kesin 1080x1080 çıktı için
2K (yaklaşık 2048x2048) üretilip PIL ile merkezden kırpılıp 1080x1080'e
yeniden boyutlandırılıyor.
"""

import json
import os
import sys
from io import BytesIO

from google import genai
from google.genai import types
from PIL import Image

MODEL = "gemini-3-pro-image"
TARGET_SIZE = 1080
GEN_IMAGE_SIZE = "2K"  # sonra 1080x1080'e kırpılacak

INPUT_FILE = os.environ.get("FB_POST_INPUT", "/tmp/fb_post_draft.json")
OUTPUT_DIR = "assets/fb-posts"

PALETTE = {
    "background": "#001830",
    "surface": "#e8e8e8",
    "accent": "#00adb5",
}

PROMPT_TEMPLATE = """Create a flat vector infographic-style square social media graphic for a trucking/DOT compliance brand called "The Trucker Codex." Do NOT use isometric or 3D rendering — flat vector illustration only, clean geometric shapes, generous negative space.

FIXED COLOR PALETTE (use only these three colors plus white/black for line work):
- Background: {bg} (dark navy)
- Surface/panel: {surface} (light gray)
- Accent: {accent} (teal)

LAYOUT:
- A single central illustrated icon: {icon_object}. This icon must be a clean, self-contained graphic element with NO blank screens, NO signage, NO panels, NO surfaces capable of holding text or numbers anywhere on or near it. It is purely decorative/symbolic.
- Above or beside the icon, render the following text EXACTLY as given, verbatim, in a bold sans-serif font, high contrast against the background:
  HEADLINE (largest, most prominent text): "{headline}"
  SUBHEADLINE (smaller, directly below headline): "{subheadline}"
- Below that, render these short items as a clean checklist or tag row, each EXACTLY as given, verbatim:
{bullets_block}
- If present, render these short footer tags near the bottom edge, EXACTLY as given, verbatim, in small caps or a small pill/badge shape:
{footer_tags_block}

ABSOLUTE RULES:
- Every piece of text in the final image must be one of the exact strings listed above. Do not invent, paraphrase, translate, or add any additional text, numbers, dates, URLs, logos, or watermarks anywhere in the image.
- Do not render any text at all on or inside the central icon itself.
- Square 1:1 composition, professional B2B infographic quality, suitable for a Facebook feed post.
"""


def build_prompt(post: dict) -> str:
    bullets = post.get("bullets") or []
    bullets_block = "\n".join(f'  - "{b}"' for b in bullets) if bullets else "  (none)"

    footer_tags = post.get("footer_tags") or []
    footer_tags_block = "\n".join(f'  - "{t}"' for t in footer_tags) if footer_tags else "  (none)"

    return PROMPT_TEMPLATE.format(
        bg=PALETTE["background"],
        surface=PALETTE["surface"],
        accent=PALETTE["accent"],
        icon_object=post["icon_object"],
        headline=post["headline"],
        subheadline=post["subheadline"],
        bullets_block=bullets_block,
        footer_tags_block=footer_tags_block,
    )


def center_crop_resize(img: Image.Image, size: int) -> Image.Image:
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    return img.resize((size, size), Image.LANCZOS)


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        post = json.load(f)

    prompt = build_prompt(post)

    client = genai.Client()  # GEMINI_API_KEY ortam değişkeninden otomatik okunur
    response = client.models.generate_content(
        model=MODEL,
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="1:1", image_size=GEN_IMAGE_SIZE),
        ),
    )

    image = None
    model_text = []
    for part in response.parts:
        if part.text is not None:
            model_text.append(part.text)
        elif part.inline_data is not None:
            image = part.as_image()

    if image is None:
        raise RuntimeError(
            "Gemini yanıtında görsel bulunamadı — model sadece metin döndürdü:\n"
            + "\n".join(model_text)
        )

    # types.Image (google-genai v2.10) ham baytları .image_bytes alanında tutar —
    # kaynak koddan doğrulandı (types.Image.model_fields, types.Image.save).
    pil_image = Image.open(BytesIO(image.image_bytes))
    final_image = center_crop_resize(pil_image, TARGET_SIZE)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    source_id = post.get("source_id", "unknown")
    out_path = os.path.join(OUTPUT_DIR, f"{source_id}.png")
    final_image.save(out_path, "PNG")

    post["image_path"] = out_path
    with open(INPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(post, f, indent=2, ensure_ascii=False)

    print(f"OK: görsel üretildi -> {out_path} ({final_image.size[0]}x{final_image.size[1]})")


if __name__ == "__main__":
    main()
