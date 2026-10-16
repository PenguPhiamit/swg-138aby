# Live release 1: plan (draft, Claude, 16 Oct 4:25 PM; revised 4:45 PM after GPT's C55)

Nothing is deployed. This is the plan the owner OKs or changes; GPT's C55 review decides
which commits are fit, and the dress rehearsal (step 3) proves it before live is touched.

## After C55 (4:45 PM): a small first release instead of all of dev

GPT's C55 approves no whole-dev merge, and it is right on the facts that matter:
- `64156084` also starts 224 test creatures (T1/T2/S1-S5) in five cities for everyone, with no
  test-only switch;
- the spawn gate (`b20a46d7`) as written removed krayt spawns for solo masters (F2);
- the helper droid deadlock reaches real new players (F1).

The whole-dev route below stays as the later "friends launch" release (with C57's client patch
and the Hoth gate). **Release 1 becomes a release branch cut from live (`920203d8`)** with only
reviewed, player-facing changes:

| Change | Source | State |
|---|---|---|
| Helper droid deadlock fix (stock bug: device locked before the droid) | new, dev 16 Oct (C55 F1) | written and built; GPT re-review (C58) |
| Per-type XP multipliers | `40af2c78` | fit (C55); all 1.0 unless configured |
| CitiesAllowed guard only | from `64156084`, split out | fit after splitting (C55) |
| Name filter: canon names, whole words | `d1cd02c6`, `0f045a47` | reviewed earlier; owner's rule |
| Spawn gate, new characters only, and the five newbie spawn fixes | `b20a46d7` + F2 fix | after a test of solo-master and novice spawns |

Held for later releases:
- crafting missions (`db5952f5`, `74fa3e8c`) and six missions: the owner's mission hold and C56;
- the city spawn tests;
- BotPop;
- Hoth, Ossus and the species (C57 client patch).

Cherry-picks onto live's older base are checked by building and by the dress rehearsal (step 3).

## Where live is

- Live `/opt/swg/Core3` (branch `sandbox`) is at `920203d8`, 13 Oct 10:40 AM. Dev
  `/opt/swg/Core3-dev` is at `a8ece12b`: **113 commits** live doesn't have (merge base `50ede927`).
- Live has 4 commits of its own. Three are older copies of dev commits (mercenary broker
  `9f74dd57` = dev `2347100a`, `28aa46d8` ⊂ dev `b942d9b5`, MTG script tracking `920203d8` =
  dev `6cdb4aef`); one is a doc (`cfdd1aa2`, local-dev/README.md) to carry over by hand.
- Live loads the MTG archives but **not** our `local_planets.tre`, and its `ZonesEnabled` has
  no Hoth or Ossus.

## Recommendation: deploy dev as a whole, with config holding back what isn't ready

Cherry-picking a subset of 113 commits that build on each other is where mistakes come from.
Dev was built so that test-only code is inert on live, and the plan relies on that:

- **Test-only, inert on live by design.** Every sandbox helper requires
  `isDisposableTestGalaxy()` (the database name ends in `_test`; live's is `swgemu`) *and* its
  own flag, so a flag copied into live's config by mistake still does nothing. This covers
  BotPop (all `managers/botpop`), MedicalAnywhere, TameAnything, god-mode pet limits, the
  sandbox tools datapad, the 2-second logout, and `/agentpath` (allowlisted agent accounts only).
  The agent client (`src/client/agent`) is not part of the server.
- **Held by config.** `Core3.MissionManager.MaxActiveMissions` defaults to **6** in dev. The
  six-mission release is on hold (owner), so live's `config-local.lua` must say
  `Core3.MissionManager.MaxActiveMissions = 2` in this release.
- **Held by the archive.** Hoth, Ossus, the Chiss, the Hutt and the Artisan floater need
  `local_planets.tre` on every client. Live doesn't load it, and Hoth and Ossus stay out of
  `ZonesEnabled`, so they ship dormant. They go live together with the friends' client patch
  (GPT's C57) and the Hoth release gate (C24, NO-GO today).

## What players on live would notice

From C55's list, if GPT finds them fit:
- the spawn level gate (`b20a46d7`; new characters stop meeting creatures far above them;
  `Core3.SpawnArea.LevelGateBase`, default 10) and five newbie spawn-data fixes;
- per-type XP multipliers (`40af2c78`; all 1.0 unless configured);
- crafting missions keep shared recipes, and delivery takes one item (`db5952f5`, `74fa3e8c`);
- a planet without a CitiesAllowed row allows no cities (`64156084`; the owner's "no cities on
  Hoth or Ossus").

Already reviewed earlier (C4b-C4f, C19, C22, C24b, C34r, C39):
- the name filter (canon names allowed, whole-word matching);
- the leash and follow assist (`Core3.LeashEnabled`, on by default; C6 is the real-client test
  after this deploy);
- the pet follow gap;
- the BARC speeder fix;
- weather entries;
- the shuttle ticket messages;
- the mercenary broker;
- the resource pool changes (Hoth and Ossus resources only spawn where those zones run).

## Gates, in order

1. **GPT C55** (running): a verdict per commit. Anything not fit is reverted on a release
   branch cut from dev, not removed from dev.
2. **GPT C56**, only when the six-mission hold lifts: the full-datapad gate.
3. **Dress rehearsal** (Claude): the release build with **live's config** (no
   `local_planets.tre`, live's zones) against a restored copy of the live database on the
   45xxx ports, the way `tools/restore_rehearsal.py` does (database `swgemu_rehearsal`, which
   doesn't end in `_test`, so test-only code stays inert exactly as on live).
   - Pass means:
     - no new console errors compared with live's own start;
     - the dormant Hoth/Ossus screenplays, resources and species templates load quietly;
     - a real client logs in and plays an existing character;
     - the mission cap is 2.
   - It runs when the test galaxy is stopped (memory).
4. **Backups**: `tools/backup_server.py` for the live database and the current `bin/core3`;
   rollback = restore both.
5. **The owner's OK** for the deploy (AGENTS.md: live changes always need it), with GPT's
   "reviewed by" in the handoff log.
6. **Deploy**: stop live, move `/opt/swg/Core3` to the release commit, `rebuild_server.py`,
   add the config line, start, watch the console, log in.

## Open questions for the owner

- Release 1 as the small set above (recommended since C55), or wait and ship everything
  together at the friends launch?
- The spawn level gate on live in release 1 (new characters only, after the spawn test), or
  off on live (`LevelGateBase = 0`) for now?
