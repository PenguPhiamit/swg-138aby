# Guild Mechanics Report

## 1. Short Answer

Guilds are created through a GuildTerminal by entering a name (1–25 characters) and abbreviation (1–5 characters); the creator becomes the leader with full permissions. New members join via sponsorship: a leader sponsors a nearby player, who receives an accept/decline dialog; leaders can also manage pending sponsorships through the terminal. Kicking removes a member (except the leader), sends system messages to both parties, and delivers a guild mail. Leaving removes the player from the guild and chat rooms, sends a mail, and triggers an election if the leader leaves without one enabled. Disbanding requires disband permission and destroys the guild, notifying all members via mail.

## 2. How It Works

### Guild Creation
- The player interacts with a GuildTerminal to start creation. `sendGuildCreateNameTo` opens an SUI input box for the guild name (478–496). Names must be 1–25 characters, unique, and allowed by the NameManager (524–546).
- Next, `sendGuildCreateAbbrevTo` opens an abbreviation input (564–577). Abbreviations must be 1–5 characters, unique, and allowed (592–614).
- `createGuild` checks the player is not already in a guild (633–636), strips newlines/color codes from name/abbrev (645–646), creates a GuildObject (648), sets the leader ID (652), adds the player as a member (656), grants all permissions to the leader (666), and creates chat channels (659–662). Delta messages are broadcast to online players (670–683).

### Sponsorship
- A leader with sponsor permission uses the terminal (`sendGuildSponsorTo`, 1403–1426) to enter a target name. `sponsorPlayer` checks permissions (1409, 1436), guild capacity (1441), finds the target by name (1446), and verifies the target is online and within 32 meters (1455).
- The target receives a SUI MessageBox (`GUILD_SPONSOR_VERIFY`) with accept/decline buttons (1476–1491). If accepted, `acceptSponsorshipRequest` sends system messages to both parties (1505–1514), adds the target to the sponsored list (1526–1527), and sends a guild mail (1534).
- Leaders can also view pending sponsorships via `sendGuildSponsoredListTo` (1537–1568) and manage them through `sendGuildSponsoredOptionsTo` (1570–1606). `acceptSponsoredPlayer` adds the member, sends messages/mail (1608–1671); `declineSponsoredPlayer` sends decline notifications (1673–1708).

### Kicking
- `kickMember` checks kick permission and that the target is not the guild leader (1247). It removes the member from the guild (1258), clears their guild object (1264), sends a system message to the kicker ("You remove %TU from %TT", 1267–1270) and to the target if online ("%TU has removed you from %TT", 1273–1275), removes them from chat rooms (1286–1295), and sends a guild mail (1305–1312).

### Leaving
- `leaveGuild` removes the player from the guild (2096), clears their guild object (2097), broadcasts a delta message (2099–2102), updates building permissions (2106–2108), sends a system message ("You leave %TU", 2092–2094) and a guild mail ("%TU has removed themselves from the guild", 2110–2113). If the leader leaves and no election is enabled, `toggleElection` is triggered (2115–2117). The player is removed from chat rooms (2121–2130).

### Disbanding
- `disbandGuild` checks disband permission (861–864), creates a mail body "The guild has been disbanded by %TU" (866–868), and calls the native function `destroyGuild` (870). The server logs "Guild ... disbanded." (872).

### Permissions
- Permission checks are enforced at each step: name change requires `hasNamePermission` (502), disband requires `hasDisbandPermission` (861), kick requires `hasKickPermission` (1247, 70–74 in GuildremoveCommand.h), sponsor requires `hasSponsorPermission` (1409, 1436), and accept/decline requires `hasAcceptPermission` (1582, 1611, 1676).

## 3. What a Bot Test Should Check

### Setup
- Two bot characters (Bot A and Bot B).
- One GuildTerminal object available in the zone.
- Bot A not in any guild; Bot B not in any guild and within 32 meters of Bot A.
- Both bots online and able to interact with SUI dialogs.

### Observable Results
- **Creation**: After completing name/abbrev input, Bot A's `isInGuild()` returns true, `getGuildObject()` is non-null, a system message confirming creation appears, and Bot A is in the guild chat room.
- **Sponsorship**: Bot B receives a SUI dialog (`GUILD_SPONSOR_VERIFY`) with accept/decline buttons. After accepting, Bot B's `isInGuild()` returns true, guild object is set, system messages appear on both bots, and a guild mail is delivered to Bot B.
- **Kicking**: After kicking, the target's `isInGuild()` returns false, guild object is null, both bots receive system messages, a guild mail is sent, and the target is removed from chat rooms.
- **Leaving**: The leaving player's `isInGuild()` returns false, guild object is null, a system message appears, a guild mail is sent, and the player is removed from chat rooms. If the leader leaves without an election enabled, an election should be triggered (observable via terminal options).
- **Disbanding**: The guild no longer exists in the server's guild list, all members receive a disband mail, and native `destroyGuild` logic executes (870).

## 4. Likely Reasons a Test Sees No Effect

- A bot is already in a guild (479–482, 633–636, 1460–1466).
- The target player is not online or not within 32 meters of the sponsor (1455).
- The guild has reached maximum capacity (`maximumMembers = 500`, GuildManager.idl line 58; check at 1441).
- Insufficient permissions: the actor lacks kick, disband, sponsor, or accept rights (502–505, 861–864, 1247, 1409–1412, 1436–1439, 1582–1585, 1611–1614, 1676–1679).
- Guild name or abbreviation already in use or invalid length (530–543, 597–611).
- The GuildTerminal is out of range (force close distance is 32 meters: 492, 573, 1421, 1486, 1550, 1598).
- Native functions (`destroyGuild`, `createGuildChannels`, etc.) are not implemented or fail silently on the test server.

## 5. Open Questions

- **`destroyGuild`**: The native function called at line 870 is declared in GuildManager.idl (line 73) but its implementation is not in the provided files. It likely handles guild cleanup, member removal, and chat room destruction.
- **Chat room creation**: `createGuildChannels` (690–713) creates rooms via `chatManager`, but the ChatManager implementation is not included.
- **Election mechanics**: Functions like `toggleElection`, `processGuildElection`, `castVote`, and `viewElectionStandings` are native (GuildManager.idl lines 72, 202–214) and not shown.
- **Permission flags**: Methods like `hasKickPermission`, `hasDisbandPermission`, `hasSponsorPermission`, and `hasAcceptPermission` are GuildObject methods not in these files. Their logic (e.g., leader-only vs. permission-based) is unclear.
- **Guild size defaults**: `requiredMembers = 5` and `maximumMembers = 500` are set in the GuildManager constructor (GuildManager.idl lines 57–58), but it is unknown if these can be overridden by configuration or if they apply to all guilds uniformly.
- **SUI callbacks**: The actual callback implementations (`GuildCreateNameResponseSuiCallback`, `GuildSponsorVerifySuiCallback`, etc.) are referenced but not included, so the exact flow from dialog submission to server action is incomplete.

## ChatGPT's review (2026-10-18 22:31)

Checked supplied matching snapshots and Core3-dev 9d08e265, including the actual config. No Saluki disputed lead was listed. Source only.

**Holds:** name/abbrev validation, creator membership/full permissions, permission-controlled kicking/leaving/disband flow and sponsor online/32 m gates (GuildManagerImplementation.cpp:524-683,1247-1312,1436-1476,2092-2130). These actions are permission-based, not exclusively leader actions.

**Corrections:**
- **Accepting sponsorship does not join the guild.** acceptSponsorshipRequest only adds the pending sponsored list (1494-1534); an actor with accept permission must then call acceptSponsoredPlayer, which adds membership, guild object and chat-room entry (1608-1670). The report's two-bot test skips this second approval and would fail correctly.
- Capacity counts members **plus pending sponsored players** (1441), not members alone.
- RequiredMembers/MaximumMembers are loaded from scripts/managers/guild_manager.lua (75-79); current Lua is RequiredMembers=2, MaximumMembers=500 (55-59). Constructor five-member defaults are not the active config.
- destroyGuild is implemented in this same supplied C++ file (375 onward): chat destruction, sponsored-map cleanup, war cleanup, loaded-member guild clearing and disband mail are visible (375-440). Calling a method native in IDL does not mean absent/unimplemented. Do not diagnose silent failure on that basis. Election behavior and offline persistence still need their own acceptance tests.

Verdict: Basic guild operations supported; fix two-stage membership acceptance, pending capacity and active config; reject missing-native diagnosis; gameplay untested.
