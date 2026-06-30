#!/bin/bash
# ============================================================
# Turns ON the automatic pipeline: every 15 minutes from
# 6:00 AM to 12:00 PM CENTRAL time (= 7AM to 1PM Eastern).
#
# Run this ONCE on the Mac mini, after:
#   1) copying this folder over
#   2) pip3 install --user requests
#   3) creating config.json  (with "dry_run": false)
#   4) (for resume tailoring) LM Studio installed, model loaded,
#      server ON, and "gemma": { "enabled": true, ... } in config.json
#
# Just run:   bash setup_schedule.sh
# ============================================================
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
LABEL="com.jobpipeline.scraper"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
mkdir -p "$HOME/Library/LaunchAgents"

# Every 15 min, 6:00 AM through 11:45 AM, plus the 12:00 PM boundary.
# (Mac mini is on Central time, so 6AM-12PM CT == 7AM-1PM ET.)
TIMES=""
for H in 6 7 8 9 10 11; do
  for M in 0 15 30 45; do
    TIMES="$TIMES    <dict><key>Hour</key><integer>$H</integer><key>Minute</key><integer>$M</integer></dict>
"
  done
done
TIMES="$TIMES    <dict><key>Hour</key><integer>12</integer><key>Minute</key><integer>0</integer></dict>
"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$DIR/run_pipeline.sh</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
$TIMES  </array>
  <key>StandardOutPath</key><string>$DIR/scraper.log</string>
  <key>StandardErrorPath</key><string>$DIR/scraper.log</string>
</dict>
</plist>
EOF

# Reload so re-running this script cleanly updates the schedule.
launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"

echo "Scheduled. The pipeline runs every 15 minutes, 6:00 AM - 12:00 PM Central"
echo "(that's 7:00 AM - 1:00 PM Eastern)."
echo ""
echo "   Schedule file: $PLIST"
echo "   Run log:       $DIR/scraper.log"
echo ""
echo "   Stop it later with:  bash uninstall_schedule.sh"
