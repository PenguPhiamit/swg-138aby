# Bank terminal radials: any range, while dead (staged fix)

Claude (missions side session), 17 Oct 2026. Bug 3 of `functional-test-plan.md` section 11. **Staged, not installed, unbuilt.** The main session builds it with the next restart batch.

- Patch: [`bank-terminal-range.patch`](bank-terminal-range.patch), made against Core3-dev `4b113bb7`. `git apply --check` is clean there and on the newer head `1be13676`. It changes one file, `BankTerminalMenuComponent.cpp` (`handleObjectMenuSelect`).
- Compile: the patched file passes a syntax-only compile (`-fsyntax-only`, with the flags from `build/dev/compile_commands.json`). Nothing was written to the build tree.
- Check: `python -I tools/bots/test_missions.py` (44 tests, OK). `test_with_the_bank_range_patch_the_bot_walks_to_the_terminal_and_back` runs the fake galaxy with the patched rule: 8 m, and no window while dead.

## The bug

- `RadialManagerImplementation::handleObjectMenuSelect` only checks building entry, and `BankTerminalMenuComponent::handleObjectMenuSelect` has no range or state check. So every bank radial works from anywhere in the zone, and while dead or incapacitated:
  - 20 (use) and 68 (Deposit/Withdraw window);
  - 69 (Deposit all) and 70 (Withdraw all), which move money at once;
  - 71/72 (join/quit the bank) and 73 (safety deposit box).
- Only the transfer window's own callback (`BankTerminalSuiCallback`) checks 8 m, and only when the player presses OK.
- So Deposit all and Withdraw all, and opening the safety deposit box, worked at any distance. A real client range-checks radials itself, but a modified client or a bot doesn't have to.

## Evidence (test galaxy)

- 17 Oct about 6 AM: Kor, dead and 2 km from the nearest bank terminal, opened its Deposit/Withdraw window. The mission scenarios read balances that way, read-only and cancelled at once, because the body forgets `bank_credits` (test plan section 11, bug 3).
- `tools/bots/missions.py` `bank_window()` relied on it: it chose a terminal once and selected it from wherever the bot stood.

## The fix

For the bank's own radials (20 and 68–73), before anything else:

- **Dead or incapacitated:** the player gets `@error_message:wrong_state` and nothing happens.
- **Out of range:** a player more than 8 m from the terminal (`isInRange`: flat, same zone; the range the transfer callback already uses) gets `@ui:radial_out_of_range_prose` with the terminal's name, as that callback sends it. Nothing happens.

Other radials (examine and so on) still go to `TangibleObjectMenuComponent` unchanged.

## The bot side (adapted in this commit)

`missions.py` `bank_window(bot, back='here')` now:

1. finds the nearest bank terminal each time (within 3 km);
2. walks to it when it's more than 6 m away;
3. opens the window, reads the balance and cancels;
4. walks back:
   - to `back` when it is a terminal (`take()` passes the mission terminal, since the accept needs 6 m);
   - with `'here'`, to where the bot stood, when that was outdoors. An indoor spot has no world walk target, so the bot stays at the bank; pass the terminal instead.

This works the same on stock and patched servers, so it can go in before the build.

The cost is time: a balance read at a lair is a walk to town and back. The walk isn't guarded, unlike `at_terminal`'s walks over 300 m. Once the body keeps `bank_credits` again (the body fix, test plan bug list), `bank()` takes the balance from `status()` and never walks.

## How to check it after the build

- **By hand.** A bot dead or 2 km from a terminal selects radial 68: no `Script.transfer` page comes, and the system message is `wrong_state` or `radial_out_of_range_prose`. Within 8 m and alive, the page comes as before.
- **Scenarios.** Any mission scenario's "the share reaches the bank" still gets numbers (the bot walks to the terminal for each read). If it shows `paid: None`, `bank_window` found no terminal within 3 km or didn't arrive.
