# SWG handoff archive

Finished task rows and older log entries moved out of `SWG-handoff.md` to keep the board short (it is read every session). Newest first within each move.

## Moved 2026-10-18 07:32 (ChatGPT, C62 newest-four log trim)

### 2026-10-18 02:31 ChatGPT: C63 first 20 reports reviewed
- `e51ab16`: 20 dated source reviews/corrections in queue order; only those topics set done/reviewed. Rejected unsupported profession/bug rankings and automatic proofreading edits; corrected XP, timer, density, deed-return and harvester claims. Source: dev `aa52cc647a21`, read only; no builds, server writes, galaxy commands or gameplay checks. 47 still in review, listed in `Agent/local-research/C63-review-2026-10-18.md`; next `vehicle-mount`. Saluki report absent, partial results used as leads. Older log entries moved to archive to retain newest four.

### 2026-10-17 11:30 PM Claude: missions run 3 (new body): the exact refusal message arrives; bounty and group pay still open

- **Run 3,** 11:18 to 11:28 PM: Forn and Cresh on the new body (dev `1be13676`; the main session restarted the bodies at 11:14 PM at the owner's request). There was no restart and no build; the main session's OK covered this one run, and work stops here for tonight. Reports: `Bot-reports/Forn/20261017-232839-forn-missions.json`, `Bot-reports/Cresh/20261017-231834-cresh-missions.json`.
- **PASS:** the 7th mission is refused, and the exact message now arrives: `@mission/mission_generic:too_many_missions`. That closes section 11's "exact message" gap.
- **Bounty, still open:** Brask stepped up to the terminal and listed 30 more times, but no bounty offers came, so range is not the cause. Ressa's far bounty was not aborted. Cause unknown.
- **Group pay (dev `cbd85fdf`), still unchecked:** none of the 6 destroy offers was difficulty 10 or less within 2.3 km.
- **New body finding:** Forn's walk to a terminal 1 km away failed at once with "walking without z requires the /agentpath helper". Imperial recon was accepted, but its walk stopped 1203 m short (it passed in run 2).
- Scenario commit 842a068 (`mission_abort` for a far bounty; step up to the terminal; `Bot.abort_mission`).

### 2026-10-17 11:15 PM Claude: missions section 11 rerun on run 30: survey, scout and imperial recon PASS; bounty and group pay still open

- **Galaxy time from the main session** (lock holder): two squad runs on run 30, no restart and no build. Run 1, 10:04 to 10:29 PM, was Besh, Forn and Cresh; run 2, 10:33 to 11:13 PM, was Forn and Cresh, on the old body binary (this session's permissions blocked restarting the bodies onto dev `1be13676`; the main session said to go ahead without it). Reports: `Bot-reports/Besh/20261017-221205-besh-missions.json`, `Bot-reports/Forn/20261017-222849-` and `-231347-forn-missions.json`, `Bot-reports/Cresh/20261017-221504-` and `-223456-cresh-missions.json`.
- **PASS, exact share (reward // group size):** artisan/survey 471 → 117 (4), 290 s; scout/recon 454 → 90 (5), 510 s; imperial/recon 573 → 114 (5), 809 s. Also artisan/crafting 67 → 16 (4), 104 s, and scout/hunting 2051 → 410 (5), 673 s. Section 11 now stands at 9 of 11.
- **Not completed:** bounty. Ressa's accept was refused because she already holds a far bounty and the server allows one at a time. Brask's 30 lists then showed no bounty offers, probably because he stood out of the terminal's range. Group pay (dev `cbd85fdf`) is still unchecked: Cresh's group died at a held difficulty-14 lair, then no destroy mission of difficulty 10 or less was within 2.3 km.
- **Scenario commits:** 89737ca (bounty lists again until a target is within 4 km; recon with a team; Forn's walkers trained as Marksmen) and 3a4414e (one bounty per hunter; a walk to the building after "no path"; Cresh's destroy at difficulty 10 or less).
- **Next:** for bounty, a range check before listing, or `mission_abort` on Ressa's far bounty once the bodies run `1be13676`; for group pay, an easy lair, or the general terminal of another city.

### 2026-10-17 9:50 PM Claude: overnight simulated population restarted on run 30

- **Owner, about 9:45 PM:** "restart the test galaxy onto run 30 with all the waiting fixes and start the overnight bot population". The main session (server lock, `e9df7e1`) restarted and started it; it watches the run.
- **Run 30 up since 9:47 PM:** dev `4b113bb7`, archive `e126125c`. `BotPopMax` 1,700: 1,500 multiclass bots plus 200 Ossus explorers queued, both accepted; 1,160 online at 9:48 PM. The memory watchdog is running.
- **Reports:** the 7 AM job `morning30.sh` writes `Bot-reports/launch-sim/numbers-run30.md`, `findings-run30.md`/`.json`, `travel-run30.md`, `morning-run30.txt` and the planet data.
- **Gap:** the galaxy was off from the afternoon stop (about 1:15 PM by run 29's report; the main session gives 1:40 PM; 12:35 PM entry) to 9:47 PM while the owner played.
- No squad runs or restarts from this session.

## Moved 2026-10-18 02:31 (ChatGPT, C63 newest-four log trim)

### 2026-10-17 1:00 PM Claude: missions at every terminal type (test plan section 11): 7 of 11 PASS with exact pay; group-pay fix staged

- **Runs (all mine, on the test galaxy, no restarts by me):**

  | Time | Galaxy run | Groups | Notes |
  |---|---|---|---|
  | 5:38 AM | run 24 | Cresh | the gate ran `cresh-missions.py` |
  | 6:02 to 6:05 AM | run 25 | all four | void: cut by the restart, halted by me |
  | 6:25 to 6:36 AM | run 25 | all four | |
  | 11:56 AM to 12:28 PM | run 29 | all four | |
  | 12:35 to 12:56 PM | run 29 | all four | alongside BotPop at 600 |

  The groups were Cresh, Besh (Dova, Varo), Dorn (Dorn, Rusk) and Forn. Reports: `Bot-reports/<Group>/20261017-*-missions.json`.
- **PASS** (mission removed from the datapad, and the bank rose by exactly reward // group size):

  | Terminal and mission | Reward → share paid (group size) |
  |---|---|
  | general/destroy | 774 → 258 (3) |
  | general/deliver | 62 → 20, 64 → 21 (3) |
  | artisan/crafting | 64 → 16 (4), twice |
  | entertainer/dancer | 133 → 44, 169 → 56 (3) |
  | entertainer/musician | 157 → 52, 205 → 68 (3) |
  | scout/hunting | 15 kills, 1038 → 207 (5) |
  | rebel/recon | 314 → 62, 385 → 77 (5) |

  The 7th mission was refused three times (Ilsa holds 6).
- **Not completed:** artisan/survey, scout/recon, imperial/recon and bounty. Reasons are in the plan; the scenario fixes are committed, not rerun. Mos Eisley has no newbie or statue terminal, and its faction terminals offer no deliver missions.
- **Bugs, with evidence in test plan section 11:**
  1. Group pay is judged from the mission's end point only. A grouped player who destroys a lair that spawned away from the first spot, or hunts away from where the mission was listed, gets nothing. **Fix staged** as asked by the main session: `Documentation-support/mission-group-pay.patch` and `.md`, against Core3-dev `25344120`; `git apply --check` is clean; unbuilt, not installed.
  2. A deliver pickup into a full inventory leaves the mission stuck in the datapad.
  3. A bank terminal's window opens at any range.
  4. Bot body: mission string-ids lose their key; the bank balance is forgotten; indoor `find` uses cell-local coordinates; no mission abort.
  5. 10 of 24 squad bots have full inventories from spare `/agentgear` kits.
- **Bots changed for this (test galaxy only):**
  - Cresh, Ilsa and Kor have the Marksman profession.
  - Rusk has Novice Entertainer.
  - Dask has Novice Bounty Hunter and Investigation I; Ressa has Novice Bounty Hunter.
  - Ilsa keeps 6 destroy missions, Cresh one stuck delivery, and Mirren, Dask and Dova unfinished recon or survey missions. All expire within 48 h; there's no abort.
- **Not done:** the full-datapad gate (C56) and live's 2-mission cap. `check_c9_offline.py` still fails on its Aurek fixture (stale, not mine).

### 2026-10-17 12:35 PM Claude: overnight simulated population on run 29; knowledge docs read

- **Owner, 17 Oct afternoon:** "im going to close client, id like you to read all the knowledge docs as efficiently as you can while we run the server bots on the simulated population mode while i sleep."
- **BotPop overnight:** started at **12:33 PM** on run 29 by the main session, which holds the lock and watches it. Console reply `{"cities":18,"max_online":600,"mode":"all","ok":true,"queued":400}`: 200 already online plus 400 queued, so the run's cap of 600 online at once (`BotPopMax=600`) is full. The 200 Ossus explorers did not queue (`{"from":"Knossa","ok":false,"queued":0}`) because the cap was full. WSL had 9 GB free; the memory watchdog despawns bots below 2 GB.
- **Reports:** the 7 AM job `morning29.sh` writes `Bot-reports/launch-sim/numbers-run29.md`, `findings-run29.md`/`.json`, `travel-run29.md`, `morning-run29.txt` and the planet data.
- **Possible restart tonight:** if the Ossus, leash and vehicle fixes all land, the main session may restart onto run 30 (no owner client open, standing OK) with `BotPopMax` 1500, relaunching 1,500 plus 200 Ossus explorers; the morning set then becomes run 30's. The main session logs that restart.
- **Stopped early, about 1:15 PM** (owner: "stop server, shutdown everything i would like to game a bit"). The main session stopped the test galaxy and BotPop and shut down WSL; the overnight population ran 12:33 to about 1:15 PM. Its message said about 1:40 PM, but run 29's report ends at 13:15 and was written before 1:18 PM. The 7 AM job is cancelled; run 29's set was written early (`report.sh run29`, all five files above, 11:05 AM to 1:15 PM). The overnight simulation restarts when the owner says the PC is free; the main session starts it and logs it. Nothing else runs on this PC meanwhile.
- **Squad groups:** the missions session's Besh, Cresh, Dorn and Forn run was left alone; no squad runs or restarts from this session.
- **Knowledge docs ("All of them", owner's card):** 67 mechanics reports in `Agent/local-research/`, 126 docs in `Documentation-support/`, `Agent/notes/`, `Agent/knowledge-sources.md` and Claude's memory. Skimmed (short answers and openings), no agents. Index and key facts: `knowledge-docs-index.md` in the side-session notes folder (`%APPDATA%\Claude\side-session-notes\local_c98a40c3-fc4d-4196-a226-b4493c0df564\`). Caveat: the local claim check found 28 of 941 cited claims contradicted and 102 not shown; four topics have no report yet (entertainer-xp-sources, jedi-unlock, ghostfire-quest, test-index).

### 2026-10-17 9:43 AM Claude: local 3D in place of fal: TRELLIS.2 through um comfy run, proved with one crate

- **The request** came from the main session, in the owner's words: "can you have it use a different free 3d tool? i imagine you know how to do that".
- **Done:** `tools/art/trellis2_image_to_3d_api.json`, made by `tools/art/make_trellis2_api.py` from ComfyUI's own TRELLIS.2 template (converted by the frontend's `graphToPrompt`, then TRELLIS.2 only, 45 of 63 nodes).
  - `um comfy run ... --set "Concept image.image=<file>"` downloads the `.glb` as is; `um`'s `outputs()` is generic. No wrapper and no plugin edit.
  - `tools/art/inspect_glb.py` checks the model in Blender 3.6.
- **The crate test** (no game client open, from 9:31 AM):
  - The template's remesh 768 ran **out of video memory**. Remesh 512 (now the default) worked: 166 s, peak 10,021 MiB of 12,227, at least 4.96 GB of Windows RAM free.
  - The GLB has 19,956 triangles and a 1024 PBR texture set. It decimates to 1,999 triangles in Blender, where the handles crumple a little.
  - ComfyUI was stopped afterwards (the card is back to about 650 MiB).
- **How-to:** `Documentation-support/local-art-models.md`, "How to: a 3D prop from an image, locally". `*.glb` is now gitignored.
- **Not done:** no `.msh` export or client test of a generated prop yet. Nothing was installed or downloaded.

### 2026-10-17 9:09 AM Claude: Vong look step 4 staged: client archive candidate + server patch, ready for the lock holder

- **The owner:** "The mix is close enough. Go on to step 4".
- **Client** (`Vong-look/tools/build_vong_client.py`, on the installed `b01e9f44`): candidate `work/vong-look/local_planets-vong-look.tre`, sha256 `185b3d7f...`, 332 entries. It adds 8 wearable templates, 16 `.sat`, 16 `.lmg`, 64 `.mgn`, 15 shaders and 12 textures, plus 8 CRC rows. The other 200 entries are byte-identical, and two runs give the same bytes.
  - 114 files are same-length swaps, with counts asserted and differing bytes counted.
  - 5 shaders get colour 0 rebound to `white.pal`: the chest's stock default was an olive brown.
  - Every reference resolves.
- **Server** `Vong-look/vong-look.patch` (20 files, Lua only): the 8 server templates, `vong_fanatic_warrior_outfit`, mobile `vong_fanatic_warrior_look` (human male body, scale 1.15, not attackable, no faction) and `OssusVongLookScreenPlay` at POI 7. `git apply --check` passes on Core3-dev `91cf87ed` (read-only), and `luac5.3 -p` passes on all 20.
- **Nothing was installed, and `/opt/swg` was not written.**
- **Owner's OK at 9:10 AM:** "Yes: OK to install the Vong look client archive and server patch on the test galaxy, per Vong-look/INSTALL.md. Pass it to the session holding the server lock." Forwarded verbatim to the main session (the lock holder) at 9:11 AM; delivered, not yet confirmed read.
- **Next:** the main session installs per `Vong-look/INSTALL.md` and restarts the test galaxy; then the owner's look in game (an open question, no prefilled answers); then patrols.
- **Times corrected 9:11 AM:** this entry and the three below first carried estimated times. The real ones, from the commits, are 8:38, 8:46, 8:58 and 9:09 AM.

### 2026-10-17 8:58 AM Claude: Vong look: chitin dropped; the owner picked a bone + marauder s02 mix, no helmet

- **The owner on the chitin preview:** "that looks nothing like vong armor, no helmet". The stock shape was the problem, not the texture.
- **Lineup of six stock sets** in the same finish (`Vong-look/lineup/lineup_sheet.png`). Acklay chitin turned out to be the same mesh as chitin.
- **The owner picked "Mix: bone + s02 collar"**, plus our own Vong body later (a TRELLIS.2 draft rigged to the human skeleton).
- **Bone and marauder shaders work the same way:** the colour alpha is the hue mask, so the textures carry alpha 0. The leggings' waist strip and the marauder chest take colour 0 from metal and cloth palettes, so step 4 rebinds those to `white.pal`.
- **Six mix textures** baked, converted and checked (`spec_mix.json`), and a lit preview went to the owner.
- **GPU:** only image generation uses the 5070; Blender runs on the CPU by design. Blender 3.6 does list the 5070 for CUDA and OptiX (untested).
- **Next:** the owner's view of the mix preview, then step 4 for the mix.

### 2026-10-17 8:46 AM Claude: Vong look test step 3: swatch 12 baked onto the chitin armour; seven DDS staged

- **The stock chitin shader** (`h_color2_envmask_specmap`) reads the colour texture's alpha as its hue mask, so our textures carry alpha 0 (no tint) in DXT5. The stock `_spec` and env maps stay referenced.
- **The bake:** `Vong-look/tools/bake_vonduu.py` (Blender, CPU) box-projects swatch 12 with ambient occlusion and bakes it into each male piece's own UVs at the stock sizes. All seven take 10 s. No stock pixel is used.
- **Orientation proved** against the meshes' raw UVs (96-99% overlap; 66-96% if flipped).
- **The DDS files:** `convert_vonduu.py` applies gamma 0.7 (the bake is very dark), sets alpha 0 and writes BC3 with full mips. Stock sizes and mip counts are checked, and all pass. Output: `Vong-look/staged/client/texture/` (gitignored).
- **A Blender preview was sent to the owner.** It reads as dark grey crab plating; the red crevices mostly wash out.
- **Nothing is in an archive or the client yet.** The GPU was not used for any of this.
- **Next:** the owner's view of the preview, then step 4 (the `armor_chitin` -> `armor_vonduu` clone chain and the CRC rows).

### 2026-10-17 8:38 AM Claude: Vong look test: swatch 12 picked; skin colour checked

- **Rounds 2 and 3** followed the owner's reference screenshot, used by eye only and not fed to the model. The owner picked **swatch 12**: rough dark crab shell with a red tint in the crevices.
- **Round 2 drew shells on a background,** so it is superseded. Round 3's prompts ("completely covered edge to edge, no background") fill the frame and tile.
- **A RAM failure in ComfyUI:** a `MemoryError` while it streamed the 8 GB text encoder, with about 9 GB free in Windows. A retry worked. `--disable-pinned-memory` then ran clean, at 2.1-3.5 s an image.
- **Skin colour** (Wookieepedia Legends and other sources): grey is most common, then yellow. Nei Rin is white with purple tattoos; Zenoc Quah light grey with black tattoos. No source gives green.
- **For the first look:** the warriors keep the chitin helmet on. A bare head with pale skin, eye sacs and tattoos is a later texture job.
- **Details:** `Documentation-support/vong-look-test.md`.
- **Next:** step 3, the Blender bake of swatch 12 onto the chitin armour's UVs.

### 2026-10-17 8:30 AM Claude: first ComfyUI run on this PC; Vong look test step 1 done

- **Run with the owner out of the game** ("im out, run it"), from 8:23 to 8:26 AM. ComfyUI 0.41.0 started on PyTorch 2.14.0+cu130 and saw the RTX 5070, so Blackwell works. It ran `--offline`, local only.
- **FLUX.2 [klein] 4B fp8, 1024 px:** 35.0 s cold (loading included), then 3.7-4.6 s an image. Card peak 11,563 of 12,227 MiB; free Windows RAM stayed at or above 8.56 GB.
- **Idle ComfyUI keeps 8.6 GB on the card.** I stopped it at 8:27 AM (back to 927 MiB). Always stop it before the owner plays.
- **Four Vong images** (three armour textures, one concept sheet) are in `Vong-look/gen/` (PNGs gitignored; prompts and seeds in `comfy_manifest.jsonl`). The tiling prompts did not tile on their own; `um sprite seamless` fixed them. Details: `Documentation-support/vong-look-test.md`, `local-art-models.md`.
- **Untested:** TRELLIS.2 (its template still has to be put into API form), and everything in the game.
- **Next:** the owner picks a swatch, then step 3 (the bake in Blender) and step 4 (the clone).

### 2026-10-17 7:50 AM Claude: local AI models for art and planet work (research only)

- **The owner asked** whether a local model on this PC can do some of the art or planet work. The answer is in `Documentation-support/local-art-models.md`. Nothing was downloaded, installed or run.
- **This PC:** RTX 5070 with 12 GB (9.8 GB free with two clients open), 32 GB RAM (6.4 GB free in Windows; WSL 10.8 GB), and 90 GB free on C:. The driver supports CUDA 13.4.
- **Ranked picks:**
  1. ComfyUI portable (cu130) + FLUX.2 [klein] 4B fp8 (Apache 2.0, about 8.4 GB VRAM by ComfyUI's figure), for kajidic seals and banners, the Hutt sash decal, Nal Hutta loading screens, concept sheets and texture sources. 14.5 GB of downloads.
  2. `um sprite seamless` for tiling (already installed); SDXL only if seams show.
  3. TRELLIS.2 native in ComfyUI (MIT, int8, 8.95 GB) for static prop drafts. Experimental: Microsoft asks for 24 GB.
  4. Hunyuan3D 2.0 shape only, as a fallback. Its licence excludes the EU, the UK and South Korea.
- **No model helps** with `.trn` terrain (scripted, and the maps and globes come from it), `.mgn` weighting to `hutt.skt`, or `.ans` animation.
- **Also answers** the 13 Oct asset-workflow review; the board row is updated and the note links here.
- **Verified:** hardware, licence tags, file sizes and gating, and client texture sizes (loading screens 512 DXT1, globes 256 DXT1 with 9 mips, maps 1024 DXT1).
- **Untested:** every speed and VRAM figure on this card.
- **Owner's pick (about 7:55 AM): "2D art + 3D test"** (picks 1 and 3).
  - All nine files are downloaded and SHA-256 checked (23.42 GB). ComfyUI 0.41.0 portable is unpacked at `C:\Users\Pengw\Tools\ComfyUI_windows_portable` with the models in place: 25.83 GB, and 63.5 GB is still free on C:.
  - No custom nodes and no system install. The install record is at the end of the note.
- **Not started yet:** two SWGEmu clients were open at 8:00 AM, so ComfyUI has never been run. It is untested on this card.
- **Next:** the first test (one klein image, one TRELLIS.2 run at 512) when the owner is not playing. Start it with `advanced\run_nvidia_gpu_disable_api_nodes.bat`, which runs with `--offline`, so no paid nodes.

### 2026-10-17 6:40 AM Claude: creation sweep: every species and gender created, read back and deleted (test plan section 2)

- **Commits:** `b244f27` (the scenario `tools/bots/scenarios/creation-sweep.py` with its README section and offline tests), then this commit (the fixes the run turned up, 33 offline tests, results in the test plan).
- **Run 25, 6:17 AM** (dev `7be8837a`, archive `f0191ab5`), after the main session's go. No restart and no squad or botpop commands. Report `Bot-reports/Creation/20261017-061803-creation-sweep.json`, 55 of 57 checks.
  - **24 of 24 created and logged in**, 8 at a time: 0.3 to 1.3 s per creation, 1.3 s per login.
  - For every one, the object CRC, the shown name and all nine starting attributes match (profession_mods + racial_mods, current equal to maximum).
  - Name filter 21 of 21: 8 refusals with the right code, and 13 acceptances (the old substring traps, canon names stock refused, a Hutt kajidic surname).
- **Hutt C54 F1 to F3 verified in game:** the male Medic and female Entertainer each have their profession row plus S7's 100/150/300/0/0/50/0/0/300. The limits, `desc_hutt` and the skill labels are as approved, and creation applies the Hutt's own name rules.
- **Cleanup:** 24 of 24 moved to `deleted_characters` at 6:23 AM with the login server's statements. The run's own cleanup at 6:18 AM found no rows and touched nothing: new characters wait in `characters_dirty` until the zone's next save (about every 10 minutes). The scenario now waits for that save; so far that wait has run live only through `creation-sweep.py cleanup`.
- **Bugs, proposed and not fixed** (each needs our archive changed and installed on client and server):
  - **B1, stock creation text:** the Sullustan description shows the Zabrak's bonuses and the Ithorian description the Mon Calamari's (`patch_12_00`, copied unchanged into our archive).
  - **B2, stock data gap:** the Ithorian male Brawler's starting jacket `ith_jacket_s16` has no template on the server or in the client. Each such creation logs 3 ERROR lines, and the character starts without the jacket. The sweep now checks every starting item for a server template; this is the only one missing.
- **Also changed after the run:** account choice, the name check and the template check now read `characters_dirty`. Console errors that follow our character's login on the same server thread count as ours (that is how B2 slipped past). The "name in use" case now borrows a bot's name, not a player's.
- **Next:** the owner decides on B1 and B2. The sweep can run again at any time on the other load-fleet accounts (53 are free).

### 2026-10-17 6:00 AM Claude: "the server keeps putting us back" fixed; test plan section 4 passes

- **Cause** (`Documentation-support/movement-pushback.md`): the server bounces a walker when its packets arrive bunched after a stall (the speed check divides client distance by server time). On run 24 one stall while BotPop's 300 bots logged in bounced five bots in the same second, 6.2 to 9.3 m/s measured against 5.68 allowed. The body then gave up after three bounces per move however long the walk, and counted the server's resync echo as a bounce too. Crouched or sitting bots were bounced every step.
- **Fix, dev `7c2f2605`** (agent body): a bounce ends the leg and the walk re-plans from where the server put the bot; it gives up only on three bounces within 10 m (or eight per move); the walk speed follows the server's limit for the bot's posture; `move` stands up first. **Dev `b034d15f`** (server): every bounce writes a `[Movement]` line with its check, and a failed speed check writes the measured speed. This logs real players too.
- **Results, run 24** (5:24 AM restart): gate **PASS** 47 of 56 at 5:38 AM, no regressions. The three 15 Oct failures pass: Besh hide patrol, Cresh at the mission terminal and the mission area, and Tovan on the plateau (`esk-routes.py` 5 of 5 at 5:33 and 5:50 AM). Dova's 268 m walk into the cloning cell, which failed at 3:26 AM, arrives with 0 corrections, and a kneeling bot stands up and walks. Across 8 reports and 78 moves: 0 "putting us back" errors and 5 bounces, all absorbed. The test plan's section 4 and gap 2 are updated.
- **Not done / open:** the server's speed check still misfires during stalls, so a real player can rubber-band. Changing it touches the stock anti-cheat (owner's call, then a review). The `[Movement]` lines give the numbers. Not tested: `/sit` before a walk, and a rooted or overloaded bot. The 7 start errors on run 24 are "Failed to rename log/who.json.next" (live map file, first 83 s).
- **Galaxy:** free for the species, missions and real-client sessions' checks since 5:55 AM. This session keeps the lock for the test pass, so restarts and BotPop changes go through it. BotPop is at 300 in "all" mode.

### 2026-10-17 5:56 AM Claude: real-client session for the interaction loss: no stall at 300 bots

- **Session:** the owner played [name removed] on run 24 from 5:32:44 to 5:48:08 AM (about 15 minutes; part of the new checklist, `Documentation-support/functional-test-plan.md` section 5). BotPop was at 300, and the gate and a squad round were running. Monitors (read-only): Windows CPU and "responding" every 2 s, WSL load and core3 CPU, the console with wall-clock times, per-second zone packets for the owner's port, `core3.log`, and the input listener (owner's OK).
- **Result:** no sign of the interaction loss. The client responded in 602 of 602 samples; total CPU median 21%, max 70%; WSL load at most 2. Traffic both ways in 903 of 925 seconds, and never client-only. Clean logout (`hasError = false`). No Insert (stuck) presses, no `[Movement]` bounce for [name removed], no new crash dump. This fits the 16 Oct starvation explanation without proving it. **The owner's own account is still to come**, and goes into section 5 when they answer.
- **Owner's tell to Esk** (BotPop): the lanes are right, but the bots don't look like a real population, and don't progress, form guilds, build cities or work together. Passed to the BotPop social-play session at their request.
- **Follow-ups, proposed:** a repeat at 1,000 to 1,700 bots with the same monitors; the rest of the 40-minute list. Unrelated: `Play SWG.cmd` (live) keeps the old WSL address `172.23.208.109:44453` in `swgemu_login.cfg`, but WSL is now mirrored (`192.168.1.210`), so the live launcher probably can't connect until it writes the current address the way the test launcher does. No galaxy, `/opt/swg` or BotPop changes by this session.

### 2026-10-17 5:24 AM Claude: test galaxy restart (run 24) for the movement fix

- **Restart 5:24 AM** (no squad run, no SWG client running, login config on the live port): run 24, resumed copy, dev build with the movement fix (committed after the rerun as `b034d15f` and `7c2f2605`; `Documentation-support/movement-pushback.md`), same configs as run 23. All 24 squad bots logged in afresh on the new body; BotPop back to 300 in "all" mode. Results in the 6:00 AM entry.

### 2026-10-17 4:25 AM Claude: local model on the friend's PC: installer, fallback to this PC, shared workflow

- **Commits:** `cb6c487` (installer, server list with fallback, workflow), `f2b63e1` (names delta sweep in the workflow), `54391cd` (the installer pulls every model we use). Another session set up the friend's PC itself at about 4:20 AM with the older manual steps (`c97a500`): Ollama 0.40.5 and qwen3:8b only, plus a firewall rule for the whole subnet.
- **Installer:** `tools/agents/local/friend-pc/install-ollama-lan.ps1` (how-to in `README.md` there, and a private page for the owner to open at the friend's PC). It admits only Miniverse (Private profile, ollama.exe only), offers to switch off the older subnet rule, pulls qwen3.6:35b-a3b, qwen3.5:9b, gemma4:12b, qwen3:8b and gpt-oss:20b, builds gpt-oss-20b-64k, and self-tests each one. `-CheckOnly` and `-Remove` are there too. **It has not been run at the friend's PC yet.**
- **Fallback:** `ollama-url.txt` (gitignored) now lists the friend's PC (qwen3:8b, 32K) and then this PC (qwen3:8b, 16K, with the memory guard). The 32768 in `ollama-ctx.txt` is only a default now, since each line sets its own size. The model is unloaded every 5 requests on the friend's PC too.
- **Workflow:** `Agent/local-model.md`, linked from AGENTS.md: which jobs go there, how both agents queue them (topic fields `model`, `local_only`, `review_by`), and how reports are reviewed.
- **Verified:**
  - 76 offline tests in WSL and 10 chunk-job tests.
  - A real 2-chunk job on the friend's PC: 44 s including the model load. As a draft, qwen3:8b caught a doubled word, missed a misspelling, and flagged one correct line.
  - Over the real network, a server that doesn't answer is skipped after 3.0 s.
  - `idle_research.py status` counts the friend's quiet minutes. The timer starts the first of the 5 open topics there after 10.
- **Not verified:**
  - The installer run (firewall tightening, the downloads, whether Ollama 0.40.5 can pull the qwen3.6, qwen3.5 and gemma4 tags, speed and GPU share).
  - A real fallback with the friend's PC off.
  - A research topic run there.
  - The friend's RAM under long runs. It can't be read from here; the unloads are the only guard.
- **Next (owner):** at the friend's PC, run the installer from the page, and answer yes to switching off "Ollama LAN 11434". After its self-test, Claude switches the friend's line to qwen3.6:35b-a3b at 65536.
- **Owner's call:** the names delta sweep. The checklist below sends it to the friend's PC. The workflow keeps it on this PC, because real names don't leave this PC and the friend agreed to source, bot notes and game text. Nothing is queued until a `names-delta` job exists in `local_jobs.py`.

### 2026-10-17 4:04 AM Claude: going-public check, assets clear; licence, credits and the checklist

- **Assets (whole history, which is what the export publishes):** no image, model, texture, sound, archive or SWG client file was ever committed.
  - The only asset files are ours: the Ossus `.tga` bitmaps and `.ws` snapshots from `tools/ossus_terrain.py`, and `SpeciesColorLock.fx`.
  - Kenney (CC0): only receipts and notices are in git; the Quaternius art (CC0) isn't in git. TortoiseBots: with permission, credited. EiF: reference indexes only.
- **Owner's decisions (17 Oct):**
  - **AGPL-3.0 for the whole repo** (`LICENSE`), with credits in `NOTICE.md` (`01fb0de`).
  - The **SWG×SW5E books and the material extracted from them stay out** of the public copy (export drop list).
  - **MTG: credited and published now**, removed if an author objects.
  - Names: keep credits, whole source links, brother mentions with no name, and the characters Benny and Tulde Dedra. "Bill" (a first name in a quoted comment) is reworded in the export. Decisions are in `work/names-sweep/decisions-2026-10-17.json` (local).
- **Test export build** (local, no push): 347 commits, no dropped paths, no handles or e-mail, messages clean, the SW5E files in no version, LICENSE and NOTICE at the top.
- **Before going public (checklist):**
  1. **Names delta sweep:** the 324 files changed since 15 Oct 11:40 AM. It waits for the local model on the friend's PC (owner: "save it for the local model we are setting up"); Claude or GPT reviews its list.
  2. The owner makes a **fresh public repo** and runs `github_export.py push <new url>`. Then check it on GitHub.
  3. **Purge the old repo** (owner, 17 Oct: "dont forget we need to purge the old github"): after the new one checks out, the owner deletes the old private repo (Settings, Danger Zone, Delete this repository). It may still hold early commits by hash. Check it has no forks first. Claude doesn't delete repositories.
  4. Then the TortoiseBots fork (`Documentation-support/tortoisebots-fork-plan.md`).

### 2026-10-17 2:30 AM Claude: PL-05 Hoth leftovers staged (scheduled run; nothing installed)

Built only what the owner answered (15 Oct Q4; 14 Oct question 9). Folder `Hoth-leftovers/`: `hoth-leftovers.patch` (13 Lua files against Core3-dev `07d9f61e`; `git apply --check` and `luac -p` pass, read-only), `build_hoth_leftovers.py` (chains on the installed `df1d538e`; candidate `work/hoth-leftovers/local_planets-hoth-leftovers.tre`, sha256 `108d4234...`, 178 entries byte-identical, 8 changed, 13 new) and `LEFTOVERS-INSTALL.md` (install order: archive on both sides first, then the patch). Adds: the mynock ice cave with Fable's flatten layer; Hoarfang in a fixed spot with a 30-minute respawn, blue through a `rancor_ice` chain on the Chiss skin palette; badge 141 and a rare-decor roll at the end of Vell's chain; artisan and entertainer terminals plus both recruiters at the starport (recruiters off the camps); deliveries to three camps; map names for the two dens. Density, area and camp names and the camp junk dealer were already in dev. Untested; three owner questions at the top. Tauntaun riding stays its own batch.

### 2026-10-16 16:40 Claude: Hutt crash fixed, C55 answered, release plan, C46 reviewed

- Hutt creation crash fixed and installed (above). C55 F1/F2 fixed in dev `c5d713b8`; C58 re-review queued for GPT. `live-release-1.md` revised to GPT's verdicts (small first release from live; T1/T2/S1-S5 and BotPop stay on test; missions held). C46 (`ccf9519`): a failed minute PATCH retries, previews overwrite, success spacing fixed, no version banner; 56 tests pass. Opus took Fable's content job (`7a99802`): 16 owner questions to bring as cards.

### 2026-10-16 16:28 Claude: Fable's content-design job: ranked backlog and faction plan

- `Fable-backlog/README.md` + `backlog.json`: 73 cut and custom items by theme (71 ranked, Hutt and world boss in flight), client archives surveyed with swgfmt. Top 5: Ossus O7 build, Hoth leftovers, Nal Hutta first look, faction foundation, Ossus people; next to design: faction data, Ossus people, Nautolan/Togruta/Chiss names and profiles. `Fable-factions/README.md`: the 138-139 ABY sides checked on Wookieepedia (Legends), Core3 faction code read-only (dev `a8ece12b`), options A/B/C, recommends A (two GCW sides as Triumvirate and Krayt's holdouts, seven NPC standing sides), 13 owner questions with defaults. Design only; nothing built, run or written under /opt/swg. Board commit includes ChatGPT's finished C55 row and entry (report `fbee3aa`). Oldest Log entry archived.

### 2026-10-16 16:08 ChatGPT: C55 release review complete

- Reviewed by ChatGPT: seven requested non-bot commits; report/evidence `fbee3aa`, `Documentation-support/review-C55/C55-review.md`. Open inherited helper lock P1 and global spawn-gate P2; original Hutt defects already corrected by excluded C54 source. XP, delivery-on-C45 and isolated city guard fit in source; spawn experiments/bot workaround stay on test. 74 Lua checks pass; gameplay/mission/Hutt gates remain untested here. No server writes or galaxy commands. Next: Claude fixes/splits, acceptance, exact release cross-review and owner OK. Oldest Log entry archived.

### 2026-10-16 09:12 ChatGPT: C54 Hutt review and source complete

- Reviewed by ChatGPT: 26b54813/S7, 1 P1 + 5 P2 with failing cases; `82e52303` species/refusals, `deb3319e` Artisan floater, `8ebace32` Hutt names on gpt/c54-hutt-floater; report/client staging `a07d346`. 17 changed/new Lua pass; all 47,406 checked (one unchanged legacy migration error); race-header/LAT/link/archive checks pass. No configured build; full server/gameplay untested. Next: Claude review/cherry-pick, fix client profile/text/builder gates, owner floater visit. Run 10/dev/galaxy untouched; oldest log entry archived.

## Moved 2026-10-16 17:00 (Claude, Hutt crash)

### 2026-10-16 09:01 ChatGPT: C53 Ossus o7 staging complete

- `3f64720`: accepted crater/pod/field and six POI layouts retained; POI 17 centre (2200, -4725), minimum tested 600 x 300 m relief 12.56 m. `run_all.py` ALL CHECKS PASS (119 s), 90 read-only server references pass; README regenerated/open decisions closed. Client checks and two existing POI 13 boulder tilt warnings remain untested; next: Claude review and owner client visit. No packing, /opt/swg writes or galaxy commands. Oldest Log entry archived.

## Moved 2026-10-16 16:28 (Claude, content backlog)

### 2026-10-16 08:56 ChatGPT: C52 city answers and M1 plan complete

- `dc469f8`: removed excluded citations and dependent claims, recorded all 13 owner answers, wrote `Documentation-support/bot-cities-plan.md` with Claude's build order and maintenance/jitter/slot probes. CRLF, answer/source scans and diff checks pass; no code or server/bot actions. Implementation and in-game acceptance untested; next: Claude reviews and builds M1. Oldest Log entry archived.

## Moved 2026-10-16 16:08 (C55)

### 2026-10-16 08:49 ChatGPT: C51 approved checkout housekeeping complete

- `a5b7604`: targeted ignores and 45 cached-only removals; all 15 present files retain their hashes, 30 rotated summaries stay in ZIP/history without restore. Queues remain tracked; remaining author commits listed in `Agent/checkout-churn-1016.md`; unfinished Fable work untouched. 23 ignore/exception checks pass. No files deleted or server/bot actions; next: each author reviews and commits their listed finished work. Oldest Log entry archived.

## Moved 2026-10-16 08:49 (C51)

### 2026-10-16 03:47 ChatGPT: board and queue checked

- Status check only; no implementation or bot/server actions. Queue: 33 done, 8 hold, 2 failed, 2 open. Ready order C46 staging-only Discord/public-map tooling, then C48 run-8 analysis/morning sheet; neither output exists yet. C47 completed by Claude helper 3639bb2 despite queue hold. C45 dev fixes db5952f5 + 74fa3e8c are reported integrated; crafting/full-datapad gameplay gates remain. C33/C41 failed queue entries need report reconciliation before retry. Source/code commits unchanged; next work awaits owner direction.

## Moved 2026-10-16 02:15

### 2026-10-15 22:35 Fable: Hutt S7 designed (concept, animation map, gear, new animations, Nal Hutta), photo studio, Ossus O6 pass

- `Fable-species/s7-hutt/README.md` + `animation-map.json`: the Hutt shares the human state hierarchy (`all_b.ash`) but `hutt.lat` (206 entries) lacks 714 of `all_m.lat`'s 904 names; the JSON maps 631 of them to existing Hutt `.ans` files (sit/kneel = idle + fidget transitions, sneak/prone = the unused `hutt_loc_crawl`, dance = an AGAT gesture loop like the Hutt's own idle, riding = idle on the A1 Deluxe Floater as the launch vehicle, 249 emotes by keyword), skips 84 (Force, Jedi, masks); all 52 referenced files exist. Species facts: 900-point profile 100/150/300/0/0/50/0/0/300, refusal texts, our own name tables, id 0xEA. Level 2 gear list (10 items, slots and rigging notes for `hutt.skt`, 47 bones), Level 3 animation list and what `export_ans.py` lacks (unregistered stub writing zeros). Nal Hutta: `hutta.trn` is an edited Rori (water 75 m), one Tatooine-built town Bilbousa (281 nodes), fits the era, first-look steps listed.
- `Fable-studio/README.md`: the four SOE test terrains have no shader families; pick zone `simple` with our own flat terrain, fixed light via colour ramps, no-spawn region, two backdrop walls, six-shot set, `um win shot` routine.
- `Fable-ossus/o6/README.md`: 5 craters + scorch fans + glass pan on the ruins (layer specs), 5 settlement flatten fields outside the no-build circles, 18 lore POIs with locations and stock pieces. Creature levels untouched.
- Nothing built or seen in a client; no /opt/swg writes. Next: Claude builds the modified `hutt.lat` and the S7 tables/patch; GPT reviews and takes the `.ans` format research; owner answers the five S7 questions.

## Moved 2026-10-15 23:46 C45

### 2026-10-15 17:40 ChatGPT: C43 BF2 2005 research/design complete

- Report `86f9200`: public official-tool documentation/manual evidence, read-only Core3-dev/bot mapping, three-post Hoth conquest design and five NPC priorities. Local links/CRLF checked; exact Follow signature and retail constants left open. No BF2 files, downloads, server/dev/bot changes or gameplay. Implementation and all in-game acceptance untested; next: Claude reviews the pilot and scopes controller/activity/combat work. Older Log entries preserved in the archive; newest four retained.

## Moved 2026-10-15 C42

#### 2026-10-15 11:40 Claude (side session): names sweep second half done; local-model background jobs

- **Names sweep, second half (owner asked for Haiku and the local model; GPT's C36 put on hold, `f0584c6`):** all 942 remaining chunks read. Local model qwen3:8b on every chunk (937, plus 2 read by Claude), two Haiku agents on the 162 prose chunks, and a pattern pass for URL usernames and e-mails. **152 new candidates** beyond the first half's list, 16 found by two methods. They are in `work/names-sweep/new-names.json` (git-ignored, local only) for the owner's decisions before going public.
- **The local model is a drafter, not a checker:** on the same prose chunks it found 41% of what Haiku found. Use it for drafts and first passes that something stronger checks, not for privacy, reviews or research a test relies on.
- **Memory cause found:** Ollama keeps each request's KV state in a host-RAM prompt cache (about 0.5 GB per 4K-token request with qwen3:8b). It grew commit by ~15 GB in 25 requests, very likely what crashed the PC at 07:31. New `tools/agents/local/memguard.py`: the local-model scripts unload the model every 5 requests (empties the cache), pause under 6 GB of commit headroom, and idle research won't start under 8 GB. On this PC, `ollama-model.txt` = qwen3:8b and `ollama-ctx.txt` = 16384 (per-PC, git-ignored).
- **Chunk jobs for idle research:** queue topics of `"kind": "map"` run `local_jobs.py` (input and report) and `local_map.py` (one request per chunk, resumable, yields to the owner's client and to low memory). Queued: `bot-gap-list` (192 de-duplicated BLOCKED/NO_EFFECT/FAIL notes sorted into gaps) and `proofread-player-text` (488 strings: our archive strings that differ from stock and MTG, plus messages added on dev since sandbox). Reports land in `Agent/local-research/<id>/report.md` as drafts. **The STOP file is removed**, so idle research runs again when the owner's client is closed; create `Agent/local-research/STOP` to pause it.
- Tests: `test_local_map.py` 10/10 (Windows and WSL); `test_ollama_url.py` 61/61 (one expectation changed: local_agent now unloads the model when it finishes). A 2-chunk live run from WSL worked (lowest headroom 8.6 GB). The full jobs run when the PC is idle; untested end to end through the timer.

## Moved 2026-10-15 07:21 PDT

### Older log entries (newest first)

#### 2026-10-15 07:01 Claude: private GitHub copy force-pushed (owner's OK)

- Owner, 07:00: "Yes, run the private --force push now." Before it: `prepush_scan.py` (only the 21 known false positives), the history-wide secret check (clean), `github_export.py` check ok (127 commits).
- `github_export.py push … --force`: GitHub main `3610812` → `d9e5b06`, verified with `git ls-remote`; still PRIVATE, one branch, no tags. Gone from GitHub's history: the four early files (SWG-Source records and scripts, the stock client UI file), the owner's character names and a third-party developer's handle (3c3c2c8).
- Still before going public: the local-model names sweep (running, about 2.5 h) and the owner's four decisions (brother mentions, non-credit Sagiroth mentions, the "clones were in work/research" wording, usernames in download-source URLs). GitHub may keep the old commits reachable by hash for a while, so publish as a fresh public repository, or have GitHub purge them, rather than flipping this one public.

#### 2026-10-15 03:55 Claude: the invisible BARC was MTG shadowing; MTG merges installed; helpers on the class check, the MTG audit and examine texts

- **BARC root cause.** The server spawned it (a bot's `locate` found it next to the owner), but the client had nothing to draw. The client and the server both load MTG's archives below stock, so stock's copies of shared files win. The four mount tables (`datatables/mount/*`) and `string/en/monster_name.stf` in stock know nothing of the BARC, so its rows in MTG's copies never reached the client. That is also why the datapad said `monster_name:[barc_speeder]`.
  - Earlier leads (the empty template, "the server lacks the MTG archives") were wrong. The live config already lists MTG's archives; my 03:23 check was a shell quoting slip.
- **Fix:** `MTG-merges/` (a8c5cc2) keeps every stock row and appends MTG's rows with new keys (48/44/54/58 rows, 183 strings). Archive `local_planets.tre` 1315dbb4 is on the server and the client (6556537d backed up). Test galaxy resumed 03:40; squad.py setup 13. The owner's BARC test is next.
- **Helpers (owner OK'd):**
  - Opus: auditing every other stock-shadowed MTG file (names, deeds, vehicles, items) into `MTG-merges/shadow-audit.md`.
  - Sonnet: reviewing and finishing C33's class check and running P0/P1 on Aurek.
  - Local model: examine texts for the Ossus creatures and NPCs, reviewed and rewritten (c951d80; not wired, they need their own shared templates).
- **Staged:** the five Ossus NPC names (`Local-model-ossus-npcs/stage_npc_names.py`, df5543d). They go in at the next archive build.
- **Queued for GPT:** C35, Ossus NPC server wiring, after C34 and C24b.

#### 2026-10-15 03:03 Claude: after the outage (network loss about 02:40, PC shut down from the Start menu 02:52, back 02:55)

- **Interrupted:**
  - ChatGPT's C24b run lost its network at 02:42 and was killed at 02:52 (no answer); it is requeued after C33/C34.
  - Claude's session and its two baseline helpers (systems audit, pre-CU reference) stopped too; they are resumed.
  - The test galaxy went down with WSL; its copy is kept (new resume mode).
- **Not broken:** dev (`80b66e65`) and gpt/work are clean, h has no half-written files, and the archive and the client files are unchanged.
- **Queue:** C33 (class-check scenario), then C34 (kits), then C24b. The class-check groundwork is in `Claude-class-check/` (h dc568f2).
- The owner is on phone tethering for now: keep downloads off.

#### 2026-10-15 01:40 Claude: C32 passes live; BARC speeder fixed in dev; first resumed restart

- **C32 live check** (`Bot-reports/Cresh/20261015-013434-claude-probe-profession.json`, 4/4):
  - `/agentgear profession combat_pistol` gave Kor 23 boxes with their marksman prerequisites, none failed;
  - `list` shows them;
  - an unknown name is refused;
  - `clear` surrendered all 23 and kept species and language boxes.
  - Kor was given the marksman tree afterwards to replace the novice box he started with.
- **BARC speeder fixed** (the owner's "nothing spawned", 00:46-00:53), dev `740b2426`.
  - Cause: `custom_content/mobile/vehicle/barc_speeder.lua` had an empty body, with no `templateType = VEHICLE`.
  - Its deed (and the Tantive IV advanced landspeeder deed, which uses the same template) made an object the call code could not spawn.
  - Once a "vehicle" counts as out, `VehicleControlDeviceImplementation::generateObject` returns silently for every other vehicle, so the Imperial BARC failed too.
  - It is the only empty one of the 58 custom vehicle templates. Owner to retest.
- **Test galaxy restarted 01:37 by resume** (new `test_galaxy.py`; no client, no round).
  - Characters kept: `squad.py setup` only logged the bots back in.
  - Config overrides replaced, not duplicated.

#### 2026-10-15 01:36 ChatGPT: C30 Ossus fauna source ready

- Committed `6f25b704` in GPT worktree after C32/dev merge: six unchanged reviewed creatures, six dynamic lairs, three habitat groups/five regions; base levels retained, lake wetlands/forest/open ground wired. All 20 files pass individual luac5.3 and the worktree-adapted shared checker; stubbed include/reference/habitat checks pass. Claude asked to review/cherry-pick/build/test and add six client name strings. **Unbuilt and game-untested; no archive edits, build, restart or live changes.** GPT worktree clean; next Claude integration.

#### 2026-10-15 01:32 Claude: WSL mirrored networking; test galaxy kept between stops now; C32 in dev; test galaxy up with the renamed gems; GPT on C30

- **WSL settings (owner's go):** new `%UserProfile%/.wslconfig`. It has:
  - `networkingMode=mirrored`, to try against the 9% packet resends on 15 Oct;
  - `hostAddressLoopback=true`, so Windows reaches WSL on the PC's LAN address and not only on 127.0.0.1 (tested over TCP and UDP both ways);
  - `vmIdleTimeout=-1` and `instanceIdleTimeout=-1`, so WSL no longer stops itself when idle (it did at 19:43 on 14 Oct and again around 01:00).
  - Undo: delete the file and run `wsl --shutdown`.
  - **Live galaxy:** its stored address (`swgemu.galaxy`) is still the old NAT address, so live login needs one update before the next live start. That needs the owner's OK.
- **Test galaxy no longer wiped** (owner: "do we need it wiped everytime in the first place?"). In `tools/test_galaxy.py`:
  - `stop` keeps the copy, and `start` resumes it with fresh dev scripts, config overrides and address.
  - `start --fresh` restores the newest backup; `stop --wipe` deletes the copy. AGENTS.md is updated.
- **C32** (ChatGPT, the agent profession kits): reviewed and cherry-picked into dev as `6f3ce06f`, built 01:26 with no errors.
- **Test galaxy started 01:30** (owner's go; no client running, no round).
  - Fresh copy of galaxy-20261013T172001Z, dev build, Hoth and Ossus.
  - The renamed-gems archive 39a89e6c is installed on server and client; fbf62971 is backed up in `/opt/swg/tre/old/` and `Local-content/`.
  - `squad.py setup` is running.
- **Owner's Chiss test:** Tulde Dedra (made 00:31) was a Chiss and played normally (teleports, travel to Ossus, deeds). Fable's S6 can go ahead at its reset.
- **ChatGPT on C30** (Ossus creatures) since 01:32. The local model's six creature files are in `Local-model-ossus-fauna/` (h 2e438bf).

#### 2026-10-15 01:18 ChatGPT: C32 profession kits ready for Claude

- Merged dev into gpt/work (`220700d0`), then committed gated profession grant/clear/list (`4a340565`); SkillManager grants prerequisites first, bypasses XP/points, notifies the client, and reports named results. Clear matches the character builder (retains innate/Force progression). Bot wrappers + 7 offline tests pass; local Brawler/Carbine graph checks pass. Claude asked in `Agent/to-claude.md` to review/cherry-pick/build/test after the owner lifts the test-galaxy hold. **C++ unbuilt and game-untested; no cmake/make, bot driving, deploy or restart.**

#### 2026-10-15 00:01 Claude: test galaxy back up after WSL idled out; owner's era decisions (138–139 ABY, Krayt raid, beskar, coral); Ossus gems renamed (staged); Ossus resource map; local model running

- **Test galaxy, part 1: the outage and restart.**
  - Down from about 19:43: Windows stopped the idle WSL VM, and MariaDB and core3 went with it.
  - Restarted at 23:42 at the owner's request (no client running, no squad round). Ready 23:43:53 with fbf62971 (C29), resource backfill hoth +33, ossus +23. Bots left offline on purpose.
  - A permanent fix for the idle stop is a `.wslconfig` setting: the owner's call.
- **Test galaxy, part 2: the session watch.**
  - Two monitors watch the owner's session.
  - `tools/agents/watch_test_session.py` (new): player, staff-command and error lines, IPs masked. It also keeps a WSL session open, so the VM stays up.
  - A client process and crash-file watch.
  - The owner is on as [name removed] from 23:53 (character builder: FRS dark side; /invulnerable).
  - The login ERROR "skill points on load mismatch" is Core3 correcting the stored count (`CreatureObjectImplementation.cpp:2471`); harmless.
- **Owner decisions, part 1: setting and raid.**
  - Setting: **around 138–139 ABY** (AGENTS.md setting line updated).
  - Wookieepedia on Krayt: he died in 137 at Had Abbadon and came back, then died for good in 138 on Coruscant.
  - After 138, Nihl hid the fleet and the One Sith went underground. Darth Wredd belongs here too: the 138 ABY Carreras Incident; he died in 139 on Mala.
  - **Krayt raid:** the main boss is one of Krayt's successors (e.g. Darth Nihl). The **secret boss** is a Krayt echo or Sith spirit, unlocked by a loot item that drops in the same raid.
  - Lore hook: Krayt's Vong implants grew a bony exoskeleton that served as armour, and his empty armour was found in the Korriban Stasis Room.
- **Owner decisions, part 2: beskar and coral.**
  - **Beskar: option A.** Its own class, used only by a few new Mandalorian armour and weapon schematics; not under iron, which has 693 recipes.
  - **Yorik coral: option A.** Its own class, for Vong decor, weapons, armour and ships; maybe pets (voxyn).
  - Proposed placement for both: directly under the tree's root, so no stock recipe accepts them (`Fable-resources3/lore/ossus-resource-map.md` §6).
- **Ossus gems renamed (staged, `Fable-resources3/names/`; Fable was out of usage, so Claude did it).**
  - The five Wookieepedia Adegan grades, one per Ossus gem leaf: kathracite, relacite, danite, mephite, pontite. Text only: ENUMs, attributes and pools unchanged.
  - `local_planets-names.tre` 39a89e6c is verified against the installed fbf62971: only `resource_tree.iff` differs, and only those five CLASS cells.
  - Installs at the next restart once the owner's client is closed. Spawns already in play keep their old names.
- **Ossus resource map:** `Fable-resources3/lore/ossus-resource-map.md`.
  - Every Ossus resource on Wookieepedia, mapped: the gems; kingwood and bambwood; potam; the fauna drops (mud yak, kirruk, gokob, tree frog, tribis, kaddyr bug, Adegan eel).
  - Also: the twin-sun solar; and the Vong line (Ossus Project, yorik coral, lambent, voxyn, yorik-kul).
  - Wookieepedia lists Ossus's exports as "none", so its metals stay generic.
- **A trap for chain builds.** While the test launcher's `swgemu_login.cfg` is in place, the client load order includes our own `local_planets.tre`.
  - A chain build then reads our archive as its base and silently drops the Chiss files.
  - `build_names_archive.py` drops `local_planets.tre` from the order. Anyone else building the chain during a test session must do the same.
- **Fable** hit its weekly limit (HTTP 429) in the middle of S6 (Nautolan and Togruta, partial in `Fable-species/s6/`). It resumes at the reset; S6 waits on the owner's Chiss test anyway.
- **Local stand-in model** (dc8de92): Ollama `gpt-oss:20b` through `tools/agents/local/local_agent.py`.
  - Three file tools inside one workspace; no shell and no network. 64K context, about 27 tok/s.
  - First test: it summarised a bot report correctly in 4 steps, 16 s.
  - `codex exec --oss` cut every reply off at about 260 tokens, so it is not used. Not yet in the relay.

#### 2026-10-14 23:27 Claude: dev build done; test-galaxy restart denied (waiting on the owner)
- Dev built after `08e6a924`: `core3` relinked at 23:25 with no errors. The `core3client` binary is still the 18:08 build. Nothing was stopped or started.
- New dev commit `f1ce7007`: `/agentgear survey` gives one survey tool per resource class (mineral, inorganic/chemical, gas, liquid/water, moisture, organic/flora, solar and wind/energy). No armour or stimpacks. Compiled; not exercised on the galaxy. This closes the C23-B1 gap (the crew had no chemical, gas, moisture or flora tools).
- **Test-galaxy restart NOT done.** The auto-mode permission check denied the restart command ("interfere with workloads"). The galaxy is still down and no bots are logged in. Waiting for the owner's go or a permission rule before retrying.
- ChatGPT: C23 can't run until "restart done" is posted. When the galaxy is up, the C23 preflight should call `bot.gear('survey')` for each crew member (`gear()` is in `tools/bots/squad.py`).
- Owner's rule, saved to memory: fix forward on dev; no auto-revert unless a failure is catastrophic. No dev reverts were made.

#### 2026-10-14 23:17 Claude: the evening: test galaxy with Chiss, Ossus and the wide resources (19:13); owner test list; Fable's TortoiseBots slice 1 and C29; a local stand-in agent
- **Test restart 19:10–19:13** (no client, no round): archive `248092a2` in `SWG-client/` and `/opt/swg/tre/`; test zones hoth and ossus. Log: "Resource backfill: zone hoth: 63 checked, 33 added, 8 at max pool, 22 not chosen"; "zone ossus: 23 added"; NativePool 120, MinimumPool 28. `squad.py setup` relogged the bots 19:14.
- **For the owner: `Owner-test-list.md`** (Chiss creation, Ossus first look, Hoth/Ossus resources, Echo Base, the Hoth leftovers), and `Client-graphics/` (ReShade and DLSS 5 through the Feeder for the 32-bit client, owner-installed; `SpeciesColorLock.fx`, ours). h `f12c2f0`.
- **Fable, TortoiseBots slice 1** (`Fable-tortoise/`, owner authorised full use; AGPL-3.0 notice and credit kept): failure backoff ported, our incident layer over Bot-reports; run_checks 8/8 on my side. On 149 reports: 9 open (5 blocked, 4 defect candidates). Besh "ordinary wild prey found" fails since 14:19 because only bots and helper droids are within 90 m of the patrol spot (a patrol-spot problem, not the server). h `f12c2f0`.
- **C29 moved from ChatGPT to Fable** (queue: hold, reassigned). Fable's `Fable-resources3/lore/`: 19 Legends materials mapped to stock classes (stock ones not duplicated: cortosis, phrik, doonium...), and two staged: Adegan crystal (Ossus) and lumni lichen (Hoth). Archive `local_planets-lore.tre` fbf62971 (verified), installed at the next restart. Dev `08e6a924` (pool lines, luac ok). h `acb25c4`. Fable's owner questions: rename Ossus Type 1/2 gems to Kathracite/Pontite; a Smuggler lumni-spice schematic; beskar stats; Corusca on Yavin 4; yorik coral.
- **Third agent (owner):** a local model, OpenAI's gpt-oss-20b through Ollama and `codex --oss` (nothing leaves the PC). `tools/agents/local/Modelfile.gpt-oss-20b-64k` written (64K context). Owner installs Ollama and the model; then Claude adds a local switch to the relay and runs one watched test. Scope: bot scenarios, tools, docs, first-pass reviews; Claude reviews all.

#### 2026-10-14 18:55 ChatGPT: C29 mechanics and owner-resource handoff complete
- Owner requested pre-CU resource/crafting and external Galaxy Harvester research for Claude, then all extracted TTRPG materials in a clean adaptation list. Saved Documentation-support/resources-crafting-and-galaxy-harvester.md and owner-ttrpg-resource-handoff.md/.json.
- Verified exact preservation of 185 planet + 80 pharmacopoeia rows (241 distinct names), 28 husbandry references, 16 recipe input groups and all three source hashes. Armory 247 items and pharmacopoeia 85 finished substances remain separately catalogued. Routes are proposals; no SW5E mechanics transferred or new resource classes enabled.
- Read-only source pin 19f40ab89363d865f4b9d1ae9435a0099c94c595: 15-file hash/range manifest plus eight client resource-class leads. Documented lifecycle, concentration versus quality, weighted experimentation, stations, harvester limits and exact factory ingredients; GH GPLv3 and SWGAide-Unity desktop distinction. No downloads/installs/accounts/public submissions, bot driving or server changes.
- Received Claude 18:50 update: C25/C26 reviewed/built; R2 98ad1d1d and coverage 3a0b154f await our independent C24b review. This source/mechanics checkpoint does not review those newer commits or claim gameplay acceptance. Next queue remains C24b, C23c after restart-ready, remaining C29 Legends/lore integration with Fable R3. Source-backed planning ready; effective runtime settings and companion-tool compatibility untested.


#### 2026-10-14 18:50 Claude: ChatGPT's C25/C26 and the R2-F1 fix in dev; Echo Base and Ossus on the test galaxy; owner: wide resources, coverage kept at 80%
- **ChatGPT's six worktree commits reviewed and in dev** (`-x`): `7267cf3c` C25 ticket messages; C26 telemetry `58797fdf` resource units, `788e456f` own credits, `7e6625c0` Hoth/Ossus names, `7817437a` waypoints, `e9a8a6c0` nine attributes. Checked against the server serializers (RCNO3 quantity and spawn ID after the TANO3 fields, delta 0x0B; CREO1 bank then cash; DeltaVectorMap ADD/DROP/SET with the value on drop; WaypointObject::insertToMessage). No findings. Built 18:09 (core3 + core3client).
- **R2-F1 fixed (`98ad1d1d`)** with ChatGPT's proposal: the chance counts maps outside the backfill zones. Model, 20,000 spawns x 5 starts: 333 changed after the first start with the old rule, 0 now.
- **Fable E0 Echo Base `8f2072e7`, Fable O5 Ossus `2ada3784`** in dev. `test_galaxy.py` TEST_ZONES = hoth, ossus. Archive `254d0e49` (Hoth + Ossus) on the server and in `SWG-client/`; `aee83cc6` kept in `/opt/swg/tre/old/` and `Temp/archive-backup-1830/`. **Re-running `hoth_client_build.py` alone republishes a Hoth-only archive:** use `Fable-ossus/o5/build_test_archive.py` until R3 merges the builders.
- **Restarts 18:17 and 18:35** (no owner client; the 18:02 round halted at 18:10; the 18:31 cycle slot didn't fire). Ossus deployed: 9 regions, 87 snapshot objects (Knossa starport), native pool 84 (42 + 42). Bots relogged 18:37 on ChatGPT's new body. Echo Base loaded with no errors; owner check in `Fable-echo-base/README.md` section 4.
- **Backfill was thin:** Hoth 3 added (44 at max pool), Ossus 1 (47 at max). The galaxy-wide minerals are 8-planet types, already on 8 of the old 10. **Owner: "Scale the galaxy-wide coverage to about 80% as planets are added."** Dev `3a0b154f`: `poolScaleZones = 10`, so each galaxy-wide type's planet range scales by active zones / 10 (8 of 10 becomes 10 of 12). Backfill cap = scaled max, chance = share of 10. Key missing (live) = stock. Built 18:48; restart after the 19:01 round starts.
- **Owner: "get hoth and ossus their resources, add everything we have for them then lets layout all the resources we have and get them adapted for swg and integrated. (a wide crafting pool keeps people interested.)"** Fable R3 (`Fable-resources3/`): Hoth's 4 MTG gems and 3 missing energies, Ossus's own minerals, then the full inventory (stock 725, MTG's 120 extras incl. Dromund Kaas 45 and space 18, Ossus, the owner's book) with an integration list. ChatGPT C29: Legends lore materials for it.
- **TortoiseBots, owner: "we do have auth to use its code and assets fully, hes the one who sent me UM".** Sagiroth's own code and assets may be ported (AGPL notices and credit kept); donor files keep their licences. Fable's fallback after R3: our SWG bot framework from it, staged in `Fable-tortoise/` (tools/bots stays ChatGPT's).
- **Next:** Claude reviews Fable S5 (Chiss, staged in `Fable-species/s5/`). ChatGPT: C24b, C23c, C29 (relay queue).

#### 2026-10-14 18:40 ChatGPT: C29 resource/crafting research claimed
- Owner requests resources/crafting and external Galaxy Harvester research for Claude. Bounded pass: primary local Core3 source + historical player workflow, Galaxy Harvester official help/source and SWGAide desktop distinction. No bot/game operations, external accounts, downloads/installs or resource publication.


#### 2026-10-14 18:03 ChatGPT: C28/F100 browser fleet monitor scoped
- Owner proposes planet maps/moving bot markers; actual video for small squads, maps sufficient at fleet scale. Saved Documentation-support/bot-fleet-browser-monitor.md with snapshot-backed TortoiseBots reference and current telemetry inspection. Current status is five-minute text; activity records lack positions; headless bodies cannot render video.
- Proposed passive telemetry, epoch/sequence/stale guards, calibrated maps/interior coordinates, selected graphical observer feed, bounded fleet overhead and C27 incident links. No code/assets copied, bot queries/driving, UI/capture, services/accounts/network changes or deployment. Next: local map telemetry prototype after intake/build priorities and owner scheduling.


#### 2026-10-14 18:00 ChatGPT: planet fleet monitor idea claimed
- Owner proposes browser planet maps with moving bot markers, video preferred for small squads and map-first fleet scale. Claim design/telemetry feasibility against existing saved sources only; no bot driving, capture, services or deployment.


#### 2026-10-14 17:52 ChatGPT: C27 scoped; screenshot leads screened
- Owner clarified agent relay to Discord after durable in-game intake; mixed developer/experienced/new player team. C27/F98 and onboarding F99 added. Source inspection: /report stub; native CreateTicket callback gated off by default, Mantis submission, category early return and commented receipt/crash TODO. Design saved, not implemented; no Mantis install or backend toggle.
- Screenshot supplied seven sources: SWAPI, Jedi-Faker, OpenSWE1R, Open Rebellion, OpenJKDF2, KYBER, NGECore2. Bounded primary-source screen saved; most promising gameplay lead Open Rebellion MIT engine, data separate. Other grants/components and NGECore2 restrictions recorded narrowly. No clones/imports/new services or Discord posts. Research checkpoint ends here.


#### 2026-10-14 17:47 ChatGPT: player bug inbox design claimed
- Owner wants developers, experienced players and new players, plus in-game bug reports persisted locally for agents to read when available. Claim native-report source inspection and local queue contract/design; no deployment, server edits or Discord creation.


#### 2026-10-14 17:40 ChatGPT: C17 remote-tester Discord blueprint complete
- Owner confirmed remote testers. Saved Documentation-support/discord-dev-qa-setup.md: private developer/QA areas, roles, forums/template/tags, native events, existing curated/status webhook tool, optional future slash app/issue intake, remote-access/reset gates. No Discord service, integrations, network change, invitations or posts created. Setup requires owner go under AGENTS.
- Official Discord/WSL/Tailscale docs checked; plugin search returned no Discord integration in this session. Existing sender verified by source inspection to permit only curated/status sends; no delivery/runtime claim. Claude owns any later QA host/account/galaxy preparation.


#### 2026-10-14 17:36 ChatGPT: C17 developer/tester Discord plan claimed
- Owner asks to investigate Discord integrations for a private developer server and potential hired testers. Claim documentation/integration research only; no server, app, webhook, invitations or posts created.


#### 2026-10-14 16:48 ChatGPT: owner video investigation request
- Claimed and completed the inbox handoff: owner asks Claude to investigate https://www.youtube.com/watch?v=bhAGu065VKk. Video contents have not been reviewed by ChatGPT; Claude investigation is pending.


#### 2026-10-14 16:39 ChatGPT: session closed at owner request
- Owner asked to close before usage exhaustion. No active ChatGPT driver claim; Esk restored to squad-plan and left upright on Tatooine. Claude retains dev tree/builds/test galaxy. GPT source worktree clean, no R2 code edits, no live changes/restarts/deploys.
- C26 source stack after C25 5c41ed62: efded50e resources, 0e02fcf6 credits, 37459ff6 planet names, b0360ec8 waypoints, 19f40ab8 secondary attributes. All unbuilt/runtime untested; Claude review/cherry-pick/build required. C23 readiness gate now checks nine armor pieces actually worn. Setup approved and done; seven pieces still refused for secondary stats; four survey-tool categories missing.
- Local commits: 088465d telemetry/fixtures; c1dd1b9 privacy; aef1307 gather evidence; edad1c8 initial asset/species receipts. Closing commit follows. Offline: six wire-layout fixtures, nine C23 evidence fixtures, 24 Discord privacy/transport fixtures, four gather fixtures. These are not C++ execution or gameplay acceptance.
- Nineteen authorized archives retained, 414149488 bytes; no imports/scripts/installs. Five 7z inventories are names-only, full audit held. Poly Haven API 403 held. C21 species checkpoint: 36 biological candidates + two human faction options + two droid options; overall census open.
- R2-F1 remains open: isolated design proposal saved, source implementation not started. C24 remains NO-GO. PDF snapshot refreshed with selected docs, scope/manifest; not a verbatim chat export. Next: Claude review/build C25/C26, solve ordinary buffs/kit and remaining survey tools, then C23 rerun. C3/C5 remain open.


#### 2026-10-14 14:56 Claude: owner: Fable does content first; order E0, Ossus, species (Chiss), Hoth extras
- **Owner: "i would prefer fable handle all the content additions first?"** Fable stopped L1 (live client kit) and T2 (refs scanner); its partial L1 notes stay in `Fable-live-client/` with a status line, for ChatGPT or Claude to finish.
- **Fable now: E0, Echo Base's first look** (`Fable-echo-base/`): fit the NGE building to MTG's three cut-outs, a dev-ready spawn screenplay, the client files it needs, and a one-page owner check for the next client session.
- **Owner answers:** Ossus is next after E0, and Claude may put Ossus into the test-session archive for a first look (question 10). Chiss first (question 11). Keep all 18 Hoth deeds (question 2). Then the Hoth extras.

#### 2026-10-14 14:51 Claude: Fable R2 (resource backfill) in dev, T1 (format tools package) in h; Fable on L1 (live client) and T2
- **R2, dev `eccb53e1`:** `backfillZones` in resource_manager.lua (empty by default, so no change on live). At load, each unrestricted in-shift spawn gets a map on the named zone with the chance it would have had at creation; the roll hashes spawn and zone, so later starts decide the same way. Reviewed by Claude (createSpawnMaps keeps existing maps; locked like the top-up). Dev build clean (14:49). `test_galaxy.py` now sets it to the test zones at every start (h `93ffa9e`): every restart restores a pre-Hoth backup. Fable's estimate: about 24 of the 64 in-shift galaxy-wide spawns reach Hoth (16 mineral, 5 chemical, 3 gas). **Untested:** the next restart waits for ChatGPT's C23 run (Esk, started about 14:50, up to 30 minutes). ChatGPT, C24: R2 is the backfill to review.
- **T1, h `1291ba0`:** the format tools are one package, `tools/swgfmt` (the old paths are shims). I re-ran the builder: `local_planets.tre` is byte-identical (aee83cc675a1e6cf); client_load_order prints the same output; the round trips are exact.
- **Fable's next task (`Fable-live-client/`):** L1, how a live player's client gets Hoth (the live launcher doesn't load `local_planets.tre`): search-order notes, a staged live launcher/cfg, a read-only checker, a player install and rollback checklist, what a player without the archive sees, and the live server config lines (reviewed, not applied). This feeds ChatGPT's C24 gate. T2: our own refs() scanner, so `hoth_closure.py` stops exec-ing Bellum's iff_tool.

#### 2026-10-14 14:47 Claude: test galaxy restarted (owner logged off): Hoth minerals in spawn, rebuilt archive installed
- **Owner, 14:38: "ok logging off now, restart it."** No client running. The 14:31 overnight round was halted (`squad.py halt`, ended 14:39). Stop at 14:39, start 14:42, ready 14:45 (backup galaxy-20261013T172001Z, dev scripts `1c4c24fb`, dev server build). `squad.py setup` relogged the bots.
- **Hoth minerals:** the server log has "MinimumPool updating: Spawned 10" (the ten `*_hoth` types from `1c4c24fb`; NativePool spawned its 42 as before). Not yet seen in a survey window: that is ChatGPT's C23 check (a).
- **Archive:** `local_planets.tre` aee83cc6 (Fable B1-B3 build) is now in `SWG-client/` and `/opt/swg/tre/`. The old 6cfeeb51 is kept at `/opt/swg/tre/old/` and in a Windows temp backup.
- **ChatGPT:** C23b (the gameplay run) is open in the relay queue, after C23a (the scenario), which it needs.
- Fable reported R2 (resource backfill patch) and T1 (format tools in one package): review next.

#### 2026-10-14 14:35 Claude: owner confirms all 18 Hoth map markers; ChatGPT gets three jobs of its own (C23–C25)
- **Map markers, verified by the owner:** "only one" was the collapsed category list. With Points of Interest expanded, all 18 Hoth POIs show with their names, in the right places. Categories: City, Cloning Facility, Junk Shop, Points of Interest, Starport, Terminal, Waypoint. Region names also show on entry ("Lucky Despot Wreck", "Scavenger Starport").
- **Owner: "you can probably give GPT some more responsibility as well."** ChatGPT now owns:
  - C23: Hoth gameplay acceptance and its fail list;
  - C24: the Hoth release gate and its "reviewed by";
  - C25: its own server-code worktree `/opt/swg/Core3-gpt` (branch `gpt/work` from dev `1c4c24fb`; rule added to AGENTS.md).
  - Instructions above the log; the relay queue has C23a, C24 and C25 open, and C23b (the run) on hold until my restart.
- The owner is still in the client on the test galaxy; the restart (dev `1c4c24fb`, archive aee83cc6) waits until they log off.

#### 2026-10-14 14:23 Claude: owner's Hoth findings (no minerals to survey, map shows one marker); Fable B1-B3 applied
- **Surveying on Hoth: no minerals.** The test DB has 15,020 resource spawns; only the 42 native-pool spawns (organics, energy, fiberplast, water vapour) are on Hoth. Core3 assigns a spawn's planets only at creation (`createSpawnMaps`), so galaxy-wide spawns from before Hoth joined `activeZones` never reach it, and MTG's ten Hoth-only inorganics (`steel_hoth`, `iron_hoth` and so on) were in no pool. **Dev 1c4c24fb** adds those ten to `minimumpoolincludes` (one of each always in spawn, Hoth only); it takes effect at the next test restart, not while the owner plays. Galaxy-wide minerals reach Hoth only as old spawns expire (6-11 days); Fable is staging an opt-in C++ backfill (R2) for that, which Ossus will also need.
- **Map markers:** the owner says they "show up fine" but there's only one. The 18 Hoth rows in `clientpoi.iff` have the same layout as stock ground rows (X, 0, world Y). I've asked the owner whether that means one marker on the whole map and for a screenshot.
- **No loot from a tauntaun** is by design (lootChance 3%, `hoth_decor_common`). Harvesting is the creature's yield, and its Hoth meat, hide and bone types are in spawn.
- **Fable B1-B3 applied (h c2573e3):** the archive builder and `client_load_order.py` now use our own format tools (fmt_tools, hoth_ui, tre_write). The real build is 20/20, and only the two UI includes changed (stray blank lines gone; now pure insertions over stock). The new archive (sha256 aee83cc6...) is in Local-content only; it's installed at the next restart window. Four old Hoth check scripts still exec Bellum's `tre_inventory`; that's part of Fable's T1 (tools/swgfmt).

#### 2026-10-14 14:12 Claude: owner sees Hoth in the real client (stormtroopers, wampas)
- Owner report: Hoth loads in their client on the test galaxy, with stormtroopers and wampas in view. This is the first human look at the MTG terrain plus our spawns; until now only bots had seen it.
- Still unseen by anyone: the planetary-map markers and labels (client files), Hoth resource names when surveying, Hoth loot drops, and Vell's first job run start to finish. Guide: `Fable-hoth-guide/hoth-first-session.md` sections 3, 7, 8 and 2.
- No test restarts while the owner's client runs.

#### 2026-10-14 14:06 Claude: C22 findings fixed; owner is on the test galaxy; Ossus ready to pack in one step
- **ChatGPT's C22 review** (`Documentation-support/review-C22/`, 2 P2 + 1 P3, no P1):
  - F1, fight attacks not guarded: fixed in dev `c046e633`. Each attack is dispatched under `worldMutex` after checking scene, connection and target; a failed approach ends the fight with its reason. Dev build clean. Bodies pick it up at their next login.
  - F2, the rancor hue can't apply on `rancor.iff`: fixed in `54a33063` (`rancor_hue.iff`).
  - F3, camp prop headings in degrees: already fixed in `5eb140ce`.
- **The owner renamed the login file and is in the real client on the test galaxy** (about 14:05). `client_load_order.py` confirms `local_planets.tre` at 49 wins the planet tables, MTG's `hoth.trn` loads, and the live login is backed up in `swgemu_login.live.cfg` until the launcher puts it back. No test restarts while the client runs (AGENTS.md).
- **Fable:**
  - R1: nothing reads `resource_names.stf` (Core3 sends the tree's CLASS text), so no blank names; no action.
  - O3: Ossus map art, globe and loading tile, with our own DDS writer.
  - O4: `stage_ossus(stage_dir, base)` packs every Ossus client file on top of Hoth in one step (self-test passed, Hoth kept).
  - Now: replacing the builder's Bellum tools with our own (UI merge byte-exact, our own TRE writer).

#### 2026-10-14 13:43 Claude: Hoth check 32/33 after the restart; the owner's Hoth walkthrough and an Echo Base plan; Fable on resource names
- **Third test restart 13:32:** Vell standing still, 33 Hoth regions (15 + 18 named), archive `6cfeeb51`. **Bot check 13:43, 32/33:** all ticket purchases pass (more than 5 minutes after the start, which supports the boot-delay diagnosis). **Vell stands at exactly (44, -2010)** and talks. The one FAIL was the check's own wrong expectation (salvage-detail props; there are none by design), now fixed.
- **For the owner: `Fable-hoth-guide/hoth-first-session.md`,** one route through everything built tonight (nine stops: waypoints, fares, boss levels, what to report). Verified versus unverified is marked.
- **`Fable-hoth-guide/echo-base-plan.md`:**
  - MTG's `hoth.trn` already carries the Echo Base massif with three cut-outs (hangar, main, tower) near (-5100, 5400).
  - The NGE `echo_base` building (33 rooms) and its props are in the MTG archives.
  - First step E0: a one-day look in the real client (does pre-CU draw the NGE building?), with a stock fallback. About 6–7 days in all; owner questions on story and GCW.
- **Fable's finding:** 11 MTG Hoth resource classes have no name in any `resource_names.stf`, so surveys may show blank names. Fable now: R1, a resource-name audit across all planets with a staging function; then O3 (Ossus map art, globe, loading tile, our own DDS writer).

#### 2026-10-14 13:41 Claude: CORRECTION: silent ticket failures are Core3's 5-minute shuttle delay, not the travel coupon
- **My 09:40 diagnosis was wrong.** No bot run has ever shown the coupon question (checked in the 09:43 and 13:36 reports). The pattern is timing: purchases failed at 09:37 and 13:36, about 3 minutes after a test restart, and worked at 09:43, 10:01 and later.
- **The cause, in source:** `ShuttleZoneComponent.cpp` delays every shuttle's `ScheduleShuttleTask` by `Core3.ShuttleZoneComponent.BootDelay` (default 300,000 ms) after a server start. Until then a travel point has no shuttle, and `PurchaseTicketCommand` returns GENERALERROR **with no message** (`arrivalShuttle == nullptr`). This also explains C7's "first purchase after a galaxy start fails silently".
- **Fix (test only):** `tools/test_galaxy.py` writes `Core3.ShuttleZoneComponent = { BootDelay = 30000 }` into the disposable config. Live keeps the stock delay.
- **Kept:** `ticket_pages.answer_coupon` (the coupon question is real Core3 behaviour; harmless). Its docstring now carries the correction.
- **Possible player-facing fix later (dev C++):** a system message when no shuttle is in service yet, instead of silence.
- **Also seen at boot (13:32), probably not ours:** `[TaskScheduler0] ERROR - custom queue tatooine not found` with an exception, while the JTL space zones deploy; the server still reaches READY.

#### 2026-10-14 13:27 Claude: Hoth map markers and place names in; restart queued; Fable on the owner's Hoth walkthrough and an Echo Base plan
- **Fable's B3 (`Fable-hoth-mapnames/`), no C++:** the client draws Points of Interest from its own `clientpoi.iff` and place labels from `clientregion/hoth.iff`.
  - Dev `dd16bcff`: 19 NAMEDREGION circles (four cave dens, six camps, eight zones; "The Ice Caves" renamed).
  - Archive `6cfeeb51…` (installed on the server and in the owner's client; `e274ed12` kept beside both): the region names, place labels, POI list and POI strings, built from stock/MTG copies through `winning()` (never our own archive). The 15 earlier files are byte-identical, and a repeat build is identical.
  - Side effect to know: Core3 keeps structures 100–150 m from a client POI.
- **Restart queued** after the 13:01 round (guarded as before): loads Vell standing still (`e9094960`), the named regions and the new archive.
- **Fable now:** G1, a one-route walkthrough for the owner's first Hoth session in the real client; G2, an Echo Base plan (plan only).

#### 2026-10-14 13:12 ChatGPT: C22 independent Hoth/fix review complete
Reviewed by ChatGPT: dev `c5f1ae06`, `69eb77fe`, `de1b679a`, `23014f39`, `90f60a81` and h `f0b192e`. Report/evidence commit `b4472b8` (`Documentation-support/review-C22/`): changes requested, 2 P2 (fight cancellation, rancor hue body) + 1 P3 (prop heading units). All 129 cave floor points, camp heights and registrations pass offline; spawn locks/archive fix accepted within documented limits. No server edits/build/restart/bot control; gameplay and concurrency untested. Next: Claude fixes findings, re-review, then authorized in-game checks.

#### 2026-10-14 13:03 Claude: C20's return-home works for real; species S4 staged; Fable on Hoth map markers
- **Claude's usage ran out about 10:15–13:00,** so the overnight check skipped 10:31–12:31 (it runs through Claude). The 13:01 run resumed it.
- **C20 runtime proof, round 20261014-100158:** Esk started on Corellia; esk-routes BLOCKED ("Mos Eisley routes require Tatooine"); the fallback's return-home preflight bought a ticket on Corellia and rode home: **"Esk: recovered to Tatooine" PASS.** That needed the coupon fix (`ff8850e`). Remaining Esk FAILs: indoor "no path" to the cantina (1/4) and the run budget.
- **ChatGPT:** C21 (the owner's census) saved checkpoint 1 at 10:06 (`9686c15`); C22 (Hoth review) started 13:01.
- **Fable's species S4 (`Fable-species/s4/`, staged, nothing applied):**
  - `acst.py` (the customization table, byte-identical round trips): Chiss needs no splice; Gotal and Nautolan do; Togruta has no customization map anywhere.
  - `cpp/species-chiss-human-rig.patch`: Races.h, CreatureObject.idl, the Director constant, and a data-driven `humanRigRaces` clothing rule (`canWearRace`). `git apply --check` OK.
  - `species_tables.py` `stage_species([...], dir)` for the archive builder.
  - Claude reviews and builds the C++ once the owner answers question 11.
- **Fable now:** Hoth map markers and region names (the held batch B3) in `outputs/Fable-hoth-mapnames/`, preferring stock Core3 mechanisms over new C++.

#### 2026-10-14 10:12 Claude: Fable's species research (S1–S3) in; owner question 11; ChatGPT on C21
- **`Fable-species/`:**
  - S1: provenance. `newspecies-original.zip` is Halyn/Phoenix's 2016 beta, usable with credit; its client files are already in the owner's client; its Wookieepedia descriptions and C++ are excluded or reference only. **No Zeltron package exists** (the "zeltros" zips are a planet), so Zeltron stays held with EiF (F51).
  - S2: what a playable species needs, end to end. For all 16 new species the creation, customization, skills and names tables, the race Lua/C++, and the wearables' race lists are missing.
  - S3: Chiss staged (server Lua, every table row, a skills row; the C++ listed, not staged).
- **Owner question 11** (order, Zeltron, Hutt, names and stats). Claude takes the two technical calls (splice the customization table; a C++ clothing rule) unless the owner objects.
- **ChatGPT:** the relay started C21 (the owner's census) at 10:01 with full access; C22 (Hoth review) is next.
- **Bots:** the 10:01 round runs with Esk parked on Corellia, so esk-routes should hand over to C20's return-home fallback.

#### 2026-10-14 10:06 (C21 checkpoint 1) - ChatGPT
Saved reproducible six-manifest baseline: 102 catalogue rows, 12,556 distinct MTG registered paths, 13,627 historical dormant paths; inherited C14 overlap 10/11 Legends-labelled local zones. Added scoped shortlist and remaining batches; no current server/game/web validation or imports. Local checkpoint commit `9686c15`; C21 returned to open, next checkpoint worlds/Legends audit.

#### 2026-10-14 09:55 Claude: Vell fix in dev; outdoor den staged; Fable starts Phase 4 (species)
- **Dev `e9094960` (Fable's fix1):** Quartermaster Vell gets `flags = AI_STATIC` in his spawn data, as stock `luthik_uwyr.lua` does. Without it, a theme-park giver patrols (AiAgentImplementation), which is why he drifted. It loads at the next restart.
- **Salvage detail "0 props" is by design:** its wreck pieces are MTG snapshot objects 60–100 m out, not our props.
- **Mynock den option 2 staged** (`Fable-hoth-batchB/den-outdoor/`): an outdoor den with 23 creatures among 18 stock ice columns in the mynock fields, no client change. Load one option only (owner question 9).
- **Fable now:** roadmap Phase 4, species, in `outputs/Fable-species/`:
  - S1: the licence and provenance of the downloaded species packages;
  - S2: an end-to-end map of what a playable species needs (client and server);
  - S3: a staged plan for the first species from the package.
  - Hybrids are deferred (owner rule).

#### 2026-10-14 09:49 Claude: Hoth content verified in game by a bot (27/28); ticket purchases fixed; Fable's Ossus O2 staged
- **Second test restart 09:33** (camps `de1b679a` + `5eb140ce`, missions and quest `92d99dba`, archive `e274ed12`): ready in 74 s, no errors from the new files, 18/18 bots back.
- **Bot check `tools/hoth/hoth_content_check.py` (Esk, 09:48), 27/28:**
  - Tatooine → Corellia → Hoth → Corellia travel works.
  - Wampas are inside the ice-cave cells (53 and 46 found).
  - All six camps have their NPCs; five have their props (the salvage detail found none under `object/static/structure/`, so Fable is checking).
  - Both mission terminals stand at the outpost.
  - **Quartermaster Vell talks** (opening screen and two player options from our string table).
  - Area-spawner lairs: none yet, as expected; zones fill only near players.
- **Ticket purchases failed silently** (Cresh's travel since 06:03, Esk 09:37). The cause is the new-player travel coupon: `PurchaseTicketCommand` asks "use the coupon?" and makes no ticket until that's answered, and the galaxy restores give the bots their coupons back. Fixed: `ticket_pages.answer_coupon` in `esk-hoth.py` and `cresh-travel.py` (`ff8850e`). This likely also explains C7's "first purchase after a start fails".
- **Vell wanders** (26 m from his spawn), so a bot that walks to his old spot can miss him. Fable is making the quest NPCs stand still (fix1).
- **Fable's Ossus O2 (`Fable-ossus/o2/`, staged, not applied):**
  - Our own snapshot writer (byte-identical on 4 stock snapshots) and `ossus.ws`: the Knossa starport, 3 stock caves at the terrain's cave mouths, 31 ruin pieces.
  - Server Lua: planet block, regions, 10 native creatures on stock bodies, lairs, spawn groups.
  - Resource rows (45 cloned from Dantooine).
  - Held until the owner answers question 10.

#### 2026-10-14 09:27 Claude: Fable's Ossus O1 staged (terrain, our own table tools, sky/loading); Fable on O2
- **`Fable-ossus/` (staging only):**
  - `terrain/ossus.trn`: 9 shader, 7 flora, 6 radial and 6 environment families of stock art referenced by name; hills, forests, the Eocho mountains, the Academy benchland, Imhar Canyon, a lake, a flat Knossa pad, a ruins pad, a road and 3 cave mouths.
  - Verified offline: byte round trip, the Core3 height-reader port over a 32 m grid, flatness at every site.
  - Our own CSTB/DTII/STF readers and writers (`tools/swg_tables.py`, byte-identical round trips on 13 stock files) replace Bellum's AGPL tools; the Ossus registration tables are staged; sky (Dantooine + a second sun), environment, clientregion and loading tables.
- **Two engine findings:** Core3's road affector only acts within 500 m of a road's start, so the road is 16 pieces; a 255 bitmap pixel passes the FBIT check only by float rounding, so bitmaps are capped at 254.
- **Nothing is in the client or on the test galaxy.** Integration is Claude's: the archive builder will take both planets. **Owner questions:** question 10 above.
- **Fable now:** O2, story-neutral: our own snapshot writer and `ossus.ws` (Knossa starport, stock caves, a ruins field), the server Lua (planet manager entry, regions, native fauna on stock bodies), and the resource data.

#### 2026-10-14 09:03 Claude: Hoth batch C in dev (missions, quest chain); new test archive installed; Fable on Ossus O1
- **Dev `92d99dba` (Fable's batch C, luac clean):**
  - A `hoth_destroy_missions` group (tauntaun 60–72, ice mynock 64–76, raider camp 70–80, wampa 85–100).
  - Two mission terminals east of the starport.
  - 8 neutral NPC spawn points and a "Scavenger Starport" mission city for deliver missions.
  - A 3-step quest chain from Quartermaster Vell at the outpost, written in our own words.
  - Fable's `apply.sh` didn't write its one "before" patch (`mission_cities.lua`); Claude added that line by hand and told Fable.
  - Snowspeeder: already complete in dev. Tauntaun mounts need client data (a rider slot), so plan only.
- **Archive `e274ed12…`** (installed on the server and in the owner's client folder; previous `b7930396…` kept beside both): adds the quest's 81 strings as a new `string/en/static_npc/hoth/scavenger_quartermaster.stf`. The other 14 files are byte-identical.
- **Test restart queued** after the 09:01 overnight round (about 09:27, same guards as 08:33): it loads the camps, the missions, the quest chain and the new archive.
- **Owner questions (Fable's batch C README):** rewards (credits only?), artisan/entertainer terminals too, a lower-level mission band (no Hoth creature is below level 62), deliver points at the camps, tauntaun mounts (needs client data) or leave them as wildlife.
- **Fable now:** Ossus batch O1 in `outputs/Fable-ossus/`: the full `ossus.trn` (story-neutral), our own writers for the planet registration tables (replacing Bellum's AGPL tools), and the environment/loading tables. Nothing goes on the test galaxy or in the client without Claude, and the real-client look needs the owner.

#### 2026-10-14 08:40 Claude: test galaxy restarted (caves + batch A + C4f-F1); Botanist box survives a relog
- **Restart at 08:33** (AGENTS.md standing OK: no owner client, no squad round; overnight check paused with the stop file, then resumed). Ready in 92 s, Hoth deployed with **15 regions** (7 + batch A's 8), 94 snapshot objects, no errors from the new files (only the old stock `loot_base`/`retrieve_quest_base` warnings). All 18 bots logged in again.
  - Running dev build: the ice caves `c5f1ae06`, batch A `69eb77fe`, the spawn-command lock fix `23014f39`. The bodies run the C4e-F2 movement fix `90f60a81`.
  - Camps `de1b679a` went into dev after the start, so they load at the next restart.
- **Botanist (owner book README updated):** server half passes. Pell is granted the box, finds the trainer at 3516 -4783, and gets the stock conversation. After a relog, and before any grant, the trainer says `topped_out`, so **the box persisted**. `botanist_check.py` now asks the trainer before granting (/agentSkill reports a re-granted box as "granted", which would hide a loss). Left for the owner's client: the skill window, and the trainer's name (the bot sees an empty title).

#### 2026-10-14 08:28 Claude: Fable's batch B reviewed; camps go in, the den waits for the owner; Fable on batch C
- **B1 (Hoth camps):** 6 sites, 35 stock props, 43 NPCs in the batch A zones. Applied to dev after the 08:27 restart finishes copying scripts, so it loads at the next restart.
- **B2 (mynock den):** held as owner question 9: it changes Hoth's terrain file, which the client also loads. **B3 (names):** held until map markers exist (dev has no MAPPOI flag).
- **Fable now:** batch C in `outputs/Fable-hoth-batchC/`: Hoth destroy missions at the outpost terminals, one short quest chain in our own words, and vehicles/mounts (MTG's snowspeeder and tauntaun).

#### 2026-10-14 08:20 Claude: Hoth batch A in dev (area spawners, glacial rancor); Fable on batch B
- **Dev `69eb77fe` (Fable's batch A, hash-checked apply, luac clean):**
  - 8 area spawners on flat ground of MTG's map (tauntaun plains ×2, mynock fields, wampa flanks ×2, Imperial, Rebel and scavenger zones), with 6 new spawn groups on the ported lairs. The world spawner stays as the fallback.
  - The lair cap goes 1024 → 1408 (+37.5%).
  - A clean-room glacial rancor, "Hoarfang": stock rancor body, palest palette colour, scale 1.35, our own text. Registered, not spawned.
  - Fable's audit: every other Hoth creature that MTG's and Bellum's scripts reference is already in dev.
- **Correction:** Fable's README called level 400 "the owner's choice". It's Bellum's value; Claude reworded the file and README.
- **Owner questions (Fable's README):**
  - density 1408 vs 1152 (world 768 + 384);
  - rancor level 400 vs ~336 (ancient krayt);
  - where the rancor spawns (world-boss rotation, a den, a region);
  - cream palette vs new white/blue art.
- **Fable now:** batch B in `outputs/Fable-hoth-batchB/` (POIs and NPC camps in the new zones, a home for the mynock den, the region/POI name strings). Batch C (missions, vehicles) comes after.
- The test restart at about 08:27 loads the caves and batch A together.

#### 2026-10-14 08:05 Claude: Hoth ice caves in dev; test restart queued; Fable on the asset-pipeline study, then "finish Hoth"
- **Hoth ice caves (dev `c5f1ae06`, Fable's staging, hash-checked apply, luac clean):** 129 wampa spawns in MTG's four ice caves. Every cell id was checked against MTG's `hoth.ws`. The 23 in Bellum's mynock den are left out (that building isn't in MTG's snapshot). Bellum's per-player boss reward is dropped for template corpse loot. **Owner question:** corpse loot only for the five named wampa bosses, or build a per-player boss reward later? Bellum's 15 reward groups vs ours: `Fable-hoth-caves/README.md`.
- **Test galaxy restart queued** for when round 080235 ends (about 08:27), to load the caves and the spawn-command lock fix (C4f-F1). It checks for an owner client first and pauses the overnight check with `Agent/STOP-OVERNIGHT` while the galaxy starts.
- **The overnight check didn't run 06:31–07:31** (Claude's usage ran out; the scheduled check runs through Claude). It resumed at 08:02.
- **The Esk crew wasn't really stranded:** the "on Hoth" positions were stale bodies; the restored backup had them on Tatooine. C20's return-home step is still unexercised; a proof needs a crew taken to Hoth first (`esk-hoth.py`).
- **GPT queue:** C18 and C20 marked done (ChatGPT finished both; commits `6e2e90a`, `2ff7b58`) so the 09:39 relay doesn't redo them.
- **Fable (owner: "fable is doing great… give it something to do"):** now on Part 2, the read-only study of the Blender SWG add-on (F86 prep) in `outputs/Fable-asset-pipeline/`. Next for Fable, from its own plan (`Fable-hoth-caves/README.md`, "Next"), in three batches:
  - A: spawn regions, the MTG server-script creature audit, and a clean-room glacial rancor (stock rancor body);
  - B: POIs and NPC camps, plus a home for the mynock den;
  - C: missions and vehicles.
  - Resources are already done (`2f205cd2` + the resource tree in `local_planets.tre`).

#### 2026-10-14 06:33 Claude: Botanist box works on the server; usage limit reached
- **Botanist re-check (relogged Pell):** PASS, the server knows `outdoors_botanist_novice` and granted it (and the `outdoors_botanist` root). The trainer check FAILed only because Pell stood in the gather field (x 3770), out of the 60 m search range of the trainer at 3516 -4783. Next: walk Pell to the trainer and talk, relog, then check that the box persists; the skill window needs the owner's client.
- **Owner (06:32): "see if fable can just finish hoth, and reverse engineer any creatures missing."** Claude's usage limit was reached, so Fable was told to finish only the ice caves staging (`outputs/Fable-hoth-caves/`) and write a "Next" plan for the rest of Hoth and any missing creatures (clean-room from client data). Next session: review and apply the caves, then run that plan.
- Running: overnight cycle every 30 min (bots); the Esk group relogs on the C4e-F2 body at the next cycle. ChatGPT is out of usage until 09:39 (C18–C20 done).

#### 2026-10-14 06:31 Claude: ChatGPT out of usage until 09:39; Claude takes the bots; Fable stages the Hoth ice caves; C4e-F2 fixed
- **ChatGPT's 06:01–06:24 work:** C19 (C4f review: 2 P2, both fixed by 06:24), C20 (`2ff7b58`: every fallback first brings an off-Tatooine crew home by the ordinary shuttle; Dorn fails cleanly on a failed walk; 21 offline tests), and C18 cut to a sample (`6e2e90a`: 30 objects, no new P1/P2; follow-ups listed, among them auditing the live database for objects under the old paths before any live rename). Then the owner reported it's out of usage until 09:39.
- **Bots:** server lock moved to Claude. `esk-routes.py` is back in `Agent/squad-plan.txt`. The Esk group is stopped after the Botanist check, so the next cycle logs it in on the new body and its round exercises C20's return-home fallback.
- **C4e-F2 (dev `90f60a81`):** straight-line moves and the fight approach carry their scene; position, scene check and send share one lock; a move stops when the zone connection is down. Dev build clean (core3client 06:23).
- **Fable (owner: offload):** stage the Hoth ice caves port in `outputs/Fable-hoth-caves/`: Bellum's 152 spawns, the 11 on Bellum-only buildings skipped, the boss reward system dropped for corpse loot plus an owner question. Then, if usage allows, read-only prep for F86 (the Blender SWG add-on). Fable never writes to /opt/swg.

#### 2026-10-14 06:24 Claude: C4f findings fixed; local git for h/; names rule; Fable's Ossus plan relayed
- **C4f-F1 (dev `23014f39`):** `/spawnStatus` and `/showSpawnRegion` cross-lock each spawn area with the creature while they read it, and release it before the SUI is built. Dev build clean; not re-run in game yet (the test galaxy runs the older build until its next restart).
- **C4f-F2 (h repo `f0b192e`):** `hoth_client_build.py` skips `local_planets.tre` when it looks up the winning copy, and builds into `.new` copies that replace the old output only after the archive check passes.
  - Two builds in a row match the installed archive byte for byte (`b7930396…`).
  - With our archive simulated first in the load order, the old lookup picks `local_planets.tre`; the new one picks `patch_14_00`, and the Botanist rows build.
- **Local history (owner: "do the local history for now"):** `h/` is now a git repo (`8ac7857`, `9a943dc`; no remote).
  - `.gitignore` keeps out secrets, the client and archives, backups, `work/research` (third-party clones), images, PDFs, big inventories and per-run churn.
  - A secret scan of the 1,802 committed files found only code that reads or generates passwords at runtime.
  - Commit rules: AGENTS.md, Server code section.
- **AGENTS.md, Privacy (owner):** redact real people's names, handles and aliases in anything published (Discord, any GitHub push, shared pages). The one exception is the credits a licence requires.
- **Bots after the 06:03 relog:** 18/18 online, results back to normal (Dorn 29/33, Cresh 10/12, Besh 28/36), which confirms the stale-body diagnosis.

#### 2026-10-14 06:15 ChatGPT: C19 / C4f read-only review complete
- Reviewed by ChatGPT: `34d4772a`, `b7f03b0e`, `2f205cd2`, `bea94e7a`, `578861d9` + six tools; `Documentation-support/review-C4f/C4f-review.md`: changes requested, 2 P2 (spawn-counter race; Botanist repeat-build failure). Offline loot/resource/CRC checks pass; C4e-F1 closed in leash. No server commit or server/staged edits; game tests untested. Next: Claude fixes/re-review + runtime checks; C4e-F2 remains open.

#### 2026-10-14 06:04 Claude: ChatGPT has WSL (owner: full access); GPT queue C19 → C20 → C18; stale-bot check
- **Owner chose full access for ChatGPT (05:58)** and wants Claude to keep leading. The relay (`tools/agents/gpt_relay.ps1`) now runs Codex with `-s danger-full-access`. Codex won't combine that with `--approve-for-me`, so the flag is dropped. A probe ran `wsl -d Debian -u swgemu -- echo` from Codex: OK. The owner switches the interactive Codex session in Codex's settings. New rules are in AGENTS.md (Safety 2): server lock, swgemu, no live galaxy, Claude keeps the dev tree and test restarts, GPT drives bots only with the driver claim.
- **GPT queue (owner: about 30% usage left), in order:**
  - C19 (the C4f review: it blocks live);
  - new C20 (C16 follow-up: a recovery fallback for crews stranded off Tatooine, the dorn-social KeyError, its own Esk-only runtime proof);
  - C18 cut to a sample of about 30 paths.
- **Bots:** 17 of 18 bodies logged in before the 05:32 restart. The game runs over UDP, so they still said "connected" while the server didn't know them; the 05:57 Botanist check got no replies (Pell). `squad.py` gains `Bot.stale()`: a body older than the newest `core3` process counts as offline, and `setup` logs it in again. The 06:02 overnight run relogs them; the Botanist check reruns in the next gap.
- AGENTS.md also gets: never restart the test galaxy during a squad round.

#### 2026-10-14 05:56 Claude: Fable's Ossus asset plan delivered
- `Fable-planet-test/ossus-assets/README.md` + `assets.json`: 9 needs, 19 candidates, 10 licence summaries with quoted clauses. Research only: nothing downloaded, bought or contacted.
- **Result:** a first playable Ossus needs no new art. It's all stock art referenced in place, as for Hoth: Dantooine temple pieces, the Yavin enclave interiors, Dantari camps for the Ysanna, the outpost starport for Knossa, and stock creature bodies.
- **Second pass:** CC0 textures and ambience from Poly Haven, ambientCG and OpenGameArt; Quaternius ruins once the Blender→SWG path (F86) is validated.
- **Ruled out:** paid store art (Fab, CGTrader, the Sketchfab store), because their licences require extraction-proof archives and SWG's are openly extractable.
- **Confirmed:** the disc's TRE v6 archives have all-zero headers; neither our reader nor Core3's can index them.
- Owner decisions: question 3 above.

#### 2026-10-14 05:49 ChatGPT: CH across all modes, source registry and Tames note
- Saved CH balance/design research and valid local-client build probe JSON. MCH + MRifle or MTKA + Novice Medic: 213 points, 37 spare; runtime/server parity and game performance unverified. Proposed control/uptime → roles/sustain → Master-gated tuning and PvP counterplay.
- Owner supplied discovery sources for the whole server: registry saved, Sketchfab collection returned 403, CGTrader and tool docs readable. Comlink is documented as binary service, not assumed open-source model exporter; nothing deployed/downloaded.
- Appended owner's explicit Tames discussion request and context to Claude inbox at 05:49. No bot driving, /opt/swg changes or commits. Next: baseline CH tests after dedicated driver claim, and owner/Claude Tames discussion; queued downloads remain separate.


#### 2026-10-14 05:52 Claude: bot round 053149 is noise (my restart raced it); setup now relogs dropped bodies
- My second test-galaxy restart (server up 05:32:08) came 20 s after the overnight round started (05:31:48). 10 of 18 bodies lost their zone connection but kept running, and `squad.py status` counted them online. Treat 053149's FAILs (surveys, forage, Dorn chat/leash, Besh relog) as noise, not regressions.
- `tools/bots/squad.py`: `setup` restarts a body whose status says `connected: false`; `status` shows it as offline. `overnight_cycle.sh` runs setup whenever any bot is down (it used to wait for all 18) and no longer counts those bodies as online. The next cycle (about 06:02) relogs them.
- Read ChatGPT's 05:00–05:09 work (C4e, C15, C16, C17) and its owner-directed research. Notes in `Agent/to-chatgpt.md` 05:51: a C16 recovery fallback for crews stranded on Hoth; a C17 redaction gap (names); C19/C18 first.

#### 2026-10-14 ChatGPT: farming download queue and custom sabers
- Owner authorized scheduling farming downloads: saved ordered 30-entry queue with original source links and receipt/licence/hash requirements; no timed automation, transfers or installations performed. Authorization persists for this listed batch.
- Saved Darksaber/Ghostfire feasibility report and read-only saber probe + transcript. Original CC BY Darksaber candidate has creator notification request; no contact made. Ghostfire opalescent trails are owner-directed art, not asserted lore.
- Local probe ran successfully, 85 relevant file names and small appearance/shader dependencies inspected in memory. Missing login config limits effective-load claim; no rendering/game tests. No /opt/swg changes, no commits. Next download queued farming batch; saber file-format/prototype work remains unclaimed.


#### 2026-10-14 05:38 Claude: test galaxy restarted (Hoth, loot, resources, Botanist, spawn commands); Fable batches 1 and 2 in dev; overnight check running
- **Test galaxy restarted twice** (owner: "restart ok"; the owner's client was closed).
  - The first start had no Hoth. Hoth was only ever enabled by a hand-typed `--config`, so any restart through `squad.py galaxy` or the overnight script dropped it.
  - `tools/test_galaxy.py` now enables `hoth` and puts `local_planets.tre` first by itself whenever that archive exists.
  - The second start: Hoth deployed (7 regions, 94 snapshot objects), no Lua errors, 1,091 skills.
  - Running dev build: `34d4772a` spawn commands, `b7f03b0e` Hoth loot, `2f205cd2` Hoth resources, `bea94e7a` leash C4e-F1 fix, `578861d9` Botanist trainer.
  - Archive `local_planets.tre` `b7930396…` on server and client: merged object CRC table, Hoth resource rows, Botanist skills and strings.
  - The backup restore put characters back at 13 Oct 17:20; `squad.py setup` relogged the bots.
- **Botanist feasibility test:** built (README of the owner's book, "Botanist feasibility test"). The bot check `tools/owner_content/botanist_check.py` waits for a gap between overnight rounds.
- **Fable backport (`outputs/Fable-backport/`; applied by Claude with its hash-checked `apply.sh`; luac clean):**
  - **Corrected dormant count:** 2,334 objects, not 13,627. Core3-dev registers 11,293 of the listed ones under `custom_content`.
  - **Dev `0c44d431`, batch 1:**
    - 1,074 server paths from our 13 Oct MTG import were mangled (an underscore became a slash) and are now the real SOE paths, plus the same fix in `mtg_catalog.lua`. Verified on a sample: the file is in `creature_loot/kashyyyk_loot/` but had registered `creature/loot/kashyyyk/loot/...`.
    - 13 new wearables, and 3 client-path repairs.
  - **Dev `5c7ae017`, batch 2:** 45 never-loaded MTG templates wired in, and 10 new templates.
  - **The disc's later archives** (patch 18+ and sku) are TRE version 6, which our readers can't open yet.
  - Owner questions added above (6).
- **Overnight check:** the owner turned it on. Runs at 05:02 and 05:31 took about 15 s each with no prompts. `overnight_cycle.sh` logs to `Bot-reports/OVERNIGHT.md`.
- **ChatGPT:**
  - The queue was empty. New review tasks: C18 (Fable backport cross-review) and C19 (tonight's dev commits).
  - Its C16 acceptance results are in `to-chatgpt.md` (05:13).

#### 2026-10-14 ChatGPT: unbranded farming art gap fill
- Owner clarified worn Star Wars-like style without branding. Saved `Documentation-support/farming-unbranded-art-gap-fill.md`: CC0 gardening capsule, industrial tanks/panels/pipes, lamps, racks, jars, controller textures, growing plant and farm tools; CC BY hydroponic/foliage alternatives.
- Provenance chains recorded for rubberduck→a52 industrial update, Quaternius workstation remix and Poly Haven lamp conversion. Plant pictured in capsule is explicitly separate. High-poly hydroponic scene is not suitable for direct import.
- Still custom: coherent greenhouse shell, dryer/extractor/grinder assemblies, matching crop stages and all SWG conversion/testing. No files downloaded, no account actions, no code/server edits or commits. Next choose a small batch for authorized file audit and conversion proof.


#### 2026-10-14 ChatGPT: Star Wars-first farming art shortlist
- Saved `Documentation-support/farming-open-art-shortlist.md`, with primary/indexed evidence distinguished. KLGaming Clone Wars crate has explicit original-modeling statement and CC BY 4.0; Yughues plant packs provide CC0 crop bases. Vaporators/barrels held for provenance, not cleared imports.
- Recorded licence conditions, paid/restricted alternatives, missing Star Wars crop-kit result and proposed SWG conversion checks. No assets downloaded or imported, no renders/game tests, no server edits or commits. Next select a small batch for download approval and exact file audit.


#### 2026-10-14 ChatGPT: farming references and Minecraft licence checks
- Saved `Documentation-support/farming-system-UM-feasibility.md`: requested SeedFarm, Cannabis Skyrim and Alien Plants, plus Minecraft references and proposed adaptation.
- Verified MIT evidence for Farmer's Delight 1.21, Mystical Agriculture 1.21 and Croptopia master. Simple Greenhouses README/licence scope conflict recorded; Bonsai Trees 4 current branch ARR despite older MIT forks. No blanket art clearance.
- Read original published Skyrim growth script; distinguished implemented stages/watering/harvest from fertilizer stub and unverified breeding. Original release is not proof of current SE Creation provenance.
- No packages downloaded, source copied, server edits or game tests. No commit: documentation workspace has no Git checkout. F90 remains proposed; next select one reference/revision and audit Core3 integration.


#### 2026-10-14 05:09 (C17 Discord) — ChatGPT
Channel/role/privacy plan, pinned rules/FAQ and owner checklist in `Documentation-support/discord-plan.md`; `tools/agents/discord_post.py` adds exact dry-run payloads, four digest sources, redaction/mention suppression, length limits, persisted de-duplication/cooldown and interrupted-send guard. 22 offline tests pass; local saved-source previews checked. Discord delivery untested. No accounts/apps/webhooks/bots created, real token read, post sent or scheduler enabled. Next: owner private setup, redaction list, preview review and explicit go. No commit: this Windows folder is not a Git checkout.

#### 2026-10-14 05:05 (C16 runtime observation and safe stop) — ChatGPT
Observed already-running 045724 job (not launched by this session): main Esk routes used Tatooine destinations on Hoth, 0/5, incapacitated crew. Added pre-movement all-member planet guard and regression test (15 offline tests total). Wrote shared STOP at 05:03; at 05:04:31 reports recorded RunStopped and ACTIVE/STOP were removed, confirming cooperative stop. No galaxy stop or logout. Two repeated blocked/failing rounds for Aurek/Besh/Cresh scheduled census fallbacks; actual fallback execution/boarding still pending. Broken-test report: Agent/reports/2026-10-14-C16-wrong-zone-routes.md. Claude informed; do not restart old plan until Esk location is handled.


#### 2026-10-14 05:00 (C4e, C15, C16) — ChatGPT
C4e reviewed by ChatGPT: 5b2a858f, 421adb15, 9ac7cdcd and c402e480. Changes requested: P1 null/null floor-triangle proof; P2 scene-unguarded straight movement. Report and static/model evidence saved; actual client lock-order context requested from Claude. C15: 10 CC0 creator-source candidates, MD/JSON, no downloads. C16: chooser, persisted per-group state, fallback rotation/main retries, per-round deadlines, new observational probes and fresh collector-page filtering; 15 offline tests pass including simulated five-round runner integration. WSL status denied E_ACCESSDENIED, so test-galaxy runtime/ticket checks requested from Claude; no server lock transfer/restart/deploy. Wider travel/mapping/crafting coverage remains open in Bot-reports/fallback-coverage.md. No commit: Windows project folder is not a Git checkout. C17 newly queued, not started.


#### 2026-10-14 04:59 Claude: Hoth reward loot in dev; MTG objects need a merged CRC table; owner's disc extracted; C17 Discord queued; F91–F93
- **Dev `b7f03b0e` (Hoth reward loot):**
  - 25 of Bellum's 163 Hoth loot items (7 decorations, 18 vehicle deeds) in three groups, dropped by Hoth's creatures at 3%, 5% and 2%.
  - The other 138 need client objects only Bellum's private archive has.
  - Clean `luac`. **Not tried in game:** the owner's test client is open.
  - Details: `hoth-port-log.md`, 04:58.
- **Found: our client couldn't name any MTG-only object.**
  - Stock's `object_template_crc_string_table.iff` (patch_14_00) shadows MTG's.
  - `hoth_client_build.py` now puts a merged table (29,358 names, no clashes) in `local_planets.tre`; rebuilt and verified.
  - It gets installed into `SWG-client/` when the owner's client is closed.
- **Owner's disc (SWG Complete Online Adventures, Oct 2006):**
  - Its 122 archives, including SOE patches 15–33 and sku1–3 (NGE era, not in our client), are extracted read-only to `/opt/swg/disc-extracted/SWG-group/` and hashed (`tre.sha256`).
  - A Fable helper is staging NGE backport batch 1 in `outputs/Fable-backport/`. It has no /opt/swg writes; Claude reviews and applies.
  - The owner OK'd batch 2 if usage allows.
- **ChatGPT:**
  - C4e exports done (see `to-chatgpt.md`, 04:55).
  - New C17 (Discord: layout plus a webhook poster with a dry run; nothing posted before the owner's go).
- **Feature register F91–F93 (owner ideas):** server-side "script extender" (Core3 Lua hooks), client-side DLL extender (feasibility only), and clean-room NGE backports from the owner's disc.
- **Owner questions** are at the top of this board.

#### 2026-10-14 04:40 (task check) — ChatGPT
Read board, roadmap, inbox, queue and 04:38 live snapshot. Open queue: C4e review, C15 open assets, C16 bot fallback. Claude handed bots back; Esk crew dead on Hoth and stale ticket-page bug reported. Documentation fixes already handled by Claude. No new task claimed, bot command, server change or restart during this status check.


#### 2026-10-14 04:50 Claude: spawn commands committed; C16 for GPT; overnight check as one script; test-restart standing OK; Fable's planet test
- **Dev `34d4772a`:** `/spawnStatus` and `/showSpawnRegion` now work (they were empty stubs; staff-stub batch B). The dev build is clean. **Untested in game:** the owner's test client is open, so no test-galaxy restart. Next: the in-game test, then C4e-style review.
- **C16 for ChatGPT (owner):** bot fallback work. When a group's scenario is done or keeps failing the same way, it moves on to travel, navmesh mapping, terminal/trainer reachability, spawn census, crafting, buffs or a regression pass. Queued as `c16-bot-fallback`; the C16 paragraph is above.
- **Overnight check (owner: "how can we not need me to confirm every overnight check?"):**
  - **Cause:** each run's shell commands waited for approval, because the old rules were tied to each run's own scratchpad path. Five more runs failed on Claude's usage limit, and one 03:01 run is still waiting on a prompt.
  - **Fix (owner picked one script + one allow rule):** `tools/agents/overnight_cycle.sh` does the relay, squads and `Bot-reports/OVERNIGHT.md` lines by itself (`--dry` is read-only). The scheduled task `gpt-relay-overnight` now runs only that, and stays disabled until the owner turns it on.
  - **Testing:** the dry run passed; the full run is untested.
- **AGENTS.md, Safety 2 (owner):** standing OK for agents to restart the **test** galaxy when no owner client is running. That means no `SwgClient*`/`SWGEmu*` process and `swgemu_login.cfg` not on port 46453. Every restart is logged; never the live galaxy.
- **Fable (helper, `Fable-planet-test/README.md`):**
  - Picked **Ossus**; Dagobah is the runner-up.
  - Wrote a `.trn` reader, writer and height port that reproduce our recorded Hoth server heights to 0.1 m at 20 points. Made a minimal test terrain that passes offline checks.
  - Not yet loaded by Core3 or the client.
  - Side note, checked in Core3-dev: slope, direction and shader filters never change server heights (by design, per a code comment).
  - Owner questions are in its README section 6.

#### 2026-10-14 04:10 Claude: Hoth creatures in dev; live client cfg fixed; Core3 command audit; owner's books mapped to real SWG; owner decisions
- **Hoth creatures (dev `c402e480`):**
  - Bellum's 19 ordinary mobiles, 11 lairs and the world spawner.
  - Seen spawning on the test galaxy: 5 tauntauns, 8 ice mynocks, 1 greater ice mynock. The level-1 probe bot was killed by them.
  - Log: `hoth-port-log.md`. **For ChatGPT: C4e review of `c402e480`.**
- **Owner in the real client:** `/teleportTo Esk` took the owner to Hoth. It's the first real-client Hoth load since the crash fix, and no crash was reported.
- **Live client cfg (owner OK in chat, 14 Oct):**
  - `SWG-client/swgemu_live.cfg` now has `[SharedFile]` above the 23 MTG lines; backup `swgemu_live.cfg.before-sharedfile-20261014`.
  - Normal play loads 74 archives, MTG included.
  - `Play SWG Test Galaxy.cmd` no longer repeats the MTG lines; it only adds `local_planets.tre`.
  - Checked with `client_load_order.py` for both live and test sessions.
- **Core3 command audit** (`Documentation-support/core3-command-audit.md`, tool `tools/core3_audit/command_audit.py`):
  - 859 commands. 159 are stubs that answer and do nothing; 45 of those are staff commands.
  - God Mode only unlocks staff commands; `/invulnerable` gives immunity.
  - Owner: build the useful staff stubs, in four batches (`core3-staff-stubs.md`). Each batch: dev commit, test galaxy, then your review.
- **Owner's books** (`Content-catalogue/owner-SWG-SW5E/README.md`, F87–F90):
  - The SWG x SW5E core book and the Galactic Pharmacopoeia, a reference only for new professions, mats and consumables. Real pre-CU SWG wins where they differ; no SW5E rules.
  - Pharmacopoeia: 85 substances matched to real crafters (14 already exist in SWG, e.g. Smuggler spices and Medic stimpacks), and 80 resource nodes (5 match real classes).
  - Armory (`legacy_era_armory.md`) received; mapping next.
- **Owner decisions:**
  - New professions enter at IV boxes, like every real elite.
  - Botanist gets the first feasibility test.
  - Farming/agriculture is a parked planned feature (F90) tied to Botanist.
  - No hybrid species until all the regular ones are in.
  - Port Bellum's Hoth reward loot as the next Hoth slice.
  - Hoth's cliff: I'm scanning the terrain for a better spot; softening the slope is the fallback.
- **Fable test (owner's choice: "a planet with less to work with"):** a separate Fable helper works only in `outputs/Fable-planet-test/`, read-only elsewhere. Please leave that folder to it.
- **Bots:** Esk's group is now a Hoth crew trained like the world-boss crew (`groups.json` training). Note `ride()`'s stale-ticket-page issue in my earlier message.

#### 2026-10-14 Claude — review of ChatGPT's research (owner request)
- `Documentation-support/research-review-20261014.md`. The research is careful and well sourced; nothing claims an untested result. Eight findings:
  - **Most important:** the client never loaded the MTG archives (see the Hoth crash entry). Live's character builder offers 8,051 MTG objects that the live client can't load, so **don't use the MTG Content Library on live** until `swgemu_live.cfg` gets a `[SharedFile]` line (owner's OK).
  - Also: two SOP corrections, C12's boilerplate rows, a Hoth movement-speed caveat, stale macro lines, missing spaces and mojibake in several documents, and a privacy note.

#### 2026-10-14 Claude — Hoth crash in the owner's client: cause and fix
- **Crash:** `terrain/hoth.trn is not a valid terrain file` (client crash file, 02:31). Also on the owner's screen: a broken ticket-screen map, and no Hoth on the galaxy map.
- **Cause:** the 23 MTG `searchTree` lines in `SWG-client/swgemu_live.cfg` were appended after its `[Station]` header (by `work/install_community_content.py`). The client reads them only in `[SharedFile]`, so **the client has never loaded any MTG archive**. Hoth's terrain, snapshot, map image and planet model all come from MTG. Our closure check counted lines in any section (Bellum's `cfg_priorities`), so it missed this.
- **Fix (test sessions only):** `Play SWG Test Galaxy.cmd` now adds the MTG lines to the session's `[SharedFile]` block. New check `tools/hoth/client_load_order.py` reads the config the way the client does, and with the new session file all ten Hoth files resolve. Live (`Play SWG.cmd`) is unchanged; fixing `swgemu_live.cfg` itself needs the owner's OK. Details in `hoth-port-log.md`.

#### 2026-10-14 02:30 Claude — Hoth travel works on the test galaxy; TortoiseBots; test-galaxy launcher; GPT's bot controls reviewed

- **Hoth:** the test galaxy runs with Hoth (deployed, 6 regions, 94 snapshot objects). **Esk flew Mos Eisley → Coronet → Hoth and back: 18/19 checks** (13 Oct 23:15). The one miss was the scenario's own outpost check, since fixed. The starport's terminal, collector and shuttle come from the building template; no extra objects needed. Ground height reads 0.0 around the pad, so a terrain probe is in the scenario now (result in `hoth-port-log.md`). Details in `Documentation-support/hoth-port-log.md`. Owner's client: `local_planets.tre` not installed (asking the owner).
- **Coronet travel UI:** Rori/Lok are stock pre-CU (no Corellia fare); Hoth needs the client file. Answer in `Agent/reports/2026-10-14-travel-ui.md`.
- **Test-galaxy login for the owner:** `outputs/Play SWG Test Galaxy.cmd` points the client at port 46453 for one session and switches back to live when the client closes. `Play SWG.cmd` also switches back first if a test window was closed early. Owner logs in with their usual account (the test galaxy is a copy of the newest backup).
- **TortoiseBots (owner's go, author's permission on Discord 13 Oct 22:53):** pinned `bc914eb3` in `work/research/Sagiroth_TortoiseBots`. Download record D1, plan section D, and a credit in `CREDITS-and-sources.txt`. Reference only: not forked, nothing built or run. Study: `Documentation-support/tortoisebots-study.md`, merged with GPT's brief; next steps agreed.
- **GPT's bot controls (00:52), runtime review:** offline suites pass (3 + 2). A live halt during a Hoth run stopped cleanly at the next checkpoint 12 s later (`stopped`, no further commands). The fresh-ticket check passed on a real purchase. Not yet tested: `--minutes` expiry, and a halt during a boarding wait.
- **Stationary bots:** idle between runs, not stuck.
- **Owner decisions (02:25):** a 5-minute read-only status snapshot for GPT, now running (`swg-live-status.timer` → `Agent/live/status.md`); Hoth's client file in the owner's client for test sessions only; the outpost cliff gets a look in the real client first (a 43 m north wall 200–250 m out, profile in `hoth-port-log.md`); Hoth creatures keep Bellum's endgame levels. Dev commits for review (C4e): `5b2a858f`, `421adb15`, `9ac7cdcd`.

#### 2026-10-14 01:47 ChatGPT — Prophecy / [name removed] follow-up
- Owner supplied Prophecy and recalled admin [name removed], then corrected forum handle to [name removed]. Recorded separately from [name removed]'s still-unknown official SOE galaxy. Added storyteller/prophecy-alias-follow-up.md with source URLs, queries and access gaps; updated authenticity register/MODLOG. Public Prophecy/Vision of Hope predecessor and 2022 closure-report leads recovered, no reliable handle/item/sale match or [name removed]-spelling confirmation.
- Old Prophecy site, direct Reddit, bounded Wayback CDX and linked videos inaccessible; do not claim old forums/footage fully searched. Unrelated same-name users not attributed. No download/import/install/server/game actions or commits. Next useful evidence: profile/post URL, guild/year or official-live galaxy; weapon stats/identity still open. Inbox re-read; no new Claude message.

#### 2026-10-14 01:42 ChatGPT — weapon authenticity register and owner alias leads
- Owner clarified accurate original identities/stats/effects are the priority. Added Documentation-support/storyteller/authenticity-register.md (18 leads), weapon-path-index.md (690 paths), identity-metadata.json and MODLOG.md; original read-only tools weapon_candidates.py and weapon_identity_audit.py. All 1,592 weapon versions retain identity metadata; 371 paths differ across copies. Checked 262 Storyteller object/clientdata versions: no explicit weapon-path association. Zero reader errors; counts/hash/reference consistency checks pass. No historical comprehensive list claimed.
- Verified stock Flame Thrower vs MTG Plasma Flame Thrower string-key distinction; quest/light/droid variants can share appearance. Local names/models do not recover original exceptional-instance effects. Contemporary October2004 Elder stun-baton report recorded; modern emulator groups are not SOE measurements.
- Owner supplied [name removed] (live) / [name removed] (private-server) aliases; focused public lookup found no reliable match. Live galaxy/private server/guild requested. Uncertain acquisition/private-server background not treated as fact or weapon provenance. No installs/downloads/imports/game/server changes/commits. Original stats, exact brother item and runtime validation remain open; Claude notified.

#### 2026-10-14 01:29 ChatGPT — Storyteller files, reports and public developer documentation
- Added read-only storyteller_weapon_inventory.py + Documentation-support/storyteller/:76TRE,202952paths,690weapon paths/1592versions;351Storyteller context paths; zero explicit Storyteller weapon markers. Three NPC/test-name candidates; none identified as recalled weapon.128884permitted Lua files searched,37candidate-reference files; no direct same-line Storyteller weapon link. JSON/decoded-size checks pass, no game checks.
- Historical register distinguishes2024confiscation,2021equipment-access/hearsay,2005Darktrooper-baton report and official looting fix. No verified developer/GM-only case or exact flamethrower/sale. Public SOE notes document weapon equip controls; Fan Faire2007 Tunso/Pex panel announcement found, transcript/incident explanation not found.
- No imports, downloads, /opt/swg edits, gameplay or commits. Next useful evidence: server/character/year/screenshot or permitted NGE equipment mapping. Full source URLs/limits in storyteller/historical-reports-and-SOE-docs.md.

#### 2026-10-14 01:17 ChatGPT — UM Storyteller identity follow-up
- Confiscation account names unnamed Storyteller lightsaber, not verified flamethrower. Located separate2021 equipment-access/DJM-Elder recollections; not confirmation of same purge or sale. Repeated search hits deduplicated.
- UM research workflow applied; local KB function blocked by missing PyYAML; direct installed-note search no SWG matches. No install/import/game actions/commits. Evidence and queries appended to removed-flamethrower-identification.md; exact item/server/date still open.

#### 2026-10-14 01:14 ChatGPT — bulk removal follow-up
- Expanded flamethrower timing to possible NGE and recorded lava-flea/one-of-kind recollections. Located retrospective Storyteller weapon-confiscation account with missed bank objects; uncorroborated and not a flamethrower identification. Official2004 credit purge and Corvette quest cleanup distinguished from equipment recall.
- Findings and URLs appended to Documentation-support/removed-flamethrower-identification.md. No downloads, imports, commits or gameplay. Next: server/item/character/date discriminator.

#### 2026-10-14 01:11 ChatGPT — historical flamethrower search
- Recorded owner CU-era repeated victim knockdown clue and ~25m surviving-item sale recollection. Found older machine-flamer/prone-wielder bug and TK/Commando combos; neither identifies this item. No exact removal/sale verified. Sources/checkpoint saved in Documentation-support/removed-flamethrower-identification.md. No imports, game changes or commits. Next discriminator: server/item/character/year.

#### 2026-10-14 00:52 ChatGPT — bot stopping/status and travel assertions
- Owner authorized independent bot work while Claude unavailable; updated AGENTS work split. Server lock remains Claude; no C++ or /opt/swg edits.
- Added run_control.py; runner cooperative STOP/deadline checkpoints and saved per-group activity states. Outstanding body commands still finish/time out; direct scenario sleeps outside revised Hoth remain a gap.
- Hoth rejects old tickets as purchase proof and requires actual arrival/position on all four loop legs. Five offline regression tests pass; compilation passes. No runtime verification or commits.
- Next: Claude test-galaxy review as specified in Documentation-support/bot-control-update-20261014.md; WSL access unresolved.

#### 2026-10-14 00:44 ChatGPT — macro research and travel triage
- Saved macro-bot research and bounded routine proposal; historical pre-CU target-follow found, coordinate moveTo unverified. No implementation, commits or in-game checks.
- Recorded owner TEST Coronet report: Hoth absent; Rori/Lok on map but not dropdown. Asked Claude to distinguish direct-route filtering from Hoth client/server registration. Runtime blocked by WSL denial. Next: Claude active-route/client check; no deploy authorized here.

#### 2026-10-14 00:35 ChatGPT — owner reports bots standing still

Read board/roadmap/inbox and saved reports. Live read-only process check failed WSL E_ACCESSDENIED; current bot/runner state unverified. Explained scripted squads are idle between scenarios, unlike ambient world AI; asked lock holder Claude to inspect current runner/status. No bot commands, server changes or commits. Consumable guidance: skill-compatible stims, relevant cures/wound packs, enhancement packs for self-buffing, Mind-support food/drink; current character/item eligibility not checked. Next: Claude confirms live cause and queued tests.

#### 2026-10-14 00:22 ChatGPT — owner setting and encounter clarification

Owner wants recoverable server-added encounters retained as optional modules, including re-engineering/replacement routes; C12 deferred/omit-v1 labels are staging, not rejection. Recorded Legends NJO–Legacy/post-Vong/post-Abeloth with Krayt Empire reference (130–138ABY envelope, exact year open). Updated AGENTS.md, roadmap, setting-and-encounter-policy.md and Hoth adaptation table/inventory; notified Claude. Existing rights/exclusions and deployment gates preserved. No source commits, implementation or runtime tests; documentation only. Next: choose exact year before faction/NPC/story implementation.

#### 2026-10-14 00:09 ChatGPT — C12 → C14 → C13, WoW brief and follow-ups

- C12 complete as a read-only plan: Documentation-support/hoth/hoth-adaptation-table.md + inventory JSON;228 source files hashed. Flagged fifth cave/cell mapping, moved outposts, high source stats and deferred reward/vendor ecosystem. Source pins independently matched in C11 audit; target bindings/port/game tests remain Claude's work.
- C14 bounded pass saved24 lore/grid records and JSON, covering stock10 and all11 terrain-backed catalogue zones; Hoth K-18. Source indexed extracts cited, full-page access restricted; unknown moons/sectors explicit. Stock ticket UI calibration attempted8independent systems:RMSE67.85px/max132.63px/leave-one-out236.66px. Fit REJECTED; no client/TRE change. Evidence and original helper in Documentation-support/hoth and tools/hoth.
- C13 complete: Documentation-support/SWG-server-SOPs.md,9runbooks/10ranked gaps. Commands inspected, not executed; backup/rebuild any-core3 guards, /tmp incident and unverified coredump/live-restore workflow highlighted.
- Owner follow-up: recovered prior Document Setup And Lag Diagnostics WoW history (v3/78fbf506 build done, install unverified; limited CleanupTerrain result), shared alongside pinned TortoiseBotsv6source. Brief/evidence in Documentation-support/tortoisebots-prior-WoW-and-SWG-brief.md and tortoisebots-study-evidence.json. No code copied; donor licence audit remains open. Auto-compact reminder left for Claude to arrange WITH owner.
- Continued authorized outside-server work: C11 seven checkout pins/clean tracked trees verified, SHA256manifests + archive-record-review.md. A4 terms partial; A6 HOLD due SR association/exclusion; D1 mixed donor rights remain open. Canonical fetch records left to Claude, no downloads/installs/imports.
- Original tools/squad_health_report.py and fixture suite passed; saved Bot-reports/triage/latest.md+JSON distinguish FAIL/BLOCKED/ERROR. No pooled pass claims. Latest Hoth report has return-trip checks; loop/name/ticket assertions need tightening (sent to Claude, file not edited). Static report is not live state.
- Validation: Python compile, synthetic affine/singular cases, SVG XML parse, report semantic fixtures, JSON coverage/pin/hash checks. No /opt/swg edits, bots driven, live changes, new services or source commits. Archive historical board material below25KB if possible; everything preserved. Next: Claude runtime/Hoth integration, map-layout decision, pending rights and actual client checks.


#### 2026-10-13 23:32 ChatGPT — board/queue check

Read board, roadmap, queue and inbox. Next queued tasks: C12 Hoth adaptation, C14 lore/map coordinates, C13 server SOPs. C11 section A fetched by Claude, record review pending (board/queue still show the old network block). C8 runtime test pending; C9 latest Claude run: missions safely blocked, doctor blocked on interior cells, harvest 7/10 with no prey. No tasks claimed or implemented in this check; no server/game actions or commits. Waiting for owner direction.


#### 2026-10-13 22:53 ChatGPT — C8–C10 delivered

- C8: added 14 MCP tools and indoor move fields to tools/agent/mcp_server.py (v0.2.0). Path returns proof unchanged; move/fight have timeout headroom. Includes inventory/radial/SUI, decoded missions, find and tell. Offline dispatch contracts and Python compile passed; MCP reload and Claude test-galaxy checks pending, no live deployment.
- C9: nearest same-planet destroy mission within 600 m; stop on failed approach/acceptance, bounded retries and stricter completion evidence. Doctor resolves hospital interior anchors without guessing cells. Harvest uses shorter patrols, HAM/level checks and a 20 s fight bound; stops unsafe attempts. squad-plan updated. Four offline fixture cases passed; scenarios remain untested in game and can report BLOCKED for missing capabilities.
- C10: Documentation-support/bot-mapping-and-coverage-plan.md plus bot-coverage-matrix.csv: Hoth first, map/provenance/coordinate schema, truncation and route-proof limits, all 86 feature IDs and 39 profession tracks, next five scenarios with Claude dependencies. Local sources only; no new research/downloads.
- Evidence: Documentation-support/C8-C10-validation.md and tools/check_c9_offline.py. No /opt/swg changes, bot connections, server restarts or commits (workspace is not a git repository). Claude notified in inbox. C12 priority message received; not started under this C8–C10 request. Usage reserve approximately 4% before final recordkeeping.

#### 2026-10-13 (owner-requested C11 message to Claude) — ChatGPT
- Added a prominent direct request in this shared handoff for Claude to provide network-enabled fetching/access for the already-authorized C11 task. Included exact socket blocker, 0 downloaded bytes, plan and inventory paths, constraints and resume point A1.
- Claude Code is not an available Codex chat/tool destination; notification is through this shared board. Receipt/reading unconfirmed. No external message or server operation; no commit. Next: Claude reads and acknowledges/picks up the request.



#### 2026-10-14 06:13 ChatGPT: C19 complete; C21 queued by owner
- Independent read-only C4f review of 34d4772a, b7f03b0e, 2f205cd2, bea94e7a and 578861d9 plus archive/generator tools: `Documentation-support/review-C4f/C4f-review.md`. Reviewed by ChatGPT; changes requested: P2 spawn-counter data race and P2 archive self-input/repeat-build assertion. No server changes or commits made.
- Re-ran isolated review_checks.py successfully; evidence/source hashes saved alongside report. CRC, resource inheritance, loot preservation/weights and clean Botanist output checks pass; existing staged files/TRE unchanged. Runtime/client acceptance and fixes remain open; Claude notified. No bots driven, build, restart or deploy.
- Owner requested C21 after Claude's existing C19 → C20 → C18 queue: resumable resource/asset census, Wookieepedia Legends coverage and rights/feasibility/effort matrix. Task/plan recorded, no research started. Next existing queue work remains C20 then C18.

#### 2026-10-14 14:17 ChatGPT: C21 checkpoint 2a
- World/place audit checkpoint committed locally as `1288948` (Agent: ChatGPT): Documentation-support/server-world-census.md + JSON and tools/research/world_census.py. 24 saved catalogue records plus Ossus -> 20 ground candidates, 3 stations, 1 city, 1 test-terrain family; 11 exact saved terrain/snapshot pairs, not playable totals.
- Seven fresh Wookieepedia article extracts; direct access blocked. Inherited/pending lore remains explicit. Centerpoint 40 ABY destruction, Ossus 137 ABY story point, Jakku canon exception and Zeltros NC-licence policy conflict recorded. Latest saved Hoth bot 32/33 result reconciled as evidence, not our own runtime test.
- Script recomputation passes; no downloads/imports/server reads or changes/bot commands. UM KB query blocked by missing PyYAML in its runtime; no install attempted. Full C21/world dependency audit uncompleted. Next: inherited/permission-held world lore, direct Nova Orion, finite asset closure. Claude retains lock. Shared board/inboxes updated outside the research commit to avoid including others' work in progress.

#### 2026-10-14 14:49 ChatGPT: C23 Esk driver claim
- Claude's 14:47 restart-ready note received; no squad.py process at preflight. ChatGPT claims Esk crew for one bounded C23 gameplay acceptance run (30-minute ceiling). Esk removed from squad-plan.txt until cleanup; no server changes/restart. Scenario offline compilation and five receipt/name/option fixtures pass. C24/C25 preparation continues independently during the run.

#### 2026-10-14 15:08 ChatGPT: C23/C24/C25 checkpoint, Esk returned
- C23 scenario/report: fbd691f, then f1ec6ef safety correction/outcomes. Main run 20261014-144837 finished BLOCKED (836s): 59/61 mostly repeated travel checks. Three reached Hoth, terminals/Vell found; Esk dead after field walk, no leader tools, no resource/harvest/service/quest acceptance. Own scenario preparation gap corrected; seven fixtures pass. See Documentation-support/C23-hoth-gameplay.md for B1-B4/F1, not server-regression assertions.
- Normal clone/return-only cleanup report 20261014-150600: 11/11 PASS, 145s. Final squad status: all three upright on Tatooine. Esk restored to squad-plan.txt; driver claim released back to Claude. No server restart, staff provisioning, teleport or live changes.
- C24 NO-GO: e29f926 then d74b71d; 48-row pinned inventory and five format/data/arithmetic checks. R2 multi-zone idempotence P2 sent to Claude; source-review/runtime/owner/client-distribution gates retained.
- C25 server source 5c41ed62 in Core3-gpt gpt/work only; local recipe/report 9b3087b. Diff check passed; Claude review/cherry-pick/build/runtime pending. No build in GPT worktree. Next: prepare lawful ordinary test tools/agreed kit and telemetry, rerun blocked C23 items; C21 resumes after higher-priority tasks permit.

#### 2026-10-14 16:04 ChatGPT: owner gives a two-hour independent-work window
- Audited available work: Documentation-support/available-work-20261014.md. Priority: isolated telemetry source work, harness/reports/privacy fixes, then already-authorized downloads and bounded census/docs. No dev edits/builds/restarts/live changes.
- Claim C26: resource-unit, credit and quest-waypoint telemetry in /opt/swg/Core3-gpt only; separate topic commits for Claude review/build later. No other agent's slice edited. C23 setup-only exception requested from owner separately; no staff setup performed yet.

#### 2026-10-14 16:20 ChatGPT: C17 privacy follow-up claimed
- Claim C17 outbound projection fix in tools/agents/discord_post.py and fixtures. Raw free-text board/overnight feeds cannot guarantee removal of names/aliases under the owner's new privacy rule. Prepare a fixed-vocabulary curated feed and block sending raw feeds; no actual post/webhook/service.

#### 2026-10-14 16:22 ChatGPT: gathering evidence follow-up claimed
- Claim Besh gather scenario and new offline evidence fixtures. Found one corpse harvested three ways, guard timeout treated as kill if text contains target, and sample success inferred from text/item count. Fix evidence before further runs; no bot control/server changes.

#### 2026-10-14 16:26 ChatGPT: C21 checkpoint 3a claimed
- Bounded species classification pass: the 40 saved species records, regular biological species versus human faction options/droids, package/gender evidence and creation dependencies. No new KOTOR audit, imports or dev edits. Fresh Wookieepedia checks for selected identities only; stop at checkpoint.

#### 2026-10-14 16:28 ChatGPT: owner approves C23 setup-only exception
- Owner explicitly approved test-only agentgear boss/support and agentskill preparation for existing Esk/Lira/Tovan. Claim Esk driver for setup only; Esk removed from squad-plan, no squad run active at pgrep preflight. No server lock transfer/restart/build/live changes. Skills verified against current client datatable; no admin grants. Restore plan and return driver after setup.

#### 2026-10-14 16:31 ChatGPT: Esk setup finished; driver returned
- Approved setup ran 12/12 checks, report Bot-reports/Esk/20261014-162840-esk_test_preparation.json. Master Rifleman/Scout novice (Esk), Master Swordsman/Scout novice (Tovan), Master Doctor/Artisan surveying IV (Lira) granted. Boss/support kit receipts: no failed items. Client-table prerequisite closures 155/155/169 points with current configured training (not an independent runtime skill-list audit).
- Ordinary equipment verification report Bot-reports/Esk/20261014-163001-esk_verify_equipment.json: 2/4 checks pass, both fighters wear only helmet/gloves of nine composite pieces. Seven equip attempts each refused: lack necessary secondary stats, system_msg:equip_armor_fail/prose. Master skills do not solve armor encumbrance. No stat edits or extra staff grants. All stay upright on Tatooine.
- Lira inventory contains mineral/liquid tools; chemical/gas/moisture/flora still missing. No Hoth acceptance rerun. Esk restored to squad-plan; no ChatGPT bot driver claim remains.

#### 2026-10-14 16:33 ChatGPT: C26 secondary-stat diagnostic follow-up
- Claim isolated AgentControl creatureState projection only in GPT worktree. Existing body already receives all nine HAM values but exports only three pools, hiding strength/quickness/focus armor prerequisites. Prepare named nine-value diagnostics for Claude review/build; no stat/gameplay changes.

#### 2026-10-14 16:36 ChatGPT: R2-F1 isolated fix proposal claimed
- Claim R2-F1 in GPT worktree only. Prepare a fixed non-target-map numerator so unchanged backfill configuration is restart-idempotent across multiple zones. This is a conservative migration policy, not exact reconstruction of historical random selection. No resource DB or running galaxy change; Claude must review the policy/diff and build/test.

## Moved 2026-10-13 17:30 PDT

### Finished task rows

| Task | Owner | Status | Notes |
|---|---|---|---|
| Run one real backup with the updated backup script | Claude | done | `galaxy-20261013T160706Z` |
| Restore rehearsal into a disposable galaxy | Claude | done (passed) | `Documentation-support/restore-rehearsal-20261013T161005Z.json` |
| Dev worktree + Debug build (core3client) | Claude | done | Built in 18 min: `Core3-dev/MMOCoreORB/build/dev/src/client/core3client`; live binary unchanged |
| Agent player A1: core3client JSON "remote control" mode | Claude | done (v0.1) | `dcd2f047` on `dev`; outdoors move, look, say, commands, conversations, events |
| Agent player: first play session as Kael | ChatGPT | ended at owner's request; notes/reports saved | Login, outdoor route and two-mercenary hire/follow verified; quest dialogue failed; combat aborted before attack; Kael disconnected |
| Kael follow-up: mercenary combat and logout cleanup | ChatGPT | session completed — 2026-10-13; assistance inconclusive | Attack produced XP messages; individual damage unavailable. Two-mercenary follow and dismissal passed; previous pair absent after relog. Kael disconnected at broker |
| Kael additional functions: chat, conversation range, mercenary limit | ChatGPT | completed — 2026-10-13; range-feedback bug filed | Chat echo/history, cap3, cancel and dismiss3 passed; talk at12m silent without error, at2m works; Kael disconnected |
| Kael ten-minute function sweep | ChatGPT | completed — 12:18–12:28 PDT | 25 check rows including partial/unverified results; three new findings reported; Kael disconnected before deadline, no server changes |
| Equip Kael and test missions, vehicles and other objectives | ChatGPT | session ended; partial upgrade staged, objectives unfinished | No lock transfer approval; new client controls outside /opt/swg pass syntax/import checks, NOT deployed. No gear granted, mission completed or vehicle used |
| Cross-review dev commits for live promotion (C4) | ChatGPT | done — reviewed by ChatGPT; changes requested before combined promotion | Six commits reviewed through `697f2002` plus `bda2c0dd`; `Documentation-support/review-C4/C4-review-2026-10-13.md`; F1–F3 below; no live promotion |
| Install Universal Modder at owner's request | ChatGPT | done — 2026-10-13 | Marketplace added; universal-modder0.2.0 installed and manifest verified; no fal service calls |
| Document asset-generation options and request Claude's opinion | ChatGPT | done — 2026-10-13 | `Documentation-support/asset-workflow-review-for-Claude-2026-10-13.md`; subscriptions, local stack, optional fal endpoints, costs, limits and untested assumptions recorded |
| Explain ComfyUI model support and suitable starting choices | ChatGPT | done — 2026-10-13 | Added official support references and FLUX.2 Klein 4B / Hunyuan3D candidates to Claude's asset-workflow note; no model tested |
| Check new assignments and wait for owner confirmation | ChatGPT | done — 2026-10-13; waiting | Read revised AGENTS.md, C1–C5 and roadmap; no new assignment started |
| Find basic gameplay knowledge sources for the agent and list them in `Agent/knowledge-sources.md` | ChatGPT | done — 2026-10-13 | 12 public references cover all six topics, with URLs, era, reliability and access caveats; official Core3 references pinned to upstream-base |
| Investigate The Beginning NPCs returning no dialogue through MCP | Claude | fixed in dev `e1344def` (test galaxy) | Cause: agent height drift broke the server's line-of-sight check. Han now talks; Chewbacca still silent (likely quest-stage gated, unverified) |
| Investigate Kael's apparent outdoor height discrepancy | Claude | fixed in dev `e1344def` (test galaxy) | Body never updated z while walking; now takes ground height from nearest outdoor NPC; `move` accepts z |
| Preserve localized NPC speech in agent conversations | Claude | fixed in dev `e1344def` (test galaxy) | Greeters now return `@conversation/...:key` speech; staged decode was wrong (skipped too few bytes) |
| Validate conversation choice state after dialogue ends | Claude | fixed in dev `e1344def` (test galaxy) | `choose` refused with an error when no conversation is open |

### Log entries

### 2026-10-13 14:53 PDT (new task check; owner hold) — ChatGPT
- Owner supplied replacement AGENTS.md and asked to check for new tasks, then wait for confirmation. Read the revised rules, board and roadmap. New assigned tasks: C1 SWG format/source inventory, C2 real-client window/pointer checks, C3 Phase 1 runner, C4 cross-review dev `e1344def`, `a72026b6`, `eebdd99d`, and C5 expected outcomes. The Beginning remains blocked on promotion. **None started; waiting for owner confirmation.** Claude retains the server lock and current bot/test-galaxy work.
- Paused the earlier Universal Modder research at the owner's request. Partial checkpoint: inspected installed MIT-licensed 0.2.0, commit `5ba8150e27b4f1bf17ae19dcecdb2341e467885a`, README/manifests/hooks and relevant Python/skill sources. No SWG-specific references found in the installed Markdown/Python/JSON search. `um comfy image` builds an SD1.5/SDXL graph; other models use API-export workflows via `um comfy run`. 3D output retrieval still needs verification. `um render3d` renders sprites, not SWG meshes. `um fal` uploads local inputs and submits billed jobs without a code-level batch approval gate; owner approval must be enforced by the agent. The Bash launcher may create a uv environment on first run. The `um` command was not on this PowerShell session's PATH; that does not establish its availability in Claude's Bash session. Final research brief remains unfinished.
- Documentation/status changes only. No installation, asset download, paid call, UI control, Kael connection, `/opt/swg` change, deploy, restart or new server commit. No new roadmap work completed. Next action requires the owner's confirmation.

### 2026-10-13 ~14:05–15:10 PDT (Phase 1 via bots: combat, death/clone, navmesh paths; work split) — Claude
- Owner: finish Phase 1 using Universal Modder and bots, and split the load with ChatGPT. Work split written into `../AGENTS.md`. ChatGPT tasks C1–C5 are above, and the roadmap is refreshed.
- Dev `a72026b6` (agent body):
  - creature state (HAM, posture, states, level, group, target) from baselines and deltas;
  - combat log events; menu option names; `inspect`;
  - `fight` reflex;
  - `move` refuses while dead and stops when the server keeps resetting it;
  - navmesh path walking, including through doors (DataTransformWithParent).
- Dev `eebdd99d`: **server** command `/agentpath` (path / height from Core3's PathFinderManager and terrain). Only `Core3.AgentAccounts` may use it. **Not deployed.**
- `tools/test_galaxy.py`: new `--dev-server` and `--config` options.
- Test galaxy only, test-Kael (dev server):
  - kill a baby rockmite (combat log, target "dead" event) PASS;
  - Kael incapacitated twice, then dead, clone pop-up → Mos Eisley PASS;
  - `/agentpath` height (town 20.2/5.0, plateau 180) PASS;
  - path from the Han platform to the greeters, re-planned when partial, PASS;
  - path from the greeters into the cloning facility (62 points, 4 cells, down the stairs) PASS;
  - path back out (cell → world): **"no path", open**.
- The "z 180" height reports came from a real plateau north-east of Mos Eisley, which the old body never followed.
- Other open items:
  - loot is still unverified (animals have no loot; needs a humanoid kill);
  - `look` indoors returns nothing;
  - out-of-range talk is still silent;
  - Chewbacca is silent.
- NPC IDs change at every server start, so look them up by name.
- Live is untouched. The agent binary is still pinned at `ab9eab6e`.

### 2026-10-13 ~13:25–14:05 PDT (Kael interaction upgrade reviewed, fixed, built, tested) — Claude
- Reviewed ChatGPT's staged patch against the Core3 server sources: radial request/response/select, SUI create/event and mission-list request layouts match. **Localized speech decode was wrong** (skipped one short instead of short + pad flag + type byte + int). Patch had CRLF line endings; applied after normalizing.
- Dev commit `e1344def` (`Core3-dev`, branch `dev`): ChatGPT's controls + fixed speech decode, conversation state under the mutex, `choose` guard, SUI page forgotten *before* replying (server reuses page IDs), `look` reports z, `status` reports container, and **ground height while walking** (nearest outdoor NPC's z; `move` takes optional `z`).
- Root cause of silent Han/greeters: the body kept its login height (20.3) while walking on 5.0 ground (live: up to z180), so the server's conversation line-of-sight check failed with a general error the body never sees.
- Test galaxy (46xxx, from `galaxy-20261013T172001Z`), test-Kael only: inventory PASS (found an X-31 landspeeder deed); Guillo speech + branching PASS; stale choose refused PASS; Han dialogue PASS; Chewbacca silent; character-builder radial → SUI list → cancel PASS, row select opened sub-list PASS; deed → vehicle control device PASS; call vehicle PASS once; **mount unverified**, a re-call after relog showed nothing; mission_list untested (no terminal in range); out-of-range talk still silent. Test galaxy stopped and deleted.
- **Live untouched**: agent binary still pinned `ab9eab6e`; ChatGPT's 6 MCP wrappers remain staged (they would fail against the pinned binary). Promotion needs ChatGPT's cross-review of `e1344def` + owner OK, then copy `build/dev/src/client/core3client` to `/opt/swg/agent/bin/core3client` and apply `staged-capabilities/mcp-capabilities.patch` (add `z` to the move schema).
- Also installed Universal Modder for Claude Code at the owner's request (user scope; fal MCP fails to connect without a key, expected).

### 2026-10-13 13:19 PDT (ComfyUI model support) — ChatGPT
- Owner asked which models ComfyUI supports. Checked official repository and workflow docs for image/editing/video/audio/3D support; added findings to `Documentation-support/asset-workflow-review-for-Claude-2026-10-13.md` for Claude's pending review. FLUX.2 Klein 4B FP8 is a new image/editing candidate (documented benchmark 8.4–9.2 GB VRAM); Hunyuan3D 2 is a 3D candidate alongside TripoSR. Native Hunyuan3D example texture support is explicitly limited; TRELLIS.2 is documented but its requirements on our PC are unverified.
- Documentation/research only: no downloads, installations, generation calls, game session, server changes or new commits. All local model performance, compatibility and SWG conversion remain **untested**. Claude's lock unchanged. Next: Claude's requested review, then an owner-selected first asset experiment.

### 2026-10-13 13:07 PDT (asset workflow note and Claude review request) — ChatGPT
- Owner asked to record the preceding fal/free-option discussion for Claude and ask its opinion. Claimed the documentation task and saved `Documentation-support/asset-workflow-review-for-Claude-2026-10-13.md`, with previously checked primary references, observed fal pricing dated to this discussion, subscription/API separation, RTX 5070 12227 MiB hardware result and the proposed concept → local TripoSR → Blender → SWG path.
- Added an open review task for Claude and explicit questions in the note. **Claude has not replied.** The shared files/board are the handoff channel; no addressable Claude Code chat was available in the Codex thread listing, so no direct chat delivery is claimed.
- Documentation only: no downloads, installations, generation calls, spending, game session, server changes or new server commits. Claude's server lock unchanged. Local-stack compatibility, SWG exporter/import path and all proposed generated assets remain **untested**.
- Next: Claude claims the review, records its opinion in the note and updates this board; owner then chooses the first asset experiment. Kael controls and the pending live deployment are separate tasks.

### 2026-10-13 approximately 12:33–12:53 PDT (equipment/objectives and requested plugin) — ChatGPT
- Owner requested equipment, retries, mission terminals, vehicles and other gameplay for twenty minutes. Read rules/guide/board/roadmap and claimed task. Live `sandbox` still `920203d8`. Lock transfer requested; owner asked about conflicts and said they could wait, **no transfer approval received**. Claude's lock unchanged. No server/shared-dev files, binary, account or database edited; no restart, backup, deployment or new server commit.
- Staged concrete source patches outside `/opt/swg` in `tools/agent/staged-capabilities/`: inventory containment inspection, radial request/selection, SUI inspection/reply, mission-list requests (six added MCP wrappers, 21 schemas), localized NPC speech identifier decoding and active-conversation guards/cache resets. **Both C++ translation units pass syntax-only checks** against dev flags; staged Python adapter compiles/imports. No link build, dev/test galaxy execution or in-game verification; all new capabilities remain **untested**. Mission delta decoding/acceptance and mounted movement still unfinished.
- `README.md` records source base `ab9eab6e`, checks, limitations, equipment candidates and acceptance sequence. `.base` files and unified patches allow review. Owner/staff provisioning is still required after the inventory/radial controls are proven: **no tools, resources, credits or vehicle were granted in this session**.
- Kael connected and retried Han at approximately 1.8 m: still no dialogue/options. Walked outdoor city route via 3400,-4782; 3210,-4782; 3399.74,-4889.85, then returned to Dax. Checked views showed banks/travel/ticket terminals but no mission terminal or mountable vehicle; not proof none exists. Current pinned interface cannot inspect datapad/inventory or send mission/radial/SUI packets. **No mission requested/accepted/completed, no vehicle called/mounted/ridden/stored.** Dismount request while unmounted was only accepted, effect unverified. No combat, staff commands or other-player interactions.
- Startup health check reported one historical invalid enqueueCommand error (CRC3494034937, actionCount1, target0); cause unassigned. Prior posture checks remain unverified.
- During session owner supplied Universal Modder install commands. Added `rehan-remade/universal-modder` marketplace and installed `universal-modder@universal-modder` version0.2.0; verified installed manifest. Uses MIT license; declares fal MCP requiring FAL_KEY. No key supplied, fal calls, purchases or paid asset generation performed. Installation modified only the authorized Codex plugin configuration/cache.
- Saved `Agent/notes/twenty-minute-objectives.md`, final playbook/progress report and disconnected. Kael at Tatooine3554,-4782 outdoors beside Dax, no companions. Next: Claude/authorized holder reviews staged diffs, builds/tests in dev/disposable galaxy, completes mission/mounted support, then required cross-review before live client promotion and actual equipment/objective tests.

### 2026-10-13 12:18–12:28 PDT (ten-minute sweep) — ChatGPT
- Owner authorized as many function tests as possible in ten minutes. Read rules/guide/board/roadmap, claimed sweep, checked healthy live `sandbox` at `920203d8`. **No server changes or new commits**; Claude's lock unchanged. Final disconnect completed by 12:28:13 PDT.
- `Agent/notes/ten-minute-sweep.md` records **25 check rows**, including partial and unverified commands, not 25 passed gameplay functions. Verified object type/radius/limit/empty-result behavior; persisted position; empty-group dismissal; one hire/follow/explicit dismissal; event cursor filtering; notebook listing and exact write/read; standard dialogue branching and walk-away closure; survey/sample no-tool errors; speed2 movement and arrival tolerance; Burst Run start/expiry/cooldown messages. Actual speed bonus/HAM cost unmeasured. Sit/stand/kneel/prone requests accepted, actual posture unverified.
- **Rapid relog cleanup finding:** Naty Voinee (281474994127026) directly observed before disconnect at 12:22:00, survived reconnect at 12:22:06–07, then followed Kael's 10 m walk. Explicit Dax dismissal at 12:23:10 removed it. Full delayed server logout remains untested; previous absence-based cleanup inference is not a universal guarantee.
- **Localized dialogue bug:** Guillo (281474994103942) and Mooch (281474994103939) returned empty npc_says text while options and Guillo branching worked; Vincie (281474994103936) returned start/options without speech in result. Kael within 2.1/3.3/4.6 m at 3530.13, -4798.91. Keys in options are expected; blank speech is the issue.
- **Stale selection bug candidate:** after Dax's conversation_end, choosing without a fresh talk reopened greeting/options without conversation_start; subsequent cancellation also refreshed greeting. Fresh talk restored normal hiring. All three findings reported in `Agent/reports/2026-10-13.md`.
- Saved checkpoint and final playbook/progress reports; disconnected/reconnected only for cleanup probe, following session routine each time. Final Kael position: Tatooine 3553.63, -4782.26, outdoors, z16.35449, beside Dax; Naty explicitly dismissed, no companions. Burst Run expired and cooldown observed. No combat or other-player interactions.
- Next: developer investigation of conversation text/state and logout lifecycle; add body HAM/damage/posture/SUI/indoors support before richer testing. Existing range/height/quest/assist issues remain open. Research PDF export remains deferred.

### 2026-10-13 (additional Kael functions, approximately 12:10–12:14 PDT) — ChatGPT
- Owner requested a couple of other function checks and checking Claude's latest work. Re-read instructions/guide/board/roadmap; no newer live-feature handoff found. Claimed additional-function testing. Galaxy active/initialized, zero startup error lines, live `sandbox` at `920203d8`. **No server changes or new commits**; Claude's lock unchanged.
- **PASS:** one spatial-chat line returned exact text from Kael and persisted in event history (seq654). Another player's reception was not tested.
- **Range-feedback bug:** Dax (281474994095833) at3552,-4782 was silent when Kael talked from3564,-4782 (12m); no documented `command_failed` or too-far error even after waiting/checking status. At3554,-4782 (2m), same NPC returned normal dialogue and choices. Restriction appears enforced; failure feedback missing. Report filed.
- **PASS:** hired exactly3 (Woilowe Aitava281474994126384, Zaca Tzista281474994126395, Cilo Raedwo281474994126418); fourth hire explicitly refused, same3 IDs remained. Not today ended conversation with empty options and unchanged companions. Dismiss all at12:13:22 removed all3 with matching gone events; follow-up look showed only Dax.
- Height clue: login at3554,-4782 reset previousz180 to16.35449; short10m out-and-back retained16.35449. Earlier long-route height issue unresolved; visual/terrain check still untested.
- Saved `Agent/notes/function-checks.md`, updated playbook, filed bug/progress reports, and disconnected successfully. Current position: Tatooine3554,-4782 outdoors beside Dax, no companions. No combat, staff commands or other-player interactions. SUI, indoors, inventory/loot, surveying, crafting and travel remain unsupported/untested by current agent tools.
- Next: fix/expose command failures, HAM/combat feedback and richer interactions under dev/test/review workflow; investigate existing quest and height reports. Successful cap/cancel/dismiss checks need repeating only after relevant changes.

### 2026-10-13 (Kael follow-up testing) — ChatGPT
- Owner requested continued testing. Re-read instructions, guide, handoff and roadmap; claimed follow-up, read playbook, checked active/initialized galaxy and connected. Live still `sandbox` at `920203d8`, zero startup error lines. **No server changes or new commits**; Claude's lock unchanged.
- Kael's logout position persisted. Previous mercenary pair absent at outskirts and broker after relog, supporting logout cleanup. Hired Fabe Tetao (281474994125308) and Nado (281474994125352); both followed from Dax to the nuna group and back.
- At 12:02:09 PDT, near Tatooine 3836.66, -4491.80, attacked dwarf nuna 281474994124570. Attack accepted and two XP-grant messages received; target subsequently emitted `gone` at 12:02:19. Consistent with a quick kill, but **combat assistance remains inconclusive**: no target posture/HAM, damage values or attacker IDs exposed. No incap/death/command-failure messages. Issued peace successfully. Did not escalate to stronger enemies with no health visibility.
- **Verified dismissal of two mercenaries:** Dax's Dismiss all at 12:05:35 returned removal events for both exact IDs and closing dialogue; subsequent look showed only Dax. Both companions had followed back to town.
- New bug candidate: Kael status reports z180 after walking/relog and on return beside broker; initial first-session login near the same position was z16.35. Ground alignment and visual impact not inspected; no fix attempted.
- Saved `Agent/notes/mercenaries.md`, updated playbook, filed bug and progress reports in `Agent/reports/2026-10-13.md`, and disconnected successfully. **Current saved position: Tatooine 3554, -4782, outdoors beside Dax, both mercenaries dismissed.** The earlier outskirts position is historical.
- Next: implement/expose HAM, posture and combat damage feedback through the dev/test workflow, investigate height and quest dialogue, then repeat assistance verification. No SUI/indoor/crafting/dungeon tests; no staff commands or other-player interactions. Research PDF export remains deferred.

### 2026-10-13 11:50 PDT (Kael first session ended; Codex handoff) — ChatGPT
- Read `AGENTS.md`, this board, roadmap and `Agent/AGENT-GUIDE.md`; claimed knowledge sources and first play session. Finished `Agent/knowledge-sources.md`: 12 public references with coverage, era, reliability and access caveats. No sign-ins, new content downloads or cut-content research.
- Read-only galaxy status: active, initialized, zero error lines since startup, live `sandbox` at `920203d8`, working tree clean. **No server changes or new commits**, no restart, backup or deployment; Claude's server lock remains unchanged.
- Via `swg-agent`: read playbook, connected as Kael, checked status/look, mapped outdoor landmarks, walked a forecourt loop and northeast outskirts. Dax Venn's conversation and hiring two mercenaries worked. Faehu Emo and Sesxe Egi followed, last directly observed 4 m behind at 3800, -4620.
- **Broken/inconclusive:** Han Solo and Chewbacca returned no dialogue/choices within 1.6 m / 4.0 m; quest not started. Dax's working conversation is a positive control, but content wiring versus message handling is unresolved. Repeated `gone` events for R5-D9 also filed as a telemetry bug candidate. See `Agent/reports/2026-10-13.md`.
- Owner first requested stopping after the next test, then requested aborting to move to Codex. Found dwarf nuna candidates but issued **no attack**. Mercenary combat assist, damage/kill/rewards, HAM, SUI, inventory/loot, crafting, travel and indoor movement remain **untested**. No staff commands or other-player interactions.
- End routine completed: updated playbook, Mos Eisley and quest notebooks using `write_notes`; filed progress report; `disconnect` returned ok. Kael's last position: Tatooine 3827.91, -4513.34, outdoors. Mercenary cleanup on logout was not separately reverified.
- Resume brief: `Agent/Codex-handoff-2026-10-13.md`. Next developer work: investigate quest dialogue and add agent HAM/combat feedback/SUI/indoors under the existing lock and review rules. Further play requires a new owner-started session. Earlier research PDF snapshot export is deferred, not completed.

### 2026-10-13 (handover to ChatGPT) — Claude
- Owner approved: promoted the fixed agent client (`/opt/swg/agent/bin/core3client` now = dev `ab9eab6e`; old copy kept as `core3client-v0.1`). Granted **live** Kael `combat_brawler_master` + `combat_unarmed_master` (server log confirms).
- ChatGPT takes over Kael from here. World boss rotation is still **not deployed** (awaiting owner OK + cross-review).

### 2026-10-13 (world bosses, test galaxy, agent fixes) — Claude
- World boss rotation + Rhea Tannor (big game hunter) in dev `bda2c0dd`. Tested on the **test galaxy** only: spawns, galaxy-wide "sighted / slain / slipped away" announcements, hunter report with coordinates and waypoints, kill handling, slot refill. **Not deployed** (owner hold).
- New `tools/test_galaxy.py`: disposable galaxy from the newest backup with dev scripts on ports 46xxx (`start [--set FILE:KEY=VALUE]`, `status`, `stop`). The live galaxy is never touched.
- Found and fixed: 18 MTG files hidden by upstream's `*test*` ignore rule (now tracked: live `920203d8`, dev `6cdb4aef`); the agent client ignored movement after planet changes (TeleportAck); string-table system messages were blank. Fixed in dev, built as `/opt/swg/agent/bin/core3client-next`; ChatGPT's tools still use the pinned `/opt/swg/agent/bin/core3client` (agentd now points there) until promotion.
- `grantskill` needs the character as target. Test-galaxy Kael has Master Brawler + Master Teras Kasi; live Kael is unchanged.
- AGENTS.md: new **Ethics check** section and cross-review before live deploys. Note: ChatGPT's earlier cut-content research tried to fetch the 2026 "Legends" leak (file was gone, not downloaded); the rules now forbid that.

### 2026-10-13 (mercenaries) — Claude
- Backup `galaxy-20261013T172001Z` taken first (includes agent01, Kael and Rook). Live `sandbox` now has `9f74dd57` (mercenaries) and `28aa46d8` (broker stands still); dev has `2347100a`, `b942d9b5` (also: body reports `command_failed` events).
- Verified in-game with Kael via MCP: broker conversation (custom text and options), hire (mercenary spawned 2 m away), follow (stayed within 1 m after a ~20 m walk), dismiss, and automatic removal after logout. **Untested: mercenaries joining combat** (DEFENDERADDED observer, then engageCombat).
- To remove the feature: revert the two commits on `sandbox`, check Lua, restart.

### 2026-10-13 (agent player v0.1) — Claude
- `core3client --agent-control` (dev branch `dcd2f047`): JSON commands on stdin, events on stdout. Fixed two protocol details along the way: DataTransform/TeleportAck must not carry ObjectControllerMessage's trailing int, and the client must acknowledge the zone-in teleport before the server accepts movement. Movement is server-verified and persists across relogs.
- `outputs/tools/agent/agentd.py` (daemon, Unix socket `/opt/swg/agent/agentd.sock`, event log `outputs/Agent/logs/`) and `mcp_server.py` (MCP server `swg-agent`, 15 tools). Registered in Codex (`codex mcp remove swg-agent` to undo; tool timeout 180 s).
- Bot account `agent01` (admin level 0). Character **Kael** (human Brawler) was created while the account was briefly admin so it could teleport out of the skipped-tutorial room (that room needs SUI); Kael keeps staff skills, and the guide forbids using them except to get unstuck. Character **Rook** is parked in the tutorial room, unused.
- Galaxy started at 10:01 by Claude (`systemctl start swg-local`), plus a background keep-alive. The owner can open `Start SWG Server.cmd` to see the live console; it attaches to the running galaxy.

### 2026-10-13 (VS Code) — Claude
- Installed VS Code 1.141 (winget, user scope) plus the WSL and Git Graph extensions (Git Graph also on the WSL side). Launcher: **Open Server Code.cmd**; workspace `/opt/swg/home/swg-server.code-workspace` (live + dev folders; build/databases excluded).
- **Debian default user is now `swgemu`** (`/etc/wsl.conf`; backup `/etc/wsl.conf.before-vscode-20261013`); WSL was restarted once with the galaxy stopped. Always pass `-u root` / `-u swgemu` explicitly.

### 2026-10-13 (Phase 0.5) — Claude
- Full backup with the updated script: `galaxy-20261013T160706Z` (verified; manifest records branch, upstream base and local commits). From now on, backups also save every `tools/*.py` and `.cmd`.
- Restore rehearsal PASSED, all 10 checks (`tools/restore_rehearsal.py`, **Rehearse Restore.cmd**). The copy and its database were deleted afterwards and the database grant revoked.
- New tools: `rebuild_server.py` (**Rebuild Server.cmd**), `upstream_sync.py` (**Check SWGEmu Updates.cmd**; `apply` rebases safely), `dev_build.py` (dev worktree). Start window and Server Status warn on backups 7+ days old.
- Dev worktree `/opt/swg/Core3-dev` (branch `dev`): Debug core3 + core3client built (17m52s, -j8). Live `bin/core3` sha256 b71a8535… unchanged. Repo note committed: `cfdd1aa2`.

### 2026-10-13 — Claude
- Content gap-check research: `SWG-gap-check-research.md` (Bellum Gero Hoth and planet tools, Flurry scripts, tools list). D20/Progor-Chat excluded at the owner's request.
- Private git in `/opt/swg/Core3`: branch `sandbox`, tag `upstream-base` (= 403893d9), push disabled. Commits: `4357970d` sandbox profile, `96f2ed94` MTG content, `bc13ef51` resource spawn snapshot, `50ede927` local-dev notes.
- `Start SWG Server.cmd` now uses `outputs/tools/start_server.py` (the old copy in `work/` is unused). The backup script now diffs against `upstream-base` and writes `local-commits.txt`.
- New: `Server Status.cmd` (`tools/server_status.py`) and `Check Lua Scripts.cmd` (`tools/check_lua.py`).
- Roadmap: `SWG-roadmap.md`, including the bot framework plan (built on core3client).
- Untested: a full backup run with the changed script.
- Later: the Start window now streams the live console (`journalctl -f`). New `View Server Log.cmd`. `Stop SWG Server.cmd` uses `tools/stop_server.py` and reports a clean stop. The owner stopped the galaxy cleanly at 08:59:59. Untested: the new Start window streaming during a real start.

## Moved 2026-10-13 18:20 PDT

### Finished task rows

| Task | Owner | Status | Notes |
|---|---|---|---|


### Log entries

### 2026-10-13 ~15:15–16:30 PDT (C4 fixes, survey/sample, fresh test bot, owner macros, follow note) — Claude
- **C4 fixes, test galaxy (dev server):**
  - **F3, dev `cde59ec5`:** every point append is checked against the 256 budget, and a capped answer is a marked-partial prefix. ChatGPT's repro routes now give 256/256, partial. Also rejects non-finite or out-of-range coordinates and cells from another zone, uses unique_ptr, and echoes the request.
  - **F1, dev `3797430a`:** one deadline per move, at most 95 s. A 20 s move toward a 1.9 km target returned "timeout" within its window, and the next status answered at once.
  - **F2:** move with the helper while incapacitated → "cannot move while incapacitated"; while dead → "cannot move while dead".
  - Helper replies are matched to their request.
- **Credits:** Flurry world-boss source added to `Community-content/CREDITS-and-sources.txt` (rev `947a7e66`, AGPL-3.0), as C4 asked.
- **Fresh non-staff test bot**, test galaxy only: account `bot02` (auto-registered; credentials in `/opt/swg/agent/bots/`, 0600), character **Tobin Arreno**, Artisan.
  - Created with skipTutorial; landed in the skip-tutorial room. Indoor `look` found its Travel Terminal.
  - `/newbieSelectStartingLocation mos_eisley` → Mos Eisley.
- **Survey/sample PASS (test galaxy):**
  - mineral tool → range SUI → resource list;
  - surveyed 10 resources, best Ihiris (iron) 65–69%;
  - `/requestCoreSample` → kneel, "sample located" ×2 + XP → **Iron container in inventory**.
- **Fight → incapacitation → death → clone** repeated with Tobin. Fixed a stale tutorial-room container that blanked `look` after a zone change.
- **Owner on live:**
  - `/resource perfect` → Sloviboiam (steel_neutronium) and Galiium (iron_plumbum), all stats 1000. That's the Phase 1 `/resource perfect` check.
  - Macro notes in `Documentation-support/swg-macros.md`.
- **Follow issue, note for ChatGPT's report:** both of [name removed]'s captures (`follow-16460*.png`) show **GOD MODE** on (overlay text plus the see-through green floor/name view). God Mode lets the GM pass through walls and ignore ground rules, while client `/follow` is straight-line steering. Suggested test: God Mode off, both characters on open ground, a stationary leader, before the turn-strafes setting. Unverified hypothesis.
- **Still open:** loot (needs a humanoid), travel, trade/group, crafting session messages, vehicle mount.
- Live untouched apart from the owner's own commands. Agent binary still pinned at `ab9eab6e`. Nothing promoted.

### 2026-10-13 14:57–15:13 PDT (C4 cross-review) — ChatGPT
- Owner authorized C4 only. **Reviewed by ChatGPT:** `e1344def`, `a72026b6`, `eebdd99d`, `5c39f411`, `697f2002`, plus world-boss `bda2c0dd`. Read exported patches and pinned server/client protocol sources as `swgemu`; saved review, 50 source-copy checksums, commit metadata and offline evidence under `Documentation-support/review-C4/`. **Review complete; changes requested before combined agent/navigation promotion.**
- Three P2 findings filed for Claude: F1 move timeout restarts for each of up to 25 legs (MCP waits 100 s); F2 path walking bypasses the dead/incap guard in direct moveTo; F3 helper interpolation exceeds its 256-point bound. Compiled the unchanged expansion loop in isolation: 2 km straight synthetic path returned 257 points; a synthetic corner route returned 326. F1/F2 verified from exact source structure; no timed gameplay reproduction claimed.
- Compared radial, SUI, NPC speech, CREO baseline/delta, combat, cell-transform and mission-list layouts against pinned server writers; all 234 generated radial option labels match. `/agentpath` account allowlist precedes terrain/path work; no credential/excluded-source/external-service addition found in the diffs. Normal non-allowlisted denial still needs an independent game test. World-boss code has no additional blocking finding; real player-damage credit payment remains untested and central adapted-source credits need updating.
- No Kael connection, game control, full client/server build, `/opt/swg` edit, backup, restart, promotion, deployment, paid call or new server commit. Claude's lock unchanged. This review is not owner deployment approval. Next: Claude fixes/tests F1–F3 on the disposable galaxy and records commits for focused re-review; owner approval remains required for live work. C1/C2/C3/C5 and Universal Modder research remain on hold.



## Archived during 13 October C7/documentation session

### 2026-10-14 (C4b + C4c reviews, unattended) — ChatGPT
- **re-reviewed by ChatGPT:** `cde59ec5`, `3797430a`, and the final net C4c changes from `09a56205`, `220e0f39`, `f25c90f9` through `2970b47e`. Report: `Documentation-support/review-C4b/C4b-C4c-review.md` — original F1–F3 closed; 3 P1 + 4 P2 findings, changes requested (including configuration-only live isolation for grant helpers). Exact-loop offline compile/run PASS: 256/256 points, both partial; no WSL/game/server access or new server commit. Runtime checks remain untested by ChatGPT; next: Claude fixes/tests in dev, then re-review and owner deploy OK.


Older log entries and finished tasks: `SWG-handoff-archive.md`. Keep this board short: when it passes about 25 KB, move finished rows and all but the newest four log entries there.


### 2026-10-13 ~17:35–18:20 PDT (squad gear, training, missions, boss crew, C1 v1) — Claude
- **Test-galaxy helpers, dev `f25c90f9`:** `/agentgear basic|boss|support` and `/agentskill <box>…`. Both need `Core3.AgentGear = true` plus the allowlist, so they can't act on live. Training granted all five boss-crew roles with their prerequisites.
- **Agent body:** decodes mission objects (baselines and deltas). New commands: `missions` and `mission_accept`. Not yet tested end to end, because no mission terminal has been found in Mos Eisley. Esk is mapping a wider area into `tools/bots/places.json`.
- **Squads:**
  - Aurek is now the 5-member world-boss crew: Doctor, entertainer and Ranger support with `aurek-boss-camp.py`. The dance/watch loop worked.
  - Combat members get `gear('basic')`. `cresh-missions.py` is waiting for a mapped terminal.
  - Findings:
    - Boss gear without training lost to a zucca boar, because uncertified weapons take penalties. Training fixes that.
    - Ticket purchase is flaky (no answer some runs).
    - Gatherers: relog keeps all items ✅.
- **Leash fixes** (dev `220e0f39`), found by the Dorn group: verified on the test galaxy, 2.7 m from the leader.
- **C1 v1:** `Documentation-support/swg-format-inventory.md`. Hoth is confirmed as the first Universal Modder job: TRE + datatable + STF work, testable with the squads.
- **Cut content:** the rule is our own client and released packages only. Flag: `Content-catalogue/Cut-content-and-backports/SOE-cut-content-selected-reference.zip` comes from SWG-Source/dsrc, which the Ethics check excludes. Don't use it. Moving it out is the owner's decision.
- Owner macros for gathering and support roles added to `Documentation-support/swg-macros.md` (untested in the client).


### 2026-10-13 ~17:00–17:35 PDT (bot squads for ChatGPT, leash fixes from squad testing, live stopped) — Claude
- **Live galaxy stopped** at the owner's request (to free RAM): clean shutdown via `stop_server.py`. Not restarted; the live deploy still waits for C4b/C4c and the owner's OK.
- **Bot squads (C7)** in `tools/bots/`:
  - `squad.py` harness, `groups.json` (5 groups, 16 bots), and starter scenarios plus a README in `scenarios/`.
  - Setup creates and groups everyone in about 40 s.
  - Runs write `Bot-reports/<Group>/<time>-<scenario>.json` plus a `LOG.md` line.
  - `--minutes/--detach` runs for hours; `tidy` keeps the files small.
  - The test galaxy allowlist now covers all squad accounts.
- **Findings from the first squad rounds:**
  - Shuttle travel works: Mos Eisley → Bestine, ticket and boarding (Phase 1 travel ✅).
  - Cloning recovers dead bots.
  - Rhea Tannor's world-boss dialogue, Dax Venn's options, dancing, spatial chat and three parallel navmesh routes (cantina, starport, plateau) all work.
  - New characters lose to a greater desert womprat.
  - The starting scout lacks `/forage` and harvesting. Error code 2 means "missing ability", and the body mislabelled it; fixed.
  - No mission terminal found near the starport or square yet.
- **Leash fixes** (dev, uncommitted, in the rebuilt test-galaxy server):
  - When the navmesh path stops short of the leader (raised ground), the follower was moved to the same out-of-range spot every 8 s. Now it goes to the leader's spot.
  - `/leash <current leader>` says "Already leashed" instead of switching it off.
- **Optimization:** this board moved from 44 KB to 19 KB. 19 finished rows and 17 older entries went to `SWG-handoff-archive.md` (nothing deleted). The roadmap's new "Housekeeping and optimization" section has the rules.


### 2026-10-13 ~16:00–16:50 PDT (follow assist `/leash`, second test bot, board fixes) — Claude
- **Follow assist, dev `09a56205` (the owner asked for a temporary fix):** client `/follow` is straight-line steering and the server never hears it, so the server now helps from its side.
  - While a leash is on, the server checks every 2 s.
  - If the follower is more than 10 m away and hasn't closed the gap for 3 checks, it moves them to a walkable point 3 m short of the leader, along a navmesh path (doorways and cells included).
  - Otherwise it does nothing.
  - Start/stop: right-click a group member, `/leash <name>` or `/leash off`. `Core3.LeashEnabled = false` turns it off.
- **Test galaxy (dev server), bots Tobin (bot02) and Mirra (bot03, new):**
  - Refused before grouping ("not in a group").
  - `/invite` + `/join` works (Phase 1 group check ✅).
  - Outdoors: the first build placed the follower 17 m back (sparse path points); fixed so it lands 3.0 m behind, once.
  - Leader walked 91 s into the cantina: the stationary follower ended up inside the same cell, about 6 m from him. A follower that doesn't move at all is hopped forward about every 8 s while the leader keeps walking.
  - Right-click label, toggle on/off, `/leash off` and usage text all work.
  - Leaving the group ends the leash.
  - **Not tested:** a real client actually running `/follow` (C6), private-building refusal, mounts.
- **Harness:** `tools/bots/bot.py` is now in outputs for C3. Fixed a hang: the FIFO holder inherited the caller's pipe.
- **Board:** the server-lock line had wrongly said a live deploy was in progress. No deploy happened: the permission check stopped the scripted deploy, and the owner hasn't chosen a method yet. Corrected my clock-skewed log times.
- Live untouched: up 6 h, same binary. Agent binary still pinned at `ab9eab6e`. Nothing promoted.

### 2026-10-13 ~15:50 PDT (follow result, owner report) — Claude
- Owner retested the alt's `/follow` with **God Mode off** on [name removed]: it "started off better", then she got stuck. Consistent with pre-CU client follow being straight-line steering with no pathfinding: walls are no longer the problem, but corners and obstacles still catch the follower.
- Suggested confirmation: open desert, leader walking a slow curve. If she keeps up there, it's normal client behaviour, not a server fault. If she still sticks on flat ground, try ChatGPT's turn-strafes setting next. ChatGPT: please fold this into `Agent/reports/2026-10-13-human-client-follow.md`.
- Also added `tools/reset_password.py` (owner tool) for the alt account `Pengwens`. The owner types the new password privately; it stores sha1 with an empty salt, and Core3 re-salts on first login. Verified that python and MariaDB SHA-1 match. The owner used it and logged in.






## Archived after KOTOR research

### 2026-10-14 (C7 scenarios, unattended) ? ChatGPT
- Added `aurek-doctor-buffs.py`: stage safely in town and verify all four enhancements by max-HAM gains; latest Aurek report falsely passed four ?wrong locomotion? refusals. Added `besh-harvest.py`: bounded patrols seek ordinary prey, verify Varo?s fresh corpse, then Pell attempts one resource type per kill; recent gather runs never reached harvesting. Updated only Aurek/Besh lines in `Agent/squad-plan.txt`. Latest summary: Aurek 28/35 (camp failed 5/5), Besh 45/45, Cresh 14/23, Dorn 30/30, Esk 25/25; `/tell` remains BLOCKED. Compilation, LF checks and offline mock gain/refusal/missing-skill/receipt cases passed. **In-game untested; no server access or commit.** Next: Claude?s scheduled run; map medical support if refused, and add resource-quantity/buff-duration decoding if needed.


Older log entries: [SWG-handoff-archive.md](SWG-handoff-archive.md).



### 2026-10-13 (owner requested the nap-work update) — ChatGPT
- Read the current board, roadmap, C4b/C4c report, squad plan and last completed squad summary. Preparing a status update distinguishing recorded Codex source/scenario work from Claude's runtime tests. No new squad run, server action, live promotion or commit performed for this status request.
- Corrected the human-client follow report's pending control test: owner had reported that disabling turn-strafes did not help. `/leash` remains development-only with C4c changes requested. Latest board says live is stopped; no real-client control or restart attempted.


Older entries: [SWG-handoff-archive.md](SWG-handoff-archive.md).



### 2026-10-13 (post-C7 shared references and historical feature research) — ChatGPT
- Completed `Documentation-support/SWG-professions-and-gameplay-reference.md`: full profession coverage map, precise local medical/harvest prerequisites, partial squad training, archived source access/era caveats. Exact skill IFF costs/boxes and detailed formula validation remain open; no invented thresholds.
- Completed `Documentation-support/universal-modder-reference-for-Claude.md`, full CLI help (76 parser entries, all 10 groups), and 50-path source hash inventory via `tools/document_um_capabilities.py`. Distinguished actual CLI/MCP from separately installed RE tools. `kb search` in native Python failed for missing PyYAML; searched bundled index/text instead, no SWG-specific note found. No dependencies installed or paid calls.
- Created shared `SWG-feature-register.md` linked from board/roadmap: 81 grouped proposals with purpose/maturity/difficulty plus all 102 existing active catalogue candidates. Added public developer-history research in `Documentation-support/SWG-official-plans-cut-content-and-backports.md`; 17 historical design candidates, official retrospective testimony distinguished from recoverable assets. No assets downloaded, imports, services, outbound posts, server edits, deploys or commits.
- All squad bots stopped after the single round. Test galaxy left unchanged; live untouched. Next engineering: Claude's fix re-review; medical site, safe harvest case and mission terminal map. Research next: corroborate contemporary official plans, verify dead creator-release links and selected dependencies/rights.


### 2026-10-13 20:18 PDT (C7 one bounded round) — ChatGPT
- Inspected Claude dev HEAD `5aadc8b9`: seven review findings have implementations, full re-review still pending. One round of the five current-plan scenarios completed in 226 s, 30/35 checks: Aurek 3/4, Besh 3/6, Cresh 10/11, Dorn 9/9, Esk 5/5. Report: `Agent/reports/2026-10-13-C7-one-round.md`; raw run `20261013-201324`.
- Errors: medical prerequisite refusal, patrol timeouts/Varo death before any harvesting, mission terminal unmapped; tells BLOCKED. Shuttle round trip and corrected leash menu behavior passed this round. No restart/deploy/server edit/new commit. All five squads disconnected successfully after completion. Owner now requests profession/game documentation and a complete installed Universal Modder capability reference; ChatGPT claims those documentation tasks next.




### 2026-10-13 (KOTOR author reuse audit and RedHawke site history) — ChatGPT
- Saved `Documentation-support/KOTOR-mod-reuse-audit.md`: 26 releases/resources plus lead-author/team and contributor register. Recovered RedHawke original Citlink URL and JumpStationZ closure/preservation trail; archive snapshot requests failed, contents not claimed recovered.
- Verified Silveredge9's direct 25 October 2016 broad grant, ChAiNz's 2014 blog plus explicit cross-game Nexus settings, and indexed Dark Hope first-person use-with-notification statement. Distinguished stock art, contributor scope, rehosting and modification. Quanon/svösh/SpaceAlex original blanket terms remain unresolved; no whole package cleared for SWG import.
- Public web research only; no package downloads, author contact, paid calls, server/client changes or git commit. Conversion/in-game testing untested. Next: select an asset and verify its exact files, bundled terms and contribution chain before import.


### 2026-10-13 (KOTOR and open-asset feasibility) — ChatGPT
- Owner owns KOTOR I/II and requested research into stock/mod assets, original inspiration and open assets. Saved `Documentation-support/KOTOR-to-SWG-and-open-assets-feasibility.md`; added F82–F86 to shared feature register. Identified KotorBlender/PyKotor and existing MIT SWG Blender exporter: investigate existing tool path before building a converter. Skeleton/animation/room and Blender compatibility remain untested.
- Verified creator CC0 pages for Quaternius sci-fi kits, Kenney space kits and Poly Haven. Deadly Stream policy is not blanket cross-game permission; modders' original and stock-derived contributions distinguished. Steam EULA retrieval failed; no edition-specific stock-asset permission established. Suggested original/CC0 terminal as first bounded asset-pipeline slice.
- No downloads, extraction, installs, paid calls, game actions, outbound contact, server edits or commits. Full rights/source research queries and gaps in the reference and MODLOG. Next: select original/CC0 first slice; pin compatible Blender/exporter; verify round trip and client appearance. Stock conversions wait for specific rights resolution.





# 2026-10-14 00:09 — preserved board history

### Historical owner question

- **Claude, 13 Oct 22:20: C11 fetch from WSL?** ChatGPT reports the owner authorized C11 in its chat but its sandbox has no network. Claude can fetch section A from WSL: six GitHub repos, about 1.1 GB if cloned whole (much less sparse), plus small CC0 kits, within the 3 GB cap. Claude is confirming with the owner in its own chat first.


## Message for Claude — C11 network access needed (13 October 2026)

Owner explicitly asked ChatGPT to let you know. C11 archive downloads are authorized: the owner said “Lets start on c11.” Codex's first A1 GitHub metadata/size request failed with sandbox socket access denied for api.github.com:443. The download plan requires stopping when the sandbox lacks network; no downloads occurred (0 bytes).

Please pick up the network-enabled fetch from your environment, or make an approved network-enabled route available. Resume at A1 and follow `Documentation-support/archive-download-plan.md` exactly: source/rights checks, pinned revisions, size checks and 3 GB total cap, then B/C as permitted. No installs/execution/sign-ins; preserve excluded sources and record verified licence/readme, credits and hashes. Pending records are in `Content-catalogue/archive-downloads.json`; null fields are unverified, not completed downloads. This request does not authorize live restarts/deployments or account changes.



## Archived session log entries

### 2026-10-13 (C11 archive download attempt) — ChatGPT
- Owner authorized C11. Claimed and read `Documentation-support/archive-download-plan.md`; first A1 GitHub metadata/size request failed with sandbox socket access denied (api.github.com:443). Followed plan's explicit no-network stop rule; did not seek a bypass or use WSL/network escalation.
- Saved `Content-catalogue/archive-downloads.json`: 15 grouped plan records, blocked/unattempted status, null unverified metadata, total downloaded 0 bytes. Nothing downloaded, extracted, installed or executed; no sign-ins, messages, server changes or commit. C11 queue is hold for external blocker, not lack of owner consent. Next: network-enabled approved executor can resume A1 then A/B/C with source/rights/size checks; owner consent for this archive task already exists.


### 2026-10-13 (C4d re-review) — ChatGPT
- Re-reviewed by ChatGPT: dev `5aadc8b9`, all eight packet files match commit. Report: `Documentation-support/review-C4d/C4d-review.md`. Five original findings resolved in source, two partial; remaining 2 P1 + 1 P2: pathfinder's failed-route fallback still permits teleport; cross-lock releases follower before task identity/online recheck; plans not invalidated by scene change.
- Offline C++ reproduction of exported unstick method + real pathfinder fallback confirms one move to (97,0) from (0,0), leader (100,0), when route evaluation fails. Null/no-progress controls do not move; supplied reachable prefix works. Source/lock/mission-writer context and hashes saved. Not a Core3 build or in-game test.
- Read-only server/source access; no restart, deploy, game connection, /opt/swg edits or server commit. Existing Dorn 9/9 and Esk 5/5 reports inspected, not rerun. Concurrent uncommitted find/tell work in AgentControl.cpp/AgentPathCommand.h is outside this review. Relay c4d task marked done to avoid duplicate review. Next: Claude fixes + disposable-galaxy regression checks, then cross-review and explicit owner deployment OK.


### 2026-10-13 ~21:30 PDT (ChatGPT's parameters updated in AGENTS.md, owner's choice) — Claude
- **New "ChatGPT's defaults" in Work split:**
  - **Model and effort:** GPT-6.1 Sol; High for code reviews, Medium for research, scenarios and docs; no Astra/Max/Ultra unless asked.
  - **Research budget:** about 30 minutes or 20% of the remaining usage per task, then write up.
  - **KOTOR author census closed** at 56 releases; reopen it only for one asset chosen for import.
- **Ethics check, item 1: a rule for assets from other games or mods.**
  - Only creator-original work with explicit other-games or conversion terms qualifies; stock files and anything derived from them are excluded.
  - Record the provenance of each imported asset.
  - Contacting or paying an author needs the owner's OK.
  - Built from ChatGPT's two audits (`Documentation-support/KOTOR-*`). Claude agrees with their recommendation: start the asset pipeline with an original or CC0 terminal through the existing SWG Blender exporter.

### 2026-10-13 (additional KOTOR mod-author research) — ChatGPT
- Owner requested roughly ten more minutes. Added `Documentation-support/KOTOR-mod-reuse-audit-additional-authors.md`: 30 more numbered releases/resources, taking combined inventory to 56, plus additional author-statement/lead register. Linked from first audit; CapitaineSpoque/ZobiZob alias now verified from creator/uploader fields and public readme.
- Strong new leads: Sithspecter's Sleheyron modules, djh269 hut resource, Quanon/Marius Fett Praetorian explicit conversion terms, ShiningRedHD credit-based cross-game terms, Seph6 holocron. Recorded Vurt conversion prohibition, Selphadur/Leilukin restrictions, redrob41 hosting tension and Dak's later scope-limited override. Final checks also verified Effix own 1 November 2025 broader credit-based policy, a permissive Leilukin dialogue patch and upstream DP Kel Dor resource terms. Author grants do not clear stock art/contributors.
- Public research and docs only: no downloads, messages, payments, server edits, conversion tests or git commit. Original Quanon/Toasty/Ferc resource retrievals and some licence chains remain unresolved. Next: select exact asset and verify files/rights before import.


### 2026-10-13 ~19:50–21:10 PDT (overnight check results, C4b/C4c fixes, Cresh round trip) — Claude
- **Overnight check:** it ran at 18:39 and 19:01–19:49. The 19:01 run sat about 45 minutes on approval prompts, so the 19:30 run was skipped. Paused when the owner came back at 19:50; re-enable it in the sidebar ("Scheduled") when wanted.
- **ChatGPT's C4b/C4c review** (`review-C4b/C4b-C4c-review.md`, 3 P1 + 4 P2) is fixed in dev `5aadc8b9` (dev keeps a clean history: `2970b47e` LF normalization, then `5aadc8b9`):
  - **P1:**
    - Grant helpers also need a disposable test galaxy (database name `*_test`; live is `swgemu`).
    - The leash cross-locks the leader for one consistent check-and-move.
    - The leash only moves along a real route: no route, no move; no repeated useless hops.
  - **P2:**
    - `/agentpath` request ids.
    - "Stop leash" only on the current leader.
    - Mission cache cleared on scene change and on late destroy.
    - Waypoint cleared on refresh.
- **Test galaxy:** restarted with the build.
  - Dorn 9/9: Nima ends 2.1 m from Dorn with 0 repeated hops, and the three-person menu labels are right.
  - Esk 5/5: paths with ids.
  - Helpers still grant on the test galaxy.
- **Scenarios:** `cresh-travel.py` is now a round trip from the nearest shuttleport. One-way trips had stranded Cresh, and the next round's 4.6 km walk got it killed. ChatGPT's 20:13 round shows the round trip passing. `dorn-social.py` adds no-rehop and menu-label checks.
- **Still open** (in C7):
  - First `/purchaseTicket` after a fresh galaxy start fails silently, 3 of 3 times; nothing in the server log.
  - Doctor buffs need a medical centre or droid.
  - The harvest scenario finds no prey and bots die on patrol.
  - Mission terminals still unmapped.
- **C4d:** re-review packet ready; queued in `Agent/gpt-queue.json`, not started (owner to confirm).



## Completed historical task rows

| Task | Owner | Status | Notes |
|---|---|---|---|
| KOTOR mod reuse-terms audit | ChatGPT | additional author pass complete — 56 numbered releases/resources; rights gaps recorded | Documentation-support/KOTOR-mod-reuse-audit.md + additional-authors.md; grants, restrictions and unavailable evidence; no imports/contact |
| KOTOR I/II, mods and open assets → SWG feasibility | ChatGPT | research complete — technical path and original/CC0 routes scoped; stock reuse unresolved | Formats/tools, per-source rights, original inspiration and open assets; no extraction/import |
| Profession/gameplay and complete UM reference | ChatGPT | complete reference documents; exact per-box/game validation remains open | Documentation-support/SWG-professions-and-gameplay-reference.md; universal-modder-reference-for-Claude.md + CLI appendix |
| Shared feature register | ChatGPT | complete first inventory — 86 feature groups + 102 catalogue candidates | SWG-feature-register.md; rough difficulty/maturity, not deployment authorization |
| Official planned/cancelled content and legitimate backports | ChatGPT | first research pass complete — 17 developer-history candidates; deeper archival validation open | Public interviews/announcements/owned-client assets; evidence and feasibility before imports |
| **C4b: focused re-review of the F1–F3 fixes** | ChatGPT | complete — original F1–F3 closed; new correlation finding, 14 Oct | Dev `cde59ec5` + `3797430a`; offline cap repro PASS. `Documentation-support/review-C4b/C4b-C4c-review.md` |
| **C7: bot squads: five groups testing on the test galaxy (owner request)** | ChatGPT | one owner-requested round complete — 30/35 checks; reports saved, 13 Oct | `tools/bots/squad.py`, `tools/bots/scenarios/`, results in `Bot-reports/<Group>/LOG.md` |
| C4 F1: bound the complete multi-leg move by one deadline | Claude | closed by C4b source re-review, 14 Oct; Claude's test-galaxy result recorded | Dev `3797430a`; one total budget capped at 95 s |
| C4 F2: apply dead/incap movement guard to path walking | Claude | closed by C4b source re-review, 14 Oct; Claude's test-galaxy result recorded | Dev `3797430a`; shared guard before/during both walking routes |
| C4 F3: enforce 256 points inside helper interpolation | Claude | closed by C4b re-review + offline compiled repro, 14 Oct | Dev `cde59ec5`; formerly 257/326 points now 256/256, both partial |
| Investigate owner's alt running away/into a wall during follow | ChatGPT | diagnosed — client `/follow` is straight-line steering; God Mode made it worse | Server-side fix built: `/leash` (row below). Report: `Agent/reports/2026-10-13-human-client-follow.md` |


## Completed C4b instructions

**C4b. Focused re-review (read-only).** `git -C /opt/swg/Core3-dev show cde59ec5 3797430a` as swgemu. These fix F1–F3 and take up the hardening notes (input validation, request echo/correlation, unique_ptr). The client commit also adds survey decoding, the indoor-look fix and a scene reset. Re-run your `point_cap_repro` against the new loop: Claude's run gave 256/256, both marked partial. Record "re-reviewed by ChatGPT" in the log.



## Completed C4c instructions

**C4c. Review the leash and the test helpers (read-only).** `git -C /opt/swg/Core3-dev show 09a56205 220e0f39 f25c90f9` as swgemu. `220e0f39` = two leash fixes found by the squads plus corrected body error labels. `f25c90f9` = `/agentgear` and `/agentskill`. Check that they can never act on live: they need `Core3.AgentGear = true` and the AgentAccounts allowlist. It also adds mission-object decoding in the body. For the leash: New file `LeashCommand.h` (a `LeashTask` re-scheduled every 2 s on the follower, plus the `/leash` command), registration in `CommandConfigManager.cpp` (special command, like agentPath) and the group-member radial item in `PlayerObjectMenuComponent.cpp` (SERVER_MENU10 = 77). Look at: locking (the task locks only the follower and reads the leader unlocked), task lifetime when a player logs out or the leash is replaced, `teleport` with cell-local coordinates, the building entry check, and any way to use it to reach places a player shouldn't (it only targets a group member's position, same planet, within 512 m). Record "reviewed by ChatGPT" and findings in the log.



## Completed C8 instructions

**C8. MCP wrappers (Medium effort).** Edit `tools/agent/mcp_server.py` (outside `/opt/swg`, yours to change) so Kael's MCP tools cover the body's newer commands. Your six staged wrappers are a starting point. Read the commands in `tools/bots/squad.py` (class `Bot`) and `tools/bots/scenarios/README.md`: inspect, fight, path (returns `points`, and now `proof`: one entry per step, `"ok"` or why it isn't proved walkable), height, move with `z`/`cell`, find (`text`, `radius`, optional `x`/`y`: the server's object search, inside buildings too), tell (`name`, `text`), missions, mission_accept, radial/select, sui pages, inventory. Keep each tool's description short and say what it returns. Python must compile. You can't run it against the game: Claude tests it on the test galaxy and reports back.



## Completed C10 instructions

**C10. Bot mapping and whole-server test coverage (Medium; research budget).** The owner wants the bots to map new areas and eventually test the whole server. Write `Documentation-support/bot-mapping-and-coverage-plan.md`:
1. **Mapping a new area** (Hoth will be the first). What a bot should record, and how, with the tools we have: `/agentpath find`, path plus per-step `proof`, `height`, and the server's planetary map registry, which Claude can expose. Record towns, buildings and cells, terminals, trainers, travel points, NPCs, creature spawns by level, and unreachable ground. Describe the file format, building on `tools/bots/places.json`.
2. **A coverage matrix**: every feature group in `SWG-feature-register.md` and every profession in `SWG-professions-and-gameplay-reference.md`, each with the scenario that would test it, what the body or server is missing to do so, and a priority.
3. **The next five scenarios to build**, and the server or body additions they need (Claude builds those).



## Completed C12 instructions

**C12. Hoth adaptation table (Medium; UM `port-a-mod` method).** Bellum Gero's Hoth server scripts are now in `work/research/Miphstoe_BellumGero-Live/MMOCoreORB/bin/scripts`: `mobile/hoth/`, the Hoth screenplays, `managers/planet` and spawn files; search for "hoth". Our Core3 is `/opt/swg/Core3-dev`, which you may read; a copy of the dev scripts is also in the test galaxy. Write `Documentation-support/hoth/hoth-adaptation-table.md`, one row per Bellum file we would port: source path → our target path, what it needs, what to change, risk. What to change can be AI or behaviour-tree fields, Lua API calls our Core3 lacks, templates (`exotic_rancor` is missing in our client, so name a stock rancor), loot tables, or snapshot-bound data (cave cell IDs, outpost coordinates; Bellum's snapshot came from SWG Infinity, ours from MTG). Read `Documentation-support/hoth-port-log.md` first. Don't copy files into `/opt/swg`; Claude ports them.



## Completed C13 instructions

**C13. Standard operating procedures for building, maintaining and debugging the server (owner request, 13 Oct; Medium, research budget applies).** Write `Documentation-support/SWG-server-SOPs.md`. Start from what we already have and highlight it:
- the docs: `AGENTS.md`, `SWG-developer-baseline.md`, `SWG-sandbox-quickstart.md`, `SWG-roadmap.md` "Housekeeping", `SWG-Readme.txt`;
- the tools: `tools/` (backup, rebuild, restore rehearsal, upstream sync, test galaxy, process check, timings) and the `.cmd` shortcuts.

Fill the gaps with common practice from public SWGEmu/Core3 documentation and general server operations: no leaked material, cite each source.

One short checklist per job:
1. build (dev → test galaxy → review → live);
2. deploy and roll back;
3. backups and restore drills;
4. upstream updates;
5. routine health checks (disk and RAM, including the `/tmp` RAM disk that filled on 13 Oct, logs, processes, database);
6. debugging a server crash (logs, core dumps, gdb on the Debug build);
7. debugging a client or bot crash;
8. performance;
9. incident notes.

Each step names our actual command or file, or "missing" (with what we'd need). End with the ten highest-value gaps, ranked.



## Completed C14 instructions

**C14. Planet lore and galaxy coordinates (owner request, 13 Oct; Medium, research budget applies).** Source: Wookieepedia, Legends continuity preferred. The rules are in `Agent/knowledge-sources.md` item 13: cite each page, and write in your own words rather than copying its text. Write `Documentation-support/planets-lore-and-coordinates.md` (and the same rows as `planets-coordinates.json`). **Hoth first**, then:
- the ten SWG planets (Corellia, Dantooine, Dathomir, Endor, Lok, Naboo, Rori, Talus, Tatooine, Yavin 4), which are the anchors for fitting our map;
- every planet with terrain in our MTG archives (`Content-catalogue/active-content-catalogue.json`, kind "Planet");
- then other well-known Legends worlds.

For each planet:
- galactic region and sector;
- the **grid square** from the standard galaxy map (for example Hoth K-18, Tatooine R-16);
- the system and its moons;
- climate and terrain;
- native species, notable creatures and notable places, especially those that suit pre-CU SWG content (for Hoth: Echo Base, wampa caves, Imperial landing sites);
- three to five sentences of lore summary in your own words;
- the source URL.

Claude uses the grid squares to place new planets on the ticket-purchase galaxy map in proportion to the existing ten, and the lore to lay out Hoth's content.

## Moved 2026-10-15 08:06 (C24b closeout)

### 2026-10-15 06:45 Claude: back up after Miniverse restart; GitHub export check fixed

- **Test galaxy restarted 06:38 by resume** (AGENTS.md standing OK: no owner client, client config on 44453, no squad round). Ready in 74 s; dev 41df647d, so the instruments-kit fix is now live on the test galaxy. `squad.py setup`: 18/18 bots online.
  - A first try at 06:35 (detached `setsid nohup` from Git Bash, as `overnight_cycle.sh` does it) never ran: no log, no process. The foreground start worked. If the cycle's own restart path ever reports "restart started" with no galaxy afterwards, this is why.
- **Automation:** live map back as a transient systemd unit `swg-live-map` (127.0.0.1:8765, as swgemu); `gpt-relay-overnight` re-enabled 06:45 (dry run clean: 18/18, GPT open tasks c34r and c24b). The live-status timer never stopped.
- **GitHub:** the repo is still private with the 05:15 push; the owner's one-time `--force` push hasn't happened, and couldn't: `github_export.py build` failed its own check on the script itself (its filter lists contain the reworded phrases). Fix 99d64ef: the script stays out of every pushed version; check now ok (124 commits).
  - Re-checked: full history free of the 24 real secret values and of SOE game data (history-wide variant of `prepush_scan.py`); the 21 "password assignment" hits in the current tree are all false positives (PASS lines, test strings, code that generates passwords).
  - Before going public: a local-model (gpt-oss:20b, on this PC) sweep for real people's names over every unique pushed line is running; the export only scrubs the brother-search handles. Owner questions in chat (brother mentions, Sagiroth, the Recycle Bin wording).
- **Idle research for the local model (owner, 06:47: "when ollama goes idle for more than 10 mins, start researching game mechanics (taking over for gpt) that will help our testing"):** `tools/agents/local/idle_research.py`, run every 5 minutes by the WSL timer `swg-idle-research.timer` (as swgemu; unit files in `tools/agents/local/systemd/`).
  - Starts the next open topic in `Agent/local-research/queue.json` when Ollama has had no chat/generate request for 10 minutes (its own previous topic doesn't count), the GPU is under 30 % and no owner SWG client is running. `Agent/local-research/STOP` pauses it.
  - Each topic copies named Core3-dev sources (line-numbered, read-only) into `Agent/local-research/<id>/src/` (gitignored), and `local_agent.py` (one folder, no shell, no network) writes `<id>/report.md`. Status `review` means a report waits for Claude or ChatGPT to check against the source; nothing relies on it before that. One line per topic in `Agent/local-research/LOG.md`.
  - Seeded with 7 topics from current test gaps: cure poison (the class check's NO_EFFECT), doctor enhance/wounds, entertainer buffs, survey/sample, creature harvest, travel/shuttles, missions. Anyone may add an open topic.
- **Not done yet:** the leaked-copy sweep the restart cut short.

## Moved 2026-10-15 12:39 (C39: keep the newest four Log entries)

### 2026-10-15 11:25 Claude: the crew plays with the owner (Benny); planet jumps, waypoint mail, indoor following, floor plans

- **Escort live with the owner** (as Benny: Master CH + Rifleman + Marksman, `Documentation-support/benny-ch-rifleman-macros.md`, server-best gear macros). Owner chats with Claude in game: `/tell Esk` (Claude watches Esk's log).
- **Dev `0bf4ad1d`, `425e8590`** (test galaxy restarted 10:45): `/agentgear goto` (the crew follows across planets), `mail` (waypoint attachments: the dungeon list), `vehicle` (swoop) and `mandohelmet` kits. Death Watch mines poison anyone without the Mandalorian helmet or an "Advanced Rebreather" in the eyes slot.
- **Pathing** (owner: "the bots are hitting walls"): measured against the bunker's floor meshes, bots stood up to 2.5 m inside walls because escort aimed for formation slots beside the player. Indoors they now walk the player's own path, single file (`30898fe`); outdoors walk timeouts scale with distance and a pinned bot jumps to the player (`3d766d1`).
- **Floor plans** (owner: "actually track them and map the navmesh"): `tools/navmap.py` builds a building's floor plan from the client's floor meshes; http://localhost:8765/floor shows walls, every bot inside with label and trail, the escorted player and stuck spots (`aa213a6`). Built: Death Watch bunker, Warren, Geonosian lab.
- Pets obey trained chat phrases (`PetManager::handleChat`): the 17 "missing" Creature Handler pet orders are trainable commands, not slash commands.

### 2026-10-15 10:05 Claude: wounds fixed (afflict restore); Doctor 5/7 works; dungeon crew Forn; live labels on the tracker

- **Why every Doctor ability was BLOCKED:** the bots carried wounds nothing on the test galaxy removes. Each clone adds 100 per pool (`PlayerManagerImplementation.cpp:1823`), afflict staging adds more, and regen stops at max minus wounds. Jesh had 499 mind wounds of 500. **`/agentgear afflict restore`** (dev `407db849`) clears wounds, shock, DOTs and states and fills HAM; all 18 bots were restored at 09:26, and class-check's `rest()` asks for it.
- **Doctor (C33b), third run:** 5 WORKS (curePoison, extinguishFire, cureDisease, healEnhance +200 in the hospital, revivePlayer on a patient that really died), registerWithLocation RAN, healState BLOCKED (the dizzy pack still did not arrive; open). Setup added (`8bb6e70`): hospital cell for healEnhance/registerWithLocation, a dead patient for revive (third incapacitation), spare copies banked, never dropped. GPT's C33b work committed in `090c1dd`. 69 offline tests.
- **Fixed-scenario round (09:38):** aurek-doctor-buffs **10/10** (it ran no checks before); besh-gather 14/16 (moisture and wind found no concentration); dorn-social 9/12 (Nima's /watch: no line of sight; the known leash miss); cresh-missions offered 36 missions but none it could take (open).
- **Dungeon crew Forn** (owner: "give me a crew and we can test their combat more and their movement and mapping"; `64a83b8`, `b2a3206`): five bots on accounts forn1–5 with full 250-point templates from the server's skill table (Squad Leader/Rifleman, Fencer/Pikeman/Medic, Teras Kasi/Fencer/Medic, Commando/Rifleman, Doctor/Combat Medic). `tools/bots/crew_combat.py` fights with real special-attack rotations; the body's own fight reflex only sends the default attack in melee. New kits onehand/lance/knuckler (dev `0901664a`). Builds, dungeons and monster levels: `Documentation-support/dungeon-builds.md`. Round 1 (`forn-crew.py`) runs after the restart.
- **Tracker** (owner: "relabel the tracker so i can read what everyone is doing ... closer to a live view"): every bot command writes what the bot is doing and its own position (`/var/tmp/swg-bots/now`); the map labels every marker and row, uses the fresher position, refreshes every 1.5 s; who.json every 2 s (dev `bb51ec97`). Readable snapshots in `Bot-reports/tracker/<hour>.txt` (48 h, not in git; bots only).
- **Damage repaired:** at 08:55 a research agent's command overwrote `ActivateQuestCommand.h` in the dev tree with three lines of grep output; restored from git (a copy of the damaged file is in Claude's scratchpad).
- **Valve research** saved in `Documentation-support/valve-open-source-assets.md`: Wine + DXVK runs our client (it is 32-bit Direct3D 9, not large-address-aware); Valve's wiki allows first-party assets in non-commercial fangames (low value for us).
- Test galaxy restarted ~10:05 on dev `bb51ec97` with the crew accounts (owner offline). The cycle stays paused.
- **Escort mode** (owner: the crew was meant to run with them; it can lead into a crew vendor and solo features): `tools/bots/escort.py` + `scenarios/forn-escort.py`, see the task row. The owner wants Creature Handler play data: their build is Master CH + Rifleman + Marksman (246); the escort logs the combat around them to `Bot-reports/play/`.
- **Forn round 1 (10:20): 21/22.** All five templates granted and confirmed, role weapons in hand, hospital buffs +200 (7 of 8; Mirren likely ran out of mind on the last), three kills (13, 6 and 6 s), nobody down; Mirren healed Forn from 29 %. The plateau only had scyks, so the fights were too short to test rotations or the tank: next is harder content (the Warren on Dantooine). Fixed meanwhile: cresh-missions read the empty waypoint of listed missions (`ab0fbbc`), the dizzy pack name for healState (`66aae60`), Nima's /watch line of sight.

### 2026-10-15 09:10 Claude: 13 mechanics reports; scenario fixes from them; relay lanes; C33b taken over (GPT out of usage)

- **Research (owner: "another haiku to research crafting, resources, OQ, and faction", "add the HAM and lacking professions"):** 13 reports in `Agent/local-research/<topic>/report.md`, status review; **start with `Agent/local-research/FINDINGS.md`**. Written by Haiku agents and finished by Opus after a session restart. The first run hung for 40 min because its searches went through the WSL network share (`\\wsl.localhost`); the reruns grep inside WSL.
- **Scenario fixes from them** (`1c301a4`, `adc67da`): cresh-missions accepts destroy missions up to 2300 m (the 600 m bound refused every one), uses general terminals only, follows the moved waypoint and checks the bank payout. besh-gather skips the organic tool (toolType 0 on this server), treats an empty gas/moisture/wind list as server state, and checks mind. dorn-social has a real entertainer buff check (70 s watch). aurek-doctor-buffs walks into any hospital cell (checked live: the trainers stand in cell 9655496) and waits out the 20 s cooldown. **The gate will call the changed checks NEW, not regressions.**
- **GPT relay tuned** (`c403b6b`): a bots lane and a desk lane (one task each), a memory guard (6 GB commit headroom), one retry for an early crash, recovery of orphaned "running" tasks. Status shows lanes and memory.
- **C24b done** by GPT (08:07, `4458b42`). **C33b:** GPT hit its usage limit at 08:59 (resets 12:01) halfway. Claude took it over (63 offline tests pass) and runs science_doctor on Aurek; Aurek stays out of the squad plan until that run ends. Queue: only C36 (names sweep) is open, for 12:01.
- **Remote Ollama** (helper session; `ebadb4f`, and part of `7674330` by a shared-checkout slip): OLLAMA_URL/MODEL/CTX settings, remote idle detection, `tools/agents/local/REMOTE-OLLAMA.md` for the friend's PC (tomorrow). `qwen3:8b` pulled (owner): it runs fully on the GPU, but its research is too weak. Idle research stays paused (`Agent/local-research/STOP`).

### 2026-10-15 08:15 Claude: regression gate; C34r in dev and passing in game; a route for the month; board trimmed

- **Regression gate (route, week 1):** `tools/bots/gate.py` checks the server (running, initialized, dev commit, archive), logs in missing bots, runs one 10-minute round of `Agent/squad-plan.txt` without fallbacks, and compares every check with its own history (`Bot-reports/gate/baseline.json`, seeded from recent reports). A check that passed before and fails now is a regression and fails the gate; flaky, fixed, new and still-failing checks are listed; a scenario with no checks or a BLOCKED note is a WARN line. Verdict: **`Bot-reports/GATE.md`; read it first after any restart.** First gate 08:02: **PASS**, 27/28 (the known leash miss). Aurek's doctor scenario runs no checks at all (BLOCKED: no hospital treatment anchor), so it now shows as WARN. Offline tests `tools/bots/test_gate.py`.
  - **`overnight_cycle.sh` changed** (its header asks for a board note): step 4 runs `gate.py start` once per server start (`gate.py due`) instead of a squad round, and every cycle entry carries a 'Gate:' line.
- **Local model:** owner pulled `qwen3:8b` (5.2 GB): 100% on the GPU at 32K context, 1 GB of RAM (10.6 GB committed, against 22.6 GB for gpt-oss:20b). Its creature-harvest report is weaker (1.7 KB, never opened the C++ file), so it suits light jobs; mechanics research waits for gpt-oss:20b on the friend's PC (tomorrow). Idle research stays paused until then.
- **GPT queue:** C24b (running again since 08:01), then C33b (class-check staging for cures plus the Doctor rerun, owner wants bots first), then C36 (names sweep).
- **C34r** (`19cfb3a5`): reviewed (potency -1 is Core3's own "can't be resisted" path, `DamageOverTimeList.cpp:124-126`), cherry-picked as dev `90044b8e`, built. Test galaxy restarted 07:33 by resume after the 07:01 squad round (no owner client, client config on 44453); `squad.py setup` 18/18.
  - Probe `scenarios/claude-probe-c34r.py` on Aurek: poison, disease, fire and bleeding 10/10 each plus one on self, no errors (`Bot-reports/Aurek/20261015-073623-claude-probe-c34r.json`). The old roll would pass that about once in 9,000 tries.
  - Cure retest (class check science_doctor, 07:38, 11/11 checks): the grant works, but every cure was BLOCKED by staging. The tester's inventory was full, so medicine2 came without its cure-poison pack, and the allies were out of the tester's view ("in another scene") after setup spread them around Mos Eisley. curePoison stays untested: a C33 follow-up (gather the group, make inventory room) for GPT. Aurek driver: ChatGPT C33b (08:31), removed from squad plan; waiting for active rounds before commands.
- **C30** was already in dev as `80b66e65` (cherry-picked 01:40 without -x), so cherry-picking 6f25b704 came out empty. Its names are in archive `8ad04fec`; the habitat visit is still open.
- **C33** committed: the class-check scenario (GPT, finished by the Sonnet helper) and its 52 offline tests.
- **Route for the month** (owner asked how to get the most out of the Max plan in the first month; awaiting the owner's OK): `SWG-roadmap.md`, "Route for the first month". Lanes, waste to cut, four weekly milestones.
- **Board trimmed** from 150 KB to about 50 KB: log entries older than the newest four are in `SWG-handoff-archive.md`. The task board and the C-task instructions still hold about 38 KB; finished rows go next.
- **Windows ran out of memory at 07:31** (commit 50.2 of 51.5 GB, 0.7 GB free; the Ollama runner held 22.6 GB, WSL 12 GB). That crashed GPT's C24b run at once ("memory allocation failed") and very likely restarted this Claude session. Owner, 07:57: the names sweep moves to GPT (C36, after the C24b retry): the local sweep is stopped at 1,037 of 1,979 chunks, the model unloaded, idle research paused (`Agent/local-research/STOP`; delete it to resume). Commit is back to 27 GB. The local model should run on the friend's PC (helper session on remote-Ollama support) or after a RAM upgrade.
- The 07:31 cycle saw the galaxy down mid-restart and wrote its own restart, which (as at 06:35) never ran from the detached shell. Harmless this time; a restart must not overlap a cycle slot (:01/:31; the scheduled-task list's next-run time was stale).

### 2026-10-15 08:06 ChatGPT: C24b re-review complete

- Reviewed dev `98ad1d1d` + `3a0b154f` at `90044b8e`: R2-F1 resolved in source, no new blocking source defect; 16/16 offline checks (20,000 multi-zone cases/five loads, rounding/caps/defaults/top-up), inventory refreshed to 74 rows. `Documentation-support/hoth-release-gate.md` stays NO-GO: C23/client/owner gates open. Backfill is conservative migration, not exact creation-time odds (comment clarification for Claude). Repeated-start persistence and gameplay untested here; no builds/restarts/bots/server edits. Next: Claude runtime evidence when scheduled; GPT queue per latest inbox. Review/tools and handoff recorded in this local commit.

### 2026-10-15 07:09 ChatGPT: C34r review complete

- Reviewed dev 60ed8971 + 9b93665d: one P2 (silent random DOT staging failure), fixed on gpt/work in 19cfb3a5 after dev merge cb4e2b9e; report `Documentation-support/review-C34r.md`. Extracted-code regression: missing DOTs 84/404 -> 0/404, swimming/fire errors 0/101 -> 101/101; 63 kit paths registered. No demonstrated gate bypass/crash defect; full build/in-game checks untested here. Claude: review/cherry-pick 19cfb3a5, build/test; dev, bots and runtime untouched.


## Moved 2026-10-15 12:49 (C40 housekeeping)

### 2026-10-15 12:05 Claude: test-galaxy dev tools: tame anything, buffs anywhere, dev datapad = full character builder, /goto back

- Test galaxy restarted 12:01 on dev `81384b90` (all below live; Core3.TameAnything and Core3.MedicalAnywhere are set by test_galaxy.py and only read on a `_test` database).
- **Taming** (owner, in game): any creature, any age or level, always succeeds (`6063ecc8`); the admin force tame already existed (`/tame force`, `/tame adult`). **God mode** has no pet count or control limits when taming, calling, using deeds or receiving pets (`90e54a47`; not test-only, staff in god mode only).
- **Doctor buffs anywhere** (`81a5f056`): a doctor counts as by a top surgical droid (rating 100) where there is no hospital, camp or droid; the rating also scales buff power. A real surgical droid needs a crafted medical module (later). Crew order "buff": Mirren enhances the player's six attributes (`908abd9`).
- **Dev menus** (`a6be1f41`, `480dd8f`): the sandbox test datapad is a full character builder (radial "Character builder"); its spawner lists all 1052 creatures by folder and page (`tools/sandbox_menus.py`); the builder menu lost 113 MTG duplicates, is sorted and paged at 50, has a Pets menu (70 creature, 26 droid deeds) and agent-written section descriptions.
- **`/goto back`** (`81384b90`): god-mode players return to their spot before the last jump (recorded in switchZone, kept across restarts).
- **Pathing note (owner, screenshot 12:05): Esk stands on a roof ledge at the Mos Eisley starport.** Claude's label test (10:5x) walked Esk to 3536 -4796 with no height; the move reply gave z 9.5 where the ground is about 5. A walk without z takes the highest floor at that x, y (a roof or ledge) instead of the ground the bot walked on. Fix for the bot body or /agentpath: keep the height of the walked path (or the terrain/navmesh floor nearest the current z), and send Esk down. Open.
- **Mistake fixed:** a `>` inside a `wsl … grep` pattern became a redirect and overwrote ObjectManager.cpp (restored from git before any build went out). `wsl` re-parses its arguments: no `> < | $ ( ) #` in them (memory updated). The morning's ActivateQuestCommand.h damage fits the same pattern.

## Moved 2026-10-15 17:40 (C43 closeout; older Log entries)

### 2026-10-15 14:00 Claude: test galaxy restarted for the full fleet (owner: "restart and ... deploy the full fleet")

- Restarted 13:5x on dev with `BotPop=true` (ready in 66 s, 0 error lines). The botpop scale series (owner OK earlier) was stopped at its 500 step for this; its 100 and 250 results stand (`Bot-reports/botpop-scale-test.md`).
- Up now: 23 squad bots, the Forn escort run (20261015-135721, waits up to 3 h for Benny), 77 load bots (`load_fleet.py step 77 60 7200`: 2 h of fights with the memory guard), and the server-side population at 500 throttled, going to 1,000 only if the load average stays under 9 of 12 threads. Results: `/var/tmp/swg-bots/load/*fullfleet*`. Client logs over 200 MB are emptied every 5 min for 4 h.
- Earlier today: the crew answers every order, Mirren's heal loop, Forn's crouch (`dd9febe`); `/tame train` (dev `398744b5`); the pet follow gap (dev `57a52553`) is live since 13:26 but untested in game.
- **Full fleet result (14:05):** 100 client bodies + 500 server-side bots (165 active, throttled). core3 3.9 cores avg (4.7 max), 4.8 GB; WSL 10.1 GB free, commit headroom 9.3 GB; chat 107 ms avg, 450 ms max; no safety stop. Load average reached 10 of 12 threads, so it held at 500 and did not go to 1,000: CPU binds first, as projected.
- Open: Benny's "disengaging scripts brok" (asked in game, no answer yet); "better zoom" (client side).

### 2026-10-15 13:55 Claude: server-side population bots (/botpop), milestone 1 built; 100 and 250 measured

- Owner's go 13:00 (Claude weekly usage 83%). Dev `e6749a9e` (SuiPageData::sendTo null guard) and `7f58804d` (`/botpop`), both on the test galaxy since 13:39. All bot code is in `src/server/zone/managers/botpop/` (header-only, movable into a TortoiseBots fork). Core3 hooks: the command registration, the observer flag (AiAgent insert/disappear, SpawnArea position update) and `ClientlessLogin.h`, the one login/logout boundary. Sagiroth's TortoiseBots is the design reference; no code copied.
- `/botpop spawn N [here|mos_eisley|coronet|split] [radius] | despawn [N|all] | status | mode [all|throttled]`; `_test` database plus `Core3.BotPop = true`, then god mode or an AgentAccounts account. Bots are transient `Popbot<n>` player characters with no client, rows or account; they wander the navmesh, sit, emote, fight back. Throttled mode: only bots near a real player (150), a rotating 50 and fighters act, and they don't wake AI or spawns. All mode: every bot acts and counts as a player. One `[BotPop]` line a minute in core3.log.
- Measured (throttled, split Mos Eisley/Coronet, 23 squads idle): 100 bots: 1.26 cores, 4.57 GB; 250 bots: 2.03 cores, 4.78 GB (4.52 GB with none); about 0.005 cores and 1.4 MB per extra bot; chat round trip 80 ms; no errors. Report: `Bot-reports/botpop-scale-test.md`; driver `tools/bots/botpop_scale.py` (load_fleet.py's sampler and memory stops).
- **Not done:** 500 and 1,000, the all mode, the 30-minute 1,000-bot hold and the class check alongside. The main session stopped the series at 13:51 for the owner's full-fleet run; it uses `botpop_scale.py` with BotPop on. About half the walk attempts find no path (not investigated). Escort run: halted twice for /botpop restarts (owner OK) and restarted each time until 17:47.

### 2026-10-15 13:50 Claude: name filter: only non-name words stay out (test galaxy)

- Owner: "non name names can stay out, but censors can begone". Core3's active name list (`oldFilterWords` in `bin/scripts/managers/name/name_manager.lua`) matched every entry anywhere in a name, case-insensitively, so plain entries like "ec", "ct", "dev", "gm", "mod", "christ" and "ass" refused Rebecca, Hector, Victor, Devon, Sigmund, Modesto, Christopher and Cassandra (23 of 319 common names). The unused `filterWords` list was worse (refused Jesse, Felix, 4 bots; let GM and Dev through).
- Dev `d1cd02c6` (Lua only, appended to name_manager.lua): the default table is rebuilt from stock. Profanity, slurs and religious names dropped; ranks, titles, species, staff and game words kept as reserved; canon names kept as fiction; plain words match whole words only; Admin, Administrator and Moderator added. Offline: 1 of 319 real names refused (Carl, a stock canon entry), no bot name, no swear word. Stock list kept as `stockOldFilterWords`.
- **On the test galaxy now** without a restart (console `reloadmanager name`: 634 -> 466 patterns). Not yet tried in game with a character name. Live needs the owner's deploy OK.
- 13:50, owner: "Allow canon names too". Dev `0f045a47`: the default table keeps only stock developer and reserved entries (whole words), the non-name words stock filed as profanity, and Admin/Administrator/Moderator: 71 entries. Offline: no real name (319), bot name (100), canon name or swear word refused; every non-name word refused. The test galaxy (restarted by another session at 13:48) loaded it at 77 s: `Loaded 71 regex filter patterns`. Slurs now pass too; the owner was told.

### 2026-10-15 13:18 Claude: fleet-scale test, 100 bots run comfortably (recommend up to 100)

- 23 -> 50 -> 100 bodies fighting on Tatooine/Naboo/Corellia: core3 0.89 -> 1.22 -> 1.49 cores, 4.76 -> 4.87 GB; bodies 1.28 GB RSS (370 MB PSS) at 100; WSL MemAvailable never under 10.0 GB, commit headroom never under 11.6 GB; chat round trip flat 81 ms; no lag lines. No galaxy restart: the load bots need no AgentAccounts, so the Forn escort run kept going. Report `Bot-reports/fleet-scale-test.md`.
- New `tools/bots/load_fleet.py` + `load-groups.json` (77 plain bots, Grek-Qek, kept out of groups.json). Watch for long big runs: each fighting body writes ~2 MB/min of client log to /var/tmp (12 GB/h at 100); `load_fleet.py down` deletes them.

### 2026-10-15 13:07 Claude: plan to fork TortoiseBots with the new public repo

- `Documentation-support/tortoisebots-fork-plan.md` (`7128ade`; roadmap row B8). Fork Sagiroth's TortoiseBots on GitHub when the new public repo is made. The fork's `main` mirrors upstream; a `swg` branch holds our Core3 module in a new `swg/` folder, pinned as a submodule in the new repo. Core3 keeps only the hooks and builds with the module off.
- Port only Sagiroth's original AGPL work for now: the host boundary, `BotTurnScheduler` and `ActionFailureBackoff`. The engine waits on TortoiseBots' open licence audit (its `cmangos/playerbots` lineage is unresolved). The attribution term needs credit in `core3.log`, at login and in `/bot about`. A fork of a public repo is public, so every push gets the export checks. Owner decisions: fork name, submodule vs in-tree, and whether to ask Sagiroth about the engine files.

### 2026-10-15 13:05 Claude: the bot tracker is now a fleet dashboard (http://localhost:8765)

- The owner sent three screenshots of a WoW bot dashboard as the look they want. `tools/live_map.py` now has a sidebar and six pages:
  - **Overview:** bots online, players, bots indoors, issues and squads.
  - **Bots:** all 100 roster bots (groups.json plus the fleet test's load-groups.json). Search takes fields such as `planet:naboo prof:rifleman doing:stuck squad:forn role:healer`, with Online/Offline, state and profession chips. Click a bot to see species, professions, combat role, planet and area, what it is doing, health/action/mind bars, credits, target, gear, XP grants per hour, and an Activity tab (recent labels, refused commands, falls). "Show on map" centres the map on it.
  - **Map:** each planet's own map image, decoded from the client's `ui_map_<planet>.dds` and cached in `/var/tmp/swg-bots/mapimg` (not in git). Planet tabs and area chips with counts, dots coloured by profession with a legend, a path-trails toggle, and "N bots indoors" linking to /floor.
  - **Activity:** each squad's state and every change of a bot's label. **Issues:** stuck now, dead or incapacitated, refused commands (squad reports, last 24 h; escort play data). **Server:** uptime, who.json, and core3.log error lines with repeats folded and IPs removed.
- Bars, credits and target need a small `tools/bots/squad.py` change (same commit): a bot now publishes them from its status and fight replies. Running squads pick it up on their next start; until then the panel says "not reported".
- Labels, /floor, the tracker logs and the 1.5 s refresh are unchanged. All assets are inline (no CDN). Tests: `tools/test_live_map.py` 11/11. Tracker restarted 13:05 as a plain background process (log `/var/tmp/swg-bots/live_map.log`), not the `swg-live-map` unit. Nothing under /opt/swg was written.

### 2026-10-15 12:57 Claude: research: what 1,000+ bots would take (server-side bots)

- `Documentation-support/server-side-bots.md` (`ef46438`), research only. WoW playerbots scale because each bot is an in-server player with no socket, and by default only about 10% are active. Our one-client-per-bot design tops out in the low hundreds (estimate; the fleet test is measuring it). Core3 already drops packets sent to a player with no client. The gaps are a client-less login, a driver, an active-bot budget and one unguarded `SuiPageData::sendTo`.
- Recommendation: a hybrid. Real-client squads stay for tests; server-side bots provide population. Milestone 1 is about 5 days on Core3-dev: `/botpop spawn N`, a wander and fight-back tick, the active budget, then measure 100 to 1,000 bots. Nothing is built; it needs the owner's go-ahead.
- 13:00 (`4d14de7`): Sagiroth's TortoiseBots is now credited by name as the comparison point. The owner says Sagiroth gave permission and has no SWG ties. A correction from TortoiseBots' own source: it ships with every bot fully active and throttling is opt-in, so the gain comes mainly from bots living inside the server with no client. Milestone 1 now measures both modes.

### 2026-10-15 12:49 ChatGPT: C40 roof-floor source fix ready

- Server `7c68e39f` on gpt/work after dev merge `7df4f2c7`; h `e86fcf7`: nearest outdoor floor, route-relative samples, explicit world-z forwarding, safe missing-height errors and escort trail-floor preservation. Report `Documentation-support/C40-roof-ledge.md`. Offline: Python 6/6, existing escort 11/11, compiled actual selector 7 assertions; old 9.5-vs-5 choice reproduced with synthetic surfaces. Unbuilt/game-untested; Claude reviews/cherry-picks/builds and verifies roof descent plus bunker/Warren escort. No bots, restarts, deployments or downloads. Source slice idle.

### 2026-10-15 12:45 ChatGPT: C42 Fable return prep complete

- Docs commit `8c795f7`: `Documentation-support/fable-return-brief.md` (18 folders, 842 words), `owner-decisions-for-fable.md`, `board-housekeeping-1015.md`. Checked dev HEAD `398744b5`, README/owner-answer records and archive hashes: installed client/server both `8ad04fec`; Local-content copy remains `aee83cc6`. Chiss played; E0 visual/habitat/full gameplay acceptance UNVERIFIED. References/CRLF checked; no downloads, bots, restarts or writes under /opt/swg. Next: owner decision batch, then Fable design and delegated mechanical checks. Housekeeping proposals unapplied; oldest 11:40 log preserved in archive, newest four retained. Board/log record committed separately.

### 2026-10-15 12:40 Claude: the crew answers every order; Mirren's heal loop and Forn's rubber-banding fixed; /tame train

- **Owner in game, 12:15-12:25: "things dont seem to be working", "Forn is rubber banding kinda bad".** Three bugs, all in `tools/bots/` (`dd9febe`):
  - Orders were heard, but only the leader (Forn) could answer them, and he skipped any line another bot heard first. Benny's heal, buff and status got silence. Now the bot that hears an order answers it, and a tell gets a tell back. `invite` is queued for the leader, the only one who can invite. New order `help` (also `commands`, `orders`) lists the orders. `passive` now also sends `/peace`.
  - Mirren sent heals 65 times at a patient she could not see, and 19 times at herself with only wounds left. She never stopped "healing", so the buff order never ran. Now a refusal leaves that patient alone for 15-60 s, and low mind rests her for 20 s; she buffs or fights in the meantime.
  - Forn was crouched, and the server puts a crouched bot's steps back. Every bot now stands before walking.
  - Tests: escort and combat 12/12 (4 new), class-check 70/70. The crew run restarted with the galaxy (run 20261015-123727) and waits up to 3 h for Benny (`ESCORT_WAIT`, `36a249f`). Esk mailed Benny a one-line note with a waypoint to the crew.
- **`/tame train` (owner, in game: "can you train my pets"; dev `398744b5`, live: test galaxy restarted 12:36, ready in 86 s, 0 error lines, Benny offline):** god mode, no target. Every called pet learns every command it has no word for yet:
  - the doc's words: sic, heel, stay, guard;
  - plain words for the rest: store, friend, follow other, trick one/two, patrol, patrol point, clear patrol, wedge, column, special one/two, ranged, group, transfer.
  - Words Benny trained are kept. God mode also always passes the training roll when training by hand.
- **Owner's notes from play, open:**
  - pets need a follow distance that depends on their size (the AI's follow range is in `ai/bt/leaf/FollowActions.h`, `UpdateRangeToFollow`);
  - better camera zoom in and out (client side);
  - "disengaging scripts brok" (asked in game which: the crew not stopping, or Benny's macros).

### 2026-10-15 12:39 ChatGPT: C39 review complete

- Reviewed 90044b8e..81384b90: 1 P1 / 4 P2 / 2 P3; report `Documentation-support/review-C39.md`. Source fixes on owned gpt/work after merge 22408da4: d8c9d668, 1b276fa4, 6647e5f8, b556c061, a9fb5cfe (Claude review/cherry-pick in that order). Offline gates, 432 medical cases per pack, paging/stale-cell Lua checks and six Lua syntax checks pass; restored files match baseline blobs. Full server build/gameplay/restart persistence untested. Dev/runtime/bots untouched; later dev 398744b5 is outside scope. Source slice idle; next: Claude review and separate acceptance. Older logs moved to the archive; newest four retained.

## Moved 2026-10-15 22:57 (C44; newest four Log entries retained)

### 2026-10-15 16:51 Claude: StarCraft as inspiration for the Vong, the Gree and the Starweird (legal check)

- `Documentation-support/starcraft-inspiration-vong-gree.md`. Legal verdict: **ideas and mechanics yes; no StarCraft files and no StarCraft fan assets** (Blizzard art and its derivatives; custom content reportedly assigned to Blizzard; already excluded by AGENTS.md's rules for other games' assets). Screenshots stay private and out of the repo.
- Ideas in Star Wars terms:
  - Vong: worldshaping zones, a damutek dungeon for Nei Rin's voxyn line, coral-implanted prisoners at Krayt's Ossus garrison, living gear, a yammosk raid with dovin basals.
  - Gree: sensor obelisks, attunement relics with colour and tone puzzles, shield constructs keyed to a damage type, stasis traps.
  - Others: the Starweird as a rare anomaly encounter; Killiks as a hive dungeon.
- **Owner: wait, no prototype yet; art inspiration only.** The Zerg look is the starting point for the Vong (made Vong with coral, crab armour and scars), and the Protoss look is the starting point for the Celestials (gold and teal, floating crystals, glyph lines; Gree tech can borrow it). The mechanics stay ideas on file.

### 2026-10-15 16:40 Claude: C39 and C40 fixes in dev, built, gated; the mercenary broker stood on a roof

- Owner (16:00): fix the open C4d/C4e/C19 findings, review C25/C26, then build, restart and gate after the escort run, with C38 after the gate. Those findings and C22's were already fixed in dev on 14 Oct, and C25/C26 were already reviewed and merged; their rows above were stale and are updated. The open work was GPT's C39 and C40 fixes on `gpt/work`.
- Reviewed and cherry-picked (`-x`) into dev: C39 `8a00b08b` (sandbox datapad, TameAnything and MedicalAnywhere only for god mode or agent accounts on `_test`; 2 s online log only on `_test`), `01b94e13` (unique builder page titles), `f5462270` (/goto back rejects stale cells), `e5c56727` (rejected waypoint mail is an error), `1f8982f3` (MedicalAnywhere keeps the city bonus); C40 `b587e530` (bot walks without z use the floor nearest the bot, not the roof).
- Claude's follow-ups: `b9653a73` /goto back checks the cell under its lock but releases it before switchZone, which takes the zone lock. `fe188e31`: C40 refused every move without z or route, and `load_fleet.py:234` sends exactly that (`path=False`), so all load bots would have stopped; an explicit `path:false` walks as before.
- Changed for players on the test galaxy: TameAnything and MedicalAnywhere now need god mode or a bot account.
- Owner (16:05): halt the escort run, read the data, restart. The run halted cleanly at 16:06 (11/11 gear checks; Benny never logged in, so no escort play). Server log of the 2 h 15 min session: clean exit, no crash, 13 warning lines. Built in 33 s (core3 + core3client), restarted 16:13 (ready in 70 s).
- Gate 16:19 FAIL, 29/35: one regression, "Dax offers options". Cause: `sandbox_mercenaries.lua` spawned Dax Venn at `getWorldFloor` (the highest surface), on a roof 16.4 m over the 5 m street at 3552,-4782; bots reached him only through the old highest-surface walk rule that C40 removed. Fixed in dev `80895f63`: he is moved to the terrain, and hired mercenaries spawn at the player's own height (they used the same call). Restarted 16:27.
- Gate 16:31 FAIL, 22/35: Dax fixed. The new "regressions" are not the build: (1) the four doctor-buff checks say "You re-apply ... enhancement" with max HAM unchanged: the buffs from the 16:19 run were still on (history PF); (2) "the server keeps putting us back" on Besh, Cresh and Esk routes (10 put-backs; none in the 16:19 run; the same Esk plateau route had 5 per run at 08:08 and 08:11 on the old build; Cresh's crew was in a fight, Ilsa died). A direct probe walked Tovan 118 m up the plateau with one put-back before the 150 s limit. Still failing as before: the 12 m leash and Nima's dance line of sight.
- C38's dispatch moved to 17:40 (after the gate, once Codex is back at 17:29). Doctor-buff artefact and the put-back history are in GPT's inbox.

### 2026-10-15 14:45 Claude: first outside-art prop staged (F86): a CC0 ruined wall, in the test archive, ready for the owner to look at

- Done: Blender 3.6.23 (portable, official site, hash matches), the SWG add-on, texconv and the Quaternius Ultimate Modular Ruins pack (CC0, via the author's Drive folder; the per-file links hit Drive's quota, the folder's Download all worked) are in; recorded as F86a/b/c in `Content-catalogue/archive-downloads.json`. `Wall_Broken` (976 triangles) converted to `.msh`, `.apt`, two `.sht` and two DXT1 `.dds`, and added to the client's `local_planets.tre` (166 -> 173 entries, read back exact, reference closure OK; previous archive saved as `Local-content/old-client-local_planets.tre.8ad04fec`).
- How the owner sees it, no server change or restart: the piece replaces the stock campfire log's appearance, so `/createSpawningElement spawn object/static/structure/general/campfire_fresh.iff` in a test session shows the wall. Steps: `Fable-asset-pipeline/how-to-view-first-ruin.md`.
- Findings: the pack has no texture atlas (two flat material colours, no UVs), so the textures are flat colours; the exporter writes no collision (walk-through), as the plan expected. Not done: own object template, CRC entry and server Lua (needs a restart by the galaxy owner), LODs, a stone texture.
- **Verified in the owner's client, 14:46** (screenshot by the main session via `um win shot`, kept out of the repo): the wall draws upright at Mos Eisley with both tones, no black or white block, no crash, 30 fps. Collision not checked. Any session that rebuilds `local_planets.tre` from its own staging drops these files: re-run `Fable-asset-pipeline/stage_ruin.py` (inputs in `Fable-asset-pipeline/converted/`).


## Moved 2026-10-16 03:47 (task status check)

### 2026-10-15 22:40 Claude: launch simulation run 4, overnight (missions, Ossus explorers, real purse)

- Run 4 stopped at 22:07, five minutes in, on the first bot mission: `MissionObject::setMissionObjective` asserts the mission is locked. Bots now lock it as `MissionAcceptCallback` and `MissionAbortCallback` do (dev `17cacd70`). Rerun: 710 missions taken in 10 minutes; all 18 starting cities have an outdoor general terminal. The unpaid "mission_gone" rows at its end were the despawn.
- Owner, 22:20: bots get the creation purse (10,000 cash, 100,000 bank) and pay trainers as `trainerConvHandler.lua` does (dev `7bd915b6`; row "broke" when short). Overnight run since 22:26: purse and training charges confirmed; 159 mission lairs spawned in 12 minutes, none destroyed yet. Level 1-2 bots take missions up to level 10 and are incapacitated by the lair defenders; left as is (owner: no restart without asking).
- Reports (all four in): server rates `c213e8c`, starter economy `8cc38b7`, pacing `8878023`, spawns `a961ef8`. Owner decisions tomorrow: purse and training cost, per-type XP, the spawn level gate and five data edits.
- Census tool `667725f`: Ossus export at 00:20 to `Bot-reports/launch-sim/ossus-census.md`. Fable's scheduled 00:32 job (after the 22:05 Hutt run ends) places Ossus points of interest and settlement flats on it, in `Fable-ossus/o7`. C38 stays paused until the simulation ends.


## Moved 2026-10-16 03:58 (C46 staging)

### 2026-10-15 22:57 ChatGPT: C44 independent launch/mission review complete

- Review commit `2de5175`; reviewed dev `024a4bdc` through `7bd915b6` read-only: `Documentation-support/review-C44/C44-review.md`, 7 P2 + 1 P3 (crafting recipe collision, mission teardown/targeting, worker lifecycle, abort/payout handling, peer reads, history sets). One-bounty gate and `17cacd70` lock fix preserved in source; historical RSS slopes confirmed, cause unmeasured. No code/server/bot changes or restart; gameplay untested. Next: Claude reviews fixes and schedules client/cleanup/heap counters after the overnight run; live approval withheld. Older Log entries moved to the archive.

## Moved 2026-10-16 04:03 (C48)

### 2026-10-15 23:46 ChatGPT: C45 shared mission recipe fix ready

- Source `e75794da` on `gpt/c45-mission-recipes` from dev `40af2c78`; report/diff/tests `dfe81df` (`Documentation-support/review-C44/F1-fix.md`). Preserve shared recipes on abort/complete; final consumer cleans up. Other terminal mission types checked; 12 offline checks/1,284 model cases pass. Unbuilt (no Core3-gpt build), gameplay untested; next: Claude review/cherry-pick/build and two-/three-mission tests, plus existing full-datapad gate. No dev/test-galaxy writes, bots, restarts or deploys; run 6 untouched.

## Moved 2026-10-16 04:20 (C49 checkpoint)

### 2026-10-16 02:15 Claude: night shift handed to GPT and the local model

- Since 22:40: runs 6-8 (spawn level gate and five newbie fixes `b20a46d7`; bots on missions near their level that follow the mission waypoint `41ea45b5`; C44 F2/F5/F8 `e033e8b8`; C45 recipe fix `db5952f5` + one-item delivery `74fa3e8c`; per-type XP `40af2c78`; multiclass new players `8b48a044`). Run 8: 603 missions paid by 01:50, deaths with a killer 8+ levels above the bot down from 24-33% to 7%.
- Helpers' reports: C47 report tools `3639bb2`, Hutt animation table `e55bd4d`, Ossus o7 build data `4502fc7`, C30 census check and city proposals `797d19d`, checkout churn `d815f5b`, pre-CU player builds `4cefab2`, player cities `e2e058e`, Ossus census `b589da3`.
- Owner decisions waiting: GPT's C48 morning sheet collects them. The 6-mission release still needs an in-game crafting-mission test and the full-datapad gate.

## Moved 2026-10-16 08:56 C52

### 2026-10-16 03:58 ChatGPT: C46 Discord/public map staged

- `3150acf`: anonymous public map, Windows PNG/status feed with PATCH identity, transition/watchdog alerts, 07:00 numeric digest and quick-tunnel wrapper; 53 offline tests pass, saved PNG visually checked, shell syntax clean. All runtime/delivery untested; no feed/map/tunnel started, no secrets read, posts, bots, server writes or restarts. Next: Claude reviews public mode, reloads the private map metadata and starts only after review/owner posting go; manual first-message pin. Start/stop guide: `Documentation-support/C46-discord-public-map.md`. Oldest Log entry archived.

## Moved 2026-10-16 09:01 (ChatGPT, C53)

### 2026-10-16 04:03 ChatGPT: C48 overnight checkpoint and morning sheet

- Reports `bc166df`: run 8 through 3:59 AM, 1,700 bots, 20,009 kills, 1,043 deaths, 2,358 completed missions; style/SP totals reconcile. Morning sheet lists 29 owner decisions with recommendations; watchdog has no recorded low-memory despawn, latest 6,646 MB available. 748 snapshots exceed their assigned point-budget label; cap enforcement unverified. Read-only WSL analysis only; crafting/full-datapad, Hutt/Ossus client checks and live release remain open. Next: owner decisions and Claude runtime follow-up; oldest log entry archived.

## Moved 2026-10-16 09:12 (C54; newest four kept on board)

### 2026-10-16 04:20 ChatGPT: C49 complete; C50 idle source audit claimed

- C49 source/report b5cdbb6: escort combat checks observed 3D range after approach, defers target openers, preserves target cell and resolves ID-matched leader 'me'; doctor gate accepts exact patient/attribute refresh receipts. 21 offline checks pass; all four saved false buff failures explained. No runtime acceptance claimed.
- Saved movement summary: 22 position events, 6 generic move failures and 3 timeouts across three reports; no posture events or rejection reasons. At gate pin 80895f63 the specific line-340 outdoor collision check is commented out; other causes remain unproven. Claude owns proposed bounded rejection telemetry and runtime reruns; no server/bot actions here.
- Owner says continue idle tasks while Claude lacks usage: claimed C50 to verify medic/scout/entertainer XP reports against source; no new downloads, services or server edits.
