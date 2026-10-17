# Planet data (run20)

Per-planet creatures, lairs, statics and coverage from `botpop-launch.jsonl`, for designing new content. Written by `tools/bots/planet_census.py`; one page and one CSV per planet that had explorers or hunters.

| planet | bots | explorers | hunters | 1 km squares covered | creatures | lairs | buildings | statics | unnamed statics |
|---|---|---|---|---|---|---|---|---|---|
| [corellia](corellia.md) | 451 | 0 | 271 | 83 of 256 | 34 | 17 | 0 | 0 | 0 |
| [naboo](naboo.md) | 357 | 0 | 204 | 65 of 256 | 20 | 12 | 0 | 0 | 0 |
| [ossus](ossus.md) | 200 | 200 | 0 | 200 of 256 | 24 | 0 | 6 | 1 | 93 |
| [rori](rori.md) | 172 | 0 | 105 | 37 of 256 | 21 | 7 | 0 | 0 | 0 |
| [talus](talus.md) | 177 | 0 | 106 | 37 of 256 | 24 | 9 | 0 | 0 | 0 |
| [tatooine](tatooine.md) | 436 | 0 | 275 | 83 of 256 | 25 | 10 | 0 | 0 | 0 |

No explorers on corellia, naboo, rori, talus, tatooine: those pages list only what hunters fought, with no buildings or statics.
No data at all for dantooine, dathomir, endor, lok, yavin4.

To get explorers onto a planet, the galaxy owner types `botpop explore N <planet>` in the test galaxy console (for example `botpop explore 50 dantooine`). Hunters go where the launch cities are.
