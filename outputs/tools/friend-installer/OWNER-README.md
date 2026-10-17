# Friends installer: the owner's guide

`SWG-Friends-Setup-<version>.exe` lets 2-3 trusted friends play on the **test galaxy** over Tailscale (a free
private network), with no port forwarding. It carries only our files (the client patch kit, our scripts and the
server address). No SOE client files, no MTG archives, no Tailscale key, no Tailscale installer: the friend's PC
downloads Tailscale from `pkgs.tailscale.com` and checks it is signed by Tailscale Inc. before installing it.

| File | What it is |
| --- | --- |
| `friend-installer.iss` | Inno Setup script: pages, uninstaller, shortcut |
| `friend-setup.ps1` | the worker the installer runs (checks, Tailscale, patch, login, probe, uninstall); `-DryRun` |
| `build.ps1` | checks the kit and settings, writes `build\`, compiles; `-DryRun` skips the compile |
| `owner-setup.ps1` | your side: Tailscale on this PC, firewall rules, the ACL, `owner-settings.json`; `-DryRun` |
| `test-friend-setup.ps1` | offline test on a dummy client (`-ProbeAddress 192.168.1.210` also pings the login port) |
| `owner-settings.example.json` | copy to `owner-settings.json` (gitignored) |
| `FRIENDS-README.md` | the friends' one page (also installed as `README.txt`) |

## Your one-time steps

1. **Tailscale on this PC.** PowerShell as administrator, in this folder:
   `.\owner-setup.ps1 -InstallTailscale`, then sign in with your own account in the browser.
   In the admin console (https://login.tailscale.com/admin/machines) open this PC and **disable key expiry**,
   otherwise friends lose the server when this PC's key expires.
2. **Firewall.** `.\owner-setup.ps1 -Firewall` (administrator). It allows UDP 46453, 46462, 46463 in, only from
   Tailscale addresses (100.64.0.0/10), in both the WSL Hyper-V firewall and Windows Defender.
   `-RemoveFirewall` takes them out.
3. **ACL.** `.\owner-setup.ps1 -ShowAcl` prints a policy with this PC's address filled in. Paste it at
   https://login.tailscale.com/admin/acls (save a copy of the old policy first). Friends tagged `tag:swg-friend`
   reach only the test galaxy's login (46453), ping (46462) and zone (46463) ports, UDP. Not Ollama (11434), the
   live map (8765), ComfyUI (8188), ORB (46419), status (46455), MariaDB or SSH; the policy's `tests` block fails
   the save if any of those opens. Your own devices keep reaching each other.
4. **Settings.** `.\owner-setup.ps1 -WriteSettings` writes `owner-settings.json` with this PC's tailnet IPv4.
   Open it and set `MtgHelpUrl` to the page you want friends sent to for the MTG archives (check MTG's terms).
   Using the IP rather than the MagicDNS name keeps the tailnet name out of the installer.
5. **Inno Setup 6** (free, https://jrsoftware.org/isdl.php), then `.\build.ps1`. The result is
   `build\out\SWG-Friends-Setup-<version>.exe` (gitignored). Before sending it, check the server's
   `local_planets.tre` matches the kit (`client-patch-for-friends.md`, check-server).
6. **The galaxy address** (the lock holder does this, see below). Without it a friend logs in and then hangs at
   the galaxy list or the zone connection.
7. **Run `.\owner-setup.ps1`** (no switches). Every line should say ok.

## Each friend

1. **An invite key**: https://login.tailscale.com/admin/settings/keys > Generate auth key:
   **Reusable off** (one-time), **Ephemeral off** (the friend keeps the device), **Pre-approved on** (if device
   approval is on), **Tags: `tag:swg-friend`**, expiry 1-7 days. Send the key in a private message, separately
   from the installer, and don't paste it anywhere else. A tagged device has no key expiry of its own.
2. Send them `SWG-Friends-Setup-<version>.exe` and tell them where to get the MTG archives.
3. Their account: they log in once with a username they choose (AutoReg makes it at level 0). Staff rights, if
   any, follow `Documentation-support/remote-access-and-second-owner.md` section 5.2.
4. **Removing a friend**: delete their device in the Tailscale admin console. The installer cannot reach anything
   after that.

## For the lock holder: the galaxy address (not applied)

The login server tells every client which address to reach the zone at, from the `galaxy` row. A friend on
Tailscale can only reach `100.x.y.z`, so the test galaxy's row must say this PC's tailnet IPv4:

```powershell
wsl -d Debian -u root --exec mariadb swgemu_test --execute "UPDATE galaxy SET address='<tailnet IPv4>' WHERE galaxy_id=2;"
```

- It takes effect at the next login, no restart. **`tools/test_galaxy.py` puts the LAN address back at every
  start** (`hostname -I`), so it has to be redone after each start, or test_galaxy.py gets a private override
  file (for example `/opt/swg/agent/galaxy-address`, outside git) that a reviewed change reads.
- **Everyone else is then told to use the tailnet address too**: the owner's client and the bots (core3client
  follows the row). Windows reaches its own tailnet address locally while Tailscale runs; whether WSL's bots do
  under mirrored networking is untested (`owner-setup.ps1` shows whether WSL lists the address). Test before a
  friend's window: one bot login and one owner login after the UPDATE. If bots fail, put `192.168.1.210` back
  between windows.
- If Tailscale stops on this PC, nobody gets past the galaxy list until it is back or the row is changed back.
- Live (44453/44463) stays LAN-only. Opening it means new firewall ports, a new ACL line and the owner's OK.

## What was tested (17 Oct)

- `test-friend-setup.ps1`: all 14 checks pass on a dummy client with the real kit scripts: wrong folder, missing
  and wrong-size MTG archive, dry runs change nothing, the key file is deleted and the key never printed, patch,
  re-patch, uninstall restoring the friend's own files, and a real probe of the test login port
  (192.168.1.210:46453 answered).
- `build.ps1 -DryRun` and `owner-setup.ps1 -DryRun -ShowAcl -Firewall` run clean.
- Inno Setup 6.7.3 installed (owner's OK, 17 Oct; winget, per-user in `%LOCALAPPDATA%\Programs\Inno Setup 6`). `build.ps1`
  compiled a 6.5 MB `SWG-Friends-Setup-2026.10.16.1.exe` with a **placeholder address (100.100.100.100)**: don't
  send that one. Rebuild after step 4.
- **Not tested**: the Tailscale download, install and `tailscale up` (needs a real key), the firewall rules, the
  ACL in the admin console, a friend logging in over Tailscale, the uninstaller's Tailscale choices, and the
  compiled installer's pages (running it needs administrator rights and would install Tailscale, so it has not been
  run on this PC).
