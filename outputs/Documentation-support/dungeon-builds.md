# Dungeon builds and the Forn crew (Claude, 15 Oct 2026)

The owner asked for builds that can do dungeons, then for a bot crew to test them ("give me a crew and we can test their combat more and their movement and mapping"). Point totals and prerequisites come from the server's own skill table (`Claude-class-check/professions.json`, read from `datatables/skill/skills.iff`); the cap is 250. Monster levels come from Core3-dev's mobile templates for each dungeon's spawns.

## The dungeons we have

| Dungeon | Planet | Monster levels | Boss | For |
|---|---|---|---|---|
| Warren | Dantooine | 11–100, most around 33 | Mirla, Dirk Maggin (100) | first dungeon |
| Geonosian bio-lab | Yavin IV | 25–157, most around 53 | Acklay (157) | mid |
| Hoth caves (ours, test galaxy) | Hoth | 20–115 | wampa Patriarch (115) | mid |
| Death Watch bunker | Endor | up to 221, most around 100 | Overlord (221) | endgame group |
| Corellian corvette (instanced, ticket from a faction NPC) | space station | up to 226, most around 100 | admiral / inquisitor (226) | endgame group |
| World bosses (ours) | several | up to 336 | ancient krayt (336) | raid |

All four Core3 dungeons are registered screenplays (`bin/scripts/screenplays/dungeon/`).

Entrances (client world snapshots): Warren dantooine -547 -3846, Geonosian lab yavin4 -6449 -401, Death Watch bunker endor -4662 4326. **Death Watch mines:** players there are poisoned every 45 s unless the eyes slot holds the Mandalorian helmet (`armor_mandalorian_helmet`) or a rebreather renamed "Advanced Rebreather" by the bunker's workbench (`deathWatchBunker.lua`, `hasRebreather`, `poisonEvent`). The crew bots are players too: they need a helmet kit before the mines. Players have long run this bunker behind a Jedi tank (owner, 15 Oct); our crew tests whether Brask can hold it.

## The crew (bot group Forn, accounts forn1–5)

| Bot | Role | Template | Points | Weapon |
|---|---|---|---|---|
| Forn Halcyr | leader, ranged | Squad Leader + Rifleman, Medic novice + injury 1–2 | 232 | T21 rifle |
| Brask Tolen | tank | Fencer + Pikeman + Medic | 246 | vibrolance (Rantok sword spare) |
| Ressa Vay | melee damage | Teras Kasi + Fencer + Medic | 246 | vibroknuckler |
| Dask Orrin | ranged damage | Commando + Rifleman, Medic novice + injury 1 | 249 | acid beam (heavy kit), T21 |
| Mirren Sol | healer | Doctor + Combat Medic, Marksman novice | 232 | T21; medicine and enhancement packs |

The two-elite melee templates cost 169, so full Medic (77) fits beside them for self-heals. Commando, Bounty Hunter and Doctor + Combat Medic each cost 232 with their prerequisites.

**Not yet proven on our server:** the class check has real results for Marksman, Medic, Doctor (5 of 7 abilities work, 15 Oct) and part of Scout. Brawler, Rifleman and Pistoleer runs were cut short; Commando, Squad Leader, Fencer, Pikeman, Teras Kasi and Combat Medic are untested here. The crew's fights are the first test of them, and the class-check campaign (C38) should take these professions first.

**Avoid for now:** Creature Handler (17 pet-order abilities have no server reference, `Agent/local-research/profession-gaps`).

## Making a character with one of these builds (if the owner wants one)

On the test galaxy, target the character and use `/grantSkill <box>` for each master box in the table (it grants the prerequisites too), or use the character builder, which is enabled there.

## How the crew fights

`tools/bots/crew_combat.py`: each bot cycles through the special attacks it holds for the weapon in its hands (from the server's command tables), mixing in the plain attack after a refusal; ranged bots stand off; Forn opens with steady aim and volley fire; Mirren heals whoever is under 70 %. The bot body's own fight reflex only walks into melee and sends the default attack, which tests no template.

Round 1 (`tools/bots/scenarios/forn-crew.py`): templates and gear, hospital buffs, three fights of rising tier on the sevorrt plateau. Next rounds: travel to Dantooine and the Warren, then the Geonosian lab, mapping each new area on the way.
