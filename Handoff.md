{\rtf1\ansi\ansicpg1252\cocoartf2870
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\froman\fcharset0 Times-Bold;\f1\froman\fcharset0 Times-Roman;\f2\fmodern\fcharset0 Courier;
}
{\colortbl;\red255\green255\blue255;\red0\green0\blue0;}
{\*\expandedcolortbl;;\cssrgb\c0\c0\c0;}
{\*\listtable{\list\listtemplateid1\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat0\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid1\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid1}
{\list\listtemplateid2\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat0\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid101\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid2}
{\list\listtemplateid3\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat0\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid201\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid3}
{\list\listtemplateid4\listhybrid{\listlevel\levelnfc0\levelnfcn0\leveljc0\leveljcn0\levelfollow0\levelstartat1\levelspace360\levelindent0{\*\levelmarker \{decimal\}}{\leveltext\leveltemplateid301\'01\'00;}{\levelnumbers\'01;}\fi-360\li720\lin720 }{\listname ;}\listid4}
{\list\listtemplateid5\listhybrid{\listlevel\levelnfc23\levelnfcn23\leveljc0\leveljcn0\levelfollow0\levelstartat0\levelspace360\levelindent0{\*\levelmarker \{disc\}}{\leveltext\leveltemplateid401\'01\uc0\u8226 ;}{\levelnumbers;}\fi-360\li720\lin720 }{\listname ;}\listid5}}
{\*\listoverridetable{\listoverride\listid1\listoverridecount0\ls1}{\listoverride\listid2\listoverridecount0\ls2}{\listoverride\listid3\listoverridecount0\ls3}{\listoverride\listid4\listoverridecount0\ls4}{\listoverride\listid5\listoverridecount0\ls5}}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\deftab720
\pard\pardeftab720\sa321\partightenfactor0

\f0\b\fs48 \cf0 \expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Project Handoff \'97 Job Application Pipeline\
\pard\pardeftab720\sa240\partightenfactor0

\f1\b0\fs24 \cf0 Read this first. It's the full context for this project, written by Claude (chat) so this Claude Code session starts with the whole picture. The human (Prasant) is comfortable copy/pasting commands and following clear steps, but is newer to building software \'97 explain things simply and avoid unexplained jargon.\
\pard\pardeftab720\sa298\partightenfactor0

\f0\b\fs36 \cf0 What this project is\
\pard\pardeftab720\sa240\partightenfactor0

\f1\b0\fs24 \cf0 A personal, semi-automated job-search assistant. It finds relevant jobs, scores them, tailors Prasant's resume per job, and presents everything in a simple webapp for him to review and act on. He applies and sends any emails 
\f0\b himself
\f1\b0  \'97 the automation never applies or emails on his behalf.\
\pard\pardeftab720\sa298\partightenfactor0

\f0\b\fs36 \cf0 The core design: two zones\
\pard\tx220\tx720\pardeftab720\li720\fi-720\partightenfactor0
\ls1\ilvl0
\fs24 \cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 The "entity" (a Mac mini, separate Apple ID, no logins):
\f1\b0  runs the scraping, scoring, and resume tailoring. Holds NO personal accounts. Writes results to Supabase. Runs a local model (Gemma) so no paid API or subscription is needed at runtime.\
\ls1\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 The "personal device" (trusted, where Prasant works):
\f1\b0  runs the review webapp, and is where he actually applies to jobs and sends emails from his own accounts.\
\ls1\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Supabase
\f1\b0  is the shared handoff between them: the entity writes rows, the webapp reads them.\
\pard\pardeftab720\sa240\partightenfactor0

\f0\b \cf0 Build now on the personal device; AirDrop the finished folder to the Mac mini later.
\f1\b0  That's the current phase: finish and test here, deploy there.\
\pard\pardeftab720\sa298\partightenfactor0

\f0\b\fs36 \cf0 Hard rules (important)\
\pard\tx220\tx720\pardeftab720\li720\fi-720\partightenfactor0
\ls2\ilvl0
\fs24 \cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Secrets never go in code or git.
\f1\b0  Supabase keys and the resume live in 
\f2\fs26 config.json
\f1\fs24  (gitignored) or are entered in the webapp's Settings (saved in the browser). Only logic gets committed/shared.\
\ls2\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Claude subscription cannot be used by automated scripts
\f1\b0  (Anthropic banned subscription use in third-party/automated harnesses in April 2026). Runtime AI work uses local Gemma, or a paid API key as an optional upgrade \'97 never the subscription. The subscription is only for interactive building (this).\
\ls2\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Resume tailoring rule:
\f1\b0  Gemma may freely rewrite the summary, bullet wording, skills, ordering, and emphasis to fit each job. It must NOT change contact info, education, company names, job titles, or employment dates, and must never fabricate experience or skills \'97 reframe truthfully only.\
\pard\pardeftab720\sa298\partightenfactor0

\f0\b\fs36 \cf0 What's already built (in this folder)\
\pard\tx220\tx720\pardeftab720\li720\fi-720\partightenfactor0
\ls3\ilvl0
\f2\b0\fs26 \cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 index.html
\f1\fs24  \'97 the review webapp ("Job Console"). Reads jobs from Supabase; filter/sort/search; per-job view of tailored resume + email draft; set status (new / to_apply / applied / skipped). Keys entered in Settings, stored in browser. Confirmed working.\
\ls3\ilvl0
\f2\fs26 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 schema.sql
\f1\fs24  \'97 creates the 
\f2\fs26 jobs
\f1\fs24  table in Supabase (run once in the SQL editor). RLS on, anon key allowed (fine for a private single-user project).\
\ls3\ilvl0
\f2\fs26 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 scraper.py
\f1\fs24  \'97 pulls jobs from public ATS feeds (Greenhouse, Lever, Ashby), filters to target roles, scores by keyword overlap, writes new rows to Supabase via REST. Only needs the 
\f2\fs26 requests
\f1\fs24  library. Reads 
\f2\fs26 config.json
\f1\fs24 .\
\ls3\ilvl0
\f2\fs26 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 config.example.json
\f1\fs24  \'97 copy to 
\f2\fs26 config.json
\f1\fs24 , add Supabase URL + anon key, target titles/keywords, and a list of companies (
\f2\fs26 ats
\f1\fs24  + 
\f2\fs26 token
\f1\fs24  + 
\f2\fs26 name
\f1\fs24 ).\
\ls3\ilvl0
\f2\fs26 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Resume_PG.tex
\f1\fs24  \'97 Prasant's master resume (LaTeX), single page. The tailoring step will copy and adapt this per job. (Add it to the folder if not present.)\
\pard\pardeftab720\sa298\partightenfactor0

\f0\b\fs36 \cf0 Targeting\
\pard\pardeftab720\sa240\partightenfactor0

\f1\b0\fs24 \cf0 Roles: software developer, game developer, frontend, full stack. Level: entry / associate / 0\'963 years. Location: United States (incl. remote).\
\pard\pardeftab720\sa298\partightenfactor0

\f0\b\fs36 \cf0 What's next (build order)\
\pard\tx220\tx720\pardeftab720\li720\fi-720\partightenfactor0
\ls4\ilvl0
\fs24 \cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	1	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Get the scraper running end to end
\f1\b0  on the personal device: run 
\f2\fs26 schema.sql
\f1\fs24 , 
\f2\fs26 pip3 install requests
\f1\fs24 , make 
\f2\fs26 config.json
\f1\fs24 , run with 
\f2\fs26 "dry_run": true
\f1\fs24  to preview, then 
\f2\fs26 false
\f1\fs24  to write. Confirm real jobs show in the webapp.\
\ls4\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	2	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Expand the company list
\f1\b0  in 
\f2\fs26 config.json
\f1\fs24  with companies Prasant wants.\
\ls4\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	3	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Local model scoring + resume tailoring with Gemma
\f1\b0  (via LM Studio's local server, default at http://localhost:1234/v1). Replace the keyword score with a real fit score, and generate a tailored resume per job into the 
\f2\fs26 tailored_resume
\f1\fs24  column, following the tailoring rule above. Run the model and the scraper at separate times (16GB RAM \'97 they don't share well).\
\ls4\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	4	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Recruiter + cold-email drafting
\f1\b0  (optional, later): draft only; Prasant sends. Mind LinkedIn ToS \'97 prefer public sources.\
\ls4\ilvl0
\f0\b \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	5	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Schedule it
\f1\b0  to run daily (9AM\'961PM ET) once moved to the Mac mini, with a Telegram heartbeat/notification when each run finishes or fails.\
\pard\pardeftab720\sa298\partightenfactor0

\f0\b\fs36 \cf0 Deployment (later)\
\pard\pardeftab720\sa240\partightenfactor0

\f1\b0\fs24 \cf0 Once it works here: AirDrop the whole folder to the Mac mini, install LM Studio\
\pard\tx220\tx720\pardeftab720\li720\fi-720\partightenfactor0
\ls5\ilvl0\cf0 \kerning1\expnd0\expndtw0 \outl0\strokewidth0 {\listtext	\uc0\u8226 	}\expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Gemma 4 12B (4-bit) and Python there, add 
\f2\fs26 config.json
\f1\fs24  directly on the mini, and schedule the daily run. The mini needs no logins \'97 just the scripts, the local model, and the config file.\
}