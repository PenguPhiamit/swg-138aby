# The archive builder on our own code (B1–B3) — Fable, 14 Oct 2026

Removes `tools/hoth/hoth_client_build.py`'s last dependency on Bellum Gero's AGPL tools (`stf_tool`, `dt_tool`,
`cstb_tool`, `tre_pack`, `merge_ticket_ui`, and `tre_inventory`'s `read_tre`/`_inflate`, which the builder and
`client_load_order.py` pull in with `exec`). Nothing applied: the patches are proposals, every check ran on scratch
copies. Read-only on /opt/swg. Numbers are mine unless a source is named.

| path | what |
|---|---|
| `tools/hoth_ui.py` | B1: `stage_hoth_ui(stage_dir, base, spot=GALAXY_SPOT)` on `Fable-ossus/o4/tools/ui_inc.py`; `--diff DIR` explains every difference from another build |
| `tools/tre_write.py` | B2: our TRE writer (`pack`, `pack_dir`, `read`, `--selftest [--md5-data]`) |
| `tools/fmt_tools.py` | B3: the five Bellum call shapes on top of `swg_tables`, `trn_iff` and `tre_write`, same bytes out |
| `patch/hoth_client_build.patch`, `patch/client_load_order.patch` | B3: unified diffs (`patch -p1 --dry-run` clean); `patch/*.py` are the patched files, `.orig` the current one |
| `staged/client/ui/*.inc` | B1's Hoth output (byte-identical to the patched builder's) |
| `work/` | `b1-hoth-ui.json` (the diff), `scratch_build.py` + `.log` (the patched builder run), `make_patch.py` |
| `checks.json` | the results below |

## B1. Hoth's UI with ui_inc

`stage_hoth_ui` clones Endor's five ticket elements and the planet-map page for Hoth exactly as `ticket_ui()` /
`planet_map_ui()` do (DataSource, galaxy-map Button, 3D viewer, map Page `ui_map_hoth`, label Text; the
`buttonHoth='map.GalaxyMap.buttonHoth'` code-data line; each right after Endor's; button/viewer/label moved by
`GALAXY_SPOT − (23, 302)`). Against the current staged files (`Local-content/local_planets/ui/`) the diff has **4 hunks
in `ui_ticketpurchase.inc` and 2 in `ui_planet_map.inc`, every one the same thing**: the stock files carry lone
carriage returns inside the multi-line `OnShow`/`OnHide` script attributes (`...\r\r\n`: 14 in the ticket file, 12 in
the map file, the map's in runs of three). Bellum's `load()` does `replace('\r\n','\n').replace('\r','\n')`, so each lone
CR became a line break and the staged files have an extra blank line at each (+14 and +12 bytes). Nothing else differs:
the Hoth blocks are identical line for line. Our output keeps the stock bytes (`base_lines_kept`, CRLF only, 14/4
`\r\r\n` runs preserved).

## B2. The TRE writer

Layout as every stock and MTG archive and as our readers parse it: 36-byte header (`EERT 5000`, count, record-block
offset, record compression and stored size, name compression, stored and unpacked size), file data in record order
(zlib level 9 when smaller, else stored with compressed size 0), the zlib record block (24 bytes a file, sorted by SOE
CRC of the lower-case path), the zlib name block, then 16 bytes a file. **The tail is the MD5 of the bytes as stored**
(patch_14_00: 1489 of 1491 records, patch_00: 8816 of 8830, mtg_planets: all 3328; the rest match nothing), whereas
`tre_pack` stores the MD5 of the unpacked data. Default is the stock rule; `md5_of='data'` reproduces tre_pack's file.
Self-test on `Local-content/local_planets/` (20 files, 770,953 bytes): read back byte-identical by `tre_write.read`
(size, CRC and MD5 checked), `trn_iff.list_tre/open_tre_entry` and `client_load_order.read_tre`; with `--md5-data`
the archive is **byte-identical to `local_planets.tre` (sha256 6cfeeb51…)**; with the stock rule the header and all 20
records are equal and only the 320-byte tail differs (sha256 ea57b68f…).

## B3. The patch

`fmt_tools.py` keeps the builder's data shapes (`stf_tool` dicts with `vals`/`keys` and Bellum's never-reuse-an-id
rule, `dt_tool` `names`/`types`/`rows`, `cstb_tool` name→CRC, `tre_pack.pack(src, out)`, `read_tre`/`_inflate`) so
only the import block, the two UI functions (now `ui_includes()` → `hoth_ui`), `ENDOR_BUTTON`, one `main()` line and
two docstrings change (59 added or removed lines, 102-line diff); `client_load_order.patch` swaps the `exec` for
`from fmt_tools import read_tre, _inflate` (14-line diff). The patched builder was run in a scratch folder (its own STAGE/TRE, the patched loader
registered first; `work/scratch_build.log`): 12 round trips exact, 0 differ, "archive verified", exit 0.
**Before/after:** the same 20 files in staging and in the archive; the only entries whose bytes change are
`ui/ui_ticketpurchase.inc` (99,919 → 99,905) and `ui/ui_planet_map.inc` (47,514 → 47,502), the stray blank lines gone;
the archive's record offset moves by 3 bytes with them and its MD5 tail follows the stock rule (pass `md5_of='data'`
in `fmt_tools.tre_pack.pack` to keep tre_pack's). Type rules agree on every table the builder touches (`I`, `i`,
`i[0]`, `b`, `b[1]`, `e(...)`, `s`: ints, ints, strings in both readers), which the round trips confirm.

After applying: `work/research/.../tools/newplanets` is no longer imported by anything in `tools/`; the docstring credit
line changes accordingly.
