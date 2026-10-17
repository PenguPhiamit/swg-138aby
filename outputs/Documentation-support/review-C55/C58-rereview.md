# C58: re-review of the C55 F1 and F2 fixes (dev `c5d713b8`)

Reviewer: Claude (side session, 16 Oct, about 10 PM), taking GPT's queued task C58 while GPT is out until 22 Oct.
Read-only, from `/opt/swg/Core3-dev` at `8edfd13f` (which contains `c5d713b8`) and from live's `920203d8`. I read the
source through files copied inside WSL. Nothing was built and no galaxy was touched. Paths are relative to
`MMOCoreORB/`.

**Summary.**

- **F1 is closed.** The task now takes its locks in the stock order. It is fit for release 1 as a hand-applied swap of
  two lines.
- **F2 is closed for its counterexample** (a solo master carrying their own line's weapon) **but not in general.** The
  gate's "level" is the level of the weapon in hand, not of the character. The gate as written also leaves every area
  whose rows start at 40 or more empty for solo levels 1 to 9.
- **For release 1:** ship the five data fixes, and ship the gate off on live (`LevelGateBase = 0`) until the owner picks
  a rule.

## F1: the helper droid lock order

**The change.** In `objects/player/events/SpawnHelperDroidTask.h:79-80`, the existing-droid path is now:

1. `Locker plock(playerCreo)` (line 56);
2. `Locker clock(helperDroidObject, playerCreo)`;
3. `Locker lock(controlDevice)`.

That is the same order as the stock radial call (`PetControlDeviceImplementation.cpp:357-363` and `377-383`: player,
the pet cross-locked against the player, then the device). Live (`920203d8`) still has the old order: device, then the
droid cross-locked.

**Why it closes C55's schedule.** Engine3's cross-lock (`ReadWriteLock::lock(Lockable*)`, ReadWriteLock.cpp, about
line 283) loops: it tries the target, and if that fails it unlocks the cross lock (the player) and blocks re-locking
it. It never blocks on the droid itself, so the only thing it can block on is the player, while holding whatever else
the thread already holds.

- **Old order.** The thread already held the device, so T1 blocked on the player while holding the device. T2, holding
  the player, then blocked on the device. That is a cycle.
- **New order.** At the cross-lock the thread holds only the player.

C55's case (one character, two helper tasks, the droid held by its AI) now runs like this:

1. T1 holds P and fails to get H. It releases P and blocks re-locking P.
2. T2 gets P and fails to get H. It releases P, and T1 takes P back.
3. The two spin on P only, holding nothing else.
4. When the AI lets go of H, whichever task holds P gets H, then plain-locks C. Nobody holds C, so it gets it, calls,
   and releases all three.
5. The other task then does the same. `callObject` returns at once, because `ghost->hasActivePet(pet)`
   (PetControlDeviceImplementation.cpp:92), so the second call is harmless.

**The other paths in the task.**

- **New-droid path.** The task holds P through creation, `transferObject` into the datapad and the call, so a second
  task waiting on P finds the new device and takes the existing-droid path. One theoretical gap: `Locker
  clocker(creatureObject, playerCreo)` at line 115 cross-locks a brand-new creature while the new device is held
  (line 106). If that try ever failed, P would be released before the device is in the datapad, and a second task could
  create a second droid. There is no deadlock in that case: the second task can't know about the first one's device. A
  fresh object is practically never contended. Not blocking.
- **After the spin.** While the cross-lock spins, P is released and taken again, so the datapad can change in between.
  The device is a strong `Reference` and the droid a `ManagedReference`, and `callObject` returns when the device is no
  longer under the player (`isASubChildOf`, line 38). Nothing dangles.
- **Remaining edge, inherited from stock.** `PetControlDeviceImplementation::destroyObjectFromDatabase` (line 771)
  plain-locks the pet while its caller holds the device: device → pet. Against player → pet → device, that is a
  possible cycle. But it is the same exposure the stock radial call already has, it needs the helper droid's device to
  be destroyed at the same instant, and this commit doesn't add it.

**Duplicate task admission.** It is still unguarded: `notifySceneReady` on every zone-in during the first day, plus the
skill-trained path at CreatureObjectImplementation.cpp:1573. With the new order it no longer needs a guard for safety:
duplicates serialize on P and the second call returns. A guard would only remove the theoretical second droid above.
Optional: a transient "helper task pending" flag on the PlayerObject.

**Small fix.** The comment at `PlayerObjectImplementation.cpp:3874` still describes the old order ("player -> device
-> droid"), and it is now wrong. Correct it on dev.

**Fit for release 1: yes, by hand.**

- **Don't cherry-pick `c5d713b8`.** Its F1 hunk sits next to the BotPop registry check (`3dca6772`/`61f5d886`), which
  live doesn't have, and the commit also carries F2.
- **On the release branch, swap the two lines** in live's task (device lock above the cross-lock today) to the order
  above, with the comment.
- **Rehearsal check, with a normal unregistered character:**
  - create a character, which spawns the droid;
  - travel, or log out and in, within the first day, which calls it again;
  - train a skill;
  - store the droid and call it from the radial;
  - pass when the droid appears once, nothing hangs, and the console shows no lock-trace errors.

## F2: the spawn level gate

**The change.** In `objects/region/SpawnAreaImplementation.cpp:303-307`:

```
skip a row when LevelGateBase > 0 && playerLevel < LevelGateMaxLevel && minDifficulty > LevelGateBase + 3 × playerLevel
```

The defaults are 10 and 10, read once into function-local statics, so a change needs a restart.

**What `playerLevel` is.** It comes from `getPlayerSpawnLevel` (line 420):

- **Solo:** `PlayerManagerImplementation::calculatePlayerLevel`, which is
  `min(25, private_<weapon in hand>_combat_difficulty / 100 + 1)`. That is the level **of the weapon being held**, not of
  the character.
- **Grouped:** `group->getGroupLevel()` (GroupObjectImplementation.cpp:562-624): the highest member's level, plus
  1/5 of each of the others'.

| Case | Level | Threshold | Krayt NE (rows 122, 275, 320, 320) | Newbie tables (minima 1-10) | `tatooine_easy_*` (1-60) | Dantooine/Lok 50, Endor 70, Dathomir 80, Rori/Talus southern 40 |
|---|---|---|---|---|---|---|
| Novice, solo | 1 | 13 | none | all | rows ≤13 | **nothing** |
| Level 9, solo | 9 | 37 | none | all | rows ≤37 | **nothing** |
| Level 10, solo | 10 | ungated | all (stock) | all | all | all |
| Solo master with own weapon | 25 | ungated | **all: F2's counterexample is closed** | all | all | all |
| Solo master holding another line's weapon, or a non-combat veteran | 1 (that weapon's mods) | 13 | **none: the counterexample comes back** | all | rows ≤13 | **nothing** |
| Group of novices (five level 1s) | about 2 | 16 | none | all | rows ≤16 | nothing |
| Novice grouped with a master | 25+ | ungated | all (stock) | all | all | all |

Findings:

1. **Weapon-based level (open).** A master rifleman holding a pistol, or a master crafter or entertainer out
   exploring, counts as level 1 and is gated like a new character. C55's krayt counterexample comes back for exactly
   these players.
   - **Fix:** use the highest `private_*_combat_difficulty` across the eight weapon types (plus Jedi) for the gate,
     not the weapon in hand. A non-combat veteran stays gated, which the owner should confirm is wanted.
2. **Empty mid-level areas for levels 1-9 (design, owner's call).** Every area whose rows all start above `10 + 3 ×
   level` spawns nothing new for that player. For solo levels 1-9 that means Dantooine, Lok, Endor, Dathomir and the
   40-minimum Rori and Talus areas, wherever no one else has spawned things there. Stock would spawn them, with the
   lair's building level scaled down. This is a choice ("new characters stop meeting creatures far above them"), but
   it reaches well beyond "next to town".
3. **No effect in the newbie tables themselves.** Their minima are 1 to 10, below even a novice's threshold of 13. So
   the gate acts only in the general "easy" and higher areas around towns, which matches the owner's 15 Oct intent for
   `tatooine_easy_*`.
4. **The level 9 / 10 step** goes from "rows ≤37" straight to "everything". That is acceptable: at level 10 the stock
   building-level scaling (lines 317-329) takes over.

**Fit for release 1: not as written.** The gate itself (from `b20a46d7`) isn't on live. I'd ship it off:

- set `Core3.SpawnArea.LevelGateBase = 0` in live's `config-local.lua`, written out so it is visible;
- or include it only after finding 1's fix and the owner's yes on finding 2.

Take only the gate and data hunks from `b20a46d7`. Its BotPop mission-selection edits stay on test.

## What I would change in live-release-1.md's table

| Row | Now | Change to |
|---|---|---|
| Helper droid deadlock fix | "written and built; GPT re-review (C58)" | **Fit (C58).** Hand-apply the two-line swap on the release branch (no BotPop context), and fix the stale comment at PlayerObjectImplementation.cpp:3874. Add the new-character helper check to the dress rehearsal's pass list. |
| Spawn gate, new characters only, and the five newbie spawn fixes | one row, "after a test" | **Split it.** (a) The five newbie spawn-data fixes: fit after the visits C55 asked for. (b) The spawn gate: ship it **off** on live (`LevelGateBase = 0`), or hold it until the gate uses the character's highest weapon level and the owner OKs that solo levels 1-9 get no new spawns in the 40+ areas. |
| (deploy step 6) | "add the config line" | Write out all three release config lines: `MaxActiveMissions = 2`, `LevelGateBase` and `LevelGateMaxLevel`. |

## What I could not check

- **Runtime.** No build or run of the release branch and no lock trace. The F1 analysis follows engine3's cross-lock
  source, not a reproduction.
- **What `CreatureObject::getLevel()` returns for a player** in the group formula. I took the group rows from the
  formula's shape, not from a measured group.
- **Spawn areas other than those listed.** I read the krayt NE table and the `*easy*` / `*newbie*` tables, not every
  medium or hard table on every planet.
