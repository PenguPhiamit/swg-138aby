D=/opt/swg/Core3-dev; S=$D/MMOCoreORB/bin/scripts
cd $D && git log --oneline -1
P=/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-species/s4/cpp/species-chiss-human-rig.patch
FILES=$(grep '^+++ b/' $P | sed 's#^+++ b/##')
echo "===== changes to the S4 files since e9094960"; for f in $FILES; do n=$(git log --oneline e9094960..HEAD -- $f | wc -l); echo "$n  $f"; done
O=/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-species/s5/work/orig
for f in $FILES MMOCoreORB/bin/scripts/object/creature/player/objects.lua MMOCoreORB/bin/scripts/object/creature/player/serverobjects.lua MMOCoreORB/bin/scripts/managers/name/name_manager.lua; do mkdir -p "$O/$(dirname $f)"; cp "$D/$f" "$O/$f"; done; echo "copied $(echo $FILES | wc -w) + 3"
echo "===== name_manager species handling"; grep -n 'species\|race\|chiss\|zabrak\|twilek' $S/managers/name/name_manager.lua | head -12
echo "===== creature/player serverobjects + objects tail"; tail -4 $S/object/creature/player/serverobjects.lua; tail -3 $S/object/creature/player/objects.lua | cut -c1-120
echo "===== NameManager species switch in C++"; grep -n 'getSpeciesName\|CreatureObject::HUMAN\|case CreatureObject::' $D/MMOCoreORB/src/server/zone/managers/name/NameManager.cpp | head -8
echo "===== PlayerCreationManager starting locations / species checks"; grep -n 'getRaceID\|getSpeciesID\|startingLocation\|starting_locations\|raceFile' $D/MMOCoreORB/src/server/zone/managers/player/creation/PlayerCreationManager.cpp | head -12
