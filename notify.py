#!/usr/bin/env python3
"""
notify.py - sends a short Telegram message after each pipeline run.

Used by run_pipeline.py. You can also run it directly to set things up:
  python3 notify.py chatid   -> prints your chat id (message your bot first)
  python3 notify.py test     -> sends a test message

Telegram settings live in the "telegram" section of config.json (secret, so
that file stays private):  bot_token + chat_id, and enabled: true.
"""

import sys
import requests
from scraper import load_config


def _post(token, chat_id, text):
    """Low-level send. Returns True on success."""
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=15)
        if r.status_code != 200:
            print("  ! telegram send failed:", r.status_code, r.text[:200])
        return r.status_code == 200
    except Exception as e:
        print("  ! telegram send error:", e)
        return False


def send_telegram(cfg, text):
    """Send only if telegram is enabled and configured. Safe to call always."""
    t = cfg.get("telegram", {})
    if not t.get("enabled"):
        return False
    token, chat = t.get("bot_token"), t.get("chat_id")
    if not token or not chat:
        print("  ! telegram: bot_token or chat_id missing in config.json")
        return False
    return _post(token, chat, text)


def _print_chat_ids(cfg):
    token = cfg.get("telegram", {}).get("bot_token")
    if not token:
        sys.exit("Put your bot_token in config.json (telegram section) first.")
    r = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=15)
    seen = set()
    for u in r.json().get("result", []):
        chat = (u.get("message") or u.get("channel_post") or {}).get("chat", {})
        cid = chat.get("id")
        if cid and cid not in seen:
            seen.add(cid)
            who = chat.get("first_name") or chat.get("title") or chat.get("username") or ""
            print(f"chat_id: {cid}   ({who})")
    if not seen:
        print("No chats found. Open your bot in Telegram, send it any message, "
              "then run this again.")


if __name__ == "__main__":
    cfg = load_config()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "test"
    if cmd == "chatid":
        _print_chat_ids(cfg)
    else:
        t = cfg.get("telegram", {})
        ok = _post(t.get("bot_token"), t.get("chat_id"),
                   "Test message from your job pipeline.")
        print("sent ✅" if ok else "not sent - check bot_token and chat_id in config.json")
