# Additional function checks — 13 October 2026

Owner requested a couple of other functions and checking Claude's handoff. Current board still shows fixed client ab9eab6e promoted, agent v0.1 limits, and world bosses held for owner approval. Live status: sandbox920203d8, active/initialized, zero startup error lines. No server changes.

## Local spatial chat — PASS for server echo / event history
- At3554,-4782 beside Dax, say "Kael: local chat function check." returned ok; after wait2, chat event at12:11:15 PDT returned exact text, from me, self oid281474994006399.
- events history also retained the same message (seq654). Another player's reception was not tested. Only one line sent; no interaction with other players.

## Conversation range — restriction works, error feedback FAIL
- Dax oid281474994095833 stands3552,-4782. Moved to3564,-4782 (12m). talk id64 returned ok, no speech/options, no command_failed. Wait2 and status confirmed options[].
- Returned to3554,-4782 (2m); talk id67 returned conversation_start, npc_says and three choices. This controls for NPC availability.
- Missing too-far error reported as a bug because guide documents command_failed for failed commands. Do not treat talk ok as proof conversation succeeded.

## Three-mercenary cap — PASS
- Hired3: Woilowe Aitava oid281474994126384; Zaca Tzista oid281474994126395; Cilo Raedwo oid281474994126418. Nearby look confirmed exactly3 companions plus Dax.
- Fourth request at12:12:46 explicitly refused: already got three. Follow-up look retained same3 IDs, no fourth.

## Conversation cancellation — PASS
- At cap, talk then choose2 Not today. Received closing speech, empty options and conversation_end. Status options[]; look retained same3 companions. No hire/dismiss side effect observed.

## Dismiss all3 — PASS
- talk then choose1 at12:13:22. Received gone events for all3 exact IDs and Contracts closed dialogue. Follow-up look showed only Dax.

## Height observation / remaining limits
- Relog at3554,-4782 reset reported z from previous180 to16.35449. Short10m out-and-back movement retained16.35449. Earlier longer-route height discrepancy remains unresolved; no terrain/visual check or fix.
- No combat, SUI, indoor navigation, inventory/loot, surveying, crafting, tickets or new planet test this session. Those need richer agent body support. End position3554,-4782, outdoors, companions dismissed.
