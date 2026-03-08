#!/usr/bin/env python3
"""
generate_post.py
Claude API ile regulatory veya OI post üretir.
Yeni postlar hem mevcut 32 yazıya hem de daha önce üretilen
yeni postlara cross-link verir (dinamik iç link sistemi).
"""

import json
import os
import sys
import re
from datetime import datetime
import anthropic

TOPICS_FILE = "_data/topics.json"
PUBLISHED_FILE = "_data/published_posts.json"
REG_DATA_FILE = "/tmp/reg_data.json"
POST_TYPE = os.environ.get("POST_TYPE", "regulatory")

BLOG_BASE = "https://blog.thetruckercodex.com"

# Kategori ilişki haritası — hangi kategoriler birbirini cross-link eder
CATEGORY_RELATIONS = {
    "hos-eld":           ["hos-eld", "audits-violations", "maintenance"],
    "dqf":               ["dqf", "audits-violations", "fmcsa-basics"],
    "maintenance":       ["maintenance", "audits-violations", "hos-eld"],
    "audits-violations": ["audits-violations", "hos-eld", "dqf", "maintenance", "fmcsa-basics"],
    "fmcsa-basics":      ["fmcsa-basics", "audits-violations", "dqf"],
    "recordkeeping":     ["recordkeeping", "audits-violations", "dqf"]
}

ETSY_CTAS = {
    "dqf": "**Build an audit-ready Driver Qualification File system:** [Driver Qualification File Bundle — The Trucker Codex](https://www.etsy.com/shop/TheTruckerCodex)",
    "hos-eld": "**Get the complete HOS compliance toolkit:** [Hours of Service Compliance Kit — The Trucker Codex](https://www.etsy.com/shop/TheTruckerCodex)",
    "maintenance": "**Inspection-ready documentation system:** [Vehicle Inspection & Maintenance Records Bundle — The Trucker Codex](https://www.etsy.com/shop/TheTruckerCodex)",
    "audits-violations": "**Prepare for your next compliance review:** [DOT Audit Preparation Bundle — The Trucker Codex](https://www.etsy.com/shop/TheTruckerCodex)",
    "fmcsa-basics": "**Complete compliance documentation system:** [DOT Compliance Starter Kit — The Trucker Codex](https://www.etsy.com/shop/TheTruckerCodex)",
    "recordkeeping": "**Litigation-grade recordkeeping system:** [DOT Recordkeeping Bundle — The Trucker Codex](https://www.etsy.com/shop/TheTruckerCodex)"
}

REGULATORY_PROMPT = """You are a technical compliance writer for The Trucker Codex (blog.thetruckercodex.com), producing expert-level content on FMCSA and DOT regulations for motor carriers, owner-operators, and compliance professionals.

Write a detailed regulatory analysis post. Requirements:

TOPIC: {title}
PRIMARY CFR REFERENCE: 49 CFR Part {cfr_part}, Section {cfr_section}
TARGET KEYWORD: {keyword}
CATEGORY: {category}

CFR SOURCE TEXT (use this as your regulatory foundation):
{cfr_text}

RECENT REGULATORY ACTIVITY:
{recent_summary}

INTERNAL LINKS TO INCLUDE (use ALL of these as markdown links — weave naturally into body):
{internal_links}

EXTERNAL LINKS TO INCLUDE (minimum 2):
- https://www.ecfr.gov/current/title-49/part-{cfr_part}/section-{cfr_section}
- https://www.fmcsa.dot.gov/

{etsy_cta_block}

POST STRUCTURE:

---
layout: post
title: "{title}"
date: {date}
categories: {category}
description: "{meta_description}"
image: /assets/images/default-compliance.png
image_alt: "{title}"
---

[POST BODY — 900 to 1200 words]

STYLE RULES:
- Write at doctoral/professional level
- No fluff — every paragraph must contain actionable regulatory specifics
- Use H2 and H3 headers
- Cite CFR sections precisely (e.g., §395.3(a)(1))
- Include at least one enforcement consequence or penalty reference
- Naturally weave ALL internal links into the post body — do not dump them in a list at the end
- End with a "Regulatory Reference" footer section
- Output ONLY the Jekyll post markdown, nothing else

FOOTER:
---
*Regulatory references verified against current eCFR and FMCSA official sources. Verify applicability for your specific operation. This post does not constitute legal advice.*"""

OI_PROMPT = """You are a technical compliance analyst for The Trucker Codex (blog.thetruckercodex.com), producing enforcement intelligence content based on FMCSA, CVSA, and DOT data.

Write a detailed operational intelligence post. Requirements:

TOPIC: {title}
TARGET KEYWORD: {keyword}
DATA SOURCE: {data_source}
CATEGORY: {category}

INTERNAL LINKS TO INCLUDE (use ALL of these as markdown links — weave naturally into body):
{internal_links}

EXTERNAL LINKS TO INCLUDE (minimum 2):
- {data_url}
- https://www.fmcsa.dot.gov/safety/data-and-statistics

{etsy_cta_block}

POST STRUCTURE:

---
layout: post
title: "{title}"
date: {date}
categories: {category}
description: "{meta_description}"
image: /assets/images/default-compliance.png
image_alt: "{title}"
---

[POST BODY — 900 to 1200 words]

STYLE RULES:
- Write at professional/expert level
- Ground every claim in enforcement data, CVSA statistics, or CFR citations
- Use H2 and H3 headers
- Include specific violation codes where applicable
- Naturally weave ALL internal links into the post body
- Analytical and direct — no platitudes
- Output ONLY the Jekyll post markdown, nothing else

FOOTER:
---
*Data sourced from {data_source} and FMCSA public records. Verify current enforcement thresholds at fmcsa.dot.gov.*"""


def load_topics():
    with open(TOPICS_FILE) as f:
        return json.load(f)


def load_published():
    if os.path.exists(PUBLISHED_FILE):
        with open(PUBLISHED_FILE) as f:
            return json.load(f)
    return {"published": []}


def get_next_topic(post_type, data):
    key = f"next_{post_type}"
    idx = data[key] % len(data[post_type])
    return data[post_type][idx], idx


def get_cross_links(current_category, current_topic_id, max_links=3):
    published = load_published()
    posts = published.get("published", [])
    if not posts:
        return []
    related_categories = CATEGORY_RELATIONS.get(current_category, [current_category])
    candidates = [p for p in posts if p.get("topic_id") != current_topic_id and p.get("category") in related_categories and p.get("url")]
    candidates = list(reversed(candidates))
    same_cat  = [p for p in candidates if p.get("category") == current_category]
    other_cat = [p for p in candidates if p.get("category") != current_category]
    return [p["url"] for p in (same_cat + other_cat)[:max_links]]


def build_slug(title):
    slug = re.sub(r'\s+', '-', re.sub(r'[^a-z0-9\s-]', '', title.lower()).strip())[:60]
    return slug.rstrip('-')


def build_internal_links_str(static_links, cross_links):
    all_links = list(static_links)
    for link in cross_links:
        if link not in all_links:
            all_links.append(link)
    return "\n".join(f"- {link}" for link in all_links)


def build_prompt(topic, post_type, reg_data=None):
    date_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    category = topic.get("category", "fmcsa-basics")
    topic_id = topic.get("id", "")
    static_links = topic.get("internal_links", [])
    cross_links = get_cross_links(category, topic_id, max_links=3)
    if cross_links:
        print(f"  Cross-links from previous auto-posts ({len(cross_links)}):")
        for cl in cross_links:
            print(f"    → {cl}")
    internal_links_str = build_internal_links_str(static_links, cross_links)
    etsy_block = ""
    if topic.get("etsy_cta", False):
        cta = ETSY_CTAS.get(category, ETSY_CTAS["fmcsa-basics"])
        etsy_block = f"ETSY CTA (include near end of post):\{cta}"
    if post_type == "regulatory":
        cfr_text = reg_data.get("cfr_text", "")[:4000] if reg_data else ""
        recent_summary = reg_data.get("recent_summary", "") if reg_data else ""
        return REGULATORY_PROMPT.format(
            title=topic["title"], cfr_part=topic["cfr_part"], cfr_section=topic["cfr_section"],
            keyword=topic["keyword"], category=category,
            cfr_text=cfr_text or "Fetch unavailable", recent_summary=recent_summary or "No recent amendments.",
            internal_links=internal_links_str, etsy_cta_block=etsy_block, date=date_str
        )
    else:
        return OI_PROMPT.format(
            title=topic["title"], keyword=topic["keyword"],
            data_source=topic.get("data_source", "FMCSA Public Data"),
            data_url=topic.get("data_url", "https://www.fmcsa.dot.gov/"),
            category=category, internal_links=internal_links_str, etsy_cta_block=etsy_block, date=date_str
        )


def call_claude(prompt):
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2500,
        system="You are a precision technical writer specializing in US federal motor carrier regulations. Your output is always publication-ready Jekyll markdown. No preamble, no explanation — only the post.",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


def extract_title_from_content(content, fallback_title):
    match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
    return match.group(1).strip() if match else fallback_title


def build_filename(topic):
    return f"_posts/{datetime.now().strftime('%Y-%m-%d')}-{build_slug(topic['title'])}.md"


def update_topics_index(post_type, current_idx, topics_data):
    topics_data[f"next_{post_type}"] = (current_idx + 1) % len(topics_data[post_type])
    with open(TOPICS_FILE, "w") as f:
        json.dump(topics_data, f, indent=2)


def save_published(filename, topic):
    published = load_published()
    url = f"{BLOG_BASE}/{build_slug(topic['title'])}/"
    published["published"].append({"file": filename, "topic_id": topic["id"], "title": topic["title"], "category": topic.get("category", "fmcsa-basics"), "url": url, "date": datetime.now().isoformat()})
    os.makedirs(os.path.dirname(PUBLISHED_FILE), exist_ok=True)
    with open(PUBLISHED_FILE, "w") as f:
        json.dump(published, f, indent=2)
    return url


def main():
    print(f"Generating {POST_TYPE} post...")
    topics_data = load_topics()
    topic, idx = get_next_topic(POST_TYPE, topics_data)
    print(f"Topic [{topic['id']}]: {topic['title']}")
    reg_data = None
    if POST_TYPE == "regulatory" and os.path.exists(REG_DATA_FILE):
        with open(REG_DATA_FILE) as f: reg_data = json.load(f)
    prompt = build_prompt(topic, POST_TYPE, reg_data)
    print("Calling Claude API...")
    content = call_claude(prompt)
    filename = build_filename(topic)
    os.makedirs("_posts", exist_ok=True)
    with open(filename, "w") as f: f.write(content)
    print(f"Post written: {filename}")
    with open("/tmp/post_title.txt", "w") as f:
        f.write(f"Auto [{topic['id']}]: {extract_title_from_content(content, topic['title'])}")
    update_topics_index(POST_TYPE, idx, topics_data)
    url = save_published(filename, topic)
    print(f"Published log updated: {url}")


if __name__ == "__main__":
    main()
