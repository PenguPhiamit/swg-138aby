# Gate: PASS

2026-10-17 02:25:50 · dev `07d9f61e` · archive `df1d538e` · bots 23/23 · server errors at start: 0 · 39/46 checks passed · details `Bot-reports/gate/20261017-021653.json`

- WARN Besh besh-harvest.py: BLOCKED: prey level unknown or above 5; need a mapped weak-animal spawn.

## Flaky (failed before too): 1
- Besh · besh-harvest.py · hide ordinary wild prey found (FAIL) — null

## Fixed: 10
- Aurek · aurek-doctor-buffs.py · Aurek receives health enhancement (pass)
- Aurek · aurek-doctor-buffs.py · Aurek receives action enhancement (pass)
- Aurek · aurek-doctor-buffs.py · Jesh receives health enhancement (pass)
- Aurek · aurek-doctor-buffs.py · Jesh receives action enhancement (pass)
- Besh · besh-harvest.py · hide patrol reached (pass)
- Cresh · cresh-missions.py · reach the mission terminal (pass)
- Cresh · cresh-missions.py · reach the mission area (pass)
- Esk · esk-routes.py · Tovan reaches the plateau (pass)
- Esk · esk-routes.py · Tovan is up on the plateau (z > 150) (pass)
- Esk · esk-routes.py · all three back in the square (pass)

## New checks: 4
- Cresh · cresh-missions.py · the target is located (waypoint updated) (pass)
- Cresh · cresh-missions.py · find the lair (pass)
- Cresh · cresh-missions.py · the lair is destroyed (FAIL)
- Cresh · cresh-missions.py · the mission completes (FAIL) — {"mission_removed": false, "message": null}

## Still failing: 4
- Besh · besh-harvest.py · meat ordinary wild prey found (FAIL) — null
- Dorn · dorn-social.py · leash brings Nima to Dorn after he stops (FAIL) — 12.0 m from Dorn
- Dorn · dorn-social.py · Nima watches Dorn dance (FAIL) — ["@healing:no_line_of_sight"]
- Dorn · dorn-social.py · Nima gets the dance buff after 70 s of watching (FAIL) — no performance_enhance message: does Dorn have private_buff_mind and healing_dance_mind (novice entertainer only)?
