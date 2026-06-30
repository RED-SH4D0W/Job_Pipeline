# Job Console

Your personal cockpit for reviewing AI-matched jobs. It reads the jobs your
scraper saves into Supabase and lets you filter, sort, view each tailored
resume / email draft, and mark each role (to apply / applied / skip).

This is the part **you** use on your trusted personal device. The Mac mini
entity only writes jobs into the database; it never runs this app.

---

## What's in this folder

- `index.html` — the whole app. One file, no build step.
- `schema.sql` — run once in Supabase to create the `jobs` table.
- `README.md` — this file.

Your Supabase keys are **not** in any of these files. You paste them into the
app's Settings once, and they're saved only in your browser.

---

## One-time setup (about 5 minutes)

**1. Create the table.**
Open your Supabase project → SQL Editor → New query. Paste everything from
`schema.sql` and click Run. (It also adds two sample rows so the app isn't
empty.)

**2. Get your two keys.**
In Supabase: Project Settings → Data API (or "API").
- Copy the **Project URL** (looks like `https://abcd1234.supabase.co`)
- Copy the **anon public** key (a long string starting with `eyJ…`)

**3. Open the app and connect.**
Run it (see below), click **Settings**, paste the URL and anon key, and click
**Save & connect**. You should see your jobs.

> Want to look around before connecting? In Settings, turn on **sample data**.

---

## How to run it

The simplest reliable way (so the app can talk to Supabase) is to serve the
folder with a tiny local web server:

```
cd job-console
python3 -m http.server 8000
```

Then open **http://localhost:8000** in your browser.

(Double-clicking `index.html` may also work, but some browsers block parts of
it when opened as a bare file — the local server avoids that.)

---

## Status colors

- **New** — just arrived, not reviewed
- **To apply** — you've decided to apply
- **Applied** — done
- **Skipped** — not for you

Changing a status saves instantly back to Supabase.

---

## What feeds this later

The `jobs` table has columns the rest of the pipeline fills in over time:
`match_score`, `match_reasons`, `tailored_resume`, `email_draft`,
`recruiter_name`, `recruiter_email`. They show up in the app automatically as
the scraper and tailoring steps populate them. Empty ones just show a friendly
placeholder for now.
