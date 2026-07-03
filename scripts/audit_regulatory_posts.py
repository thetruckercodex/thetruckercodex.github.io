#!/usr/bin/env python3
"""
audit_regulatory_posts.py

Gunluk mevzuat guncelleme denetimi.

Ne yapar:
  1. _posts/ altindaki TUM yazilari tarar (otomasyonla uretilmis olsun ya da
     olmasin), her yazinin govdesinden atifta bulundugu 49 CFR title/part/
     section referanslarini regex ile cikarir. CFR atfi sifir olan yazilar
     (or. salt istatistiksel/OI yazilar) denetim kapsami disinda kalir --
     kapsam otomatik ve icerik-temelli belirlenir, elle etiketlemeye bagimli
     degildir.
  2. _data/topics.json / _data/published_posts.json eslemesi varsa (yazi
     otomasyonla uretildiyse), oradaki resmi cfr_title/cfr_part/cfr_section
     alani ile metinden cikarilan atiflari birlestirir (union) -- hem
     yapilandirilmis hem de metin-tabanli sinyali kullanir.
  3. Yazilari YAYIN TARIHINE GORE (en eskiden en yeniye) sirali bir kuyruga
     koyar ve _data/audit_state.json icindeki imleci kullanarak HER CALISMADA
     sirayla 5 yazi isler. Kuyrugun sonuna gelince bastan baslar (mevzuat
     surekli degistigi icin denetim surekli bir dongudur).
  4. Her yazi icin:
       a) Federal Register API'den, ilgili CFR part'i degistiren, o yazinin
          son kontrol tarihinden SONRA yayinlanmis RULE/PRORULE belgelerini
          arar (conditions[cfr][title]/[part]).
       b) eCFR API'den ilgili section'in GUNCEL tam metnini ceker.
       c) Federal Register'da hicbir yeni belge YOKSA ve eCFR taramasi
          erisilemiyorsa, Claude'a hic sormadan "insufficient_data" olarak
          isaretler (kaynak yoksa TAHMIN YURUTMEZ).
       d) Sinyal varsa, mevcut yazi metni + resmi kaynak verisini Claude'a
          verip yalnizca somut, kaynaga dayali bir fark varsa
          MATERIAL_UPDATE karari vermesini ister. Emin degilse NO_CHANGE
          doner (belirsizlikte guncelleme yapilmaz).
  5. MATERIAL_UPDATE durumunda: ayri bir branch acar, yaziyi orada gunceller,
     push eder ve kaynak atiflariyla dolu bir Pull Request acar -- canli,
     Google'da indexlenmis icerige DOGRUDAN dokunmaz, insan onayi bekler.
  6. Her calistirmanin sonucu (degisiklik olsun olmasin) _data/audit_log.json
     dosyasina eklenir -- "hicbir sey yapilmadi" durumlari da denetlenebilir
     sekilde kayit altina alinir.

Ortam degiskenleri:
  ANTHROPIC_API_KEY   - Claude API anahtari (zorunlu)
  GITHUB_TOKEN        - PR acmak icin (zorunlu, Actions'ta secrets.GITHUB_TOKEN)
  GITHUB_REPOSITORY   - "owner/repo" (Actions tarafindan otomatik saglanir)
  AUDIT_BATCH_SIZE    - Gunde kac yazi kontrol edilecek (varsayilan 5)
  AUDIT_BASE_BRANCH   - PR'larin hedef alacagi ana branch (varsayilan: repo'nun mevcut branch'i)
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

import requests

# -- Sabitler ------------------------------------------------------------

POSTS_DIR = "_posts"
TOPICS_FILE = "_data/topics.json"
PUBLISHED_FILE = "_data/published_posts.json"
STATE_FILE = "_data/audit_state.json"
LOG_FILE = "_data/audit_log.json"

ECFR_BASE = "https://www.ecfr.gov/api/versioner/v1"
FR_BASE = "https://www.federalregister.gov/api/v1"

BATCH_SIZE = int(os.environ.get("AUDIT_BATCH_SIZE", "5"))
CLAUDE_MODEL = "claude-sonnet-4-6"

# Yazi govdesinden CFR atiflarini yakalamak icin desenler.
# Oncelik sirasi: acik title belirtilenler, sonra "Sec part.section" (title 49
# varsayilir, cunku bu blogdaki tum CFR icerigi 49 CFR -- FMCSA/PHMSA/RSPA
# konularidir).
CFR_PATTERNS = [
    re.compile(r'(\d{1,3})\s*C\.?\s?F\.?\s?R\.?\s*(?:Part\s*)?\xa7?\s*(\d{2,4})(?:\.(\d{1,4}))?', re.IGNORECASE),
    re.compile(r'\xa7\s*(\d{2,4})\.(\d{1,4})'),
    re.compile(r'ecfr\.gov/current/title-(\d+)/part-(\d+)/section-([\d.]+)'),
]

FR_MIN_TITLE = 40  # "49 CFR" gibi eslesmelerde title>=40 kabul ederek yanlis pozitifleri ele

DISCLAIMER_MARKERS = ("does not constitute legal advice", "regulatory references")


# -- Yardimci: JSON I/O ----------------------------------------------------

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def today_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# -- Frontmatter parse (basit, mevcut quality_check.py ile ayni yaklasim) --

def parse_front_matter(content):
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not match:
        return {}, content
    fm_text = match.group(1)
    body = content[match.end():]
    fm = {}
    for line in fm_text.split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip('"\'')
    return fm, body


# -- CFR atif cikarimi ------------------------------------------------------

def extract_cfr_citations(text):
    """Metinden {(title, part): {"count": n, "sections": {sec: count}}} doner."""
    agg = {}
    for pat in CFR_PATTERNS:
        for m in pat.finditer(text):
            g = m.groups()
            if len(g) == 3 and g[0] and g[0].isdigit() and int(g[0]) >= FR_MIN_TITLE:
                title, part, sec = g
            elif len(g) == 2:
                part, sec = g
                title = "49"
            else:
                continue
            if not part or not part.isdigit():
                continue
            key = (title, part)
            entry = agg.setdefault(key, {"count": 0, "sections": {}})
            entry["count"] += 1
            if sec and re.match(r'^\d{1,4}$', sec):
                entry["sections"][sec] = entry["sections"].get(sec, 0) + 1
    return agg


def primary_cfr_refs(agg, max_parts=2):
    """En cok atif alan (title,part) ciftlerinden en fazla max_parts tanesini,
    her biri icin en sik gecen section ile birlikte doner."""
    ordered = sorted(agg.items(), key=lambda kv: -kv[1]["count"])
    refs = []
    for (title, part), data in ordered[:max_parts]:
        sec = None
        if data["sections"]:
            sec = max(data["sections"].items(), key=lambda kv: kv[1])[0]
        refs.append({"cfr_title": title, "cfr_part": part, "cfr_section": sec})
    return refs


# -- Yazi kuyrugunu kur ------------------------------------------------------

def build_topic_lookup():
    """published_posts.json (file -> topic_id) + topics.json (topic_id -> cfr
    alanlari) uzerinden dosya adina gore resmi CFR referansini doner:
    {filename: {cfr_title,...}}"""
    published = load_json(PUBLISHED_FILE, {"published": []})
    topics = load_json(TOPICS_FILE, {"regulatory": [], "oi": []})
    topic_by_id = {t["id"]: t for t in topics.get("regulatory", []) + topics.get("oi", [])}

    lookup = {}
    for entry in published.get("published", []):
        topic = topic_by_id.get(entry.get("topic_id"))
        if topic and topic.get("cfr_part"):
            fname = os.path.basename(entry["file"])
            lookup[fname] = {
                "cfr_title": str(topic.get("cfr_title", "49")),
                "cfr_part": str(topic["cfr_part"]),
                "cfr_section": str(topic.get("cfr_section", "")).lstrip("\xa7").strip() or None,
                "topic_id": topic.get("id"),
            }
    return lookup


def build_regulatory_queue():
    """Tum _posts/*.md dosyalarini tarar, CFR atfi olanlari tarih sirasina
    gore (en eski -> en yeni) sirali bir liste olarak doner."""
    topic_lookup = build_topic_lookup()
    queue = []
    for fname in sorted(os.listdir(POSTS_DIR)):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(POSTS_DIR, fname)
        with open(fpath, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        fm, body = parse_front_matter(content)

        detected = extract_cfr_citations(body)
        declared = topic_lookup.get(fname)

        refs = primary_cfr_refs(detected, max_parts=2) if detected else []
        if declared:
            already = any(
                r["cfr_title"] == declared["cfr_title"] and r["cfr_part"] == declared["cfr_part"]
                for r in refs
            )
            if not already:
                refs.insert(0, declared)
            elif declared.get("cfr_section"):
                for r in refs:
                    if r["cfr_title"] == declared["cfr_title"] and r["cfr_part"] == declared["cfr_part"]:
                        r["cfr_section"] = r["cfr_section"] or declared["cfr_section"]

        if not refs:
            continue  # CFR atfi yok -> kapsam disi (regulatory degil)

        date_str = fm.get("date", "") or fname[:10]
        queue.append({
            "file": fpath,
            "filename": fname,
            "title": fm.get("title", fname),
            "date": date_str,
            "category": fm.get("categories", ""),
            "topic_id": declared.get("topic_id") if declared else None,
            "cfr_refs": refs,
        })

    queue.sort(key=lambda p: (p["date"], p["filename"]))
    return queue


# -- State -------------------------------------------------------------------

def load_state():
    return load_json(STATE_FILE, {"cursor": 0, "cycle": 1, "posts": {}, "updated_at": None})


def save_state(state):
    state["updated_at"] = now_iso()
    save_json(STATE_FILE, state)


def select_batch(queue, state):
    n = len(queue)
    if n == 0:
        return [], 0, state.get("cycle", 1)
    cursor = state.get("cursor", 0) % n
    batch = []
    idx = cursor
    wrapped = False
    for _ in range(min(BATCH_SIZE, n)):
        batch.append(queue[idx])
        idx = (idx + 1) % n
        if idx == 0:
            wrapped = True
    cycle = state.get("cycle", 1) + (1 if wrapped else 0)
    return batch, idx, cycle


# -- Federal Register / eCFR sorgulari ---------------------------------------

def fetch_fr_documents_for_part(cfr_title, cfr_part, since_date):
    """FMCSA/PHMSA'nin belirli bir CFR part'ini degistiren, since_date'ten
    SONRA yayinlanmis resmi kural belgelerini doner. Kaynaga ulasilamazsa
    None doner (bos liste ile None'i ayirt etmek kritik: bos liste =
    'kontrol edildi, yeni belge yok'; None = 'kontrol edilemedi')."""
    params = {
        "fields[]": [
            "title", "document_number", "publication_date", "type",
            "abstract", "html_url", "action", "effective_on",
        ],
        "conditions[cfr][title]": cfr_title,
        "conditions[cfr][part]": cfr_part,
        "conditions[publication_date][gte]": since_date,
        "conditions[type][]": ["RULE", "PRORULE"],
        "per_page": 20,
        "order": "newest",
    }
    try:
        r = requests.get(f"{FR_BASE}/documents.json", params=params, timeout=30)
        if r.status_code == 200:
            return r.json().get("results", [])
        print(f"  Federal Register API HTTP {r.status_code}", file=sys.stderr)
    except requests.RequestException as e:
        print(f"  Federal Register fetch error: {e}", file=sys.stderr)
    return None


def fetch_ecfr_current_text(cfr_title, cfr_part, cfr_section):
    """Guncel eCFR section metnini (mevcutsa) ve kaynak URL'sini doner.
    fetch_regulations.py ile ayni fallback zincirini kullanir."""
    if cfr_section:
        source_url = f"https://www.ecfr.gov/current/title-{cfr_title}/part-{cfr_part}/section-{cfr_part}.{cfr_section}"
    else:
        source_url = f"https://www.ecfr.gov/current/title-{cfr_title}/part-{cfr_part}"

    if cfr_section:
        try:
            url = f"https://www.ecfr.gov/api/versioner/v1/full/title-{cfr_title}.json?part={cfr_part}"
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                text = json.dumps(r.json())
                marker = f'"label":"{cfr_section}"'
                idx = text.find(marker)
                if idx > 0:
                    return text[max(0, idx - 200):idx + 4000], source_url
                return text[:5000], source_url
        except requests.RequestException as e:
            print(f"  eCFR fetch error: {e}", file=sys.stderr)

    try:
        struct_url = f"{ECFR_BASE}/structure/{today_iso()}/title-{cfr_title}.json?part={cfr_part}"
        r = requests.get(struct_url, timeout=30)
        if r.status_code == 200:
            return json.dumps(r.json())[:4000], source_url
    except requests.RequestException as e:
        print(f"  eCFR structure fetch error: {e}", file=sys.stderr)

    return None, source_url


# -- Claude degerlendirmesi ---------------------------------------------------

ASSESS_SYSTEM = (
    "You are a senior regulatory compliance editor specializing in US federal "
    "motor carrier law (49 CFR, FMCSA, PHMSA). You audit already-published blog "
    "posts against fresh primary-source data. You are extremely conservative: "
    "you only flag MATERIAL_UPDATE when the supplied source data contains a "
    "CONCRETE, SPECIFIC change (a new final/interim rule, an amendment, a "
    "revocation, a new effective date, a changed numeric threshold, a new "
    "compliance deadline, a redesignated or removed section, etc.) that is not "
    "already reflected in the post. If the source data is ambiguous, missing, "
    "unreachable, or only tangentially related, you MUST return NO_CHANGE -- "
    "never speculate or infer a change that isn't explicitly evidenced in the "
    "provided source text. When in doubt, NO_CHANGE."
)

ASSESS_PROMPT_TEMPLATE = """CURRENT PUBLISHED POST (Jekyll markdown, full file):
<<<POST_START>>>
{post_content}
<<<POST_END>>>

CFR REFERENCE(S) BEING AUDITED: {cfr_refs_str}

FEDERAL REGISTER DOCUMENTS PUBLISHED SINCE {since_date} THAT AMEND THIS CFR PART:
{fr_documents_str}

CURRENT ECFR SECTION TEXT (fetched live just now):
{ecfr_text}

TASK:
Compare the post's regulatory claims against the source data above. Determine
whether there is a concrete official change (new rule, amendment, revocation,
new deadline/threshold, redesignation, etc.) that the post does NOT currently
reflect.

Respond in EXACTLY this format, nothing else:

VERDICT: NO_CHANGE
REASONING: <one paragraph explaining why nothing warrants an update>

-- OR, only if a concrete change is evidenced --

VERDICT: MATERIAL_UPDATE
REASONING: <what specifically changed, citing the FR document number or eCFR amendment>
CHANGE_SUMMARY: <1-2 sentence summary suitable for a pull request description>
SOURCES:
- <url1>
- <url2>
---UPDATED_POST_START---
<the FULL revised Jekyll post file: front matter + body, preserving the
existing structure, tone, internal links, and disclaimer footer, modified
ONLY where the regulatory facts require it. Add a line near the footer noting
the verification date and the specific source (e.g. "Last verified against
eCFR/Federal Register on {today}; updated to reflect [specific FR document
number / effective date].")>
---UPDATED_POST_END---
"""


def call_claude_assess(post_content, cfr_refs, fr_documents, ecfr_text, since_date):
    import anthropic

    cfr_refs_str = "; ".join(
        f"49 CFR Part {r['cfr_part']}" + (f" Sec {r['cfr_part']}.{r['cfr_section']}" if r.get("cfr_section") else "")
        for r in cfr_refs
    )
    if fr_documents:
        fr_documents_str = "\n".join(
            f"- [{d.get('type')}] {d.get('title')} (doc #{d.get('document_number')}, "
            f"published {d.get('publication_date')}, effective {d.get('effective_on')}): "
            f"{(d.get('abstract') or '')[:400]} -- {d.get('html_url')}"
            for d in fr_documents
        )
    else:
        fr_documents_str = "(none found)"

    prompt = ASSESS_PROMPT_TEMPLATE.format(
        post_content=post_content,
        cfr_refs_str=cfr_refs_str,
        since_date=since_date,
        fr_documents_str=fr_documents_str,
        ecfr_text=(ecfr_text or "(eCFR fetch unavailable)")[:4000],
        today=today_iso(),
    )

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=4000,
        system=ASSESS_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def parse_assessment(text):
    verdict_m = re.search(r'VERDICT:\s*(NO_CHANGE|MATERIAL_UPDATE)', text)
    verdict = verdict_m.group(1) if verdict_m else "NO_CHANGE"

    reasoning_m = re.search(r'REASONING:\s*(.+?)(?:\nCHANGE_SUMMARY:|---UPDATED_POST_START---|\Z)', text, re.DOTALL)
    reasoning = reasoning_m.group(1).strip() if reasoning_m else text.strip()[:800]

    result = {"verdict": verdict, "reasoning": reasoning}

    if verdict == "MATERIAL_UPDATE":
        cs_m = re.search(r'CHANGE_SUMMARY:\s*(.+?)(?:\nSOURCES:|---UPDATED_POST_START---)', text, re.DOTALL)
        result["change_summary"] = cs_m.group(1).strip() if cs_m else ""

        src_m = re.search(r'SOURCES:\s*(.+?)---UPDATED_POST_START---', text, re.DOTALL)
        sources = []
        if src_m:
            sources = [l.strip("- ").strip() for l in src_m.group(1).splitlines() if l.strip().startswith("-")]
        result["sources"] = sources

        body_m = re.search(r'---UPDATED_POST_START---\n(.*?)\n---UPDATED_POST_END---', text, re.DOTALL)
        result["updated_content"] = body_m.group(1) if body_m else None
        if not result["updated_content"]:
            # Guvenli taraf: govde cikarilamadiysa guncelleme yapma.
            result["verdict"] = "NO_CHANGE"
            result["reasoning"] += " [PARSE_ERROR: updated content block missing, downgraded to NO_CHANGE]"

    return result


def ensure_last_modified_at(content, date_str):
    """Frontmatter'a last_modified_at alanini ekler/gunceller.

    Bu alan olmadan minimal-mistakes temasi dateModified schema.org meta
    etiketini HIC render etmiyor (bkz. _layouts/single.html) ve
    jekyll-sitemap'in urettigi sitemap.xml'deki <lastmod> orijinal yayin
    tarihinde kaliyor (bkz. jekyll-sitemap README, oncelik sirasi: 1) sadece
    GitHub Pages ile uyumsuz jekyll-last-modified-at eklentisi, 2)
    last_modified_at front matter, 3) fallback post.date). GitHub Pages bu
    repoda kullanildigi icin (1) devre disi -- last_modified_at set
    edilmezse Google'a hicbir gercek guncelleme sinyali gitmiyor.
    """
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not match:
        return content  # frontmatter yoksa dokunma

    fm_block = match.group(1)
    rest = content[match.end():]

    if re.search(r'^last_modified_at\s*:', fm_block, re.MULTILINE):
        fm_block = re.sub(
            r'^last_modified_at\s*:.*$',
            f'last_modified_at: {date_str}',
            fm_block, flags=re.MULTILINE,
        )
    else:
        lines = fm_block.split("\n")
        insert_at = len(lines)
        for i, line in enumerate(lines):
            if re.match(r'^date\s*:', line):
                insert_at = i + 1
                break
        lines.insert(insert_at, f'last_modified_at: {date_str}')
        fm_block = "\n".join(lines)

    return f"---\n{fm_block}\n---\n{rest}"


# -- Git / GitHub PR -----------------------------------------------------------

def run_git(args, **kwargs):
    subprocess.run(["git"] + args, check=True, **kwargs)


def get_base_branch():
    override = os.environ.get("AUDIT_BASE_BRANCH")
    if override:
        return override
    out = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return out.decode().strip()


def check_pr_state(repo, token, pr_number):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    r = requests.get(f"https://api.github.com/repos/{repo}/pulls/{pr_number}", headers=headers, timeout=30)
    if r.status_code == 200:
        return r.json().get("state")  # "open" | "closed"
    return None


def open_pull_request(repo, token, branch, base, title, body):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    r = requests.post(
        f"https://api.github.com/repos/{repo}/pulls",
        json={"title": title, "head": branch, "base": base, "body": body},
        headers=headers, timeout=30,
    )
    r.raise_for_status()
    return r.json()


def create_update_pr(post, assessment, base_branch, repo, token):
    slug = post["filename"].rsplit(".", 1)[0]
    branch = f"audit/{slug}"[:60]

    run_git(["fetch", "origin", base_branch])
    run_git(["checkout", base_branch])
    run_git(["checkout", "-B", branch, f"origin/{base_branch}"])

    updated_content = ensure_last_modified_at(assessment["updated_content"], today_iso())
    with open(post["file"], "w", encoding="utf-8") as f:
        f.write(updated_content)

    run_git(["config", "user.email", "action@github.com"])
    run_git(["config", "user.name", "Trucker Codex Regulatory Auditor"])
    run_git(["add", post["file"]])
    run_git(["commit", "-m", f"Audit: update {post['filename']} -- {assessment.get('change_summary', '')[:72]}"])
    run_git(["push", "-u", "origin", branch, "--force"])

    sources_md = "\n".join(f"- {s}" for s in assessment.get("sources", [])) or "- (see reasoning below)"
    cfr_list_str = ", ".join(f"49 CFR Part {r['cfr_part']}" for r in post["cfr_refs"])
    pr_body = (
        f"**Automated regulatory audit -- official source change detected.**\n\n"
        f"**File:** `{post['file']}`\n"
        f"**CFR reference(s) audited:** {cfr_list_str}\n\n"
        f"**Change summary:**\n{assessment.get('change_summary', '(see reasoning)')}\n\n"
        f"**Reasoning:**\n{assessment['reasoning']}\n\n"
        f"**Sources:**\n{sources_md}\n\n"
        f"---\n*Bu PR otomatik olarak acildi. Yayinlamadan once mevzuat referanslarini "
        f"resmi kaynaklardan (eCFR / Federal Register) dogrulayip incele.*"
    )

    pr = open_pull_request(
        repo, token, branch, base_branch,
        title=f"Regulatory audit: update {post['title']}",
        body=pr_body,
    )

    run_git(["checkout", base_branch])
    return pr, branch


# -- Ana akis ------------------------------------------------------------------

def main():
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        print("GITHUB_TOKEN / GITHUB_REPOSITORY not set -- PR acma devre disi, sadece rapor uretilecek.", file=sys.stderr)

    base_branch = get_base_branch()
    queue = build_regulatory_queue()
    state = load_state()

    if not queue:
        print("Denetlenecek regulatory (CFR atifli) yazi bulunamadi.")
        return

    batch, new_cursor, new_cycle = select_batch(queue, state)
    print(f"Cycle {state.get('cycle', 1)} | Kuyruk uzunlugu: {len(queue)} | Bu calismada kontrol edilecek: {len(batch)}")

    log_entries = []

    for post in batch:
        print(f"\n--- {post['filename']} ---")
        print(f"  CFR refs: {post['cfr_refs']}")

        post_state = state["posts"].get(post["filename"], {})
        since_date = post_state.get("last_checked_date") or post["date"][:10]

        pending_pr = post_state.get("open_pr_number")
        if pending_pr and token and repo:
            pr_state = check_pr_state(repo, token, pending_pr)
            if pr_state == "open":
                print(f"  Bekleyen PR hala acik (#{pending_pr}), bu dongude atlaniyor.")
                log_entries.append({
                    "timestamp": now_iso(), "file": post["filename"], "status": "pending_pr",
                    "pr_number": pending_pr,
                })
                continue
            else:
                post_state["open_pr_number"] = None

        primary = post["cfr_refs"][0]
        fr_docs = fetch_fr_documents_for_part(primary["cfr_title"], primary["cfr_part"], since_date)
        ecfr_text, ecfr_source_url = fetch_ecfr_current_text(
            primary["cfr_title"], primary["cfr_part"], primary.get("cfr_section")
        )

        if fr_docs is None and ecfr_text is None:
            print("  Kaynaklara ulasilamadi -- TAHMIN YURUTULMEDI, manuel inceleme icin isaretlendi.")
            status = "insufficient_data"
            log_entries.append({
                "timestamp": now_iso(), "file": post["filename"], "status": status,
                "cfr_refs": post["cfr_refs"],
            })
            post_state["last_result"] = status
            state["posts"][post["filename"]] = post_state
            continue

        fr_docs = fr_docs or []

        if not fr_docs:
            print(f"  Federal Register: {since_date} sonrasi yeni kural yok.")
        else:
            print(f"  Federal Register: {len(fr_docs)} yeni belge bulundu.")

        with open(post["file"], encoding="utf-8") as f:
            post_content = f.read()

        assessment = None
        if fr_docs or ecfr_text:
            raw = call_claude_assess(post_content, post["cfr_refs"], fr_docs, ecfr_text, since_date)
            assessment = parse_assessment(raw)
            print(f"  Claude verdict: {assessment['verdict']}")

        if assessment and assessment["verdict"] == "MATERIAL_UPDATE" and token and repo:
            try:
                pr, branch = create_update_pr(post, assessment, base_branch, repo, token)
                status = "updated"
                print(f"  PR acildi: {pr.get('html_url')}")
                post_state["open_pr_number"] = pr.get("number")
                log_entries.append({
                    "timestamp": now_iso(), "file": post["filename"], "status": status,
                    "pr_url": pr.get("html_url"), "change_summary": assessment.get("change_summary"),
                    "sources": assessment.get("sources"),
                })
            except subprocess.CalledProcessError as e:
                print(f"  HATA: git islemi basarisiz: {e}", file=sys.stderr)
                status = "error"
                log_entries.append({
                    "timestamp": now_iso(), "file": post["filename"], "status": status, "error": str(e),
                })
                try:
                    run_git(["checkout", base_branch])
                except subprocess.CalledProcessError:
                    pass
        elif assessment and assessment["verdict"] == "MATERIAL_UPDATE":
            status = "material_update_detected_no_pr_credentials"
            log_entries.append({
                "timestamp": now_iso(), "file": post["filename"], "status": status,
                "reasoning": assessment["reasoning"],
            })
        else:
            status = "no_change"
            reasoning = assessment["reasoning"] if assessment else "No source signal found since last check."
            log_entries.append({
                "timestamp": now_iso(), "file": post["filename"], "status": status, "reasoning": reasoning,
            })

        post_state["last_checked_date"] = today_iso()
        post_state["last_result"] = status
        state["posts"][post["filename"]] = post_state

    state["cursor"] = new_cursor
    state["cycle"] = new_cycle
    save_state(state)

    log = load_json(LOG_FILE, {"runs": []})
    log["runs"].append({"run_date": now_iso(), "entries": log_entries})
    save_json(LOG_FILE, log)

    print(f"\nDone. {len(log_entries)} yazi islendi.")


if __name__ == "__main__":
    main()
