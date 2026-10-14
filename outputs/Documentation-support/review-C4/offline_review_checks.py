"""Offline source checks and a compiled reproduction; never connects to a galaxy."""
import json
from pathlib import Path
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
SRC = HERE / "sources" / "MMOCoreORB" / "src"
CLIENT = SRC / "client/agent/AgentControl.cpp"
HELPER = SRC / "server/zone/objects/creature/commands/AgentPathCommand.h"


def main():
    client = CLIENT.read_text()
    helper = HELPER.read_text()
    manifest = json.loads((HERE / "snapshot-manifest.json").read_text())
    import hashlib
    for row in manifest["files"]:
        data = (HERE / "sources" / row["path"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == row["sha256"], row["path"]
    metadata = json.loads((HERE / "commit-metadata.json").read_text())
    checked_commits = []
    for patch in sorted(HERE.rglob("*.patch")):
        text = patch.read_text()
        commit = re.match(r"From ([0-9a-f]{40})", text).group(1)
        meta = next(row for row in metadata if row["metadata"].startswith(commit))
        changed = re.findall(r"^diff --git a/(.+) b/.+$", text, re.M)
        assert sorted(changed) == sorted(meta["changed_paths"]), patch.name
        assert "Agent: Claude" in meta["metadata"], commit
        checked_commits.append(commit)
    enum = (SRC / "server/zone/managers/radial/RadialOptions.h").read_text()
    enum = re.sub(r"//[^\n]*|/\*.*?\*/", "", enum, flags=re.S)
    entries = enum.split("enum {", 1)[1].split("};", 1)[0].split(",")
    expected = [x.strip().lower() for x in entries if x.strip()]
    names = client.split("static const char* radialNames[] = {", 1)[1].split("};", 1)[0]
    actual = re.findall(r'"([^\"]+)"', names)
    mismatches = [{"id": i, "server": expected[i], "client": name}
                  for i, name in enumerate(actual) if i >= len(expected) or expected[i] != name]
    assert not mismatches, mismatches

    # Compile the exact server point-expansion block with minimal containers and terrain stubs.
    # This executes the reviewed loop, not a Python translation of it.
    start = helper.index("\t\tJSONSerializationType points =")
    end = helper.index("\n\t\tdelete path;", start)
    block = helper[start:end]
    harness = r'''
#include <array>
#include <cmath>
#include <iostream>
#include <vector>
namespace Math { float sqrt(float x) { return std::sqrt(x); } }
struct CellObject { unsigned long getObjectID() const { return 1; } };
struct WorldCoordinates {
 float x,y,z; CellObject* cell=nullptr;
 float getX() const{return x;} float getY() const{return y;} float getZ() const{return z;}
 CellObject* getCell() const{return cell;}
};
template<class T> struct Vector : std::vector<T> {
 using std::vector<T>::vector;
 const T& get(int i) const{return (*this)[i];}
};
struct Number { double v; template<class T> Number(T x):v(static_cast<double>(x)){} };
struct JSONSerializationType {
 std::vector<std::array<double,4>> values;
 static JSONSerializationType array(){return {};}
 std::size_t size() const{return values.size();}
 void push_back(std::initializer_list<Number> row){
  std::array<double,4> a{}; int i=0; for(auto n:row) a[i++]=n.v; values.push_back(a);
 }
};
struct CollisionManager {static float getWorldFloorCollision(float,float,int*,bool){return 0;}};
std::size_t flatten(Vector<WorldCoordinates>* path) {
 int* zone=nullptr;
''' + block + r'''
 return points.size();
}
int main(){
 Vector<WorldCoordinates> straight{{0,0,0},{2048,0,0}};
 Vector<WorldCoordinates> corner{{0,0,0},{1600,0,0},{1600,1000,0}};
 std::cout << "{\"straight_2048m_points\":" << flatten(&straight)
           << ",\"corner_points\":" << flatten(&corner) << "}\n";
}
'''
    cpp = HERE / "point_cap_repro.cpp"
    exe = HERE / "point_cap_repro"
    cpp.write_text(harness)
    compiler = shutil.which("g++")
    if not compiler:
        raise RuntimeError("g++ unavailable; compiled reproduction was not run")
    subprocess.run([compiler, "-std=c++17", "-O0", str(cpp), "-o", str(exe)], check=True, capture_output=True, text=True)
    cap = json.loads(subprocess.check_output([str(exe)], text=True))
    assert cap["straight_2048m_points"] == 257 and cap["corner_points"] == 326, cap

    move = client.split('if (cmd == "move" || cmd == "path")', 1)[1].split('if (cmd == "height")', 1)[0]
    assert "leg <= 25" in move and 'walkPath(plan["points"], speed, timeout)' in move
    assert "Time started" not in move
    walk = client.split("JSONSerializationType AgentControl::walkPath", 1)[1].split("JSONSerializationType AgentControl::fight", 1)[0]
    direct = client.split("JSONSerializationType AgentControl::moveTo", 1)[1].split("JSONSerializationType AgentControl::askHelper", 1)[0]
    assert "posture == 13 || posture == 14" in direct
    assert "posture" not in move and "posture" not in walk
    current_mcp = (HERE.parents[1] / "tools/agent/mcp_server.py").read_text()
    assert "}, 100)" in current_mcp.split("def t_move_to", 1)[1].split("def t_say", 1)[0]

    record = {
        "scope": "Offline only; no game connection, protocol replay, full client build or deployment",
        "pinned_commit": "697f2002e01c65130bed9f9c7aea69855953ee6a",
        "snapshot_files_verified": len(manifest["files"]),
        "export_commit_ids_and_path_lists_verified": checked_commits,
        "radial_labels_compared": len(actual), "radial_label_mismatches": mismatches,
        "point_cap_compiled_from_reviewed_loop": cap, "advertised_cap": 256,
        "timeout_source_check": {
            "legs_allowed": 25, "per_leg_default_seconds": 90,
            "current_mcp_wait_seconds": 100,
            "illustrative_two_55_second_legs_total": 110,
            "note": "Timing arithmetic and exact-source structure check, not a wall-clock/game run"
        },
        "dead_incap_guard": {"straight_moveTo": True, "path_dispatch_or_walkPath": False}
    }
    (HERE / "offline-review-results.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record))


if __name__ == "__main__":
    main()
