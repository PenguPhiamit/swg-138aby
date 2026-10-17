# Planet data (run18)

Per-planet creatures, lairs, statics and coverage from `botpop-launch.jsonl`, for designing new content. Written by `tools/bots/planet_census.py`; one page and one CSV per planet that had explorers or hunters.

| planet | bots | explorers | hunters | 1 km squares covered | creatures | lairs | buildings | statics | unnamed statics |
|---|---|---|---|---|---|---|---|---|---|
| [corellia](corellia.md) | 925 | 0 | 205 | 72 of 256 | 36 | 22 | 0 | 0 | 0 |
| [naboo](naboo.md) | 703 | 0 | 218 | 67 of 256 | 41 | 14 | 0 | 0 | 0 |
| [ossus](ossus.md) | 200 | 200 | 0 | 255 of 256 | 7 | 0 | 2 | 0 | 280 |
| [rori](rori.md) | 294 | 0 | 103 | 38 of 256 | 27 | 9 | 0 | 0 | 0 |
| [talus](talus.md) | 324 | 0 | 108 | 40 of 256 | 24 | 9 | 0 | 0 | 0 |
| [tatooine](tatooine.md) | 745 | 0 | 192 | 69 of 256 | 32 | 11 | 0 | 0 | 0 |

No explorers on corellia, naboo, rori, talus, tatooine: those pages list only what hunters fought, with no buildings or statics.
No data at all for dantooine, dathomir, endor, lok, yavin4.

To get explorers onto a planet, the galaxy owner types `botpop explore N <planet>` in the test galaxy console (for example `botpop explore 50 dantooine`). Hunters go where the launch cities are.
