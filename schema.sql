-- ============================================================
-- Job Console — Supabase schema
-- Paste this whole file into:  Supabase dashboard → SQL Editor → New query → Run
-- It creates the single "jobs" table that the scraper writes to
-- and the webapp reads from.
-- ============================================================

create table if not exists public.jobs (
  id              uuid primary key default gen_random_uuid(),
  created_at      timestamptz not null default now(),
  source          text,           -- where it came from: greenhouse | lever | ashby | ...
  company         text not null,
  title           text not null,
  location        text,
  url             text,           -- the apply / posting link (used to avoid duplicates)
  description     text,
  match_score     int,            -- 0-100, filled by the matching step
  match_reasons   text,           -- short note on why it fits you
  status          text not null default 'new',  -- new | to_apply | applied | skipped
  tailored_resume text,           -- tailored resume (text or LaTeX) for this job
  recruiter_name  text,
  recruiter_email text,
  email_draft     text,           -- drafted cold email (you send it yourself)
  notes           text,
  posted_at       timestamptz
);

-- Stop the same posting (same url) from being inserted twice.
-- Lets the scraper safely "insert, or skip if already there".
create unique index if not exists jobs_url_unique
  on public.jobs (url)
  where url is not null;

-- Row Level Security: required by Supabase. For a private, single-user
-- project, this policy lets the anon (public) key read and write the
-- jobs table. You can tighten this later by adding real login.
alter table public.jobs enable row level security;

drop policy if exists "anon full access to jobs" on public.jobs;
create policy "anon full access to jobs"
  on public.jobs for all
  to anon
  using (true)
  with check (true);

-- Optional: a couple of rows so the webapp shows something immediately.
-- Delete these once your scraper is adding real jobs.
insert into public.jobs (source, company, title, location, url, match_score, match_reasons, status)
values
  ('greenhouse', 'Pixelforge Games', 'Frontend Engineer (Tools)', 'Remote — US', 'https://example.com/1', 91, 'Strong React + tools UI overlap at a game studio.', 'new'),
  ('lever', 'Northwind Labs', 'Full Stack Developer', 'Austin, TX', 'https://example.com/2', 84, 'React/Node full-stack match with integration experience.', 'to_apply')
on conflict do nothing;
