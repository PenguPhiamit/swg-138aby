# Veteran Rewards Report

## 1. Short Answer

Veteran rewards are granted to players based on **account age in days**, not character play time. The system checks the account's total logged-in days against predefined milestones (e.g., 30, 60, 90, 180 days). When a player reaches a milestone, they become eligible and receive a system message prompting them to use `/claimVeteranReward`. The claiming process opens a SUI list box where the player selects from available rewards for that milestone, then confirms. Rewards marked `oneTime` can only be claimed once per account. At 180 days, players also receive a special Jump to Lightspeed (JTL) yacht announcement.

## 2. How It Works

### Eligibility Conditions
- **Account age**: The system uses `account->getAgeInDays()` to determine eligibility (`GetVeteranRewardTimeCommand.h:49`). This is the total account creation age, not character play time.
- **Milestone checking**: `playerManager->getEligibleMilestone(ghost, account)` returns the milestone number if eligible, or `-1` if not (`GetVeteranRewardTimeCommand.h:55`).
- **Next milestone**: If not eligible, `playerManager->getFirstIneligibleMilestone(ghost, account)` returns the next milestone to reach (`GetVeteranRewardTimeCommand.h:72`).

### Messages the Player Sees

**When checking eligibility (via `/getVeteranRewardTime`):**
- Always shows account age: `"You have %DI days logged for veteran rewards."` (`GetVeteranRewardTimeCommand.h:48`)
- **If eligible**: `"You are eligible for the %DI day veteran reward! Use the /claimVeteranReward command to get your reward."` (`GetVeteranRewardTimeCommand.h:58`)
- **If 180+ days**: Also shows JTL yacht announcement: `"Congratulations! You have earned the 180-day Jump to Lightspeed Veteran Reward, the Sorosuub Luxury Yacht! You can claim this reward for every character on your account."` (`GetVeteranRewardTimeCommand.h:65`)
- **If not eligible**: `"You are not currently eligible for a veteran reward."` followed by `"You will be eligible for the X-day reward in Y days"` (`GetVeteranRewardTimeCommand.h:69,73-74`)
- Always shows character play time at the end (`GetVeteranRewardTimeCommand.h:79`)

### Claiming Process
1. Player runs `/claimVeteranReward` command (`ClaimVeteranRewardCommand.h:28`)
2. System opens a **list box SUI** showing available rewards for the eligible milestone (`SelectVeteranRewardSuiCallback.h:46-47`)
3. Player selects an item by index; if cancelled or invalid, session is cancelled (`SelectVeteranRewardSuiCallback.h:28-43`)
4. On selection, system shows a **confirmation message box** via `playerManager->confirmVeteranReward()` (`SelectVeteranRewardSui.h:50`)
5. If confirmed, reward is generated via `playerManager->generateVeteranReward()` (`ConfirmVeteranRewardSuiCallback.h:34`)

### Reward Structure (from VeteranReward.h)
Each reward has:
- **templateFile**: The item template to generate (`VeteranReward.h:14`)
- **milestone**: Which day milestone this reward belongs to, in days (`VeteranReward.h:15`)
- **oneTime**: Whether it can only be claimed once per account (`VeteranReward.h:16`)
- **description**: Text description (`VeteranReward.h:17`)
- **jtlReward**: Whether it's a Jump to Lightspeed reward (`VeteranReward.h:18`)

Rewards are loaded from Lua data via `parseFromLua()` (`VeteranReward.h:48-53`).

### Session Tracking
A `VeteranRewardSession` tracks the current claiming process (`VeteranRewardSession.idl:10`):
- **milestone**: The day milestone being claimed (`VeteranRewardSession.idl:12,17`)
- **selectedRewardIndex**: Which reward index the player selected (`VeteranRewardSession.idl:14,28`)

## 3. What a Bot Test Should Check

### Setup Needed First
1. Create or use an account with known age (or manipulate test environment to simulate account age)
2. Ensure the account has reached at least one milestone threshold (e.g., 30+ days simulated)
3. Have a player character logged in

### Observable Results to Check

**After running `/getVeteranRewardTime`:**
- System message showing account age in days (`GetVeteranRewardTimeCommand.h:48`)
- If eligible: system message with milestone number and claim prompt (`GetVeteranRewardTimeCommand.h:58`)
- If not eligible: "not_eligible" message plus next milestone countdown (`GetVeteranRewardTimeCommand.h:69,73-74`)
- Character play time message at the end (`GetVeteranRewardTimeCommand.h:79`)

**After running `/claimVeteranReward` (if eligible):**
- SUI list box appears with reward options
- Player selects a reward and confirms
- Reward item should appear in player's inventory or be delivered via mail
- If `oneTime` is true, subsequent checks should show no new eligible milestone for that day count

**For 180+ day accounts:**
- JTL yacht announcement message appears (`GetVeteranRewardTimeCommand.h:65`)

## 4. Likely Reasons a Test Sees No Effect

1. **Account age too low**: The test account hasn't reached the first milestone (likely 30 days). Account age is checked via `account->getAgeInDays()`, which reflects real account creation time, not character play time (`GetVeteranRewardTimeCommand.h:49`).
2. **No rewards defined for that milestone**: Even if eligible, no reward entries exist in the Lua data for that milestone number.
3. **oneTime flag already claimed**: If the reward was previously claimed on this account and `oneTime` is true, it won't appear again.
4. **JTL not installed**: The 180-day yacht message only appears if the account age is >= 180 days (`GetVeteranRewardTimeCommand.h:64`).
5. **PlayerManager not initialized**: If `playerManager` is null, commands return `GENERALERROR` without messages (`ClaimVeteranRewardCommand.h:25-26`, `GetVeteranRewardTimeCommand.h:35-36`).

## 5. Open Questions

The provided files are headers and an IDL file; they **do not contain the PlayerManager implementation**. The following critical details are missing:

1. **Which milestones exist**: What day values (30, 60, 90, etc.) are defined? This data is loaded from Lua but no Lua files are provided.
2. **How rewards are selected per milestone**: Which rewards appear for each milestone? The list box population logic is in PlayerManager (not provided).
3. **How `oneTime` is enforced**: What storage tracks claimed rewards? Likely a player object field or database entry, but the implementation file is missing.
4. **How JTL yacht is generated**: Does it go to inventory, mail, or a special delivery system? The `generateVeteranReward()` function body is not in these files.
5. **Reward template format**: What does `templateFile` look like (e.g., `"object/tangible/wearables/jetpack/jetpack_common.iff"`)? No examples provided.
6. **Whether rewards are per-character or per-account**: The 180-day message says "for every character on your account" (`GetVeteranRewardTimeCommand.h:65`), but it's unclear if lower-milestone rewards are also account-wide or character-specific.

The missing files that would answer these questions include:
- `PlayerManager.cpp` (or `.cc`)
- Lua data files defining veteran reward entries (likely in `data/veteran/` or similar)
- PlayerObject storage for tracking claimed rewards
