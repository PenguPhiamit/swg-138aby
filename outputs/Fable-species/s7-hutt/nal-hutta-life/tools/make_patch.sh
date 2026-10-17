#!/bin/bash
# PL-06: build core3-dev-nal-hutta-life.patch against Core3-dev HEAD and check it. Read-only on /opt/swg (git show,
# git apply --check, luac -p on copies). Run as root inside WSL:  bash make_patch.sh
set -e
L=/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-species/s7-hutt/nal-hutta-life
W=$(mktemp -d); trap 'rm -rf $W' EXIT
DEV=/opt/swg/Core3-dev; G="git -c safe.directory=* -C $DEV"
S=MMOCoreORB/bin/scripts
EDITED="$S/managers/planet/hutta_regions.lua $S/managers/resource_manager.lua $S/screenplays/screenplays.lua $S/mobile/serverobjects.lua $S/mobile/conversations.lua $S/mobile/spawn/hutta/hutta_lowlands_near.lua $S/mobile/spawn/hutta/hutta_lowlands_mid.lua $S/mobile/spawn/hutta/hutta_deep_swamp.lua"
NEW="$S/screenplays/sandbox/hutta_life.lua $S/screenplays/sandbox/hutta_life_places.lua $S/mobile/sandbox/hutta_life.lua $S/mobile/conversations/sandbox/hutta_life_conv.lua"
echo "HEAD $($G rev-parse --short HEAD)"
for f in $EDITED; do mkdir -p $W/a/$(dirname $f) $W/b/$(dirname $f); $G show HEAD:$f > $W/a/$f; cp $W/a/$f $W/b/$f; done
python3 -I $L/tools/edit_dev.py $W
OUT=$L/core3-dev-nal-hutta-life.patch
( cd $W
  for f in $EDITED; do echo "diff --git a/$f b/$f"; diff -u --label a/$f --label b/$f a/$f b/$f || true; done
  for f in $NEW; do echo "diff --git a/$f b/$f"; echo "new file mode 100644"; diff -u --label /dev/null --label b/$f /dev/null $L/server/$f || true; done
) > $OUT
$G apply --check $OUT && echo "git apply --check: OK"
$G apply --stat $OUT
for f in $EDITED; do luac5.1 -p $W/b/$f 2>/dev/null || luac -p $W/b/$f; done
for f in $NEW; do luac5.1 -p $L/server/$f 2>/dev/null || luac -p $L/server/$f; done
echo "luac -p: OK on $(echo $EDITED $NEW | wc -w) files"
