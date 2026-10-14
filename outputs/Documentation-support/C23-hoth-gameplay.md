# C23 Hoth gameplay acceptance

ChatGPT owns the run and this open acceptance list. **Not accepted yet.** Scenario: `tools/hoth/hoth_gameplay_check.py`; five offline fixtures and compilation pass. No staff provisioning or teleporting. Normal shuttle travel and existing crew inventory/skills only.

## Run 20261014-144837 — in progress at 14:53, 14 October 2026

Claude restart-ready note 14:47: galaxy ready 14:45, dev scripts `1c4c24fb`, client archive prefix `aee83cc6`; startup author evidence says ten minimum-pool spawns. Run ceiling 30 minutes, one round, Esk only. No other squad process at preflight. Esk temporarily removed from squad-plan; restore on completion. Later R2 `eccb53e1` is not covered by this running instance.

| Acceptance item | Status / evidence |
|---|---|
| Six survey classes, resolved names and concentrations | Pending runtime |
| Ten `_hoth` inorganic resource types | Pending runtime; needs mineral/gas/liquid tools |
| Mineral inventory units | Pending; current body historically omits stack quantity, which is BLOCKED |
| Tauntaun meat/hide/bone units | Pending; separate fresh corpse per harvest category |
| Loot observation over confirmed kills | Pending; zero random drops is allowed |
| Both outpost terminals list Hoth offers; accepted destroy target stays on Hoth | Pending runtime |
| Vell first job, Ria 600–900 m, waypoint, two level-67 mynocks, regulator and reward | Pending; waypoint/credit telemetry currently unavailable -> BLOCKED |
| All crew home on Tatooine | Pending; cleanup subject to same bounded run deadline |

## Fail / blocked list

- Telemetry prerequisites: inventory resource units, cash/bank credit totals and theme-park waypoint observation. These must be exposed or checked by the owner before their acceptance items can be closed; success chat/new object count is insufficient.
- No runtime failure has yet been attributed to server code. Final saved JSON and summary will replace pending rows while retaining this version boundary.

Real-client evidence supplied by owner separately: Hoth loads, stormtroopers/wampas visible, entry-region names and all 18 markers present. That does not close harvest/mission/quest checks.

## Run 20261014-144837 — finished 15:02, blocked (836 seconds)

Saved evidence: `Bot-reports/Esk/20261014-150233-hoth_gameplay_check.json`, `Bot-reports/runs/20261014-144837-summary.md`. Scenario version at run start corresponds to local commit `fbd691f`. **59/61 checks passed, overwhelmingly repeated travel checks; this is not 97% Hoth gameplay coverage.**

- All three crew members reached Hoth through normal Tatooine -> Corellia -> Hoth ticket/boarding/arrival checks.
- Esk reached (20, -2235), z 10.97 at t=716 s. At t=718.2 s status reported level 1, max health 900, health -125, posture dead. The move reply said arrived; it did not establish survival. Attacker identity/cause was not established here. No combat kill was attempted/confirmed by the scenario (loot observation: 0 kills/0 new loot records).
- Leader inventory had none of the six survey tool categories. No surveys or sampling were verified. The first version inspected only the leader's tools, so this is not proof that every crew inventory lacks tools.
- Both mission terminals were found at exact expected coordinates, OIDs 281474994029161/281474994029162. Movement to them returned `cannot move while dead`; no mission list or accepted target was verified.
- Vell was found at (44, -2010), OID 281474994046505. Esk was dead and could not reach him, so the absent first-job option does **not** establish a quest-conversation defect. No Ria/guards/regulator/reward acceptance occurred.
- Lira and Tovan returned to Tatooine. Esk's return failed: travel-terminal gap 253.1 m, `cannot move while dead`. Separate normal death/clone recovery and return-only run started afterwards; result appended below when complete.

### Open items owned by ChatGPT

| ID | Classification | Required next step |
|---|---|---|
| C23-B1 | Preparation blocked | Verify normal survey tools and skills across the whole crew before travel; obtain/craft/trade missing tools within owner-approved scope. No staff provisioning in the scenario. |
| C23-B2 | Test readiness / scenario defect | Confirm the agreed combat kit before leaving the outpost; stop immediately if field traversal compromises leader. Do not use this novice death as a server balance regression. |
| C23-B3 | Telemetry blocked | Resource stack units, cash/bank totals and quest waypoint data needed, or explicit owner-side verification for those receipts. |
| C23-B4 | Gameplay untested | Repeat actual survey/harvest/mission/first-job acceptance after prerequisites; object existence alone closes none of these service checks. |
| C23-F1 | Cleanup handling | Death during a scenario was not recovered before first return attempt. Revised scenario now uses normal recover() before shuttle cleanup; runtime validation of the revised finally block pending. |

### Scenario correction after this run

Added tool/boss-armor preflight before any travel, searches for tools across crew, uses the tool owner for surveys/sample, logs best concentration explicitly, stops after compromised field traversal, and invokes ordinary death recovery before return. Seven offline fixtures and compilation pass. These changes do not retroactively validate this run or prove the armor marker guarantees survival. No second gameplay hunt was started with the unprepared crew.

## Cleanup complete — report 20261014-150600

`Bot-reports/Esk/20261014-150600-esk-recover-home.json`: **11/11 PASS**, 145 s. Start-of-run normal death recovery changed Esk from dead to upright; ordinary Hoth -> Corellia -> Tatooine shuttle travel passed. All three crew are home; final squad status checked before restoring `esk-routes.py` to the overnight plan. No staff commands, teleport, server restart or account changes. This validates the separate return-only recovery, not the revised C23 finally block or blocked gameplay checks. Driver claim released to the existing board owner after cleanup.
