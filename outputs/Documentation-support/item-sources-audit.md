# Item sources: can every item be obtained? (dev 91cf87ed against stock 403893d9)

Written by `tools/core3_audit/item_sources.py` (static reading; see its header for what each way means). The full map is `tools/core3_audit/item_sources.json`. The local model sorts the flagged items first (`local_jobs.py item-check`); Claude checks its draft.

5828 item templates. ok: 3766, no-source: 1653, test-only: 399, gained-script: 9, new: 1.

## Broken references in the dev tree (stock count in brackets)

- loot item -> missing object: 25 (1): hoth_decor_col_reward_hoth_tauntaun_head -> object/tangible/collection/reward/col_reward_hoth_tauntaun_head.iff; hoth_decor_decorative_hoth_travel_advertisement -> object/tangible/tcg/series3/decorative_hoth_travel_advertisement.iff; hoth_decor_decorative_stuffed_tauntaun -> object/tangible/tcg/series4/decorative_stuffed_tauntaun.iff; hoth_decor_decorative_stuffed_wampa -> object/tangible/tcg/series4/decorative_stuffed_wampa.iff; hoth_decor_diorama_atat_attack -> object/tangible/tcg/series8/diorama_atat_attack.iff; hoth_decor_frn_plush_tauntaun -> object/tangible/veteran_reward/frn_plush_tauntaun.iff ...
- group -> missing entry: 0 (0)
- creature -> missing group: 0 (0)
- schematic -> missing object: 0 (0)
- lair -> missing creature: 0 (0)

## Flags by folder

| Folder | Items | ok | no-source | test-only | new | lost | gained |
|---|---|---|---|---|---|---|---|
| tangible/ship | 1836 | 1136 | 562 | 138 | 0 | 0 | 0 |
| tangible/wearables | 803 | 561 | 238 | 1 | 0 | 0 | 3 |
| tangible/component | 604 | 345 | 259 | 0 | 0 | 0 | 0 |
| tangible/loot | 413 | 326 | 83 | 4 | 0 | 0 | 0 |
| tangible/deed | 378 | 251 | 24 | 102 | 1 | 0 | 0 |
| tangible/furniture | 302 | 186 | 45 | 68 | 0 | 0 | 3 |
| weapon/melee | 260 | 195 | 62 | 3 | 0 | 0 | 0 |
| tangible/medicine | 234 | 184 | 50 | 0 | 0 | 0 | 0 |
| tangible/food | 178 | 130 | 12 | 36 | 0 | 0 | 0 |
| weapon/ranged | 103 | 64 | 34 | 5 | 0 | 0 | 0 |
| tangible/event_perk | 92 | 1 | 91 | 0 | 0 | 0 | 0 |
| tangible/painting | 80 | 47 | 1 | 32 | 0 | 0 | 0 |
| tangible/space | 73 | 51 | 22 | 0 | 0 | 0 | 0 |
| tangible/container | 55 | 11 | 41 | 0 | 0 | 0 | 3 |
| tangible/dungeon | 55 | 20 | 35 | 0 | 0 | 0 | 0 |
| tangible/crafting | 33 | 16 | 15 | 2 | 0 | 0 | 0 |
| tangible/item | 33 | 29 | 4 | 0 | 0 | 0 | 0 |
| tangible/veteran_reward | 30 | 29 | 1 | 0 | 0 | 0 | 0 |
| tangible/scout | 28 | 27 | 0 | 1 | 0 | 0 | 0 |
| tangible/skill_buff | 24 | 23 | 1 | 0 | 0 | 0 | 0 |
| tangible/powerup | 20 | 11 | 9 | 0 | 0 | 0 | 0 |
| tangible/firework | 17 | 9 | 8 | 0 | 0 | 0 | 0 |
| tangible/fishing | 17 | 7 | 9 | 1 | 0 | 0 | 0 |
| tangible/theme_park | 17 | 16 | 1 | 0 | 0 | 0 | 0 |
| tangible/instrument | 14 | 12 | 2 | 0 | 0 | 0 | 0 |
| tangible/vendor | 12 | 11 | 1 | 0 | 0 | 0 | 0 |
| tangible/survey_tool | 11 | 7 | 1 | 3 | 0 | 0 | 0 |
| tangible/droid | 9 | 7 | 2 | 0 | 0 | 0 | 0 |
| tangible/beta | 8 | 0 | 8 | 0 | 0 | 0 | 0 |
| tangible/bug_jar | 8 | 8 | 0 | 0 | 0 | 0 | 0 |
| tangible/jedi | 8 | 7 | 1 | 0 | 0 | 0 | 0 |
| tangible/dice | 7 | 7 | 0 | 0 | 0 | 0 | 0 |
| tangible/gcw | 7 | 2 | 5 | 0 | 0 | 0 | 0 |
| tangible/treasure_map | 6 | 4 | 2 | 0 | 0 | 0 | 0 |
| tangible/recycler | 5 | 5 | 0 | 0 | 0 | 0 | 0 |
| tangible/slicing | 5 | 5 | 0 | 0 | 0 | 0 | 0 |
| tangible/encoded_disk | 4 | 4 | 0 | 0 | 0 | 0 | 0 |
| tangible/faction_perk | 4 | 0 | 4 | 0 | 0 | 0 | 0 |
| tangible/gambling | 4 | 1 | 3 | 0 | 0 | 0 | 0 |
| tangible/gem | 4 | 2 | 2 | 0 | 0 | 0 | 0 |
| tangible/quest | 4 | 0 | 4 | 0 | 0 | 0 | 0 |
| tangible/travel | 4 | 2 | 2 | 0 | 0 | 0 | 0 |
| weapon/mine | 4 | 3 | 1 | 0 | 0 | 0 | 0 |
| tangible/trophy | 3 | 0 | 0 | 3 | 0 | 0 | 0 |
| tangible/droid_battery | 2 | 1 | 1 | 0 | 0 | 0 | 0 |
| tangible/battery | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| tangible/harvesting | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| tangible/magic_eight_ball | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| tangible/microphone | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| tangible/mission_bag | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| tangible/newbie_tutorial | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| tangible/npc | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| tangible/parrot_cage | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| tangible/speaker | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| weapon/trap | 1 | 0 | 1 | 0 | 0 | 0 | 0 |

## Items that lost a way of getting them against stock (0)

