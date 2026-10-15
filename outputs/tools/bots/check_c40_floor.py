"""Compile the actual C40 floor selector with collision stubs, outside the server build.
Run in WSL: python3 -I check_c40_floor.py /opt/swg/Core3-gpt
Synthetic surfaces reproduce the reported coordinates; this does not load real terrain.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(sys.argv[1])
source = (root / 'MMOCoreORB/src/server/zone/objects/creature/commands/AgentPathCommand.h').read_text()
a = source.index('static float floorNear(')
b = source.index('\n\tJSONSerializationType findPath', a)
method = source[a:b]
harness = r'''#include <cmath>
#include <vector>
#include <cassert>
#include <iostream>
struct IntersectionResult { float z; float getIntersectionDistance() const { return 16384.f-z; } };
template<class T> struct SortedVector {
 std::vector<T> rows;
 int size() const { return rows.size(); }
 T get(int i) const { return rows.at(i); }
};
struct Terrain { float height=5; float getHeight(float, float) { return height; } };
struct Planet { Terrain terrain; Terrain* getTerrainManager() { return &terrain; } };
struct Zone { Planet planet; std::vector<float> floors; Planet* getPlanetManager() { return &planet; } };
struct CollisionManager { static void getWorldFloorCollisions(float, float, Zone* z, SortedVector<IntersectionResult>* out) {
 for(float height:z->floors) out->rows.push_back({height});
} };
struct Selector {
''' + method + r'''
};
int main() {
 Zone z; z.floors={9.5f, 5.f};
 // Old highest-surface rule reproduces the owner's 9.5 instead of 5.
 float old=5; for(float h:z.floors) if(h>old) old=h;
 assert(old==9.5f);
 assert(Selector::floorNear(3536,-4796,5,&z)==5);
 assert(Selector::floorNear(3536,-4796,9.5,&z)==9.5f);
 assert(Selector::floorNear(3536,-4796,7.25,&z)==5); // ties go down
 z.floors.clear();
 assert(Selector::floorNear(3545,-4796,9.5,&z)==5); // roof -> clear ground
 z.planet.terrain.height=180;
 assert(Selector::floorNear(0,0,5,&z)==180); // real plateau, not a global height cap
 z.planet.terrain.height=5; z.floors={9.5f,14.f};
 assert(Selector::floorNear(0,0,9.5,&z)==9.5f); // stacked exterior floors
 z.planet.terrain.height=-20; z.floors={-12.f,0.f,9.5f};
 assert(Selector::floorNear(0,0,-12,&z)==-12); // subterranean outside-world surface
 std::cout << "C40 actual selector: old roof choice reproduced; 7 floor assertions passed\n";
}
'''
with tempfile.TemporaryDirectory(prefix='c40-') as temp:
    cpp, exe = Path(temp)/'floor.cpp', Path(temp)/'floor'
    cpp.write_text(harness)
    subprocess.run(['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror', str(cpp), '-o', str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
