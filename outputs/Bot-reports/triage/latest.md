# Squad triage — saved reports, not live status

latest saved report per squad, possibly different runs/builds; no pooled pass rate. PASS means only the recorded checks; BLOCKED means prerequisites or capabilities prevented completion. Missing build revisions prevent build-to-build comparison. Original reports are unchanged.

| Squad | Scenario | State | Recorded checks | Evidence |
|---|---|---|---|---|
| Aurek | aurek-doctor-buffs.py | BLOCKED | 0/0 | [report](../Aurek/20261013-225748-aurek-doctor-buffs.json) |
| Besh | besh-harvest.py | FAIL | 7/10 | [report](../Besh/20261013-225928-besh-harvest.json) |
| Cresh | cresh-missions.py | BLOCKED | 3/3 | [report](../Cresh/20261013-225820-cresh-missions.json) |
| Dorn | dorn-social.py | FAIL | 9/10 | [report](../Dorn/20261013-222753-dorn-social.json) |
| Esk | esk-hoth.py | FAIL | 18/19 | [report](../Esk/20261013-231520-esk-hoth.json) |

## Aurek

- BLOCKED: hospital found but no interior treatment anchor; Claude should expose building cells/medical rating. No guessed cell.

## Besh

- Failed check: meat ordinary wild prey found — null
- Failed check: hide ordinary wild prey found — null
- Failed check: bone ordinary wild prey found — null

## Cresh

- BLOCKED: no same-planet destroy mission with a known waypoint within 600 m; no mission accepted.

## Dorn

- Failed check: leash brings Nima to Dorn after he stops — 11.7 m from Dorn

## Esk

- Failed check: the outpost is there (buildings or terminals nearby) — ["@obj_n:unknown_object", "@theme_park_name:transport", "@travel:ticket_collector_name"]
