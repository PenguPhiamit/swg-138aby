# C8–C10 validation

13 October 2026 · ChatGPT.

- Python compile: MCP adapter and three modified scenarios passed.
- Offline adapter contracts: indoor coordinates, timeout clamp/headroom, path dispatch, mission acceptance payload, SUI arguments, menu-before-select ordering and incomplete-coordinate rejection passed. No daemon was contacted.
- Coverage inventory: 86 unique feature IDs and 39 profession/track rows, 125 CSV records.
- In-game wrappers/scenarios/mapping: **untested**, Claude to run on test galaxy. MCP process must reload to discover new tools; body capabilities remain deployment-dependent.
- Doctor scenario can remain BLOCKED until an interior hospital anchor and medical rating are available. Harvest deliberately blocks unknown-level or >5 prey and low HAM; this is not proof the hunt can complete.

C9 offline fixtures (`tools/check_c9_offline.py`) passed: nearest eligible mission selected; >600 m/cross-planet excluded; no interior hospital cell means no walk/buff; level-30 prey means no fight. Revised mission completion requires both lair disappearance and removal of the accepted mission; payout is explicitly unverified. These checks do not establish runtime success.
