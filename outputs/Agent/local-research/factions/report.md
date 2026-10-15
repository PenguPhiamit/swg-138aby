Written by Claude Haiku, 15 Oct 2026, from Core3-dev 90044b8e. (Run restarted part-way; Claude Opus finished the reading and wrote this file.)

# Factions and the Galactic Civil War

Paths are relative to MMOCoreORB/. "Convo" = bin/scripts/screenplays/gcw/recruiters/recruiterConvoHandler.lua, "Screenplay" = .../recruiterScreenplay.lua in the same folder.

## 1. Short answer
A player joins Rebel or Imperial at a recruiter once they have at least 200 standing with that faction, and starts as covert (Convo:125-146, Screenplay:8). Standing goes up and down from NPC kills (killed faction's enemies gain, the faction and its allies lose double) and from PvP kills (+30 / -45). It is spent at the recruiter on promotions and items, always keeping 200 in reserve. Status is on leave (0), covert (1) or overt (2); recruiter changes take 30 s or 5 min. Two players of opposite factions can attack each other only when both are overt, or when a covert one has a 5-minute GCW TEF (temporary enemy flag), unless grouped, in a no-combat area or in different zones.

## 2. How it works
**Joining.** Minimum standing 200 (Screenplay:8). Path "accept_join2": below 200 shows screen "neutral_need_more_points2" with the 200 figure; otherwise sets faction to the recruiter's and status 1 (Convo:125-146). No points are deducted on joining (inferred, Convo:140-146). An older "accept_join" screen sets faction and status 1 with no check in that branch (Convo:35-37).

**Status values and changes at a recruiter.** 0 = on leave, 1 = covert, 2 = overt (Screenplay:780, 794, 799). Each change sets a future status, writes "changingFactionStatus" and schedules an event: go overt 30 000 ms (Convo:39-42); go covert 300 000 ms (Convo:43-51); go on leave 300 000 ms (Convo:52-60); resign 300 000 ms (Convo:62-70); resume duties = covert in 30 000 ms (Convo:73-76). Jedi (force_rank_light/dark_novice) are refused covert, leave and resign with @faction_recruiter:jedi_cant_go_covert / jedi_cant_resign (Convo:44-46, 63-66; Screenplay:774-777). Resign sets rank 0, status 0, faction 0 (Screenplay:819-836).

**Field change (no recruiter).** Refused if already overt, same status, or a change is pending (PlayerObjectImplementation.cpp:3681-3687). A box titled @gcw:gcw_status_change asks the player to type YES (PlayerObjectImplementation.cpp:3692-3705); anything else or Cancel gives @gcw:abort_field_change (FieldFactionChangeSuiCallback.h:24-32, under src/server/zone/objects/player/sui/callbacks/). Covert: @gcw:handle_go_covert, applied after 30 000 ms (same file:48-59). Overt: "You will be flagged as Special Forces in 5 minutes.", applied after 300 000 ms (61-72). Overt to covert in the field is refused with @gcw:cannot_change_from_combatant_in_field (43-45).

**What the player sees when status lands** (src/server/zone/objects/tangible/TangibleObjectImplementation.cpp). Future status reset to -1 (177-178). Covert: "Your faction affiliation has now been hidden from others." (covert/overt system) or @faction_recruiter:covert_complete; OVERT flag cleared (195-203). Overt: OVERT flag set, cooldown "declare_overt_cooldown" = GCW manager overt cooldown, default 300 s (205-218); "You successfully declare overt faction status. You may now be attacked by opposing faction members." or @faction_recruiter:overt_complete (220-224). On leave: OVERT cleared; @faction_recruiter:resign_complete (covert/overt system) or on_leave_complete (238-251). The PvP status bitmask is resent (254-255).

**Standing limits and messages** (PlayerObjectImplementation.cpp). Gain: non-GCW factions capped at 5000; own GCW faction capped at the rank cap; the other GCW faction at 1000 (2170-2184). Message @base_player:prose_award_faction with the amount, or prose_max_faction when nothing changed (2188-2199). +10% bonus if the player's faction won Cries of Alderaan, message prose_coa_bonus (2203-2235). Loss: floor -5000 (2273-2274); message prose_lose_faction or prose_min_faction (2285-2296). Rank cap = max(1000, rank cost x 20) (src/server/zone/managers/faction/FactionManager.cpp:287-292); rank names and costs come from datatables/faction/rank.iff (FactionManager.cpp:26-41).

**Earning.** NPC kill: gain = level x the faction's adjust factor, added to each player-allowed enemy of the killed faction (rebel/imperial only when the killed faction is itself GCW); the killed faction and its non-GCW allies lose 2 x gain (FactionManager.cpp:91-152). Factions, enemies, allies and adjust factors load from scripts/managers/faction_manager.lua (FactionManager.cpp:20-24, 55-75). PvP kill (both players): rebel kills imperial gives killer +30 rebel and -45 imperial, victim -45 imperial; the mirror for imperial (FactionManager.cpp:238-257).

**Spending.** Promotion: next rank cost from getRankCost; needs standing >= cost + 200, else screen "not_enough_points" with rank name and cost; otherwise cost is deducted and rank +1 (Convo:78-99). Highest rank is the last in the table or 15 (src/server/zone/managers/faction/FactionManager.h:65-67). Purchases need standing >= item cost + 200 (Screenplay:477, 566, 618); failures: inventory full, datapad full, too many hirelings, not enough standing (Screenplay:426-435). Categories: furniture, weapons/armor, installations, uniforms, hirelings, schematics, with a GCW discount (Convo:113-114). Smugglers with combat_smuggler_underworld_04 can bribe 20 000 / 100 000 credits for 250 / 1250 standing if under the cap (Convo:101-111).

**Who can attack whom (player target)** (src/server/zone/objects/creature/CreatureObjectImplementation.cpp:3628-3809). False if: same object, invisible, dead, different zone, either in a no-combat area, target on load screen (3629-3667). For player vs player, in order: server PvP mode means true (3728-3730); mutual personal enemy flag, mutual duel, bounty mean true (3740-3753); same group means false (3756-3758); both in a PvP area or guild war means true (3760-3768); same faction means false (3771-3772). Different factions, covert/overt system: overt vs overt true; covert target with GCW TEF vs overt attacker, or vs covert attacker with TEF, true; overt target with TEF vs covert attacker with TEF true; else false (3776-3794). Old system: both overt (3796-3800). Faction NPC vs player: never attacks neutral or same faction (3701-3710); covert/overt system needs player overt or with GCW TEF (3712-3715). A crackdown TEF overrides (3696-3699). A target that is attackable is not healable (3818-3819).

**TEF timer.** TEFTIMER = 300 000 ms (FactionManager.h:22). A GCW action extends the GCW TEF by that much and sets the TEF bit in the PvP status (PlayerObjectImplementation.cpp:2860-2870); hasGcwTef is true until it expires (2906-2908).

## 3. What a bot test should check
Setup: two bots in the same zone, not grouped, no duel, no bounty, outside no-combat and PvP areas, no guild war; server PvP mode off. Give each 200+ standing with its faction (from kills, or an admin tool; see open questions). Know whether the covert/overt system is on.
1. Join: talk to the recruiter; expect the faction set, status 1 and "hidden from others" message. With under 200, expect the need-more-points screen and no faction.
2. Covert vs covert, no TEF: neither shows as attackable; an attack is refused.
3. Go overt (recruiter, 30 s; field, 5 min): expect the OVERT bit and the overt message after the delay, not before. Both overt: each is attackable by the other.
4. One overt, one covert: not attackable until the covert bot gets a GCW TEF; then attackable for 5 min, and the TEF bit drops after expiry.
5. Points: record standing, kill a faction NPC, expect the award/loss messages and changed totals. A PvP kill gives killer +30 and both sides -45 to the enemy faction.
6. Promotion: standing falls by the rank cost and the rank rises; with too few points, the not_enough_points screen and no change.
7. Group the two overt bots: no longer attackable.

## 4. Likely reasons a test sees no effect
The timer has not run (30 s or 5 min). A change is already pending (field change silently returns). The bot is Jedi. The bots are grouped, in different zones, in a no-combat area, or on a load screen. One is covert without a GCW TEF, or the TEF expired after 5 min. PvP mode on makes everything attackable (false pass). Standing under 200, or under cost + 200 for promotions. Standing at the cap, so the award shows the max message and no change. The recruiter delay uses createEvent; a server restart in between may drop it (inferred).

## 5. Open questions
- Config keys and current values behind useCovertOvertSystem and getPvpMode (not read).
- Which code calls awardFactionStanding and with which level; what exactly sets the GCW TEF (combat manager not read).
- Rank costs and names (rank.iff is client data, not in the tree); adjust factors in faction_manager.lua (not read).
- GCWManagerImplementation.cpp was not read: faction bases, overt cooldown value, GCW discount, crackdown scans.
- FactionStatus.h not read; the 0/1/2 mapping comes from the recruiter scripts.
- Which command opens the field status change box; whether "accept_join" checks standing earlier in the conversation (checks exist at Convo:289, 295, context not read).
- How an admin can set standing for a bot quickly (a Lua setFactionStanding exists in PlayerObjectImplementation.cpp:2300; the command was not found).
