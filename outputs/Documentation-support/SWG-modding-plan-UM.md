# Star Wars Galaxies (pre-CU client) modding plan: Universal Modder recon

15 Oct 2026, Claude, with Universal Modder 0.2.0 (`game-recon` skill, `um scan`, `um kb`, `um publish`, `um win`). The owner asked: "lets use UM to look at SWG and tell us what it can".

- **Install:** `outputs/SWG-client` (standalone, no store id), 7.5 GB, 77 TRE archives. `SWGEmu.exe` and `SWGEmu_Setup.exe`, both 32-bit native (x86, not .NET).
- **Engine:** SOE's own engine. `um scan` doesn't recognise it ("unknown native engine", 10%). The real map of its formats is ours: `Documentation-support/swg-format-inventory.md` (IFF chunks inside TRE archives; msh, mgn, sht, dds, trn, ws, pob, flr, apt, lod, stf, datatables).
- **Anti-cheat / online:** none found, and the official servers closed in 2011. We play on our own private server (Core3), and client mods only change our own clients. Hooks or modified clients never go near public SWGEmu servers.
- **Loaders:** `um scan` reports an "ASI loader", but that is a false positive. The file is `miles/mssmp3.asi`, the Miles Sound System's MP3 codec. There is no mod loader. The ReShade/DLSS feeder is installed by the owner (`Client-graphics/`).
- **Saves:** none on the PC (characters live on the server). **Config:** `swgemu.cfg` (archive list: `swgemu_live.cfg`), `user.cfg`, `options.cfg`, `swgemu_login.cfg`, `swgemu_machineoptions.iff`, `profiles/<account>/` (UI layout, keymaps). **Logs:** `ui.log`, and crash reports `SWGEmu.exe-stage.*.txt` and `.mdmp` next to the exe (two so far: 14 Oct 09:31 and 15 Oct 12:50).
- **Community route:** data mods through TRE archives. The client reads archives in priority order, so our own `local_planets.tre` (priority 49) overrides or adds files without touching stock ones. Public tools: SIE and TRE Explorer (Mod The Galaxy), the MIT Blender add-on io_scene_swg_msh (Blender 3.6 LTS; 4.x breaks it). Our own tools already pack, merge and check archives: `tools/hoth/`, `MTG-merges/`, `Fable-planet-test/tools/trn_iff.py`.
- **Knowledge base:** `um kb search` has no SWG notes (82 games; the nearest are Battlefront II 2005 and Starfield).

## Route, in Universal Modder's order

1. **Loader API:** none exists.
2. **Data and asset mods: our route, already working.** Hoth, Ossus, Chiss, the MTG merges, the BARC fix and the first outside-art prop (`Fable-asset-pipeline/how-to-view-first-ruin.md`) all ship this way. They need no code in the client.
3. **Managed patching:** doesn't apply (native code).
4. **Native hooks:** a proxy DLL with function hooks (UM's `native.md` playbook: MinHook/SafetyHook, Ghidra or IDA, x64dbg). Only for what data can't do, such as client-side `/follow` pathing (F16) or UI behaviour. It means reverse-engineering our own client binary for compatibility with our own server, never leaked source (AGENTS.md ethics check). It is a large job; nothing is planned yet.
5. **Reimplementation:** no.

## What each Universal Modder tool can do for this project

| UM tool | For SWG | State |
|---|---|---|
| `um scan` / `game-recon` | fingerprint and route (this note) | done |
| `reverse-engineering` skill | prove each format with a round trip (parse, write back, byte-compare): next are `.trn` (no public editor), `.pob`/`.flr` (interiors), `.mgn`/`.skt`/`.ans` (wearables and creatures), particles (the Darksaber trail) | our tools already follow this method for TRE, IFF, datatables and STF |
| `asset-pipeline`, `render3d`, `comfy`, `fal-assets` | new art into SWG: 2D first (item icons, loading screens, the Ossus and Hoth planet-map art, the galaxy-map globe: DDS only), then 3D props (Blender 3.6 + the add-on, or fal image-to-3D, paid per batch with the owner's OK) | first static prop converted (Quaternius wall, CC0); Blender not installed (owner question 7); fal needs the owner's key |
| `game-automation` (`um win shot / record / drive / ps / launch`) | real-client checks the bots can't make: screenshots of the SWG window (does the ruin draw, are the Hoth map markers right), short recordings, scripted input | ready; controlling the mouse or keyboard needs the owner's OK each time (C2, C6, F09) |
| `showcase-video` (`um video`, ffmpeg 4.3.1) | a Hoth or Ossus trailer for the friends' Discord | ready |
| `backup` (`um backup`) | snapshot `profiles/` and the `.cfg` files before swapping archives or graphics mods | ready |
| `publish-mod` (`um publish check`) | lint the friends' client patch before sharing | runs (staged Ossus patch: 55 files, 0 failures, 1 warning for a missing README), **but it doesn't recognise SWG's retail files**: the patch holds edited copies of stock string tables and datatables, and it didn't flag them. Our own rule decides what a patch may hold, and how friends get it, before anything is shared. |
| `port-a-mod` | porting MTG, Bellum and Flurry content with an adaptation table | already used for Hoth (C12) |
| `share-field-notes` / `um kb` | the first SWG field note: TRE priority, IFF layout, the MTG shadowing trap, the object CRC table | candidate; publishing it opens a pull request on GitHub, so it needs the owner's OK and the usual names check |
| `mashup-mods` | KOTOR content into SWG | researched (`Documentation-support/KOTOR-to-SWG-and-open-assets-feasibility.md`), rights open |

## Lab plan

`um backup` of `SWG-client/profiles` and the `.cfg` files before each archive swap. Test sessions use `Play SWG Test Galaxy.cmd` (test archive, login on 46453). `um win` runs windowed, with the owner's OK.

## Unknowns to resolve first

- Blender 3.6 LTS install (owner question 7). It unlocks 3D props and wearables.
- How friends receive `local_planets.tre`, and what it may contain (the publish check can't decide this).
- `um win shot` works on the SWG client (15 Oct 14:46, with the owner's OK, client running as administrator): 1600x900 frames in about 2 s, capturing only the SWG window. It needs the BtbN ffmpeg that `um win setup --force` downloads (191 MB, SHA-256 checked, into `AppData\Local\universal-modder\ffmpeg`).
  - UM bug: plain `um win setup` accepts any ffmpeg on the PATH whose reply contains the word gfxcapture, including the "Unknown filter 'gfxcapture'" error from our ffmpeg 4.3.1.
  - Still untested: `um win drive` input (needs the owner's OK each time) and recording.
- The two client crash reports (14 Oct 09:31, 15 Oct 12:50): what caused them.
