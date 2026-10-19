# Light whip: design and build plan

18 October 2026, Claude. Design only: nothing built, installed or tested.

## Owner decisions (decision card, about 7:00 PM)

- **Route:** the real bending whip, through the graphics hook (the O15 effects layer), not only a stiff blade or a lash effect.
- **Users:** Jedi, as a saber. It is a one-handed saber template, so Jedi skills, Force cost and crystals apply, including the ghostfire crystal through the O14 shader.
- **Source:** loot plus schematic. A rare drop (a schematic or a broken whip) that a crafter finishes.
  - **Owner, about 8:20 PM: bosses only**, chosen over Dathomir Nightsisters and over not yet. Each kill of a world-rotation boss has a 5% chance to give one player who damaged it a roll of the whip group (schematic 80%, whip 20%). Patch built, not applied: `Lightwhip/server/lightwhip-boss-drop-dev.patch`.
- **Stats:** reach and the lore's trade-offs, and whip attacks partly slip past parries (a small C++ change).
- **Owner's answers, 8:26 PM:**
  - The leather hilt for now, a shorter strand (now 2.1 m), and no trail without a specific crystal (now no visible native trail; the ghostfire crystal still brings its ribbons).
  - Drop: "Krayt dragons for now, the boss", so the two rotation krayts at 10% per kill.
  - Schematic: "Master weaponsmith +saber crafting 1 or 2 or jedi master". As skills (client `skills.iff`): (`crafting_weaponsmith_master` and `force_discipline_light_saber_technique_01`, Lightsaber Technique I, which gives `jedi_saber_assembly`; Technique II needs I) or `force_title_jedi_master`. A loot schematic takes one `requiredSkill` (`LootSchematicMenuComponent.cpp:35`), so the OR needs a small Lua menu component that checks the skills and calls `addRewardedSchematic` (bound in `LuaPlayerObject.cpp:37`). Owner's pick: "Smith + Tech I, or LS Master", so the last part is `force_discipline_light_saber_master` rather than the Jedi Master title. It is wired as `LightwhipSchematicMenuComponent` in the drop patch, built, not applied.
  - Archive `23368576` (2.1 m, no native trail, on O14 `4c5a29d0`) was installed at 8:35 PM by the main session, with the owner's OK.
- **Looks (owner, about 7:35 PM, after the first look):** "keep as built". The crystal decides the colour, and the ghostfire crystal gives the near-invisible ghostfire blade.
- **Scope (owner, about 8:20 PM, then 8:3x PM):** first, "step 2 and the bosses-only drop now; bend and art after the reset". Then: "can we wait on the parry thing in favor of the bend?"
  - So now: the bosses-only drop, and the bend (steps 0 and 3), which goes to the mirage session because it owns the O15 hook.
  - Step 2 and the art (step 4) wait until after the 22 Oct reset.

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
   - **Installed 18 Oct 8:41 PM, with `log_draws=600`:** O15 proxy `5582152a` (built 8:36 PM). `Fable-ossus/o15-mirage/capture_read.py` reads its log. Its `log_draws` setting (off by default) writes `SWG-client/mirage-draws-<pid>.log`. To run it:
     1. With the client closed, swap the proxy in and add `log_draws=600` to `mirage.ini`.
     2. In game, swing a stock saber for a few seconds, then the whip, pressing Ctrl+Shift+L while swinging.

     The details, and what step 3 needs from the log, are in [O15 DESIGN.md](../Fable-ossus/o15-mirage/DESIGN.md), under "The light whip's bend".
   - **Result, 8:50 PM (`capture_read.py` on both clients' logs, 8:43 to 8:50 PM): the ends can be recovered every frame.**
     - **The draws.** Each blade draws once per frame as a 4-vertex triangle fan, plus a 2-vertex line list over one edge. Both use vertex program `5e68b930`.
     - **The quad, in object space:** x is plus or minus half the width (0.15 for the saber, 0.09 for the whip), y is 0, and z runs from 0 at the base to the current length at the tip. Vertex 0 is always at the tip.
     - **Off or igniting.** A blade that is off or still igniting draws with length 0. The saber grows over about 24 frames; the whip appears at full length at once.
     - **World positions.** c4 to c7 are packed column-major (world.x = dot(p, c4)). Base = object (0, 0, 0), tip = object (0, 0, length).
     - **Scale.** The object-to-world scale is 0.817 (the character's scale), so the whip's 2.1 m is 1.72 m in the world and the saber's 1.2 m is 0.98 m.
     - **Tracks.** Tracked by the nearest base, every blade had a quad in every frame. The exceptions were 3 frames in 211 (the saber) and 0 in 142 (the whip).
     - **Speeds.** During swings the base moved up to 7 m/s and the whip's tip up to 48 m/s, so the rope needs sub-steps.
   - **The constants.** `a_nolighting.vsh` includes `vertex_shader_constants.inc`, which sets c0 to c3 as object to clip, c4 to c7 as object to world and c8 as the camera position. So the vertices plus c4 to c7 should give the blade's two ends in world space. The game draws the blade with `DrawPrimitive`, twice a frame (O15 `mirage.log`, 8:11 PM).
1. **Base (no game needed to build).** The archive gets a whip hilt template (a stock hilt for now), a long, thin `.lsb` blade with its own blade shaders and pixel program, and its own swoosh trail row. The server Lua gets a one-handed saber template with longer range, lower damage against armour and weaker blocking, plus the loot item and schematic. Built, not installed; then the test galaxy.
   - **On the test galaxy since 18 Oct 7:42 PM (run 37):** archive `a2610d64` on O14 `feb3bf84`. Built first at 7:25 PM as `d424d2f6` on O14, plus a Lua patch for dev. What's in it, the install steps and the test questions are in [Lightwhip/README.md](../Lightwhip/README.md). The blocking penalty isn't in it, because `saber_block` is the wielder's skill mod, not the weapon's, so it moved to step 2.
2. **Parry slip and weaker blocking (dev C++, `CombatManager.cpp`).** Whip attacks partly ignore the target's parry and block, and a Jedi holding a whip blocks less well. First check which Core3 defence rolls apply to melee against a Jedi, then agree the number with the owner.
   - **What Core3 rolls** (`CombatManager.cpp` `getHitChance`, `CombatManager.h:282`):
     - **Roll 1 (to hit).** Accuracy against the target's defence: its level plus the attacking weapon's defence mods (`melee_defense` for the whip), capped at 125, plus private, group and food bonuses.
     - **Roll 2 (after a hit; never for Force attacks).** It is decided by the target's own weapon.
       - If the target holds any saber, it takes the ricochet path: `saber_block` applies only to ranged and heavy attacks, so a melee hit, the whip included, gets no second roll.
       - Otherwise one-handed melee and pistols give dodge, two-handed and carbines give counter, and polearms and rifles give block. The chance comes from level plus the target's weapon's secondary mods (capped at 125), plus center of being and posture.
     - So against a saber-holding Jedi the only parry-like defence is roll 1's `melee_defense`. The whip's "weaker blocking" means its holder's `saber_block` against ranged shots.
   - **On hold until after the 22 Oct reset** (owner, 8:3x PM: "can we wait on the parry thing in favor of the bend?"). No C++ was written. The options stand for then.
   - **Options sent to the owner (8:27 PM):**
     - **A:** ignore 25% of roll 2; holder −25% `saber_block`.
     - **B (recommended):** ignore 50% of roll 2 and 10% of the target's `melee_defense` in roll 1, so it also works on saber Jedi; holder −33% `saber_block`.
     - **C:** skip roll 2 and ignore 20% of `melee_defense`; holder −50% `saber_block`.
     - The whip is recognised by its server template CRC. The patch must sit on the dev working tree, because `CombatManager.cpp` has the ghostfire session's uncommitted edits.
3. **Hook effect.** The rope strip from "How it works", as one more effect in the O15 effects layer (`Fable-ossus/o15-mirage/DESIGN.md`), after the mirage works in game. Owner, 8:3x PM: the bend comes before the parry slip. Steps 0 and 3 belong to the mirage session, which owns the O15 hook. The whip's blade program id is `238eb66a` (archive `a2610d64`), and the blade is 2.5 m by 0.09 m on the leather hilt, with `tr1e` at 2.425 m.
4. **Art.** An original hilt and crack sound (no film sounds). Waits for the 22 Oct reset. Placement is settled: bosses only (see Owner decisions).

## Open questions

- How the blade's geometry reaches the GPU (step 0).
- Whether a saber's range can go past the stock melee range without other checks in the combat queue rejecting it.
- Who owns the O15 files when step 3 starts: the O15 mirage session. Its plan for step 3 is in O15 DESIGN.md: the strip goes back into the blade's object space and is drawn with the game's own vertex program and state, and only `238eb66a` is replaced.
