#!/bin/bash
# Run a test page in headless Chromium until its title starts with "DONE".
#
#   tools/runpage.sh URL [DEBUG_PORT=9301] [TIMEOUT_SECONDS=3600]
#
# Needed for pages that work in Web Workers (generate.html, custom.html,
# ui.html): --dump-dom and --virtual-time-budget don't wait for workers.
# Pair with ?post=/name and tools/serve.py to capture the output.
# CHROME overrides the browser binary. Snap Chromium can only write under
# ~/snap/chromium/common, so the profile goes there when that exists.
URL=$1; PORT=${2:-9301}; TMO=${3:-3600}
CHROME=${CHROME:-$(command -v chromium || command -v chromium-browser || command -v google-chrome)}
if [ -d "$HOME/snap/chromium/common" ]; then PROF=$HOME/snap/chromium/common/antfeast-prof-$PORT
else PROF=$(mktemp -d); fi
"$CHROME" --headless=new --disable-gpu --user-data-dir="$PROF" --remote-debugging-port="$PORT" "$URL" >/dev/null 2>&1 &
PID=$!
T=
for ((i = 0; i < TMO; i += 5)); do
  sleep 5
  T=$(curl -s "localhost:$PORT/json/list" | grep -o '"title": *"DONE[^"]*"')
  [ -n "$T" ] && break
done
kill $PID 2>/dev/null; wait $PID 2>/dev/null
echo "${T:-TIMEOUT}"
