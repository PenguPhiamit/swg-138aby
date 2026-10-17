# Playing on the owner's SWG server

The owner runs a private Star Wars Galaxies server (SWGEmu, pre-CU) with new planets (Hoth, Ossus, Nal Hutta)
and Hutts as a playable species. This installer gets your PC ready in a few clicks.

## What you need first

1. **SWGEmu installed and working.** You can already start it and see the login screen. Get it from
   https://www.swgemu.com/ if you don't have it. The folder with `SWGEmu.exe` in it is your "client folder".
2. **The Mod The Galaxy (MTG) archives** (`mtg_patch_001` ... `mtg_patch_023` and `mtg_planets.tre`) in that same
   folder. They are not in this installer; the owner tells you where to get them. Setup checks for them and stops
   with a list if any is missing.
3. **Your invite key**: a line starting with `tskey-` that the owner sends you. It works once.
4. **`SWG-Friends-Setup-<version>.exe`** from the owner.

## Install

1. Close the game.
2. Run `SWG-Friends-Setup-....exe` and say Yes when Windows asks for permission.
3. **Your SWGEmu client**: Setup suggests a folder. If it is wrong, click Browse and pick the folder with
   `SWGEmu.exe`. On Next it checks the MTG archives.
4. **Your invite key**: paste the key. Setup installs **Tailscale** (a free, private network made by Tailscale Inc.;
   Setup downloads it from Tailscale and checks it is really theirs) and joins the owner's network with your key.
   The key is used once and not saved.
5. Setup adds the server's planets to your client, points the client at the server, puts **Play SWG (owner's
   server)** on your desktop, and tests the connection.

## Play

- Double-click **Play SWG (owner's server)**. It also fixes things if the SWGEmu launcher reset your settings.
- **Tailscale must be running**: its icon sits by the clock. Through it your PC can reach the game server and
  nothing else on the owner's network, and the owner's network cannot reach your PC.
- First login: type any username and password you like. The server makes your account then. Don't reuse a
  password from anywhere else. Tell the owner your username (not your password).
- If it says the server is not answering, the owner's server is probably off. Message the owner.

## Remove it

Settings > Apps > **SWG Friends Galaxy** > Uninstall. It puts your client back the way it was (your own login
file and config) and asks what to do with Tailscale: keep it, log out of the owner's network, or remove it.
Don't log in on another server with a character standing on Hoth, Ossus or Nal Hutta.

## Good to know

- If you already use Tailscale for something else, Setup adds the owner's network as a second account and
  switches to it. Switch back from the Tailscale icon.
- Your SWGEmu login goes back to the normal SWGEmu servers only when you uninstall.
- The installer contains only the owner's own files: no game files, no MTG files, no keys.
