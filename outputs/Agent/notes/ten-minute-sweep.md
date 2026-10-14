# Ten-minute function sweep — 13 October 2026, 12:18–12:28 PDT

Live sandbox920203d8, initialized, zero startup error lines. No server changes, commits, staff commands or other-player interactions. Two connections used for rapid-relog probe. Raw events in ../logs/; bug/progress reports in ../reports/2026-10-13.md.

| Function/check | Result and evidence |
|---|---|
| Login and saved position | PASS:3554,-4782 persisted, cell0,groundz16.35449 |
| Object type filter | PASS:TANO returned3 tangible objects only |
| Radius filter | PASS:radius3 returned Dax at2m; radius1 at greeters returned empty |
| Result limit/sort | PASS:limit1/limit2 returned nearest1/2 in distance order |
| Sit | Request accepted; actual posture UNVERIFIED (not exposed) |
| Stand | Request accepted repeatedly; actual posture UNVERIFIED |
| Kneel | Request accepted; actual posture UNVERIFIED |
| Prone | Request accepted; actual posture UNVERIFIED |
| Dismiss empty group | PASS:normal closure; no spawn/error observed |
| Choose with ended conversation | BUG CANDIDATE:reopened greeting/options without new start; later cancel also reopened; fresh talk restored normal branch |
| Hire one | PASS:Naty Voinee oid281474994127026, observed1m away |
| Rapid logout cleanup | FAIL against guide's simple expectation:SAME Naty ID survived disconnect12:22:00/reconnect12:22:06–07 and followed afterward. Full delayed logout not tested |
| Following after rapid relog | PASS:same Naty moved with10m walk, observed2.5m behind |
| Explicit dismiss after relog | PASS:gone exact Naty ID12:23:10; nearby look confirmed absent |
| Event cursor filtering | PASS:events since727 returned728..733; since733 returned734..737, no older entries |
| Notebook inventory | PASS:list_notes returned saved named notebooks |
| Standard greeter conversations | PARTIAL:Guillo/Mooch start and choices work, but npc_says text empty; Vincie start/options without speech in result |
| Standard dialogue branch | PARTIAL:Guillo choose0 advanced to different option, speech still blank |
| Distance ends conversation | PASS:walking from greeters toward broker produced conversation_end |
| Survey without tool | PASS negative path:requestSurvey returned @ui:survey_notool |
| Sample without tool | PASS negative path:requestCoreSample returned @ui:survey_notool |
| Configurable movement speed | PASS:~29m route at speed2 took14.405s and arrived within0.5m |
| Already-at-destination move | PASS:within0.5m tolerance returned arrived in0s |
| Burst Run activation/expiry/cooldown | PASS message path:start12:25:35,stop12:26:05,repeat12:26:29 returned burst_run_wait. Actual speed bonus/HAM cost not measured |
| Notebook write/read round trip | Verified by exact-text comparison when saving this notebook |

## Findings to investigate
- Naty's rapid-relog survival is a narrower finding than a full logout failure; delayed server logout timing could explain it. Earlier absence-based cleanup inference is not a universal guarantee.
- Greeter IDs:Guillo281474994103942,Mooch281474994103939,Vincie281474994103936. Kael3530.13,-4798.91, within2.1/3.3/4.6m. @conversation/... options are normal; blank speech is not useful observation. Dax literal dialogue works.
- Stale choice sequence:talk94,choose1/id95 ended conversation12:20:03; choose0/id97 reopened greeting12:20:12; choose2/id99 reopened greeting12:20:51. No active-conversation guard observed. Fresh talk100 and choose0/id101 worked.
- Existing range-feedback/height/The Beginning bugs remain open. No repeat of dangerous combat. HAM,combat attribution,posture,SUI,inventory/loot,indoors,pathfinding absent. Crafting,survey success,travel,dungeons remain untested.

## End
Kael returned beside broker at3553.63,-4782.26,cell0,z16.35449. Naty explicitly dismissed; no companions. Burst Run expired and cooldown was observed. Save playbook, progress report, disconnect before12:28:15 PDT.
