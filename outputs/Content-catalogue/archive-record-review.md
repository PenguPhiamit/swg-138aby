# C11 downloaded-source record review

13 October 2026 · ChatGPT. Read-only audit of seven existing checkouts; **no network fetch, repository program execution, install or content import**. Git was invoked only to read HEAD, tracked paths and change names, with per-command safe.directory limited to each checkout; no global Git setting changed.

All seven HEADs match the recorded pinned revisions; no staged or unstaged tracked changes were reported. Per-materialized-file SHA-256 manifests and manifest hashes are in [archive-checkout-audit.json](archive-checkout-audit.json). A sparse checkout deliberately omits tracked files: those counts are recorded, not falsely called missing downloads. Symlinks are not followed. Source hashes establish the bytes inspected, not creator rights or binary authenticity.

| Item | Materialized files / bytes | Pin | Record review / use gate |
|---|---|---|---|
| A1 | 32,268 / 121,712,333 | matches `1f4438a129c0` | AGPL COPYING present; Hoth228-file adaptation separately inventoried. Client art remains separately gated. |
| A2 | 49,488 / 151,158,038 | matches `947a7e666dee` | Root LICENSE + Core COPYING present; selected script donor/asset chains need per-file review. |
| A3 | 32 / 479,995 | matches `cdb1cdbbe172` | LICENSE present; recorded MIT. Add-on import/export limits remain untested; not installed/run. |
| A4 | 933 / 101,698,075 | matches `72ef01b24e32` | Mixed component evidence: SWGHeightCompiler and SWGHeightDump each have WTFPLv2 COPYING; behavior-studio has GPLv3 COPYING. No root blanket grant found; other components stay uncleared. |
| A5 | 68 / 309,426 | matches `fe88c0184199` | AGPL COPYING present; sparse tests/spec selection only, not complete server tree. |
| A6 | 8,502 / 236,063,751 | matches `b2103a99b32e` | HOLD: README identifies viewer developed for owner-excluded Sentinels Republic; no licence file, casual README grant and third-party screenshots are not a clean import clearance. No SR links/images opened or assets used. Owner clarification needed before any use. |
| D1 | 1,849 / 42,557,935 | matches `bc914eb3b5f4` | Original AGPL+attribution and mixed donor lineages; open donor compatibility audit. Owner-reported author permission does not clear other contributors. Design study only. |

## Corrections needed in shared download records

- Top-level network error/zero-download notes and old board C11 block are historical; Claude fetched A1–A6 and D1. Record an explicit partial completion, with remaining A7/B/C deferred rather than implying all sections were collected.
- Existing bytes fields are estimates/checkout storage figures, not measured network transfer. Materialized tracked-byte totals above exclude .git and untracked content; keep that distinction and the 3 GB cap. Do not overwrite estimates with these as though they measure the same thing.
- A4 is per-component, not simply unlicensed or blanket permissive. A6 should be held under the existing exclusion until owner clarification. D1 licence_verified means its notice was read, not that the donor audit is resolved.
- Git commit pins are useful, but the new SHA-256 manifests now satisfy per-file byte recording for selected future work. Any actual import still records the exact asset/release, contributors, licence text and required credit next to that import.

No source files were modified/deleted, no new remote added, no account fork created. The canonical download JSON was deliberately not edited while Claude owns fetching/records; audit findings were sent through its inbox. C11 is **partially complete**, not a blanket rights clearance or completion of the full A/B/C plan.
