# How to see the first outside-art prop (F86), 15 Oct 2026, Claude

**The piece:** Quaternius' `Wall_Broken` (CC0, Ultimate Modular Ruins), 976 triangles, about 2 m wide, 2 m high, 0.28 m thick, two flat colours (dark and light grey-green, the pack's own materials; the pack has no texture atlas).

**How it is wired (test archive only):** it replaces the appearance of the stock *fresh campfire log*, so the stock campfire object shows our wall. No server change, no restart, no new object template. Every campfire in a test session looks like the wall; live sessions are untouched (they do not load `local_planets.tre`).

## Steps

1. Close the client if it is open. Double-click `Play SWG Test Galaxy.cmd` (the test galaxy must be up; the launcher tells you if it is not). It loads `local_planets.tre`, which now holds the wall.
2. Log in with your usual account and character. You need your GM/admin level for step 3.
3. Stand somewhere open and flat (outside, not in a building) and type in the chat box:

   `/createSpawningElement spawn object/static/structure/general/campfire_fresh.iff`

   The object appears at your feet (if it lands inside you, step sideways).
4. Look at it. What a pass looks like: a broken grey-green stone wall, lit by the sun, no flicker, standing on the ground, its two tones visible (the lighter one on the edges and capstones).
5. Walk up to it and into it. Expect to walk **through** it: the exporter writes no collision (known, in the plan).
6. To remove it: `/createSpawningElement delete <object id>` (target it and use its id), or `/createSpawningElement deleteall`.

## What to tell me

- Draws and looks right: say so.
- Invisible or a black or white block: probably the shader or the texture; tell me what you saw.
- Client crash on log-in or when spawning: copy the newest `SWGEmu.exe-stage...txt` from `SWG-client/` and tell me the time. Put the previous archive back with: copy `Local-content\old-client-local_planets.tre.8ad04fec` over `SWG-client\local_planets.tre`.
- If the spawn command says the template is unknown or you lack rights, tell me; the other route is a server template, which needs a restart by whoever holds the galaxy.

## What was done, for the record

| Step | Result |
|---|---|
| Tools | Blender 3.6.23 portable (official site, SHA-256 matches), add-on io_scene_swg 3.1.4 from the repo copy, Microsoft texconv (valid Microsoft signature). Recorded as F86a, F86b, F86c in `Content-catalogue/archive-downloads.json`. |
| Mesh | `convert_ruin.py` (Blender headless): import the OBJ, constant UV (the pack has none), materials named after the shaders, export with the add-on. The exporter's structure matches stock (MESH/0005, SPS, VTXA, INDX). |
| Texture | two flat-colour 256x256 PNGs, sRGB of the pack's two material colours, `texconv -f BC1_UNORM -m 0`: DXT1, 9 mips. |
| Shader | two clones of stock `eqp_camping_ground_fresh_as8.sht` with the texture path replaced (`a_simple.eft`). |
| Stage | `stage_ruin.py`: adds `appearance/mesh/fable_ruin_01.msh`, `appearance/fable_ruin_01.apt`, two `.sht`, two `.dds`, and the override `appearance/eqp_camping_log_fresh.apt` to the client's `local_planets.tre` (166 -> 173 entries, read back byte for byte, reference closure checked). Backup of the previous archive: `Local-content/old-client-local_planets.tre.8ad04fec`. |
| Not done | `shared_fable_ruin_01.iff`, CRC-table entry and server Lua template (they need a server restart to place the piece by its own name); collision; LODs; a real stone texture. |

**Caution for other sessions:** anything that rebuilds `local_planets.tre` from its own staging folder (the Hoth or Ossus builders) drops these files. Re-run `python -I Fable-asset-pipeline/stage_ruin.py <work_dir> --install` afterwards; the converted inputs are in `Fable-asset-pipeline/converted/`.
