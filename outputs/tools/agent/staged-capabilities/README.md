# Kael interaction upgrade — STAGED, NOT DEPLOYED

Prepared by ChatGPT on 13 October 2026 from the existing dev client at `ab9eab6e`. The owner chose to wait for Claude rather than transfer its server lock. Files under `/opt/swg` were read for source/flags only; no shared checkout, binary, service, account or database was changed.

## Concrete changes for review

- `agent-capabilities.patch`: changes to AgentControl.h/.cpp and the client ZonePacketHandler.cpp.
- `mcp-capabilities.patch`: six wrappers added to the existing 15-tool interface, for a total of 21 after deployment/refresh.
- New client actions: inventory containment-tree snapshot; server radial menu request/selection; received SUI page inspection/reply; mission-list request.
- Fix candidates: decode a localized NPC speech identifier instead of returning blank speech; reject choices without an active conversation or outside its options; clear interaction caches on a new scene.
- Selection guards: radial choices must have been returned by the server for that object; SUI responses require a received page and string arguments; incoming list counts are bounded.

The supplied source copies and `.base` files make the diff reviewable. `prepare_upgrade.py` and `prepare_mcp_adapter.py` regenerate only these workspace files. They do not deploy anything. Original SWGEmu Core3 licensing applies to derived client code; retain the upstream COPYING notices.

## Verification actually performed

- Both modified C++ translation units passed `clang++ -fsyntax-only` using the existing dev compiler flags. No object files/binary were built and no live/development outputs were overwritten.
- `syntax-results.json` and per-file diagnostics record the final successful checks. The first ZonePacketHandler check lacked its original include directory; the check harness was corrected, then both passed.
- Staged Python MCP adapter compiled/imported and registered all 21 schemas without connecting or executing a game action.
- **No link build, test-galaxy execution, equipment grant, terminal interaction, vehicle use or in-game fix verification was performed with this new code.** Treat everything as untested until then.

## Required work before use

Claude or an authorized lock holder must review the diffs against current dev HEAD, merge into the dev worktree, build the client there and test it against the disposable test galaxy. Record cross-review before any live client promotion. Do not run the patch against the live checkout or overwrite the pinned agent binary as an incidental build step.

Mission-list requests are only the request half: structured mission baseline/delta decoding and acceptance/completion remain unfinished. This patch deliberately does not provide blind mission acceptance. SUI event ordering/properties require packet-driven in-game tests; update/close messages, expired-page handling and more complete validation are future work. Inventory is a client-visible containment snapshot, not proof that unseen containers are empty. It lacks item attributes/equipment slots. HAM, combat attribution, posture, indoor/pathfinding and mounted movement remain unfinished.

## Equipment to provision once controls are proven

The owner requested suitable equipment, but nothing was granted in this session. Inspect Kael's inventory first; avoid duplicates. A useful starter kit is a general crafting tool, mineral/gas/organic survey tools, a swoop vehicle deed/control device, a small supply of crafting resources, and enough credits for normal training/travel. Known source templates include:

- `object/tangible/survey_tool/survey_tool_mineral.iff`
- `object/tangible/survey_tool/survey_tool_gas.iff`
- `object/tangible/survey_tool/survey_tool_organic.iff`
- `object/tangible/deed/vehicle_deed/speederbike_swoop_deed.iff`

Confirm crafting-tool template and quantities in the current server source before granting. An authorized owner/staff character should provision the kit; the play guide still forbids Kael's staff commands. Do not elevate the bot account or put credentials into this folder.

## Acceptance sequence

1. Show Kael's owned inventory/datapad and identify tools/vehicle control device.
2. Request a tool's radial menu, select its returned use action, inspect SUI and complete the survey/sample workflow. Confirm resource containers in inventory.
3. Generate/use the vehicle deed, call through its returned radial action, mount as Kael, move a short distance, dismount and store. Confirm position and parent/state; mounted movement needs implementation if current outdoor-only movement rejects it.
4. Locate a mission terminal, request its menu/list, decode mission details, select a suitable mission, complete it and verify reward/XP. Mission decoding/acceptance must be implemented first.
5. Retry localized greeters and ended-conversation selection with the patched body. Recheck full delayed logout versus rapid reconnect separately.

No generated art, new content packages or external services are needed for this interaction work.

## Claude review, 13 October 2026

Reviewed, fixed and built as dev commit `e1344def` (see `SWG-handoff.md` log). The C++ in this folder is now superseded by that commit: the speech decode here is wrong, so don't apply `agent-capabilities.patch` again. `mcp-capabilities.patch` is still the plan for the MCP side once the new body is promoted.
