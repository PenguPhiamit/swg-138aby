# Plan: fork TortoiseBots when we make the new repo

15 October 2026 · Claude · plan only: nothing forked, pushed or ported yet.

**Credit.** This plan builds on **TortoiseBots by Sagiroth** (<https://github.com/Sagiroth/TortoiseBots>), licensed AGPL-3.0 with the TortoiseBots attribution term. The owner says Sagiroth gave permission to be named and to build on it. Facts below come from our archived copy (`work/research/Sagiroth_TortoiseBots`, `bc914eb3`, v6): its `LICENCE.md`, `docs/PROVENANCE.md` and `docs/LICENSE_AUDIT.md`.

## Why fork

Our server-side bots follow TortoiseBots' design (`server-side-bots.md`):
- headless sessions;
- a strategy and trigger engine;
- a module behind one host boundary, so that core code never knows a player is a bot;
- a budgeted turn scheduler, and observability.

A GitHub fork does four things for us:
- It shows that lineage on GitHub.
- It gives us a pinned reference to cite, in place of the local archive, which stays gitignored.
- It lets us take upstream fixes.
- It lets us offer generic fixes back to Sagiroth.

## When

At the same step as the **new public repository**. The export plan is to push to a fresh repository rather than make the private `swg-sandbox` public. Both steps are the owner's actions on their GitHub account, and every push needs the owner's OK.

## Layout (recommended)

| Where | What it holds |
|---|---|
| **Fork** `<owner>/TortoiseBots` on GitHub | `main` mirrors upstream and is never edited; sync it with `gh repo sync`. Branch `swg` adds one new top-level folder, `swg/`, holding the Core3 host adapter (`swg/host/`), SWG strategies, tests, and `swg/PORTED.md`, which maps each ported file to its upstream path and commit. The WoW tree stays untouched beside it, so merging upstream into `swg` never conflicts. |
| **New public SWG repo** (filtered h) | `third_party/TortoiseBots` as a git submodule pinned to a commit on the fork's `swg` branch, `CREDITS.md` with Sagiroth's credit text, and the bot docs. |
| **Core3 tree** (`Core3-dev`, published on its own path) | Only the narrow hooks the module needs: client-less login, the tick entry and the "counts as observer" flag. It also gets a CMake switch, so Core3 builds and runs with the module off, as TortoiseBots requires of its own core. |

**Alternative:** keep the bot code inside the Core3 tree with credit headers, and use the fork only as a reference. The build is simpler, but the lineage lives only in file headers, and upstream fixes have to be copied by hand. Pick it only if the submodule build proves awkward.

**A fork of a public repo is public and can't be made private.** Everything pushed to `swg` is public at once, so every push needs the same checks as the export first: `prepush_scan.py` and the names rules.

## What we may take, and on what terms

| Part | Origin (per `PROVENANCE.md` / `LICENSE_AUDIT.md`) | Use |
|---|---|---|
| Original TortoiseBots work: the host boundary and headless-session pattern, the `BotManager` lifecycle, `runtime/BotTurnScheduler.h` (bots due every 400 ms in combat, 1 s dead or in a battleground, 3 s otherwise, most overdue first), and the observability emitter and dashboard ideas | Sagiroth's own: AGPL-3.0 plus the attribution term | Port it. Keep the notice, source link and attribution term in each file. |
| `ActionFailureBackoff` (already ported to Python in `Fable-tortoise/`) | TortoiseBots, with intent ported from `Shyalya/tortoise-wow` (AGPL-3.0) | Port it; same licence family. |
| The engine (Engine, AiObjectContext, Strategy, Trigger, Action, Value, ReactionEngine) and the strategies | `Shyalya/tortoise-wow`, which vendors `cmangos/playerbots@c33dfac` (no root licence: "Unresolved"). Some later code comes from `mod-playerbots` (GPL-2.0; the sampled headers say "or later") | **Wait.** TortoiseBots' own licence audit is Open. Ask Sagiroth, through the owner, which engine files are cleared. Until then, write our own engine from the design (`server-side-bots.md`, section 3). |
| WoW content: classes, spells, raids, auction house, gear tiers | mixed | Not used; SWG has nothing to map it onto. |

**Licence fit.** Core3 is AGPL-3.0 (its `COPYING` file), the same family as TortoiseBots and its target core. A combined build is allowed once every included file's own grant is compatible. GPL-2.0-only code is not compatible; "or later" code is.

## Obligations we take on

- **Attribution term** (AGPL-3.0 section 7(b)). Forks must keep Sagiroth's credit and source link where TortoiseBots shows them: the startup log, a login message to every player, and `.bot version`/`.bot about`. Our equivalents are a `core3.log` startup line, a login system message and a `/bot about` command. They go in with the first ported file.
- **AGPL network use.** Everyone who plays on a server running this code must be able to get its source. The public repo, plus the fork's `swg` branch pinned by the submodule, covers that. The login message should carry the source link.
- **File notices.** Keep every ported file's original notice, and never relabel donor files.

## Steps and size

1. **With the new repo (about half a day, owner and Claude):**
   - The owner forks Sagiroth/TortoiseBots on GitHub, or Claude runs `gh repo fork` with the owner's OK.
   - Branch `swg` gets `swg/README.md` (credit, scope, what's ported), `swg/PORTED.md` and the licence notes.
   - The new repo gets the submodule and `CREDITS.md`.
   - Export rules: Sagiroth's name is no longer a pending decision (owner, 15 Oct); the other name scrubs stay.
2. **Move milestone 1 into the module (about 1–2 days, once it passes in Core3-dev).** The `/botpop` work from the [server-side bots plan](server-side-bots.md) moves into `swg/` behind the host boundary. Core3 keeps only the hooks and the CMake switch, and the attribution places are added.
3. **Port the clean original parts (about 3–4 days):**
   - `BotTurnScheduler`, which is our active budget;
   - `ActionFailureBackoff` in C++;
   - the observability emitter, feeding our live map and dashboard.
   Each comes with its upstream test, ported, where one exists.
4. **Engine (1–2 weeks):** port the engine files that are cleared, or finish our own engine if the audit isn't settled.
5. **Upstream (ongoing):** sync `main` monthly, and offer generic fixes to Sagiroth as pull requests, if Sagiroth wants them.

## Decisions for the owner

1. The account and name for the fork (default `<owner>/TortoiseBots`, branch `swg`).
2. A submodule (recommended), or code inside the Core3 tree.
3. Whether to ask Sagiroth now about the engine files' licence status. If they're cleared, step 4 ports the engine instead of rewriting it.
