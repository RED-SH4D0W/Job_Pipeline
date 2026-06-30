#!/bin/bash
# Runs ONE scrape pass. Called automatically by the scheduler, but you can
# also run it by hand:  bash run_scraper.sh
#
# It just changes into this folder and runs the scraper, logging the output.

cd "$(dirname "$0")" || exit 1

# launchd starts with a bare PATH, so spell out where python3 might live.
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

echo ""
echo "================ scrape run: $(date) ================"
python3 scraper.py
echo "================ finished:   $(date) ================"
