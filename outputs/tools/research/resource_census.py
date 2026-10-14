"""C21 saved-manifest baseline. Reads local JSON only; does not inspect live data."""
import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "outputs/Documentation-support/server-resource-census-baseline.json"
INPUTS = {
    "active": "outputs/Content-catalogue/active-content-catalogue.json",
    "mtg": "outputs/Content-catalogue/MTG-file-inventory.json",
    "summary": "outputs/Content-catalogue/MTG-inventory-summary.json",
    "dormant": "outputs/Content-catalogue/dormant-client-objects.json",
    "packages": "outputs/Content-catalogue/downloaded-package-evidence.json",
    "lore": "outputs/Documentation-support/planets-coordinates.json",
}

def counts(values):
    return dict(sorted(collections.Counter(values).items()))

def main():
    data, evidence = {}, {}
    for key, relative in INPUTS.items():
        raw = (ROOT / relative).read_bytes()
        data[key] = json.loads(raw.decode("utf-8-sig"))
        evidence[key] = {"path": relative, "sha256": hashlib.sha256(raw).hexdigest()}
    a, m, s, d, packages, lore = (data[k] for k in INPUTS)
    registered = {p for f in m["files"] for p in f.get("templates", [])}
    assert len(registered) == s["unique_registered_object_paths"]
    assert len(m["files"]) == s["lua_files"]
    dormant = {x["object"] for x in d["objects"]}
    assert len(dormant) == len(d["objects"]) == d["dormant"]
    assert len(a["rows"]) == a["counts"]["entries"]
    zones = {r["zone"] for r in a["rows"] if r.get("local_asset_evidence")}
    lore_zones = {r["zone"] for r in lore["planets"]}
    result = {
        "schema_version": 1,
        "checkpoint": "C21-1; saved manifests, not current server or full rights validation",
        "input_evidence": evidence,
        "active_catalogue": {
            "rows": len(a["rows"]), "by_kind": counts(r["kind"] for r in a["rows"]),
            "by_permission_label": counts(r["status_label"] for r in a["rows"]),
            "local_evidence_zones": sorted(zones),
            "runtime_validated_rows_in_old_catalogue": sum(bool(r.get("runtime_validated")) for r in a["rows"]),
        },
        "mtg": {
            "source_revision": m["revision"], "lua_files": len(m["files"]),
            "lua_files_by_category": counts(f["category"] for f in m["files"]),
            "unique_registered_paths": len(registered),
            "registered_paths_by_prefix": counts("/".join(p.split("/")[:2]) for p in registered),
            "archive_entry_records": m["archive_entry_records"],
            "terrain_paths": len(set(s["terrain_files"])),
            "snapshot_paths": len(set(s["snapshot_files"])),
            "player_object_paths": len(set(s["player_object_files"])),
        },
        "dormant_snapshot": {
            "client_object_paths": d["client_objects"], "server_template_count": d["server_templates"],
            "unique_dormant_paths": len(dormant),
            "by_origin": counts(x["origin"] for x in d["objects"]),
            "by_prefix": counts("/".join(x["object"].split("/")[:2]) for x in d["objects"]),
        },
        "creator_package_records": {
            "packages": len(packages), "member_records": sum(len(x["files"]) for x in packages),
            "archive_bytes": sum(x["bytes"] for x in packages),
            "note": "Manifest records; no new ZIP integrity/hash verification or blanket import clearance",
        },
        "inherited_lore_batch": {
            "records": len(lore["planets"]),
            "by_continuity": counts(x["continuity"] for x in lore["planets"]),
            "local_evidence_zones_matched": sorted(zones & lore_zones),
            "local_evidence_zones_unmatched": sorted(zones - lore_zones),
            "note": "C14 search-extract evidence only; full-page access and citations remain unverified",
        },
    }
    OUT.write_bytes((json.dumps(result, indent=2, ensure_ascii=False) + "\n").replace("\n", "\r\n").encode("utf-8"))
    print(json.dumps(result, indent=2, ensure_ascii=True))

if __name__ == "__main__":
    main()
