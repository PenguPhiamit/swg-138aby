# Pets: Creature Handler and Bio-Engineer decisions (17 Oct 2026)

The owner's answers, 17 Oct about 7:30 AM, after a Character Builder Terminal kimogila looped on the "invalid pet" window.
Code facts from Core3-dev (`PetControlDeviceImplementation.cpp`, `PetDeedImplementation.cpp`, `PetMenuComponent.cpp`).

## How it works today

- **Taming** is per creature: `tamingChance` in its mobile template. Wild kimogila (`mobile/lok/kimogila.lua`, level 95)
  have 0. The kimogila pet is the bio-engineered one (`mobile/pet/kimogila_be.lua`, template level 40) from a deed.
  On the test galaxy `Core3.TameAnything` lets sandbox players tame anything; live keeps the per-creature rule.
- **Calling:** without Creature Handler, 1 pet up to level 10. With CH, the skill mods `keep_creature` (how many)
  and `tame_level` (their total level) decide; vicious pets also need `tame_aggro`. God mode skips these (owner, 15 Oct).
- **The invalid-pet check** (deed pets only): the deed's level must be at least 85% of the level its stats work out to.

## The owner's decisions

| Question | Decision |
|---|---|
| Pets per Creature Handler box and their total level | **Later, after data.** |
| Which creatures can be tamed | **The same basic premise for wild creatures, expanded a bit. Extra-dangerous creatures (krayt, wampa, certain bosses) only through bio-engineering or breeding, like the kimogila.** The owner and Claude go through the list together. |
| The invalid-pet check | **Fix it properly for everyone so bio-engineered pets can be repaired.** "I want CH and BE to be viable ... super good pets I think will be OK", since the trees and scaling are being expanded. The owner is a little worried players won't like strong pets. |

## Done (dev, not yet tried in game)

- `44c2933a` God mode: the invalid-pet check is skipped, and a pet's radial has **"Teach every command (god mode)"**
  (id 72), which teaches every standard command, each by its own name ("follow", "stay", "attack" and so on). This is the
  owner's "macro to train my creatures"; a client macro can't pick radial options.
- `393c5c25` For everyone: the fix window is a list box now (as the mount growth window), so **Adjust Pet Level** and
  **Adjust Pet Stats** each do what they say; before, both ran Adjust Pet Stats. **Adjust Pet Level** has no level-75
  ceiling any more.

## Next

- The taming list, together with the owner: wild creatures to add, and the krayt, wampa and boss lines for BE or breeding.
- CH limits once there is data from players and bots.
