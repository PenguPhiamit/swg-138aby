# C4: cross-review of dev commits (for ChatGPT)

**Reviewed by ChatGPT, 13 October 2026:** [C4 review and findings](/C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Documentation-support/review-C4/C4-review-2026-10-13.md). Review complete; request fixes for F1–F3 before combined agent/navigation promotion. Offline evidence is in `offline-review-results.json`; no live deployment authorized.

Exported 13 Oct 2026 by Claude from `/opt/swg/Core3-dev` (branch `dev`) with `git format-patch`, so the review needs no access to `/opt/swg`. Nothing here is deployed. The live agent body is still `ab9eab6e`, and the live server has none of these.

| Patch | Commit | What | Live impact if promoted |
|---|---|---|---|
| 0001 | `e1344def` | Agent body: inventory, radial menus, SUI pop-ups, mission-list request, NPC speech decode, `choose` guard, ground height | Agent client binary only |
| 0002 | `a72026b6` | Agent body: HAM/posture/states from baselines and deltas, combat log, menu option names, `inspect`, `fight`, move safety, navmesh path walking (incl. indoors) | Agent client binary only |
| 0003 | `eebdd99d` | **Server:** `/agentpath path\|height` helper (PathFinderManager + terrain); accounts in `Core3.AgentAccounts` only | **Server rebuild + restart**, plus a `config-local.lua` line |
| 0004 | `5c39f411` | **Server:** `/agentpath` heads part of the way when leaving a building for a far target | Same rebuild as 0003 |
| 0005 | `697f2002` | Agent body: keep re-planning long paths while each leg gets closer | Agent client binary only |
| world-boss/0001 | `bda2c0dd` | **Server scripts:** world boss rotation + Rhea Tannor (big game hunter) | Lua only; restart |

## What to check

1. **Ethics list** (`../../../AGENTS.md`): sources and rights, owner consent, honest reporting, fair play, secrets. Things to check:
   - no credentials in the patches;
   - `/agentpath` can't be used by normal players: the account allowlist, and `INSUFFICIENTPERMISSION` otherwise.
2. **Protocol layouts against the server.** Compare the client parsers with the server's writers (read-only, in `/opt/swg/Core3-dev/MMOCoreORB/src/server/zone/packets/`):
   - `object/ObjectMenuResponse.h`, `ObjectMenuSelect.h`, `ObjectMenuRequest.h`;
   - `ui/SuiCreatePageMessage.h`, `ui/SuiEventNotificationCallback.h`;
   - `object/NpcConversationMessage.h` and `server/chat/ChatParameter.cpp` / `StringIdChatParameter.cpp`;
   - `creature/CreatureObjectMessage3/6.h`, `CreatureObjectDeltaMessage3/6.h`, `DeltaMessage.h`, `objects/scene/variables/DeltaVector.h`;
   - `object/CombatSpam.h`, `object/transform/Transform.h`.
3. **Server helper risks** (0003/0004): CPU cost per call (findPath on demand; bots only); memory (each `findPath` result is deleted); reply size (at most 256 points); behaviour when the zone is null or the cell unknown.
4. **Anything untested** that the commit messages claim works.

Verified on the test galaxy only, by Claude:
- character builder radial → SUI → select/cancel;
- fight → kill → target "dead" event; incapacitation → death → clone SUI → cloned;
- `/agentpath` heights;
- paths: platform → greeters (partial, re-planned); greeters → cloning facility basement (62 points, 4 cells); basement → greeters (3 legs).

Not verified:
- loot;
- vehicle mount;
- mission list;
- `look` indoors (returns nothing);
- out-of-range `talk` failure event.

## How to record the result

Add a log entry to `SWG-handoff.md`: "reviewed by ChatGPT: <patches>, findings: …", and mark C4 done on the board. Findings that need a fix go to Claude as a board row. Anything that fails the ethics list goes to the owner first.
