#!/bin/bash
# Refreshes the deploy folder with the latest app, then you re-deploy site/.
# Run:  bash publish.sh
cp "$(dirname "$0")/index.html" "$(dirname "$0")/site/index.html"
echo "Updated site/index.html. Now drag the 'site' folder to Netlify (or 'git push' if linked)."
