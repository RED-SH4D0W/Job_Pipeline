#!/bin/bash
# Stops and removes the automatic daily scrape.  Run:  bash uninstall_schedule.sh
LABEL="com.jobpipeline.scraper"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
launchctl unload "$PLIST" 2>/dev/null || true
rm -f "$PLIST"
echo "✅ Automatic runs removed. (scraper.py still works by hand.)"
