# Ossus people (PL-02): NPCs, conversations and first missions (Claude, 16 Oct 2026)

Built on O7 (PL-01) and staged, **not installed, untested in game**. The server half is `../server/core3-dev-ossus-people.patch`, made from
the three files under `MMOCoreORB/` here plus one include line each. The client half is `../build_ossus_people.py`. Stock bodies only.
The names and text are our own. Era 138-139 ABY: the academy fell in 130, Krayt died in 138, and his garrison still holds the benchland.

## Who stands where (33 spawns, positions from `../poi-placements.json` -> `npc_points`)

| Place | People (template; ours in bold) |
|---|---|
| 3 Garrison and dig | **Major Kesh Vantor** (talks; refuses rebels), 4 `stormtrooper_rifleman` (gate and the two tower doors, 5 m in front of each tower), `stormtrooper_squad_leader`, `stormtrooper`, 2 `imperial_sergeant` (one is the dig overseer), 2 `commoner_technician` dig workers |
| 2 Sanctuary (cell 11, the deepest chamber) | **a robed stranger**, the hidden Jedi: present one hour, then away 2-4 hours (first visit 10-60 minutes after start); talk only, invulnerable, will not speak to Imperials |
| 4 Vault dig | **Archivist Senn Oduro** (the memorial road) |
| 5 Ysanna camp, 6 stone circle | **Elder Iravi** (the highland hunt), 2 `hermit` hunters; 2 `commoner_old` singers at the circle |
| 8 Hamlet | **Old Pell** (talks), a `farmer` fisher |
| 9 Adit | **Brannock Teel**, foreman (the part errand), a `miner` |
| 10 Canyon floor | 3 `brigand` canyon raiders (aggressive, level 4, respawn 10 min) |
| 11 Knossa | stock `imperial_recruiter` by the shuttle pad, `junk_dealer` (stock conversation), `artisan`, 2 `commoner` at the cantina |
| 14 Sith post | an `imperial_sergeant` post guard on the apron |
| 15 Crashed fighter | **Lieutenant Dera Moll**, Galactic Alliance pilot (the part errand) |
| 18 Hutt field | **Ondrubba the Hutt** (talks through a protocol unit; `hutt_male` body), a `smuggler` kathracite buyer |

All spawns are stationary. Ambient ones respawn after 5 minutes. Two of the brief's suggestions do not exist in dev (`jedi_light`, `hutt_thug_npc`),
and `imperial_inquisitor` is level 120, so the dig overseer is a sergeant and the people who talk have our own templates (level 30, invulnerable).

## Three starter missions (progress is per player in screenplay data: it survives logouts and restarts)

1. **The highland hunt.** Elder Iravi asks for three kirruk (level 19, a pack, not aggressive) on the shoulder just north of the stone circle.
   They are spawned for that player, with a waypoint. Each kill is counted, and back at the camp the reward is 1,500 credits. "I lost their trail"
   respawns the missing ones. An unfought target is removed after 30 minutes.
2. **The pilot's part.** Lieutenant Moll needs a power coupling. Foreman Teel at the adit hands it over, and back at the fighter the reward is
   1,000 credits. A waypoint is given at each step. No item is created: the coupling is a progress flag.
3. **The memorial road and its badge.** Three trigger areas: the first stone above Knossa, the middle stone and the memorial ring.
   Walking them in order awards **badge 140, "Location: The Memorial Road of Ossus"** (exploration). Anyone can walk it.
   Archivist Oduro marks the three spots and pays 500 credits once the walk is done.

## Not done (said plainly)

- **Standing gates and the new faction strings** wait for FW-01. For now the garrison is GCW `imperial`, so its troopers fight overt rebels.
  The commander turns rebels away, and the stranger will not speak to Imperials.
- **What meeting the hidden Jedi gives** is the owner's open question: for now the meeting is only remembered (`metJedi`). The stranger cannot be attacked.
- No interiors are dressed: the vault, the adit, the Sith post and the garrison buildings. The singers have no night loop, the rim patrol stands still,
  and the Hutt does not trade. The troopers are not hued as Sith troopers.
- Not run on any galaxy. Checked offline: `git apply --check` on dev `d4b9d9a1` (with the O7 regions patch too); `luac -p` on all six files;
  a stubbed load of the three new files (8 templates, 42 screens, every option and every screen the handlers name resolves, no dead ends).
