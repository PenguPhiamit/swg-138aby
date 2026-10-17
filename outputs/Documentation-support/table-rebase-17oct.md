# Table rebase check, 17 Oct (speeders invisible and uncallable, run 27)

Claude, 17 Oct, on archive `b01e9f44` (`work/nal-hutta-life/local_planets-nalhutta-life.tre`). Read-only; nothing built
to install, because nothing was missing.

**Finding: the overridden tables are not the cause.** No stock vehicle lost a row.

- **Mount tables** (`datatables/mount/*`): ours are a key superset of both the stock winner (`patch_11_02`) and
  MTG's newest (`mtg_patch_022`). Every stock speeder resolves end to end in ours: appearance, saddle lookup, saddle
  appearance, rider pose and scale row. That covers the X31 and X34 (both `pv_landspeeder_luke.sat`), the speeder
  bike, the swoop, the AV-21 and the jetpack.
  - The byte and row gap the main session saw comes from MTG 022's duplicate keys. It has a second rider-pose row for
    the swamp speeder, the hoverlifter and the AT-RT camo, naming poses `vehicle_swamp_speeder`, `vehicle_hoverlifter`
    and the misspelt `vehichle_at_rt`. MTG's own local_planets dropped those rows too.
  - There are two value differences. Ours has nerf saddle `x` and bantha minimum scale 0.6, where MTG 022 has a saddle
    lookup and 0.5. Neither is a speeder.
  - `tools/build_table_rebase.py` adds any missing key and asserts both supersets. On `b01e9f44` it writes an archive
    byte-identical to the base (`work/table-rebase/checks.json`).
- **Customization tables** (`customization_data`, `customization_group_instance`, `palette_columns`, `allow_bald`,
  `hair_assets_skill_mods`): ours keep every row of the stock winner (`patch_09`/`patch_11_00`), plus the Chiss and
  Hutt rows. MTG 023's bigger copies sit at search priority 23, below every stock archive (24 and up). So the client
  has never read their extra rows, with or without our archive. Rebasing onto them would add NGE rows the client has
  never loaded, so they were left alone.
- **Template CRC table** (`misc/object_template_crc_string_table.iff`, changed for the ice rancor): 29,359 entries, all
  sorted, every CRC matching its name. It is a superset of MTG 023 and of stock `patch_14_00`, and all 539 vehicle
  templates are present.

**So look elsewhere for the invisible speeders:** the server side of the call, the vehicle's customization (Core3
sets `/private/index_hover_height`), or the Wookiee/god-mode case. Rows missing from tables are ruled out.
