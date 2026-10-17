# Planet data (run22)

Per-planet creatures, lairs, statics and coverage from `botpop-launch.jsonl`, for designing new content. Written by `tools/bots/planet_census.py`; one page and one CSV per planet that had explorers or hunters.

| planet | bots | explorers | hunters | 1 km squares covered | creatures | lairs | buildings | statics | unnamed statics |
|---|---|---|---|---|---|---|---|---|---|
| [corellia](corellia.md) | 235 | 0 | 101 | 45 of 256 | 19 | 5 | 0 | 0 | 0 |
| [naboo](naboo.md) | 200 | 0 | 88 | 47 of 256 | 13 | 9 | 0 | 0 | 0 |
| [ossus](ossus.md) | 100 | 100 | 0 | 6 of 256 | 5 | 0 | 3 | 1 | 6 |
| [rori](rori.md) | 90 | 0 | 45 | 22 of 256 | 19 | 6 | 0 | 0 | 0 |
| [talus](talus.md) | 85 | 0 | 51 | 26 of 256 | 13 | 4 | 0 | 0 | 0 |
| [tatooine](tatooine.md) | 230 | 0 | 141 | 69 of 256 | 22 | 9 | 0 | 0 | 0 |

No explorers on corellia, naboo, rori, talus, tatooine: those pages list only what hunters fought, with no buildings or statics.
No data at all for dantooine, dathomir, endor, lok, yavin4.

To get explorers onto a planet, the galaxy owner types `botpop explore N <planet>` in the test galaxy console (for example `botpop explore 50 dantooine`). Hunters go where the launch cities are.
