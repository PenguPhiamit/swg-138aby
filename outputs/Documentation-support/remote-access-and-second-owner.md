# Remote access and a second owner account (Claude, 15 Oct 2026)

The owner, 15 Oct: "prep port forwarding and ready the server for a second owner account. my developer friend is possibly joining so i'd like to have things ready".

**Status: prep only. Nothing was opened or changed.** No router, firewall, WSL, config or database change was made, and no account was created. Every fact below was read on 15 Oct (10:00–10:10) from the files, database and Windows settings named next to it. "Untested" marks what nobody has tried yet. Opening ports is an outward-facing step: it waits for the owner's go, and the owner does the router and firewall steps themselves (section 4).

Placeholders used below. Never write the real values into `h/` (it goes to GitHub) or into Discord:
- `<PUBLIC_ADDRESS>`: the home connection's public IPv4, or a dynamic-DNS name for it;
- `<FRIEND_IP>`: the friend's public IPv4 (for a friend on the home network: `192.168.1.0/24`);
- `<FRIEND_USERNAME>`: the account name the friend picks. The friend's password is never written, chosen, stored or typed by anyone but the friend.

## 1. Short version

- **The friend on the home network:** firewall rules only (section 4.2). No router change, no address change: both galaxies already advertise the PC's LAN address `192.168.1.210`.
- **The friend outside the home network:** firewall rules, three UDP forwards on the router, and the lock holder switches the galaxy's advertised address to `<PUBLIC_ADDRESS>` for the window. With that address, every client on this PC (the owner's and the bots) also reaches the zone through the router, which works only if the router does NAT loopback (section 2.3). Test that first.
- **Second owner account:** the friend logs in once (AutoReg, which is on in both galaxies, makes the account), the lock holder runs one `UPDATE`, then the friend creates a character, which then gets admin level 15, the same level the owner's account has.
- **Order:** test galaxy first, a short window, rules limited to the friend's IP, everything closed again afterwards (section 6).

## 2. What the galaxies listen on, and how a client finds the zone

### 2.1 Ports (read from `bin/conf/config.lua` and `config-local.lua`)

Live: `/opt/swg/Core3/MMOCoreORB/bin/conf/` (service `swg-local`, stopped and disabled). Test: `/opt/swg/testgalaxy/Core3/MMOCoreORB/bin/conf/` (its `config.lua` is identical to live's; the ports come from the `-- TEST GALAXY OVERRIDES` block that `tools/test_galaxy.py` writes, line 47).

| Server | Live | Test | Protocol | Forward to the internet? |
|---|---|---|---|---|
| Login | 44453 (`LoginPort`) | 46453 | UDP | **yes** |
| Zone | 44463 (no `ZoneServerPort` in live's config, so `ConfigManager.h:490` returns 0 and `ServerCore.cpp:752-760` reads `port` from the `galaxy` table) | 46463 (`ZoneServerPort`) | UDP | **yes** |
| Ping | 44462 (`PingPort`) | 46462 | UDP | **yes** (the galaxy list's ping) |
| Status | 44455 (`StatusPort`) | 46455 | TCP | no: the game client doesn't use it |
| ORB (Core3's internal object broker) | 44419 (`ORBPort`) | 46419 | TCP | **never** |
| Web admin | 44460 (`WebPorts`) | off | TCP | off (`MakeWeb = 0`) |
| MariaDB | 3306, bound to 127.0.0.1 | same server | TCP | **never** |
| Live map (`swg-live-map`) | 8765, bound to 127.0.0.1 | | TCP | **never** |
| Ollama | 11434 | | TCP | **never** (`tools/agents/local/REMOTE-OLLAMA.md`) |

Checked on the running test galaxy with `ss -lntup` (15 Oct 10:05): `core3` holds UDP 46453, 46462 and 46463 and TCP 46419 and 46455, all on `0.0.0.0`. The live galaxy is stopped, so its ports come from the config alone. Clients use random source ports of their own; nothing needs forwarding on the friend's side.

### 2.2 How the login server hands out the zone address

1. The client's `swgemu_login.cfg` (`loginServerAddress0`, `loginServerPort0`) points it at the login server.
2. At every login, the login server reads the `galaxy` table again (`GalaxyList.h:25`) and sends each galaxy's `address`, `port` and `pingport` (`LoginServerImplementation.cpp:184-200`). The client then connects to the zone server at that address. There is one row, `galaxy_id = 2` (`ZoneGalaxyID = 2`). `galaxy_access` is empty in both databases, so every account sees the galaxy.
3. Rows on 15 Oct:
   - live `swgemu.galaxy`: "My Galaxy", `172.23.208.109` (stale, the WSL address from before mirrored networking), port 44463, ping 44462;
   - test `swgemu_test.galaxy`: "Test Galaxy", `192.168.1.210`, port 46463, ping 46462.
4. **Both start tools rewrite the address at every start:** `tools/start_server.py` (the address of the default route; it also rewrites `SWG-client/swgemu_login.cfg` to port 44453) and `tools/test_galaxy.py:131-133` (`hostname -I`). With mirrored networking both give `192.168.1.210`, so live's stale row is fixed at its next start.

**What a friend outside the home network needs:** `galaxy.address` must be `<PUBLIC_ADDRESS>`. The login server reads the table at each login, so an `UPDATE` works from the next login without a restart, but the next start of that galaxy puts the LAN address back. For now, the lock holder re-runs the `UPDATE` after each start (section 5.1). A later improvement, not made: both start tools could read an override from a private file outside git (for example `/opt/swg/agent/galaxy-address`). That needs a review, because `start_server.py` starts the live galaxy.

The bot client follows the same table: `core3client` connects to `galaxy.getAddress()` (`Core3-dev/.../src/client/actions/ConnectToZoneAction.cpp:73-104`), and `tools/bots/bot.py:53-55` logs in at the LAN address.

### 2.3 Hairpin NAT: the catch for everyone on this PC

The `galaxy` row holds one address for everybody. Once it says `<PUBLIC_ADDRESS>`:
- the friend outside connects fine (through the forwards);
- **the owner's client and every bot on this PC** are also told to reach the zone at `<PUBLIC_ADDRESS>`. Their packets go out to the router and must come back in through its forwards (NAT loopback, "hairpinning"). Many home routers do this, some don't, and some have it as a setting. Login itself still works, because their login address stays `192.168.1.210`. Bots already in the zone keep their connection; new logins and re-logins use the new address.

Ways around it:
1. **The router does NAT loopback** (check the router's settings, or test it: section 6, step 3). Simplest.
2. **A dynamic-DNS name** in `galaxy.address`, with a hosts-file line on this PC that maps the name to `192.168.1.210` (`C:\Windows\System32\drivers\etc\hosts`; also `/etc/hosts` in Debian for the bots). Untested: whether the SWG client and `core3client` resolve a name in that field. A DDNS name is a new external service (owner's OK), though many routers include a DDNS client; the hosts files are system files the owner edits.
3. **No local play during the window**: the owner plays after the address is put back, and bots stay logged in or paused.

## 3. WSL networking and inbound UDP

- `C:\Users\Pengw\.wslconfig`: `networkingMode=mirrored`, `hostAddressLoopback=true` (experimental), `vmIdleTimeout=-1`, `instanceIdleTimeout=-1`. WSL 3.0.3.0 on Windows 10.0.26200. Inside Debian, `eth0` is `192.168.1.210/24`, the same address as Windows' Ethernet adapter. The live map at `http://localhost:8765` reaches the WSL process through mirrored loopback (it is bound to 127.0.0.1 in Debian).
- Windows: Ethernet, static address `192.168.1.210` (DHCP off), gateway `192.168.1.1`, network profile **Private**.
- **What mirrored mode means for inbound UDP:** there's no NAT between Windows and WSL, so no `netsh interface portproxy` (which only handles TCP anyway). A packet that reaches the PC on a port a WSL socket holds goes straight to WSL. If a Windows program and a WSL program both bind a port, Windows gets it; nothing on Windows uses these ports today.
- **But WSL's Hyper-V firewall blocks it now.** `Get-NetFirewallHyperVVMSetting` for WSL's ID `{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}`: Enabled, **DefaultInboundAction Block**, LoopbackEnabled True, AllowHostPolicyMerge True. Its active rules (175) are the WSL defaults (ICMP and mDNS) plus copies of the host's own Windows Defender rules, merged in because of that last setting (the ARK server's UDP 7777, 7778 and 27015 show up there too). None of them names a galaxy port. So nothing from the internet reaches the galaxy today. The owner's client works because it runs on this PC (loopback).
  - One system rule, `MPSSVC_CONSTRAINED_INTERFACE_RULE_INBOUND_ALLOW`, allows every port from the local subnet. Its name says it covers "constrained" interfaces only. Whether a second PC on the LAN already reaches the galaxy without new rules is untested; add the rules anyway.
  - Remote play needs an allow rule. Section 4.2 adds two: a Hyper-V firewall rule for WSL (Microsoft's documented way for mirrored mode) and a Windows Defender rule (which the merge above should carry over as well). Which one is decisive is untested; both are limited to the friend's address and both come off after the window.
- **Don't use the common forum shortcut** `Set-NetFirewallHyperVVMSetting ... -DefaultInboundAction Allow`. It opens every WSL port to the network, including ORB (44419/46419) and status (44455/46455), which listen on all addresses.
- A VPN client is installed on this PC (its firewall rule is in the list). Keep it disconnected while hosting, or the server's replies may leave through the VPN.

## 4. The owner's checklist (the owner does these; agents don't)

### 4.1 Before the first window

- [ ] **Decide where the friend plays from:** the home network (skip the router steps and section 5.1) or outside.
- [ ] **CGNAT check (outside only).** Compare the WAN IPv4 on the router's status page with the public address a what's-my-IP page shows. If they differ, or the WAN address starts with `100.64`–`100.127`, `10.`, `172.16`–`172.31` or `192.168.`, the provider uses carrier-grade NAT and port forwarding can't work. The ways out need the owner's OK: ask the provider for a public IPv4, or use a mesh VPN such as Tailscale or ZeroTier (a new external service, installed on both PCs).
- [ ] **Keep `192.168.1.210` for this PC.** The PC sets it statically, so make sure the router's DHCP pool can't give it to another device (a reservation, or a pool that doesn't include .210).
- [ ] **Get the friend's public IPv4** (they read it from a what's-my-IP page). It's `<FRIEND_IP>` below. Keep it out of `h/`.
- [ ] **Tell the lock holder the window** in chat or on the board ("friend on the test galaxy 19:00–21:00"). The standing OK for test-galaxy restarts (AGENTS.md) checks only the owner's own client, so no agent, and not the 30-minute cycle, would notice a friend playing from another PC.

### 4.2 Windows firewall (PowerShell, "Run as administrator")

Test galaxy (paste as is, after putting the friend's address in the first line):

```powershell
$friend = '<FRIEND_IP>'    # the friend's public IPv4; for a friend on the home network: '192.168.1.0/24'
$wsl = '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}'    # WSL's ID in the Hyper-V firewall
New-NetFirewallHyperVRule -Name 'SWG-Test-UDP-In' -DisplayName 'SWG test galaxy (UDP in)' -Direction Inbound -VMCreatorId $wsl -Protocol UDP -LocalPorts 46453,46462,46463 -RemoteAddresses $friend -Action Allow
New-NetFirewallRule -Name 'SWG-Test-UDP-In' -DisplayName 'SWG test galaxy (UDP in)' -Group 'SWG remote access' -Direction Inbound -Protocol UDP -LocalPort 46453,46462,46463 -RemoteAddress $friend -Profile Private -Action Allow
```

Live galaxy (later, with its own window; same first two lines):

```powershell
New-NetFirewallHyperVRule -Name 'SWG-Live-UDP-In' -DisplayName 'SWG live galaxy (UDP in)' -Direction Inbound -VMCreatorId $wsl -Protocol UDP -LocalPorts 44453,44462,44463 -RemoteAddresses $friend -Action Allow
New-NetFirewallRule -Name 'SWG-Live-UDP-In' -DisplayName 'SWG live galaxy (UDP in)' -Group 'SWG remote access' -Direction Inbound -Protocol UDP -LocalPort 44453,44462,44463 -RemoteAddress $friend -Profile Private -Action Allow
```

Check what is open:

```powershell
Get-NetFirewallHyperVRule -Name 'SWG-Test-UDP-In','SWG-Live-UDP-In' -ErrorAction SilentlyContinue | Format-Table Name, LocalPorts, RemoteAddresses, Action, Enabled
Get-NetFirewallRule -Group 'SWG remote access' -ErrorAction SilentlyContinue | Format-Table Name, Enabled, Action
```

Close everything again (after every window):

```powershell
Remove-NetFirewallHyperVRule -Name 'SWG-Test-UDP-In','SWG-Live-UDP-In' -ErrorAction SilentlyContinue
Remove-NetFirewallRule -Group 'SWG remote access' -ErrorAction SilentlyContinue
```

The cmdlet parameters were checked on this PC with `Get-Command -Syntax`; the rules themselves have not been created or tried.

### 4.3 Router (outside only)

- Three port forwards, **UDP only**, external port = internal port, to `192.168.1.210`:
  - test galaxy: **46453, 46462, 46463**;
  - live galaxy: **44453, 44462, 44463**.
- If the router can limit a forward to one source address ("remote IP", "allowed source"), set `<FRIEND_IP>`.
- Never forward TCP for this, and never 44419/46419, 44455/46455, 3306, 8765 or 11434. Don't turn on UPnP for it.
- Remove the forwards when the window ends.

### 4.4 The friend's client

- **Game files:** the friend needs their own copy of the game, installed the way SWGEmu requires. Handing over this PC's SOE files isn't ours to do (AGENTS.md, Ethics check 1).
- **Extra archives:** the 23 MTG archives come from MTG's own release; check its terms before the owner passes copies on. `local_planets.tre` (Hoth, Ossus) is our test-only archive; how friends get it is the open roadmap item "Client patch distribution for friends". Without it the friend's client has no Hoth or Ossus, so the friend stays off those planets. What happens if they try is untested.
- **Login file** (`swgemu_login.cfg` in their client folder):

```
[ClientGame]
loginServerAddress0=<PUBLIC_ADDRESS>
loginServerPort0=46453
```

  Use `44453` for the live galaxy. For a friend on the home network: `loginServerAddress0=192.168.1.210`.

## 5. Steps for the lock holder (written here, not run)

Run as root in Debian. The commands below were checked from PowerShell with a read-only `SELECT` in the same form (`--exec` keeps Debian's shell from splitting the quotes).

### 5.1 Advertise the public address (outside only; after the galaxy has started)

Test galaxy:

```powershell
wsl -d Debian -u root --exec mariadb swgemu_test --execute "UPDATE galaxy SET address='<PUBLIC_ADDRESS>' WHERE galaxy_id=2;"
```

Live galaxy (a live database change: the owner's OK first): the same with `swgemu` in place of `swgemu_test`.

Back to the LAN address: the same statement with `192.168.1.210`, or the next start of that galaxy. Check with `SELECT galaxy_id, name, address, port, pingport FROM galaxy;`. While the public address is set, a bot login is the quickest hairpin test (section 2.3).

### 5.2 The second owner (full admin) account

How Core3 stores staff rights:
- **Accounts:** the `accounts` table (`account_id`, `username`, `password`, `salt`, `station_id`, `created`, `active`, `admin_level`). On 15 Oct, both databases have the owner's account as `account_id = 1`, `admin_level = 15`, active. Live has 3 accounts (one at 15, two at 0); test has 20 (the owner's at 15 and 19 bot accounts at 0).
- **Levels:** `bin/scripts/staff/levels/*.lua`. 15 is `admin` (full), 14 `dev`, 13 `qa`, 12 `csr`, 0 `player`.
- **Characters:** a character gets staff rights from its account only when it is created, and only for account levels 9, 10, 12 or 15 (`PlayerCreationManager.cpp:445-449`; `freeGodMode = 0` in `player_creation_manager.lua`). A character made earlier changes only with `/setGodMode` (below).
- `bin/conf/adminusers.lst` is an upstream example list that the Core3 source never reads. Leave it alone.

The safest route; nobody but the friend ever sees or handles their password:
1. **The friend makes their own account.** They log in from their own client with a username and password they choose themselves. AutoReg is on (`Core3.AutoReg = 1` in both config-local files), so the login server creates the account at level 0 (`AccountManager.cpp:223-231`). They stop at the character screen and quit, and tell the owner only the username.
2. **The lock holder raises it,** with the owner's OK (an account change), using one statement in the galaxy's database (`swgemu` for live, `swgemu_test` for test):

   ```sql
   UPDATE accounts SET admin_level = 15 WHERE username = '<FRIEND_USERNAME>' AND admin_level = 0;
   ```

   It must report 1 row changed. Check it with `SELECT account_id, active, admin_level FROM accounts WHERE username = '<FRIEND_USERNAME>';` (never select `password` or `salt`).
3. **The friend logs in again and creates their character.** It gets admin level 15 at creation.
4. **If the friend already made a character before step 2:** the owner, in game, on a character with admin level 15, while the friend is online: `/setGodMode <character first name> admin` (`SetGodModeCommand.h`: it needs the `admin_base` skill and a level at least as high as the target's).

Live and test are separate databases. An account made on the test galaxy doesn't exist on live, so the friend logs in once on each galaxy and step 2 runs on each. The other way round, a test start with `--fresh` copies the newest live backup, so a live account carries over to the test galaxy from then on.

## 6. Order and risks

**Order:**
1. Section 4.1 checks; the lock holder confirms that no squad round or restart is due during the window.
2. **Test galaxy, short window (an hour or two), rules limited to `<FRIEND_IP>`:** the owner adds the firewall rules and router forwards; the lock holder sets the public address (outside only).
3. **Hairpin test before the friend logs in** (outside only): the lock holder logs one bot in, and the owner tries their own client. If either hangs at the zone connection, use option 2 or 3 of section 2.3.
4. The friend logs in, which creates their account → the lock holder's `UPDATE` → the friend creates a character → a quick check of a staff command.
5. **Close:** the owner removes the forwards and rules (section 4.2); the lock holder puts the LAN address back. One line on the board: what worked, what didn't.
6. **Live, only later and only with the owner's go:** a backup first (`Back Up SWG Galaxy.cmd`), then the same steps on ports 44xxx, a live start (owner's OK) and the account steps on live. Close again afterwards. Don't leave forwards open between sessions.

**Risks:**
- **Open registration.** With the ports reachable and AutoReg on, anyone who reaches the login port can create an account just by logging in. Limiting the rules to `<FRIEND_IP>` prevents that. If neither the router nor the firewall rule can be limited, the lock holder can set `Core3.AutoReg = 0` in config-local once the friend's account exists (a restart, and new players then need accounts made by hand: the owner's call).
- **Core3 isn't hardened for the internet.** Its UDP servers answer anyone, and scanners find open ports within hours. Keep windows short, and never expose ORB, status, MariaDB, the live map or Ollama.
- **Full admin can undo a lot** (delete, spawn, grant). Back up before giving it on live; staff commands are written to the admin log (`logAdminCommand`).
- **Restarts under the friend:** see 4.1. The test galaxy also carries the bot squads and the 30-minute cycle, and this PC ran out of memory once on 15 Oct (board, 08:15).
- **The public address can change** (most home connections get a dynamic IP). The friend's login file and the `galaxy` row then break until both are updated; a DDNS name avoids that (owner's OK).
- **Privacy:** the friend's IP, username and character names stay out of `h/`, the board and Discord. The server's own logs, on this PC only, will hold their IP.

## 7. Developer access (optional)

- **GitHub:** a filtered copy of `h` goes to the owner's private repository, made and pushed only by `outputs/tools/github_export.py` after `outputs/tools/prepush_scan.py` (AGENTS.md, "Source control"). Agents never push and never add a remote. **The owner** adds the friend as a collaborator on GitHub (an account change only the owner makes). On a personal repository, GitHub gives collaborators push rights. The export can force-push (it does after a scrub-list change), so anything the friend pushes there may be overwritten. Ask them to send changes as patches (`git format-patch`) instead; the owner or an agent applies them to `h` locally, and the next export carries them.
- **Server code:** the repositories under `/opt/swg` (Core3, Core3-dev, Core3-gpt) aren't on GitHub, and stay off it until the owner decides. The friend sees `h` only: docs, tools, scenarios and reports.
- **Shell or remote-desktop access to this PC** isn't part of this prep. It would be a separate owner decision with its own risks.
- **AGENTS.md rules that apply to a human developer too:**
  - **Privacy:** no real names, handles or identifying character names in anything pushed (the friend's own included), except licence-required credits.
  - **Owner consent:** new external services, downloads, live deploys and restarts, account changes and outbound posts each need the owner's own OK.
  - **Server lock:** only the agent or person named in the board's lock line edits `/opt/swg`; take it on the board first.
  - **Rights:** the Ethics check's rules on sources and asset rights apply to anything the friend brings in, and the same in-game fair-play rules apply to staff commands.
