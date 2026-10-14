# C4b + C4c review packet (exported 13 Oct for an offline review: no WSL needed)

- `01-cde59ec5.patch`: `/agentpath` 256-point cap, input validation, request echo (fixes C4 F3).
- `02-3797430a.patch`: agent body, one move deadline (F1), no path walking while down (F2), survey decode, indoor look, scene reset.
- `03-leash-helpers-missions-net.diff`: the commit messages of `09a56205`, `220e0f39`, `f25c90f9` and `2970b47e`, then the **net** diff `3797430a..2970b47e`. Four files had been saved with CRLF in between, and `2970b47e` puts LF back, so the net diff shows only real changes. Covers:
  - `/leash` follow assist and its two fixes;
  - `/agentgear` and `/agentskill`, test galaxy only;
  - body error labels;
  - mission-object decoding.
- `files/`: the current full versions of the touched files, for context.
- `commits.txt`: the recent dev history.

What to look for: the C4b and C4c sections on the board (`SWG-handoff.md`). In particular, check that `/agentgear` and `/agentskill` can't act on live: they need `Core3.AgentGear = true` and the `Core3.AgentAccounts` allowlist.
