#!/usr/bin/env python3
"""
fetch_regulations.py
eCFR API'den CFR metni çeker, Federal Register'dan son 7 günün FMCSA kurallarını tarar.
Sonuçları /tmp/reg_data.json'a yazar.
"""

import json
import os
import sys
import requests
from datetime import datetime, timedelta

ECFR_BASE = "https://ecfr.gov/api/versioner/v1"
FR_BASE = "https://www.federalregister.gov/api/v1"
OUTPUT = "/tmp/reg_data.json"
TOPICS_FILE = "_data/topics.json"


def load_today_topic():
    with open(TOPICS_FILE) as f:
        data = json.load(f)
    idx = data["next_regulatory"] % len(data["regulatory"])
    return data["regulatory"][idx], idx


def fetch_cfr_section(title, part, section):
    """eCFR API'den belirli bir section metnini çeker."""
    # Önce mevcut versiyonu al
    url = f"{ECFR_BASE}/full/{title}/chapter-III/subchapter-B/part-{part}"
    
    # Basit endpoint: section text
    section_url = f"https://www.ecfr.gov/api/versioner/v1/full/title-{title}/chapter-III/subchapter-B/part-{part}/section-{section}"
    
    try:
        r = requests.get(section_url, timeout=30)
        if r.status_code == 200:
            return r.text[:8000]  # İlk 8000 karakter
    except Exception:
        pass

    # Fallback: part-level özet
    try:
        part_url = f"https://www.ecfr.gov/api/versioner/v1/structure/title-{title}/chapter-III/subchapter-B/part-{part}"
        r = requests.get(part_url, timeout=30)
        if r.status_code == 200:
            return json.dumps(r.json())[:4000]
    except Exception:
        pass

    return f"49 CFR Part {part} Section {section} — Fetch failed, use official eCFR source."


def fetch_ecfr_text(title, part, section):
    """Ana eCFR text fetch fonksiyonu."""
    try:
        # eCFR versioner API ile section metnini al
        url = f"https://www.ecfr.gov/api/versioner/v1/full/title-{title}.json?part={part}"
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            data = r.json()
            # Section'ı bul
            text = json.dumps(data)
            # İlgili section'ı bul
            sec_marker = f'"label":"{section}"'
            idx = text.find(sec_marker)
            if idx > 0:
                return text[max(0, idx-100):idx+3000]
            return text[:5000]
    except Exception as e:
        print(f"eCFR fetch warning: {e}", file=sys.stderr)

    # Son fallback: URL formatını dene
    try:
        url = f"https://ecfr.gov/current/title-{title}/part-{part}/section-{section}"
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            return r.text[:5000]
    except Exception:
        pass

    return f"Reference: 49 CFR Part {part}, Section {section}. Fetch unavailable — verify at ecfr.gov."


def fetch_recent_fmcsa_rules():
    """Federal Register'dan son 7 günün FMCSA final rule'larını çeker."""
    since = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    params = {
        "fields[]": ["title", "document_number", "publication_date", "abstract", "action"],
        "conditions[agencies][]": "federal-motor-carrier-safety-administration",
        "conditions[type][]": ["RULE", "PRORULE"],
        "conditions[publication_date][gte]": since,
        "per_page": 5,
        "order": "newest"
    }
    try:
        r = requests.get(f"{FR_BASE}/documents.json", params=params, timeout=30)
        if r.status_code == 200:
            results = r.json().get("results", [])
            return results
    except Exception as e:
        print(f"Federal Register fetch warning: {e}", file=sys.stderr)
    return []


def main():
    topic, idx = load_today_topic()
    print(f"Fetching data for: {topic['title']}")

    cfr_text = fetch_ecfr_text(
        topic["cfr_title"],
        topic["cfr_part"],
        topic["cfr_section"]
    )

    recent_rules = fetch_recent_fmcsa_rules()
    recent_summary = ""
    if recent_rules:
        recent_summary = "Recent FMCSA Activity (last 7 days):\n"
        for rule in recent_rules:
            recent_summary += f"- {rule.get('title','')}: {rule.get('abstract','')[:200]}\n"

    output = {
        "topic": topic,
        "topic_index": idx,
        "cfr_text": cfr_text,
        "recent_rules": recent_rules,
        "recent_summary": recent_summary,
        "fetch_date": datetime.now().isoformat(),
        "cfr_reference": f"https://www.ecfr.gov/current/title-{topic['cfr_title']}/part-{topic['cfr_part']}/section-{topic['cfr_section']}"
    }

    with open(OUTPUT, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Regulatory data written to {OUTPUT}")
    print(f"CFR Reference: 49 CFR Part {topic['cfr_part']}, Section {topic['cfr_section']}")
    if recent_rules:
        print(f"Recent FMCSA rules found: {len(recent_rules)}")


if __name__ == "__main__":
    main()
