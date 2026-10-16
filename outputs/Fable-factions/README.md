# More than two sides: a faction plan for 138-139 ABY on Core3

Claude (Opus 5.5), 16 Oct 2026, taking over the content-design job Fable had queued. The owner asked (15 Oct) for "a
galaxy-wide faction plan with more than two sides mapped onto Core3", and earlier said "more than two factions could be
cool too since there is more than 2 in universe".

Design only. Core3 was read, never written: `/opt/swg/Core3-dev`, dev `a8ece12b`, inside WSL as swgemu, from a script
file in my temp folder. The client tables were read with `tools/swgfmt` and extracted to a temp folder outside the repo.
The lore was checked on Wookieepedia's Legends pages in the browser pane on 16 Oct; every lore summary below is in our own
words. Nothing was built, run or posted. The ranked content list is [`../Fable-backlog/README.md`](../Fable-backlog/README.md),
where this plan is item FW-01.

## In short

- **The sides at 138-139 ABY.** In the war:
  - the Triumvirate (Fel's Empire, the Galactic Alliance Remnant and the Jedi, ruling from Coruscant since 138);
  - Krayt's holdouts: the One Sith gone underground, plus Imperial garrisons that never stood down (the second part is
    ours).

  Around the war: Darth Wredd, a rogue Sith hunting the One Sith; the hidden Jedi; the Vong around Nei Rin; the Hutt
  kajidics; the Mandalorian clans; and local peoples such as Ossus's Ysanna.
- **What Core3 can already do.** It tracks a player's standing with any number of NPC factions, and that standing
  already decides whether a side's NPCs attack, ignore or defend against the player. It also has PvP that doesn't depend
  on the war's two sides: PvP areas, guild wars, duels and bounty flags. Only the GCW itself (the banners, ranks, bases
  and overt/covert flags) is built for exactly two sides, in about 45 C++ files.
- **Three options.**
  - **A, light:** the two GCW sides get era meanings (Triumvirate and holdouts) and seven new NPC sides get standing.
    Mostly data in our own file.
  - **B, medium:** A plus contested PvP zones, guild-war allegiances and three-team battles.
  - **C, heavy:** a true third GCW side, with weeks of C++ and an unknown client.
- **Recommendation: Option A now.** Add B's contested zones when there are enough regular players. Build C only if
  friends who have played A and B ask for a third side in the war. The owner chooses (questions at the end).

## 1. Who the sides are after Krayt's death

Checked means I read the Legends article on 16 Oct. Ours means it is our invention, and it is labelled as such in game
text.

| Side | Who they are (Legends, our summary) | Checked | Unsure, or ours |
|---|---|---|---|
| **The Triumvirate** (Galactic Federation Triumvirate) | Formed in 138 ABY from the Galactic Alliance Remnant, Fel's Empire-in-exile and the New Jedi Order, ruling from Coruscant. The three triumvirs are Admiral Gar Stazi, Jedi Master K'Kruhk and Empress Marasiah Fel; Stazi and K'Kruhk side together more often than with Fel. The Imperial Knights are its public face. It disbanded the Imperial Mission and started a communications array linking the Outer Rim to the Core, which caused friction. | "Galactic Federation Triumvirate" | How far the Alliance and the Empire merged: the article itself says the comics never settled it. |
| **Krayt's holdouts**: the One Sith and Imperial die-hards | After Krayt died on Coruscant (138), Darth Nihl ordered the One Sith to scatter, infiltrate governments and wait. In 139 ABY the gathered One Sith were destroyed at the Battle of the Floating World, and the order ended. | "One Sith", "Darth Nihl" (no death recorded), "Darth Wredd" | **Ours:** Imperial garrisons that never stood down, like Krayt's garrison on Ossus. **Unsure:** what Krayt's Moffs did after 138; the fate of his Sith troopers (the raid draft has Nihl killing them; not re-read today). |
| **Darth Wredd's insurgency** | A rogue Sith who killed his master in 138, hunted the One Sith across the galaxy to bring back the Rule of Two, lured them to their destruction, then died attacking Empress Fel (139). | "Darth Wredd" | One man and his schemes: event content, not a joinable side. |
| **The hidden Jedi** | The Order survived (K'Kruhk sits on the Triumvirate) but was gutted. Its hidden temple on Taivas was besieged in 138. On Ossus, Nei Rin and two Vong warriors kept the Jedi relics in a hidden sub-basement of the ruined temple from 130 to 137 ABY, and K'Kruhk and other Jedi hid there in 137 while Krayt's patrols searched. Our "hidden sanctuary under the ruins" is very close to canon. | "Nei Rin", "Darth Nihl" (Taivas), "Galactic Federation Triumvirate" | **Ours:** that Jedi still hide on Ossus in 138-139. In Legends they are public again under the Triumvirate; we keep them hidden there because the holdout garrison still holds the planet. |
| **The Yuuzhan Vong** | Pariahs since the war a century before. Nei Rin was the Master Shaper of the Ossus Project (terraforming with Jedi Kol Skywalker), which the One Sith sabotaged in 126-127 ABY with a fanatic shaper's help (Zenoc Quah, hidden on Wayland). Most surviving Vong of the project died; Nei Rin's three stayed loyal to the Jedi. | "Nei Rin", "Yuuzhan Vong" | **Ours:** "Nei Rin's Shapers" growing a tame voxyn line (owner, 15 Oct). **Unsure:** Zenoc Quah's fate; how many Vong live where in 138. |
| **The Hutt kajidics and cartels** | By 130 ABY the Hutts had retaken Nar Shaddaa. Under Krayt they bribed and threatened Imperial bureaucrats and watched for Jedi on the Empire's bounty lists; a Hutt owned a well-known club on Coruscant itself. Nal Hutta is the kajidics' council world (Fable S7, section 8). | "Hutt" (Legends) | **Not checked:** other cartels in 138 (Black Sun and the rest). Don't use them until checked. |
| **The Mandalorian clans** | In 127 ABY the Mand'alor, Chernan Ordo, was betrayed and killed at Botajef by Yaga Auchs, who took the title and pulled the clans out of the war. The clans hire out. | "Mandalorian" (Legends), history section | **Unsure:** who leads in 138-139; whether Hutts hire Mandalorians in this era (Fable's S7 says so; not re-checked). |
| **The Ysanna** (Ossus) | Force-sensitive descendants of the Jedi who survived the Cron Supernova. Hunters who guard the Jedi ruins and guide their concussion-bow shots with the Force; they met Luke Skywalker in the New Republic years and later hosted visiting scholars. | "Ysanna" (Legends) | **Ours:** that they are there in 138-139. Legends never shows them in the Legacy years, but a people 4,000 years on the planet is a safe extrapolation. |
| **The Chiss** (for the playable Chiss) | The Ascendancy kept its allegiance to Krayt's Empire by diplomacy. A Chiss Moff sat on the Moff Council and was suspected of sheltering Emperor Fel. | "Chiss" (Legends) | Fits a Chiss on either side. |
| **Locals and scavengers** | Knossa's survivors, relic hunters, fishers, miners. | - | **Ours.** |

## 2. How Core3 handles factions today (read-only, dev `a8ece12b`)

- **The GCW side** is a number on every creature:
  - 0 for neutral, `0xDB4ACC54` for Imperial, `0x16148850` for Rebel (`src/templates/faction/Factions.h`);
  - plus a status: on leave 0, covert 1, overt 2 (`src/server/zone/objects/player/FactionStatus.h`). Our config uses the
    pre-CU behaviour (`Core3.GCWManager.useCovertOvertSystem` defaults to false).
- **Who may attack whom** (`CreatureObjectImplementation.cpp`, `isAttackableBy`):
  1. Players first: mutual personal-enemy flags, duels, bounty flags, then grouping (which protects), then **PvP areas**
     (a region flag, `PVPAREA = 0x1000` in `managers/planet/regions.lua`), then **guild wars**.
  2. Only then the GCW: same side never; different sides only when both are overt.

  The rule compares the two side numbers, so a third side number would already count as an enemy here. The two-side
  assumption sits elsewhere.
- **NPC standing** (`managers/faction/FactionManager.cpp`):
  - The faction list is `bin/scripts/managers/faction_manager.lua`: rebel, imperial and 68 NPC factions, each with
    enemies, allies, a "players may earn it" flag and an adjust factor.
  - After the stock file, Core3 also loads **`scripts/custom_scripts/managers/faction_manager.lua`**. That file is absent
    today, and an entry in it replaces the stock entry of the same name, so new sides and relations go in our own file.
  - Killing an NPC of level L costs 2L standing with its faction and that faction's allies, and earns L with its enemies.
    The two GCW sides only move through GCW kills: NPC sides never earn war points.
- **What standing does** (`AiAgentImplementation.cpp`, `isAggressive`, and `InstallationObjectImplementation.cpp`):
  - A side's NPCs attack a player at −3,000 standing or below, and never attack at +3,000 or above. In between, the NPC's
    own aggressive flag decides. NPCs flagged to ignore standing skip this.
  - Turrets with a faction use the same thresholds.
  - Two NPCs fight when either lists the other as an enemy.
- **Lua access.** Screenplays and conversations can read and change any standing
  (`getFactionStanding`, `increaseFactionStanding`, `decreaseFactionStanding`, `setFactionStanding`) and set a
  creature's GCW side and rank. That is enough for vendors, quests and doors that check standing.
- **Ranks.** 22 ranks shared by both sides (`datatables/faction/rank.iff`, from recruit to surface marshal). A player can
  hold at most max(1,000, 20 × the next rank's cost) points.
- **The GCW manager** (`bin/scripts/managers/gcw_manager.lua`, `managers/gcw/`):
  - bases on Imperial and Rebel HQ templates only, up to 25 per planet;
  - vulnerability windows and a 300 s overt cooldown;
  - contraband crackdown scans on the ten stock planets;
  - planetary control and a racial penalty.
- **The client.**
  - `datatables/player/pvp_factions.iff` has exactly three rows: neutral, imperial and rebel.
  - Faction names come from `string/en/faction/faction_names.stf`: 78 in stock, 95 in our `local_planets.tre`.
  - The ranks table is shared.
- **How deep "two sides" goes:**
  - C++: `Factions::FACTIONIMPERIAL` in 68 lines in 26 files; `FACTIONREBEL` in 51 lines in 20 files; `isImperial()` in
    33 lines and `isRebel()` in 26; the overt and covert checks in 71 and 38 lines across 37 and 24 files.
  - Lua: 91 and 72 references.
  - Mobiles: 402 Imperial and 335 Rebel; 1,581 townspeople; 3,011 with no faction.

**What follows:** more NPC sides are a data change. A third GCW side is a broad C++ change, plus a client question
nobody has tested.

## 3. Three options

### Option A: two GCW sides, many standings (light; recommended)

**What players get:**
- **The war:** join the Triumvirate or the holdouts at a recruiter. Combatant and special-forces status, ranks, bases,
  crackdown scans and PvP all work as stock pre-CU.
- **Seven more sides:** the Jedi, the Ysanna, Nei Rin's Shapers, the relic hunters, the Hutt kajidics, the Mandalorian
  clans and the One Sith. Each shows in the character sheet's faction list. Standing earns vendors, quests and safe
  passage; bad standing makes that side's people hostile.
- **Every side has a place** on the planets we have (section 5).

**Which side is which:** the Rebel side becomes the Triumvirate, and the Imperial side becomes Krayt's holdouts.
- Stock Rebel soldiers look like the Alliance Remnant's troops.
- Stock Imperial forces look like Krayt's garrisons, and the owner's Ossus garrison is Krayt's.
- Fel's Imperial Knights can still be Triumvirate NPCs: an NPC's side does not depend on its look.
- Players who want the dark side join the holdouts.

**What Claude builds:**
- the faction data file `custom_scripts/managers/faction_manager.lua` (section 6);
- the new names in `faction_names.stf` through the archive chain;
- era recruiters on Ossus and Hoth, with lines in our own words;
- the faction strings on the new mobiles;
- the standing checks in screenplays (vendors, the sanctuary path);
- a bot check of the standing arithmetic and of the ±3,000 behaviour.

**What GPT builds:**
- the review;
- an offline check that every faction key used by a mobile or screenplay exists in both the server table and the client
  name table;
- a bot scenario that kills set NPCs and reports the standing changes;
- updates to the Hoth and Ossus acceptance checks.

**Size:** M for the data and the checks; the places' content is in the backlog.

**Risks:**
- Stock content stays in its 0 ABY dress: the Rebel and Imperial theme parks, and recruiters who talk about the Rebel
  Alliance. Relabelling the two names (question 3) helps the character sheet, not stock dialogue.
- There is no three-way PvP.
- Standing can be farmed. Kills give only L per kill and quests give fixed amounts, so tune the adjust factors.
- The stock `hutt` faction is an enemy of `imperial` in the stock table. Use new keys, not edits to stock relations.

### Option B: contested ground and hired allegiances (medium)

**Everything in A, plus:**
- **Contested zones.** A few regions carry the PvP-area flag, so anyone not grouped with you can fight you there. That
  gives real three-way and four-way fights (cartel crews, Triumvirate, holdouts, freelancers) with no new faction code.
  You opt in by walking in, and warnings appear on entry. A first candidate is the swamp outside Bilbousa. Not the Ossus
  dig: that is the garrison's PvE.
- **Guild wars for organised sides.** A cartel or Mandalorian player guild declares war on a Triumvirate guild, and
  Core3 already lets warring guilds fight.
- **A hired allegiance.** A cartel contract or a clan oath (standing plus a stored flag) with its own vendor, missions
  and a title. Pledged players stay off the GCW and fight in contested zones and battles.
- **Three-team battles.** The Battlefront-style controller (`Documentation-support/bf2-battles-and-ai-for-swg.md`) gives
  match-only teams, and it can run three.

**What Claude builds:** the region flags and a contested-zone screenplay (entry warnings, rewards), the pledge flow, a
guard that keeps brand-new characters out of zones, and the battle controller's match-only attack rules (C++, already
on C43's list).

**What GPT builds:** zone and guild-war tests with two client bots, and the report.

**Size:** M to L beyond A.

**Risks:**
- PvP zones invite griefing on a small server.
- The PvP-area and guild-war code is untested on our build.
- A pledge is a soft identity, with no overhead side marker.

### Option C: a third GCW side (heavy)

**What players get:** a third side number with its own overt and covert status, recruiters, ranks, bases, planetary
control, PvP flags and NPC aggression. For example: "the Cartels" or "the One Sith".

**What Claude builds:**
- the new side number in `Factions.h`;
- every Imperial and Rebel branch generalised (about 45 C++ files and the Lua references counted in section 2);
- recruiter and GCW manager logic for three sides;
- third HQ templates (new client object files and a new look);
- a `pvp_factions.iff` row and strings;
- **first, a client test.** The 2005 client may hard-code two sides in the executable (overhead colours, faction icons,
  attack cursors). If it does, the fix is a client-side hook (feature register F92, very high cost).

**What GPT builds:** a review of every branch and a three-way bot matrix.

**Size:** XL (weeks).

**Risks:**
- the unknown client;
- many conflict points when we merge upstream Core3;
- with a handful of friends, three sides leave sides empty;
- balance.

## 4. Recommendation

**Option A now.**
- It gives the galaxy its sides through the standing system Core3 already enforces.
- It costs a data file and the places' content, which we are building anyway.
- It keeps the pre-CU war intact for PvP.

Add B's contested zones and guild wars when the friends' playtest shows people who want to fight outside the two
sides. Hold C until players who have tried A and B ask for a third side in the war, and run the client test before
any C++.

## 5. The factions on our planets

**Hoth.**
- The stock snow soldiers become an Alliance Remnant cold-weather unit. The snowtroopers become a holdout detachment.
- **Echo Base** (our invention, to answer E1's open story): the Triumvirate has reopened the old base as a relay for its
  new communications network (Legends has such an array in 138), and holdouts want it. That makes the base the natural
  battlefield for the Battlefront-style Hoth pilot (Triumvirate against holdouts, PvE first).
- Recruiters stay at the starport only (owner, 15 Oct). No player GCW bases on Hoth for now.

**Ossus** (the accepted layout: `../Fable-ossus/o6/README.md`, `o7-build/README.md`, `inspiration.md`).
- **Krayt's garrison** on the benchland rim over the academy ruins guards the dig. Troopers are Imperial (holdout) side;
  killing them earns Triumvirate war points, as stock. A One Sith overseer (`one_sith`) runs the dig. The Sith
  interrogation post in the west cave (POI 14) leads toward the Krayt raid.
- **The hidden sanctuary** under the ruins is the Jedi (`jedi`) and Nei Rin's Shapers (`nei_rin_shapers`). It is the only
  place the rare Jedi are met. The way in is earned: Ysanna trust shows you the pilgrimage stones, and Jedi trust gets
  you past the lookout.
- **The Ysanna** (`ysanna`) live at the hunting camp, the stone circle and the sky-burial cliff. They are neutral and
  fight back. They hate relic hunters and Sith.
- **Relic hunters** (`relic_hunter`) work the canyon and the old library vaults. They are allied to the Hutt buyers, so
  helping the Ysanna costs Hutt goodwill. That is a real choice.
- **The Hutts** (`hutt_kajidic`) run the kathracite adit and the landing field.
- **The Triumvirate** is present through the crashed fighter's pilot and a small forward camp with a Rebel-side
  (Triumvirate) recruiter, which the inspiration list proposed. Its place is to be chosen when Ossus's people are
  designed.
- No player cities on Ossus (owner, 16 Oct). The two fields are for houses. No player GCW bases for now.

**Nal Hutta.** The kajidics' home is neutral ground: GCW off, as Fable's S7 first-look steps already say (no bases, no
crackdown scans, no recruiters). Standing with the Hutt kajidics opens the palace interiors, vendors (Hutt gear later)
and smuggler work, and Mandalorian clan guards stand at the kajidic seats. With Option B, the swamp outskirts become the
first contested zone.

**The playable Hutt** starts with +500 standing with the Hutt kajidics. It can join either GCW side: the Hutts bribed
Krayt's officials and now trade with the Triumvirate.

**The playable Chiss** gets no special standing; Legends has the Ascendancy courted by both Krayt and Fel, so a Chiss
fits either side.

**Stock planets** keep their stock factions and content unchanged. The new sides appear there only where our own
content puts them (for example, a Mandalorian crew for hire through the crew vendor).

## 6. Option A in data: a draft for the owner to react to

Claude finalises this when designing FW-01. The stock factions stay exactly as they are; these entries are new keys in
our own file.

| Key | Shown as | Enemies | Allies | Where | How standing moves |
|---|---|---|---|---|---|
| `one_sith` | One Sith | jedi, ysanna, nei_rin_shapers | - | Ossus garrison overseer, the Sith post, the Krayt raid | Killing their enemies' people raises it (the dark path); killing Sith lowers it |
| `jedi` | Jedi Order | one_sith | nei_rin_shapers | The Ossus sanctuary only (rare) | Killing One Sith; the Jedi path quest |
| `ysanna` | Ysanna | one_sith, relic_hunter | - | Ossus camp, stone circle, burial cliff | Killing relic hunters and Sith; the highland hunt mission |
| `nei_rin_shapers` | Nei Rin's Shapers | one_sith | jedi | The sanctuary; later the Vong fields (held) | Killing One Sith; later the voxyn line |
| `relic_hunter` | Relic Hunters | ysanna | hutt_kajidic | Imhar canyon, the library vaults | Killing Ysanna (an ugly choice); selling relics |
| `hutt_kajidic` | Hutt Kajidics | - | relic_hunter | Nal Hutta, the Ossus adit and Hutt field | Quests and trade; the Hutt starts at +500 |
| `mandalorian` | Mandalorian Clans | - | - | Kajidic guards, crews for hire, Mandalore later | Contracts |
| later: `wredd_insurgent`, `vong_fanatic` | | | | the 139 ABY event; the Vong fields | |

**Thresholds** (proposed; ±3,000 is Core3's own rule):
- 1,000: the side's vendors sell to you and its quest-givers talk.
- 3,000: its people never attack you.
- −3,000: they attack on sight.
- The sanctuary path: Ysanna 1,500 and Jedi 1,000.

None of these sides gives GCW points, and the GCW sides keep their stock rules.

## 7. Questions for the owner

Each has a recommended answer and a default. Claude does the default unless you object.

1. **Which option?** *Recommended: A now, B's zones later, C not planned.* Default: Claude designs A's data next
   (backlog FW-01).
2. **Which era side takes which GCW side?** *Recommended: Rebel = the Triumvirate, Imperial = Krayt's holdouts.*
   Default: as recommended.
3. **Relabel the names in the client** (character sheet and faction list)? *Recommended: "Rebel" becomes "Triumvirate"
   and "Imperial" stays "Imperial"; stock dialogue is untouched.* Default: in the test archive first, for your look.
4. **The seven new sides** (One Sith, Jedi Order, Ysanna, Nei Rin's Shapers, Relic Hunters, Hutt Kajidics, Mandalorian
   Clans)? *Recommended: yes; Wredd's insurgents and Vong fanatics later.* Default: these seven.
5. **The thresholds**: vendors and quests at 1,000, safe passage at 3,000, hostile at −3,000, the sanctuary path at
   Ysanna 1,500 plus Jedi 1,000? *Recommended: yes.* Default: as listed.
6. **Can the hidden Jedi be attacked?** If yes, killing one raises One Sith standing (a dark path) and costs Jedi trust.
   *Recommended: not in the first build (they withdraw into the sanctuary); a dark path later if you want one.* Default:
   not attackable.
7. **Jedi hidden on Ossus although Legends has them public under the Triumvirate**, because the holdout garrison still
   holds Ossus (ours)? *Recommended: yes.* Default: yes.
8. **The server's year**: 138 to early 139 ABY, before the One Sith's destruction at the Floating World, which becomes a
   later server event (FW-04)? *Recommended: yes, so the holdouts stay an active enemy.* Default: yes.
9. **Nal Hutta as neutral ground** (GCW off, kajidic standing instead)? *Recommended: yes.* Default: yes.
10. **Player GCW bases on Hoth and Ossus?** *Recommended: none for now; recruiters only, and the garrison is a fixed
    story site.* Default: none.
11. **Echo Base's story**: a Triumvirate relay station under holdout attack (ours), later the Hoth battlefield?
    *Recommended: yes.* Default: yes, once your Echo Base E0 look says the building works.
12. **The playable Hutt and Chiss**: Hutt +500 with the kajidics and free to join either side; Chiss no special
    standing? *Recommended: yes.* Default: yes.
13. **When Option B's contested zones come**: *Recommended: when six or more friends play regularly; the first on Nal
    Hutta's outskirts.* Default: none now.

## Sources

Wookieepedia (Legends) articles read on 16 Oct; their text is CC BY-SA and only summarised here in our own words:
- [Galactic Federation Triumvirate](https://starwars.fandom.com/wiki/Galactic_Federation_Triumvirate)
- [One Sith](https://starwars.fandom.com/wiki/One_Sith)
- [Darth Nihl](https://starwars.fandom.com/wiki/Darth_Nihl)
- [Darth Wredd](https://starwars.fandom.com/wiki/Darth_Wredd)
- [Nei Rin](https://starwars.fandom.com/wiki/Nei_Rin)
- [Yuuzhan Vong](https://starwars.fandom.com/wiki/Yuuzhan_Vong)
- [Hutt (Legends)](https://starwars.fandom.com/wiki/Hutt/Legends)
- [Mandalorian (Legends)](https://starwars.fandom.com/wiki/Mandalorian/Legends)
- [Ysanna (Legends)](https://starwars.fandom.com/wiki/Ysanna/Legends)
- [Chiss (Legends)](https://starwars.fandom.com/wiki/Chiss/Legends)

Our own notes: `Documentation-support/legends-timeline-njo-legacy.md`, `Documentation-support/krayt-raid-design.md`,
`Documentation-support/starcraft-inspiration-vong-gree.md`, `Documentation-support/bf2-battles-and-ai-for-swg.md`,
`Fable-species/s7-hutt/README.md` (sections 1 and 8), and the Ossus files above.

Core3 (read-only, dev `a8ece12b`):
- `bin/scripts/managers/faction_manager.lua`, `bin/scripts/managers/gcw_manager.lua`,
  `bin/scripts/managers/planet/regions.lua`;
- in `src/server/zone/`: `managers/faction/`, `objects/creature/CreatureObjectImplementation.cpp`,
  `objects/creature/ai/AiAgentImplementation.cpp`, `objects/installation/InstallationObjectImplementation.cpp`,
  `objects/player/LuaPlayerObject.cpp`, `objects/player/FactionStatus.h`;
- `src/templates/faction/Factions.h`.

No SWG Legends or SWG Restoration server pages were used.
