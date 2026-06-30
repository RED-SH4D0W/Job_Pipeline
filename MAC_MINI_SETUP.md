# Mac mini setup — full guide (beginner friendly)

This sets up the Mac mini (the "entity") to **automatically find jobs and tailor
your resume** every 15 minutes from **7AM–1PM Eastern** (which is **6AM–12PM
Central**, the mini's time zone). The mini only writes to the database; you
review jobs on your own laptop.

Do these steps **once**, in order. You only need to copy/paste commands.

---

## Part A — Copy the project over

1. **AirDrop the whole `Job_app_pipeline` folder** from your laptop to the Mac
   mini. Put it somewhere simple, like your home folder.
2. On the mini, open the **Terminal** app (press `Cmd+Space`, type "Terminal",
   Enter).
3. Go into the folder (adjust the path if you put it elsewhere):
   ```
   cd ~/Job_app_pipeline
   ```

---

## Part B — Install Python's one library + make your config

1. Install the `requests` library:
   ```
   pip3 install --user requests
   ```
2. Create your private config from the template:
   ```
   cp config.example.json config.json
   ```
   > If `config.json` already came over from your laptop, you can skip this.
3. Open it to edit:
   ```
   open -e config.json
   ```
   Make sure these are set:
   - `"supabase_url"` and `"supabase_key"` → your real Supabase values
   - `"dry_run": false`  ← so runs actually save jobs
   Save and close.

4. **Test a plain scrape** (no AI yet):
   ```
   python3 scraper.py
   ```
   You should see it scan the companies and either add new jobs or say
   "Nothing new to add." If so, the mini can talk to your database. 

---

## Part C — Install Gemma (the local AI) with LM Studio

LM Studio is a free app that runs the Gemma model on the mini and exposes a
small local "server" the scripts talk to. Nothing leaves the machine; no API
key, no subscription.

1. **Download LM Studio** from <https://lmstudio.ai> and install it (drag to
   Applications), then open it.

2. **Download the model.** In LM Studio, click the 🔍 **Search** (Discover) tab
   and search for **`gemma 3 12b`**. Pick a **4-bit (Q4)** version — it's the
   right size for 16GB RAM. Click **Download** and wait (it's several GB).

3. **Load the model.** Go to the **Chat** tab, click the model dropdown at the
   top, and select the Gemma you just downloaded. Wait until it says loaded.
   (Send it a quick "hi" to confirm it answers.)

4. **Turn on the local server.** Click the **Developer / Local Server** tab
   (the `>_` icon). Make sure the **Port is `1234`**, then click **Start
   Server**. You should see it listening at `http://localhost:1234`.

5. **Get the exact model name.** On that server screen LM Studio shows the
   model identifier it expects (something like `google/gemma-3-12b` or
   `gemma-3-12b-it`). Copy that exact text.

6. **Tell the config to use Gemma.** Open the config again:
   ```
   open -e config.json
   ```
   In the `"gemma"` section set:
   - `"enabled": true`
   - `"model": "<paste the exact model name from step 5>"`
   Leave `base_url` as `http://localhost:1234/v1`. Save and close.

7. **Test the AI step by hand:**
   ```
   python3 enrich.py
   ```
   It should say "Tailoring N job(s) with Gemma…" and list jobs as it scores and
   tailors them. (The first run on a big backlog is slow — that's normal. It
   does up to `batch_per_run` jobs each run and catches up over time.)

> **Keep LM Studio open and the server running** for tailoring to work. In LM
> Studio settings you can enable "run at login" and keep the model loaded so it
> survives restarts.

---

## Part C2 — Telegram heartbeat (get a message every run)

After each 15-minute cycle, the mini can text you on Telegram how many new roles
it scraped (and how many resumes it tailored). Optional, but here's the setup.

1. **Make a bot.** In Telegram, search for **@BotFather**, open it, send
   `/newbot`, and follow the prompts (give it any name). BotFather replies with
   a **token** that looks like `123456789:AAE...`. Copy it.
2. **Say hi to your bot.** Tap the link BotFather gives you to open your new bot,
   and send it any message (e.g. "hi"). This is required so it can message you.
3. **Put the token in config and find your chat id:**
   ```
   open -e config.json
   ```
   In the `"telegram"` section, paste your token into `"bot_token"`, save. Then:
   ```
   python3 notify.py chatid
   ```
   It prints a `chat_id` (a number). Copy it.
4. **Finish the config:** open `config.json` again, set:
   - `"enabled": true`
   - `"chat_id": "<the number from step 3>"`
   Save.
5. **Test it:**
   ```
   python3 notify.py test
   ```
   You should get a "Test message from your job pipeline" in Telegram. Done.

> The token and chat id are secret — they live only in `config.json`, which is
> never shared or committed.

---

## Part D — Turn on the automatic schedule

This makes the mini run the whole pipeline (scrape → score → tailor) every 15
minutes during your window.

```
bash setup_schedule.sh
```

That's it. It prints where the schedule and log live. It runs at
6:00, 6:15, 6:30 … 11:45, and 12:00 **Central** time (= 7AM–1PM Eastern).

---

## Checking that it's working

- **Watch what it's doing live:**
  ```
  tail -f ~/Job_app_pipeline/scraper.log
  ```
  (Press `Ctrl+C` to stop watching — that does NOT stop the schedule.)
- **Confirm the schedule is installed:**
  ```
  launchctl list | grep jobpipeline
  ```
- **Run one full cycle right now:**
  ```
  bash run_pipeline.sh
  ```

## Reviewing the results (on your laptop)

Nothing changes here — open the Job Console on your laptop as usual. New jobs,
their Gemma fit scores/reasons, and the **Tailored resume** button will fill in
automatically as the mini works.

## Changing or stopping things

- **Stop the automatic runs:** `bash uninstall_schedule.sh`
- **Change the window or frequency:** edit the loop near the top of
  `setup_schedule.sh`, then run `bash setup_schedule.sh` again.
- **Pause the AI only (keep scraping):** set `"gemma": { "enabled": false }` in
  config.json.

---

## How the AI tailoring behaves (the safety rule)

Gemma is instructed to rewrite only your **summary, bullet wording, skills,
ordering, and emphasis** to fit each job. It is told **not** to change your
contact info, education, company names, job titles, or employment dates, and
**never** to invent experience — only to reframe what's true. Always glance at
a tailored resume before you use it.
