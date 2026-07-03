#!/usr/bin/env python3
"""
Search Console veri cekme otomasyonu.

Amac: blog.thetruckercodex.com altindaki sayfalarin GERCEK, URL-bazli
indeksleme durumunu (URL Inspection API) ve son 90 gunun sayfa/sorgu
bazli performans verisini (Search Analytics API) cekip _data/ altina
yazmak. Bu, GSC arayuzunun sadece agregat kategori sayisi verdigi
"Coverage" raporunun aksine, HANGI URL'nin HANGI durumda oldugunu
kesin olarak ortaya koyar.

Onemli sinirlar:
- Bu script SADECE okur; hicbir icerik veya ayar degistirmez.
- GSC_SERVICE_ACCOUNT_JSON ortam degiskeni (servis hesabi JSON
  anahtarinin tam metni) olmadan calismaz; secret GitHub Actions
  tarafinda enjekte edilir, repoya asla yazilmaz/commitlenmez.
- URL Inspection API kotasi mulk basina 2.000 istek/gun ve
  600 istek/dakikadir (bkz. developers.google.com/webmaster-tools/limits).
  155 post icin 1.1 sn araliklarla cagri yapmak bu kotanin cok altinda
  kalir.
"""
import os
import sys
import json
import time
import glob
import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SITE_URL = "sc-domain:thetruckercodex.com"
BLOG_HOST = "blog.thetruckercodex.com"
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

PERF_OUT = "_data/gsc_performance.json"
INDEX_OUT = "_data/gsc_indexing.json"

INSPECT_DELAY_SEC = 1.1  # 600 istek/dk kotasinin cok altinda, guvenli marj


def load_credentials():
    raw = os.environ.get("GSC_SERVICE_ACCOUNT_JSON")
    if not raw:
        print("HATA: GSC_SERVICE_ACCOUNT_JSON ortam degiskeni bulunamadi.", file=sys.stderr)
        sys.exit(1)
    info = json.loads(raw)
    return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)


def get_all_post_urls():
    """_posts/*.md dosyalarindan gercek yayindaki tam URL'leri turetir."""
    urls = []
    for f in sorted(glob.glob("_posts/*.md")):
        with open(f, encoding="utf-8", errors="ignore") as fh:
            content = fh.read()
        permalink = None
        in_frontmatter = False
        for idx, line in enumerate(content.splitlines()):
            if idx == 0 and line.strip() == "---":
                in_frontmatter = True
                continue
            if in_frontmatter and line.strip() == "---":
                break
            if line.strip().startswith("permalink:"):
                permalink = line.split(":", 1)[1].strip().strip('"').strip("'")
                break
        if permalink:
            urls.append(f"https://{BLOG_HOST}{permalink}")
        else:
            # _config.yml default: permalink: /:title/
            base = os.path.basename(f).replace(".md", "")
            parts = base.split("-", 3)
            slug = parts[3] if len(parts) > 3 else base
            urls.append(f"https://{BLOG_HOST}/{slug}/")
    return sorted(set(urls))


def fetch_search_analytics(service):
    """Son 90 gunun sayfa- ve sorgu-bazli performans verisini ceker (sadece blog host)."""
    end = datetime.date.today()
    start = end - datetime.timedelta(days=90)

    page_filter = {
        "filters": [{
            "dimension": "page",
            "operator": "contains",
            "expression": f"https://{BLOG_HOST}/",
        }]
    }

    results = {}
    for dim in ["page", "query"]:
        rows_all = []
        start_row = 0
        while True:
            body = {
                "startDate": start.isoformat(),
                "endDate": end.isoformat(),
                "dimensions": [dim],
                "rowLimit": 25000,
                "startRow": start_row,
                "dimensionFilterGroups": [page_filter],
            }
            resp = service.searchanalytics().query(siteUrl=SITE_URL, body=body).execute()
            rows = resp.get("rows", [])
            rows_all.extend(rows)
            if len(rows) < 25000:
                break
            start_row += 25000
        results[dim] = rows_all

    return {
        "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
        "date_range": {"start": start.isoformat(), "end": end.isoformat()},
        "by_page": results["page"],
        "by_query": results["query"],
    }


def fetch_url_inspection(service, urls):
    """Her URL icin GERCEK indeksleme durumunu URL Inspection API ile ceker."""
    out = []
    for i, url in enumerate(urls):
        body = {"inspectionUrl": url, "siteUrl": SITE_URL}
        try:
            resp = service.urlInspection().index().inspect(body=body).execute()
            result = resp.get("inspectionResult", {})
            idx = result.get("indexStatusResult", {})
            out.append({
                "url": url,
                "verdict": idx.get("verdict"),
                "coverageState": idx.get("coverageState"),
                "robotsTxtState": idx.get("robotsTxtState"),
                "indexingState": idx.get("indexingState"),
                "lastCrawlTime": idx.get("lastCrawlTime"),
                "pageFetchState": idx.get("pageFetchState"),
                "googleCanonical": idx.get("googleCanonical"),
                "userCanonical": idx.get("userCanonical"),
                "sitemap": idx.get("sitemap", []),
            })
        except HttpError as e:
            out.append({"url": url, "error": str(e)})
        time.sleep(INSPECT_DELAY_SEC)
        if (i + 1) % 20 == 0:
            print(f"  ... {i + 1}/{len(urls)} URL denetlendi", file=sys.stderr)
    return {
        "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
        "total_urls": len(urls),
        "results": out,
    }


def main():
    creds = load_credentials()
    service = build("searchconsole", "v1", credentials=creds)

    print("Search Analytics verisi cekiliyor (son 90 gun, blog host)...")
    perf = fetch_search_analytics(service)
    os.makedirs("_data", exist_ok=True)
    with open(PERF_OUT, "w", encoding="utf-8") as f:
        json.dump(perf, f, ensure_ascii=False, indent=2)
    print(f"  -> {PERF_OUT} yazildi ({len(perf['by_page'])} sayfa, {len(perf['by_query'])} sorgu)")

    urls = get_all_post_urls()
    print(f"URL Inspection API ile {len(urls)} URL denetleniyor...")
    idx = fetch_url_inspection(service, urls)
    with open(INDEX_OUT, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=2)
    print(f"  -> {INDEX_OUT} yazildi")


if __name__ == "__main__":
    main()
