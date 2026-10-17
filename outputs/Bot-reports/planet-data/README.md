# Planet data (run21)

Per-planet creatures, lairs, statics and coverage from `botpop-launch.jsonl`, for designing new content. Written by `tools/bots/planet_census.py`; one page and one CSV per planet that had explorers or hunters.

| planet | bots | explorers | hunters | 1 km squares covered | creatures | lairs | buildings | statics | unnamed statics |
|---|---|---|---|---|---|---|---|---|---|
| [corellia](corellia.md) | 416 | 0 | 268 | 61 of 256 | 17 | 5 | 0 | 0 | 0 |
| [naboo](naboo.md) | 332 | 0 | 214 | 58 of 256 | 14 | 7 | 0 | 0 | 0 |
| [ossus](ossus.md) | 200 | 200 | 0 | 137 of 256 | 17 | 0 | 6 | 1 | 59 |
| [rori](rori.md) | 166 | 0 | 109 | 29 of 256 | 19 | 5 | 0 | 0 | 0 |
| [talus](talus.md) | 166 | 0 | 108 | 27 of 256 | 13 | 4 | 0 | 0 | 0 |
| [tatooine](tatooine.md) | 420 | 0 | 265 | 75 of 256 | 25 | 8 | 0 | 0 | 0 |

No explorers on corellia, naboo, rori, talus, tatooine: those pages list only what hunters fought, with no buildings or statics.
No data at all for dantooine, dathomir, endor, lok, yavin4.

To get explorers onto a planet, the galaxy owner types `botpop explore N <planet>` in the test galaxy console (for example `botpop explore 50 dantooine`). Hunters go where the launch cities are.
