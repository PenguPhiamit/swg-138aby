# Planet data (run19)

Per-planet creatures, lairs, statics and coverage from `botpop-launch.jsonl`, for designing new content. Written by `tools/bots/planet_census.py`; one page and one CSV per planet that had explorers or hunters.

| planet | bots | explorers | hunters | 1 km squares covered | creatures | lairs | buildings | statics | unnamed statics |
|---|---|---|---|---|---|---|---|---|---|
| [corellia](corellia.md) | 825 | 0 | 208 | 82 of 256 | 30 | 16 | 0 | 0 | 0 |
| [naboo](naboo.md) | 643 | 0 | 213 | 67 of 256 | 19 | 12 | 0 | 0 | 0 |
| [ossus](ossus.md) | 200 | 200 | 0 | 250 of 256 | 24 | 0 | 6 | 1 | 146 |
| [rori](rori.md) | 268 | 0 | 96 | 37 of 256 | 23 | 8 | 0 | 0 | 0 |
| [talus](talus.md) | 271 | 0 | 106 | 38 of 256 | 20 | 10 | 0 | 0 | 0 |
| [tatooine](tatooine.md) | 701 | 0 | 227 | 80 of 256 | 30 | 12 | 0 | 0 | 0 |

No explorers on corellia, naboo, rori, talus, tatooine: those pages list only what hunters fought, with no buildings or statics.
No data at all for dantooine, dathomir, endor, lok, yavin4.

To get explorers onto a planet, the galaxy owner types `botpop explore N <planet>` in the test galaxy console (for example `botpop explore 50 dantooine`). Hunters go where the launch cities are.
