# Krayt raid: design draft (Claude, 15 Oct 2026). Paper only, for the owner to mark up

Owner's brief (14–15 Oct):
- around 138–139 ABY, "make krayt a raid boss";
- the main boss is one of his successors (e.g. Darth Nihl);
- plus a Krayt "echo" or Sith-spirit **secret boss**, locked behind a loot requirement in the same raid;
- yorik coral is its own resource class, used for decor, weapons, armour, ships, and maybe pets.

Lore from Wookieepedia (Legends), in our own words:
- Krayt died for good on Coruscant in 138 ABY.
- Nihl then took command, had Krayt's Sith troopers killed (without Krayt they went mad), and ordered the One Sith into
  hiding: scatter, infiltrate governments, strike from the shadows.
- The Galactic Federation Triumvirate (Stazi, K'Kruhk, Empress Marasiah Fel) then held the known galaxy.
- In 139 ABY, Darth Wredd hunted his fellow Sith, and a gathered army of One Sith infiltrators was destroyed at the
  Floating World.
- Krayt's Vong implants (yorik-kul) grew a bony exoskeleton he wore as armour. In 137 his empty armour was found in
  the Stasis Room on Korriban.
- The Krayt "echo" itself is **our invention**. Legends has no Krayt ghost.

Sources:
- https://starwars.fandom.com/wiki/Darth_Nihl
- https://starwars.fandom.com/wiki/Darth_Krayt
- https://starwars.fandom.com/wiki/One_Sith
- https://starwars.fandom.com/wiki/Darth_Wredd
- https://starwars.fandom.com/wiki/Galactic_Federation_Triumvirate

## 1. The pitch

**"Nihl's Hold."** In 139 ABY the One Sith are hunted on two fronts, by the Triumvirate and by Wredd. Darth Nihl gathers what's left of his order at a hidden stronghold. The players find it and take it apart.
- **Main boss:** Nihl himself.
- **Secret boss:** the stronghold also holds the one thing Nihl never let go of, the Stasis Vault with Krayt's empty coral armour. With the right relic the vault opens, and the armour wakes as the **Echo of Krayt**: the dark side clinging to the shell his body grew. It is not a resurrection; we write that in the boss's examine text.

## 2. Where it lives (owner to pick)

| option | for | against |
|---|---|---|
| **A. A derelict Dragon ship** (Krayt's warships, revealed in 138), reached by a shuttle from Ossus or Dathomir; the interior is an instance | lore-exact; one boarding point; an instance keeps raids from clashing | needs an interior: the Corellian corvette instance (`dungeon1`) is the stock model to copy, and its art is reusable for a first pass |
| B. A Sith tomb complex on Korriban | Krayt's Stasis Room is canon here | we don't have Korriban yet (it's a census candidate) |
| C. A hidden One Sith bunker on Ossus, below the ruined academy | Ossus is ours and in the story (130, 137 ABY) | Ossus is the Jedi world, and the Sith left it after 137 |

Recommendation: A, with C as the interim location while the Dragon ship interior is built.

## 3. Encounters

| stage | what | lore | SWG mechanics (pre-CU) |
|---|---|---|---|
| Trash 1 | **Maddened Sith troopers**, Krayt's survivors | canon: went mad after his death | stock stormtrooper bodies with a dark retexture or hue; high damage, low defence, flee at low health ("broken") |
| Trash 2 | **One Sith acolytes and warriors** | the local model's Ossus NPC drafts (15 Oct) | dark-adept and dark-Jedi templates, Force attacks, they assist each other |
| Mini-boss | **a Sith Lord lieutenant** (Darth Havok or another of Nihl's inner circle; check fates before naming) | Nihl's circle | a world-boss-style template, lightsaber plus Force lightning; calls adds at 50% |
| Main boss | **Darth Nihl** (Nagai warlord, Krayt's former Hand) | canon leader in 138–139 | high HAM; lightsaber specials; Force choke as a single-target stun and DoT; at 66% and 33% summons an acolyte wave; at 25% "Hide the fleet": he tries to flee to a second room, and the raid must stop him (an interrupt by killing a channelling acolyte) |
| **Secret** | **Echo of Krayt** | our invention, built on the canon armour | spawns only when a raid member uses a **Stasis Vault Key** on the vault console after Nihl dies |

**The Echo of Krayt fight:**
- *Yorik-kul seeds*: a disease DoT that spreads to nearby players. Pre-CU has disease DoTs; cured by Doctors.
- *Coral shell*: very high armour until the shell is "cracked" by attacks of one damage type. A puzzle for mixed raids.
- *Force storm*: area damage around the boss.
- *Echoes of the Hand*: spectral Sith adds (hued and translucent stock bodies).
- At 0 HP the armour collapses and stays as a lootable shell.

## 4. The secret-boss key (the owner's "loot requirement")

- **Stasis Vault Key** (or "Krayt's Seal"): assembled from three **Vault Seal Fragments**, which drop in the same raid run:
  - one from the mini-boss;
  - one from Nihl;
  - one from a rare trash spawn (a "Sith archivist").
- Combining them is a radial on any fragment when all three are in one inventory. Fragments are no-trade, so the raid must earn it together.
- Alternative (simpler to build): Nihl has a 1-in-N drop of the whole key. That's less teamwork and more luck. Owner's choice.
- Lockout: the vault opens once per raid instance or per server day.

## 5. Loot (ties into the coral and beskar decisions)

- **Nihl:** One Sith robes, a Nagai warlord's lightsaber crystal (colour), Sith holocron decor, Vault Seal Fragment.
- **Echo of Krayt:**
  - **Krayt's Coral Plate**: yorik coral loot, the first source of the new class (option A) until coral spawns exist;
  - a schematic for **Coral-Grown Armour** (Armorsmith), using the coral class;
  - **Krayt's Mask**: a decor or wearable trophy;
  - a rare **Shell of the Dark Lord**: a house trophy, the armour as a statue.
- **Beskar:** not from this raid, which keeps it Mandalorian. It belongs in a later Mandalorian content line.
- **Badges:** "Nihl's Downfall", "Echo Silenced".

## 6. Build pieces and who could do them

1. NPC templates:
   - Sith troopers, the lieutenant, Nihl and the Echo;
   - acolytes and warriors from the local model's drafts.
   The local model can draft them from stock bases with a brief; Claude reviews.
2. A screenplay for the fight logic: phases, adds, the flee interrupt, the vault console and key assembly. ChatGPT, in its worktree; Claude reviews and builds.
3. Loot groups and items: the fragments, the key, the coral plate, robes. Some need client object templates; stock look-alikes first.
4. Location: option C first (bunker on Ossus, stock interior), then A.
5. The yorik coral class in the resource tree (root-level branch, `Fable-resources3/lore/ossus-resource-map.md` §6) and the coral armour schematic.
6. Testing: bots fight trash and the bosses on the test galaxy (needs the class-check work: Doctors curing the disease DoT, mixed damage types).

## 7. Questions for the owner

1. Location: A (Dragon ship), B (wait for Korriban) or C (Ossus bunker) first?
2. Key: three fragments from the same run, or one rare drop from Nihl?
3. Raid size: pre-CU-style open-world (any number, e.g. 20+) or a capped instance (e.g. 8–12)?
4. Should the Echo fight lean on mixed professions (Doctors curing, a specific damage type to crack the shell), or stay a pure damage race?
5. Is Darth Wredd (139 ABY, anti-One Sith) worth a later raid of his own, with Nihl's Hold as the first?
