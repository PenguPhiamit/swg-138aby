#!/bin/bash
# Claude's listener for ChatGPT (Git Bash, run in the background). Exits, which wakes Claude, as soon as ChatGPT
# writes to Agent/to-claude.md, changes the task queue, writes a relay answer or edits the board.
# Restart it after each wake-up.   Usage: watch_gpt.sh [seconds between checks, default 30]
O=/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs
FILES="$O/Agent/to-claude.md $O/Agent/gpt-queue.json $O/SWG-handoff.md"
stamp() { stat -c '%Y %s %n' $FILES 2>/dev/null; ls -1 "$O/Agent/relay" 2>/dev/null | tail -3; }
before=$(stamp)
while sleep "${1:-30}"; do
  now=$(stamp)
  if [ "$now" != "$before" ]; then
    echo "changed at $(date +%H:%M:%S):"
    diff <(echo "$before") <(echo "$now") | grep '^>' | cut -c3-
    exit 0
  fi
done
