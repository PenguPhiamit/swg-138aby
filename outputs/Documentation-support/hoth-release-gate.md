# Hoth release gate — NO-GO

14 October 2026, ChatGPT. **Reviewed by ChatGPT for the scope stated below; not approved for live promotion.** Owner approval is still required even after this gate turns green. C23 gameplay acceptance is running, not passed. No server restart, merge, archive installation or live deploy was performed by ChatGPT.

## Commit and evidence boundary

[Commit-by-commit inventory](hoth-release-commits.md) and [JSON](hoth-release-commits.json) record every `sandbox..dev` commit as a conservative superset, plus the archive-builder/format-tool history (48 rows at capture). Dev was `eccb53e1`, sandbox `920203d8`. Each row records purpose, existing review or its absence, and gameplay status. Reproduce with `tools/hoth/release_inventory.py`; refreshing the inventory does not renew a review. Unrelated Botanist/world-boss/companion features need not be bundled with a Hoth promotion.

The C23 running galaxy was prepared by Claude at 14:42–14:45 with scripts `1c4c24fb` and archive prefix `aee83cc6`, before R2's new dev commit. **A C23 result from that instance cannot validate R2.** Source/branch HEAD, running binary, Lua scripts and client archive are separate version boundaries.

## Additional independent review

| Change | Review result | Required gameplay evidence |
|---|---|---|
| dev `1c4c24fb`, ten Hoth-only minimum-pool entries | Read exact Lua diff: explicit leaf types, one each; no despawn/reset logic. Depends on Hoth enabled, merged resource tree and valid `_hoth` zone restriction. No new source defect established in this small diff. | All ten types in actual surveys; quantities and concentrations; ordinary classes beyond those ten. Claude's startup “Spawned 10” is author evidence, not survey acceptance. |
| h `2009167`, map/region names | Read builder integration and merge/verification functions: uses base reader excluding own archive, explicit key merges, round-trip/key-resolution checks. Owner confirmed all 18 markers and entry labels; that covers map presence, not every encounter. | Retain owner confirmation; check UI again against the final shipped archive rather than an earlier build. |
| h `c2573e3`, own format readers/writers/UI cloner | Read builder/loader diff, formatter adapter, TRE writer/reader and UI wrapper. Four isolated checks pass: mixed/empty TRE data through separate reader, case-collision refusal, stock UI lines preserved, R2 counterexample below. No production archive was packed/published by ChatGPT. | Final archive load in real client, both UI includes, round trip and retained stock destinations. Later T1 shim/package refactor is separately inventoried; no blanket audit of all later importers implied. |
| dev `c046e633`, C22-F1 fight guard | Read exact diff: generation/connection/target checks and attack dispatch now share worldMutex; non-timeout approach failure ends fight, timeout retries sampling. Original source race addressed. | Scene reload/disconnect cancellation stress test; no post-cancellation attack/count. Ordinary successful combat alone is insufficient. |
| dev `54a33063`, C22-F2 rancor body | Read exact one-line template replacement to hue-capable body, matching C22's independently inspected client chain. Source finding resolved. Still not spawned. | Owner decision on appearance/encounter, real-client hue/body check before exposure. |
| R2 staged patch / dev `eccb53e1` | **Changes requested, P2 for multiple configured backfill zones:** probability depends on mutable map count, so a loser can become a winner on a later restart after another zone was added. Default empty config makes the path inactive; single-zone use does not demonstrate the multi-zone contract. | Correct/limit the supported configuration, then compare exact resource-map sets across two starts, existing maps/statistics retained, restricted/max-pool cases and new-zone samples. No restart by ChatGPT. |

### R2-F1 — P2: multiple-zone restart idempotence

Location: `ResourceSpawner.cpp`, new backfill loop in `eccb53e1` / `Fable-resources2/cpp/resource-backfill.patch`: `mapSize = resourceSpawn->getSpawnMapSize()` is recomputed per candidate and compared using `roll * zones >= mapSize * 1000`.

Counterexample: 12 active zones, two existing maps, maxPool 5; backfill A has hash bucket 200, B bucket 100. First startup: A loses (2400 >= 2000); B wins (1200 < 2000), increasing maps to three. Next startup: A now wins (2400 < 3000), B is already present. The fixed hash did not prevent restart-dependent allocation. `test_release_formats.py` reproduces this arithmetic as a regression fixture; it does not assert that a particular real spawn has those buckets. The condition is a supported two-zone configuration and valid bucket values.

Fix by making eligibility depend on a stable pre-backfill baseline or persisted decision data, or explicitly restrict/document one-zone configuration. A snapshot only at the start of each load still changes on the second load, so it is not sufficient. Current Hoth-only operation can be evaluated separately but must not be advertised as general multi-zone idempotence. Existing resource maps must not be silently destroyed to fix this.

## Non-code blockers and owner decisions

1. **C23 remains open:** surveys in six classes, ten inorganic types and resolved labels; actual mineral units; meat/hide/bone units; two terminals and accepted Hoth destroy target; Vell job/waypoint/two guards/regulator/exact reward; all crew home. Missing units/credits/waypoint telemetry is BLOCKED, not PASS. Zero rare loot drops is observational, not a failed probability check.
2. **Questions 2, 8, 9:** approve/adjust common/rare/deed rates and non-Hoth deed selection; corpse-only versus per-player wampa boss rewards; mynock den option, terrain/client edits, map naming and camp-vendor scope. Unchosen optional encounters remain deferred options, not discarded features or automatic release scope.
3. **Client delivery unresolved:** normal live launcher currently does not load `local_planets.tre`. Define version/hash, backup and install procedure, required MTG archives and precedence; verify stock destinations still work. A live player with an old client must not be routed to an unavailable Hoth. Agree the access/rollout gate before enabling the live route.
4. **Exact promotion set:** pick reviewed Hoth/shared-system commits, not blindly all dev. Unreviewed rows and later source edits need review at their exact hash. Retain Bellum/MTG notices, creator/art provenance, and no excluded-source material. Public documents must redact personal identifiers except required licence credit.
5. **Rollback/backup and owner consent:** Claude owns deployment/build/restart. Record source and archive hashes, reviewed-by entry, backup and recovery plan, then obtain the owner's explicit deployment go. This report is not that go.

## Verification performed

Read-only git history/source, staged R2 patch and builder source. C23 five offline evidence fixtures pass; C24 four format/arithmetic fixtures pass. Both scripts compile. C25 is separate, unbuilt worktree commit `5c41ed62`; Claude review/build/runtime pending. No full Hoth gameplay success or concurrency stress test is claimed here.

Update this verdict only after each blocker has dated evidence, a reviewed fix, or an explicit owner waiver. C23 findings are tracked in `C23-hoth-gameplay.md`; do not erase failures when a later run uses a different server/archive.
