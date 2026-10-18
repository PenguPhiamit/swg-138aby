# Job lists, one per worker

Started 18 Oct 2026, 8:36 AM, by Claude (owner: "start a job list for each model ... i think some housekeeping is in
order"). Whoever finishes a job ticks it here and says so on the board. The machine queues stay where they are:
ChatGPT's tasks in `gpt-queue.json`, the local models' topics in `local-research/queue.json`. This page is the readable
list across all of them.

## Where things stand (18 Oct, 8:30 AM)

- **Galaxies.** Live is stopped (owner, 18 Oct). The test galaxy has been up since 6:05 AM on run 30's build (dev
  `4b113bb7`), with BotPop 200 and the galaxy row on the Tailscale address. The owner played Hoth on it from 7:30 AM
  and found H1 to H5 (task board).
- **Usage.** Claude has used 79% of the week; it resets 22 Oct about 10 PM, so about a fifth is left for 4.5 days.
  GPT is at its 5-hour limit until 12:24 PM today; its weekly limit was reset on 18 Oct.
- **Done since the evening of 17 Oct:**
  - GPT's C62 cross-review of 47 dev commits (ultra). It found 7 problems: 5 commits need fixes, 21 are fit for live
    and 21 are test-only. It recommends stock worlds first for release 1.
  - GPT's C63 reviewed the first 20 local research reports.
  - Saluki runs on this PC with vision. The claim pass and the item check finished. Claude reviewed 14 reports.
  - Two mission bugs explained:
    - bounty lists need the player within 6 m of the terminal;
    - the shown difficulty includes the group's level.
  - Missions pass at 9 of 11 terminal types.
  - The Tailscale galaxy address works. The friend installer downloads the MTG archives.
  - The pre-push history scan and the README draft were written.
  - Housekeeping:
    - every other session's finished work committed;
    - GPT's queue tidied (C56 to C61 marked done, 8 old items dropped);
    - the board cut from 80 KB to 25 KB (answered questions and finished rows moved to the archive).

## Claude (Opus 5.5, main session; holds the server lock)

Usage is tight until 22 Oct, so reading and first passes go to GPT and the local models, and Claude does the fixes,
builds and sign-offs.

**Now:**
1. ~~**Fix C62's findings on dev.**~~ **Done 18 Oct 8:48 AM** (owner: "start the C62 fixes on dev (F1 to F6). No
   restart until I say I'm off the game"): in dev, not built. GPT re-reviews them as C65. The review is
   `Documentation-support/review-C62/C62-review.md`. F1 turned out to affect nine Hoth creatures, not two.
   - F1: two Hoth bosses (Rimefang, Old Echo) are healed by heat and electricity, because resistance values over 200
     decode to over 100%. File: `hoth_fill_creatures.lua:85,89`.
   - F2: walking the memorial road first hides Ossus's ghostfire lead for good. Files: `ossus_people.lua`,
     `ossus_people_conv.lua`.
   - F3: a pet's kill gives no job credit on Hoth or Nal Hutta. Files: `hoth_world.lua`, `hutta_life.lua`
     (`creditKill`).
   - F4: group pay still pays a member on another planet, at the old endpoint. File:
     `MissionObjectiveImplementation.cpp:277-288`.
   - F5: the new jobs erase each other's waypoints, because they share `WAYPOINTQUESTTASK`.
   - F6: a bank window that is already open ignores the alive check. File: `BankTerminalSuiCallback.h`.
   - F7 (BotPop walks through walls near a target) affects the test galaxy only. It comes later.
2. **H1: the Echo Base building doesn't draw.** **Fixed on the test galaxy, 9:43 AM (run 31c, dev `0262d8de`).**
   - The client reads all the building's file formats.
   - The cause was Core3's 192 m send range: the doors are 319 m and 627 m from the building's centre.
   - Big buildings are now sent as far as they reach, and the probe passes at the main door.
   - **It draws** (owner's screenshots, ~9:45 AM): the main door frame and blast door show. The hangar's roof
     shows, but its mouth is filled with snow. Still open: walking in, and the hangar mouth (a terrain fit, which
     needs the owner's OK).
3. ~~**The next build and restart.**~~ **Done: run 31 since 8:59 AM** (owner: "i am logged off"). Release build of
   dev `35e7dbe6`:
   - `4bae9ab1` (full-inventory pickup);
   - `aa52cc64` (bank radials);
   - the C62 fixes.
   Same settings as before: BotPop 200, Tailscale address. The log is clean (Saluki's triage, 9:01 AM).
   `PICKUP_FIX = True` is set in `tools/bots/missions.py`. **The speed check is still to come, in its own build.**
4. **Missions after that build.**
   - Bounty: Brask never walks to the terminal.
   - Rerun the group-pay check with Cresh. It needs the Marksman fighting fix.

**Next:**
5. Read the local models' output:
   - the scenario drafts, then run them (test plan section 3: trainers, vehicles, buffs, surveys, groups, bazaar,
     housing).
6. Spot-check GPT's C63b, C63c and C64 when they land.
7. H3, the Hoth weather: look again in clear weather.
8. Release 1 candidate branch, as C62 recommends: a reviewed cut, not all of dev. This waits for the owner's Hoth
   decision.

**Later:**
- the ComfyUI art handoff on Microverse (`comfy-url.txt`, an upload helper);
- the local-model bot driver;
- F7.

## ChatGPT (GPT 6.1 Sol through Codex; desk lane)

Effort: ultra for code reviews, high for report reviews, medium or lower for research (owner, 18 Oct). The
dispatcher (`next_gpt.sh` in Claude's scratchpad) starts the next open task whenever none is running.

**Queued (`gpt-queue.json`, in this order):**
0. **C66** (medium): how much is missing from Nal Hutta (owner, 18 Oct ~8:42 AM). A gap table against a stock planet,
   what blocks opening it, and one rough overall figure, in `Documentation-support/nal-hutta-gaps.md`.
0. **C65** (ultra): review Claude's C62 fixes (dev, 18 Oct).
0. **C67** (medium): the bosses in the owner's screenshot (owner, 18 Oct 9:06 AM: "do we have these? or can we have a
   session find them and see if we can use them?"). What we have, what the originals were, and what we may use
   (other servers' own bosses only as ideas), in `Documentation-support/bosses-review.md`.
1. **C63b** (high): the next 20 local research reports, from `vehicle-mount`. It was reopened because the 7:33 AM run
   hit the limit and wrote nothing.
2. **C63c** (high): the remaining reports.
3. **C64** (medium): known bugs of Core3 and of live SWGEmu servers. It also covers:
   - the 19 items with no source;
   - the unskilled accuracy penalty at `CombatManager.cpp:1980`.

**To queue when ready:**
- **H4: which Hoth resources spawn** (medium). From the config and the server's own output, read-only. The owner's
  surveys give the in-game half.

**On hold:**
- C11, archive downloads: waits on owner decisions.
- C23c, the Hoth gameplay rerun: waits for the C62 Hoth fixes and H1.
- C38, the class-check campaign: bots lane.

## Saluki on this PC (RTX 5070, with vision)

Runs by hand with queue status `here`. It yields to the owner's game client, and nothing leaves this PC.

- **Done 18 Oct 8:34 AM: log triage** of the test galaxy since 6 AM: 4,994 lines in 207 patterns, sorted in 3.4
  minutes. Claude checked the one crash-risk row (the bots' known net-status packet, which the server catches) and
  the six new rows (stock warnings). The log is clean, and nothing in it explains H1. The confirmed patterns are now in
  `tools/agents/local/log-known.txt`.
- **Done 18 Oct 8:31 AM: board trim.** There was nothing to trim (no log entries older than two days). The bulk of the
  board was answered questions and finished rows, which Claude moved by hand.
- **Next:**
  - Log triage after every restart.
  - Art checks on any ComfyUI or TRELLIS output. It is the only model that saw the crumpled crate handles.
  - A claim pass over new research reports before Claude reads them.

## Microverse (RTX 4070 Super: qwen3.6 35B, Saluki with vision, ComfyUI)

**Paused:** `Agent/local-research/STOP` (the queue finished at 3:11 AM). The owner starts runs there, because auto mode
blocks Claude from sending repo text to that PC.

- **Queued:** `scenario-draft` (qwen3.6), one first-draft bot scenario per open area of test plan section 3.
- **Owner runs:** the names delta sweep (before GitHub). The personal-details sweep ran there about 6 AM; its results
  are not reviewed yet.
- **Next, once Claude writes them as jobs:**
  - item names and examine texts for new content (Hoth rewards, Ossus loot, Nal Hutta);
  - a project search index (needs `nomic-embed-text`, a download the owner does).
- **Art:** ComfyUI batches there, then Saluki sorts them.

## Microverse (developer, with his own Claude account; not started)

- Waiting on the owner: how he gets the code (a private GitHub repository, or a git remote on this PC).
- Proposed lane:
  - art and the local models on his PC;
  - client and modding tools;
  - H2 Hoth props, as staged Lua for Claude to install.
- He never writes `/opt/swg`. His sessions follow AGENTS.md.

## Waiting on the owner

1. Hoth in release 1. The launch scope says open; C62 says hold it until F1, F3 and F5 are fixed and the Hoth gate
   passes.
2. H2: what goes on Hoth's north-west plateau.
3. H5: harvesters or outposts on Hoth.
4. Microverse's access to the code.
5. GitHub: the names delta sweep, then the new repository `swg-138aby`.
6. The BotPop social questions 1 to 3 (board, 17 Oct).
7. H1: can you walk in at the main door? And may the hangar mouth's terrain be fitted (a terrain edit)?
