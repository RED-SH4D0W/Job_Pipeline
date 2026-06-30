#!/usr/bin/env python3
"""
run_pipeline.py - one full cycle, called by the scheduler every 15 minutes:
  1) scrape new jobs        (scraper.py)
  2) score + tailor them    (enrich.py, if Gemma is on)
  3) send a Telegram heartbeat with how many roles were scraped this run.

Run by hand:  python3 run_pipeline.py
"""

from datetime import datetime
import scraper
import enrich
import notify
from scraper import load_config


def build_message(cfg, scrape, tailored):
    now = datetime.now().strftime("%-I:%M %p")
    lines = [f"Job pipeline · {now}"]
    if scrape:
        lines.append(f"Scanned {scrape['companies']} companies")
        lines.append(f"New roles scraped: {scrape['added']}")
    else:
        lines.append("Scrape did not complete.")
    if cfg.get("gemma", {}).get("enabled"):
        lines.append(f"Resumes tailored: {tailored}")
    return "\n".join(lines)


def main():
    cfg = load_config()

    print("--- step 1: scraping ---")
    scrape = scraper.main()          # {companies, fetched, matched, added, dry}

    print("--- step 2: scoring + tailoring ---")
    tailored = enrich.main()         # int (0 if Gemma off / unreachable)

    print("--- step 3: telegram heartbeat ---")
    msg = build_message(cfg, scrape, tailored)
    if notify.send_telegram(cfg, msg):
        print("telegram: sent")
    else:
        print("telegram: not sent (off or not configured)")


if __name__ == "__main__":
    main()
