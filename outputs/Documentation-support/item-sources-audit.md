# Item sources: can every item be obtained? (dev 91cf87ed against stock 403893d9)

Written by `tools/core3_audit/item_sources.py` (static reading; see its header for what each way means). The full map is `tools/core3_audit/item_sources.json`. The local model sorts the flagged items first (`local_jobs.py item-check`); Claude checks its draft.

12062 item templates. new: 6235, imported-unused: 6176, ok: 3769, no-source: 1650, test-only: 399, gained-script: 9.

## Broken references in the dev tree (stock count in brackets)

- loot item -> missing object: 0 (0)
- group -> missing entry: 0 (0)
- creature -> missing group: 0 (0)
- schematic -> missing object: 23 (0): object/draft_schematic/armor/cybernetic_appearance_s02_forearm_l.iff -> object/tangible/wearables/cybernetic/cybernetic_crafted_forearm_l_02.iff; object/draft_schematic/armor/cybernetic_appearance_s02_forearm_r.iff -> object/tangible/wearables/cybernetic/cybernetic_crafted_forearm_r_02.iff; object/draft_schematic/armor/cybernetic_appearance_s02_hand_l.iff -> object/tangible/wearables/cybernetic/cybernetic_crafted_hand_l_02.iff; object/draft_schematic/armor/cybernetic_appearance_s02_hand_r.iff -> object/tangible/wearables/cybernetic/cybernetic_crafted_hand_r_02.iff; object/draft_schematic/armor/cybernetic_appearance_s03_forearm_l.iff -> object/tangible/wearables/cybernetic/cybernetic_crafted_forearm_l_03.iff; object/draft_schematic/armor/cybernetic_appearance_s03_forearm_r.iff -> object/tangible/wearables/cybernetic/cybernetic_crafted_forearm_r_03.iff ...
- lair -> missing creature: 0 (0)

## Flags by folder

Imported-unused: templates under object/custom_content that nothing gives out; the local check leaves them out.

| Folder | Items | ok | no-source | test-only | imported-unused | new | lost | gained |
|---|---|---|---|---|---|---|---|---|
| tangible/loot | 1727 | 328 | 81 | 4 | 1314 | 1314 | 0 | 0 |
| tangible/ship | 1836 | 1136 | 562 | 138 | 0 | 0 | 0 | 0 |
| tangible/wearables | 1314 | 561 | 238 | 1 | 511 | 511 | 0 | 3 |
| tangible/quest | 700 | 0 | 4 | 0 | 696 | 696 | 0 | 0 |
| tangible/collection | 644 | 0 | 0 | 0 | 643 | 644 | 0 | 0 |
| tangible/furniture | 781 | 186 | 45 | 68 | 458 | 479 | 0 | 3 |
| tangible/component | 881 | 345 | 259 | 0 | 277 | 277 | 0 | 0 |
| tangible/tcg | 379 | 0 | 0 | 0 | 374 | 379 | 0 | 0 |
| tangible/item | 327 | 29 | 4 | 0 | 294 | 294 | 0 | 0 |
| tangible/food | 357 | 131 | 11 | 36 | 179 | 179 | 0 | 0 |
| tangible/deed | 459 | 251 | 24 | 102 | 64 | 82 | 0 | 0 |
| weapon/melee | 396 | 195 | 62 | 3 | 125 | 136 | 0 | 0 |
| tangible/storyteller | 222 | 0 | 0 | 0 | 222 | 222 | 0 | 0 |
| weapon/ranged | 263 | 64 | 34 | 5 | 159 | 160 | 0 | 0 |
| tangible/dance_prop | 129 | 0 | 0 | 0 | 129 | 129 | 0 | 0 |
| tangible/medicine | 234 | 184 | 50 | 0 | 0 | 0 | 0 | 0 |
| tangible/holiday | 114 | 0 | 0 | 0 | 114 | 114 | 0 | 0 |
| tangible/meatlump | 104 | 0 | 0 | 0 | 104 | 104 | 0 | 0 |
| tangible/veteran_reward | 111 | 29 | 1 | 0 | 80 | 81 | 0 | 0 |
| tangible/event_perk | 140 | 1 | 91 | 0 | 48 | 48 | 0 | 0 |
| tangible/dungeon | 105 | 20 | 35 | 0 | 50 | 50 | 0 | 0 |
| tangible/painting | 103 | 47 | 1 | 32 | 23 | 23 | 0 | 0 |
| tangible/gcw | 64 | 2 | 5 | 0 | 57 | 57 | 0 | 0 |
| tangible/saga_system | 59 | 0 | 0 | 0 | 59 | 59 | 0 | 0 |
| tangible/npe | 50 | 0 | 0 | 0 | 50 | 50 | 0 | 0 |
| tangible/smuggler | 38 | 0 | 0 | 0 | 38 | 38 | 0 | 0 |
| tangible/container | 65 | 11 | 41 | 0 | 10 | 10 | 0 | 3 |
| tangible/space | 73 | 51 | 22 | 0 | 0 | 0 | 0 | 0 |
| tangible/theme_park | 37 | 16 | 1 | 0 | 20 | 20 | 0 | 0 |
| tangible/powerup | 38 | 11 | 9 | 0 | 18 | 18 | 0 | 0 |
| tangible/scout | 42 | 27 | 0 | 1 | 14 | 14 | 0 | 0 |
| tangible/content | 21 | 0 | 0 | 0 | 21 | 21 | 0 | 0 |
| tangible/crafting | 34 | 16 | 15 | 2 | 1 | 1 | 0 | 0 |
| tangible/door | 16 | 0 | 0 | 0 | 16 | 16 | 0 | 0 |
| tangible/skill_buff | 24 | 23 | 1 | 0 | 0 | 0 | 0 | 0 |
| tangible/firework | 17 | 9 | 8 | 0 | 0 | 0 | 0 | 0 |
| tangible/fishing | 17 | 7 | 9 | 1 | 0 | 0 | 0 | 0 |
| tangible/instrument | 14 | 12 | 2 | 0 | 0 | 0 | 0 | 0 |
| tangible/jedi | 11 | 7 | 1 | 0 | 3 | 3 | 0 | 0 |
| tangible/vendor | 12 | 11 | 1 | 0 | 0 | 0 | 0 | 0 |
| tangible/survey_tool | 11 | 7 | 1 | 3 | 0 | 0 | 0 | 0 |
| tangible/droid | 9 | 7 | 2 | 0 | 0 | 0 | 0 | 0 |
| tangible/beta | 8 | 0 | 8 | 0 | 0 | 0 | 0 | 0 |
| tangible/bug_jar | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 0 |
| tangible/dice | 7 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| tangible/hologram | 3 | 0 | 0 | 0 | 3 | 3 | 0 | 0 |
| tangible/treasure_map | 6 | 4 | 2 | 0 | 0 | 0 | 0 | 0 |
| tangible/recycler | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| tangible/slicing | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| tangible/buildout | 2 | 0 | 0 | 0 | 2 | 2 | 0 | 0 |
| tangible/encoded_disk | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| tangible/faction_perk | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 0 |
| tangible/gambling | 4 | 1 | 3 | 0 | 0 | 0 | 0 | 0 |
| tangible/gem | 4 | 2 | 2 | 0 | 0 | 0 | 0 | 0 |
| tangible/travel | 4 | 2 | 2 | 0 | 0 | 0 | 0 | 0 |
| weapon/mine | 4 | 3 | 1 | 0 | 0 | 0 | 0 | 0 |
| tangible/trophy | 3 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| tangible/droid_battery | 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| tangible/battery | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| tangible/harvesting | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| tangible/magic_eight_ball | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| tangible/microphone | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| tangible/mission_bag | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| tangible/newbie_tutorial | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| tangible/npc | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| tangible/parrot_cage | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| tangible/sandbox | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| tangible/speaker | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| weapon/trap | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |

## Items that lost a way of getting them against stock (0)

