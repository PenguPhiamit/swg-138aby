# SWG handoff archive

Finished task rows and older log entries moved out of `SWG-handoff.md` to keep the board short (it is read every session). Newest first within each move.

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

