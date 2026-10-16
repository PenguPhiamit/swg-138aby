#!/usr/bin/env python3
"""Planet census from the launch simulation's explorers (botpop-launch.jsonl): what they saw, where, and how flat
the ground is. Written for Fable's Ossus points-of-interest pass; any planet the explorers walked works.

  python3 tools/bots/ossus_census.py /opt/swg/testgalaxy/Core3/MMOCoreORB/bin/log/botpop-launch.jsonl \
      --out Bot-reports/launch-sim

Rows read: "seen" (each name once per 256 m square: kind, name, level, x, y, z) and the explorers' "snap" rows
(their position and ground height every snapshot). Writes <planet>-census.md (summary, map, tables, flat ground)
and <planet>-census.csv (every sighting).
"""
import argparse
import csv
import json
import os
import time
from collections import defaultdict

HALF = 8192  # SWG planets run from -8192 to 8192 m
CELL = 512   # map cell
SQ = 256     # census and flatness square


def sq(v, size=SQ):
    return int(v // size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("--planet", default="ossus")
    ap.add_argument("--out", default=".")
    ap.add_argument("--flat-range", type=float, default=4.0, help="max height range (m) in a 256 m square to count as flat")
    ap.add_argument("--flat-samples", type=int, default=4)
    a = ap.parse_args()

    tag = ('"planet":"%s"' % a.planet).encode()
    seen = {}                       # (kind, name, sx, sy) -> row
    heights = defaultdict(list)     # (sx, sy) -> ground heights
    visited = defaultdict(int)      # map cell -> explorer snapshots
    explorers, first, last = set(), None, None

    with open(a.log, "rb") as f:
        for line in f:
            if tag not in line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            e, t = r.get("e"), r.get("t")
            if t:
                first = t if first is None else min(first, t)
                last = t if last is None else max(last, t)
            if e == "seen":
                key = (r.get("kind", "?"), r.get("name", "?"), sq(r["x"]), sq(r["y"]))
                seen.setdefault(key, r)
                if r.get("kind") == "creature" and "z" in r:
                    heights[(sq(r["x"]), sq(r["y"]))].append(r["z"])
            elif e == "snap" and r.get("role") == "explorer":
                explorers.add(r.get("bot"))
                visited[(sq(r["x"], CELL), sq(r["y"], CELL))] += 1
                if "z" in r:
                    heights[(sq(r["x"]), sq(r["y"]))].append(r["z"])

    by_name = defaultdict(list)
    for (kind, name, _, _), r in seen.items():
        by_name[(kind, name)].append(r)

    os.makedirs(a.out, exist_ok=True)
    base = os.path.join(a.out, "%s-census" % a.planet)

    with open(base + ".csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["kind", "name", "lvl", "x", "y", "z"])
        for (kind, name), rows in sorted(by_name.items()):
            for r in rows:
                w.writerow([kind, name, r.get("lvl", ""), int(r["x"]), int(r["y"]), int(r.get("z", 0))])

    # The map: one character per 512 m cell, north at the top.
    n = 2 * HALF // CELL
    grid = [[" "] * n for _ in range(n)]
    for (cx, cy) in visited:
        gx, gy = cx + n // 2, n // 2 - 1 - cy
        if 0 <= gx < n and 0 <= gy < n:
            grid[gy][gx] = "."
    rank = {" ": 0, ".": 1, "c": 2, "L": 3, "S": 4, "B": 5}
    mark = {"creature": "c", "lair": "L", "static": "S", "building": "B"}
    for (kind, _, _, _), r in seen.items():
        ch = mark.get(kind, "S")
        gx, gy = sq(r["x"], CELL) + n // 2, n // 2 - 1 - sq(r["y"], CELL)
        if 0 <= gx < n and 0 <= gy < n and rank[ch] > rank[grid[gy][gx]]:
            grid[gy][gx] = ch

    flat = []
    for (sx, sy), zs in heights.items():
        if len(zs) >= a.flat_samples and max(zs) - min(zs) <= a.flat_range:
            flat.append((len(zs), max(zs) - min(zs), sx, sy, sum(zs) / len(zs)))
    flat.sort(key=lambda f: (-f[0], f[1]))

    fmt = lambda ms: time.strftime("%I:%M %p", time.localtime(ms / 1000)).lstrip("0") if ms else "?"
    out = []
    out.append("# %s census (launch-simulation explorers)" % a.planet.capitalize())
    out.append("")
    out.append("Written by `tools/bots/ossus_census.py` from `%s`, %s. Data from %s to %s (test galaxy, server bots)."
               % (os.path.basename(a.log), time.strftime("%d %b %Y %I:%M %p"), fmt(first), fmt(last)))
    out.append("")
    out.append("- Explorers seen: %d. Map cells visited: %d of %d (512 m cells)." % (len(explorers), len(visited), n * n))
    kinds = defaultdict(int)
    for (kind, _, _, _) in seen:
        kinds[kind] += 1
    out.append("- Sightings (each name once per 256 m square): %s." % (", ".join("%s %d" % kv for kv in sorted(kinds.items())) or "none"))
    out.append("- Ground samples: %d in %d squares of 256 m. Flat: at least %d samples within %.0f m of each other: %d squares."
               % (sum(len(z) for z in heights.values()), len(heights), a.flat_samples, a.flat_range, len(flat)))
    out.append("- Every sighting with coordinates: `%s-census.csv`." % a.planet)
    out.append("")
    out.append("## Map")
    out.append("")
    out.append("One character per 512 m; north up; x from -8192 (left) to 8192. `.` visited, `c` creatures, `L` lair, "
               "`S` static object, `B` building, blank not visited.")
    out.append("")
    out.append("```")
    out.append("+" + "-" * n + "+")
    for row in grid:
        out.append("|" + "".join(row) + "|")
    out.append("+" + "-" * n + "+")
    out.append("```")

    def table(title, kinds_wanted, with_lvl):
        items = [(k, v) for k, v in by_name.items() if k[0] in kinds_wanted]
        if not items:
            return
        out.append("")
        out.append("## " + title)
        out.append("")
        out.append("| Name | Kind | Squares | %sWhere (up to 4, x/y) |" % ("Level | " if with_lvl else ""))
        out.append("|---|---|---|%s---|" % ("---|" if with_lvl else ""))
        for (kind, name), rows in sorted(items, key=lambda kv: -len(kv[1])):
            where = "; ".join("%d/%d" % (r["x"], r["y"]) for r in rows[:4])
            lv = ""
            if with_lvl:
                lvls = [r["lvl"] for r in rows if "lvl" in r]
                lv = ("%d-%d | " % (min(lvls), max(lvls)) if lvls and min(lvls) != max(lvls)
                      else ("%d | " % lvls[0] if lvls else "? | "))
            out.append("| %s | %s | %d | %s%s |" % (name, kind, len(rows), lv, where))

    table("Buildings and static objects", {"building", "static"}, False)
    table("Lairs", {"lair"}, True)
    table("Creatures", {"creature"}, True)
    other = set(k for k, _ in by_name) - {"building", "static", "lair", "creature"}
    table("Other", other, True)

    out.append("")
    out.append("## Flat ground (256 m squares, best sampled first, up to 40)")
    out.append("")
    if flat:
        out.append("| Centre x/y | Height | Range (m) | Samples |")
        out.append("|---|---|---|---|")
        for cnt, rng, sx, sy, z in flat[:40]:
            out.append("| %d/%d | %.0f | %.1f | %d |" % (sx * SQ + SQ // 2, sy * SQ + SQ // 2, z, rng, cnt))
    else:
        out.append("None yet: too few samples per square.")
    out.append("")
    out.append("Heights are the explorers' own ground samples and the creatures' positions; a square counts only where "
               "an explorer or creature stood, so a flat square is flat where it was sampled, not necessarily across all "
               "256 m. No-build circles around towns and POIs are not checked here.")

    with open(base + ".md", "w") as f:
        f.write("\n".join(out) + "\n")
    print("%s.md: %d sightings, %d explorers, %d cells visited, %d flat squares" %
          (base, len(seen), len(explorers), len(visited), len(flat)))


if __name__ == "__main__":
    main()
