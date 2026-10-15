# Your test list: test galaxy, evening of 14 Oct 2026

The test galaxy restarted at 19:13 with everything below, and your client's `local_planets.tre` was updated to match
(248092a2; the old one is backed up). Start with **`Play SWG Test Galaxy.cmd`**. Do this first look **without**
ReShade/DLSS, so we can tell game problems from filter effects (`Client-graphics/README.md` is for afterwards).
**[admin]** = needs your staff character. I won't restart the test galaxy while your client is running.

Report anything odd with: where you were (`/loc` or the on-screen coordinates), what you expected, what you saw, and a
screenshot if it's visual.

## 1. Chiss: create a character (new)
1. Character creation: **Chiss** (male and female) in the species list, with its own description.
2. Appearance: human sliders; blue skin palette; human hair styles; note the eye colours you get.
3. Finish one Chiss (any professions). If creation fails, note the exact message in the box.
4. In game: default clothes on; Skills window shows a **Species: Chiss** box.
5. Clothing rule: a human shirt and boots must equip (**[admin]** `/giveitem object/tangible/wearables/shirt/shirt_s01.iff`
   and `object/tangible/wearables/boots/boots_s01.iff`). "You cannot wear that" = report it.
6. Is the skin still blue in daylight, at night and indoors?

## 2. Ossus: first look (new)
1. Coronet Starport (Corellia): the ticket list offers **Ossus**, 3,000 credits. Board.
2. Loading screen: an olive map tile and an Ossus line of text. A crash here: report the last line of the crash file.
3. You land on the **Knossa** pad (about 21, -3582). Look around: starport, olive scrub plain, ponds; sky and sun.
   White or purple ground = missing textures (say where).
4. Walk south off the pad: a ramp, not a wall.
5. **[admin]** teleports: `/teleport 500 -1500 ossus` (the road), `/teleport 2016 2848 ossus` (academy ruins),
   `/teleport -3600 1200 ossus` (the lake), `/teleport 4300 -700 ossus` (Imhar Canyon),
   `/teleport -2976 -4940 ossus` (a cave mouth; walk in).
6. Planetary map: the Ossus map with the Knossa label; your location reads "Knossa" on the pad.
7. No creatures on Ossus yet. That's by design for this first look.

## 3. Resources on Hoth and Ossus (fixed tonight)
1. On **Hoth**, use a mineral survey device: Hoth's own types ("Hothian Steel", ores, radioactive...), the four new
   gemstones ("Hothian Type 1 Amorphous Gemstone" and so on), and ordinary galaxy-wide minerals (33 now; there were 3).
2. Gas and chemical devices on Hoth: Hoth's reactive gas and fuels, plus galaxy-wide ones.
3. On **Ossus**: "Ossus Steel", "Ossus Iron" ... "Ossus Type 2 Crystalline Gemstone" (14 types), plus galaxy-wide
   minerals (23).
4. Solar and wind devices on both: Hoth/Ossus solar and wind energy.
5. Expected gap: geothermal, tidal and hydron-3 energy now spawn on every planet, but no survey device can find them
   yet (SOE never built one). Nothing to report there.
6. Blank or raw names (like `@resource...`) = report the exact text.

## 4. Echo Base: first look (new)
1. **[admin]** `/teleport -5051 5440 hoth`, face the mountain: a metal door in the rock at about (-5051, 5411).
   No door: try `/teleport -5051 5380 hoth` and look back.
2. Walk through the main door: lit corridors, floor level with the snow outside. Falling through or a black void =
   report it.
3. `/teleport -5307 5750 hoth`: the 49 m hangar mouth. `/teleport -5036 5120 hoth`: the tower opening near the top.
4. Inside: missing textures (flat white or purple), doors that don't open (expected for now), dark rooms, places you
   get stuck. Note the room or coordinates.

## 5. Hoth, still unchecked from the first session (`Fable-hoth-guide/hoth-first-session.md`)
1. Quartermaster Vell's first job, start to finish (section 2): Ria Baxx 600-900 m out, two ice mynocks, the regulator,
   1,500 credits on return.
2. Loot (section 8): kill a few named beasts; any drop must show a proper name.
3. The Botanist trainer in Mos Eisley (section 9): skill names, not `@skl_n:...`.

## 6. Optional, afterwards: graphics
`Client-graphics/README.md`: Path A (ReShade only) or Path B (DLSS 5 through the Feeder). For Chiss skin, the
`SpeciesColorLock.fx` shader in the same folder keeps the colours.
