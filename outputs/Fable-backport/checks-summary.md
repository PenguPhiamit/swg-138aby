# Batch 1 verification (offline)

- objects: 1090; all checks passed: 1090; with a problem: 0
- files staged: 1100 (1081 changed, 19 new)
- client shared .iff present: 1090 of 1090; winning archives: {'mtg_patch_022.tre': 1088, 'mtg_patch_019.tre': 2}
- IFF form tags: {'STOT': 1088, 'STAT': 2} (STOT = SharedTangibleObjectTemplate, the class every staged object uses)
- in the merged CRC table (Local-content/local_planets): 1090 of 1090; in the stock table: 0
- server path or Lua name collisions with Core3-dev: 0
- client name string resolves: 775 of 1090 (missing listed in checks.json: client_name_missing)
- includeFile targets missing because of this batch: 0 (already missing in Core3-dev before the batch: 0: -); staged files not reached from object/main.lua: 0
- luac5.3 -p: 1100 files checked, 0 failed

