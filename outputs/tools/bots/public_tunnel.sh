#!/usr/bin/env bash
# C46 staging ONLY. After Claude reviews public mode and starts it on 127.0.0.1:8766:
#   wsl -d Debian -u swgemu -- bash /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/bots/public_tunnel.sh
# Foreground: Ctrl+C stops this wrapper and its cloudflared child, removing the URL.
# Background (inside WSL): bash tools/bots/public_tunnel.sh >Agent/discord-feed/tunnel-wrapper.log 2>&1 &
# Stop (inside WSL, outputs is cwd): kill -TERM "$(cat Agent/discord-feed/tunnel.pid)"
# This never starts a map or galaxy; it exposes ONLY the already reviewed public port.
set -euo pipefail
[[ $(id -un) == swgemu ]] || { echo 'Run as swgemu.' >&2; exit 2; }
outputs=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
state="$outputs/Agent/discord-feed"
binary=/opt/swg/agent/cloudflared/cloudflared
mkdir -p -- "$state"
# Kernel-held lock releases even on an uncatchable wrapper crash.
exec 9>"$state/tunnel.lock"
flock -n 9 || { echo 'Tunnel wrapper is already running.' >&2; exit 2; }
[[ -x $binary ]] || { echo 'Approved cloudflared binary unavailable.' >&2; exit 2; }
child=''
cleanup() {
    if [[ -n $child ]]; then
        kill -TERM "$child" 2>/dev/null || true
        wait "$child" 2>/dev/null || true
    fi
    rm -f -- "$state/public-url.txt" "$state/public-url.txt.tmp" "$state/tunnel.pid"
}
trap cleanup EXIT
trap 'exit 0' INT TERM
printf '%s\n' "$$" >"$state/tunnel.pid"
rm -f -- "$state/public-url.txt"
# Prevent an accidental tunnel to a different listener; readiness reads only the public API.
python3 - <<'PY'
import json, urllib.request
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
with opener.open('http://127.0.0.1:8766/data.json', timeout=5) as r:
    d = json.load(r)
if set(d) != {'bots', 'stats', 'roles', 'cities'}:
    raise SystemExit('Public map schema check failed.')
PY
"$binary" tunnel --url http://127.0.0.1:8766 --no-autoupdate >"$state/tunnel.log" 2>&1 &
child=$!
for ((n=0; n<60; n++)); do
    kill -0 "$child" 2>/dev/null || { echo 'Quick tunnel exited; inspect the local log.' >&2; exit 1; }
    link=$(sed -nE 's@.*(https://[a-z0-9]+(-[a-z0-9]+)*\.trycloudflare\.com).*@\1@p' "$state/tunnel.log" | head -n 1)
    if [[ -n $link ]]; then
        printf '%s\n' "$link" >"$state/public-url.txt.tmp"
        mv -- "$state/public-url.txt.tmp" "$state/public-url.txt"
        echo 'Public URL ready in the local feed state folder.'
        wait "$child"
        exit $?
    fi
    sleep 1
done
echo 'Quick tunnel did not provide a URL within 60 seconds.' >&2
exit 1
