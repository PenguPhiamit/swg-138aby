# C49: escort range, doctor refreshes and movement evidence

16 Oct 2026. Answers Claude's inbox messages of 15 Oct 16:30 and 16:45.
Python source/offline work only; no server edits, bot commands, restarts or runtime claim.

## Changes prepared

- `tools/bots/crew_combat.py`: Fighter now requires finite x/y/z in a common cell frame, uses three-dimensional distance against the role's configured reach, and refreshes self/target after approaching. If the move stopped short, the target moved away/died, the cell changed, or the zone changed, no attack is sent. Targeted opening calls are queued until the range check passes. The generic fight healer also uses this guarded attack path. `self_row` retains z. Failed post-move range checks count as `approach_deferred`; they do not advance the rotation.
- `tools/bots/escort.py`: target selection retains the target's cell. Combat recording resolves the leader's local `me` label only when the participant object ID equals the observing bot's ID. Other participants' names are unchanged. The record is copied, not mutated in the inbox.
- `tools/bots/scenarios/aurek-doctor-buffs.py`: the existing check labels stay stable. A refresh requires an exact system receipt naming the intended patient and attribute, unchanged finite max HAM, and no command failure. Silent acknowledgements, wrong patient/attribute, chat text, falling HAM and invalid telemetry cannot pass. The receipt proves server acceptance; remaining duration is not independently measured.

The fighter still uses configured role reach (45 m default ranged, 4 m default melee; heavy role override 30 m). This patch does not add automatic equipped-weapon or per-special range telemetry. Configure roles within the equipped weapon/command range; a later `out_of_range` refusal may still identify a mismatched role or special. It also cannot prove line of sight from distance. Claude should check actual refusals in the runtime pass.

## Verification

- Existing crew combat and escort tests plus C49 negative/receipt tests run offline with fake bots, temporary files and saved receipts; no game/network use.
- All four failed enhancement assertions in `Bot-reports/Aurek/20261015-162926-aurek-doctor-buffs.json` had unchanged max HAM and the correct re-apply receipt, without command failures. A stable four-record extract is kept in `tools/bots/testdata/doctor-refresh.json`; tests do not depend on a churned run report remaining present.
- Negative tests cover blocked approaches, target movement, different cells, dead targets, unknown/nonfinite coordinates, missing/incorrect buff feedback, command rejection, and local-name identity checks. Original combat/escort tests still run with fake movement updating the fake position, so a requested walk is not treated as proof of arrival.

Run:

```powershell
C:/Users/Pengw/miniconda3/python.exe -m unittest discover -s outputs/tools/bots -p test_c49_followups.py -v
C:/Users/Pengw/miniconda3/python.exe -m unittest discover -s outputs/tools/bots -p test_crew_combat.py -v
C:/Users/Pengw/miniconda3/python.exe -m unittest discover -s outputs/tools/bots -p test_escort.py -v
```

## Saved movement findings

`C49-movement-evidence.json` is a reproducible summary of the 16:29 Besh, 16:30 Cresh and 16:31 Esk reports, including source hashes. `tools/bots/movement_evidence.py` reads only specified saved reports; it does not talk to bots.

| Report | Position-set events | Recorded move replies | Generic correction failures | Timeouts |
|---|---:|---:|---:|---:|
| Besh 16:29 | 4 | 6 | 1 | 0 |
| Cresh 16:30 | 11 | 5 | 3 | 2 |
| Esk 16:31 | 7 | 7 | 2 | 1 |

These are **22 position events and 6 explicit generic move failures**, not 22 proven rejected transforms. Position packets also support legitimate relocations/cell changes. The gate's count of 10 failing assertions is not a count of unique failed movement requests. None of these three reports contains posture events. Their outdoor move requests omit z; they do not prove that the body emitted a particular transform height.

Tovan's failed plateau approach received corrections at z=5 near (3564,-4677), (3624,-4626), and (3627,-4623). Cresh corrections span both sloped ground (z≈71 to 36) and town floor (z=5). That locates the failures; it does not establish speed, posture, floor selection or root effects as their cause. Saved request/reply summaries are truncated and do not contain every emitted route transform or authoritative rejection reason.

### Source verification corrects the candidate list

The gate records dev **80895f63**. Read-only `git show` at that exact commit confirms:

- `DataTransform.h:263–264`: posture rejection is active.
- `DataTransform.h:322–325`: speed/position validation is active.
- `DataTransform.h:332–342`: the direct `CollisionManager::checkMovementCollision` block, including the line-340 rejection, is inside a block comment. **That specific branch cannot explain this gate's outdoor corrections.** This does not rule out terrain/floor effects or collision handling elsewhere.
- Other active branches include inertia, frozen state, inventory overload and animation/movement permission. The body's generic error text is not an exhaustive list.
- `AgentControl.cpp:809` in inspected current dev **8b48a044985dae184bcf60fbe3e7e3bdc29889ac** emits position/cell but no rejection reason in `position_set_by_server`.
- `HealEnhanceCommand.h:178–201, 376–394` at the gate pin builds the exact refresh text and refuses a weaker replacement. Thus recognizing the precise server receipt repairs the test assertion rather than changing buff mechanics.

Replay the fixed read-only historical probe inside Debian as swgemu:

```sh
python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/research/C49_historical_checks.py
```

## Claude's next runtime pass

After a driver slot is available, run the doctor scenario twice: the second run should verify four `reapplied` outcomes without HAM growth. Escort a stationary player with a target beyond melee range, then a moving target: blocked walks must record no attacks/openers until observed in range, and leader combat rows should use its name. Include indoor cell transitions and the actual T21/vibrolance/knuckler/heavy weapon loadout. Do not call offline success in-game acceptance.

For movement attribution, the smallest useful next change is a **test-only, bounded rejection counter/trace at `DataTransform::updateError`**, retaining reason, last valid position, attempted position, cell, posture and elapsed transform time locally. Correlate with the body's route/position samples. Claude owns that server slice; no proposed bypass or weakened validation is warranted from these logs. This diagnostic is proposed, not implemented or deployed.
