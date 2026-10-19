# C65 read-only format notes, 18 October 2026

Universal Modder reverse-engineering skill applied to H1's stock-layout audit. No game binaries/assets were copied, modified, imported or published. Source search/Git ran inside WSL as swgemu; no galaxy control or compilation.

- Engine pin: `0262d8de`; relevant readers are `src/templates/appearance/PortalLayout.cpp`, `CellProperty.cpp`, `FloorMesh.cpp`.
- Use the project's existing `outputs/tools/swgfmt/trn_iff.py` IFF/TRE reader. IFF tags/sizes are big endian, chunk payload values little endian. POB's supported `PRTO` versions are `0003`/`0004`; cell versions `0004`/`0005`.
- Cell DATA: 4-byte portal count, one byte, NUL cell name, NUL appearance filename, one-byte floor-present flag, then NUL floor filename when present. The audit follows this flag, rather than collecting arbitrary filename-looking bytes.
- Supported floor versions: `FLOR 0003`, `0005`, `0006`. VERT holds float32 XYZ triples; TRIS holds 60-byte records with three int32 indices at offset 0. Version 0006 prefixes VERT/TRIS with counts.
- The engine builds its AABB from triangle vertices, not unused vertices. Measure horizontal X/Z absolute extrema of referenced vertices and take hypot; use maximum per-cell corner, not a combined AABB from different cells.
- Reader/writer roundtrip conserves all examined supported POB/FLR bytes; this is format-reader verification, not a game test or asset conversion.
- Audit: 223 stock and 69 MTG winning layouts; 55 supported stock layouts exceed 96 m. Two zero-byte test layouts have no floors; three PRTO 0001 layouts are rejected by the engine too. No unexplained parse errors.
- Reproduction: WSL swgemu, `nice -n 19 python3 .../review-C62/audit_h1_reach.py`. Exact layout names, mapped building templates, limiting floors, SHA-256 fingerprints and calculated ranges are in `H1-stock-buildings.md`.
- Runtime boundary: old serialized TreeEntry.radius can overwrite freshly derived reach; see C65 N2. No database/runtime benchmark performed.
