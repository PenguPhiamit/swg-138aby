# Mynock den, option 2: an outdoor den (no client change)

Fable, 14 Oct 2026. The alternative to batch B's option 1 (the spawned ice cave plus a terrain patch in
`local_planets.tre`). This one is server Lua only: the same 23 creatures (15 ice mynocks, 7 greater ice mynocks, the
broodmother on an 1800 s respawn, the rest 420 s, as in Bellum Gero's cave den, AGPL-3.0, credited in batch B) laid out
by us on the open snow at the same site, (-2000, -4800) in `hoth_mynock_fields_south`, around 18 stock ice props:
three `cave_column_ice_style_01..03` at the centre, nine `cave_stalagmite_ice_style_01..09` in a ring at 18 m and six
more at 34 m. The broodmother stands among the columns, the greater mynocks ring her at 12 m, the ice mynocks at
26 m and 44 m. Heights from the Core3 height port validated on Hoth: 39.6-45.0 m across the site, steepest 10 m
step 0.72 m (`checks.json`). Every prop has a server template in Core3-dev and the client has the objects
(stock `data_other_00.tre`); luac5.3 passes (`work/dev-check.txt`).

Pick one option: option 1 keeps the interior and Bellum's 22 cell-local positions but needs the terrain patch and a
client look at the cave mouth; option 2 needs nothing on the client and loses the interior. Do not load both
(`poi/hoth_mynock_den.lua` and `poi/hoth_mynock_den_outdoor.lua`).

```
bash /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-batchB/den-outdoor/apply.sh --selftest
bash /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-batchB/den-outdoor/apply.sh --check    # 1 copy, 1 patch, 0 refused today
bash /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-batchB/den-outdoor/apply.sh
```

Copies `screenplays/poi/hoth_mynock_den_outdoor.lua` and adds its include after the camps line in `screenplays.lua`.
Bot check: search within 60 m of (-2000, -4800) for `hoth_mynock_broodmother` (1), `hoth_greater_ice_mynock` (7),
`hoth_ice_mynock` (15) and 18 `object/static/structure/general/cave_*_ice_style_*` props. Note the site is inside
batch A's `hoth_mynock_fields_south` spawn area (scripted spawns ignore spawn areas), so wild mynock packs can wander
through; the broodmother is the den's only unique creature.
