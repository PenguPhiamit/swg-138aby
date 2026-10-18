#!/bin/sh
# git apply --check + luac for the S6 patch in a throw-away repo (never in h/ or /opt/swg). Run: wsl -d Debian -e sh gitcheck.sh
set -e
S6=/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-species/s6
T=$(mktemp -d)
cd "$T"
git init -q .
for f in MMOCoreORB/src/server/zone/objects/player/Races.h MMOCoreORB/src/server/zone/objects/creature/CreatureObject.idl \
         MMOCoreORB/src/server/zone/managers/director/DirectorManager.cpp MMOCoreORB/bin/scripts/managers/player_creation_manager.lua \
         MMOCoreORB/bin/scripts/object/creature/player/objects.lua MMOCoreORB/bin/scripts/object/creature/player/serverobjects.lua \
         MMOCoreORB/bin/scripts/object/creature/player/chiss_male.lua MMOCoreORB/bin/scripts/object/creature/player/chiss_female.lua; do
  mkdir -p "$(dirname "$f")"
  cp "$S6/work/orig/$f" "$f"
done
git add -A && git -c user.name=f -c user.email=f@f commit -q -m base
git apply --check "$S6/patch/species-s6.patch" && echo "git apply --check: ok"
git apply "$S6/patch/species-s6.patch"
for f in MMOCoreORB/bin/scripts/managers/player_creation_manager.lua MMOCoreORB/bin/scripts/object/creature/player/objects.lua \
         MMOCoreORB/bin/scripts/object/creature/player/serverobjects.lua MMOCoreORB/bin/scripts/object/creature/player/nautolan_male.lua \
         MMOCoreORB/bin/scripts/object/creature/player/togruta_female.lua; do
  luac5.3 -p "$f" && echo "luac5.3 -p ok: $f"
done
git status --short | wc -l
cd /
rm -rf "$T"
echo "scratch removed"
