set -e
P=/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-species/s5/patch/species-chiss.patch
T=$(mktemp -d); cd "$T"; git init -q .; git config user.email f@x; git config user.name f
for f in $(grep '^+++ b/' "$P" | sed 's#^+++ b/##'); do if [ -f "/opt/swg/Core3-dev/$f" ]; then mkdir -p "$(dirname "$f")"; cp "/opt/swg/Core3-dev/$f" "$f"; fi; done
git add -A; git commit -q -m base
git apply --check "$P" && echo "git apply --check: clean"
git apply "$P"; git diff --stat HEAD | tail -12
for f in MMOCoreORB/bin/scripts/object/creature/player/objects.lua MMOCoreORB/bin/scripts/object/creature/player/serverobjects.lua MMOCoreORB/bin/scripts/object/creature/player/chiss_male.lua MMOCoreORB/bin/scripts/object/creature/player/chiss_female.lua MMOCoreORB/bin/scripts/managers/player_creation_manager.lua; do luac5.3 -p "$f" && echo "luac ok $f"; done
cd /; rm -rf "$T"
echo "===== NameManager default"; sed -n '305,322p' /opt/swg/Core3-dev/MMOCoreORB/src/server/zone/managers/name/NameManager.cpp | grep -n 'default\|return' | head -4
echo "===== Races.h hunk: existing ids untouched?"; grep -n '^-' "$P" | grep -v '^[0-9]*:---' | head -20
