#!/usr/bin/env python3
"""
sync_fb_educational.py
business-post.yml tarafindan generate_post.py + quality_check.py'den SONRA calistirilir.

fb_content_map.json'daki "educational" havuzu, otomasyon kurulduguktan sonraki tek
seferlik statik bir anlik goruntuydu (153 post, sitemap+front matter'dan tek seferde
uretilmis) -- otomatik guncellenmiyordu. Diger 6 kategori icin bu sorun degil (onlarin
FB rotasyonu zaten o statik havuzdan besleniyor), ama business-management kategorisi
YENI ve sifirdan basliyor: bu script olmadan yeni business yazilari FB otomasyonuna
hicbir zaman girmez.

Bu script her yeni business yazisi yayinlandiginda (marker dosyasindan veya
published_posts.json'in son kaydindan) otomatik olarak "educational" havuzuna bir
satir ekler, boylece facebook-automation.yml bu yazilari da rotasyona alabilir.

Yalnizca category == "business-management" olan yazilar icin calisir; diger
kategoriler icin generate_post.py cagirmiyor zaten (bkz. business-post.yml).
"""
import json
import os
import sys

MARKER_FILE = "/tmp/last_generated_post.txt"
PUBLISHED_FILE = "_data/published_posts.json"
FB_MAP_FILE = "_data/fb_content_map.json"
TARGET_CATEGORY = "business-management"


def main():
    if not os.path.exists(MARKER_FILE):
        print("Marker dosyasi yok -- generate_post.py bu calistirmada hic calismamis. Atlanıyor.")
        return

    with open(MARKER_FILE) as f:
        marker_path = f.read().strip()

    if not marker_path:
        print("Marker bos -- bu calistirmada yeni yazi uretilmedi (konu havuzu tukenmis olabilir). Atlanıyor.")
        return

    if not os.path.exists(PUBLISHED_FILE):
        print("ERROR: published_posts.json bulunamadi.", file=sys.stderr)
        sys.exit(1)

    with open(PUBLISHED_FILE) as f:
        pub_data = json.load(f)

    published = pub_data.get("published", [])
    # marker_path'e karsilik gelen kaydi bul (normalde son kayit, ama saglamlik icin ariyoruz)
    entry = next((p for p in reversed(published) if p.get("file") == marker_path), None)
    if entry is None:
        print(f"ERROR: {marker_path} icin published_posts.json'da kayit bulunamadi.", file=sys.stderr)
        sys.exit(1)

    if entry.get("category") != TARGET_CATEGORY:
        print(f"Kategori '{entry.get('category')}' -- business-management degil, FB educational sync'i atlaniyor.")
        return

    with open(FB_MAP_FILE) as f:
        fb_data = json.load(f)

    already = any(e.get("url") == entry["url"] for e in fb_data["educational"])
    if already:
        print(f"Zaten fb_content_map.json'da mevcut: {entry['url']} -- atlaniyor (duplicate onlendi).")
        return

    existing_ids = [e["id"] for e in fb_data["educational"] if e["id"].startswith("E")]
    next_num = max((int(i[1:]) for i in existing_ids if i[1:].isdigit()), default=0) + 1
    new_id = f"E{next_num:03d}"

    # ONEMLI: sona (append) degil, listenin BASINA (insert 0) ekliyoruz.
    # generate_fb_post.py'deki pick_next_educational() listeyi baştan tarayip ilk
    # used=false ogeyi seciyor -- next_educational_index alani gorunuse ragmen
    # SECIMDE KULLANILMIYOR (sadece increment ediliyor, hic okunmuyor). Bu yuzden
    # sona eklenen bir oge, listenin basindaki tum eski used=false ogeler (su an
    # 129 tane) tuketilene kadar -- gunde ~2 slotla yaklasik 2 ay -- hic secilmez.
    # Yeni yayinlanan business yazisi taze ve donusum-kritik oldugu icin (Etsy CTA'ya
    # dogrudan baglaniyor), bir sonraki FB calismasinda hemen secilebilmesi icin
    # basa ekliyoruz.
    fb_data["educational"].insert(0, {
        "id": new_id,
        "url": entry["url"],
        "title": entry["title"],
        "category": entry["category"],
        "date": entry["date"][:10],
        "used": False
    })

    with open(FB_MAP_FILE, "w") as f:
        json.dump(fb_data, f, indent=2, ensure_ascii=False)

    print(f"OK: {new_id} eklendi -- {entry['title']} ({entry['url']})")


if __name__ == "__main__":
    main()
