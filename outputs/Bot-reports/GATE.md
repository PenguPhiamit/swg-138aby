# Gate: PASS

2026-10-17 05:38:33 · dev `fc3bb3e2` · archive `df1d538e` · bots 23/23 · server errors at start: 7 · 47/56 checks passed · details `Bot-reports/gate/20261017-052926.json`

- WARN Besh besh-harvest.py: BLOCKED: prey level unknown or above 5; need a mapped weak-animal spawn.

## Flaky (failed before too): 1
- Aurek · aurek-doctor-buffs.py · Jesh receives health enhancement (FAIL) — {"max_ham_before": 1000, "max_ham_after": 1000, "outcome": "unverified", "messages": ["@healing_response:healing_respons

## Missing (passed before, did not run): 7
- Cresh · cresh-missions.py · a mission terminal in town
- Cresh · cresh-missions.py · reach the mission terminal
- Cresh · cresh-missions.py · the terminal lists missions
- Cresh · cresh-missions.py · accept the nearest destroy mission
- Cresh · cresh-missions.py · reach the mission area
- Cresh · cresh-missions.py · the target is located (waypoint updated)
- Cresh · cresh-missions.py · find the lair

## New checks: 19
- Cresh · cresh-missions.py · a general mission terminal within 2 km (pass)
- Cresh · cresh-missions.py · Cresh reaches the general terminal (pass)
- Cresh · cresh-missions.py · general/deliver: the general terminal offers deliver (pass)
- Cresh · cresh-missions.py · general/deliver: accepted into the datapad (pass)
- Cresh · cresh-missions.py · general/destroy: the general terminal offers destroy (pass)
- Cresh · cresh-missions.py · general/destroy: accepted into the datapad (pass)
- Cresh · cresh-missions.py · general/deliver pickup: reach the NPC (pass)
- Cresh · cresh-missions.py · general/deliver pickup: an NPC stands at the waypoint (pass)
- Cresh · cresh-missions.py · general/deliver: the pickup hands something over (FAIL) — []
- Cresh · cresh-missions.py · general/deliver: the waypoint moves to the destination (FAIL) — {"from": {"planet": "tatooine", "x": 3293.10009765625, "y": -4651.669921875, "z": 0.0}, "to": {"planet": "tatooine", "x"
- Cresh · cresh-missions.py · general/cap: Ilsa holds 6 missions (pass)
- Cresh · cresh-missions.py · general/cap: the 7th mission is refused (pass)
- Cresh · cresh-missions.py · general/cap: a refusal message comes (pass)
- Cresh · cresh-missions.py · general/destroy: reach the mission area (pass)
- Cresh · cresh-missions.py · general/destroy: the target is located (pass)
- … 4 more in the JSON

## Still failing: 5
- Besh · besh-harvest.py · meat ordinary wild prey found (FAIL) — null
- Besh · besh-harvest.py · hide ordinary wild prey found (FAIL) — null
- Dorn · dorn-social.py · leash brings Nima to Dorn after he stops (FAIL) — 12.0 m from Dorn
- Dorn · dorn-social.py · Nima watches Dorn dance (FAIL) — ["@healing:no_line_of_sight"]
- Dorn · dorn-social.py · Nima gets the dance buff after 70 s of watching (FAIL) — no performance_enhance message: does Dorn have private_buff_mind and healing_dance_mind (novice entertainer only)?
