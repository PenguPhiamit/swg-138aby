# Task: six Ossus creatures for a Star Wars Galaxies server (Core3 Lua templates)

The folder `stock/` holds six stock creature templates. Make one new creature from each, following the table below.
Write each new file into the folder `ossus/` with the file name given. Then write `ossus/creature_names.tsv`.

## How to make each file

1. Read the base file from `stock/`.
2. Copy it exactly, then change ONLY these things:
   - the variable name on the first line and in the last line (`CreatureTemplates:addCreatureTemplate(<var>, "<var>")`): use the "var" column;
   - `objectName = "@mob/creature_names:<var>"`;
   - `socialGroup`;
   - `meatType`, `hideType`, `boneType` (the amounts stay as they are);
   - milk: if the table says "none", set `milk = 0` and delete the `milkType` line if there is one; if it says "keep", leave both lines as they are;
   - `creatureBitmask`;
   - `diet` when the table gives one ("base" means leave it).
3. Add one comment line at the very top: `-- Ossus (138-139 ABY): <one short sentence in your own words describing the creature, from the facts column>. Base: stock <base file name>.`
4. Do not change any other line: level, damage, HAM, resists, attacks, templates, hues and everything else stay exactly as in the base.

## The six creatures

| new file | base | var | English name | socialGroup | meatType | hideType | boneType | milk | creatureBitmask | diet | facts |
|---|---|---|---|---|---|---|---|---|---|---|---|
| mud_yak.lua | falumpaset.lua | ossus_mud_yak | Mud Yak | mud_yak | meat_herbivore | hide_wooly | bone_horn | keep | HERD | HERBIVORE | hairy horned grazer about 3 m tall; herds live in swamps and marshes and dig up river roots with downswept horns; timid |
| kirruk.lua | dewback.lua | ossus_kirruk | Kirruk | kirruk | meat_reptilian | hide_scaley | bone_mammal | none | PACK | CARNIVORE | reptilian four-legged predator named for its squawking call; the Ysanna tamed it as a mount |
| gokob.lua | womp_rat.lua | ossus_gokob | Gokob | gokob | meat_wild | hide_leathery | bone_mammal | none | PACK + HERD | base | friendly hairless rodent of the forest canopy; sprays a stinking mist when frightened; steals food from the Jedi academy kitchens |
| ossus_tree_frog.lua | worrt.lua | ossus_tree_frog | Ossus Tree Frog | tree_frog | meat_reptilian | hide_leathery | bone_mammal | none | NONE | base | large brightly coloured tree frog; its long sticky tongue can pull a small training starfighter out of the air |
| tribis.lua | kaadu.lua | ossus_tribis | Tribis | tribis | meat_avian | hide_scaley | bone_avian | none | HERD | base | small two-legged reptavian (part reptile, part bird) |
| kaddyr_bug.lua | bark_mite.lua | ossus_kaddyr_bug | Kaddyr Bug | kaddyr_bug | meat_insect | hide_scaley | bone_mammal | none | PACK | base | chirping insect |

## creature_names.tsv

One line per creature, the var, a tab, then the English name. No header line. Six lines.

## Finish

When all seven files are written, reply with a short list of the files you wrote. Do not change anything in `stock/`.
