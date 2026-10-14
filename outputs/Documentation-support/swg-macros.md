# SWG client macros (pre-CU): how they work, plus owner macros

Researched 13 Oct 2026 (Claude) for the owner. Sources: [SWG Wiki: Macro](https://swg.fandom.com/wiki/Macro), [SWG Wiki: Crafting macros](https://swg.fandom.com/wiki/Crafting_macros), [The Ultimate Crafting Macro (scrapbook copy)](https://swg-piloten.com/Scrapbook/UltimateCraftingMacro/). These are community guides from the live-game era. Their details are not checked against our SWGEmu client except where marked.

## Rules

- **Create:** Command Browser → **Macro** tab → **New Macro**. Enter a name, pick an icon, type the commands, then press OK. Macros are saved per character.
- **Name:** one word. Our client rejects spaces with "Macro names cannot contain spaces" (seen by the owner, 13 Oct). The name is also how it's called: `/macro Name`, and a macro loops by calling itself as its last line.
- **Commands:** one slash command per line, ending in `;`, exactly as typed in chat. Case matters for some commands.
- **`/pause n;`:** waits n seconds; decimals are allowed. Short pauses between commands guard against lag misfires.
- **Run:** double-click the icon in the Command Browser, drag it to a toolbar slot, or type `/macro Name`. **`/dump`** stops a running or looping macro.
- **Length limit:** text beyond the limit is cut off at the next login. The guides don't give the exact number.
- **Copy and paste:** one guide says it had to be enabled in the old client; the setting wasn't found for ours. If Ctrl+V does nothing, type the macro in.

## Owner macro: SR Combat Pistol materials (`SRPistolMats`)

Ingredients come from the server schematic `object/draft_schematic/weapon/pistol_blaster_short_range_combat.lua`:

- steel_neutronium ×45, iron_plumbum ×20, metal ×10;
- blaster power handler ×2, which must be identical;
- blaster pistol barrel ×1;
- weapon scope ×1 (optional).

Neutronium Steel also fills the Metal slot.

**One-time setup (done 13 Oct):** `/resource perfect steel_neutronium` and `/resource perfect iron_plumbum` created **Sloviboiam** (Neutronium Steel) and **Galiium** (Plumbum Iron), all stats 1000, on the live galaxy. `createresource` needs these spawn names, not the type names. To find a name later, use `/resource find <type> res_quality gt 999`, or run `/resource dump` and search `scripts/managers/resource_manager_spawns.lua`. Running `perfect` again makes another new spawn.

```
/object createresource Sloviboiam 55;
/pause 1;
/object createresource Galiium 20;
/pause 1;
/object createitem object/tangible/component/weapon/blaster_power_handler.iff 2;
/pause 1;
/object createitem object/tangible/component/weapon/blaster_pistol_barrel.iff;
/pause 1;
/object createitem object/tangible/component/weapon/scope_weapon.iff;
```

- **Power handlers:** `createitem … 2` makes one stack of two, which suits the "identical" slot (`/object` source: `ObjectCommand.h`, quantity 1–100 becomes the use count).
- **Crafting window:** it may need Back and reopen before it lists new inventory items.
- **Status:** the three `createitem` lines are verified on live (server log, 13 Oct). The two `createresource` lines with these names are not yet confirmed.

## Gathering and support macros (13 Oct, for the owner's characters)

Command names come from our server source, and the bots use the same commands (`tools/bots/scenarios/besh-gather.py`, `aurek-boss-camp.py`). The loop pattern and pause lengths follow community guides: a macro loops by calling itself; flourish loops are a common entertainer macro; a 2007 forum sampling loop paused for minutes between samples ([entertainer guide, 2008 archive](https://www.swgemu.com/archive/scrapbookv51/data/20080108200838/entertain_guide.html); [SWGR macro rules](https://swgr.org/wiki/macro-protection)). SWGR's macro-dump rules are their server's; ours has none set. **None of these has been tried in our client yet.** Stop any loop with `/dump`.

| Macro | Text | Use |
|---|---|---|
| `SampleLoop` | `/requestCoreSample Bapaium; /pause 30; /macro SampleLoop;` | Change the name to the resource you surveyed (survey window). Kneels and samples; stand up with `/stand` when done. |
| `ForageLoop` | `/forage; /pause 15; /macro ForageLoop;` | Scouts. A fresh Novice Scout lacks the forage ability (the bots found this), so train first. |
| `HarvestAll` | `/harvestcorpse meat; /pause 1; /harvestcorpse hide; /pause 1; /harvestcorpse bone;` | Target a fresh corpse first. Scouts. |
| `DanceLoop` | `/flourish 1; /pause 10; /flourish 2; /pause 10; /macro DanceLoop;` | Start dancing first with `/startdance basic`; `/stopdance` ends it. |
| `DocBuff` | `/healenhance health; /pause 3; /healenhance action; /pause 3; /healenhance strength; /pause 3; /healenhance constitution; /pause 3; /healenhance quickness; /pause 3; /healenhance stamina;` | Doctors. Target the patient first; needs the matching enhancement packs in the inventory. |
| `StimTarget` | `/healdamage; /pause 4; /macro StimTarget;` | Medics. Target the patient (or yourself); needs stimpacks. |

In the macro window, put each command on its own line. They're shown on one line here to keep the table short.
