# Benny: Creature Handler + Rifleman + Marksman, macros and gear (Claude, 15 Oct 2026)

The owner's play-data character (Master Creature Handler, Rifleman, Marksman: 246 points). Every command below was checked against the server's command table: all have a real handler on our server. Pets tank; Benny shoots from range; the Forn crew escorts (`tools/bots/escort.py`).

## Skills first (admin): target yourself

`/grantSkill` needs a target (`GrantSkillCommand.h`: no target gives "invalid target" and grants nothing). Click your
own character, then:
```
/grantSkill outdoors_creaturehandler_master
/grantSkill combat_rifleman_master
/grantSkill combat_marksman_master
```
Each answers "Granted skill". "Failed to grant skill" means the 250-point cap: the starting profession's boxes use the
points, so `/surrenderSkill <profession>_novice` and repeat. Gear before skills gives errors (no rifle certification).

## Server-best gear as two macros (owner: "make me a macro for server bests of the gear i need")

Picked from the item templates (15 Oct), because `/object createitem` gives an item its template's base stats; crafted
items with good resources can beat these.
- **Rifle: T21.** Ties the Berserker rifle for the best rifle damage (38 per second at base) and has **heavy armour
  piercing**; the flame thrower and lightning rifle hit harder but need Commando certifications Benny lacks.
- **Armour: Composite.** The best any species can wear: 75 kinetic, energy, blast, heat, cold and acid, 30 stun. It is
  heavy (encumbrance 300/120/85); if action drains too fast, Padded or Bounty Hunter armour weigh almost nothing.
- **Mandalorian helmet**, for the Death Watch bunker: its mines poison every 45 s unless the eyes slot holds this helmet
  or a rebreather renamed "Advanced Rebreather" by the bunker's own workbench (`DeathWatchBunkerScreenPlay:hasRebreather`).
  A created rebreather does not count. Swap it on in the mines.
- **Speeder: AV-21 landspeeder**, tied fastest with the swoop and Flash bikes (speed 17).
- **Pet medicine:** the strongest stimpack (d) and vitapack (c).

**bestgear**
```
/object createitem object/weapon/ranged/rifle/rifle_t21.iff
/object createitem object/tangible/wearables/armor/mandalorian/armor_mandalorian_helmet.iff
/object createitem object/tangible/medicine/pet/pet_stimpack_d.iff 10
/object createitem object/tangible/medicine/pet/pet_vitapack_c.iff 3
/object createitem object/tangible/deed/vehicle_deed/landspeeder_av21_deed.iff
```

**bestarmor**
```
/object createitem object/tangible/wearables/armor/composite/armor_composite_helmet.iff
/object createitem object/tangible/wearables/armor/composite/armor_composite_chest_plate.iff
/object createitem object/tangible/wearables/armor/composite/armor_composite_leggings.iff
/object createitem object/tangible/wearables/armor/composite/armor_composite_boots.iff
/object createitem object/tangible/wearables/armor/composite/armor_composite_gloves.iff
/object createitem object/tangible/wearables/armor/composite/armor_composite_bicep_l.iff
/object createitem object/tangible/wearables/armor/composite/armor_composite_bicep_r.iff
/object createitem object/tangible/wearables/armor/composite/armor_composite_bracer_l.iff
/object createitem object/tangible/wearables/armor/composite/armor_composite_bracer_r.iff
```

## Gear one line at a time (admin, test galaxy): `/object createitem <template> [quantity]`

```
/object createitem object/weapon/ranged/rifle/rifle_t21.iff
/object createitem object/weapon/ranged/rifle/rifle_dlt20a.iff
/object createitem object/tangible/wearables/armor/composite/armor_composite_helmet.iff
/object createitem object/tangible/wearables/armor/composite/armor_composite_chest_plate.iff
/object createitem object/tangible/wearables/armor/composite/armor_composite_leggings.iff
/object createitem object/tangible/wearables/armor/composite/armor_composite_boots.iff
/object createitem object/tangible/wearables/armor/composite/armor_composite_gloves.iff
/object createitem object/tangible/wearables/armor/composite/armor_composite_bicep_l.iff
/object createitem object/tangible/wearables/armor/composite/armor_composite_bicep_r.iff
/object createitem object/tangible/wearables/armor/composite/armor_composite_bracer_l.iff
/object createitem object/tangible/wearables/armor/composite/armor_composite_bracer_r.iff
/object createitem object/tangible/medicine/pet/pet_stimpack_d.iff 10
/object createitem object/tangible/medicine/pet/pet_vitapack_c.iff 3
/object createitem object/tangible/deed/vehicle_deed/speederbike_swoop_deed.iff
```
T21: the Rifleman's heavy hitter; the DLT-20A is the spare. Pet stimpacks heal a pet, vitapacks bring a dead pet back. Mirren (the crew's doctor) heals Benny.

## Pets first

1. Target a creature (young or baby ones tame easily) and `/tame`. Call the pet from the datapad.
2. Train its commands: radial menu on the pet, **Train Command**, choose one, then **say** the word you want for it. Suggested words: Attack = `sic`, Follow = `heel`, Stay = `stay`, Guard = `guard`.
3. Pets obey trained phrases in spatial chat (`PetManager::handleChat`), which is why a macro can command them with `/say`. The 17 "pet order" abilities in the skill boxes are these trainable commands, not slash commands; the 15 Oct research counted them as missing for that reason.

## Macros (Command Browser, Macro tab, New; one command per line)

**sic** (send the pets, buff them):
```
/say sic
/pause 1
/emboldenpets
/pause 1.5
/enragepets
```

**open** (first shots, then the loop):
```
/aim
/pause 1.5
/headShot3
/pause 1.5
/macro rifle
```

**rifle** (the damage loop; it calls itself, `/dump` stops every macro):
```
/headShot3
/pause 1.5
/flurryShot2
/pause 1.5
/mindShot2
/pause 1.5
/strafeShot2
/pause 1.5
/macro rifle
```

**ambush** (optional opener: Surprise Shot needs cover first):
```
/takeCover
/pause 4
/surpriseShot
/pause 1.5
/macro rifle
```

Specials share one cooldown group with a 1.5 s queue time, so the pauses match the queue. When action runs low the specials stop landing and the auto-attack carries on; let it recover or add a `/pause 3` to the loop.

## Play data to watch

The escort logs the combat around Benny to `Bot-reports/play/`. Worth noting in play: pets that ignore a trained word, pet damage against Benny's, embolden/enrage effects, how often pets die, and anything that refuses with a message.
