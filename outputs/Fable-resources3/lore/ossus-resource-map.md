# Ossus on Wookieepedia, mapped to SWG resources (Claude, 14 Oct 2026)

The owner asked for every Ossus resource on Wookieepedia to be checked and mapped to an SWG class. Sources: the Legends
Ossus page (infobox, Geography, Flora and fauna, History, Locations), the categories "Plants of Ossus" and "Creatures of
Ossus", the 801 pages that link to Ossus filtered by material, plant, creature and food categories, and the pages for
each hit. The pages were read in the browser pane; Fandom refuses the fetch tools. Wookieepedia text is CC BY-SA, so the
summaries below are our own words. Setting: 138–139 ABY (owner, 14 Oct). **Canon-only** entries are marked and not
used, because our setting is Legends.

What the pages say about the planet as a whole:

- The infobox gives **major exports: none**. Ossus was never a mining world.
- The Cron supernova (3996 BBY) turned it into an irradiated desert.
- By 40 ABY it was green again near the Academy. A century later the Yuuzhan Vong Shapers' Ossus Project had fully
  restored it, so in our window Ossus is a Vongformed garden world.
- Twice a year it passes between its two suns: weeks without night, and most surface water boils into cloud.
- The Ysanna farm the nitrogen-rich valleys below the Eocho Mountains.

So the stock-style metals, ores, gas and fuels on Ossus (R3 part 2) are gameplay, not lore. They keep their generic
"Ossus …" names.

## 1. Gems: done, staged in `names/` (owner: "rename the placeholder gems")

The Legends Adegan crystal page names five grades, from the most common to the rarest:

| grade | what the page says | our enum | new name |
|---|---|---|---|
| kathracite | the most common; training sabers | `crystalline_ossus_1` | Kathracite Crystalline Gemstone |
| relacite | common; training sabers | `armophous_ossus_1` | Relacite Crystal Amorphous Gemstone |
| danite | common; training sabers | `armophous_ossus_2` | Danite Crystal Amorphous Gemstone |
| mephite | the typical Jedi crystal | `crystalline_adegan_ossus` | Mephite Crystalline Gemstone |
| pontite | the rarest and most powerful | `crystalline_ossus_2` | Pontite Crystalline Gemstone |

- The first Adegan crystals were found on Ossus.
- Knossa's central plaza had two obelisks topped with Adegan crystals.
- Ossus has exactly five gem leaves, so each grade gets one.
- The two weaker grades take the amorphous slots, the way stock already has "Bal'ta'ran Crystal Amorphous Gemstone".
- The ENUMs, attributes and pools stay as they are. Only the name text changes; see `names/README.md`.
- **Open for the owner:** all five still have the same ranges, because R3's rule cloned the strongest stock gem of each
  class. If the grades should mean something, give kathracite, relacite and danite lower floors and keep pontite at the
  top. That would be a stated variant, like the lumni lichen's.

## 2. Flora

Only Kingwood and Bambwood are proposed as text renames (not staged). Every other row is a note, not a change.

| Wookieepedia | what it says | SWG mapping | proposal |
|---|---|---|---|
| Kingwood | tall straight-trunked trees with heart-shaped leaves, on the slopes below the Academy | `wood_deciduous_ossus` (Hard Wood, 113 recipes) | text "Kingwood Deciduous Wood" |
| Bambwood | jungle plant, a hedge at the Academy | `softwood_evergreen_ossus` (Soft Wood, malleability 800–1000, cane-like) | text "Bambwood Evergreen Wood" |
| Dbergo tree | jungle tree with big red fronds | no clean class: not a conifer | flora and decor only |
| Wodobo bush | bush that grows by the Academy | the page gives no fruit | flora only; "Wodobo berries" would be our invention |
| Potam | a food served in the Academy kitchens (40 ABY); gokobs steal it | `vegetable_tubers_ossus` is our reading; the page doesn't say what it is | text "Potam Tubers", flagged as our reading |
| Kyleme, Fizzer | snack and drink sold in the Academy's pilots' lounge | prepared food, not a raw resource | names for a Chef or Bartender recipe |
| Roo-wood | furniture wood: a table in the Academy; chairs on Valnoos | the page doesn't place it on Ossus | not an Ossus native |
| Ysanna valley farms | nitrogen-rich valleys under the Eocho Mountains | the domesticated corn, rice, oats and wheat natives | a lore reason for the grain natives; no change |
| Uneti tree | **canon only** (an old-growth forest on Ossus by 9 ABY) | – | not used |

## 3. Fauna

Creature resources come from creatures, and Ossus already has every native. The mapping says which creature should
drop what, for whoever builds Ossus's creature spawns.

| creature | what the page says | meat | hide | bone / other | gameplay hook |
|---|---|---|---|---|---|
| Mud yak | hairy horned herd grazers of swamps and marshes, about 3 m, dig river roots with downswept horns | `meat_herbivore_ossus` | `hide_wooly_ossus` | `bone_horn_ossus`, `milk_wild_ossus` | the obvious herd creature for Ossus's wetlands |
| Kirruk | reptilian quadruped mount the Ysanna tamed after the Cron disaster; named for its squawk | `meat_reptilian_ossus` | `hide_scaley_ossus` | `bone_mammal_ossus` | tameable; a mount if our build supports it |
| Gokob | friendly hairless canopy rodent that sprays a stinking mist; raids the Academy kitchens | `meat_wild_ossus` | `hide_leathery_ossus` | `bone_mammal_ossus` | a harmless critter with a stink debuff |
| Ossus tree frog | big tree frog whose tongue can pull down a trainer craft | `meat_reptilian_ossus` (SWG has no amphibian class) | `hide_leathery_ossus` | – | tongue grab as a snare or root |
| Tribis | small bipedal reptavian | `meat_avian_ossus` | `hide_scaley_ossus` | `bone_avian_ossus` | small prey |
| Kaddyr bug | chirping insect | `meat_insect_ossus` | – | – | ambient |
| Adegan eel | snake-like eel of the Adega system; a royal snack in Old Republic times | `seafood_fish_ossus` | – | – | a fishing catch name |
| Goldie | pet fish kept at the Academy | – | – | – | a decor fish tank |
| Arges frog | **canon only** | – | – | – | not used |

## 4. Energy and the rest

- **Twin suns.** The figure-eight orbit gives weeks without night. A stated variant could raise
  `energy_renewable_unlimited_solar_ossus` above the stock native's PE 200–600, e.g. to 500–1000. Not staged.
- **Water vapor.** The boiled-off seas give `water_vapor_ossus` a lore reason. No change.
- **Radioactive.** The Cron supernova's fallout gives `radioactive_ossus` a lore reason. No rename needed.

## 5. The Yuuzhan Vong line (owner, 14 Oct: coral as a new class, "option A")

Ossus is where Vong biotech belongs in 138–139 ABY:

- The Ossus Project used the Shaper caste (Master Shaper Nei Rin, with Kol Skywalker) to heal the planet. Ossus came
  through untouched by the mutations the Sith sabotage caused elsewhere.
- In 137 ABY, Nei Rin and her Vong were hiding under the Temple, guarding the lost Jedi vault.

| Wookieepedia | what it says | use |
|---|---|---|
| Yorik coral | the Vong's grown shipbuilding material; it absorbs the rock or ore it grows on, needs organic matter too, and is run through with nerves and vessels. Used for missiles; after the war it was park decor on Coruscant and kept growing in the undercity | the new class (owner): decor, weapons, armour, ships. A recipe can "grow" it from ore plus organics, as the page describes |
| Lambent | crystal fruit of a Vong plant, cut from a sac behind the leaves after calming the plant; it brightens or dims with its owner's thoughts and can sense hidden enemies | the Vong line's gem: lamps and decor, a sensor or scanner component |
| Voxyn | Vong-bred Jedi hunters: eight legs, sonic scream, acid. All were clones of one queen and could not breed; the last died in 28 ABY | **lore problem for pets:** none exist in 138 ABY. Bringing them back needs a story, e.g. Nei Rin's Shapers growing a tame line, which would be our invention. The owner decides |
| Yorik-kul | Vong coral seeds. Krayt infected prisoners with them in 137 ABY; his own Vong implants grew a bony exoskeleton that served as his armour | the raid tie-in: coral armour drops, and Krayt's armour as the secret boss's prize |

## 6. Where new classes go in the tree (for the beskar and coral classes the owner chose)

A schematic accepts a class and everything under it, so placement decides who can use the new class:

| class | recipes that accept it |
|---|---|
| Iron | 693 |
| Metal | 590 |
| Mineral | 116 |
| Inorganic | 45 |
| Organic | 72 |
| Creature Resources | 76 |
| the root "Resources" | none |

- **Beskar** under iron would be the best iron in 693 recipes. That is what option A avoids.
- **Yorik coral** under Organic would feed 72 recipes.
- To keep each class to its own recipes, both go **directly under the root** as their own branches:
  - "Mandalorian Iron";
  - "Yuuzhan Vong Biotech" > "Yorik Coral" (Lambent can sit beside it later).
- Survey tool and container are per row, so they can still be surveyed or looted.
- Only the new schematics that name these classes will take them.
