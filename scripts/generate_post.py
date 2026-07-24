#!/usr/bin/env python3
"""
generate_post.py
Claude API ile regulatory veya OI post üretir.
Yeni postlar hem mevcut 32 yazıya hem de daha önce üretilen yeni postlara
cross-link verir (dinamik iç link sistemi).
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

CATEGORY_RELATIONS = {
    "hos-eld": ["hos-eld", "audits-violations", "maintenance"],
    "dqf": ["dqf", "audits-violations", "fmcsa-basics"],
    "maintenance": ["maintenance", "audits-violations", "hos-eld"],
    "audits-violations": ["audits-violations", "hos-eld", "dqf", "maintenance", "fmcsa-basics", "business-management"],
    "fmcsa-basics": ["fmcsa-basics", "audits-violations", "dqf", "business-management"],
    "recordkeeping": ["recordkeeping", "audits-violations", "dqf", "business-management"],
    # business-management yalnızca konusal olarak en yakın 3 kategoriye link veriyor/alıyor
    # (hos-eld, maintenance ile bilinçli olarak bağlanmıyor -- konu ilgisi zayıf)
    "business-management": ["business-management", "recordkeeping", "audits-violations", "fmcsa-basics"]
}

ETSY_CTAS = {
    "dqf": "**Build an audit-ready Driver Qualification File system:** [Driver Qualification File Bundle — The Trucker Codex](https://www.etsy.com/shop/TheTruckerCodex)",
    "hos-eld": "**Get the complete HOS compliance toolkit:** [Hours of Service Compliance Kit — The Trucker Codex](https://www.etsy.com/shop/TheTruckerCodex)",
    "maintenance": "**Inspection-ready documentation system:** [Vehicle Inspection & Maintenance Records Bundle — The Trucker Codex](https://www.etsy.com/shop/TheTruckerCodex)",
    "audits-violations": "**Prepare for your next compliance review:** [DOT Audit Preparation Bundle — The Trucker Codex](https://www.etsy.com/shop/TheTruckerCodex)",
    "fmcsa-basics": "**Complete compliance documentation system:** [DOT Compliance Starter Kit — The Trucker Codex](https://www.etsy.com/shop/TheTruckerCodex)",
    "recordkeeping": "**Litigation-grade recordkeeping system:** [DOT Recordkeeping Bundle — The Trucker Codex](https://www.etsy.com/shop/TheTruckerCodex)",
    "business-management": "**Track load-by-load income, expenses, and profitability automatically:** [Easy All-in-One Trucking Load and Expense Tracker — The Trucker Codex](https://www.etsy.com/listing/4479085412/easy-all-in-one-trucking-load-and)"
}

REGULATORY_PROMPT = """You are a technical compliance writer for The Trucker Codex (blog.thetruckercodex.com), producing expert-level content on FMCSA and DOT regulations for motor carriers, owner-operators, and compliance professionals.

Write a detailed regulatory analysis post.

Requirements:
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

EXTERNAL LINKS TO INCLUDE (minimum 2, maximum 3 — do NOT add any other external links beyond these):
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
---

[POST BODY — 900 to 1200 words]

STYLE RULES:
- Write at doctoral/professional level
- No fluff — every paragraph must contain actionable regulatory specifics
- Use H2 and H3 headers — every H2 section must have at least one H3 subsection
- The target keyword "{keyword}" must appear in at least one H2 heading
- Include at least one bullet list of 4-5 items (requirements, steps, criteria, or consequences)
- Cite CFR sections precisely (e.g., §395.3(a)(1))
- Include at least one enforcement consequence or penalty reference
- Naturally weave ALL internal links into the post body — do not dump them in a list at the end
- End with a "Regulatory Reference" footer section
- Output ONLY the Jekyll post markdown, nothing else

FOOTER:
---
*Regulatory references verified against current eCFR and FMCSA official sources. Verify applicability for your specific operation. This post does not constitute legal advice.*"""

OI_PROMPT = """You are a technical compliance analyst for The Trucker Codex (blog.thetruckercodex.com), producing enforcement intelligence content based on FMCSA, CVSA, and DOT data.

Write a detailed operational intelligence post.

Requirements:
TOPIC: {title}
TARGET KEYWORD: {keyword}
DATA SOURCE: {data_source}
CATEGORY: {category}

INTERNAL LINKS TO INCLUDE (use ALL of these as markdown links — weave naturally into body):
{internal_links}

EXTERNAL LINKS TO INCLUDE (minimum 2, maximum 3 — do NOT add any other external links beyond these):
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
---

[POST BODY — 900 to 1200 words]

STYLE RULES:
- Write at professional/expert level
- Ground every claim in enforcement data, CVSA statistics, or CFR citations
- Use H2 and H3 headers — every H2 section must have at least one H3 subsection
- The target keyword "{keyword}" must appear in at least one H2 heading
- Include at least one bullet list of 4-5 items (violation patterns, criteria, statistics, or action items)
- Include specific violation codes where applicable
- Naturally weave ALL internal links into the post body
- Analytical and direct — no platitudes
- Output ONLY the Jekyll post markdown, nothing else

FOOTER:
---
*Data sourced from {data_source} and FMCSA public records. Verify current enforcement thresholds at fmcsa.dot.gov.*"""


BUSINESS_PROMPT = """You are a technical business-management and tax-compliance writer for The Trucker Codex (blog.thetruckercodex.com), producing doctoral-level content on trucking business formation, bookkeeping, tax compliance, and load-level profitability analysis for owner-operators and small motor carriers who run their own LLC.

This is NOT a DOT/FMCSA regulatory post. Do not write about Hours of Service, ELDs, roadside inspections, or vehicle maintenance unless directly relevant to a financial/tax point. This is business-school-for-truckers content: how to legally form and run the company, keep the books, file taxes correctly, and decide whether a load is actually profitable.

Requirements:
TOPIC: {title}
PRIMARY AUTHORITY / SOURCE: {primary_authority} ({authority_url})
TARGET KEYWORD: {keyword}
CATEGORY: {category}

CRITICAL ACCURACY INSTRUCTION: {time_sensitive_instruction}

INTERNAL LINKS TO INCLUDE (use ALL of these as markdown links — weave naturally into body):
{internal_links}

EXTERNAL LINKS TO INCLUDE (minimum 2, maximum 3 — do NOT add any other external links beyond these):
- {authority_url}
- https://www.irs.gov/businesses/small-businesses-self-employed
{etsy_cta_block}

POST STRUCTURE:
---
layout: post
title: "{title}"
date: {date}
categories: {category}
description: "{meta_description}"
---

[POST BODY — 900 to 1200 words]

STYLE RULES:
- Write at doctoral/professional level — precise, technical, zero fluff, zero generic small-business platitudes
- Every paragraph must contain actionable financial, tax, or operational specifics — cite dollar figures, percentages, forms, or statute/publication numbers wherever the topic allows
- Use H2 and H3 headers — every H2 section must have at least one H3 subsection
- The target keyword "{keyword}" must appear in at least one H2 heading
- Include at least one bullet list of 4-5 items (steps, criteria, formulas, or common mistakes)
- Cite specific authorities precisely (IRS Publication/Form number, Internal Revenue Code section, FinCEN/SBA/state filing requirement, ATRI cost data) — never invent a citation
- Where the topic allows, include one worked numeric example (e.g., a cost-per-mile, break-even, or P&L calculation) using realistic illustrative figures clearly labeled as an example
- Naturally weave ALL internal links into the post body — do not dump them in a list at the end
- End with a "Professional Disclaimer" footer section
- Output ONLY the Jekyll post markdown, nothing else

FOOTER:
---
*This content is for educational purposes and does not constitute legal, tax, or accounting advice. Rules, thresholds, and deadlines referenced above are subject to change — verify current requirements with a licensed CPA, tax attorney, or the issuing agency before acting.*"""


def load_topics():
    with open(TOPICS_FILE) as f:
        return json.load(f)


def load_published():
    if os.path.exists(PUBLISHED_FILE):
        with open(PUBLISHED_FILE) as f:
            return json.load(f)
    return {"published": []}


def get_published_ids():
    """published_posts.json'daki tüm topic_id'leri set olarak döner."""
    published = load_published()
    return {p["topic_id"] for p in published.get("published", [])}


def get_next_topic(post_type, data):
    """
    published_posts.json'ı okuyarak daha önce yayınlanmış topic_id'leri kontrol eder.
    Counter nerede olursa olsun (sıfırlanmış, bozuk vb.) yayınlanmamış
    ilk topic'i seçer. Tüm topicler tükendiyse (None, -1) döner.
    """
    published_ids = get_published_ids()
    pool = data[post_type]
    start = data[f"next_{post_type}"] % len(pool)

    for i in range(len(pool)):
        idx = (start + i) % len(pool)
        topic = pool[idx]
        if topic["id"] not in published_ids:
            return topic, idx

    return None, -1  # Tüm topicler yayınlandı


def get_cross_links(current_category, current_topic_id, max_links=3):
    published = load_published()
    posts = published.get("published", [])
    if not posts:
        return []

    related_categories = CATEGORY_RELATIONS.get(current_category, [current_category])
    candidates = [
        p for p in posts
        if p.get("topic_id") != current_topic_id
        and p.get("category") in related_categories
        and p.get("url")
    ]
    candidates = list(reversed(candidates))
    same_cat = [p for p in candidates if p.get("category") == current_category]
    other_cat = [p for p in candidates if p.get("category") != current_category]
    ordered = same_cat + other_cat
    return [p["url"] for p in ordered[:max_links]]


def build_slug(title):
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)[:60]
    return slug.rstrip('-')


def build_internal_links_str(static_links, cross_links):
    all_links = list(static_links)
    for link in cross_links:
        if link not in all_links:
            all_links.append(link)
    return "\n".join(f"- {link}" for link in all_links)


def build_prompt(topic, post_type, reg_data=None):
    date_str = datetime.now().strftime("%Y-%m-%d")
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
        # Konu bazlı spesifik ürün linki varsa (etsy_url) onu kullan -- generic mağaza
        # linkinden çok daha yüksek dönüşüm sağlıyor çünkü ürün, yazının konusuyla
        # doğrudan eşleşiyor. Yoksa kategori bazlı genel CTA'ya düş.
        if topic.get("etsy_url"):
            anchor = topic.get("etsy_anchor", "Get the tool built for this exact problem:")
            product_name = topic.get("etsy_product_name", "The Trucker Codex — Etsy Shop")
            cta = f"**{anchor}** [{product_name}]({topic['etsy_url']})"
        else:
            cta = ETSY_CTAS.get(category, ETSY_CTAS["fmcsa-basics"])
        etsy_block = f"ETSY CTA (include near end of post):\n{cta}"

    if post_type == "regulatory":
        cfr_text = ""
        recent_summary = ""
        if reg_data:
            cfr_text = reg_data.get("cfr_text", "")[:4000]
            recent_summary = reg_data.get("recent_summary", "")
        meta_description = (
            f"Comprehensive analysis of {topic['title']} under 49 CFR Part {topic['cfr_part']}. "
            f"Regulatory requirements, enforcement consequences, and compliance guidance for motor carriers."
        )
        return REGULATORY_PROMPT.format(
            title=topic["title"],
            cfr_part=topic["cfr_part"],
            cfr_section=topic["cfr_section"],
            keyword=topic["keyword"],
            category=category,
            cfr_text=cfr_text or "Fetch unavailable — reference official eCFR source.",
            recent_summary=recent_summary or "No recent amendments in last 7 days.",
            internal_links=internal_links_str,
            etsy_cta_block=etsy_block,
            date=date_str,
            meta_description=meta_description
        )
    elif post_type == "business":
        meta_description = (
            f"{topic['title']}. Business formation, bookkeeping, tax compliance, and "
            f"profitability guidance for trucking LLC owners and owner-operators."
        )
        if topic.get("time_sensitive"):
            ts_instruction = (
                "This topic involves dollar thresholds, deadlines, or filing requirements that "
                "change over time or have changed recently (e.g., tax year figures, deadline dates, "
                "or a regulatory status that has been revised). Before writing, use web search to "
                "confirm the CURRENT figures/requirements as of the post date below -- do NOT rely on "
                "memorized figures, and do NOT state a specific number, deadline, or legal requirement "
                "unless you have verified it via search for the current date. If a fact cannot be "
                "verified, describe it qualitatively and point the reader to the authoritative source "
                "instead of guessing a number."
            )
        else:
            ts_instruction = (
                "This topic is largely structural/evergreen, but still verify via web search any "
                "specific dollar figure, form number, or deadline you state -- do not guess."
            )
        return BUSINESS_PROMPT.format(
            title=topic["title"],
            keyword=topic["keyword"],
            category=category,
            primary_authority=topic.get("primary_authority", "IRS Small Business and Self-Employed Tax Center"),
            authority_url=topic.get("authority_url", "https://www.irs.gov/businesses/small-businesses-self-employed"),
            time_sensitive_instruction=ts_instruction,
            internal_links=internal_links_str,
            etsy_cta_block=etsy_block,
            date=date_str,
            meta_description=meta_description
        )
    else:
        meta_description = (
            f"Enforcement intelligence analysis: {topic['title']}. "
            f"Data-driven insights from FMCSA and CVSA records for motor carriers and compliance professionals."
        )
        return OI_PROMPT.format(
            title=topic["title"],
            keyword=topic["keyword"],
            data_source=topic.get("data_source", "FMCSA Public Data"),
            data_url=topic.get("data_url", "https://www.fmcsa.dot.gov/"),
            category=category,
            internal_links=internal_links_str,
            etsy_cta_block=etsy_block,
            date=date_str,
            meta_description=meta_description
        )


def call_claude(prompt, post_type="regulatory"):
    client = anthropic.Anthropic()
    kwargs = dict(
        model="claude-sonnet-4-6",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )

    if post_type == "business":
        # Business/tax/vergi içeriği zaman duyarlı (vergi yılı rakamları, dolar eşikleri,
        # dosyalama son tarihleri, BOI gibi mevzuat durumu değişebilir). Modelin ezberden
        # eski/olası yanlış rakam üretmesini önlemek için web_search tool'unu açıyoruz --
        # tool-use turlarını karşılamak için max_tokens'ı da yükseltiyoruz.
        kwargs["max_tokens"] = 6000
        kwargs["tools"] = [{
            "type": "web_search_20260318",
            "name": "web_search",
            "max_uses": 6,
            # Arama sonuçları code execution uzerinden (dynamic filtering) tuketildiginde
            # bu agir bloklari nihai response'tan dusuruyoruz -- hem token maliyetini
            # azaltiyor hem de asagidaki metin-cikarma mantigini sadelestiriyor.
            "response_inclusion": "excluded",
        }]
        kwargs["system"] = (
            "You are a precision business-management and tax-compliance writer specializing in "
            "trucking LLC formation, bookkeeping, and profitability analysis for US owner-operators. "
            "You have web search available -- use it to verify any current dollar figure, deadline, "
            "form number, or legal requirement before stating it. Never state a specific current-year "
            "figure or deadline from memory alone. Your final output is always publication-ready Jekyll "
            "markdown. No preamble, no explanation, no description of your search process -- only the "
            "final post."
        )
    else:
        kwargs["system"] = (
            "You are a precision technical writer specializing in US federal motor carrier "
            "regulations. Your output is always publication-ready Jekyll markdown. No preamble, "
            "no explanation — only the post."
        )

    response = client.messages.create(**kwargs)
    content_blocks = list(response.content)

    # Web search acikken Claude, arama kararlarini/ozetlerini ayri "text" bloklari olarak
    # yazabiliyor (ör. "I'll search for..." bir arama cagrisindan ONCE gelen bir text
    # blogu). Tum text bloklarini kor kor birlestirmek bu on-yazi metinlerini nihai posta
    # karistiriyordu (bkz. business-post.yml run #2 -- front matter dosyanin basinda
    # cikmadi, kelime sayisi sistigi). Dogru yaklasim: SADECE en son tool-kullanim
    # blogundan SONRAKI text bloklari nihai cevabi olusturur; arama hic tetiklenmediyse
    # (regulatory/oi -- tools hic verilmiyor) tum icerik zaten tek bir text blogu olur ve
    # bu mantik onceki davranisla ayni sonucu verir.
    last_tool_idx = -1
    for i, block in enumerate(content_blocks):
        if getattr(block, "type", None) != "text":
            last_tool_idx = i

    final_blocks = content_blocks[last_tool_idx + 1:]
    text_blocks = [b.text for b in final_blocks if getattr(b, "type", None) == "text"]
    if not text_blocks:
        raise RuntimeError("Claude API response contained no text block (post_type={})".format(post_type))
    result = "".join(text_blocks).strip()

    # Ikinci bir guvenlik agi: talimata ragmen model yine de nihai text blogunun icine
    # bir on-yazi sikistirirsa, Jekyll front matter'in basladigi ilk "---" satirindan
    # itibaren kirp -- front matter dosyanin ilk karakterinden baslamak zorunda.
    fm_match = re.search(r'^---\s*$', result, re.MULTILINE)
    if fm_match and fm_match.start() > 0:
        result = result[fm_match.start():]

    return result


def extract_title_from_content(content, fallback_title):
    match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return fallback_title


def build_filename(topic):
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = build_slug(topic["title"])
    return f"_posts/{date_str}-{slug}.md"


def update_topics_index(post_type, current_idx, topics_data):
    key = f"next_{post_type}"
    topics_data[key] = (current_idx + 1) % len(topics_data[post_type])
    with open(TOPICS_FILE, "w") as f:
        json.dump(topics_data, f, indent=2)


def save_published(filename, topic):
    published = load_published()
    slug = build_slug(topic["title"])
    url = f"{BLOG_BASE}/{slug}/"
    published["published"].append({
        "file": filename,
        "topic_id": topic["id"],
        "title": topic["title"],
        "category": topic.get("category", "fmcsa-basics"),
        "url": url,
        "date": datetime.now().isoformat()
    })
    os.makedirs(os.path.dirname(PUBLISHED_FILE), exist_ok=True)
    with open(PUBLISHED_FILE, "w") as f:
        json.dump(published, f, indent=2)
    return url


def main():
    print(f"Generating {POST_TYPE} post...")
    topics_data = load_topics()
    topic, idx = get_next_topic(POST_TYPE, topics_data)

    if topic is None:
        print(f"All {POST_TYPE} topics have been published. Nothing to generate.")
        # Marker dosyasını BOŞ yazıyoruz ki quality_check.py bunu "bu çalıştırmada
        # yeni içerik üretilmedi" olarak kesin şekilde anlasın ve eski/rastgele bir
        # dosyayı yanlışlıkla denetleyip job'ı gereksiz yere düşürmesin.
        with open("/tmp/last_generated_post.txt", "w") as f:
            f.write("")
        sys.exit(0)

    print(f"Topic [{topic['id']}]: {topic['title']}")
    print(f"Category: {topic.get('category')}")

    reg_data = None
    if POST_TYPE == "regulatory" and os.path.exists(REG_DATA_FILE):
        with open(REG_DATA_FILE) as f:
            reg_data = json.load(f)

    prompt = build_prompt(topic, POST_TYPE, reg_data)
    print("Calling Claude API...")
    content = call_claude(prompt, POST_TYPE)

    filename = build_filename(topic)
    os.makedirs("_posts", exist_ok=True)
    with open(filename, "w") as f:
        f.write(content)
    print(f"Post written: {filename}")

    title = extract_title_from_content(content, topic["title"])
    with open("/tmp/post_title.txt", "w") as f:
        f.write(f"[{topic['id']}]: {title}")

    # quality_check.py'nin HANGİ dosyayı denetleyeceğini kesin olarak bilmesi için
    # (mtime tahminine güvenmek yerine, çünkü actions/checkout tüm dosya mtime'larını
    # sıfırlıyor ve bu tahmini kırılgan/yanlış kılıyor -- bkz. Temmuz 2026 kesintisi)
    with open("/tmp/last_generated_post.txt", "w") as f:
        f.write(filename)

    update_topics_index(POST_TYPE, idx, topics_data)
    url = save_published(filename, topic)
    print(f"Published log updated: {url}")
    print("Done.")


if __name__ == "__main__":
    main()
