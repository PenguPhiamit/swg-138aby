"""Read selected public game-mechanics source; never reads config or account data."""
from pathlib import Path
import argparse
import json
import hashlib
import subprocess

p = argparse.ArgumentParser()
p.add_argument("root")
p.add_argument("spec")
p.add_argument("--manifest", action="store_true", help="Print file hashes/ranges rather than source text")
args = p.parse_args()
root = Path(args.root).resolve()
manifest = []
for entry in json.loads(Path(args.spec).read_text(encoding="utf-8")):
    path = (root / entry["file"]).resolve()
    if root not in path.parents or path.suffix not in {".cpp", ".h", ".lua", ".idl"}:
        raise ValueError("Only explicit source files inside root are permitted")
    lines = path.read_text(encoding="utf-8").splitlines()
    if args.manifest:
        manifest.append({**entry, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "line_count": len(lines)})
        continue
    selected = set()
    for start, end in entry.get("ranges", []):
        selected.update(range(start - 1, min(end, len(lines))))
    for i, line in enumerate(lines):
        if any(term.lower() in line.lower() for term in entry.get("terms", [])):
            selected.update(range(max(0, i-entry.get("before", 2)), min(len(lines), i+entry.get("after", 4)+1)))
    print("\nFILE " + entry["file"])
    previous = -2
    for i in sorted(selected):
        if i != previous + 1:
            print("...")
        print(f"{i+1}: {lines[i]}")
        previous = i
if args.manifest:
    pin = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    print(json.dumps({"source_pin": pin, "root": str(root), "files": manifest}, indent=2))
