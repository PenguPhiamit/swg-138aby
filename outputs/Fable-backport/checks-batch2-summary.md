# Batch 2 verification (offline)

- objects: 55; all checks passed: 55; with a problem: 0
- files staged: 22 (10 changed, 12 new)
- client shared .iff present: 55 of 55; winning archives: {'mtg_patch_022.tre': 44, 'mtg_patch_019.tre': 2, 'mtg_patch_023.tre': 8, 'mtg_patch_010_object_01.tre': 1}
- IFF form tags: {'STOT': 35, 'SIOT': 10, 'STAT': 10} (STOT = SharedTangibleObjectTemplate, the class every staged object uses)
- in the merged CRC table (Local-content/local_planets): 55 of 55; in the stock table: 0
- server path or Lua name collisions with Core3-dev: 0
- client name string resolves: 22 of 55 (missing listed in checks.json: client_name_missing)
- includeFile targets missing because of this batch: 0 (already missing in Core3-dev before the batch: 0: -); staged files not reached from object/main.lua: 0
- luac5.3 -p: 22 files checked, 0 failed

