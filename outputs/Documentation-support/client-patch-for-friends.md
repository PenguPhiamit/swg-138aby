# Playing on our server: the client patch

This patch adds our server's content to your SWGEmu client. It is one file, `local_planets.tre`, plus one line of
client config that tells the game to load it. The kit installs both, checks them, and can take them out again.
You don't need admin rights.

## What changes in game

- **New planets** on the travel screen and the galaxy map: **Hoth**, **Ossus** and **Nal Hutta**.
- **Hutts as a playable species** at character creation, with their own names, stats and starting look.
- **The A1 Deluxe Floater**, a repulsor sled Master Artisans can craft, and a riding pose that fits a Hutt.
- Nothing else in your client changes. Your other characters, settings and keybinds stay as they are.

Without the patch you can still log in, but the new planets are missing from your travel screen. A character
standing on one of them will very likely crash your client at login (expected, not tested).

## Before you start

1. **A working SWGEmu client** that you can already log in with (the folder that holds `SWGEmu.exe`).
2. **The MTG archives** (the files named `mtg_patch_001_appearance_01.tre` up to `mtg_patch_023.tre`, plus
   `mtg_planets.tre`) in that same folder. The new planets and the Hutt are built on them. The kit checks they are
   there and stops if any is missing. The kit does not include them; the server owner will tell you where to get
   them.
3. **The kit**, a zip named like `local_planets-2026.10.16.1.zip`. The server owner sends it to you directly.
   Nothing is posted publicly.
4. **Close the game.** The kit won't run while the client is open.

## Install

1. Unzip the kit anywhere, for example to your Desktop. Keep the files together.
2. Double-click **`Install.cmd`**. When it asks, paste or drag in your client folder (for example `C:\SWGEmu`) and
   press Enter. You can also drag the client folder onto `Install.cmd`.
3. Wait for `Installed local_planets version ...`. If you see `STOPPED:` instead, read the reason. Nothing has been
   changed. The common ones:
   - *does not look like a SWGEmu client folder*: you picked the wrong folder. Pick the one with `SWGEmu.exe` in it.
   - *these MTG archives must be in the client folder first*: copy in the files it lists, then run Install again.
   - *a program in the client folder is running*: close the game (and its launcher), then try again.
   - *the kit is damaged*: the download got cut short. Ask for the zip again.
4. Start the game the way you normally do.

What it changes in your client folder:

- It adds or replaces `local_planets.tre`.
- It writes `local_planets.cfg`, which holds the line that loads the archive (and the MTG archives, if your client
  wasn't loading them yet).
- It adds one line, `.include "local_planets.cfg"`, at the end of `swgemu.cfg`.
- It makes a `local_planets-patch` folder holding backups of anything it replaced, plus a note of which version is
  installed.

**Checking what you have.** In PowerShell, from the kit folder, run
`.\Install-ClientPatch.ps1 -ClientDir C:\SWGEmu -Status`. It prints the installed version and whether the file is
still intact. The server owner may ask you for that line.

## A new version

When the server owner sends a new kit, just install it the same way. It replaces the old archive and keeps a copy
in `local_planets-patch\backup\<old version>`. The kit won't install an older version over a newer one unless the
owner asks you to roll back (`-AllowDowngrade`).

Your client must have **the same version as the server**. If the game crashes when you travel or at login after a
server update, you probably still have the old patch.

## Remove it

1. Close the game.
2. Double-click **`Uninstall.cmd`** and give it the same client folder.
3. It takes the line out of `swgemu.cfg`, deletes the kit's `local_planets.tre` and `local_planets.cfg`, and puts
   back any file of yours they replaced. If `local_planets.tre` has been changed since the install, it is moved to
   the backup folder, not deleted.
4. The `local_planets-patch` folder stays, in case you want the backups. Delete it by hand when you're done.

After removing it, don't log in a character that is on Hoth, Ossus or Nal Hutta.

## If the SWGEmu launcher "repairs" your files

The SWGEmu launcher may reset `swgemu.cfg` and drop our line. If the new planets are gone from the travel screen,
run Install again. It puts the line back and changes nothing else.

---

## For the server owner: building and matching versions

**Build a kit** from the exact archive the server loads (today the Nal Hutta + floater archive, `503401b4…`):

```bash
C:/Users/Pengw/miniconda3/python.exe -I tools/client_patch/client_patch.py build --archive ../work/c59-hutt-walk/base-503401b4.tre --expect-sha 503401b4 --version 2026.10.16.1 --notes ../work/client-patch/notes-2026.10.16.1.txt
```

It writes `../work/client-patch/<version>/` and `local_planets-<version>.zip`. It reads the MTG requirement list
(name, priority, size, sha256) from your own client's config chain. It never edits the archive. Then
`client_patch.py verify <kit folder>` checks a kit's files against its manifest.

**Version numbers** are `year.month.day.build` (for example `2026.10.16.1`; the next build that day is `.2`). The
installer compares them as numbers, so a new kit always replaces an older one, and an older one needs
`-AllowDowngrade`. The archive keeps the name `local_planets.tre`, at priority 49, the highest the client loads.
One slot means old and new versions can never both be loaded.

**Keeping server and client matched.** The server's `/opt/swg/tre/local_planets.tre` must be byte-identical to the
archive in the kit. Before you send a kit, and after every server archive change:

```bash
wsl -d Debian -u swgemu -- sha256sum /opt/swg/tre/local_planets.tre
```

```bash
C:/Users/Pengw/miniconda3/python.exe -I tools/client_patch/client_patch.py check-server ../work/client-patch/2026.10.16.1 --server-sha "<the line printed above>"
```

`MATCH` means the kit is right for the server. `MISMATCH` means build a new version from the server's archive (or
put the server back on the kit's archive). The order for an update:

1. Build the new kit from the archive you are about to install.
2. Install that archive on the server at the next restart, and run check-server.
3. Send the kit to friends with the date it goes live.

A friend's `-Status` line shows their version and sha256, so a crash report can be matched to a version.

**Your own client.** The test launcher (`Play SWG Test Galaxy.cmd`) already adds `searchTree_00_49=local_planets.tre`
for each session. Installing the kit on your own client as well loads the same file twice at priority 49, which
does no harm. Two things remain your call: how friends get the MTG archives (check MTG's terms before sharing them),
and how you send the kit. The tools only build files on this PC.

Tests (offline; dummy client folders in a temp folder, the real PowerShell scripts):
`C:/Users/Pengw/miniconda3/python.exe -I tools/client_patch/test_client_patch.py`
