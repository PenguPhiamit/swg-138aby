# Ossus O4: ready to pack in one step — Fable, 14 Oct 2026

`stage_ossus(stage_dir, base)` writes every Ossus client file on top of whatever is already staged (Hoth's copies of
the shared files), with the owner's open decisions kept as named placeholders (question 10: the fares and the galaxy-map
spot). Our own code throughout (no Bellum tools); self-tested on scratch copies of `Local-content/local_planets/` and of
the stock base. Read-only on /opt/swg; numbers are mine unless a source is named.

## O4a. The ticket-purchase and planetary-map UI (`tools/ui_inc.py`)

`add_planet(ticket, planet_map, 'Ossus', 'ossus', 'ui_planet_sel_ossus.apt', 'ui_map_ossus', spot, after='Hoth')` clones
Endor's five ticket elements (`DataSource` with the planet model, the galaxy-map `Button`, the `CuiWidget3dObjectListViewer`
3D planet, the map `Page` with `SourceResource='ui_map_ossus'` (O3's 1024 map, `SourceRect 0,0,1024,1024`), the label
`Text`) plus the code-data line `buttonOssus='map.GalaxyMap.buttonOssus'`, and the planet-map `Page` `ossus`; each goes
in right after Hoth's element when Hoth is there, else after Endor's. The button, 3D planet and label move together by
(spot − Endor's 23,302), the stock offsets (+4,+4 and +8,−4) preserved. **Spot placeholder (425, 290)**: directly below
Hoth's provisional (425, 225); the button is 61x59 so the two do not overlap. Lines are split on the raw `\r\n` and only
inserted, never rewritten: 79 lines in the ticket file (DataSource 8, Button 11, 3D planet 20, Page 20, Text 19, the
code-data line), 22 in the map file.

Note for your builder: the stock files carry bare carriage returns inside the multi-line `OnShow`/`OnHide` scripts
(14 `\r\r\n` in `ui_ticketpurchase.inc`, 4 in `ui_planet_map.inc`). Bellum's `load()` splits on them too, so your Hoth
copies have an extra blank line at each (harmless, but the files differ from stock beyond the Hoth blocks). Mine keeps
the base bytes as they are, whichever copy it starts from.

## O4b. `waypoint_planets.iff`

The `ossus` row now names `ui_planet_sel_ossus.apt` (O3's globe), inserted after `hoth` (else `yavin4`); an earlier
placeholder row (O1's `ui_planet_sel_dant.apt`) is updated in place.

## O4c. `stage_ossus(stage_dir, base)` (`tools/stage_ossus.py`)

`base(name) -> bytes | None` must give the staged copy when one exists, else the client's winning copy
(`staging_base(folder)` does that; your `winning()` plus a staging lookup is the same thing). Shared files, each
round-tripped before it is changed and merged idempotently:

| file | what is added | kept |
|---|---|---|
| `misc/planet_crc_string_table.iff` | `ossus` (CRC f270b502), CRC order kept ascending | every entry (`hoth` included) |
| `datatables/travel/travel.iff` | column + row: Corellia→Ossus 3000, Ossus→Corellia 1750, Ossus→Ossus 100 (placeholders) | every column, row and cell |
| `string/en/planet_n.stf` | `ossus` "Ossus" | every key and text |
| `datatables/player/waypoint_planets.iff` | `ossus` / `ui_planet_sel_ossus.apt` after `hoth` | every row |
| `ui/ui_ticketpurchase.inc`, `ui/ui_planet_map.inc` | the O4a blocks | every base line, in order |
| `datatables/resource/resource_tree.iff` | the 45 Ossus rows (dantooine's cloned, O2c rule), ancestors' type counts raised | every row; non-count cells unchanged |

Ossus-only files are copied from the earlier batches' staged output (18 files): O1 terrain (`terrain/ossus.trn`, 3 TGAs,
`terrain/environment/ossus.iff`), O1c `datatables/environment|clientregion/ossus.iff`, `string/en/ossus_region_names.stf`,
`string/en/loading/ossus*.stf`, O2a `snapshot/ossus.ws`, O3 art (`texture/ui_map_ossus.dds`, the globe chain, the loading
tile and the loading table). The report lists every file with bytes and sha256, the placeholders and the notes
(`include_resources=False` leaves the tree alone; the server needs the same tree and `ossus` in `activeZones`).

`--selftest`: a scratch copy of your current staging → stage → `verify()` (every base entry kept, Ossus present, UI files
only grew, CRLF only, bare CRs unchanged) → a second pass on the result reports every shared file "present" with
identical bytes; the same on the stock base (no Hoth) passes too, with `hoth_kept` false as expected. `staged/client/`
is the result on your staging as of today (checks.json = report + verify): Hoth's entries kept everywhere, Ossus added
once; 12 planets in the ticket UI, travel columns `... yavin4, hoth, ossus`.

## Still placeholders / your side

Fares and the galaxy-map spot (question 10); `PLACEHOLDERS` at the top of `stage_ossus.py` is the one place to set them.
The O1 `placeholders.json` entry `planet_model` is superseded by O4b. Untested in a client: the globe with a 32-bit
texture (O3 note). The server side (planet entry, regions, fauna, lairs, resources, activeZones) is O2b/O2c's `apply.sh`.
