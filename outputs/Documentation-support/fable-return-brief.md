# Fable return brief - 15 October 2026

Read this first; checked at 12:43 PDT. Paths below are relative to `outputs/`; dev hashes belong to `/opt/swg/Core3-dev`. Reset 21:59 local is the owner's C42 instruction. This is a read-only preparation pass, not deployment approval.

**Current baseline.** Dev HEAD `398744b5`; since 14 Oct 15:00, E0 `8f2072e7`, Ossus `2ada3784`, Chiss `a32566bc`, resources `b7976890`/`9d6b4a78`/`08e6a924`, fauna `80b66e65` and weather `615ca43e` landed. Runtime restart on `398744b5` is Claude-reported, not independently exercised (`SWG-handoff.md`, 12:40 log). Installed client `SWG-client/local_planets.tre` and server `/opt/swg/tre/local_planets.tre` independently hash to **8ad04fecff021f920891facfc6c30739bc2f65f1ea79e7cecac3f85640aa26ed**. `Local-content/local_planets.tre` instead hashes to **aee83cc6...**: do not use it as today's installed baseline. MTG's 119-file merge adds 7,388 names and mount/CRC rows; strings alone do not enable species (`MTG-merges/shadow-audit.md`, final addendum; h `53c9dcc`).

Each entry gives staging -> later change -> remaining gate. Historical "stage only" README headers are not current deployment status.

| Folder | Return point and remaining gate |
|---|---|
| `Fable-echo-base` | E0 fitted shell is now dev `8f2072e7`; error-free loading reported in `SWG-handoff-archive.md`, 14 Oct 18:50. Visual/collision acceptance **UNVERIFIED**; owner client check in `README.md` section 4 precedes E1/fallback choice. |
| `Fable-ossus` | O5, 87-node first-look snapshot, is dev `2ada3784`; map/globe already staged (`o3/README.md`, `o5/README.md`). Six fauna added `80b66e65`; five NPC names in current MTG chain, server wiring still C35 (`Agent/to-chatgpt.md`, 03:51). Needs garrison/Jedi/content choices; full visual/habitat acceptance **UNVERIFIED**. |
| `Fable-planet-test` | Prototype/asset research superseded for deployment by O5 `2ada3784`, not a second planet to build (`README.md` section 5; `Fable-ossus/o5/README.md`). Ossus and 138-139 ABY already chosen (`../AGENTS.md`). External packs/paid permission still gated (`ossus-assets/README.md` section 5). |
| `Fable-species` | S5 Chiss is dev `a32566bc`; owner created and played a Chiss, so S6 may proceed (`SWG-handoff-archive.md`, 15 Oct 01:32). S6 Nautolan/Togruta remains staged, absent from later dev log (`s6/README.md`). Names/stats, Hutt look and Zeltron route remain choices; don't re-ask Chiss-first. |
| `Fable-asset-pipeline` | F86 remains an unexecuted one-prop validation plan (`README.md` opening/section 5). No later dev prop commit found. Needs specific install/download and client-session consent; no exporter/render success established. |
| `Fable-hoth-guide` | Route and E0-E5 design exist (`hoth-first-session.md`, `echo-base-plan.md`). E0 landed `8f2072e7`; guide's "map not verified" is stale: owner saw all 18 markers (`Agent/to-chatgpt.md`, 14 Oct 14:35). Base story/occupier/GCW still open. |
| `Fable-hoth-caves` | Four cave placements already applied (`SWG-handoff-archive.md`, dev `c5f1ae06`). Later resources/weather affect testing (`b7976890`, `615ca43e`). Corpse versus per-player boss rewards still owner question 8; gameplay acceptance open (`Documentation-support/hoth-release-gate.md`). |
| `Fable-hoth-batchA` | Area split/rancor staged then applied (`SWG-handoff-archive.md`, `69eb77fe`; `README.md`). Later resource/weather baseline above. Level 400 already retained (`Agent/to-chatgpt.md`, owner decisions 14 Oct). Density, spawn mode, palette/rewards remain choices. |
| `Fable-hoth-batchB` | Camps applied `de1b679a`; cave and outdoor den alternatives staged (`README.md`, `den-outdoor/README.md`). Map support now exists; old MAPPOI blocker superseded (`Fable-hoth-mapnames/README.md`). Owner still chooses one den and camp vendors. |
| `Fable-hoth-batchC` | Missions/quest staged then applied `23014f39` (`SWG-handoff-archive.md`); later telemetry `58797fdf`/`788e456f`/`7817437a` aids checks. BARC fixed `740b2426` plus MTG merges. Reward extras/terminals/mission spread/tauntaun rides still optional decisions (`README.md`). C23 remains blocked, not accepted. |
| `Fable-hoth-mapnames` | Names/18 POIs already owner-verified (`Agent/to-chatgpt.md`, 14 Oct 14:35); staged method in `README.md`. Current MTG chain preserves them (`MTG-merges/shadow-audit.md`). Held den/rancor/base markers depend on those encounter choices. |
| `Fable-backport` | Batches applied `0c44d431`/`5c7ae017`, sampled C18 review (`Documentation-support/C18-backport-sample-review.md`). MTG merges now restore many missing strings; old unnamed counts need re-audit. Loot policy, wearable extension, v6 research and pants remain owner choices (`README.md` section 8). |
| `Fable-builder` | Own-code builder is installed, not merely proposed (`SWG-handoff-archive.md`, h `c2573e3`; `README.md`). Current chain adds Ossus/species/resources/MTG. Mechanical maintenance; preserve all stages, never publish the Hoth-only intermediate (`SWG-handoff-archive.md`, 14 Oct 18:50). |
| `Fable-live-client` | L1 partial/T2 held by owner prioritization (`README.md`; archive 14 Oct 14:56). Test archive has advanced to 8ad04fec; L1's 20-file example is historical. Live delivery/rollback remains C24 gate; no new Fable design needed. |
| `Fable-resource-names` | R1 established CLASS text drives names (`README.md` section 1). R3/lore/grade naming supersedes 777-row audit (`Fable-resources3/names/README.md`). No new naming-file repair needed; owner chooses future names/grades. |
| `Fable-resources2` | R2/T1 landed; R2 corrected `98ad1d1d`, scaling `3a0b154f`. C24b source re-review passes; repeated-start/gameplay gates remain (`Documentation-support/hoth-release-gate.md`). No owner choice blocks mechanical acceptance. |
| `Fable-resources3` | R3/lore are dev `b7976890`/`08e6a924`; grades renamed in current chain (`names/README.md`, `MTG-merges/build_mtg_merges_archive.py`). Beskar/coral separate classes chosen (archive 15 Oct 00:01). Grade ranges/flora/solar/consumer recipes remain decisions. |
| `Fable-tortoise` | Backoff/incidents staged, checked offline (`README.md`, h `f12c2f0`); integration **UNVERIFIED**. Since then escort/staging changed (`SWG-handoff.md`, 12:40 log). Retry/epochs/classifier belong to GPT engineering; only a new service needs owner consent. |

**Fable design effort** (owner order: archive 14 Oct 14:56):
- Interpret E0 evidence, then Ossus encounters/quests and era presence; species S6 presentation; later Hoth story/rewards.
- Resource identities and new schematic consumers after owner choices (`Fable-resources3/lore/lore-materials.md` section 4).

**Mechanical work for others:**
- GPT: C23/C24 acceptance reporting, S6/source cross-checks, Tortoise integration; Claude: review/build/runtime and C35.
- Haiku: inventories, licence evidence, table splices and housekeeping with checked manifests; local model: drafts only, stronger review required (`SWG-handoff.md`, 11:40 log).
- Downloads/installs only after specific owner yes; F86 execution and L1 kit need engineering/checks, not another design census (`Fable-asset-pipeline/README.md` section 5).

## Hutt (added by Claude, 15 Oct 15:10; owner: "maybe we could use it [Universal Modder] for the hutts?")

**Correction to `Fable-species/README.md` (owner question 3):** the package's player Hutt is not a Hutt on the human skeleton. `object/creature/player/shared_hutt_male.iff` (mtg_patch_023) uses `appearance/hutt_m.sat`, and that file (data_other_00, 177 bytes) names `appearance/mesh/hutt_m.lmg`, the skeleton `appearance/skeleton/hutt.skt` (4 LODs, 47 bones at LOD 0) and the animation table `appearance/lat/hutt.lat` (patch_05 copy wins). Only the sound file `clientdata/player/client_shared_player_human_m.cdf` is human. Checked by extracting both files with `tools/swgfmt/fmt_tools.py`.

**What a player Hutt can and can't animate** (counted from the tables; the human tables are `all_m.lat`/`all_f.lat`):

| | Hutt | Human |
|---|---|---|
| ANIM entries | 206 | 908 |
| Walk, run, swim, death | yes | yes |
| Melee attacks / get-hit | 5 / 4 | 14 / 21 |
| Ranged stances | 20 (pistol) | 73 |
| Emotes | 22 | 190 |
| Sit, mount, dance, kneel or crouch, survey | none | yes |

Human clothing and armour are built for the human skeleton, so they won't fit a Hutt either.

**Existing NPC Hutts in dev:** Jabba (`mobile/tatooine/jabba_the_hutt.lua`, Jabba's palace), Borvo and Shalera (quest Hutts), the Hutt expeditionary force leader on Yavin 4, and the plain bodies `object/mobile/hutt_male.iff` and `hutt_female.iff` (the same `hutt_m/f.sat` the player template uses, so a spawned NPC shows exactly the player look).

**For Fable's design:** a playable Hutt is a restricted species, or it isn't playable at all. Options to weigh:
- **(a) Restricted species:** no mounts, no dancing or entertainer buffs, no clothing (or Hutt-only items), a short emote list. It suits trader, crime-lord, politician and merchant roles. The engineering list would be: refuse those actions for the Hutt race with a clear message, a race-restricted item set, and the species tables as for Chiss.
- **(b) A Hutt on a repulsor sled:** the Legends look. The Hutt has no rider pose, so this needs new animation or art work; the hardest option.
- **(c) NPC-only Hutts:** crime lords and quest givers. The 138-139 ABY setting has Hutt cartels to use.

Universal Modder evidence for the owner: Claude takes `um win shot` screenshots of a spawned Hutt in the owner's client (`/createSpawningElement spawn object/mobile/hutt_male.iff`), saved outside the repo because they show the owner's character name.
