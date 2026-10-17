# Planet data (run13)

Per-planet creatures, lairs, statics and coverage from `botpop-launch.jsonl.1955.old`, for designing new content. Written by `tools/bots/planet_census.py`; one page and one CSV per planet that had explorers or hunters.

| planet | bots | explorers | hunters | 1 km squares covered | creatures | lairs | buildings | statics | unnamed statics |
|---|---|---|---|---|---|---|---|---|---|
| [corellia](corellia.md) | 416 | 0 | 269 | 97 of 256 | 52 | 25 | 0 | 0 | 0 |
| [naboo](naboo.md) | 332 | 0 | 208 | 76 of 256 | 46 | 19 | 0 | 0 | 0 |
| [ossus](ossus.md) | 200 | 200 | 0 | 256 of 256 | 7 | 0 | 2 | 0 | 326 |
| [rori](rori.md) | 166 | 0 | 105 | 41 of 256 | 33 | 10 | 0 | 0 | 0 |
| [talus](talus.md) | 166 | 0 | 109 | 43 of 256 | 31 | 11 | 0 | 0 | 0 |
| [tatooine](tatooine.md) | 420 | 0 | 267 | 91 of 256 | 40 | 14 | 0 | 0 | 0 |

No explorers on corellia, naboo, rori, talus, tatooine: those pages list only what hunters fought, with no buildings or statics.
No data at all for dantooine, dathomir, endor, lok, yavin4.

To get explorers onto a planet, the galaxy owner types `botpop explore N <planet>` in the test galaxy console (for example `botpop explore 50 dantooine`). Hunters go where the launch cities are.
