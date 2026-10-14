# C24 commit inventory

Pinned dev `eccb53e1ee6f491e84ea8dd3ec2a6f0e3ad5d04d`, sandbox `920203d8fa68b9b573cdcfc8df227deaf2811c6a`.

Conservative superset: every unpromoted dev commit, including shared bot/client helpers; unrelated features need not be promoted with Hoth.

| Repo | Commit | Purpose | Independent review | Gameplay |
|---|---|---|---|---|
| dev | `eccb53e1` | Resources: opt-in backfill of in-shift galaxy-wide spawns onto a newly enabled zone (Fable R2) | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| dev | `1c4c24fb` | Hoth: MTG's ten Hoth-only minerals, gas and fuels in the minimum pool (owner's first survey found none) | C24 source review; gameplay pending | C23 pending; source review is not gameplay acceptance |
| dev | `c046e633` | Agent body: a fight checks scene, connection and target with each attack (C22-F1) | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| dev | `54a33063` | Glacial rancor: use the hue-capable rancor body (C22-F2) | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| dev | `dd16bcff` | Hoth regions: named regions for the caves, camps and zones (Fable batch B3) | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| dev | `e9094960` | Hoth quest: Quartermaster Vell stands still (AI_STATIC, as stock luthik_uwyr) | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| dev | `5eb140ce` | Hoth camps: prop headings in radians (spawnSceneObject's heading; they were degrees) | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| dev | `92d99dba` | Hoth missions: outpost mission terminals, destroy and deliver missions, a quest chain (Fable batch C) | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| dev | `de1b679a` | Hoth camps: six camps and patrol posts in the batch A zones (Fable batch B1) | C22: heading finding; follow-up fix separately gated | C23 pending; source review is not gameplay acceptance |
| dev | `69eb77fe` | Hoth batch A: eight area spawners on MTG's map; clean-room glacial rancor (not spawned) | C22: rancor appearance finding; follow-up fix separately gated | C23 pending; source review is not gameplay acceptance |
| dev | `c5f1ae06` | Hoth ice caves: 129 wampa spawns in MTG's four ice caves (Fable, from Bellum) | C22: source/geometry checks, client checks pending | C23 pending; source review is not gameplay acceptance |
| dev | `90f60a81` | Agent body: straight-line moves belong to their scene and need a connection (C4e-F2) | C22: enclosing fight incomplete | C23 pending; source review is not gameplay acceptance |
| dev | `23014f39` | Spawn commands: read each spawn area under its lock (C4f-F1) | C19 addendum + C22, source finding resolved | C23 pending; source review is not gameplay acceptance |
| dev | `5c7ae017` | Sandbox MTG backport batch 2 (Fable): wire 45 unreached templates, 10 new | C18 reduced sample only | C23 pending; source review is not gameplay acceptance |
| dev | `0c44d431` | Sandbox MTG backport batch 1 (Fable): real SOE paths, 13 wearables, 3 client paths | C18 reduced sample only | C23 pending; source review is not gameplay acceptance |
| dev | `578861d9` | Sandbox: Botanist feasibility test, server side (trainer in Mos Eisley) | C19: feasibility trainer, client acceptance pending | C23 pending; source review is not gameplay acceptance |
| dev | `bea94e7a` | Sandbox leash: an indoor step needs both ends on the floor mesh (C4e-F1) | C19: floor counterexample resolved in source | C23 pending; source review is not gameplay acceptance |
| dev | `2f205cd2` | Sandbox Hoth: resources spawn on Hoth | C19: data/inheritance reviewed; resource gameplay pending | C23 pending; source review is not gameplay acceptance |
| dev | `b7f03b0e` | Sandbox Hoth: reward loot (Bellum Gero, AGPL-3.0) on Hoth's creatures | C19: offline loot checks, no drop acceptance | C23 pending; source review is not gameplay acceptance |
| dev | `34d4772a` | Sandbox staff tools: /spawnStatus and /showSpawnRegion (were empty stubs) | C19: original counter race; fixed separately | C23 pending; source review is not gameplay acceptance |
| dev | `c402e480` | Sandbox Hoth: ordinary creatures, lairs and a world spawner (Bellum Gero, AGPL-3.0) | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| dev | `9ac7cdcd` | Agent body: find and tell; replies from an old scene are discarded | C4e: reviewed | C23 pending; source review is not gameplay acceptance |
| dev | `421adb15` | Sandbox /leash: re-check after the cross-lock; prove each step it moves | C4e: review findings retained | C23 pending; source review is not gameplay acceptance |
| dev | `5b2a858f` | Sandbox Hoth v1: planet entry, travel point and regions | C4e: Hoth travel evidence, review findings retained | C23 pending; source review is not gameplay acceptance |
| dev | `5aadc8b9` | Address ChatGPT's C4b/C4c review: test-galaxy guard, leash locking and routes, request ids | C4d: remaining findings; later fixes separate | C23 pending; source review is not gameplay acceptance |
| dev | `2970b47e` | Normalize line endings (LF) in agent body and sandbox command files | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| dev | `f25c90f9` | Sandbox test helpers /agentgear and /agentskill; agent body reads mission objects | C4b/C4c: changes requested | C23 pending; source review is not gameplay acceptance |
| dev | `220e0f39` | Sandbox /leash: never re-place a follower out of range; naming the leader keeps it on | C4b/C4c: changes requested | C23 pending; source review is not gameplay acceptance |
| dev | `09a56205` | Sandbox /leash: server-side follow assist for group members | C4b/C4c: changes requested | C23 pending; source review is not gameplay acceptance |
| dev | `3797430a` | Agent body: one move deadline, no walking while down, survey, indoor look | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| dev | `cde59ec5` | Sandbox /agentpath: enforce the 256-point cap, validate input, echo the request | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| dev | `697f2002` | Agent body: keep re-planning long paths while each leg gets closer | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| dev | `5c39f411` | Sandbox /agentpath: head part of the way when leaving a building for a far target | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| dev | `eebdd99d` | Sandbox: /agentpath helper for the agent client (bot accounts only) | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| dev | `a72026b6` | Agent body: HAM/posture/combat state, combat log, fight reflex, navmesh path walking | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| dev | `e1344def` | Agent body: inventory, radial menus, SUI pop-ups, mission-list request, ground height | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| dev | `ab9eab6e` | Agent body: acknowledge teleports after planet changes; decode string-table system messages | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| dev | `6cdb4aef` | Track 18 MTG script files hidden by upstream's *test* ignore rule | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| dev | `bda2c0dd` | Sandbox world boss rotation and big game hunter (dev, not deployed) | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| dev | `b942d9b5` | Agent body reports failed commands; mercenary broker stands still | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| dev | `2347100a` | Sandbox mercenaries: broker NPC at Mos Eisley, hire up to 3 followers that join your fights | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| dev | `dcd2f047` | core3client: --agent-control remote control mode for the AI agent player | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| h archive tools | `1291ba02` | Format tools in one package, outputs/tools/swgfmt (Fable T1); Fable's R2 resource backfill staging | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| h archive tools | `c2573e31` | Archive builder on our own format tools (Fable B1-B3) | C24: format switch reviewed; isolated format checks pass | C23 pending; source review is not gameplay acceptance |
| h archive tools | `2009167b` | hoth_client_build: Hoth map markers and place names (Fable's B3) in local_planets.tre | C24: map integration reviewed; owner confirmed 18 markers | C23 pending; source review is not gameplay acceptance |
| h archive tools | `981c60a3` | hoth_client_build: pack the Hoth quest chain's strings as a new string table | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
| h archive tools | `f0b192e9` | hoth_client_build: never read our own archive; publish only after checks (C4f-F2) | C19/C22: self-input failure resolved | C23 pending; source review is not gameplay acceptance |
| h archive tools | `8ac78577` | Local history for the SWG project (no remote) | No independent per-commit approval recorded in this inventory | C23 pending; source review is not gameplay acceptance |
