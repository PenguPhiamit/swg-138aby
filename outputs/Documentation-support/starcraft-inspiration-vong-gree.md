# StarCraft as inspiration for the Vong, the Gree and Legends oddities (Claude, 15 Oct 2026)

Owner: "check out starcraft 1 and 2 and the custom assets that exist for them for inspiration on the Vong, gree, and maybe other potential things like star weirds or other crazy legends things"; "we need the legal checks".

## Owner's direction (15 Oct, after reading this)

"no lets wait, lets just use for art insporation and do what we can. the zerg had features i think would work well enough as a starting point. and the protoss for the celestial stuff."

- **No prototype yet.** The damutek dungeon and the other mechanics below are ideas on file, not tasks.
- **Art inspiration only**, made our own way: our models through the pipeline, CC0 kitbashing, and recolours of SWG's own assets.
- **Zerg → the Vong look, as a starting point.** Keep:
  - chitin and carapace plates with segmented joints;
  - bone spikes and claws, sinew and membrane between plates;
  - glowing sacs and veins;
  - organic spires and grown structures;
  - ground that looks overgrown by living tissue.
  
  Make it Vong, not Zerg: yorik coral and vonduun-crab textures, ritual scars and tattoos on the Vong themselves, and coral greys, deep reds and bone in place of the Zerg purple-brown. Don't copy any one Zerg unit's silhouette.
- **Protoss → the Celestials.** These are the Legends Celestials (the Architects behind ancient megastructures such as Centerpoint Station). Keep:
  - gold and teal plating;
  - floating crystals and hovering geometry;
  - obelisks and pylon-like power stones;
  - glowing glyph lines;
  - serene, monumental shrines.
  
  This is for Celestial ruins and relics, and Gree tech can borrow from the same lane. Again, no Protoss silhouettes one-to-one.

## Legal check first: ideas yes, files no

| What | Verdict | Why |
|---|---|---|
| StarCraft 1/2 game files (models, textures, sprites, sounds, music) | **No** | Blizzard's copyright; no licence for use outside their games. AGENTS.md (Ethics check 1): stock game files are excluded unless the rights holder allows it, and owning the game doesn't change that. Blizzard has taken down fan projects that copied its art (an HTML5 StarCraft remake, 2015). |
| Fan assets made for StarCraft (SC2Mapster, CurseForge SC2 assets, Hive Workshop, Brood War sprite mods) | **No, by default** | Most are edits of Blizzard's art, and an author's permission covers only their own contribution (AGENTS.md). Blizzard's editor and custom-game terms are reported to assign custom-game content to Blizzard; that is confirmed for Warcraft III Reforged and reported for SC2 (not confirmed against the current SC2 text). Even "use my models freely" packs credit Activision Blizzard and forbid commercial use. A fully original model whose author explicitly allows use in other games would still need the owner's OK and the full record (release, files, hashes, licence, credit) before import. |
| Screenshots or art from StarCraft for a private mood board | **Private only** | Fine to look at; don't commit them to the repo or push them (copyright). |
| Ideas, mechanics, genre conventions (organic bio-tech, hive structures, ancient-ruin tech, shields, spreading terrain) | **Yes** | Ideas and mechanics aren't protected; specific expressions are. Don't copy a distinctive unit silhouette, name, icon or exact ability one-to-one. Write our own versions in Star Wars terms. |
| The Star Wars side (Vong, Gree, Starweird) | Same status as all our content | Lucasfilm IP, used the way the whole SWG emulator project uses it: noncommercial fan work. Book and comic art (e.g. the Starweird illustration in *Ultimate Adversaries*, 2004) is a description reference only. |

**How the art gets made instead:** our own models through Fable's pipeline (first model worked in the client today, `67c7c62`), CC0 packs (Quaternius and similar) kitbashed into new shapes, and recolours of SWG's own creatures and props in our test archive.

## Ideas worth taking, in Star Wars terms

### Yuuzhan Vong (fits the voxyn decision: Nei Rin's Shapers, 138 ABY)
The Zerg are the closest genre cousin, but the Vong are a culture with castes and pain-faith, not a mindless swarm. Take the mechanics, not the look.
- **Spreading terrain → worldshaping zones.** Coral and yorik-kul growth spreads from "shaper nodes" over days. Players hold it back by destroying nodes, which makes it a server event with a visible map change.
- **Living buildings → a damutek dungeon.** Grown, not built: a Shaper habitat with coral corridors (indoor floor mesh, our navmap tools). This is the home of the voxyn breeding line, with egg sacs, cocoons and a Shaper boss who shapes adds mid-fight.
- **Infested soldiers → coral-implanted prisoners.** Our Ossus notes already have Krayt seeding prisoners with coral in 137 ABY. They become enemies around Krayt's Ossus garrison.
- **Living gear** as loot and crafting: vonduun crab armour, amphistaff, thud bugs (a thrown stun), razor bugs, blorash jelly (a root, like SC2's fungal growth), villips (a comms item).
- **Raid boss: yammosk with dovin basals.** Basals pull players in (like SC2's abduct) and swallow projectiles (a shield phase). This fits the coral raid already in the era notes.

### Gree (ancient tech masters who no longer understand their own machines)
Protoss and Xel'Naga ruins are the reference: old, beautiful, half-working technology.
- **Watchtowers → Gree sensor obelisks.** Activate one to reveal an area on the planetary map.
- **Power fields and warp-in → attunement.** Gree devices only work near a powered relay or with a Gree key-rod. A relic quest chain gathers rods, and the "puzzles" are colour and tone sequences, since Gree speech is colour and tone.
- **Shields → constructs with regenerating shields** that only break to one damage type at a time. SWG's eight damage types make this a natural mechanic.
- **Stasis wards → stasis traps** in Gree ruins, using SWG's own states (stun, dizzy).
- **Look:** smooth, chromatic, colour-shifting machines. That suits recolours and CC0 kitbashing, without copying Protoss shapes.

### Starweird and other Legends oddities
- **Starweird.** A creature from the 2004 sourcebook *Ultimate Adversaries*; a Starweird Queen is mentioned in TOR. Legends gives it the Force; canon (*Doctor Aphra* #34, 2023) gives it gravity powers. Inspiration: SC2's void and hybrid enemies. It could be a rare deep-space or hyperspace-anomaly encounter (a JTL space event later), or an "anomaly" world event with fear and mind effects and gravity knockdowns.
- **Killiks:** the most Zerg-like thing in Legends, an insect hive mind with "Joiners" absorbed into the hive (Dark Nest era, still around in 138 ABY). A hive dungeon where long exposure gives a stacking "joining" debuff.
- **Others to research before use:** Abeloth (a Legacy-adjacent horror), the Mnggal-Mnggal (a gelatinous mind). Check each against Wookieepedia before writing content; nothing here was verified past the Starweird.

## Next steps (owner's choice)
1. Pick one to prototype: the damutek dungeon (Vong) is the best fit with the voxyn line, the coral raid and the Ossus garrison.
2. Lore checks for the picked one go to ChatGPT's research lane (cheaper than Claude), with the Starweird, Killik and Abeloth facts verified on Wookieepedia.
3. Art through our own pipeline and CC0 kitbashing; no StarCraft or StarCraft-mod files at any step.

## Sources
- [PC Gamer: Blizzard's claim that it owns Warcraft 3 mods](https://www.pcgamer.com/au/blizzards-claim-that-it-owns-warcraft-3-mods-isnt-just-the-standard-fine-print), which also notes the same policy for SC2 custom games
- [TechSpot: Blizzard now owns the copyright to custom Warcraft 3: Reforged content](https://www.techspot.com/community/topics/blizzard-now-owns-the-copyright-to-all-of-your-custom-warcraft-3-reforged-content.260232/)
- [Hive Workshop thread on SC2 custom content ownership](https://www.hiveworkshop.com/threads/so-why-arent-you-working-on-a-starcraft-2-custom-campaign-username.349880) (a user's reading, not official)
- [CurseForge: an SC2 asset pack's terms (credits Activision Blizzard, no commercial use)](https://www.curseforge.com/sc2/assets/baiwuchangs-assets)
- [Blizzard Video Policy](https://www.blizzard.com/en-us/legal/dd76b654-f2c4-4aaa-ba49-ca3122de2376/blizzard-video-policy) (noncommercial use of Blizzard content in videos only)
- [Ubergizmo: Blizzard takes down a fan-made HTML5 StarCraft](https://ubergizmo.com/2015/10/blizzard-takes-down-html5-starcraft/amp)
- [Starweird (fan wiki)](https://starwars.archivum.wiki/article/starweird) and [Canaltech on its return in canon](https://canaltech.com.br/quadrinhos/star-wars-traz-monstro-esquecido-de-volta-a-continuidade-oficial-258074/)

Not legal advice. The current SC2 EULA text was not retrieved: confirm on Blizzard's legal pages before relying on the exact wording. The verdicts above don't depend on it, because our own rules already exclude these files.
