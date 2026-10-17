#!/bin/bash
# PL-04 server checks, read-only (Claude, 17 Oct 2026). Writes nothing under /opt/swg: the patch is applied to copies
# of the touched files in a scratch folder under /tmp, which is removed at the end.
#   wsl -d Debian -u swgemu -- bash /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-species/s7-hutt/nal-hutta-home/tools/server_check.sh
HOME_DIR=/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-species/s7-hutt/nal-hutta-home
PATCH=$HOME_DIR/core3-dev-nal-hutta-home.patch
DEV=/opt/swg/Core3-dev
S=$DEV/MMOCoreORB/bin/scripts
fail=0
echo "# PL-04 server checks on $(date '+%d %b %Y %I:%M %p'); dev HEAD $(git -C $DEV rev-parse --short HEAD)"

echo "## git apply --check (dev working tree, read-only)"
if git -C $DEV apply --check "$PATCH"; then echo "ok apply --check on HEAD"; else echo "FAIL apply --check"; fail=1; fi
files=$(grep '^+++ b/' "$PATCH" | sed 's#^+++ b/##')
changed=$(grep '^--- a/' "$PATCH" | sed 's#^--- a/##')
same=$(git -C $DEV diff --stat 69f5c879 HEAD -- $changed | tail -1)
echo "files the patch changes, 69f5c879..HEAD: ${same:-identical}"

echo "## luac -p on the patched files"
T=$(mktemp -d /tmp/pl04-check.XXXXXX)
for f in $changed; do mkdir -p "$T/$(dirname $f)"; git -C $DEV show HEAD:$f > "$T/$f"; done
( cd "$T" && git init -q . && git apply "$PATCH" ) || { echo "FAIL apply in scratch"; fail=1; }
LUAC=$(command -v luac5.3 || command -v luac || command -v luac5.4)
for f in $files; do
  if $LUAC -p "$T/$f"; then echo "ok luac $f"; else echo "FAIL luac $f"; fail=1; fi
done

echo "## referenced templates exist in dev"
P=$T/MMOCoreORB/bin/scripts
for l in $(grep -ho 'lairTemplateName = "[a-z0-9_]*"' $P/mobile/spawn/hutta/*.lua $P/mobile/spawn/destroy_mission/hutta_destroy_missions.lua | sed 's/.*"\(.*\)"/\1/' | sort -u); do
  if grep -rqs "^$l = Lair:new" $S/mobile/lair; then echo "ok lair $l"; else echo "MISSING lair $l"; fail=1; fi
done
for l in $(grep -ho 'lairTemplateName = "[a-z0-9_]*"' $P/mobile/spawn/hutta/*.lua | sed 's/.*"\(.*\)"/\1/' | sort -u); do
  for m in $(grep -rh -A1 "^$l = Lair:new" $S/mobile/lair | grep -o 'mobiles = {{"[a-z0-9_]*"' | sed 's/.*"\(.*\)"/\1/'); do
    lvl=$(grep -h -m1 '^\s*level' $(grep -rl "^$m = Creature:new" $S/mobile | head -1) | tr -dc '0-9'); echo "   $l: $m level $lvl"
  done
done
for m in gamorrean_guard patron_nikto trainer_smuggler; do
  if grep -rqsE "addCreatureTemplate\\($m, *\"$m\"\\)" $S/mobile; then echo "ok mobile $m"; else echo "MISSING mobile $m"; fail=1; fi
done
for t in $(grep -ho '"object/[a-z0-9_/]*\.iff"' $P/screenplays/sandbox/hutta_home.lua $P/screenplays/sandbox/hutta_home_places.lua $P/mobile/sandbox/hutta_home.lua | tr -d '"' | sort -u); do
  s="${t%.iff}.lua"
  if [ -f "$S/$s" ]; then echo "ok template $t"; else echo "MISSING template $t"; fail=1; fi
done
for t in $(python3 -c "import json;print('\n'.join(sorted({s['template'] for s in json.load(open('$HOME_DIR/home.json'))['statics']})))"); do
  s="${t//shared_/}"; s="${s%.iff}.lua"
  if [ -f "$S/$s" ]; then echo "ok snapshot template $t"; else echo "MISSING snapshot template $t"; fail=1; fi
done
for c in $(grep -ho '"hutta_[a-z_]*_convo_template"' $P/mobile/sandbox/hutta_home.lua | sort -u); do
  if grep -q "addConversationTemplate($c" $P/mobile/conversations/sandbox/hutta_home_conv.lua; then echo "ok conversation $c"; else echo "MISSING conversation $c"; fail=1; fi
done
for h in $(grep -ho 'convo("[A-Za-z]*")' $P/mobile/conversations/sandbox/hutta_home_conv.lua | sed 's/convo("\(.*\)")/\1/'); do
  if grep -q "^$h = conv_handler:new" $P/screenplays/sandbox/hutta_home.lua; then echo "ok handler $h"; else echo "MISSING handler $h"; fail=1; fi
done
if grep -rqs "hutta_destroy_missions\|planet_hutta\|HuttaHome" $S; then echo "NOTE dev already mentions PL-04 names"; fi

rm -rf "$T"
echo "## result: $([ $fail = 0 ] && echo PASS || echo FAIL)"
exit $fail
