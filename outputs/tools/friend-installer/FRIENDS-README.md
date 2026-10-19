# Playing on the owner's SWG server

The owner runs a private Star Wars Galaxies server (SWGEmu, pre-CU) with new planets (Hoth, Ossus, Nal Hutta)
and Hutts as a playable species. This installer gets your PC ready in a few clicks.

## What you need first

1. **SWGEmu installed and working.** You can already start it and see the login screen. Get it from
   https://www.swgemu.com/ if you don't have it. The folder with `SWGEmu.exe` in it is your "client folder".
2. **Your invite key**: a line starting with `tskey-` that the owner sends you. It works once.
3. **`SWG-Friends-Setup-<version>.exe`** from the owner.
4. **Room for the Mod The Galaxy (MTG) archives** (`mtg_patch_001` ... `mtg_patch_023` and `mtg_planets.tre`), which
   the server is built on. Setup checks your client folder and downloads any you are missing from Miniverse:
   up to 4.7 GB, plus the same again free on your C: drive while it downloads. Tell the owner before you start, so
   their PC is on and sharing the files.

## Install

1. Close the game.
2. Run `SWG-Friends-Setup-....exe` and say Yes when Windows asks for permission.
3. **Your SWGEmu client**: Setup suggests a folder. If it is wrong, click Browse and pick the folder with
   `SWGEmu.exe`. On Next it checks the MTG archives and tells you how many it will download.
4. **Your invite key**: paste the key. On Install, Setup installs **Tailscale** (a free, private network made by
   Tailscale Inc.; Setup downloads it from Tailscale and checks it is really theirs) and joins the owner's network
   with your key. The key is used once and not saved.
5. **The MTG download**, if you need it: a progress bar per file. It can take an hour or two, depending on the
   owner's upload speed. Every file is checked against the server's own copy before it goes into your client. If
   you already had a different version of one, yours is kept in `local_planets-patch\backup` in your client folder.
6. Setup adds the server's planets to your client, points the client at the server, puts **SWG Fractured Galaxy** (the
   launcher) on your desktop, and tests the connection.

## Play

- Double-click **SWG Fractured Galaxy**. The launcher shows whether the server is up, downloads the owner's latest
  update if there is one (Play stays greyed out until it's done), fixes things if the SWGEmu launcher reset your
  settings, and starts the game. Windows may warn the first time ("More info" > "Run anyway"): it isn't signed.
- **Tailscale must be running**: its icon sits by the clock. Through it your PC can reach the game server and
  nothing else on the owner's network, and the owner's network cannot reach your PC.
- First login: type any username and password you like. The server makes your account then. Don't reuse a
  password from anywhere else. Tell the owner your username (not your password).
- If it says the server is not answering, the owner's server is probably off. Message the owner.
- **The graphics add-on.** The launcher also puts in DXVK (it runs the game's Direct3D 9 on Vulkan, capped at
  60 fps) with the owner's small graphics hook in front of it: the light whip bends like a rope, and ghostfire
  blades get a heat haze. In game, Ctrl+Shift+B switches the bend on and off, Ctrl+Shift+M the haze. If the game
  won't start or looks wrong after it arrives, delete `d3d9.dll` in the game folder (the launcher then leaves the
  add-on off) and tell the owner. It's left out on a PC without Vulkan, or if your game folder already has a
  `d3d9.dll` of its own.

## Remove it

Settings > Apps > **SWG Friends Galaxy** > Uninstall. It puts your client back the way it was (your own login
file and config, the MTG archives it downloaded removed and your own versions back, the graphics add-on taken
out) and asks what to do with
Tailscale: keep it, log out of the owner's network, or remove it.
Don't log in on another server with a character standing on Hoth, Ossus or Nal Hutta.

## Good to know

- If you already use Tailscale for something else, Setup adds the owner's network as a second account and
  switches to it. Switch back from the Tailscale icon.
- Your SWGEmu login goes back to the normal SWGEmu servers only when you uninstall.
- The installer contains only the owner's own files: no game files, no MTG files, no keys.
- You can run more than one game window, and the mouse can leave the game window: the launcher sets that in
  `fractured-galaxy.cfg` in the game folder (the uninstaller removes it).

## Credits

The MTG archives are the work of Mod the Galaxy and its community (https://modthegalaxy.com), not the owner's.
`MTG-CREDITS.txt` next to this file lists who made them. Nal Hutta in those archives is the Levarrishawk/Darklight
public version.

DXVK (https://github.com/doitsujin/dxvk) is the work of the DXVK project and its contributors, under the zlib/libpng
licence; the add-on passes on its official 3.1.1 release unchanged.
