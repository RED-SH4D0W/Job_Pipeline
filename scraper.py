#!/usr/bin/env python3
"""
scraper.py - pulls jobs from public company job feeds (Greenhouse, Lever,
Ashby) and saves the ones that match your targets into Supabase.

Run it:   python3 scraper.py

It reads all its settings from config.json (which you create from
config.example.json). Nothing secret is inside this file.
"""

import json
import os
import re
import sys
import html
import requests

CONFIG_PATH = "config.json"


def load_config():
    try:
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
    except FileNotFoundError:
        sys.exit("No config.json found. Copy config.example.json to config.json and fill it in.")
    except json.JSONDecodeError as e:
        sys.exit(f"config.json has a typo (JSON error): {e}")
    # Let secrets / resume come from the environment (used by GitHub Actions),
    # overriding the file. Locally these env vars are unset, so config.json wins.
    if os.environ.get("SUPABASE_URL"):
        cfg["supabase_url"] = os.environ["SUPABASE_URL"]
    if os.environ.get("SUPABASE_KEY"):
        cfg["supabase_key"] = os.environ["SUPABASE_KEY"]
    if os.environ.get("RESUME_TEXT"):
        cfg["_resume_text"] = os.environ["RESUME_TEXT"]
    return cfg


def strip_html(s):
    """Turn an HTML job description into plain text."""
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


# ---------- One small fetcher per job-feed type ----------

def fetch_greenhouse(token):
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    out = []
    for j in r.json().get("jobs", []):
        out.append({
            "title": j.get("title", ""),
            "location": (j.get("location") or {}).get("name", ""),
            "url": j.get("absolute_url", ""),
            "description": strip_html(j.get("content", "")),
            "posted_at": j.get("updated_at"),
        })
    return out


def fetch_lever(token):
    url = f"https://api.lever.co/v0/postings/{token}?mode=json"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    out = []
    for j in r.json():
        cats = j.get("categories") or {}
        out.append({
            "title": j.get("text", ""),
            "location": cats.get("location", ""),
            "url": j.get("hostedUrl") or j.get("applyUrl", ""),
            "description": j.get("descriptionPlain", "") or strip_html(j.get("description", "")),
            "posted_at": None,
        })
    return out


def fetch_ashby(token):
    url = f"https://api.ashbyhq.com/posting-api/job-board/{token}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    out = []
    for j in r.json().get("jobs", []):
        out.append({
            "title": j.get("title", ""),
            "location": j.get("location", "") or ("Remote" if j.get("isRemote") else ""),
            "url": j.get("jobUrl") or j.get("applyUrl", ""),
            "description": j.get("descriptionPlain", "") or strip_html(j.get("descriptionHtml", "")),
            "posted_at": j.get("publishedAt"),
        })
    return out


FETCHERS = {"greenhouse": fetch_greenhouse, "lever": fetch_lever, "ashby": fetch_ashby}


# ---------- Location: is this a US (or US-remote) role? ----------

US_STATES_FULL = {
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
    "connecticut", "delaware", "florida", "hawaii", "idaho", "illinois",
    "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine", "maryland",
    "massachusetts", "michigan", "minnesota", "mississippi", "missouri",
    "montana", "nebraska", "nevada", "new hampshire", "new jersey",
    "new mexico", "new york", "north carolina", "north dakota", "ohio",
    "oklahoma", "oregon", "pennsylvania", "rhode island", "south carolina",
    "south dakota", "tennessee", "texas", "utah", "vermont", "virginia",
    "washington", "west virginia", "wisconsin", "wyoming",
    "district of columbia",
}
# Two-letter abbreviations are only trusted in "City, ST" form (comma-prefixed),
# so we don't mistake words like "in"/"or" or "Canada" for a US state.
US_STATES_ABBR = {
    "al", "ak", "az", "ar", "ca", "co", "ct", "de", "fl", "ga", "hi", "id",
    "il", "in", "ia", "ks", "ky", "la", "me", "md", "ma", "mi", "mn", "ms",
    "mo", "mt", "ne", "nv", "nh", "nj", "nm", "ny", "nc", "nd", "oh", "ok",
    "or", "pa", "ri", "sc", "sd", "tn", "tx", "ut", "vt", "va", "wa", "wv",
    "wi", "wy", "dc",
}
US_SIGNALS = [
    "united states", " usa", "usa ", "u.s.a", "u.s.", " us ", " us,", " us;",
    " us-", "-us ", "-us,", "(us)", " us)", "us remote", "remote us",
    "us-remote", "remote-us", "u.s ",
]


def is_us_location(loc):
    """True if the location clearly indicates United States (incl. US-remote).
    Blank/ambiguous locations return False so we stay strictly US-only."""
    if not loc:
        return False
    l = " " + loc.lower().strip() + " "
    if any(sig in l for sig in US_SIGNALS):
        return True
    if any(state in l for state in US_STATES_FULL):
        return True
    # "City, ST" — abbreviation must follow a comma to count as a US state.
    if any(re.search(r",\s*" + ab + r"\b", l) for ab in US_STATES_ABBR):
        return True
    return False


# ---------- Simple matching (Gemma will make this smarter later) ----------

def _present(term, text):
    """Is `term` in `text`? Plain words match on word boundaries so 'ui'
    doesn't match inside 'build'; terms with spaces/symbols (e.g. 'full
    stack', 'c#') fall back to a substring check."""
    term = term.lower()
    if re.search(r"[^a-z0-9]", term):
        return term in text
    return re.search(r"\b" + re.escape(term) + r"\b", text) is not None


def title_is_relevant(title, cfg):
    """The job TITLE must name a real dev/engineering/game role, and must NOT
    look senior. This gate keeps out unrelated jobs (ops, sales, forklift) and
    senior/lead/staff roles (you want entry / associate / 0-3 years)."""
    title = (title or "").lower()
    # Seniority words use word-boundary matching so 'lead' won't hit
    # 'leadership' and 'ii' won't hit 'hawaii'.
    if any(_present(ex, title) for ex in cfg.get("exclude_keywords", [])):
        return False
    return any(t.lower() in title for t in cfg.get("target_titles", []))


def required_years_ok(desc, max_years):
    """Drop roles asking for more than `max_years` of experience. Reads the
    numbers mentioned near the word 'experience'; if none are found, keep it
    (we don't drop a job just for being vague)."""
    if not desc:
        return True
    t = desc.lower()
    reqs = []
    for em in re.finditer(r"experience", t):
        w = t[max(0, em.start() - 60):em.end() + 25]
        for m in re.finditer(r"(\d{1,2})\s*(?:-|to|–|—)\s*\d{1,2}\s*\+?\s*(?:years?|yrs?)", w):
            reqs.append(int(m.group(1)))          # range like "2-4 years" -> 2
        for m in re.finditer(r"(\d{1,2})\s*\+\s*(?:years?|yrs?)", w):
            reqs.append(int(m.group(1)))          # "5+ years"
        for m in re.finditer(r"(\d{1,2})\s*(?:years?|yrs?)", w):
            reqs.append(int(m.group(1)))          # plain "5 years"
    return (min(reqs) <= max_years) if reqs else True


# ---------- Resume match: score jobs by overlap with YOUR resume's skills ----------

RESUME_PATH = "Resume_PG.tex"

# Skills/tech we look for. Only the ones actually present in your resume are
# used for scoring (see load_resume_skills), so this can be a broad list.
TECH_VOCAB = [
    "python", "java", "javascript", "typescript", "c#", "c++", "go", "golang",
    "rust", "kotlin", "swift", "ruby", "php", "scala", "sql",
    "react", "angular", "vue.js", "vue", "next.js", "redux", "html", "css", "tailwind",
    "node.js", "node", "express", "spring boot", "spring", "asp.net", ".net",
    "django", "flask", "fastapi", "rails",
    "rest api", "rest", "graphql", "grpc", "webhooks", "api design",
    "llm", "rag", "prompt engineering", "agentic", "machine learning", "nlp",
    "vector database", "semantic search", "embeddings", "openai", "langchain",
    "pytorch", "tensorflow", "speech-to-text", "computer vision",
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "jenkins",
    "terraform", "github actions", "microservices",
    "kafka", "event-driven", "data synchronization", "redis", "postgres",
    "postgresql", "mongodb", "elasticsearch",
    "logging", "monitoring", "observability", "debugging", "troubleshooting",
    "full stack", "full-stack", "integration", "automation", "unit testing",
    # Game development
    "unity", "unreal", "unreal engine", "godot", "c#", "c++", "opengl",
    "directx", "vulkan", "metal", "shaders", "shader", "hlsl", "glsl",
    "gameplay", "game engine", "physics", "3d", "animation", "rigging",
    "blueprint", "multiplayer", "netcode", "ar", "vr", "blender", "maya",
]


def skills_from_text(raw):
    """Return the subset of TECH_VOCAB mentioned in a resume's text (plain or LaTeX)."""
    if not raw:
        return []
    text = re.sub(r"\\([#&%$_{}])", r"\1", raw)       # unescape \# \& -> # &
    text = re.sub(r"\\[a-zA-Z]+", " ", text)          # strip LaTeX commands
    text = re.sub(r"[{}$&%~^_\\]", " ", text).lower()  # keep # + . / -
    return sorted({t.lower() for t in TECH_VOCAB if _present(t, text)})


def load_resume_skills(path=RESUME_PATH):
    """Read the resume file and return the skills it mentions."""
    try:
        with open(path) as f:
            raw = f.read()
    except FileNotFoundError:
        print(f"  ! {path} not found - resume scoring will be weak.")
        return []
    return skills_from_text(raw)


# ---------- Pull a contact + draft an email straight from the posting ----------

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")

# Generic/no-reply inboxes that aren't a real recruiter to email.
EMAIL_DENY = ["noreply", "no-reply", "donotreply", "paytransparency", "transparency",
              "accommodation", "accessibility", "privacy", "legal", "compliance",
              "security", "press", "media", "support", "abuse", "dpo", "gdpr"]


def extract_contact(description):
    """Return a *useful* email from the posting, skipping generic/legal inboxes."""
    if not description:
        return None
    for m in EMAIL_RE.finditer(description):
        addr = m.group(0)
        local = addr.split("@")[0].lower()
        if not any(bad in local for bad in EMAIL_DENY):
            return addr
    return None


def make_email_draft(title, company, contact, matched_skills):
    to_line = (f"To: {contact}\n" if contact
               else "To: (no contact in the posting — find one on the company careers page)\n")
    skills = ", ".join(matched_skills[:4]) if matched_skills else "full-stack development"
    return (
        f"{to_line}"
        f"Subject: Application for {title} - Prasant Ganesan\n\n"
        f"Hi {company} team,\n\n"
        f"I'm reaching out about the {title} role. I'm a software engineer with "
        f"experience in {skills}, and it looks like a strong fit for my background.\n\n"
        f"I'd love to share my resume and discuss how I can contribute. Thank you "
        f"for your time and consideration.\n\n"
        f"Best regards,\nPrasant Ganesan\n"
        f"ganesanprasant11@gmail.com | +1 (602) 989-9882 | linkedin.com/in/prasantganesan"
    )


def matched_skills(job, cfg):
    blob = (job["title"] or "").lower() + " " + (job["description"] or "").lower()
    return [s for s in cfg.get("_resume_skills", []) if _present(s, blob)]


def score_job(job, cfg):
    """Return a 0-100 resume-match score, or None to drop the job."""
    # US-only: drop anything not clearly in the United States.
    if cfg.get("us_only", True) and not is_us_location(job["location"]):
        return None
    # The title must name a relevant role and not look senior.
    if not title_is_relevant(job["title"], cfg):
        return None
    # Drop roles that require more experience than you have.
    if not required_years_ok(job["description"], cfg.get("max_years", 3)):
        return None

    # Score by how many of YOUR resume's skills the posting mentions.
    hits = len(matched_skills(job, cfg))
    return min(100, 35 + hits * 7)   # 35 base (relevant role) + resume overlap


# ---------- Supabase (plain REST, only needs the 'requests' library) ----------

def sb_headers(cfg):
    return {"apikey": cfg["supabase_key"], "Authorization": f"Bearer {cfg['supabase_key']}"}


def existing_urls(cfg):
    """Fetch URLs already in the table so we never insert a duplicate."""
    base = cfg["supabase_url"].rstrip("/")
    urls, offset, page = set(), 0, 1000
    while True:
        r = requests.get(
            f"{base}/rest/v1/jobs?select=url",
            headers={**sb_headers(cfg), "Range": f"{offset}-{offset + page - 1}"},
            timeout=20,
        )
        if r.status_code not in (200, 206):
            print("  ! could not read existing jobs:", r.status_code, r.text[:200])
            break
        rows = r.json()
        for row in rows:
            if row.get("url"):
                urls.add(row["url"])
        if len(rows) < page:
            break
        offset += page
    return urls


def insert_jobs(cfg, rows):
    base = cfg["supabase_url"].rstrip("/")
    headers = {**sb_headers(cfg), "Content-Type": "application/json", "Prefer": "return=minimal"}
    r = requests.post(f"{base}/rest/v1/jobs", headers=headers, data=json.dumps(rows), timeout=30)
    if r.status_code not in (200, 201, 204):
        print("  ! insert failed:", r.status_code, r.text[:300])
        return 0
    return len(rows)


# ---------- Main ----------

def main(cfg=None):
    if cfg is None:
        cfg = load_config()
    dry = cfg.get("dry_run", False)
    companies = cfg.get("companies", [])
    if not companies:
        sys.exit('No companies in config.json. Add some under "companies".')

    resume_text = cfg.get("_resume_text")
    cfg["_resume_skills"] = skills_from_text(resume_text) if resume_text else load_resume_skills()
    src = "active resume from the app" if resume_text else RESUME_PATH
    print(f"Scanning {len(companies)} companies...  (dry_run={dry})")
    print(f"Matching against {len(cfg['_resume_skills'])} skills (source: {src}).")
    seen = set() if dry else existing_urls(cfg)
    new_rows, total_fetched = [], 0

    for c in companies:
        ats, token = c.get("ats"), c.get("token")
        name = c.get("name") or token
        fetch = FETCHERS.get(ats)
        if not fetch:
            print(f"  - {name}: unknown feed type '{ats}', skipping")
            continue
        try:
            jobs = fetch(token)
        except Exception as e:
            print(f"  - {name} ({ats}:{token}): could not fetch - {e}")
            continue
        total_fetched += len(jobs)
        kept = 0
        for j in jobs:
            if not j["url"] or j["url"] in seen:
                continue
            sc = score_job(j, cfg)
            if sc is None:
                continue
            seen.add(j["url"])
            ms = matched_skills(j, cfg)
            contact = extract_contact(j["description"])
            new_rows.append({
                "source": ats, "company": name, "title": j["title"],
                "location": j["location"], "url": j["url"],
                "description": (j["description"] or "")[:6000],
                "match_score": sc, "status": "new", "posted_at": j.get("posted_at"),
                "match_reasons": ("Resume skills matched: " + ", ".join(ms)) if ms else "No direct resume-skill overlap.",
                "recruiter_email": contact,
                "email_draft": make_email_draft(j["title"], name, contact, ms),
            })
            kept += 1
        print(f"  - {name}: {len(jobs)} fetched, {kept} matched")

    print(f"\nTotal fetched: {total_fetched} | new matches to add: {len(new_rows)}")

    summary = {"companies": len(companies), "fetched": total_fetched,
               "matched": len(new_rows), "added": 0, "dry": dry}

    if dry:
        print("\ndry_run is ON - nothing was written. Top matches preview:")
        for r in sorted(new_rows, key=lambda x: -x["match_score"])[:12]:
            print(f"  [{r['match_score']:>3}] {r['company']} - {r['title']}  ({r['location']})")
        print('\nWhen this looks right, set "dry_run": false in config.json and run again.')
        return summary

    if not new_rows:
        print("Nothing new to add. (Re-running only adds jobs you don't already have.)")
        return summary

    added = 0
    for i in range(0, len(new_rows), 100):
        added += insert_jobs(cfg, new_rows[i:i + 100])
    print(f"\nAdded {added} new jobs to Supabase. Refresh your Job Console to see them.")
    summary["added"] = added
    return summary


if __name__ == "__main__":
    main()
