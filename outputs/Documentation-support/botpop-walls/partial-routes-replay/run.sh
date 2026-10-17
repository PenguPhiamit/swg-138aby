# Read-only replay of BotPop's meshPath on the test galaxy's navmeshes (partial-routes.md). Run inside WSL as root:
#   bash run.sh            (works in /root/pr; reads /opt/swg, writes nothing there)
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
R=/opt/swg/Core3-dev/MMOCoreORB/src/pathfinding/recast
mkdir -p /root/pr && cd /root/pr
cp /opt/swg/testgalaxy/Core3/MMOCoreORB/bin/databases/navareas.db .   # a copy: the server keeps it open
rm -rf meshes && python3 "$HERE/extract.py" navareas.db meshes | head -3
grep -o '{"[a-z0-9_]*", "[^"]*", -\?[0-9]*, -\?[0-9]*, [0-9]*}' /opt/swg/Core3-dev/MMOCoreORB/src/server/zone/managers/botpop/BotPopLaunch.h \
	| sed 's/{"\([a-z0-9_]*\)", "[^"]*", \(-\?[0-9]*\), \(-\?[0-9]*\), [0-9]*}/\1 \2 \3/' | sed 's/^nal_hutta/hutta/' > cities.txt
nice g++ -O2 -std=c++17 -w -I$R "$HERE/replay.cpp" $R/DetourNavMesh.cpp $R/DetourNavMeshQuery.cpp $R/DetourNode.cpp $R/DetourCommon.cpp $R/DetourAlloc.cpp $R/DetourAssert.cpp -o replay
python3 "$HERE/snapbots.py" snapbots.txt                 # every bot's last snap row: planet x y z
python3 "$HERE/arrive.py" arrivals.txt                   # every travel_done landing, and who left it
./replay snapbots.txt meshes 8192 | grep -v '^   bot at'  # as the code is (69f5c879)
FIX=1 ./replay snapbots.txt meshes 8192 | grep '^fix\|^ALL'   # with the pocket hop
PIECES=1 ./replay snapbots.txt meshes 8192 > pieces.txt && python3 "$HERE/classify.py" pieces.txt
PIECES=1 ./replay arrivals.txt meshes 8192 > arr_pieces.txt && python3 "$HERE/join.py"
LANDINGS=1 ./replay arrivals.txt meshes 8192 | awk '/LANDING/{l=$0; next} /_city_/{print $1 " :: " l; l=""}'
