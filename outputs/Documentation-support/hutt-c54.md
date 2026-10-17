# C54: playable Hutt review and Artisan floater

Reviewed by ChatGPT, 16 October 2026. Review target: dev `26b54813`; client builder `Fable-species/s7-hutt/build_test_archive.py` and its recorded archive SHA-256 `7f28f0272a0924596abd483681b6d8160302fe58159046652a040cd22bc5ba94`. Requirements: S7 README sections 5 and 7, with the owner's later answers taking precedence.

Source/review work is complete on **`gpt/c54-hutt-floater`**, cut directly from dev HEAD `26b54813` in `/opt/swg/Core3-gpt`. Claude still owns `/opt/swg/Core3-dev` and the galaxy. **Run 10 received no commands, restart, stop, installation or deployment.** Full-server compilation and all gameplay remain **untested**. The client-profile and builder findings below still need work before acceptance; this is not a release approval.

## Ranked findings, with failing cases

### F1 — P1: Hutt templates identify themselves as Wookiees, bypassing the Hutt rules

Locations: both `bin/scripts/object/creature/player/hutt_{male,female}.lua:6`; inherited MTG `object/creature/player/shared_hutt_{male,female}.iff`; `CreatureObjectImplementation.cpp:4375`.

Both shared templates contain `species = 4`. `CreatureObject::getSpecies()` reads the creature template, rather than `Races.h::TemplateSpecies`. Neither new Lua template overrides this. The otherwise-correct `0xEA` race rows therefore do not make either player template a Hutt for the new conditions.

**Failing case:** create either Hutt gender with the reviewed commit, then attempt a disallowed mount or chair sit. Its species comparison evaluates `4 == 0xEA`, false. The mount restriction and chair refusal are skipped; the player-container error also selects its generic message. The new Hutt name case would similarly go unused. The species fields and source call path were checked offline; an actual creation visit was not performed.

**Prepared fix:** `82e52303` explicitly sets `species = 0xEA` in both player templates. The template loader's `SharedCreatureObjectTemplate::parseVariableData` handles that Lua field. Claude must compile and verify both genders in game.

### F2 — P2: the archive supplies the wrong racial stats and limits

Locations: `build_test_archive.py:50`; `s4/tools/species_tables.py:148`; output `datatables/creation/racial_mods.iff` and `attribute_limits.iff`; server `PlayerCreationManager.cpp:1085`.

The generic stager copies the package row instead of applying S7 5.2. The installed S7 Hutt racial row is **350/350/150/200/100/100/100/150/100 (1,600 total)**, identical to the package Wookiee profile, instead of **100/150/300/0/0/50/0/0/300 (900)**. Its attribute limits are the human row, all nine ranges 400–1100, total 5400. The correct Lua `baseHAM` does not fix creation: profession defaults replace the base HAM, then `addRacialMods` adds the data-table mods.

**Failing case:** create a Hutt Artisan using this server/archive pair. Its racial contribution is the 1,600-point table row, so, for example, Constitution receives 150 rather than the approved 300, and Willpower 100 rather than 300. The creation limits also remain the human limits. These are decoded-data/source counterexamples, not a measured live character.

**Open:** Claude must make explicit approved Hutt rows in the client builder and the server's matching archive. Validate the limit derivation against the stock species pairs and server creation reader; do not treat Lua HAM as the creation-data override.

### F3 — P2: the creation description retains unapproved imported prose and contradictory stats

Locations: `s4/tools/species_tables.py:232`; output `string/en/player_species.stf:desc_hutt`; S7 5.1.

The stager writes our description only when the key is absent. This base already has `desc_hutt`, so the builder preserves the older multi-paragraph imported lore text. Its attribute display says **0/0/250/250/300/0/100/0/0**, matching neither S7's approved profile nor the archive's actual racial row. S7 expressly requires our own prose; the generic stager's own documentation identifies the package descriptions as Wookieepedia text that should not be used.

**Failing case:** select Hutt in creation and read the attribute description. It advertises zero Health/Strength and 300 Quickness, while the actual racial row gives 350/350 and 100. The selected string key and decoded contents establish the mismatch offline.

**Open:** replace this existing key with S7's original text and approved attributes, and use the requested skill labels. Keep attribution/licence decisions separate from technical success; do not ship the retained imported description as our prose.

### F4 — P2: disallowed vehicle calls are permitted

Locations: `VehicleControlDeviceImplementation.cpp:22`; `MountCommand.h:55`; S7 5.4.

The commit adds only a mount-time test. `generateObject` has no Hutt guard before it schedules the call or spawns the vehicle. Additionally, the mount command uses the message intended for a datapad call instead of the specified saddle message.

**Failing case:** a Hutt outdoors, out of combat, owns an X34 control device and chooses Call. With an empty spawned-vehicle slot, the call path proceeds to its delay/spawn; the requested call refusal never occurs. This persists after F1 is corrected unless the call path is also changed.

**Prepared fix:** `82e52303` refuses the call before scheduling/spawning unless its controlled vehicle is `object/mobile/vehicle/a1_deluxe_floater.iff`, with the exact call text; the mount command now uses the exact saddle text. Both currently share the single launch exception as literal template checks. The proposed configurable `huttVehicles` Lua list remains unimplemented; adding another allowed platform will require updating both checks.

### F5 — P2: chair refusal reports success without performing the ground sit

Location: `SitServerCommand.h:55`; S7 5.4.

The new branch sends the refusal then returns `SUCCESS`, without calling `setPlayerPosture` or setting `SITTING`. This is separate from F1's unreachable branch.

**Failing case:** with species corrected, an upright Hutt clicks a chair after posture cooldowns have expired. The command returns success and the character remains upright server-side, instead of entering the ground-sit posture at its current position. The idle visual stand-in does not remove the server posture requirement.

**Prepared fix:** `82e52303` routes that branch to `setPlayerPosture`, preserving posture cooldowns and avoiding chair teleport/state. The owner must verify server posture and position, since Level 1 intentionally looks upright.

### F6 — P2: archive checks accept a stale or invalid cached animation table and unrelated edits

Locations: `build_test_archive.py:52,69,78` and `checks.json`.

An existing staged LAT is copied without rebuilding it or invoking its checker. `checks.json` records changed filenames but enforces no allowed-change set or species-content assertions; its only final assertion checks dropped entries. Thus its claimed closure/unchanged guarantees are weaker than the script's docstring.

**Failing case, executed in a disposable directory:** invoke the actual builder with an existing cached `hutt.lat` containing `not an IFF`, and a stub stage that changes an unrelated retained entry. The builder writes the archive and returns **0**. No real client/archive was changed by this counterexample. A changed animation map with an existing old staged LAT follows the same unchecked-cache branch.

**Open:** always rebuild or validate/cache-key the LAT against its inputs, validate species facts against S7, and assert an explicit set of permitted mutations plus byte equality for everything else. The current recorded archive does have a valid LAT; this finding concerns the builder's acceptance gate.

## Checks that passed and remaining specification gaps

- All six race arrays align. A small C++ harness compiled the actual `Races.h` and checked both Hutt rows, species `0xEA`, genders, CRCs, reverse lookup and bounds. Independent SOE CRC calculation reproduced male `0x916443F9`, female `0xE0B607C0`, and the Chiss control `0x02F60EAC`.
- `objects.lua` registers the two shared templates before the player includes. Both Lua HAM arrays match the approved nine numbers and total 900; the default six child objects and `PLAYERCREATURE` type follow the established player shape. Hutts were not added to `humanRigRaces`.
- Basic comprehension/speech exist. No `social_language_huttese_*` rows exist in the resolved skills table, so omitting them follows S7 5.3's conditional requirement. Do not award nonexistent skills.
- The recorded S7 archive independently matches its hash: 173 original entries, 164 byte-identical, nine changed, one new LAT, none dropped. This proves preservation for this artifact, not correctness of its changed data.
- The LAT checker was actually rerun with `--check`: **21 checks PASS**, 837 entries, 208,161 bytes, hash `1b7e2f03b314f64454f992ad1be0e4487c7087ec3593fd707e2430ebbcf0aa7b`. Both male and female SATs reference `hutt.skt` and this `hutt.lat`. Bone/reference/round-trip checks are offline checks; animation appearance remains untested.
- The archive has no explicit Hutt NAME-only hairstyle or empty equipment/profession PTMP blocks. Absence may currently yield empty results through the server's missing-entry handling; no clothing/hair fallback defect is claimed without a client visit. Add the S7-required blocks or document and test the equivalent absence behavior. The UI also retains the package camera offsets (0.9/5); framing is an owner check.
- Existing Hutt customization appearances are present in ACST, so the generic stager skips them. That is not the requested S7 male/female customization comparison. Palette coverage remains unverified.
- S7's proposed canon-name blacklist conflicts with the owner's later **15 Oct instruction allowing canon names** in `name_manager.lua`. C54 follows the owner and does not restore that blacklist. No new source downloads or art imports occurred.

## What C54 built

Cherry-pick these commits in order from `gpt/c54-hutt-floater`:

| Commit | Change |
|---|---|
| `82e52303` | Explicit Hutt template species, ground-sit fallback, vehicle-call refusal and exact mount message |
| `deb3319e` | A1 Deluxe Floater mobile, deed, PCD and draft schematic; shared-template declarations, includes and schematic registry |
| `8ebace32` | `managers/name/species/hutt.lua`, require, `huttData` member, load, destructor/reload deletion and `getSpeciesData` case |

The vehicle trio is cloned from the X34 files with their SWGEmu licence headers retained. Mobile `templateType = VEHICLE` follows `740b2426`; deed remains `VEHICLEDEED`. Speed is **20 m/s run, 10 m/s walk**, with X34 decay 15 every 600 seconds. The PCD keeps the X34 shape and relies on the existing MTG vehicle-PCD shared template. The craft recipe retains X34's tool tab, complexity, assembly/experimentation, durability, XP and resources: **1,125 nonferrous metal + 3,125 ferrous metal**. It produces the floater deed, which produces the floater PCD/mobile.

The existing resolved schematic group data puts X34, speeder bike and swoop in **`craftArtisanVehicle`**, granted by **`crafting_artisan_master`**. A new unique shared draft is necessary: reusing X34's shared CRC would make client-ID lookup ambiguous. C54 registers `shared_a1_deluxe_floater.iff`, CRC **`0x2386AC6B`**, distinct from X34 **`0xBD720FA1`**.

`tools/build_hutt_c54_crafting.py` stages that shared draft from the owner's local X34 template, replaces its crafted-deed reference, gives it a distinct display-name key, and appends the recipe to the actual X34 group. A final reference check found MTG's `pet_deed:a1_deluxe_floater_deed` key missing from the resolved table; the builder adds our original **A1 Deluxe Floater Deed** and **A1 Deluxe Floater** labels while retaining every existing string. It creates an archive for **later integration on both server and client**. It never installs anything. The floater's mobile/deed/PCD and art are already in the owner's MTG archives; no external asset source was added.

Invocation from the project root:

```powershell
& C:/Users/Pengw/miniconda3/python.exe -I outputs/tools/build_hutt_c54_crafting.py
```

Default output: `work/c54-crafting/local_planets-c54.tre`, SHA-256 **`70423ace9809a51895582aae77062dbc6a65ef95c454659230025d9e8c6f9140`**. It retains all 174 S7 entries (173 byte-identical; only `pet_deed.stf` gains two labels) and adds the schematic group table and unique shared draft (176 entries). Rebuilding on its own result is idempotent. **It inherits F2/F3 and does not repair the reviewed S7 profile.** Claude should first fix the Hutt species staging, then pass that reviewed archive as `--base` and regenerate; the hash will change. Generated client data and archives stay local/untracked.

The original name table supplies 33 distinct syllables from S7 and all 12 invented kajidics, shared by both genders, two or three first-name syllables, no punctuation, and nominal 40% surname omission. The stock generator's inclusive `random(100)` makes omission 41/101 (~40.6%); its unique/special chances use 101 to ensure generated surnames always come from the kajidic list. Names are capitalized by the existing NameManager.

## Verification and integration limits

- **17/17 changed/new Lua files:** `luac5.3 -p` PASS. This includes the reviewed Hutt player files and every C54 Lua registration/include.
- **Entire tree:** all **47,406** Lua files were checked individually. Exactly one existing failure: `managers/databaseversions/2573version.lua:10`, missing `then`. It is byte-identical to dev HEAD; left untouched as unrelated work.
- Executed a Lua registration harness over the actual shared declarations/includes and four new templates: chain references, template types, speed, resource quantities, single recipe registration and exact kajidic membership PASS.
- Compiled and ran the actual race header in a minimal type-stub harness at `nice -n 10`; this is not a server build. All-tree inspection found **no `CMakeCache.txt` in Core3-gpt**, so no existing build was available. No build tree was configured and Claude's dev build was not used.
- NameManager lifecycle and dispatch were inspected; full-engine generation/reload and the C++ refusal paths remain uncompiled and game-untested.
- `git diff --check` PASS; generated archive readback, input conservation, unique CRC, group/master grant and idempotency PASS. Machine-readable evidence: [hutt-c54-checks.json](hutt-c54-checks.json). Local reproducibility harnesses are `work/c54-{qa.lua,qa.py,final-qa.py,evidence.py}`.

## Owner's in-client floater checks, after Claude integrates and approves testing

Do these after run 10 is released by the owner and Claude has reviewed/cherry-picked, built, and loaded a corrected matching archive. **These steps are a test plan; none was executed in C54.**

1. Create one Hutt of each gender; confirm species-specific refusals and random names, the corrected description/HAM, and no default human clothes. Use a Hutt Artisan for the vehicle visit.
2. At Novice Artisan, confirm the floater is absent. Train **Master Artisan**, open the same crafting-tool category as X34, and confirm **A1 Deluxe Floater** appears beside the basic speeders. Verify X34, bike and swoop remain separate recipes with their original names and outputs.
3. Insert 1,125 nonferrous and 3,125 ferrous metal; assemble and experiment. Confirm the finished item is the **floater deed**, rather than X34, with sensible durability and the floater preview/name. If using a factory, verify the usual X34 manufacturing path separately.
4. Use the deed outdoors with datapad space, then Call. Confirm the floater appears, mounts, turns, stops and dismounts normally. On flat clear ground, check approximately 200 m in 10 seconds at full speed, allowing for acceleration and measurement error; intended run speed is 20 m/s. Check storing, calling again and relog persistence.
5. Capture front/side/back views for both Hutt genders: tail through platform, body/saddle height, steering animation, idle/run pose and camera framing. Level 1 riding is intentionally a static Hutt pose; note clipping. Check ground, slopes, shallow water and a transition back to foot. Do not change vehicle scale without recording it.
6. Call an X34 from the Hutt datapad: expect **“A Hutt cannot ride this. Sell it, or give it to someone with legs.”** and no spawned X34. Attempt to mount a nearby disallowed mount: expect **“That saddle was never built for a Hutt. A Hutt travels by repulsor platform.”** Verify a regular species can still call/ride both the floater and ordinary speeders.
7. Click a chair: expect the chair refusal, no teleport/chair state, and ground-sit posture at the same position after cooldown. Check ordinary `/sit`, stand, kneel, prone, sneak, dance, survey and craft; record remaining Level 1 visual limitations separately from functional failures.

Next: Claude reviews the three source commits and stages the client corrections F2/F3/F6, completes the explicit creation/customization checks, then compiles gently and arranges the owner's client visit. No live merge or deploy is authorized by this report.

## Owner's in-client test, 16 Oct (Claude)

1. **4:12 PM, client crash at creation** (integer divide by zero, customization screen).
   - Cause: no `palette_columns` row for the Hutt skin palette `npc_species_hutts.pal` (32 colours, 0 columns), and no Hutt blocks in `default_pc_equipment`, `default_pc_hairstyles` and the six `profession_defaults` tables (the client used the human-male clothes).
   - Fixed in the S7 builder (`a07b46e`) and installed on client and server (`6ff21312`). Creation now works.
2. **4:35 PM, the created Hutt cannot be played.** The camera and UI respond, but W moves nothing, even locally. Chat, `/kneel` and right-click menus do nothing, and the server receives nothing.
   - The server side is fine: an agent-client Hutt (`huttcheck`) chatted, knelt (posture changed), took the starting-city command and got its helper droid. Its health/action/mind and posture were normal.
   - An A/B archive without our generated `hutt.lat` (`dc79c11a`) made no difference, so Level 1's animation table is not the cause.
   - Likely cause: the client cannot control the Hutt rig as a player.
     - Every playable species, the Ithorian included, uses a body skeleton with the human bone names (`Head`, `neck`, `hold_l`, `hold_r`, `lArm`...), a separate face skeleton, and the shared `all_m.lat`.
     - `hutt.skt` has `head` (lowercase), no `neck`, no `hold_l`, its face bones inside the body skeleton, and no face skeleton.
     - MTG's player Hutt templates come from a later client whose code knows Hutts; our pre-CU client does not.
   - Not proven: the client's code is closed, so this is the best structural explanation, not a traced one.

3. **5:46 PM, rig experiment (owner: "test once")** (`d3bfe26`, archive `dd28259b`, client only).
   - What it added: 35 human bone names and `hold_l` on `hutt.skt`, and the human face skeleton attached at `head`.
   - Result: the client crashed on character select, before the Hutt logged in, and left no crash dump.
   - The client is back on `6ff21312` (5:54 PM), matching the server.
   - Untested: bones only (no face skeleton), and the reverse.
4. **6:00-6:45 PM, narrowing it down.**
   - Bones only (`12e035e4`): no crash, but the animation is broken and the Hutt still can't interact.
   - The Wookiee appearance on the Hutt templates (`1e39dbbe`): still no interaction, so the rig is not the cause.
   - The owner's **Chiss** could not interact either on that archive, so the problem is not the Hutt at all.
   - Server side is fine:
     - a gdb dump at 6:10 PM shows no stuck locks;
     - an agent-client Hutt opened the character builder and navigated it (Character Options returned its page).
   - The builder has not handed out an item on run 13 today ("[CharacterBuilder] gave player" never logged).
   - **On the pre-Hutt archive (`f1046025`, this morning's backup) the owner's characters work again** (6:42 PM).
   - So one of today's archive changes breaks interaction in the real client for every character:
     - **S7 tables:** racial_mods, attribute_limits, allow_bald, customization_data/group_instance, skills, skl_n, skl_d, player_species, ui_avatardata.inc, hutt.lat;
     - **C54:** schematic_group, pet_deed.stf, the floater schematic;
     - **4:20 PM creation fix:** palette_columns and the eight creation tables.
   - Checked and ruled out:
     - Every overridden datatable is the client's real winning copy plus our rows, with nothing dropped.
       - The earlier "schematic_group is MTG's" claim was wrong: `swgfmt.tre_write.read` cannot open most stock `patch_*.tre` (one record fails its checksum), so `trn_iff.client_file` silently picked older or MTG copies. The real winner is `patch_12_00`, identical to MTG's.
     - The UI loaded the same element counts on both archives.
   - Next: bisect the three groups with the owner's Chiss, one client restart each.
