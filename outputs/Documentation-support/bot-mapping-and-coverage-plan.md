# Bot mapping and whole-server coverage plan

13 October 2026 · ChatGPT · C10. Design based on the local feature register, profession reference, Bot API and places.json. No mapping run or new game test was performed. Existing pass counts must be taken from dated reports, not this plan.

## First mapping session: Hoth

Claude prepares a disposable test galaxy with Hoth registered and a verified return route. One driver owns each bot. Begin with a town/base seed from the planetary map registry; until the registry is exposed, Claude supplies a versioned export. Do not invent a usable landing site from terrain alone.

1. Record server/client revisions, snapshot/TRE hashes, planet, seed and time. Query registry towns, travel points and POIs. Divide the bounded town into 100 m survey tiles; cap one batch at 20 tiles or ten minutes. Resume using a saved frontier.
2. Search each tile using find for terminal, trainer, hospital, cantina and known spawn/template words. The current 30-object limit means a full result is potentially truncated: subdivide and mark completeness unknown until a count/pagination capability exists. A text search cannot enumerate unnamed objects; combine look observations and a registry/object-type listing from Claude.
3. Store buildings and their entry/exit edges. An indoor record needs building identity, cell identity and local x/y/z as well as its world position. Resolve cells anew each galaxy start; never reuse raw object IDs as permanent references. Request building cells/portals and medical ratings when a search cannot find an interior anchor.
4. Plan each edge with path; retain every point and corresponding proof verbatim. Missing or mismatched proof lengths, partial paths and any non-ok proof mark the edge unproved. Even all-ok planning is only a planned route: walk and verify final planet/cell/position separately. Compare outdoor height to terrain; indoor height is local, not terrain height. Record cliffs, no-navmesh areas and one-way transitions as blocked/unknown, never silently reachable.
5. Observe creatures without attacking: template/name, level, posture, location, time and count. Revisit on at least three separated passes to distinguish one sighting from a spawn region. Unknown level stays unknown. Record safe weak-prey sites separately; no stronger or injured target is a harvest-test fixture.
6. Test a reversible town loop, building entry/exit, terminal approach and return travel. Save checkpoints after each tile. Disconnect or release bots back to Claude and file unreachable-route/terminal defects with exact evidence. Stop after two repeated no-progress moves, death/incapacitation, a scene change or the batch deadline.

## Map format and migration

Keep existing places.json consumers working: its mos_eisley area/terminals structure remains unchanged. Add a separate versioned map file under Agent/maps/<planet>.json, then generate legacy terminal projections only from verified observations. Proposed schema:

```json
{"schema_version":1,"planet":"hoth","provenance":{"server_revision":"pending","client_manifest":"pending","observed_at":"pending"},"seeds":[],"frontier":[],"objects":[{"key":"template+world-position+building-cell-name","category":"terminal","template":"pending","name":"pending","world":{"x":0,"y":0,"z":0},"interior":null,"runtime":{"oid":null,"cell":null,"galaxy_epoch":"pending"},"evidence":[],"reachability":"unknown"}],"routes":[],"spawn_observations":[],"blocked_areas":[]}
```

Each route stores from/to keys, points, proof, partial, traversal result, final position and report reference. Interior stores building key, cell name/index and local coordinates. Runtime IDs are ephemeral. Search hits, planned routes and traversed routes are separate evidence states. Never fill unobserved coordinates with sample zeros in a real record. Store tile bounds/search terms/truncation flags and unresolved errors so completeness is auditable. Sanitize account/player data from exports.

## Coverage inventory

The companion [CSV](bot-coverage-matrix.csv) has one explicit row for **all 86 feature groups F01–F86 and all 39 profession/track rows** in the reference. It records a proposed scenario, capability/gate, priority and expected outcome or remaining implementation work. Scenario filenames are proposals, not existing files or passing tests. The 102 catalogue assets are candidates rather than extra feature groups: add an asset-manifest child row only when one is selected and cleared.

P0 protects data/isolation; P1 supports Hoth and common play; P2 broadens specialized mechanics/assets; P3 requires an approved design first. Infrastructure needs offline checks, visuals need human client acceptance, and external services need owner approval. Bots cannot prove every feature alone. Every gameplay test needs ordinary non-staff permissions, prerequisites, positive evidence, a refused/invalid case, cleanup and relog persistence where applicable. Test helpers establish fixtures only; they do not prove natural progression.

Existing relevant scenarios: cresh-missions.py (nearest bounded destroy mission), aurek-doctor-buffs.py (hospital/max-HAM), besh-harvest.py (fresh eligible corpse), besh-survey.py, dorn-social.py and esk-routes.py. The C9 revisions are locally compiled and **untested in game**. They do not cover all profession rows by themselves.

## Next five scenarios and Claude dependencies

| Order | Proposed scenario | Concrete evidence | Claude additions / prerequisites |
|---|---|---|---|
| 1 | esk-hoth-map.py | Complete bounded seed tile, interior anchors, route proof plus actual arrival, saved frontier | Planet registry export/query, building cells/portals and paginated type search; Hoth registration and safe seed/return travel |
| 2 | cresh-hoth-travel.py | Buy ticket, depart, arrive on Hoth, return, credits/ticket deltas and relog | Travel session/ticket decoding; destination/travel registration; human client verifies loading/rendering |
| 3 | besh-resource-craft.py | Sample quantity increases, consume exact ingredients, finish prototype, XP and relog persistence | Resource stack quantities and attributes, schematic/slot/session assembly, crafting result/XP snapshots |
| 4 | aurek-medical-support.py | Hospital treatment, pack charge delta, actual HAM/wound change, buff duration/refresh and refusal outside | Building medical rating, medicine charges, wounds/battle fatigue and active-effect durations; C9 hospital anchor first |
| 5 | dorn-vehicle-trade.py | Own deed/device, call/mount/move/dismount/store; consenting second bot trade with item/credit conservation | Mount/controller state and vehicle commands; secure trade request/offer/accept/cancel protocol and credits inventory; disconnect rollback |

Bound each scenario by a total deadline, not only per-command waits. One failed prerequisite produces BLOCKED and cleanup, not an invented pass. Publish passed/failed/blocked/not-run separately with report paths, build pins and exact scope. Claude runs these on test; live deployment still requires cross-review and owner approval.
