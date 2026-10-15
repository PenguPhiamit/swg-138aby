# Owner decisions for Fable - 15 October 2026

Checked against `SWG-handoff.md` Questions, all Fable README owner sections (including nested batches), both `Agent/to-*.md` files and relevant archived answers. Paths are relative to `outputs/`. **Defaults below are suggestions for an explicit answer, never consent by silence.** No choices made here. "Open" means no answer found in those local records; unrecorded chat answers are **UNVERIFIED**.

Already settled and omitted from the questions: Ossus after Echo Base E0; Chiss first; all 18 Hoth deeds; Hoth levels 62-115/rancor 400; keep the outpost and leave south; 138-139 ABY after Krayt's final death; Adegan grade names; beskar and yorik coral as separate classes; full use of the bot author's own work with donor licences retained. Evidence: `../AGENTS.md`; `SWG-handoff.md` Q2/Q10/Q11; `Agent/to-chatgpt.md` 14 Oct owner decisions and 18:50; `SWG-handoff-archive.md` 14 Oct 14:56 and 15 Oct 00:01/01:32. A played Chiss clears S6's stated prerequisite; it does not prove every S5 checklist item.

## 1. Ossus after E0 - highest design priority

| ID | What the owner can answer | Sensible default to consider | Evidence / what it unblocks |
|---|---|---|---|
| O0 | E0 client result: usable NGE interior, or failed/needs repair? Then base as ruin, recovered base or repurposed site; current holder, shuttleport and GCW yes/no? | Record the door/cell/collision result first; postpone E1 design until it is known. | `Fable-echo-base/README.md` section 4; `Fable-hoth-guide/echo-base-plan.md` E1-E5. No completed visual result found. |
| O1 | Who holds Knossa: no garrison, an era-appropriate Imperial remnant/One Sith presence, or another faction? Hidden Jedi encounters yes/no? | Light local/Ysanna presence with rare hidden Jedi; no large garrison until its story is chosen. | Board Q10; `Fable-planet-test/README.md` section 6; `Fable-ossus/o5/README.md` section 4. Era itself is already answered; do not offer the standing pre-138 Temple timeline again. |
| O2 | Keep fares 3000 outward/1750 return/100 local and map position (425,290), or change? Keep current region names and terrain scale, or adjust after the look? | Keep current test placeholders pending one annotated client visit. | `Fable-ossus/README.md` questions 1-5; `o5/README.md` section 4. O3/O4 already provide map/globe/loading art: don't ask to approve obsolete generic placeholders. |
| O3 | Accept cave bodies/current ruins composition and no-build radii (Knossa 320 m, ruins 260 m), or change caves/add scorched ruins/alter housing space? | Keep first-look layout until client evidence identifies a problem. | `Fable-ossus/o2/README.md` owner questions 3-5. Ground/interior acceptance remains unverified here. |
| O4 | Fauna: retain the six reviewed creatures and current levels, or redesign levels/names after habitat checks? Accept stock body stand-ins for native creatures? | Retain reviewed six for baseline; treat more species as a later art/design batch. | `Fable-planet-test/ossus-assets/README.md` section 5.5; O2 questions 1-2; dev `80b66e65` replaces the earlier placeholder roster/level assumption (base levels 6-19; `Agent/to-claude.md` 15 Oct 01:36). |
| O5 | Adegan grades: identical ranges or progressively stronger kathracite to pontite ranges? | Keep equal ranges until new consumer schematics give grades a purpose. | Board 15 Oct era Q1; `Fable-resources3/names/README.md`. Names themselves are settled. |
| O6 | Kingwood/bambwood/potam names yes/no; Ossus solar PE stock 200-600 or higher (example 500-1000)? | Approve text separately from stat changes; retain stock solar pending balance evidence. | Board 15 Oct era Q3-4; `Fable-resources3/lore/ossus-resource-map.md`. Lore assertions are recorded proposals, not revalidated in C42. |
| O7 | Voxyn at this date: explicitly invented tame Shaper line, a different Vong creature, or defer? | Defer voxyn until the owner selects the fiction; retain the encounter option. | Board 15 Oct era Q2. No fresh lore claim or pet authorisation implied. |
| O8 | Resource consumers: lumni-spice Smuggler recipe yes/no; beskar ranges variant or planet-mineral parity; Corusca from Yavin IV (labelled variant) or GemDiver vendor? | Design consumers first; hold new balance/placement changes until chosen. | `Fable-resources3/lore/lore-materials.md` section 4.2-4. Beskar/coral class choice is settled in archive 15 Oct 00:01; do not reopen it. |

## 2. Species - Chiss is already first and played

| ID | Options | Sensible default to consider | Evidence |
|---|---|---|---|
| S1 | After Chiss: Nautolan/Togruta S6, then Hutt; or Hutt before those? | Finish the already staged S6 pair first. | `Fable-species/README.md` Q1; `s6/README.md`; archive 15 Oct 01:32 clears Chiss gate. S6 is staged, not in inspected dev log. |
| S2 | Zeltron: rights hold, or a stock red-human palette stand-in? Hutt on a human skeleton: acceptable or wait for a better body? | Hold unresolved art; request an explicit yes to any stand-in. | `Fable-species/README.md` Q2-3. Permission to use other games' stock art is not inferred. |
| S3 | Human random-name fallback or custom tables? Chiss flat-100 profile or a designed attribute profile? | Keep the working baseline until a coherent species balance pass is ready. | `Fable-species/README.md` Q6-7; `s5/README.md` owner check. |

Customization splicing, human-rig clothing, S4 ids/mapping shape are engineering choices already implemented in dev `a32566bc`; route future changes to Claude, not another owner decision round (`Fable-species/s4/README.md`; board Q11 technical delegation). Specific wearable coverage still needs checks.

## 3. F86 - first real model into the client

| ID | Options | Sensible default to consider | Evidence |
|---|---|---|---|
| A1 | Approve Blender 3.6 LTS + local MIT add-on install; approve one Quaternius Ultimate Modular Ruins CC0 download; or defer? | One ruin segment, one bounded validation batch, retain licence/hash evidence. | Board Q7; `Fable-asset-pipeline/README.md` section 5. No install/download consent found. |
| A2 | DDS: own writer first, Microsoft texconv, or NVIDIA exporter/account? Optional stock extract for materials? | Own writer first; texconv only if separately approved and needed. Existing map DDS work does not validate mesh textures. | Same section 5.4-5. Optional Sytner editor/account is not needed for the minimum experiment. |
| A3 | Approve staged archive/test-session integration and owner-at-PC visual session once offline checks pass? | Agree the one-prop acceptance session; Claude handles runtime, GPT can check files. | Same section 5.6-8; AGENTS owner-presence rule. This task performs none of it. |
| A4 | Second-pass asset downloads: select specific candidates; request written permission for the $14 pack or skip; use MTG Mustafar temple ruins or stock-only? | Stock first; CC0 candidates only after individually named download approval; defer paid/outbound request. | `Fable-planet-test/ossus-assets/README.md` section 5.1-2/6. No blanket batch approval inferred. |

## 4. Hoth batches - after the above

| ID | Options | Sensible default to consider | Evidence |
|---|---|---|---|
| H1 | Ordinary loot rates: retain 3% common/5% rare/2% deed or change? Bosses corpse-only or per-player rewards? | Preserve existing rates/corpse loot until observed runs establish a need. | Board Q2/Q8; `Fable-hoth-caves/README.md` boss-loot question. All 18 deed types already approved. |
| H2 | Density 1024 or 768; rancor rotation, fixed den or grounds; cream stock hue or new white/blue palette? | Keep density pending census; leave rancor unspawned until mode is selected; stock hue for first check. | `Fable-hoth-batchA/README.md` Q1/4/5. Level 400 is settled. |
| H3 | Mynock den: indoor cave + terrain patch, or outdoor 23-creature den? Camp vendors or starport-only? | Outdoor for the first test, vendors starport-only. Owner must choose; never load both dens. | Board Q9; `Fable-hoth-batchB/README.md` Q1/3; `den-outdoor/README.md`. |
| H4 | Quest credits only or badge/rare-decor/faction extra; add artisan/entertainer terminals; lower mission band; deliver points at camps? | Keep current credits/general terminals/band until C23 acceptance; camp points later. | `Fable-hoth-batchC/README.md` Q1-4; `Documentation-support/C23-hoth-gameplay.md`. |
| H5 | Tauntauns wildlife or rideable via client asset route? | Wildlife until a separate mount validation batch is approved. | `Fable-hoth-batchC/README.md` Q5. MTG scale rows alone do not establish rider slots/usable mounts (`MTG-merges/shadow-audit.md`, Risks 1). |

Map names already exist for 18 approved Hoth sites; don't ask again for general MAPPOI support. Optional den/rancor/Echo Base labels follow their placement decisions (`Fable-hoth-mapnames/sites.tsv`; `Agent/to-chatgpt.md`, 14 Oct 14:35).

## 5. Later backport and parked questions - not return blockers

- **Backport B1/B2 policy:** keep corrected SOE paths or revert; loot groups or staff-only junk/collections; extend wearables with species; investigate disc TRE v6 or defer; keep/drop prison-guard pants. Suggested defaults: retain tested path baseline, staff-only pending economy design, check clothing mechanically, defer v6, keep pants optional. Applied status is not an owner answer (`Fable-backport/README.md` section 8; board Q6).
- **Clean-room F93:** collections or buffs first? Suggested default: after the current content gates, choose the smallest useful slice (board Q4). Still open; not permission to implement both.
- **Discord and old overnight permission prompt:** board Q5 and Q1; no Fable design dependency. Suggested default: keep Discord parked and have Claude check whether the old prompt still exists, rather than asking the owner to approve an obsolete run. `Agent/to-claude.md` 14 Oct 17:40/17:52 retains explicit setup/post gates.
- **Tortoise Retry/epochs/classifier:** delegate to GPT/Claude as engineering; a new service still needs consent (`Fable-tortoise/README.md` section 7). Earlier exclusions/donor-rights holds in `Agent/to-claude.md` remain gates on those sources, not Fable research assignments.
