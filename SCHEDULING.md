# Scheduling — quick reference

Full beginner walkthrough (with Gemma): see **MAC_MINI_SETUP.md**.

**What the schedule does:** runs `run_pipeline.sh` (scrape → score → tailor)
every **15 minutes from 6:00 AM to 12:00 PM Central** time, which is
**7:00 AM – 1:00 PM Eastern**. The Mac mini stays on Central time; the schedule
is written in Central so it lines up with the Eastern window.

**Turn it on:**  `bash setup_schedule.sh`
**Turn it off:** `bash uninstall_schedule.sh`
**Watch it:**    `tail -f scraper.log`
**Run once now:** `bash run_pipeline.sh`

The scrape and the Gemma step run one-after-another inside each cycle, so they
never use memory at the same time. macOS won't start a new cycle until the
previous one finishes, so runs never pile up.
