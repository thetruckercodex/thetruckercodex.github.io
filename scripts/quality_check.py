#!/usr/bin/env python3
"""
quality_check.py
Üretilen son postu doğrular.

Kontroller:
- Front matter eksiksiz mi?
- Kelime sayısı 800–1500 arası mı?
- İç link: min 2, max 5
- Dış link: min 2, max 3
- topics.json'daki 2 zorunlu statik link yazıda var mı?
- Duplicate değil mi?
"""

import os
import re
import sys
import json
import glob

MIN_WORDS = 800
MAX_WORDS = 1500
MIN_INTERNAL = 2
MAX_INTERNAL = 5
MIN_EXTERNAL = 2
MAX_EXTERNAL = 3

PUBLISHED_FILE  = "_data/published_posts.json"
TOPICS_FILE     = "_data/topics.json"
BLOG_BASE       = "https://blog.thetruckercodex.com"

REQUIRED_FRONT_MATTER = ["layout", "title", "date", "categories", "description"]


def get_latest_post():
    posts = sorted(glob.glob("_posts/*.md"), key=os.path.getmtime, reverse=True)
    if not posts:
        print("ERROR: No posts found in _posts/")
        sys.exit(1)
    return posts[0]


def parse_front_matter(content):
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not match:
        return None, content
    fm_text = match.group(1)
    body    = content[match.end():]
    fm = {}
    for line in fm_text.split('\n'):
        if ':' in line:
            key, _, val = line.partition(':')
            fm[key.strip()] = val.strip().strip('"\'')
    return fm, body


def count_words(content):
    _, body = parse_front_matter(content)
    return len(re.findall(r'\b\w+\b', body))


def find_links(content):
    _, body = parse_front_matter(content)

    md_links   = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', body)
    all_urls   = [url for _, url in md_links]
    html_links = re.findall(r'href=["\']([^"\']+)["\']', body)
    all_urls.extend(html_links)

    internal = [
        u for u in all_urls
        if (u.startswith('/') and not u.startswith('//'))
        or BLOG_BASE in u
    ]
    external = [
        u for u in all_urls
        if u.startswith('http')
        and BLOG_BASE not in u
        and 'etsy.com' not in u          # Etsy CTA dış link sayısını şişirmesin
    ]
    return internal, external


def get_required_static_links(filepath):
    """
    Son publish edilen topic'in topics.json'daki statik 2 linkini döner.
    published_posts.json → topic_id → topics.json lookup.
    """
    if not os.path.exists(PUBLISHED_FILE) or not os.path.exists(TOPICS_FILE):
        return []

    with open(PUBLISHED_FILE) as f:
        pub_data = json.load(f)
    if not pub_data.get("published"):
        return []

    last_entry = pub_data["published"][-1]
    topic_id   = last_entry.get("topic_id", "")

    with open(TOPICS_FILE) as f:
        topics_data = json.load(f)

    for pool in ["regulatory", "oi"]:
        for topic in topics_data.get(pool, []):
            if topic.get("id") == topic_id:
                return topic.get("internal_links", [])
    return []


def check_duplicate(filepath):
    if not os.path.exists(PUBLISHED_FILE):
        return False
    with open(PUBLISHED_FILE) as f:
        data = json.load(f)
    basename = os.path.basename(filepath)
    # Son entry kendisi — öncekilerle karşılaştır
    for entry in data["published"][:-1]:
        if os.path.basename(entry.get("file", "")) == basename:
            return True
    return False


def main():
    filepath = get_latest_post()
    print(f"Quality checking: {filepath}")

    with open(filepath) as f:
        content = f.read()

    errors   = []
    warnings = []

    # ── 1. Front matter ──────────────────────────────────────────────────────
    fm, body = parse_front_matter(content)
    if fm is None:
        errors.append("CRITICAL: No valid Jekyll front matter found")
    else:
        for field in REQUIRED_FRONT_MATTER:
            if field not in fm or not fm[field]:
                errors.append(f"Front matter missing or empty: {field}")

        desc = fm.get("description", "")
        if len(desc) < 50:
            warnings.append(f"Description short: {len(desc)} chars (recommended 120–160)")

    # ── 2. Kelime sayısı ─────────────────────────────────────────────────────
    word_count = count_words(content)
    print(f"  Word count: {word_count}")
    if word_count < MIN_WORDS:
        errors.append(f"Word count too low: {word_count} (min {MIN_WORDS})")
    elif word_count > MAX_WORDS:
        errors.append(f"Word count too high: {word_count} (max {MAX_WORDS})")

    # ── 3. Link sayıları ─────────────────────────────────────────────────────
    internal_links, external_links = find_links(content)
    print(f"  Internal links: {len(internal_links)}")
    print(f"  External links: {len(external_links)}")

    if len(internal_links) < MIN_INTERNAL:
        errors.append(
            f"Internal links too few: {len(internal_links)} (min {MIN_INTERNAL})"
        )
    if len(internal_links) > MAX_INTERNAL:
        errors.append(
            f"Internal links too many: {len(internal_links)} (max {MAX_INTERNAL})"
        )
    if len(external_links) < MIN_EXTERNAL:
        errors.append(
            f"External links too few: {len(external_links)} (min {MIN_EXTERNAL})"
        )
    if len(external_links) > MAX_EXTERNAL:
        errors.append(
            f"External links too many: {len(external_links)} (max {MAX_EXTERNAL})"
        )

    # ── 4. Zorunlu statik linkler yazıda var mı? ──────────────────────────────
    required = get_required_static_links(filepath)
    if required:
        for link in required:
            # URL'nin slug kısmını içerikte ara (absolute veya relative format)
            slug = link.rstrip('/').split('/')[-1]
            if slug not in content:
                errors.append(f"Required static link missing from post body: {link}")
    else:
        warnings.append("Could not verify required static links (topics lookup failed)")

    # ── 5. Authoritative regulatory source linki ─────────────────────────────
    authoritative = ["ecfr.gov", "federalregister.gov", "fmcsa.dot.gov", "cvsa.org"]
    if not any(any(src in u for src in authoritative) for u in external_links):
        warnings.append(
            "No authoritative regulatory source linked (ecfr.gov, fmcsa.dot.gov, etc.)"
        )

    # ── 6. Disclaimer footer ──────────────────────────────────────────────────
    if ("does not constitute legal advice" not in content
            and "regulatory references" not in content.lower()):
        warnings.append("Regulatory disclaimer footer may be missing")

    # ── 7. Duplikasyon ────────────────────────────────────────────────────────
    if check_duplicate(filepath):
        errors.append(f"DUPLICATE: {filepath} already published")

    # ── 8. H3 varlığı ────────────────────────────────────────────────────────
    _, body = parse_front_matter(content)
    h3_count = len(re.findall(r'^###\s+.+', body, re.MULTILINE))
    print(f"  H3 headers: {h3_count}")
    if h3_count < 1:
        errors.append("SEO: No H3 headers found (at least 1 required under each H2)")

    # ── 9. Bullet list varlığı ────────────────────────────────────────────────
    bullet_items = re.findall(r'^[-*]\s+.{10,}', body, re.MULTILINE)
    print(f"  Bullet list items: {len(bullet_items)}")
    if len(bullet_items) < 4:
        errors.append(f"SEO: Too few bullet list items: {len(bullet_items)} (min 4 required)")

    # ── 10. Keyword H2'de geçiyor mu? ─────────────────────────────────────────
    h2_headers = re.findall(r'^##\s+(.+)', body, re.MULTILINE)
    fm_keyword = fm.get("description", "").split(".")[0].lower() if fm else ""
    # Basit kontrol: en az 1 H2 başlığı 6+ kelime içermeli (keyword-rich)
    long_h2 = [h for h in h2_headers if len(h.split()) >= 4]
    print(f"  H2 headers: {len(h2_headers)} (keyword-rich: {len(long_h2)})")
    if not long_h2:
        warnings.append("SEO: No descriptive H2 headers found (headers should be keyword-rich, 4+ words)")


    print("\n--- Quality Check Report ---")
    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  ⚠️  {w}")

    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  ❌ {e}")
        print(f"\nQuality check FAILED — {len(errors)} error(s)")
        sys.exit(1)
    else:
        print("✅ Quality check PASSED")
        print(
            f"   Words: {word_count} | "
            f"Internal: {len(internal_links)} | "
            f"External: {len(external_links)}"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
