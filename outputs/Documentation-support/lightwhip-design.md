# Light whip: design and build plan

18 October 2026, Claude. Design only: nothing built, installed or tested.

## Owner decisions (decision card, about 7:00 PM)

- **Route:** the real bending whip, through the graphics hook (the O15 effects layer), not only a stiff blade or a lash effect.
- **Users:** Jedi, as a saber. It is a one-handed saber template, so Jedi skills, Force cost and crystals apply, including the ghostfire crystal through the O14 shader.
- **Source:** loot plus schematic. A rare drop (a schematic or a broken whip) that a crafter finishes.
- **Stats:** reach and the lore's trade-offs, and whip attacks partly slip past parries (a small C++ change).

## Lore (Wookieepedia, Legends: [Lightwhip](https://starwars.fandom.com/wiki/Lightwhip/Legends))

In our words: a rare lightsaber variant with several small crystals instead of one. Its flexible blade is several metres long, so it reaches further and can bend around a parry. It is weaker against armour, poor for blocking and hard to control. Nightsisters, Sith and Dark Jedi used it, Lumiya most famously. Post-NGE SWG showed it only on a loading screen. Write our own item text.

## What the client has (read-only probe, 18 Oct)

- **No light whip model, template or blade.** The only file is the loading screen `texture/loading/large/large_load_nightsister_lightwhip.dds`, in `mtg_patch_015.tre` (MTG rights rules apply).
- **A blade is straight.** A `.lsb` (LSAT form) holds one hilt appearance (BASE), one blade (BLAD: SHDR, LGTH, WDTH, OPEN, CLOS) and the idle sound. Double blades (`wp_mle_lightsaber_blade_2horgen6.lsb`) have the same fields.
- **The blade draws with** `effect/e_h_lightsaberblade.eft`: vertex program `a_nolighting.vsh` (shared with many effects, so not ours to change) and pixel program `e_h_lightsaberblade_ps20.psh` (replaced by O14).
- **No weapon has bones** (no `appearance/wp_*.sat`), and players have no whip attack animations. The only whip animations are `all_b_cbt_pistol_whip.ans` and creature tail-whips. There are 61 one-handed sword standing animations to reuse.
- MTG has a static whip mesh (`appearance/item_whip.apt`) and belt whips (`belt_whip_*.sat`). Reusing them needs a rights check. A stock saber hilt is fine for the prototype.

## How the bending whip works

1. **The whip blade can be told apart.** The whip's blade shaders point to their own effect, with its own pixel program (a copy of the O14 blade program). The hook knows that program's id, the way `blade_ids.h` lists the blade programs now. Stock sabers keep theirs.
2. **The hook replaces the straight draw.** On a whip blade draw, the hook reads the blade's base and tip from the game's vertices and the vertex program's matrix constants. It moves a rope of about 16 to 24 segments, pinned at the hilt, with the tip pulled towards where the straight blade points, plus lag and damping, so the strand trails the swing and snaps at the end. It draws a camera-facing strip along the rope with the game's own pixel program, textures and depth test, and skips the original straight draw.
3. **Several whips on screen.** Each whip is matched to its rope from the last frame by the nearest hilt position.
4. **Fallback.** Without the DLL, players see the stiff whip: a long, thin straight blade with its own long trail. So the stiff whip gets built first anyway.

## Steps

0. **Capture (needs the O15 hook installed and the owner in game).** Add a log option for blade draws: draw kind, primitive type, vertex count, stride, the first vertices and vertex constants c0 to c11. The owner swings a stock saber for a few seconds. This shows whether the blade's two ends can be recovered every frame. If they can't, stop and rethink before building step 3.
1. **Base (no game needed to build).** The archive gets a whip hilt template (a stock hilt for now), a long, thin `.lsb` blade with its own blade shaders and pixel program, and its own swoosh trail row. The server Lua gets a one-handed saber template with longer range, lower damage against armour and weaker blocking, plus the loot item and schematic. Built, not installed; then the test galaxy.
2. **Parry slip (dev C++, `CombatManager.cpp`).** Whip attacks partly ignore the target's parry and block. First check which Core3 defence rolls apply to melee against a Jedi, then agree the number with the owner.
3. **Hook effect.** The rope strip from "How it works", as one more effect in the O15 effects layer (`Fable-ossus/o15-mirage/DESIGN.md`), after the mirage works in game.
4. **Art and placement.** An original hilt and crack sound (no film sounds), a Nightsister loot entry on Dathomir and the schematic's resources.

## Open questions

- How the blade's geometry reaches the GPU (step 0).
- Whether a saber's range can go past the stock melee range without other checks in the combat queue rejecting it.
- Who owns the O15 files when step 3 starts: the session that built the mirage, or a hand-over.
