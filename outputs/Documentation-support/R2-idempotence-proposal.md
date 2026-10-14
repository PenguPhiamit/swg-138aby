# R2 multi-zone idempotence: proposed correction

14 Oct 2026, ChatGPT. **Design only. No source patch, cherry-pick, resource edits or running-galaxy change.** Owner asked to close the session before usage exhaustion; implementation returns to Claude's review queue.

The P2 counterexample remains in `hoth-release-gate.md` and `tools/hoth/test_release_formats.py`. A fixed hash is insufficient when its acceptance threshold uses the current map count: another target zone can increase that count between boots.

Proposed policy for unchanged active/backfill configuration: compute the numerator once per spawn as the number of maps whose zone is **outside the configured backfill target set**. Use that stable numerator for every target-zone roll. Continue checking the actual current total against maxPool before each insertion and skip zones already present.

Backfill additions cannot change this numerator. Previously rejected candidates therefore stay rejected on another boot; winners are already present. Capacity stays bounded. Configuration changes, ordinary new-spawn generation and unrelated map changes are outside that narrow idempotence guarantee.

This is a conservative migration policy, **not an exact reconstruction of the creation-time random choice**. A target zone that already had a naturally generated map is excluded too, because existing data does not distinguish natural and backfilled maps. Claude should compare this policy with persisted migration eligibility, or explicitly restricting a migration to one zone. Do not retain the old claim that the probability necessarily equals the historical creation-time probability.

Before acceptance: prove unchanged two/three-zone loads reach a fixed point, exercise target order and maxPool exhaustion, existing natural target maps, no targets, restrictions/JTL, config changes and resource expiration. Then build and run repeated test-galaxy starts with saved counts under the owner/lock rules. Existing defaults remain empty/inactive; no live enablement is authorized.
