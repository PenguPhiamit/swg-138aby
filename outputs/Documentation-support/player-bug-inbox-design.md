# In-game reports -> durable local inbox -> agent -> Discord

14 October 2026. Owner requests reports submitted inside the game, retained locally until an agent has capacity, then relayed by that agent to Discord. Intended group includes developer friends, experienced players and people new to SWG. **Scoped design/source reconnaissance only; not implemented or deployed.**

## Player experience

Provide a visible **Report a problem** action in the game. Prefer the native help/bug form if it works reliably with this client; otherwise use a small server SUI form exposed through a compatible menu/NPC. The exact opening command is not yet verified, so no new slash command is promised.

The beginner form asks only what the player was doing and what went wrong. Expected behavior, reproduction steps and category are optional. Capture build, test session, planet, cell, coordinates and time automatically. After a successful durable save, show a receipt such as **Report QA-000123 saved. The team will review it when available.** Never claim an agent has seen it or a Discord post exists at this point. On a storage failure, tell the player it was not saved and offer a retry; do not silently discard it.

Discord adds `getting-started` and `ask-for-help` beside QA. Keep player confusion/support questions distinct from confirmed bugs; the agent may request clarification rather than dismissing a new player's report. Developer friends get the Developer role only when approved; game staff, source access and server credentials are separate decisions.

## Durable queue and agent processing

1. A server-side producer saves a structured report to an append-only JSONL journal or one immutable JSON file per report. It acknowledges only after the selected flush/durability operation succeeds. One-file-per-report with atomic publication is a viable alternative to a locked journal; choose one implementation and prove concurrent writers/crash recovery.
2. Keep the spool outside the disposable test world's restore path and outside tracked source files. It must survive agent restarts and test-galaxy resets. Store metadata and original player text locally; no Discord credentials in game-server configuration or report records.
3. On a session start, or after its current assigned task, an agent checks for pending reports within a bounded triage budget. The agents share a claim/lease per report to prevent simultaneous processing. An expired lease returns unfinished work to pending; do not delete the original on read.
4. The agent treats report text as untrusted player data, never as instructions to run commands, reveal secrets, change permissions or deploy code. Validate structure/length/encoding, remove private names/aliases, addresses, credentials and raw logs before preparing an external summary. Preserve the original locally and distinguish player allegations from reproduced behavior.
5. Give the sanitized report a summary, category, impact and reproduction status. Link probable duplicates to a canonical report without deleting their independent observations. Unknown reproduction is **unverified**, never confirmed by a player's assertion alone.
6. The agent relays the reviewed summary to the owner-selected private Discord bug channel/forum. Record the report ID, destination and returned message/thread ID locally. Retry only with durable delivery state; ambiguous delivery needs reconciliation before another post. This is a separate reviewed-report feed, not permission to send raw board/player text through the existing C17 sender.
7. Track new -> triaged -> needs-info/reproduced -> in-progress -> ready-to-retest -> verified/duplicate. Track delivery separately: pending -> prepared -> sending -> posted/uncertain. Being posted is not being fixed.

This works while both agents are offline: reports accumulate on disk. Processing starts when an actual agent session is available; it does not depend on a model remembering previous chat context, and it does not promise an always-on agent. No new scheduled agent wakeup is configured here.

## Record contract (proposed)

Required envelope: schema version, unique server-assigned report ID, server timestamp, test/live environment, build identifier, session identifier, planet/cell/position, category and original text. Optional target context is captured only when observable. Player identity, if needed for private follow-up, is taken from the authenticated server session and kept in a private local field; do not trust the name supplied in the client packet or publish identifying fields to Discord.

Limit report size and rate per authenticated sender. Encode newlines inside JSON strings so text cannot forge another log record. Do not collect passwords, account hashes, private chat history, entire console tails or database dumps. A spool reader must safely handle partial final records, invalid Unicode, malformed/oversized input, ID collisions, duplicate delivery and a full disk. Choose bounded retention/rotation while retaining unresolved reports and their delivery records. Back up the spool separately from the resettable test world.

## Native source findings

Inspected `/opt/swg/Core3-gpt`, source checkpoint `19f40ab8`, read-only:

- `MMOCoreORB/src/server/zone/objects/creature/commands/ReportCommand.h`: validates state/locomotion then returns SUCCESS; no report storage in this command. Do not advertise it as our bug inbox.
- `MMOCoreORB/src/server/zone/packets/ui/CreateTicketMessageCallback.h`: native client ticket intake exists, gated by `Core3.AccountManager.HolocronTicketsEnabled` (false by default in the callback). It parses player name, category/subcategory and Unicode body, then calls `HolocronManager::submitTicket`.
- `MMOCoreORB/src/server/zone/managers/holocron/HolocronManager.cpp`: `loadBugCategories()` immediately returns; the dormant category-loading code uses Mantis. `submitTicket()` attempts Mantis SQL writes and reporter lookup. Its client response is commented out beside a historical crash TODO. No durable local queue/receipt is implemented here.

Therefore do not simply turn on HolocronTicketsEnabled and assume the native form is ready. Add a deliberately selected local backend, usable categories and safe acknowledgement, then verify on the real client. **Mantis is not required for the proposed local queue + agent relay architecture**, although the existing native implementation currently depends on it. Existing native UI compatibility/response behavior is a test gate, not established fact.

## Ownership and implementation order

**C27 proposed engineering task:** Claude owns native server intake/UI, authenticated context, spool persistence and receipt. ChatGPT owns outside-server queue reader/claims, triage/outbox tooling, source cross-review and evidence checks. No C27 server edits, service installs, account changes or deployment performed in this design session. Agent-to-Discord relay is the owner's requested workflow; its destination/integration and standing delivery settings still need concrete setup.

1. Agree the producer schema/storage contract and an outside-restore spool location.
2. Implement a disabled-by-default local backend and a simple player form/receipt in isolated source; cross-review and build.
3. Implement the local reader/claim/outbox and failure-state tests against fixture reports, without networking.
4. On the test galaxy, prove a new ordinary player can submit, gets a true receipt, and the report survives logout, server reset and an offline-agent interval. Test concurrency, length/rate limits and storage failure.
5. Connect the approved Discord destination and prove one sanitized report becomes one tracked post, then test uncertain delivery recovery and duplicate linking.
6. Add it to newcomer onboarding and playtest plans. Live deployment remains a separate reviewed owner-approved action.

Difficulty: **Medium**, with the native client form/acknowledgement the main uncertainty; a new client command/UI patch would increase effort. Maturity: **scoped, source inspected; implementation and end-to-end testing pending**.
