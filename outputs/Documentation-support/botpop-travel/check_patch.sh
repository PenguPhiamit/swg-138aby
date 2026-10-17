#!/bin/bash
# Checks botpop-travel.patch against /opt/swg/Core3-dev HEAD without touching /opt/swg:
#  1. git apply --check in the dev tree (read-only);
#  2. a syntax-only clang compile of CommandConfigManager.cpp (the file that includes BotPop) with the dev build's own
#     flags from build/dev/compile_commands.json and the patched BotPop headers in a /tmp overlay in front.
# Run as swgemu:  wsl -d Debian -u swgemu -- bash <this folder>/check_patch.sh
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
PATCH="$HERE/botpop-travel.patch"
DEV=/opt/swg/Core3-dev
WORK=$(mktemp -d /tmp/botpop-travel-check.XXXXXX)
trap 'rm -rf "$WORK"' EXIT

echo "HEAD: $(git -C "$DEV" log --oneline -1)"
echo "== git apply --check"
git -C "$DEV" apply --check "$PATCH" && echo "APPLY OK" || exit 1

echo "== overlay"
git -C "$DEV" archive HEAD MMOCoreORB/src/server/zone/managers/botpop | tar -x -C "$WORK"
(cd "$WORK" && git apply "$PATCH") || exit 1

echo "== clang syntax-only"
TU="$DEV/MMOCoreORB/src/server/zone/managers/objectcontroller/command/CommandConfigManager.cpp"
CMD=$(python3 - "$DEV/MMOCoreORB/build/dev/compile_commands.json" "$TU" <<'EOF'
import json, shlex, sys
for e in json.load(open(sys.argv[1])):
    if e['file'] == sys.argv[2]:
        args = e.get('arguments') or shlex.split(e['command'])
        out, skip = [], False
        for a in args[1:]:
            if skip:
                skip = False
                continue
            if a in ('-o', '-c', '-MF', '-MT', '-MQ'):
                skip = True
                continue
            if a in ('-MD', '-MMD') or a == e['file']:
                continue
            out.append(a)
        print(e['directory'])
        print(shlex.join(out))
        break
EOF
)
DIR=$(echo "$CMD" | head -1)
FLAGS=$(echo "$CMD" | tail -n +2)
[ -z "$FLAGS" ] && { echo "no compile command for $TU"; exit 1; }
cd "$DIR" || exit 1
LOG="$WORK/clang.log"
eval nice -n 10 clang++-19 -fsyntax-only -iquote "$WORK/MMOCoreORB/src" -Wno-unknown-warning-option -H $FLAGS "$TU" > "$LOG" 2>&1
STATUS=$?
echo "clang exit: $STATUS"
echo "patched BotPop headers compiled from the overlay: $(grep -o "$WORK/[^ ]*botpop/[A-Za-z]*\.h" "$LOG" | sort -u | wc -l)"
echo "errors: $(grep -c 'error:' "$LOG"), BotPop warnings: $(grep 'warning:' "$LOG" | grep -c botpop)"
grep -E "error:|botpop.*warning:" "$LOG" | head -40
exit $STATUS
