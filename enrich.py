#!/usr/bin/env python3
"""
enrich.py - uses your LOCAL Gemma model (served by LM Studio) to, for each new
job:  (1) give it a real fit score + a short reason, and  (2) write a tailored
version of your resume into the `tailored_resume` column.

Run it AFTER scraper.py (run_pipeline.sh does both for you). It reads its
settings from the "gemma" section of config.json and your master resume from
Resume_PG.tex. Only needs the 'requests' library.

TAILORING RULE (enforced in the prompt): Gemma may rewrite the summary, bullet
wording, skills, ordering and emphasis to fit the job. It must NOT change
contact info, education, company names, job titles, or employment dates, and
must NEVER invent experience or skills - reframe truthfully only.
"""

import json
import re
import sys
import requests
from scraper import load_config, sb_headers

RESUME_PATH = "Resume_PG.tex"


def read_resume():
    try:
        with open(RESUME_PATH) as f:
            return f.read()
    except FileNotFoundError:
        sys.exit(f"No {RESUME_PATH} found - put your master resume in this folder.")


def gemma_chat(g, messages, max_tokens, temperature):
    """One call to the local LM Studio server (OpenAI-compatible API)."""
    url = g["base_url"].rstrip("/") + "/chat/completions"
    payload = {
        "model": g.get("model", ""),
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    r = requests.post(url, json=payload, timeout=g.get("timeout", 300))
    r.raise_for_status()
    msg = r.json()["choices"][0]["message"]
    # Some models leave `content` empty and put text in a reasoning field.
    content = (msg.get("content") or "").strip()
    if not content:
        content = (msg.get("reasoning_content") or msg.get("reasoning") or "").strip()
    return content


def score_with_gemma(g, resume, job):
    sysmsg = (
        "You rate how well a candidate fits a job for an ENTRY-LEVEL / 0-3 year "
        "software or game developer. Reply with EXACTLY ONE line in this format "
        "and nothing else:\nSCORE=<integer 0-100> | REASON=<one short sentence>"
    )
    usr = (
        f"CANDIDATE RESUME:\n{resume[:6000]}\n\n"
        f"JOB: {job.get('title','')} at {job.get('company','')}\n"
        f"LOCATION: {job.get('location','')}\n"
        f"DESCRIPTION:\n{(job.get('description') or '')[:4000]}"
    )
    out = gemma_chat(g, [{"role": "system", "content": sysmsg},
                         {"role": "user", "content": usr}], max_tokens=800, temperature=0.2)
    return _parse_score(out)


def _parse_score(out):
    """Pull a 0-100 score (+ short reason) out of the model's reply. Tries the
    SCORE=.. | REASON=.. format first, then JSON, then any number near 'score'."""
    txt = re.sub(r"<think>.*?</think>", " ", out or "", flags=re.S)  # drop reasoning blocks

    ms = re.search(r"score\s*[=:]\s*(\d{1,3})", txt, re.I)
    mr = re.search(r"reason\w*\s*[=:]\s*(.+)", txt, re.I)
    if ms:
        reason = (mr.group(1).strip().strip('"|').strip() if mr else "")[:500]
        return max(0, min(100, int(ms.group(1)))), reason

    m = re.search(r"\{.*\}", txt, re.S)               # JSON fallback
    if m:
        try:
            d = json.loads(m.group(0))
            if d.get("score") is not None:
                sc = int(re.search(r"\d{1,3}", str(d["score"])).group(0))
                return max(0, min(100, sc)), str(d.get("reasons", "")).strip()[:500]
        except Exception:
            pass

    ms = re.search(r"score\D{0,6}(\d{1,3})", txt, re.I)  # loose fallback
    if ms:
        return max(0, min(100, int(ms.group(1)))), ""

    print("    (debug) could not read a score. Raw model reply was:", repr((out or "")[:300]))
    return None, None


def tailor_with_gemma(g, resume, job):
    sysmsg = (
        "You tailor a resume to one specific job. You MAY rewrite the summary, "
        "bullet wording, skills, ordering and emphasis to fit the job. You MUST "
        "NOT change contact info, education, company names, job titles, or "
        "employment dates, and MUST NOT invent any experience, skill, or metric "
        "not in the original. Reframe truthfully only. Keep the same LaTeX format "
        "and one page. Output ONLY the resume, no commentary."
    )
    usr = (
        f"ORIGINAL RESUME (LaTeX):\n{resume}\n\n"
        f"TARGET JOB: {job.get('title','')} at {job.get('company','')}\n"
        f"DESCRIPTION:\n{(job.get('description') or '')[:4000]}"
    )
    out = gemma_chat(g, [{"role": "system", "content": sysmsg},
                         {"role": "user", "content": usr}], max_tokens=3000, temperature=0.4)
    # Strip any hidden reasoning so only the resume is saved.
    return re.sub(r"<think>.*?</think>", "", out, flags=re.S).strip()


def fetch_todo(cfg, limit):
    """Jobs that don't have a tailored resume yet (highest match first)."""
    base = cfg["supabase_url"].rstrip("/")
    r = requests.get(
        f"{base}/rest/v1/jobs?match_reasons=is.null"
        f"&select=id,company,title,location,description&order=match_score.desc&limit={limit}",
        headers=sb_headers(cfg), timeout=30)
    r.raise_for_status()
    return r.json()


def update_job(cfg, jid, fields):
    base = cfg["supabase_url"].rstrip("/")
    h = {**sb_headers(cfg), "Content-Type": "application/json", "Prefer": "return=minimal"}
    r = requests.patch(f"{base}/rest/v1/jobs?id=eq.{jid}",
                       headers=h, data=json.dumps(fields), timeout=30)
    return r.status_code in (200, 204)


def main():
    cfg = load_config()
    g = cfg.get("gemma", {})
    if not g.get("enabled"):
        print("Gemma is off (config.json -> gemma.enabled = false). Skipping tailoring.")
        return 0

    # Is the local model server actually up?
    try:
        requests.get(g["base_url"].rstrip("/") + "/models", timeout=5)
    except Exception:
        print("Could not reach the local model server. Is LM Studio open with the "
              "server turned ON and a model loaded? Skipping this run.")
        return 0

    resume = read_resume()
    todo = fetch_todo(cfg, g.get("batch_per_run", 10))
    if not todo:
        print("No new jobs need tailoring - all caught up.")
        return 0

    print(f"Tailoring {len(todo)} job(s) with Gemma...")
    done = 0
    for job in todo:
        try:
            sc, reasons = score_with_gemma(g, resume, job)
            tailored = tailor_with_gemma(g, resume, job)
        except Exception as e:
            print(f"  - {job.get('company')} / {job.get('title')}: model error - {e}")
            continue
        # Always set match_reasons (non-null) so the job is marked done and not
        # re-processed. Only overwrite the score if Gemma gave us a number.
        fields = {"tailored_resume": tailored, "match_reasons": reasons or "Scored by local model."}
        if sc is not None:
            fields["match_score"] = sc
        if update_job(cfg, job["id"], fields):
            done += 1
            print(f"  - {job.get('company')} / {job.get('title')}: scored {sc}, resume tailored")
        else:
            print(f"  - {job.get('company')} / {job.get('title')}: could not save to Supabase")
    print(f"Done. {done} job(s) updated.")
    return done


if __name__ == "__main__":
    main()
