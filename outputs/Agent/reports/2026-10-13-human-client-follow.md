# Human-client follow investigation — in progress

13 October 2026, ChatGPT. Owner reports [name removed] [name removed] (alt) runs away or into a wall after following [name removed] (main). Owner authorized reading console/settings, then explicitly confirmed being at the PC with both clients logged in and permitted window inspection. **Root cause and fix not yet established.**

## Observed

- Windows: SWGEmu PID 16460 / HWND 660484 = [name removed]; PID 30604 / HWND 1179684 = [name removed]. These are session-specific identifiers, not stable launch settings.
- Captured both windows with Universal Modder's `um.win.shot`, using exact HWNDs and also saving 0.33-scale copies. Both client areas are 1600 × 900.
- First captures: [name removed] at approximately 3501,-4764, z5; [name removed] at approximately 3514,-4744, z5, against a wall. [name removed]'s selected target and group member are [name removed], about 24 m away. Chat shows “You start following [name removed]” and subsequent “You stop following [name removed].”
- Second captures: [name removed] had moved out near [name removed], approximately 3495,-4760, z5, and chat shows a new follow start. [name removed]'s window rendered [name removed] nearby. Captures are sequential, not synchronized position measurements or continuous video.
- Owner then reported the open-street test **still runs the wrong way or gets stuck**. Therefore an intervening wall alone does not explain the report. Target selection is confirmed correct in the captured state; steering/input/frame timing remain hypotheses.
- The last 20 minutes of `swg-local` journal, filtered for follow/movement/teleport/bounce/blocked/invalid-transform/speedhack, returned no matches. This is not proof that movement is correct; ordinary follow steering is not exposed in these logs. Local chat logs contain login lines only; UI log contains load statistics.

Screenshots in `screenshots/`: `20261013-follow-16460.png`, `20261013-follow-30604.png`, and each `-check2.png` version, with `_small.png` companions.

## Settings and primary references

- `SWG-client/user.cfg`: windowed 1600 × 900, multiple instances enabled, cursor unconstrained, hardware cursor enabled, pointer-mode mouse-camera disabled. `fullscreenRefreshRate=60` is present; it does **not** prove a 60 FPS limit in windowed play. Actual FPS is unmeasured.
- Both character profiles contain the same `turnStrafesDuringMouseModeToggle` boolean record. Captured [name removed]'s Options → Controls and Keymap page: **“Turn Strafes When Mouselook Enabled (EQ Style)” is checked**; Mouse Pointer Mode Default and Chase Camera Mode are also checked; selected standard keymap is MMORPG (EQ style). Autorun Toggle visibly binds NUMLOCK, Q and MOUSEBUTTON4. Screenshot: `screenshots/20261013-follow-alt-controls.png` (and `_small`).
- Asked owner to uncheck only the turn-strafes option, apply, close menus and repeat `/follow` toward stationary visible [name removed] on open ground. **Owner reported no improvement: still runs away or gets stuck. This comparison failed to establish a fix.** No agent input or direct profile/config edits.
- The [archived official command list](https://swgreckoning.org/archive/data/20070128130746/manual_detail_120.html) says `/follow` follows the current target and `/stopfollow` stops following. Owner was advised to stop the runaway attempt before testing.
- The [official controls manual](https://swgreckoning.org/archive/data/20070128130746/manual_detail_004.html) documents configurable bindings; no default autorun key was assumed. The [official setup manual](https://swgreckoning.org/archive/data/20070128130746/manual_detail_001.html) distinguishes refresh and VSync.
- A delegated public-primary-source check found **no verified source linking this symptom to high FPS, strafing/chase controls or controller drift**. A 60 FPS or control-mode comparison would be a diagnostic, not an established fix.

## Capture-tool setup and scope

Universal Modder 0.2.0's screenshot dependencies were absent. Told the owner what setup downloads, then ran its setup: copied WinDrive/ProcLoopback scripts and installed BtbN's GPL FFmpeg build under the owner's LocalAppData. Package SHA-256 was verified against the published checksums: `6048bd162997ad0f1ebfd6a249ec483b0488432cb0b049c07f00916bcbc66008`. `gfxcapture` and NVENC setup succeeded. [Build source](https://github.com/BtbN/FFmpeg-Builds).

**No keyboard/mouse injection, game restart, profile/config edit, Kael connection, `/opt/swg` write, server restart/deployment or paid generation occurred.** Claude's lock and bot work remain unchanged.

Input-helper limitation found during source inspection: shipped WinDrive selects the first process by name and checks foreground by process name. Both clients share `SWGEmu`, so it is unsuitable for choosing one of these clients reliably without a PID/HWND-aware change. Captures used exact handles; no ambiguous input was sent.

## Next

The turn-strafes comparison did not fix the symptom. Later shared handoff records Claude's development-only `/leash` assist and its C4c review findings; it is not approved for live promotion. Further real-client testing waits for an authorized running galaxy and the owner at the PC. Restore the changed turn-strafes preference if the owner wants the original controls; no successful control-setting fix was established here. Confirm approach/stop and short follow movement before declaring the issue resolved.
