# Making the game run better: client and server options (Claude, 16 Oct 2026, 7:40 PM)

Owner's questions:
- "research what we could possibly do to make SWG better optimized";
- "server optimization";
- "can we offload a lot of the client onto the GPU";
- "is there a mod";
- "could we rebuild our own optimized exe".

## What actually went wrong today

- Windows CPU sat at **97%**, with the WSL load average at 9.7 of the 5600X's 12 threads.
- The load comes from run 13's 1,700 active bots, running on a **Debug** build of Core3.
- The SWG client does most of its work on one main thread. When that thread is starved, radials, windows, chat and movement stall.
- The server itself answered in 0.05-0.25 s throughout (latency probe), so the fix is mostly on the server side first.

## Server (biggest wins first)

| # | Change | Evidence | Cost and risk |
|---|---|---|---|
| S1 | **Run the test galaxy on an optimised build** (`RelWithDebInfo`: `-O2` and symbols, so gdb thread dumps still work) | The test galaxy's `core3` is Debug (`CMAKE_BUILD_TYPE=Debug`, 347 MB); live's is Release (60 MB). Unoptimised C++ commonly costs several times the CPU for the same work. | A second build directory beside `build/dev`, about an hour of gentle build, then a test-galaxy restart. No live change. Measure before and after with the same bot count. |
| S2 | **Cut active bots while a real client plays** | BotPop steps alone use about 3 CPU-seconds per second at 1,700 bots. Throttled mode keeps only bots near real players active, but switching needs a full despawn. | `botpop despawn <n>` now; for the next run, start throttled while the owner plays and switch to "all" overnight. |
| S3 | **Reserve cores for Windows and the client**: `.wslconfig` `processors=8` | WSL can currently take all 12 threads. | Owner's decision: a user config file and a WSL restart (everything in WSL restarts). |
| S4 | **Profile the bot step** (gdb sampling, no install) and fix hot spots | 2.9 CPU-s/s of bot steps is a target in itself. | Engineering time; after S1, since Debug profiles mislead. |
| S5 | Thread settings: `ZoneProcessingThreads` is 4 on test and live (stock default 10) | Unmeasured. | Try after S1, one change at a time. |

Already fine: both builds link jemalloc (`libjemalloc.so.2`); `-march=native` is on by default.

## Client

The client is SWGEmu's pre-CU `SWGEmu.exe`: 32-bit, Direct3D 9 through `gl07_r.dll` (`rasterMajor=7`), shader capability 2.0 per its crash report.

| # | Change | What it does | Cost and risk |
|---|---|---|---|
| C1 | **Process priority** | The client's main thread gets a core first. The client has its own `processPriority` setting (found in the exe's foundation settings), or it can be set per launch in Task Manager. | Free and reversible. |
| C2 | **GPU skinning for more characters**: `[ClientSkeletalAnimation]` `lodManagerEnable`, `lodManagerHardSkinningCharacterCount`, `lodManagerEveryOtherFrameSkinningCharacterCount`, `lodManagerFirstLodCount`, `hardSkinningScreenFraction`, `noSkinningScreenFraction`, `skipActionGenerationFrameCount` | The client skins characters on the CPU (`SoftwareBlendSkeletalShaderPrimitive`) unless the LOD manager hard-skins them. Raising hard-skinning counts moves crowds onto the 5070. | `user.cfg` lines; test one at a time in Mos Eisley with bots around. Names come from the exe; defaults and exact sections still need testing. |
| C3 | **Network thread**: `[SharedNetwork]` `useNetworkThread`, `networkThreadPriority`, `networkThreadSleepTimeMs` | If off by default, networking shares the main thread; on, it uses another core. | `user.cfg`; test. |
| C4 | **Cheaper effects**: `[ClientObject]` shadows (`renderShadows`, `skeletalShadows`, `shadowDetailLevel`); `[ClientParticle]` `maxMeshParticles`; `[ClientTerrain]` flora distances; camera zoom | Volume shadows and flora cost CPU. | `user.cfg`; visible quality trade-off. |
| C5 | **Large address aware** flag on `SWGEmu.exe` | The exe is not LAA, so it is capped at 2 GB (crash report: `Ram: 2047mb`). The flag allows 4 GB on 64-bit Windows: fewer out-of-memory crashes, more asset caching. | One header bit; keep a backup. Owner's OK (it changes the owner's program). |
| C6 | **DXVK** (`d3d9.dll`, 32-bit, in the client folder) | Translates Direct3D 9 to Vulkan with multi-threaded submission. It is the standard modern fix for CPU-bound D3D9 games and spreads driver work over more cores. The client loads `d3d9.dll` from its own folder first. | A download (owner's OK); remove the DLL to undo. Test for visual bugs. |
| C7 | `debugExamine=0` in `user.cfg` | Stops debug examine spam (currently 1). | Free. |

Not available in this client: the `[ClientLimits] SetFramesPerSecond` frame cap a community forum describes is not in our exe (checked); it belongs to another client build.

### Rebuilding the client

- **Not viable.** The client is closed source; the only full source is SOE's leaked 2014 code, which we must not use.
- Reconstructing a game client from the binary is not a realistic project.
- What is realistic: data and config changes (C1-C4, C7), wrappers (C6), and small patches to our own copy (C5).
- Universal Modder's "native hooks" route (a proxy DLL) could add targeted fixes later if a specific hot spot is found.

## Suggested order

1. S1, the optimised test build. Claude can do this with no owner input.
2. S2 for play sessions.
3. C1, C7 and the C2/C3 experiments in `user.cfg`.
4. Then the owner's decisions: C5 (exe flag), C6 (DXVK download), S3 (`.wslconfig`).

## Sources

- Local checks (16 Oct):
  - the PE header of `SWGEmu.exe`;
  - the config key strings in `SWGEmu.exe`;
  - the client folder's DLLs;
  - the `CMakeCache.txt` of both builds;
  - `ldd` of both `core3` binaries;
  - Windows and WSL load figures.
- [user.cfg tweaks (Sentinels Republic forum)](https://forum.swgsremu.com/viewtopic.php?t=66): frame cap and camera zoom notes; their frame-cap key is not in our client.
- [DXVK 1.6: D3D9 performance work (Phoronix)](https://www.phoronix.com/news/DXVK-1.6-Released) and [DXVK 1.10.2 game fixes (Phoronix)](https://www.phoronix.com/news/DXVK-1.10.2-Released): DXVK's D3D9 path.
- [4GB Patch (TechPowerUp forum)](https://techpowerup.com/forums/goto/post?id=3484635): large address aware for 32-bit programs on 64-bit Windows.

## Installed on the owner's client (16 Oct 2026, 7:10 PM, owner's OK)

- C5: `SWGEmu.exe` is large address aware. The original is `SWGEmu.exe.bak`.
- C6: DXVK 3.1.1 from the official release (`dxvk-3.1.1.tar.gz`, sha256 `40565b4a...` matched GitHub's digest).
  - Its 32-bit `d3d9.dll` is in `SWG-client/`.
  - `dxvk.conf` caps the frame rate at 60 (`d3d9.maxFrameRate = 60`).
  - Undo: delete `d3d9.dll`.
- C2/C3/C7 in `user.cfg`:
  - `debugExamine=0`;
  - `[SharedNetwork] useNetworkThread=true`;
  - `[ClientSkeletalAnimation] lodManagerEnable=true`, `lodManagerHardSkinningCharacterCount=100`.
  - Undo: restore `user.cfg.bak`.
- C1: the owner's own launchers, `Play SWG Test Galaxy.cmd` and `Play SWG.cmd`, now start the client at Above normal priority.
  - A desktop shortcut, "SWG Test Galaxy", opens the test-galaxy one.
  - 7:25 PM fix: the first launcher (`SWG-client/Start SWG (above normal).cmd`, now removed) started the client
    directly, so it went to the stopped live login (44453) without the test archive. The owner could not log in.
- The client archive is back on `6ff21312`, matching the server.
- S1: the optimised `RelWithDebInfo` test build (`dev_build.py --release`) is building. The test galaxy picks it up at its next `--dev-server` start.
- Not yet tested in game.

## Result: the optimised build at 1,700 bots (16 Oct 2026, 7:58 PM)

Run 14: the `RelWithDebInfo` core3 (dev `724809fa`, which also has the walls fix), with the same population as run 13 (1,500 multiclass + 200 Ossus explorers, "all" mode). The owner's client was running in both measurements.

| At 1,700 bots | Debug (run 13, 7:15 PM) | Optimised (run 14, 7:58 PM) |
|---|---|---|
| core3 CPU | 7.07 cores | **2.38 cores** |
| WSL load average | 18.6 (a build was also running) / 9.7 earlier | **1.96** |
| Windows CPU, whole PC | 97% (earlier, client running) | **36%** (client running) |
| BotPop pass | 8 ms | 3 ms |
| Bot steps | ~3 CPU-seconds per second | 0.76 CPU-seconds per second, including 1,158 navmesh routes a minute (0 deferred) |
| core3 memory | 8.6 GB | 5.2 GB |

- So S1 alone took about two-thirds off the server's CPU.
  - The walls fix's route planning fits easily: 1,158 routes a minute is about 19 a second, against a cap of 200 a pass.
  - The memory figures aren't strictly comparable: run 13 had been running for 4 hours, run 14 for 3 minutes.
- **The priority launcher doesn't take effect.** The client showed `Normal` priority even when started from `Play SWG Test Galaxy.cmd` with `/abovenormal`.
  - Likely cause: the client asks for administrator rights, and the elevated process doesn't inherit the launcher's priority class.
  - With the PC at 36%, this matters less now.
  - The fix would be a per-program setting in Windows, which is the owner's change to make, or the client's own `processPriority` key (untested).
- Next: the owner's experience at full load, in their own words. Then about 200 bots while the owner plays. Then decide S3 (`.wslconfig`), which this result makes less urgent.
