#!/bin/bash
# Overnight cycle: everything routine the scheduled overnight check does, as one fixed command (owner, 14 Oct:
# "how can we not need me to confirm every overnight check?"). The owner allows exactly this command once, so a
# scheduled run makes one or two tool calls and never waits on a prompt. Test galaxy only; never the live galaxy.
# Claude maintains this file. Anyone who changes it notes that on the board, because the allow rule trusts whatever
# it contains.
#
# Usage (Git Bash):  bash .../tools/agents/overnight_cycle.sh [--dry]
#   --dry   read-only: report what a run would see; no GPT dispatch, no setup, restart, round or tidy, no log lines
# Each run, in order:
#   1. Stop if Agent/STOP-OVERNIGHT exists (prints STOP so the scheduled run can disable itself).
#   2. GPT relay: dispatch the next open task when GPT's usage allows (gpt_relay.ps1 -Dispatch), then its state.
#   3. Squads: if any bot is offline or lost its connection, squad.py setup. If nobody can log in, the test galaxy is down: restart it
#      (AGENTS.md standing OK) unless one of the owner's clients is running; the start takes about 5 minutes,
#      so setup happens on the next run.
#   4. Once per server start, the regression gate (tools/bots/gate.py start: health, all bots in, one round of the
#      plan compared with each check's history; verdict in Bot-reports/GATE.md). Otherwise a 25-minute squad round
#      in the background from Agent/squad-plan.txt (a running one is left alone).
#   5. 3-6 lines in Bot-reports/OVERNIGHT.md; squad.py tidy every 4th run.
set -u
O=/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs
W=/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs
Q="$W/tools/bots/squad.py"
RELAY='C:\Users\Pengw\Documents\Codex\2026-10-13\h\outputs\tools\agents\gpt_relay.ps1'
LOG="$O/Bot-reports/OVERNIGHT.md"
WORK="$O/Agent/logs"   # not Agent/relay: Claude's listener watches that folder
DRY=0; [ "${1:-}" = "--dry" ] && DRY=1

sq() {  # sq SECONDS ARGS...: squad.py as swgemu inside Debian
    local t=$1; shift
    MSYS_NO_PATHCONV=1 timeout "$t" wsl -d Debian -u swgemu -- python3 "$Q" "$@" 2>&1 </dev/null
}
owner_on() {  # an owner client is running, or the client still points at the test galaxy
    tasklist //FO CSV //NH 2>/dev/null | grep -q -i -E '^"(swgclient|swgemu)' && return 0
    grep -q 46453 "$O/SWG-client/swgemu_login.cfg" 2>/dev/null && return 0
    return 1
}
gate() {  # gate SECONDS ARGS...: tools/bots/gate.py as swgemu inside Debian
    local t=$1; shift
    MSYS_NO_PATHCONV=1 timeout "$t" wsl -d Debian -u swgemu -- python3 "$W/tools/bots/gate.py" "$@" 2>&1 </dev/null | tr -d '\r'
}
online() { echo "$1" | grep -E '^  [A-Z][a-z]+ ' | grep -v -c -E 'HNone|offline'; }
lines=()
say() { lines+=("$1"); echo "$1"; }

# 1. stop file
if [ -e "$O/Agent/STOP-OVERNIGHT" ]; then
    echo "STOP: Agent/STOP-OVERNIGHT exists"
    [ $DRY = 0 ] && printf '\r\n### %s\r\n- Stop file found; the overnight cycle ends here.\r\n' "$(date +%H:%M)" >> "$LOG"
    exit 0
fi

# 2. GPT relay
[ $DRY = 0 ] && powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$RELAY" -Dispatch >/dev/null 2>&1
rs=$(powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$RELAY" -Status 2>&1 | tr -d '\r')
running=$(echo "$rs" | grep '^running:' | head -1)
open=$(echo "$rs" | grep -E '^open +' | awk '{print $2}' | paste -sd, -)
last=$(echo "$rs" | grep -E '^20[0-9]{2}-' | tail -1)
case "$last" in
    *"usage lim"*) last="${last%%not ready:*}not ready (GPT usage limit)" ;;
    *) last=$(echo "$last" | cut -c1-160) ;;
esac
say "- GPT relay: ${running:-nothing running}; open: ${open:-none}; last: ${last:-none}"

# 3. squads online?
st=$(sq 180 status)
n=$(online "$st")
if [ "$n" -lt 18 ] && [ $DRY = 0 ]; then  # any bot down or disconnected (a galaxy restart under it): log it in again
    sq 900 setup >/dev/null
    st=$(sq 180 status); n=$(online "$st")
    if [ "$n" = 0 ]; then
        if owner_on; then
            say "- Test galaxy down (setup logged nobody in); an owner client is running, so no restart."
        else
            sq 60 galaxy | tr -d '\r' | grep '^python3 ' > "$WORK/galaxy-restart.sh"
            if [ "$(grep -c '^python3 .*/tools/test_galaxy.py ' "$WORK/galaxy-restart.sh")" = 2 ]; then
                MSYS_NO_PATHCONV=1 wsl -d Debian -u root -- bash -c \
                    "setsid nohup bash $W/Agent/logs/galaxy-restart.sh > $W/Agent/logs/galaxy-restart.log 2>&1 < /dev/null &"
                say "- Test galaxy down (setup logged nobody in): restart started (AGENTS.md standing OK); setup next run."
            else
                say "- Test galaxy down, but squad.py galaxy didn't print the two restart lines; no restart."
            fi
        fi
    fi
fi
say "- Bots online: $n/18"

# 4. the regression gate once per server start (tools/bots/gate.py, 15 Oct), otherwise a squad round
due=$(gate 60 due | tail -1)
if [ "$n" != 0 ] && [ $DRY = 0 ] && [ "$due" = "due" ]; then
    say "- Gate: $(gate 60 start | tail -1 | cut -c1-160)"
elif [ "$n" != 0 ] && [ $DRY = 0 ] && [ "$due" != "running" ]; then
    plan=()
    for s in $(tr -d '\r' < "$O/Agent/squad-plan.txt"); do plan+=("$W/tools/bots/scenarios/$s"); done
    r=$(sq 120 run "${plan[@]}" --minutes 25 --detach | tr -d '\r' | grep -v '^$' | tail -1 | cut -c1-160)
    say "- Squad round: $r"
fi
say "- Gate: $(head -1 "$O/Bot-reports/GATE.md" 2>/dev/null | sed 's/^# Gate: //') (this server: $due)"

# 5. newest results, log, tidy
lr=$(sq 120 last | tr -d '\r')
say "- Latest run: $(echo "$lr" | grep -m1 '^# Squad run' | sed 's/^# Squad run //')"
groups=$(echo "$lr" | grep -E '^## [A-Z][a-z]+: [0-9]+/[0-9]+' | sed -E 's/^## ([A-Za-z]+): ([0-9]+\/[0-9]+).*/\1 \2/' | paste -sd, - | sed 's/,/, /g')
[ -n "$groups" ] && say "- Passed: $groups"
echo "$lr" | grep -E '^- (FAIL|ERROR|BLOCKED|RULE)' | head -4 | cut -c1-200 | while IFS= read -r l; do echo "$l"; done > "$WORK/overnight-last-issues.txt"
while IFS= read -r l; do say "$l"; done < "$WORK/overnight-last-issues.txt"

if [ $DRY = 0 ]; then
    { printf '\r\n### %s (overnight_cycle.sh)\r\n' "$(date +%H:%M)"; for l in "${lines[@]}"; do printf '%s\r\n' "$l"; done; } >> "$LOG"
    c=$(( $(cat "$WORK/overnight-cycle.count" 2>/dev/null || echo 0) + 1 )); echo $c > "$WORK/overnight-cycle.count"
    [ $((c % 4)) = 0 ] && sq 300 tidy >/dev/null && echo "- tidy done (run $c)"
fi
echo "OK"
