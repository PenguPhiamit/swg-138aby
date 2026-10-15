# Task: five Ossus NPCs for a Star Wars Galaxies server (Core3 Lua templates)

The folder `stock/` holds five stock NPC templates. Make one new NPC from each, following the table below. Write each new file into the folder `ossus/` with the file name given. Then write `ossus/npc_names.tsv`.

## How to make each file

1. Read the base file from `stock/`.
2. Copy it exactly, then change ONLY these things:
   - the variable name on the first line and in the last line (`CreatureTemplates:addCreatureTemplate(<var>, "<var>")`): use the "var" column;
   - `objectName = "@mob/creature_names:<var>"`;
   - `socialGroup`;
   - `faction`: set it to `""` (an empty string) for all five;
   - `pvpBitmask` and `creatureBitmask`: only where the table gives a value ("keep" means leave the line as it is).
3. Add one comment line at the very top: `-- Ossus (138-139 ABY): <one short sentence in your own words describing this NPC, from the facts column>. Base: stock <base file name>.`
4. Do not change any other line: level, damage, HAM, resists, weapons, attacks, templates, loot groups, random names and everything else stay exactly as in the base.

## The five NPCs

| new file | base | var | name | socialGroup | pvpBitmask | creatureBitmask | facts |
|---|---|---|---|---|---|---|---|
| ysanna_hunter.lua | janta_hunter.lua | ossus_ysanna_hunter | a Ysanna hunter | ysanna | ATTACKABLE | PACK + HERD | tribal hunter of Ossus's native Ysanna people; guides thrown spears with the Force without knowing it; wears a ritual mask |
| ysanna_warrior.lua | janta_warrior.lua | ossus_ysanna_warrior | a Ysanna warrior | ysanna | ATTACKABLE | PACK + HERD | defends the tribe; the Ysanna descend from Jedi who survived the Cron supernova in the caves of the Eocho Mountains |
| ysanna_shaman.lua | janta_shaman.lua | ossus_ysanna_shaman | a Ysanna shaman | ysanna | ATTACKABLE | PACK + HERD + HEALER | tribal elder who sees the Force as magic and heals the tribe |
| one_sith_acolyte.lua | dark_adept.lua | ossus_one_sith_acolyte | a One Sith acolyte | one_sith | keep | keep | follower of Darth Krayt's Sith order, which went underground after his death; hunts the surviving Jedi |
| one_sith_warrior.lua | dark_jedi_knight.lua | ossus_one_sith_warrior | a One Sith warrior | one_sith | keep | keep | a trained Sith of the One Sith, marked with Krayt's red and black tattoos |

## npc_names.tsv

One line per NPC: the var, a tab, then the name exactly as in the "name" column. No header line. Five lines.

## Finish

When all six files are written, reply with a short list of the files you wrote. Do not change anything in `stock/`.
