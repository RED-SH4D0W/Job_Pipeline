#!/bin/bash
# One full cycle: scrape -> score/tailor with Gemma -> Telegram heartbeat.
# This is what the scheduler runs. You can also run it by hand:
#   bash run_pipeline.sh
#
# The steps run one-after-another (never at the same time), so the scraper and
# the local model don't fight over memory.

cd "$(dirname "$0")" || exit 1
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

echo ""
echo "================ pipeline run: $(date) ================"
python3 run_pipeline.py
echo "================ finished: $(date) ================"
