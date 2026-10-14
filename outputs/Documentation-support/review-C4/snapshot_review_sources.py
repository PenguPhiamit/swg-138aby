"""Read pinned tracked source only; write review copies inside this folder, never /opt/swg."""
import hashlib
import json
from pathlib import Path
import subprocess

REPO = "/opt/swg/Core3-dev"
REV = "697f2002"
OUT = Path(__file__).resolve().parent / "sources"
NAMES = {
    "AgentControl.cpp", "AgentControl.h", "ZonePacketHandler.cpp", "AgentPathCommand.h",
    "ObjectMenuRequest.h", "ObjectMenuResponse.h", "ObjectMenuSelect.h",
    "SuiCreatePageMessage.h", "SuiEventNotificationCallback.h", "SuiForceClosePage.h",
    "NpcConversationMessage.h", "ChatParameter.cpp", "StringIdChatParameter.cpp",
    "CreatureObjectMessage3.h", "CreatureObjectMessage6.h",
    "CreatureObjectDeltaMessage3.h", "CreatureObjectDeltaMessage6.h",
    "TangibleObjectMessage3.h", "TangibleObjectMessage6.h",
    "DeltaMessage.h", "DeltaVector.h", "CombatSpam.h", "Transform.h",
    "RadialOptions.h", "CreatureState.h",
    "PathFinderManager.cpp", "PathFinderManager.h", "WorldCoordinates.h",
    "CollisionManager.cpp", "LuaCreatureObject.cpp", "CreatureObjectImplementation.cpp",
    "AiAgentImplementation.cpp", "PlayerManagerImplementation.cpp", "AccountManager.cpp",
    "sandbox_world_bosses.lua", "sandbox_big_game_hunter_conv.lua",
    "DataTransformWithParent.h", "DataTransform.h",
    "CreatureManagerImplementation.cpp", "TangibleObjectImplementation.cpp",
    "StringIdChatParameter.h", "SuiPageData.cpp", "SuiPageData.h", "SuiCommand.h",
    "MissionListRequestCallback.h", "ThreatMap.cpp", "ThreatMap.h", "COPYING",
}


def git(*args):
    return subprocess.check_output(["git", "-C", REPO, *args])


def main():
    commit = git("rev-parse", REV).decode().strip()
    paths = git("ls-tree", "-r", "--name-only", commit, "MMOCoreORB/src", "MMOCoreORB/bin/scripts", "COPYING").decode().splitlines()
    chosen = [p for p in paths if Path(p).name in NAMES]
    rows = []
    for rel in chosen:
        data = git("show", f"{commit}:{rel}")
        target = OUT / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        rows.append({"path": rel, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    record = {"commit": commit, "source": REPO, "files": rows,
              "unmatched_names": sorted(NAMES - {Path(p).name for p in chosen})}
    (OUT.parent / "snapshot-manifest.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    commits = ["e1344def", "a72026b6", "eebdd99d", "5c39f411", "697f2002", "bda2c0dd"]
    meta = []
    for rev in commits:
        text = git("show", "--no-patch", "--format=%H%n%P%n%B", rev).decode()
        changed = git("diff-tree", "--no-commit-id", "--name-only", "-r", rev).decode().splitlines()
        meta.append({"commit": rev, "metadata": text, "changed_paths": changed})
    (OUT.parent / "commit-metadata.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"commit": commit, "copied_files": len(rows),
                      "bytes": sum(r["bytes"] for r in rows), "unmatched_names": record["unmatched_names"]}))
    print(json.dumps({"mission_packet_candidates": [p for p in paths if "packets" in p and "Mission" in p and "List" in p]}))


if __name__ == "__main__":
    main()
