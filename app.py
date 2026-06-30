#!/usr/bin/env python3
"""
app.py - the local Job Console app.

Run it:   python3 app.py
Then open http://localhost:8000 in your browser.

It serves the webapp AND backs the "Find Jobs" button:
  POST /find-jobs  ->  scrapes fresh roles, scores them against your resume,
                       writes new ones to Supabase, returns the counts.

Everything runs locally on this machine. Press Ctrl+C to stop.
"""

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import scraper

PORT = 8000


class Handler(SimpleHTTPRequestHandler):
    def _send_json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path.rstrip("/") == "/find-jobs":
            print("\n>>> Find Jobs clicked - scraping...")
            try:
                length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(length) if length else b""
                data = json.loads(body) if body else {}
                cfg = scraper.load_config()
                cfg["dry_run"] = False           # the button always writes
                if data.get("resume"):           # active resume sent from the app
                    cfg["_resume_text"] = data["resume"]
                summary = scraper.main(cfg) or {}
                total = self._total_in_db(cfg)
                print(f">>> Done. {summary.get('added', 0)} new, {total} total.\n")
                self._send_json(200, {"ok": True, "total": total, **summary})
            except Exception as e:
                print(">>> Error:", e)
                self._send_json(500, {"ok": False, "error": str(e)})
        else:
            self._send_json(404, {"ok": False, "error": "not found"})

    @staticmethod
    def _total_in_db(cfg):
        import requests
        base = cfg["supabase_url"].rstrip("/")
        h = {**scraper.sb_headers(cfg), "Prefer": "count=exact", "Range": "0-0"}
        r = requests.get(f"{base}/rest/v1/jobs?select=id", headers=h, timeout=20)
        try:
            return int(r.headers.get("content-range", "0-0/0").split("/")[-1])
        except Exception:
            return None

    def log_message(self, *args):
        pass  # keep the terminal quiet except for our own prints


if __name__ == "__main__":
    print(f"Job Console running at  http://localhost:{PORT}")
    print("Open that link in your browser. Press Ctrl+C to stop.")
    try:
        ThreadingHTTPServer(("", PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
