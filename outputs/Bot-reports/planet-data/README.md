# Planet data (run29)

Per-planet creatures, lairs, statics and coverage from `botpop-launch.jsonl`, for designing new content. Written by `tools/bots/planet_census.py`; one page and one CSV per planet that had explorers or hunters.

| planet | bots | explorers | hunters | 1 km squares covered | creatures | lairs | buildings | statics | unnamed statics |
|---|---|---|---|---|---|---|---|---|---|
| [corellia](corellia.md) | 219 | 0 | 95 | 60 of 256 | 24 | 5 | 0 | 0 | 0 |
| [hutta](hutta.md) | 147 | 0 | 8 | 15 of 256 | 2 | 0 | 0 | 0 | 0 |
| [naboo](naboo.md) | 179 | 0 | 70 | 61 of 256 | 20 | 9 | 0 | 0 | 0 |
| [rori](rori.md) | 73 | 0 | 40 | 29 of 256 | 21 | 6 | 0 | 0 | 0 |
| [talus](talus.md) | 70 | 0 | 37 | 31 of 256 | 17 | 4 | 0 | 0 | 0 |
| [tatooine](tatooine.md) | 528 | 0 | 331 | 90 of 256 | 29 | 9 | 0 | 0 | 0 |

No explorers on corellia, hutta, naboo, rori, talus, tatooine: those pages list only what hunters fought, with no buildings or statics.
No data at all for dantooine, dathomir, endor, lok, yavin4.

To get explorers onto a planet, the galaxy owner types `botpop explore N <planet>` in the test galaxy console (for example `botpop explore 50 dantooine`). Hunters go where the launch cities are.
