# Squad incidents (offline, from saved reports)

Source: `C:\Users\Pengw\Documents\Codex\2026-10-13\h\outputs\Bot-reports` — 149 timestamped reports read, 0 unreadable, 6 stopped runs ignored (a halt or time budget is not evidence). Saved reports only: not live bot or server state. A `blocked` incident is a missing prerequisite or capability the scenario named, not a server defect; `defect-candidate` is a failed check with the body connected, for a person to judge.

Gates: shown after 2 runs; persistent from 3 runs; post-restart blackout 300 s for bot-down issues; 5 newest evidence entries each. Epochs (server restarts): 2026-10-14 13:27:00.

## Open

| Id | Group | Scenario | Kind | Class | Key | Runs | First | Last | Severity | Latest evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| Au-Bbe5339-2 | Aurek | aurek-doctor-buffs.py | BLOCKED | blocked | hospital found but no interior treatment anchor; Claude should expose building cells/medical rating. No guessed cell. | 5 | 10-14 14:01 | 10-14 14:35 | persistent | Aurek/20261014-143547-aurek-doctor-buffs.json: BLOCKED: hospital found but no interior treatment anchor; Claude should expose building cells/medical rating. No guesse… |
| Be-B6cbea2-2 | Besh | besh-fallback-crafting.py | BLOCKED | blocked | full crafting session/ingredient/assembly body API unavailable; no crafting success claimed | 2 | 10-14 14:14 | 10-14 18:09 | watch | Besh/20261014-180907-besh-fallback-crafting.json: BLOCKED: full crafting session/ingredient/assembly body API unavailable; no crafting success claimed |
| Be-Fbe7974-3 | Besh | besh-harvest.py | FAIL | defect-candidate | bone ordinary wild prey found | 3 | 10-14 14:20 | 10-14 18:06 | persistent | Besh/20261014-180621-besh-harvest.json: null |
| Be-F42d045-2 | Besh | besh-harvest.py | FAIL | defect-candidate | hide ordinary wild prey found | 3 | 10-14 14:20 | 10-14 18:06 | persistent | Besh/20261014-180621-besh-harvest.json: null |
| Be-Ff69483-3 | Besh | besh-harvest.py | FAIL | defect-candidate | meat ordinary wild prey found | 4 | 10-14 14:19 | 10-14 18:06 | persistent | Besh/20261014-180621-besh-harvest.json: null |
| Cr-B27600a-2 | Cresh | cresh-missions.py | BLOCKED | blocked | no same-planet destroy mission with a known waypoint within # m; no mission accepted. | 5 | 10-14 14:02 | 10-14 14:35 | persistent | Cresh/20261014-143552-cresh-missions.json: BLOCKED: no same-planet destroy mission with a known waypoint within 600 m; no mission accepted. |
| Do-F37b6b9-2 | Dorn | dorn-social.py | FAIL | defect-candidate | leash brings Nima to Dorn after he stops | 5 | 10-14 14:03 | 10-14 14:37 | persistent | Dorn/20261014-143711-dorn-social.json: 12.0 m from Dorn |
| Do-B807c42-2 | Dorn | esk-fallback-reach.py | BLOCKED | blocked | no terminal_bazaar within local reachability sample | 3 | 10-14 14:19 | 10-14 18:09 | persistent | Dorn/20261014-180911-esk-fallback-reach.json: BLOCKED: no terminal_bazaar within local reachability sample |
| Es-B7facfb-1 | Esk | esk-fallback-reach.py | BLOCKED | blocked | no terminal_bank within local reachability sample | 2 | 10-14 14:14 | 10-14 14:15 | watch | Esk/20261014-141543-esk-fallback-reach.json: BLOCKED: no terminal_bank within local reachability sample |

## Resolved (newest 40)

| Id | Group | Scenario | Kind | Class | Key | Runs | First | Resolved | By |
|---|---|---|---|---|---|---|---|---|---|
| Au-Bbe5339-1 | Aurek | aurek-doctor-buffs.py | BLOCKED | blocked | hospital found but no interior treatment anchor; Claude should expose building cells/medical rating. No guessed cell. | 6 | 10-14 10:11 | 10-14 13:27 | server restart (epoch 1) |
| Be-B6cbea2-1 | Besh | besh-fallback-crafting.py | BLOCKED | blocked | full crafting session/ingredient/assembly body API unavailable; no crafting success claimed | 3 | 10-14 10:20 | 10-14 13:27 | server restart (epoch 1) |
| Be-B67ecab-1 | Besh | besh-harvest.py | BLOCKED | blocked | prey level unknown or above #; need a mapped weak-animal spawn. | 3 | 10-14 10:12 | 10-14 13:15 | Besh/20261014-131529-besh-harvest.json |
| Be-B67ecab-2 | Besh | besh-harvest.py | BLOCKED | blocked | prey level unknown or above #; need a mapped weak-animal spawn. | 3 | 10-14 14:03 | 10-14 14:20 | Besh/20261014-142005-besh-harvest.json |
| Be-Fbe7974-1 | Besh | besh-harvest.py | FAIL | defect-candidate | bone ordinary wild prey found | 3 | 10-14 10:25 | 10-14 13:27 | server restart (epoch 1) |
| Be-F42d045-1 | Besh | besh-harvest.py | FAIL | defect-candidate | hide ordinary wild prey found | 2 | 10-14 13:15 | 10-14 13:27 | server restart (epoch 1) |
| Be-Ff69483-2 | Besh | besh-harvest.py | FAIL | defect-candidate | meat ordinary wild prey found | 3 | 10-14 10:25 | 10-14 13:27 | server restart (epoch 1) |
| Cr-B27600a-1 | Cresh | cresh-missions.py | BLOCKED | blocked | no same-planet destroy mission with a known waypoint within # m; no mission accepted. | 6 | 10-14 10:11 | 10-14 13:27 | server restart (epoch 1) |
| Cr-B807c42-1 | Cresh | esk-fallback-reach.py | BLOCKED | blocked | no terminal_bazaar within local reachability sample | 2 | 10-14 13:02 | 10-14 13:25 | Cresh/20261014-132531-esk-fallback-reach.json |
| Do-F37b6b9-1 | Dorn | dorn-social.py | FAIL | defect-candidate | leash brings Nima to Dorn after he stops | 6 | 10-14 10:12 | 10-14 13:27 | server restart (epoch 1) |
| Do-B807c42-1 | Dorn | esk-fallback-reach.py | BLOCKED | blocked | no terminal_bazaar within local reachability sample | 2 | 10-14 13:02 | 10-14 13:25 | Dorn/20261014-132505-esk-fallback-reach.json |

## Seen once (32, not yet incidents)

- Cresh · esk-fallback-reach.py · BLOCKED · blocked · no terminal_bazaar within local reachability sample · 10-14 18:09 · open
- Esk · esk-fallback-reach.py · BLOCKED · blocked · no terminal_bazaar within local reachability sample · 10-14 14:15 · open
- Esk · esk_verify_equipment.py · FAIL · defect-candidate · Esk: all supplied composite pieces worn · 10-14 16:30 · open
- Esk · esk_verify_equipment.py · FAIL · defect-candidate · Tovan: all supplied composite pieces worn · 10-14 16:30 · open
- Esk · hoth_content_check.py · FAIL · defect-candidate · salvage detail: props at the camp · 10-14 13:42 · open
- Esk · hoth_gameplay_check.py · BLOCKED · blocked · Esk return-home leg hoth -> corellia failed · 10-14 15:02 · open
- Esk · hoth_gameplay_check.py · BLOCKED · blocked · Vell first-job option unavailable; quest state retained, no reset · 10-14 15:02 · open
- Esk · hoth_gameplay_check.py · BLOCKED · blocked · cannot reach mission terminal · 10-14 15:02 · open
- Esk · hoth_gameplay_check.py · BLOCKED · blocked · chemical: no ordinary survey tool in inventory · 10-14 15:02 · open
- Esk · hoth_gameplay_check.py · BLOCKED · blocked · energy: no ordinary survey tool in inventory · 10-14 15:02 · open
- Esk · hoth_gameplay_check.py · BLOCKED · blocked · flora: no ordinary survey tool in inventory · 10-14 15:02 · open
- Esk · hoth_gameplay_check.py · BLOCKED · blocked · gas: no ordinary survey tool in inventory · 10-14 15:02 · open
- Esk · hoth_gameplay_check.py · BLOCKED · blocked · mineral sample: inventory units unavailable; new item or success text is insufficient · 10-14 15:02 · open
- Esk · hoth_gameplay_check.py · BLOCKED · blocked · mineral: no ordinary survey tool in inventory · 10-14 15:02 · open
- Esk · hoth_gameplay_check.py · BLOCKED · blocked · tauntaun combat requires upright crew leader with >=#% known HAM · 10-14 15:02 · open
- Esk · hoth_gameplay_check.py · BLOCKED · blocked · water: no ordinary survey tool in inventory · 10-14 15:02 · open
- Esk · hoth_gameplay_check.py · FAIL · defect-candidate · crew returns to Tatooine · 10-14 15:02 · open
- Esk · hoth_gameplay_check.py · FAIL · defect-candidate · hoth -> corellia: at the terminal (# m to buy) · 10-14 15:02 · open
- Besh · besh-harvest.py · FAIL · defect-candidate · bone ordinary wild prey found · 10-14 14:04 · resolved
- Besh · besh-harvest.py · FAIL · defect-candidate · meat ordinary wild prey found · 10-14 10:12 · resolved
- Cresh · cresh-fallback-travel.py · FAIL · defect-candidate · Mos Eisley -> Bestine: travel terminal · 10-14 14:10 · resolved
- Cresh · esk-fallback-reach.py · BLOCKED · blocked · could not return outdoors after reachability probe · 10-14 13:25 · resolved
- Cresh · esk-fallback-reach.py · BLOCKED · blocked · no terminal_bank within local reachability sample · 10-14 13:02 · resolved
- Dorn · esk-fallback-reach.py · BLOCKED · blocked · could not return outdoors after reachability probe · 10-14 13:06 · resolved
- Dorn · esk-fallback-reach.py · BLOCKED · blocked · could not return outdoors after reachability probe · 10-14 14:20 · resolved
- Dorn · esk-fallback-reach.py · BLOCKED · blocked · no terminal_bank within local reachability sample · 10-14 13:02 · resolved
- Dorn · esk-fallback-reach.py · BLOCKED · blocked · no terminal_bank within local reachability sample · 10-14 13:25 · resolved
- Dorn · esk-fallback-reach.py · BLOCKED · blocked · no terminal_bank within local reachability sample · 10-14 14:19 · resolved
- Esk · esk-fallback-reach.py · BLOCKED · blocked · no terminal_bazaar within local reachability sample · 10-14 13:09 · resolved
- Esk · esk-routes.py · FAIL · defect-candidate · Esk reaches the cantina (indoors) · 10-14 14:06 · resolved
- Esk · esk-routes.py · FAIL · defect-candidate · Esk reaches the cantina (indoors) · 10-14 18:05 · resolved
- Esk · hoth_content_check.py · FAIL · defect-candidate · tatooine -> corellia: buy a ticket · 10-14 13:36 · resolved

## Runs per group

| Group | Runs | Stopped | Scenarios | First | Last |
|---|---|---|---|---|---|
| Aurek | 29 | 0 | 3 | 10-14 10:11 | 10-14 18:09 |
| Besh | 29 | 2 | 4 | 10-14 10:12 | 10-14 18:09 |
| Cresh | 29 | 0 | 4 | 10-14 10:11 | 10-14 18:09 |
| Dorn | 29 | 0 | 4 | 10-14 10:12 | 10-14 18:09 |
| Esk | 33 | 4 | 9 | 10-14 10:19 | 10-14 18:10 |
