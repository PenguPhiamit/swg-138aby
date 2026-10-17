# Ossus O9: the look pass (Claude, 17 Oct 2026)

The owner, after walking O8 (17 Oct, about 8 AM): "the colors and topography seem off ... the legends article seems like more red", meaning the
atmosphere. The reference is Wookieepedia's Ossus (Legends) article (https://starwars.fandom.com/wiki/Ossus/Legends): its main picture shows the
planet from space with an orange-gold atmosphere. The article describes hills, mountains, gorges, forests and caves, a temperate climate and a
type I atmosphere. The planet was lush, with two-thirds of its surface water, until the Cron supernova made it a desert. The Ossus Project
(Yuuzhan Vong shapers, from 40 ABY) restored it: kingwood forests on the mountain slopes and verdant turf around the academy.

**Staged, not installed, untested in game.** This is a client and server archive step. No terrain shape changes, and no Lua.

## What changes (colours only)

`build_ossus_look.py` works on any base archive (default: the installed `b01e9f44…`). It makes our own warm versions of the two images Ossus's
sky and light come from, and points the environment table at them. Each pixel is pulled toward gold (RGB 255, 168, 72) at its own brightness,
so night stays night and the ground keeps its greens.

| Entry | Before | After |
|---|---|---|
| `datatables/environment/ossus.iff`, clear weather (6 families × weather 0) | sky `texture/grad_sky_dantooine.dds`, light `terrain/colorramp/dantooine_global0.tga` | sky `texture/grad_sky_ossus.dds`, light `terrain/colorramp/ossus_global0.tga` |
| same table, weather 1-4 (24 rows: overcast, no sky gradient) | light `terrain/colorramp/naboo_global1.tga` | light `terrain/colorramp/ossus_overcast0.tga` (stays overcast, slightly warmer) |
| `texture/grad_sky_ossus.dds` (new, 256×32) | — | Dantooine's gradient, gold pull 0.55 |
| `terrain/colorramp/ossus_global0.tga` (new, 256×8) | — | Dantooine's ramp, gold pull 0.25-0.50 per row (the fog and sky rows the most) |
| `terrain/colorramp/ossus_overcast0.tga` (new) | — | Naboo's overcast ramp, gold pull 0.20 |

Everything else stays the same: fog densities, clouds, sounds and every other entry (200 of 201, byte for byte).

Colours at eight times of day (left to right: the 0, 32, ..., 224 columns of 256), as hex RGB, from `checks-look.json`:

| | Before | After |
|---|---|---|
| Sky, horizon row | `595564 b6afb1 c1c3c4 a0a3aa 5b596c 2c2d44 23253a 25263c` | `6b5340 daa876 ecba82 c59c70 6f5644 382c29 2d2422 2f2524` |
| Sky, middle row | `535667 80889f 8aa1c0 828fa9 646273 354059 1e334e 27364e` | `685341 a28265 b79879 a7886b 7a5f49 493d36 322f2d 3a332e` |
| Sky, top row | `303d4b 425874 4c6a8f 566081 494a5c 202638 0d1726 17222d` | `43392e 5f5247 706356 715c4f 5b483a 2c2421 161516 231f1b` |
| Light ramp row 1 | `555161 b2abad bdbfc0 9ea1a8 595669 2b293d 211f32 232235` | `5d5051 c2a893 d0bba3 af9e8e 625558 302932 251f29 27222b` |
| Light ramp row 5 (warmest) | `8b6767 a78644 af903c a68247 8b6767 666c91 5473a5 617096` | `95684a b2823d bc8a3a b07f3e 95684a 80695e 786d68 7e6b61` |
| Light ramp row 7 | `65687c 896b64 7f7464 70657e 54567d 3d5677 395677 455d79` | `7a6557 946a4b 8f704c 816458 675455 555150 525150 5e5852` |

Pictures: `work/ossus-look/preview-sky-before.png` and `-after.png`, `preview-ramp-*.png`, `preview-overcast-*.png` (the folder is not in git).
If the result is too strong or too weak, rerun with `--sky 0.35` (or `0.7`) and `--ramp 0.3`; the defaults are in the file.

Not done: the planet-select globe (`texture/ui_planet_sel_ossus.dds`). Its glow would need a hand-painted edge, so it waits for your look at the sky.

Candidate on `b01e9f44`: **`work/ossus-look/local_planets-ossus-look.tre`**, 5,329,223 bytes, 203 entries,
**sha256 `48c805189872c193514221e664e2dedeccf4f59ec927bf2a1d481f9d28afa7e4`** (two builds, same hash).

## Install (the main session)

```bash
C:/Users/Pengw/miniconda3/python.exe -I Fable-ossus/o9-look/build_ossus_look.py --base <the archive to install on> --out <new .tre>
```
Then install the new archive in both places (`/opt/swg/tre/local_planets.tre` and `SWG-client/local_planets.tre`) and restart the test galaxy.
The step changes only Ossus's environment table and adds three images, so it chains in any order with the other steps.

## Questions for the owner's visit

1. Stand at Knossa (0 -3600) at midday, at sunset and at night. How do the sky and the light on the ground look now, compared with the
   Legends picture?
2. Is the gold too strong, too weak, or the wrong shade (more red, more yellow)?
3. When it is cloudy or raining, does it still look like Ossus?
4. Does anything look wrong: a white sky, a black sky, or green or purple light?

## Topography: what would make it read as Legends Ossus (your decision; nothing changed)

The article's words are hills, mountains, gorges, forests, caves, two-thirds water, kingwood forests on the mountain slopes and verdant turf at the academy.
Today Ossus is mostly open plains, a flat 104 m mesa in the east, one canyon and a low mountain band in the south. Options, each needing your OK:
1. **Forests (flora only, no shape change):** kingwood-like stock trees thick on the mountain slopes and around the benchland, with the plains staying open.
   This changes the terrain file's flora layers, not its heights. Do you want it?
2. **More water:** raise the global water from 38.5 m so the low west and the basins become lakes and inlets (toward "two-thirds water").
   Knossa (50 m) and the hamlet would need checking. How much water do you want?
3. **Hills instead of the flat mesa:** break the 104 m mesa into rolling hills and gorges. This is a big shape change, and the Hutt field and
   two places sit on it.
4. **Higher mountains:** make the Eocho Mountains taller and steeper, so they read as mountains from Knossa.
5. **More gorges:** two or three more canyons like Imhar, running from the mountains to the lakes.
6. **Caves:** more cave mouths in the hills (stock caves in the snapshot, as O7 did). These would be places to find, not shape changes.

Tell me which of these you want, and I will stage them as one terrain batch with before and after pictures.
