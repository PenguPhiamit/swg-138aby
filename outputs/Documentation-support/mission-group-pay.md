# Mission group pay: judged from the end point only (staged fix)

Claude (missions side session), 17 Oct 2026. Found by the mission scenarios for `functional-test-plan.md` section 11. **Staged, not installed, unbuilt.** The main session builds it with the next restart batch.

- Patch: [`mission-group-pay.patch`](mission-group-pay.patch), against Core3-dev `25344120`. `git apply --check` is clean. It changes one file, `MissionObjectiveImplementation.cpp` (`awardReward`).
- Check: `tools/bots/missions.py` `destroy()`, "everyone who fought at the lair is paid", and its offline test `test_a_lair_far_from_the_first_waypoint_shows_the_group_pay_bug`.

## The bug

`MissionObjectiveImplementation::awardReward` pays each group member within 128 m of the mission's **end point**. If none is, it pays the owner alone. The owner always gets "group_too_far" when anyone is left out. Two mission types end somewhere else:

- **Destroy.** The generator sets start = end = the spot it picks (`MissionManagerImplementation.cpp`, `randomizeGenericDestroyMission`). When the owner comes near, the lair spawns up to about 256 m away. `DestroyMissionObjectiveImplementation.cpp:175` then moves the start and the waypoint to the lair, but not the end. So the players fighting at the lair are out of range whenever the lair is more than 128 m from the first waypoint.
- **Hunting.** The end is where the list was made, at the terminal in town (`randomizeGenericHuntingMission`: `setEndPosition(player position)`). A grouped hunter out in the field gets nothing if any groupmate is still near that terminal.

In both cases the share of whoever stands near the end point is paid, and the share of the players who did the work is lost. Solo players are not affected: with no group, the owner is always paid.

## Evidence (test galaxy)

1. **Destroy, 17 Oct 5:38 AM** (gate run of `cresh-missions.py`, report `Bot-reports/Cresh/20261017-053833-cresh-missions.json`).
   - The mission: "@mission/mission_destroy_neutral_easy_creature:m28t", reward 383, a group of 3, so a share is 127.
   - The first waypoint was at about (3155, -3005). The lair (`tatooine_kreetle_over_death_neutral_medium_boss_01`) spawned at about (3386, -2917), roughly 247 m away.
   - Cresh (the owner) and Kor destroyed it there. Ilsa had been incapacitated, then killed, near the first waypoint.
   - At t = 538.6 s, Cresh got `@mission/mission_generic:group_too_far` and `group_success`, but no `success_w_amount`. Kor got no mission message. Ilsa got `@mission:mission_generic`, the body's truncated `success_w_amount`, at t = 540.6 s, while dead.
2. **Hunting, 17 Oct 12:22 PM** (`forn-missions.py`, report `Bot-reports/Forn/20261017-122209-forn-missions.json`).
   - Forn finished a hunting mission ("@mission/mission_npc_hunting_neutral_easy:m7t", reward 1010, a group of 5, so a share is 202) by killing rills out of town. The mission left his datapad.
   - His bank stayed at 100000 → 100000, and he got `group_too_far`. The groupmate near the scout terminal who was presumably paid instead was not measured.

## The fix

A group member is in range when within 128 m of the end point **or** of the owner at the moment the mission completes, in the same zone, measured flat (the owner's z set to 0, as the code already does for bounty missions).

- **Nobody loses pay.** Everyone in range today stays in range.
- **The owner is always in range of themselves**, so a grouped owner who did the work is always paid. Members fighting beside the owner are paid too.
- **The money stays the same.** The divisor is unchanged (`max(rewardCreditsDivisor, group size)`), so no share gets bigger and the total never exceeds the reward. The only change is that shares which used to be lost are now paid.
- **Faction points and the end-point log are unchanged.** Faction points come from `awardFactionPoints`, which doesn't use the in-range list. The transaction log still records the mission's end point; only its "in range" count changes.

An alternative is to move the destroy end point with the lair (one line at `DestroyMissionObjectiveImplementation.cpp:175`). It fixes destroy only, not hunting, and it would stop paying a member who waited at the first waypoint.

## How to check it after the build

- **Destroy.** Run `squad.py run scenarios/cresh-missions.py --round-minutes 40`.
  - Unpatched, "general/destroy: everyone who fought at the lair is paid" fails whenever `lair_from_first_waypoint_m` is over 128. The RESULT and the shares note give the numbers.
  - Patched, it passes at any distance.
- **Hunting.** In `forn-missions.py`, "scout/hunting: the share reaches the bank" passes with the patch even when a groupmate stands at the scout terminal.
- **Offline.** `python -I tools/bots/test_missions.py` runs the fake galaxy both ways. Unpatched, Ilsa and Kor are unpaid when the lair lands 200 m away; patched, nobody is.
