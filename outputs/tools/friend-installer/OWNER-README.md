# Friends installer: the owner's guide

`SWG-Friends-Setup-<version>.exe` lets 2-3 trusted friends play on the **test galaxy** over Tailscale (a free
private network), with no port forwarding. It carries only our files (the client patch kit, our scripts, the
server address and MTG-CREDITS.txt). No SOE client files, no Tailscale key, no Tailscale installer: the friend's
PC downloads Tailscale from `pkgs.tailscale.com` and checks it is signed by Tailscale Inc. before installing it.
No MTG archives either: Setup downloads the ones a friend lacks from `MtgBaseUrl` (for now `mtg-share.py` on this
PC, over Tailscale) and checks each against the kit manifest's sha256.

| File | What it is |
| --- | --- |
| `friend-installer.iss` | Inno Setup script: pages, the download page, uninstaller, shortcut |
| `friend-setup.ps1` | the worker the installer runs (checks, Tailscale, MTG placing, patch, login, probe, uninstall); `-DryRun` |
| `build.ps1` | checks the kit and settings, writes `build\`, compiles; `-DryRun` skips the compile |
| `owner-setup.ps1` | your side: Tailscale on this PC, firewall rules, the ACL, `owner-settings.json`; `-DryRun` |
| `mtg-share.py`, `Share MTG files.cmd` | shares the 23 MTG archives with friends' Setup, Tailscale addresses only, port 43480 |
| `MTG-CREDITS.txt` | credits for the MTG archives; installed next to the friend's README |
| `test-friend-setup.ps1` | offline test on a dummy client and a loopback share (`-ProbeAddress <ip>` also pings the login port) |
| `owner-settings.example.json` | copy to `owner-settings.json` (gitignored) |
| `FRIENDS-README.md` | the friends' one page (also installed as `README.txt`) |
| `launcher/Launcher.cs` | the **SWG: Fractured Galaxy** launcher and updater (the friends' desktop shortcut); `build.ps1` compiles it |
| `launcher/make-banner-art.sh`, `make-banner.py` | the banner: local ComfyUI art, then the title (`launcher/banner.png`, not in git) |
| `news.txt` | the news line friends' launchers show; edit it any time, `mtg-share.py` reads it on each request |

## Your one-time steps

1. **Tailscale on this PC.** Done 18 Oct: this PC is `[tailnet address removed]`, key expiry off.
   (PowerShell as administrator, in this folder: `.\owner-setup.ps1 -InstallTailscale`, then sign in; then in the
   admin console, https://login.tailscale.com/admin/machines, disable key expiry for this PC.)
2. **Firewall.** `.\owner-setup.ps1 -Firewall` (administrator). It allows UDP 46453, 46462, 46463 (the test
   galaxy, in both the WSL Hyper-V firewall and Windows Defender) and TCP 43480 (the MTG share, Windows Defender)
   in, only from Tailscale addresses (100.64.0.0/10). Run it again after an update: it replaces its own rules.
   `-RemoveFirewall` takes them out.
3. **ACL.** `.\owner-setup.ps1 -ShowAcl` prints a policy with this PC's address filled in. Paste it at
   https://login.tailscale.com/admin/acls (JSON editor; delete the comment lines at the top if the paste splits
   one). Friends tagged `tag:swg-friend` reach only the test galaxy's login (46453), ping (46462) and zone (46463)
   ports over UDP, and the MTG share (43480) over TCP. Not Ollama (11434), the live map (8765), ComfyUI (8188),
   ORB (46419), status (46455), MariaDB or SSH; the policy's `tests` block fails the save if any of those opens.
   Your own devices keep reaching each other.
4. **Settings.** `.\owner-setup.ps1 -WriteSettings` writes `owner-settings.json` with this PC's tailnet IPv4 and
   `MtgBaseUrl` `http://<that IPv4>:43480/`. Using the IP rather than the MagicDNS name keeps the tailnet name out
   of the installer.
5. **Build.** `.\build.ps1` (Inno Setup 6 is installed). The result is `build\out\SWG-Friends-Setup-<version>.exe`
   (gitignored). Before sending it, check the server's `local_planets.tre` matches the kit
   (`client-patch-for-friends.md`, check-server).
6. **The galaxy address** (the lock holder does this, see below). Without it a friend logs in and then hangs at
   the galaxy list or the zone connection.
7. **Run `.\owner-setup.ps1`** (no switches). Every line should say ok.

## The launcher: updates without a new Setup.exe

Friends start the game from **SWG Fractured Galaxy** on their desktop. Each time it opens it asks `mtg-share.py`
(the same window as the MTG share, port 43480, Tailscale only) for `update.json`, then:
- downloads **the `local_planets.tre` the server loads right now** (read from `\\wsl.localhost\Debian\opt\swg\tre`,
  read-only) whenever the friend's copy differs, keeping their old one in `local_planets-patch\backup\<version>`;
- downloads any MTG archive they're missing; every file is checked against its sha256 before it replaces anything;
- replaces itself when `build.ps1` has built a newer launcher (bump `AssemblyVersion` in `Launcher.cs`);
- puts the login and `.include` lines back if the SWGEmu launcher reset them, and shows server status and `news.txt`;
- (since 1.0.2, owner 18 Oct: "on for everyone") puts in the **graphics add-on**: DXVK 3.1.1 as `dxvk_d3d9.dll` with
  the O15 hook in front of it as `d3d9.dll` (the light whip's bend, the ghostfire haze), O15's default `mirage.ini`
  and this client's `dxvk.conf` (60 fps cap). The share offers `SWG-client`'s own copies, and only while its
  `dxvk_d3d9.dll` is that DXVK and its `d3d9.dll` a mirage build, so **a hook installed on your client reaches
  friends at their next launch**. Left out on a PC without Vulkan, next to a `d3d9.dll` it doesn't know, and after a
  friend deleted ours (their way to turn it off). Settings files that are there are never overwritten. What it adds
  is recorded in `local_planets-patch\addon.json`, and the uninstaller takes it out again.

The banner (built into the exe) is `launcher/banner.png`, not in git: the owner's pick of 18 Oct, B_s303, made on
Juggernaut XL Lightning with the Star Wars Cinematic Style XL LoRA (image-to-image and inpaint over the owner's seed-128
picture), titled by `launcher/make-banner.py`. To change it, replace `banner.png` (1536x512), bump `AssemblyVersion`
in `Launcher.cs`, and run `build.ps1`; friends' launchers pick up the new exe by themselves.

Play stays off while a friend's patch differs from the server's. So after a server archive change you only need
`Share MTG files.cmd` running when friends start their launchers; rebuild Setup.exe only for new friends or a new
installer. When the share is off, the launcher says it can't check and lets them play with what they have.

## Each friend

1. **An invite key**: https://login.tailscale.com/admin/settings/keys > Generate auth key:
   **Reusable off** (one-time), **Ephemeral off** (the friend keeps the device), **Pre-approved on** (if device
   approval is on), **Tags: `tag:swg-friend`**, expiry 1-7 days. Send the key in a private message, separately
   from the installer, and don't paste it anywhere else. A tagged device has no key expiry of its own.
2. **Share the MTG archives while they install**: double-click `Share MTG files.cmd` and leave its window open.
   It checks the 23 files against the kit, then lists each download as it finishes. A friend with no MTG
   archives pulls 4.7 GB from your upload: about 35 minutes at 20 Mbps up, 70 at 10. Close the window afterwards.
3. Send them `SWG-Friends-Setup-<version>.exe`.
4. Their account: they log in once with a username they choose (AutoReg makes it at level 0). Staff rights, if
   any, follow `Documentation-support/remote-access-and-second-owner.md` section 5.2.
5. **Removing a friend**: delete their device in the Tailscale admin console. The installer cannot reach anything
   after that.

## The MTG archives: where they come from, and moving them later

- The share serves `outputs/Community-content/MTG-assets` (gitignored): Mod the Galaxy's 23 archives, downloaded
  13 Oct from a public Google Drive folder recorded as MTG's (`work/download_mtg_assets.py`). They match the kit
  manifest byte for byte (`mtg-share.py --verify`, 18 Oct).
- **Terms (checked 18 Oct):** MTG's site terms say nothing on re-hosting or bundling. MTG's one stated condition
  for using its content is full credit to the creators and not claiming the work
  (https://github.com/ModTheGalaxy/mtgserver/wiki). Precedent: Infinity's launcher downloaded 22 MTG archives from
  Dropbox links, Flurry hosts them on its own site, and MTG's own Relics of Corbantis launcher downloads the whole
  SWGEmu client. No public server fork hosts the .tre files on GitHub itself. Not checked: MTG's login-only forum
  threads and Discord. Keep `MTG-CREDITS.txt` with every build.
- **Moving to Cloudflare R2 later** (free: 10 GB storage a month, downloads free; it charges only past 10 GB
  stored or millions of requests; the r2.dev link is rate-limited and meant for development, so connect a domain
  if many friends join): upload the 23 files side by side into a bucket, put its https link in `MtgBaseUrl`, rebuild.
  The TCP 43480 ACL line and firewall rule can then go. Backblaze B2 also works (10 GB free; downloads free up to
  3x what is stored, about 3 full friend installs a month, then $0.01/GB).
- Why 43480: in mirrored mode WSL reserves 44620-48715 for Linux's own outgoing ports, and Windows cannot listen
  inside that range.

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
  follows the row). WSL lists the tailnet address under mirrored networking (`owner-setup.ps1`, 18 Oct), but
  nobody has logged in through it yet. Test before a friend's window: one bot login and one owner login after the
  UPDATE. If bots fail, put `192.168.1.210` back between windows.
- If Tailscale stops on this PC, nobody gets past the galaxy list until it is back or the row is changed back.
- Live (44453/44463) stays LAN-only. Opening it means new firewall ports, a new ACL line and the owner's OK.

## What was tested

- 17 Oct: `test-friend-setup.ps1` (14 checks then), `build.ps1 -DryRun`, `owner-setup.ps1 -DryRun -ShowAcl
  -Firewall`; Inno Setup 6.7.3 installed (owner's OK; winget, per-user in `%LOCALAPPDATA%\Programs\Inno Setup 6`).
- 18 Oct: Tailscale installed and signed in on this PC, and the UDP firewall rules added (owner, as
  administrator). `test-friend-setup.ps1`: all 24 checks pass, including the MTG list (links and sha256),
  placing downloads with the friend's own version kept, an incomplete download changing nothing, uninstall
  removing what Setup added and restoring the friend's files, and `mtg-share.py` on loopback (serves listed files
  byte for byte, 404 for anything else, refuses to start on a mismatched file). `mtg-share.py --verify` on the
  real archives, then `mtg_patch_021.tre` fetched from `http://[tailnet address removed]:43480/` on this PC (sha256 matches)
  and `manifest.json` refused (404). `build.ps1` compiled `SWG-Friends-Setup-2026.10.16.1.exe` (6.5 MB) with the
  real address and the download step.
- **Not tested**: Setup.exe's pages and download page on a real friend PC; the TCP 43480 firewall rule and the new
  ACL from another device; a friend joining with a real key; a login over Tailscale (the test galaxy was off on
  18 Oct morning); the uninstaller's Tailscale choices.
