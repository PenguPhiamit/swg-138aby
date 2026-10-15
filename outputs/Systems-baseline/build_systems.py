#!/usr/bin/env python3
"""Core3 systems baseline: static code layer.

Re-run:  python outputs/Systems-baseline/build_systems.py
Writes:  outputs/Systems-baseline/systems.md and systems.json

What it does
- SYSTEMS (below) holds the hand-written findings for each game system: status,
  gaps, evidence, bot probe and fix work. Those were written by reading the code
  (Claude, 15 Oct 2026) and are NOT recomputed. Edit them when the code changes.
- Everything numeric IS recomputed on each run, read-only, through WSL:
  files / lines / TODO-FIXME-"not implemented" hits for each system's paths,
  the current git revision, a re-check of every command the audit called a stub
  (so later local fixes show up), and a whole-repo search for every skill mod and
  ability flag each profession grants (to spot perks no server code reads).
- Command status comes from outputs/tools/core3_audit/command_audit.json and the
  profession data from outputs/Claude-class-check/professions.json. Neither file
  is modified.

Rules this script keeps: it never writes outside its own folder (plus a temp
script in the system temp dir), never reads bin/conf/config-local.lua, and only
runs read-only git commands in /opt/swg/Core3-dev.
"""

import collections
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.dirname(HERE)
AUDIT_JSON = os.path.join(OUTPUTS, "tools", "core3_audit", "command_audit.json")
PROFESSIONS_JSON = os.path.join(OUTPUTS, "Claude-class-check", "professions.json")
REPO = "/opt/swg/Core3-dev"
DISTRO = "Debian"
TODO_RE = r"TODO|FIXME|not implemented|unimplemented|not yet implemented"
MM = "MMOCoreORB/"
SRC = MM + "src/server/zone/"
CMD = SRC + "objects/creature/commands/"
SCR = MM + "bin/scripts/"

STATUSES = ["implemented", "partial", "stub", "disabled", "missing"]

# --------------------------------------------------------------------------
# Hand-written findings. Paths in evidence are relative to MMOCoreORB/.
# "paths" are git pathspecs (relative to the repo root) used for the counts.
# "cmds" lists commands (lower case, as registered) that belong to the system;
# CMD_RULES further down catch whole families (combat engine, Jedi, space, ...).
# --------------------------------------------------------------------------
SYSTEMS = [
    dict(
        id="1", group="Characters",
        name="Species, character creation, attributes, skills, XP, trainers, titles",
        status="implemented",
        gaps=["Staff `/grantTitle` is a stub (players' own `/setCurrentSkillTitle` works).",
              "Stat changes after creation only through Image Designer stat migration (row 7)."],
        evidence=["`src/server/zone/managers/player/creation/PlayerCreationManager.cpp`; `bin/scripts/managers/player_creation_manager.lua` (10 pre-CU species plus local Chiss, commit a32566bc)",
                  "`src/server/zone/managers/skill/SkillManager.cpp` loads client `skills.iff`; sandbox skill points from `Core3.Sandbox.SkillPoints` (profile: 1000)",
                  "XP: `PlayerManagerImplementation::awardExperience`, sandbox multiplier (profile: 5x, Jedi 2x); training cost `Skill.h` x `Core3.Sandbox.TrainingCostMultiplier` (0.25)",
                  "Trainers: about 35 trainer templates `bin/scripts/mobile/trainer/`, `screenplays/trainers/trainerData.lua` (893 lines); apprenticeship on (`managers/skill_manager.lua`)",
                  "Languages: `bin/scripts/skills/language/` (23), `/setSpokenLanguage`"],
        switches=["Core3.Sandbox.SkillPoints", "Core3.Sandbox.TrainingCostMultiplier", "Core3.PlayerCreationManager.MaxCharactersPerGalaxy"],
        paths=[SRC + "managers/player/creation", SRC + "managers/skill/SkillManager*", SRC + "managers/skill/SkillModManager*", SRC + "objects/creature/variables/Skill*", SCR + "screenplays/trainers", SCR + "managers/player_creation_manager.lua", SCR + "managers/skill_manager.lua"],
        cmds=["setcurrentskilltitle", "surrenderskill", "findmytrainer", "skill", "clientqualifiedforskill", "getattributes", "getattributesbatch", "requestcharactersheetinfo", "requestbiography", "setbiography", "setspokenlanguage", "newbieselectstartinglocation", "newbierequeststartinglocations", "teach", "innate", "regeneration", "equilibrium", "vitalize", "burstrun", "toggleawayfromkeyboard", "anon", "lfg", "newbiehelper", "roleplay", "requestcharactermatch", "setmatchmakingcharacterid", "setmatchmakingpersonalid", "stat"],
        probe="Fresh agent of each species: `/agentskill` a starter box at its trainer, assert skill points left, XP cap and the box in the character sheet.",
        fix="None for pre-CU. Keep species work (Chiss) on the human rig; re-check skill-point and XP sandbox values before any live promotion."),
    dict(
        id="2", group="Combat",
        name="Melee and ranged combat, specials, states, DoTs, posture, wounds and battle fatigue, incapacitation",
        status="implemented",
        gaps=["`/coupDeGrace` is a stub; `/deathBlow` is the working finisher (animation TODO, `DeathBlowCommand.h:37`).",
              "`/combatEscape` and `/multiTargetShot` are stubs (neither is granted by a pre-CU box); `/target`, `/combatSpam`, `/combatTarget`, `/toggleCombatTaunts` are stubs too, probably client-side settings.",
              "CombatManager TODOs: tangible-vs-tangible damage not implemented (`CombatManager.cpp:584`), unskilled-weapon penalty unresearched (`:1980`), animation choice (`:485`)."],
        evidence=["`src/server/zone/managers/combat/CombatManager.cpp` (shared engine for 190+ combat commands whose numbers live in `bin/scripts/commands/*.lua`)",
                  "States and DoTs: `objects/creature/commands/StateEffect.h`, `DotEffect.h`, `CreatureObject::addDotState`",
                  "Squad Leader commands on `SquadLeaderCommand.h` (all 10 implemented)",
                  "Class check: 222 attack abilities across professions, 2 stub-looking handlers (`outputs/Claude-class-check/matrix.md`)"],
        switches=["Core3.CombatManager.AllowSameAccountLinkDeadBeneficialActions"],
        paths=[SRC + "managers/combat", CMD + "CombatQueueCommand.h", CMD + "SquadLeaderCommand.h", CMD + "DotEffect.h", CMD + "StateEffect.h", CMD + "CommandEffect.h", SCR + "commands"],
        cmds=["aim", "kneel", "prone", "stand", "sitserver", "peace", "deathblow", "coupdegrace", "combatescape", "combattarget", "combatspam", "togglecombattaunts", "target", "assist", "berserk1", "berserk2", "centerofbeing", "meditate", "powerboost", "tumbletokneeling", "tumbletoprone", "tumbletostanding", "warcry1", "warcry2", "intimidate1", "intimidate2", "taunt", "lastditch", "feigndeath", "throwgrenade", "fireheavyweapon", "rescue", "wookieeroar", "setwarcry", "setintimidate", "setboostmorale", "setformup", "setretreat", "setsteadyaim", "combatmodecheck", "multitargetshot", "multitargetpistolshot", "reload", "takecover"],
        probe="Agent fight reflex vs a weak creature with each weapon class; assert damage lines in the combat log, a posture/state change from one special, and wounds after incapacitation.",
        fix="Decide whether `/coupDeGrace` should alias `/deathBlow`. Otherwise balance testing, not building."),
    dict(
        id="3", group="Combat",
        name="Death, cloning, insurance, corpses and consent",
        status="implemented",
        gaps=["`/clone` is a stub, but cloning runs through the clone SUI (`PlayerManagerImplementation.cpp:1576-1740`).",
              "`/lootPlayerCorpse`, `/corpse` and `/deathCount` are stubs; check whether the pre-CU client uses them."],
        evidence=["`PlayerManagerImplementation::killPlayer` (`:1316`), `sendActivateCloneRequest` (`:1576`), `sendPlayerToCloner` (`:1740`); city-banned players can't use a city's cloner (`:1720`)",
                  "Item decay on death: insured 1%, uninsured 5%, insurance cleared (`:1855-1862`)",
                  "Insurance: `InsureCommand.h`, `objects/tangible/components/InsuranceTerminalMenuComponent`",
                  "Agent already observed death and cloning on the test galaxy (feature register F18)"],
        switches=["Core3.PlayerManager.WipeFillingOnClone"],
        paths=[SRC + "managers/player/PlayerManagerImplementation.cpp", SRC + "objects/building/cloning", CMD + "InsureCommand.h", SRC + "objects/tangible/components/InsuranceTerminalMenuComponent*", SRC + "objects/player/sui/callbacks/CloningRequestSuiCallback.h"],
        cmds=["activateclone", "clone", "consent", "unconsent", "haveconsent", "cuiconsentresponse", "insure", "corpse", "deathcount", "lootplayercorpse", "dragincapacitatedplayer"],
        probe="Agent dies to a strong creature, picks the nearest cloner, then insures one item at a terminal; assert respawn location, clone sickness/decay and the insured flag.",
        fix="None needed for play."),
    dict(
        id="4", group="Combat",
        name="PvP, TEF, duels and faction combat flags",
        status="implemented",
        gaps=["Staff `/setTef`, `/harmful`, `/harmless` are stubs.",
              "`Core3.PvpMode` (all players attackable) defaults off; `useCovertOvertSystem` (CU/NGE-style rules) defaults off, so pre-CU behaviour applies."],
        evidence=["`objects/player/events/PvpTefRemovalTask.h`; duel and TEF checks in `CreatureObjectImplementation.cpp:3470-3482` (crackdown TEF, PvpMode, duels)",
                  "`DuelCommand.h`, `EndDuelCommand.h`, `ShowPvPRatingCommand.h`; `ConfigManager::useCovertOvertSystem()` used in about 25 places (`CombatManager.cpp:380`, `GCWManagerImplementation.cpp:758`, ...)"],
        switches=["Core3.PvpMode (default false)", "Core3.GCWManager.useCovertOvertSystem (default false)"],
        paths=[SRC + "objects/player/events/PvpTefRemovalTask.h", CMD + "DuelCommand.h", CMD + "EndDuelCommand.h", CMD + "DeclareOvertCommand.h", CMD + "ShowPvPRatingCommand.h"],
        cmds=["duel", "endduel", "showpvprating"],
        probe="Two agents `/duel` each other and trade one attack; assert both flagged attackable and the flag clears after `/endDuel`.",
        fix="None for pre-CU. Write the staff `/setTef` only if moderators need it."),
    dict(
        id="5", group="Medical",
        name="Healing, wounds, buffs, cures, revives, hospitals and medical rating",
        status="implemented",
        gaps=["`/tendDamageTool` and `/tendWoundsTool` are stubs (`/tendDamage` and `/tendWound` work).",
              "TODOs in `/healDamage` (area-target refactor, `HealDamageCommand.h:312`), `/healWound` (string, `:314`) and `/revivePlayer` (debuff message, `:109`) are cosmetic."],
        evidence=["Heal commands in `objects/creature/commands/Heal*.h`, `ForceHealQueueCommand` family, `CurePackCommand`, `DotPackCommand`, `TendCommand`",
                  "Medical rating: building templates and `private_medical_rating` (`BuildingObjectImplementation.cpp:1211`, `HealEnhanceCommand.h:91`)",
                  "Class check: 25 heal-other abilities, none stub-looking"],
        switches=[],
        paths=[CMD + "Heal*", CMD + "Tend*", CMD + "Cure*", CMD + "Apply*", CMD + "FirstAid*", CMD + "QuickHeal*", CMD + "Diagnose*", CMD + "RevivePlayer*", CMD + "StopBleeding*", SRC + "objects/tangible/pharmaceutical"],
        cmds=["firstaid", "quickheal", "diagnose", "reviveplayer", "healenhance", "stopbleeding", "extinguishfire", "requeststimpack", "medicalforage", "healstate", "healmind", "healdamage", "healwound", "tenddamage", "tendwound", "tenddamagetool", "tendwoundstool"],
        probe="Medic agent heals a wounded group mate with a stim and a wound pack in a hospital; assert HAM and wound values rose and one charge was used.",
        fix="None needed. Map the two tool stubs to the real tend code if the client sends them."),
    dict(
        id="6", group="Entertainment",
        name="Dancing and music, flourishes, bands, entertainer buffs, wound and battle-fatigue healing, venues",
        status="implemented",
        gaps=["`/pauseDance`, `/pauseMusic`, `/showDanceVisuals`, `/showMusicianVisuals` are stubs (cosmetic)."],
        evidence=["`objects/player/sessions/EntertainingSessionImplementation.cpp` (1250 lines): patron effects (`:33`), venue check (`:128`), wound/BF healing (`:145-180`), bands (`:334`, `:1199`), buffs (`:694-930`), XP (`:1002`), entertainer missions (`:933`)",
                  "`managers/skill/PerformanceManager.cpp`, `objects/creature/buffs/PerformanceBuff*`",
                  "Class check: 53 performance abilities"],
        switches=[],
        paths=[SRC + "objects/player/sessions/EntertainingSession*", SRC + "managers/skill/Performance*", SRC + "objects/creature/buffs/PerformanceBuff*", CMD + "Start*Dance*", CMD + "Start*Music*", CMD + "*Band*", CMD + "Flourish*", CMD + "Change*"],
        cmds=["startdance", "stopdance", "startmusic", "stopmusic", "changedance", "changemusic", "changebandmusic", "startband", "stopband", "bandflourish", "flourish", "watch", "listen", "stopwatching", "stoplistening", "pausedance", "pausemusic", "showdancevisuals", "showmusicianvisuals", "setperformancebufftarget", "denyservice", "colorlights", "dazzle", "distract", "firejet", "smokebomb", "spotlight", "ventriloquism"],
        probe="Dancer agent `/startDance` in a cantina while a wounded agent `/watch`es for 2 minutes; assert Mind wounds and battle fatigue fell and the watcher gets the dance buff on leaving.",
        fix="None needed."),
    dict(
        id="7", group="Entertainment",
        name="Image Designer: customisation sessions, stat migration, holo-emotes",
        status="partial",
        gaps=["Server trusts the client on colour palette indices: the per-level check is commented out (`ImageDesignManager.cpp:489-562`).",
              "Holo-emote purchase has no skill or price check (`ImageDesignSessionImplementation.cpp:283-297`).",
              "Stat migration only inside the 4 salon building templates (`gameObjectType 530`); no ID tent or player salon.",
              "Designer's salon checked twice instead of designer and target (`ImageDesignSessionImplementation.cpp:198`).",
              "`/requestStatMigrationStart` and `/requestStatMigrationStop` are empty (the `...Data` commands do the work)."],
        evidence=["Session: `objects/player/sessions/ImageDesignSessionImplementation.cpp` (start `:50`, commit `:111`, payment `:320`, timeout `:385`)",
                  "Manager: `managers/skill/imagedesign/ImageDesignManager.cpp` (skill-mod gate `:41`, hair `:396-487`)",
                  "Packets `0x238`/`0x239` at `ZonePacketHandler.cpp:211-212`; `/holoEmote` `HoloEmoteCommand.h` (16 emotes, 20 charges, 30 s cooldown)",
                  "Full function table: `id-politician-gaps.md` section 1"],
        switches=[],
        paths=[SRC + "managers/skill/imagedesign", SRC + "objects/player/sessions/ImageDesign*", SRC + "objects/player/sessions/MigrateStatsSession.idl", SRC + "objects/player/events/ImageDesignTimeoutEvent.h", SRC + "packets/object/ImageDesign*", CMD + "ImagedesignCommand.h", CMD + "HoloEmoteCommand.h", CMD + "Request*StatMigration*"],
        cmds=["imagedesign", "holoemote", "requeststatmigrationdata", "requestsetstatmigrationdata", "requeststatmigrationstart", "requeststatmigrationstop"],
        probe="Two grouped agents in the Theed salon: `/imagedesign <target>`, one hair change, both accept; assert the target's hair template and the designer's `imagedesigner` XP. Needs a new agent ability to send ImageDesignChange (0x238).",
        fix="Re-enable the palette check by designer level; gate holo-emotes on ID skill; fix the double salon check; optionally a config switch or ID tent so migration works outside the 4 salons."),
    dict(
        id="8", group="Crafting",
        name="Crafting: schematics, assembly, experimentation, customisation, crafting stations, factories",
        status="implemented",
        gaps=["Staff `/craft` and `/manufacture` are stubs.",
              "Player stubs `/requestDraftSlots`, `/requestResourceWeights`, `/getPrototype`, `/requestManfSchematicSlots`, `/restartCraftingSession`, `/stopCraftingSession`; the `...Batch` variants and crafting-session packets carry the real work (check in game).",
              "Droid lab TODO: `droid_count` property not read (`DroidLabratory.cpp:18`)."],
        evidence=["`managers/crafting/CraftingManagerImplementation.cpp`, labs in `managers/crafting/labratories/`, `objects/player/sessions/crafting/CraftingSessionImplementation.cpp` (sandbox `Core3.Sandbox.CraftSeconds`)",
                  "2252 draft schematic templates in `bin/scripts/object/draft_schematic/` (clothing 519, space 336, chemistry 204, bio_engineer 155, ...)",
                  "Factories: `objects/installation/factory/FactoryObjectImplementation.cpp` (sandbox time x0.25); stations `objects/tangible/tool/CraftingStation*`"],
        switches=["Core3.Sandbox.CraftSeconds", "Core3.Sandbox.FactoryTimeMultiplier"],
        paths=[SRC + "managers/crafting", SRC + "objects/player/sessions/crafting", SRC + "objects/draftschematic", SRC + "objects/manufactureschematic", SRC + "objects/installation/factory", SRC + "objects/tangible/tool/Crafting*", SRC + "objects/factorycrate", SCR + "managers/crafting"],
        cmds=["requestcraftingsession", "cancelcraftingsession", "selectdraftschematic", "nextcraftingstage", "createprototype", "createmanfschematic", "requestdraftslots", "requestdraftslotsbatch", "requestmanfschematicslots", "requestresourceweights", "requestresourceweightsbatch", "restartcraftingsession", "stopcraftingsession", "getprototype", "factorycratesplit", "extractobject"],
        probe="Artisan agent crafts a survey tool from granted resources, experiments once, then runs 2 in a factory; assert item stats and the crate count. Needs the planned crafting agent protocol (F22).",
        fix="None for play; build the agent crafting protocol to test it."),
    dict(
        id="9", group="Crafting",
        name="Resources and spawning, surveying and sampling",
        status="implemented",
        gaps=["`/survey`, `/makeSurvey`, `/resSampleLoop`, `/resourceSetName` are stubs; surveying runs from the survey tool (`SurveyToolImplementation.cpp`, needs `survey` ability)."],
        evidence=["`managers/resource/` (30 files) incl. `resourcespawner/ResourceSpawner.cpp` (city Sample Rich bonus `:1083,:1096`)",
                  "`bin/scripts/managers/resource_manager.lua`: 12 active zones incl. Hoth and Ossus, minimum pools with local Hoth/Ossus/Legends types",
                  "Agent survey and sample already passed on the test galaxy (feature register F21)"],
        switches=["Core3.Sandbox resource deed 100000 and stack 999999 (compiled, commit 4357970d)"],
        paths=[SRC + "managers/resource", SRC + "objects/resource", SRC + "objects/tangible/tool/SurveyTool*", SCR + "managers/resource_manager.lua"],
        cmds=["survey", "requestsurvey", "sample", "requestcoresample", "makesurvey", "ressampleloop", "resourcesetname", "resourcecontainersplit", "resourcecontainertransfer"],
        probe="Agent uses a mineral survey tool, waypoints the best concentration and samples 3 times; assert resource units rose (agent already reads authoritative units).",
        fix="None."),
    dict(
        id="10", group="Crafting",
        name="Harvesters, power generators, installation maintenance",
        status="implemented",
        gaps=["`/harvesterHarvest`, `/harvesterMakeCrate`, `/harvesterTakeSurvey` are stubs; activate, deactivate, select resource, get data and discard hopper are real. Unsure whether the pre-CU harvester window sends the stubbed three: check in game.",
              "Power and maintenance deposits live in SUI callbacks with TODOs to move them to StructureManager (`InsertPowerSuiCallback.h:46`, `InstallationObjectMenuComponent.cpp:96`)."],
        evidence=["`objects/installation/harvester/HarvesterObjectImplementation.cpp`, `objects/installation/generator/GeneratorObjectImplementation.cpp`, `objects/installation/InstallationObjectImplementation.cpp`",
                  "Maintenance: `objects/structure/events/StructureMaintenanceTask.cpp` (sandbox x0.5)"],
        switches=["Core3.Sandbox.StructureMaintenanceMultiplier", "Core3.StructureMaintenanceTask.AllowBankPayments"],
        paths=[SRC + "objects/installation", SRC + "packets/harvester", CMD + "Harvester*", CMD + "AddPower*"],
        cmds=["harvesteractivate", "harvesterdeactivate", "harvesterdiscardhopper", "harvestergetresourcedata", "harvesterharvest", "harvestermakecrate", "harvesterselectresource", "harvestertakesurvey", "addpower"],
        probe="Agent places a personal mineral harvester and a generator from deeds, adds power and maintenance, waits one cycle; assert hopper quantity > 0.",
        fix="Confirm the three stubs in game; implement only if the client uses them."),
    dict(
        id="11", group="Economy",
        name="Bazaar (auction) and player vendors",
        status="implemented",
        gaps=["All `/auction*` slash commands are stubs: the bazaar runs on client packets (`packets/auction/`), so this is expected.",
              "`/giveMaintenanceToVendor` and `/giveVendorMaint` are stubs (vendor maintenance through the vendor radial; check).",
              "TODO in bid handling: 'prior didn't have enough money' (`AuctionManagerImplementation.cpp:1243`)."],
        evidence=["`managers/auction/AuctionManagerImplementation.cpp` (city sales tax `:689,:1022`), `objects/auction/AuctionItem*`",
                  "`managers/vendor/VendorManager.cpp`, `objects/tangible/components/vendor/` (ads and map registration need Merchant Advertising boxes, `VendorMenuComponent.cpp:87,95`), `bin/scripts/managers/vendor_manager.lua` hiring tiers",
                  "Merchant perks are checked by skill box, not by the `*_fees_1` ability names: bazaar fee -20%/-40% (`AuctionManagerImplementation.cpp:744-749`), vendor rate (`VendorDataComponent.cpp:440-442`), ad barking (`VendorAdBarkingSessionImplementation.cpp:60`), barker droid (`DroidMerchantModuleDataComponent.cpp:41`), maintenance discount by ability (`StructureManager.cpp:1382`)"],
        switches=["Core3.MaxAuctionSearchJobs", "Core3.AuctionManager.Startup.ExpireInvalid"],
        paths=[SRC + "managers/auction", SRC + "managers/vendor", SRC + "objects/auction", SRC + "objects/tangible/components/vendor", SRC + "packets/auction", SCR + "managers/vendor_manager.lua"],
        cmds=["auction", "auctionaccept", "auctionbid", "auctioncancel", "auctioncreate", "auctionquery", "auctionretrieve", "auctionsay", "createvendor", "givemaintenancetovendor", "givevendormaint", "registerwithlocation"],
        probe="Agent A lists an item on a bazaar terminal; agent B buys it; assert credits moved minus sales tax and B can retrieve it.",
        fix="None for play; confirm vendor maintenance works from the vendor radial."),
    dict(
        id="12", group="Economy",
        name="Banks, secure trade, tips and wire transfers, credit sinks",
        status="implemented",
        gaps=["`/tip` carries a TODO but is real (cash and bank wire with 5% surcharge, `TipCommand.h:24-221`).",
              "Staff `/money`, `/editBank`, `/editBankAccount` are stubs (`/credits` works)."],
        evidence=["`objects/tangible/components/BankTerminalMenuComponent.cpp`, `objects/player/sui/callbacks/BankTerminalSuiCallback.h`",
                  "`objects/player/sessions/TradeSession.idl` (secure trade); `managers/credit/` and `objects/transaction/TransactionLog.cpp` log every credit move",
                  "Credit sinks with code: structure and city maintenance, five city taxes, cloning, insurance, trainer fees, travel tickets, ID payments, vehicle repair"],
        switches=["Core3.SameAccountTipsAreFree"],
        paths=[SRC + "managers/credit", SRC + "objects/transaction", SRC + "objects/player/sessions/TradeSession.idl", SRC + "objects/tangible/components/BankTerminal*", CMD + "TipCommand.h"],
        cmds=["tip", "giveitem"],
        probe="Agent A `/tip`s agent B 100 credits in cash and 100 by bank; assert both balances (agent reads cash and bank).",
        fix="None. Secure trade needs the planned agent trade protocol (F23) to be tested."),
    dict(
        id="13", group="Economy",
        name="Loot tables and group loot rules",
        status="implemented",
        gaps=["`/lootAll` is a stub; `/loot` and the group loot task are real. Unsure whether the client's loot-all uses it: check in game.",
              "`/openLotteryContainer` and `/closeLotteryContainer` are stubs; lottery runs on `LootLotterySession` and lottery window packets."],
        evidence=["`managers/loot/` (12 files), `bin/scripts/managers/loot_manager.lua` (yellow/exceptional/legendary chances), 659 loot groups and 2222 loot items in `bin/scripts/loot/`",
                  "Group rules free-for-all, master looter, lottery, random: `managers/group/GroupLootTask.h:45-126`, `GroupManager.cpp:606-682`, `objects/player/sessions/LootLotterySessionImplementation.cpp`; credits auto-split (`GroupLootTask.h:126`)"],
        switches=["Core3.LootManager.DebugAttributes"],
        paths=[SRC + "managers/loot", SRC + "managers/group/GroupLootTask.h", SRC + "objects/player/sessions/LootLottery*", SCR + "loot/groups.lua", SCR + "managers/loot_manager.lua"],
        cmds=["loot", "lootall", "grouploot", "makemasterlooter", "openlotterycontainer", "closelotterycontainer"],
        probe="Grouped agents set lottery, kill a creature and loot; assert the lottery window opens and one item lands with the winner.",
        fix="None for play."),
    dict(
        id="14", group="Housing",
        name="Structure placement, permissions, decoration, storage limits, maintenance, condemnation",
        status="implemented",
        gaps=["`/vertFurniture` is a stub (raise/lower uses `/itemMoveUp`/`Down`, which work); `Core3.StructureManager.EnhancedFurnitureRotate` defaults off.",
              "`/transferStructure` has a TODO but is real; staff `/addAllowedPlayer`/`/removeAllowedPlayer` are stubs."],
        evidence=["`managers/structure/StructureManager.cpp`: placement checks `:300-476`, residence `:683-748`, property tax `:1015`, uncondemn `:1149-1182`, Merchant maintenance discount `:1382`",
                  "Permissions `objects/structure/StructurePermissionList.cpp`; storage `BuildingObjectImplementation.cpp` lots x `Core3.Sandbox.HouseItemsPerLot` (profile 1000, cap 10000)",
                  "Maintenance and decay `objects/structure/StructureObjectImplementation.cpp`, `events/StructureMaintenanceTask.cpp`"],
        switches=["Core3.Sandbox.HouseItemsPerLot", "Core3.Sandbox.HouseMaxItems", "Core3.StructureObject.MaintenanceBootDelay", "Core3.Tweaks.StructureObject.DestoryOrphans", "Core3.StructureManager.EnhancedFurnitureRotate"],
        paths=[SRC + "managers/structure", SRC + "objects/structure", SRC + "objects/building/BuildingObject*", SRC + "objects/player/sessions/PlaceStructureSession*", CMD + "*Structure*", CMD + "*Furniture*", CMD + "ItemMove*", CMD + "ItemRotate*"],
        cmds=["placestructure", "placestructuremode", "destroystructure", "namestructure", "permissionlistmodify", "setpermission", "structurestatus", "paymaintenance", "movefurniture", "rotatefurniture", "vertfurniture", "itemmoveback", "itemmovedown", "itemmoveforward", "itemmoveup", "itemrotateleft", "itemrotateright", "declareresidence", "transferstructure", "setprivacy", "setowner"],
        probe="Agent places a small house from a deed, adds a second agent to entry, drops and rotates one item inside; assert the item count and the permission list after relog.",
        fix="None for play."),
    dict(
        id="15", group="Cities",
        name="Player cities and Politician",
        status="partial",
        gaps=["Clone Lab and Entertainment District specialisations grant mods nothing reads (`private_spec_cloning`, `private_spec_entertainer`).",
              "Militia can ban, pardon and grant zoning, but have no law-enforcement attack right the UI promises (`CityManagerImplementation.cpp:1480`).",
              "`/cityWarn` does not exist (switch `EnableCityWarn` in `city_manager.lua:73`, no command).",
              "City guards: `/startCitySpawner` and `/stopCitySpawner` are empty stubs.",
              "Weekly updates and 3-update elections make it look idle in short tests (God-mode city hall menu can force updates)."],
        evidence=["`managers/city/CityManagerImplementation.cpp` (2481 lines, 1 TODO): founding `:196`, updates `:737`, taxes `:814,:1846-1944`, elections `:1118-1255`, militia `:1463-1580`, zoning `:2404`",
                  "`objects/region/CityRegionImplementation.cpp`, city hall and voting menus `objects/region/components/`",
                  "All five taxes have consumers (income, property, sales, travel, garage); 6 of 8 specialisations have readers",
                  "Full function table: `id-politician-gaps.md` section 2"],
        switches=["city_manager.lua: CitizensPerRank {1,2,3,4,5} (sandbox), CityUpdateInterval 10080 min, CityVotingCycles 3, maintenanceDiscount 0.5, EnableCityWarn false, CitiesAllowed (none on Dathomir/Endor/Yavin 4; Hoth/Ossus not listed)"],
        paths=[SRC + "managers/city", SRC + "objects/region/CityRegion*", SRC + "objects/region/Citizen*", SRC + "objects/region/components", SRC + "objects/region/events", CMD + "City*", CMD + "*CitySpawner*", CMD + "GrantZoningRights*", CMD + "InstallMissionTerminal*", CMD + "RecruitSkillTrainer*", SRC + "objects/player/sui/callbacks/City*", SRC + "objects/player/sui/callbacks/PlaceCityHall*", SCR + "managers/city_manager.lua"],
        cmds=["cityban", "citypardon", "grantzoningrights", "installmissionterminal", "recruitskilltrainer", "startcityspawner", "stopcityspawner"],
        probe="Politician agent places a city hall, a second agent declares residence in the radius, staff forces a city update; assert 'New City Approved' mail, rank in `/cityInfo` and `political` XP.",
        fix="Read the two dead spec mods (cloning, entertainer); add militia TEF and `/cityWarn`; optional city guard spawner; a test-galaxy multiplier for the update interval."),
    dict(
        id="16", group="Factions and GCW",
        name="Factions: recruiters, ranks, overt/covert, faction points, perks",
        status="implemented",
        gaps=["Staff `/showFactionInformation`, `/getRank`, `/setRank` are stubs.",
              "`useCovertOvertSystem` (later CU/NGE rules) is off by default; pre-CU on-leave/covert/overt status applies."],
        evidence=["`managers/faction/` (FactionManager), `bin/scripts/managers/faction_manager.lua` (faction relationship table), recruiters `screenplays/gcw/recruiters/` with `factionPerkData.lua`",
                  "`DeclareOvertCommand.h`, `DelegateFactionPointsCommand.h`, `ToggleDisplayingFactionRankCommand.h`"],
        switches=["Core3.GCWManager.useCovertOvertSystem (default false)"],
        paths=[SRC + "managers/faction", SCR + "managers/faction_manager.lua", SCR + "screenplays/gcw/recruiters", CMD + "DeclareOvert*", CMD + "DelegateFactionPoints*"],
        cmds=["declareovert", "toggledisplayingfactionrank", "delegatefactionpoints", "gcwstatus"],
        probe="Agent joins the Rebels at a recruiter, buys one perk with faction points, goes overt; assert faction status and points.",
        fix="None for play."),
    dict(
        id="17", group="Factions and GCW",
        name="GCW bases (placement, terminals, vulnerability, destruction), turrets and minefields, contraband scans",
        status="implemented",
        gaps=["`/purchaseReinforcement` is a stub.", "Base alarms off (`spawnBaseAlarms = false`, `gcw_manager.lua`)."],
        evidence=["`managers/gcw/GCWManagerImplementation.cpp` and 32 more files: vulnerability tasks, DNA and slicing terminals, power switches, shutdown and destruction tasks, donations, contraband scans",
                  "`bin/scripts/managers/gcw_manager.lua` (25 bases per planet, 3 per player, 3 h vulnerability every 48 h), city control banners and crackdown screenplays"],
        switches=["gcw_manager.lua: maxBasesPerPlanet, maxBasesPerPlayer, allowPveBases, spawnBaseAlarms"],
        paths=[SRC + "managers/gcw", SCR + "managers/gcw_manager.lua", SCR + "screenplays/gcw", SCR + "screenplays/crackdown", CMD + "Minefield*", CMD + "Defuse*"],
        cmds=["defuseminefield", "minefieldattack", "turretfire", "purchasereinforcement"],
        probe="Faction agent places a small base deed, waits for vulnerability (staff can shorten), slices a terminal; assert the base state changes.",
        fix="None for play; base fights need several agents."),
    dict(
        id="18", group="Factions and GCW",
        name="Battlefields",
        status="stub",
        gaps=["Only no-build markers are spawned (`screenplays/battlefields/battlefield_spawner.lua`); no battlefield game logic in C++.",
              "`/battlefieldStatus`, `/placeBattlefieldStructure`, `/repairBattlefieldStructure` are empty stubs."],
        evidence=["`bin/scripts/screenplays/battlefields/battlefield_spawner.lua` (112 lines, marker list for 8 planets)", "No battlefield code in `src/server` beyond the three stub commands"],
        switches=[],
        paths=[SCR + "screenplays/battlefields", CMD + "*Battlefield*"],
        cmds=["battlefieldstatus", "placebattlefieldstructure", "repairbattlefieldstructure"],
        probe="`/battlefieldStatus` inside a marker: expect a status window; today nothing happens.",
        fix="Large build (pre-CU battlefield rules, structures, scoring) or leave out. Low priority for a LAN PvE server."),
    dict(
        id="19", group="Factions and GCW",
        name="GCW invasions",
        status="missing",
        gaps=["Only object templates exist (`object/custom_content/tangible/gcw/flip_banner_invasion_spawner.lua`, invasion binoculars); no invasion logic. Invasions are a later (CU/NGE-era) feature."],
        evidence=["`git grep -i invasion` finds templates only"],
        switches=[],
        paths=[],
        cmds=[],
        probe="Not applicable.",
        fix="Leave out for pre-CU unless the owner wants it."),
    dict(
        id="20", group="Missions",
        name="Mission terminals: destroy, deliver, survey, hunting, recon, crafting, dancer and musician, bounty",
        status="implemented",
        gaps=["TODOs: deliver item is a placeholder (`DeliverMissionObjectiveImplementation.cpp:185`), destroy string id (`DestroyMissionObjectiveImplementation.cpp:182`)."],
        evidence=["`managers/mission/MissionManagerImplementation.cpp` (all nine types at `:438-460`, city mission bonus `:638-725`, city ban `:188`)",
                  "Objectives `objects/mission/*MissionObjective*`; terminal templates general, artisan, bounty, entertainer, imperial, rebel, scout, newbie, statue (`object/tangible/terminal/terminal_mission*.lua`)",
                  "Local Hoth outpost terminals with destroy and deliver missions (commit 92d99dba); agent mission list/accept works (F20)"],
        switches=["Core3.MissionManager.ListRequestCooldown", "Core3.MissionManager.IncludeFactionPets"],
        paths=[SRC + "managers/mission", SRC + "objects/mission", SCR + "managers/mission"],
        cmds=[],
        probe="Agent takes a destroy mission at a general terminal, kills the lair and returns; assert the payout and mission removal.",
        fix="None for play."),
    dict(
        id="21", group="Missions",
        name="Bounty Hunter: player bounties, Jedi bounties, probe droids and tracking",
        status="partial",
        gaps=["No observer fails a bounty mission when someone else kills the target (`BountyMissionObjectiveImplementation.cpp:177`).",
              "`bounty_mission_level` skill mod has no reader (unsure how BH mission level is chosen).",
              "Several BH `private_*_combat_difficulty` mods have no reader."],
        evidence=["`objects/mission/BountyMissionObjectiveImplementation.cpp`, `objects/mission/PlayerBounty*`, `objects/mission/bountyhunter/` (probe droid, `FindTargetTask.h` reads `droid_find_chance`, `droid_track_chance`, `droid_tracks`)",
                  "Jedi bounties via visibility (`bin/scripts/managers/jedi/visibility_manager.lua`: terminal threshold 1500)"],
        switches=["Core3.MissionManager.MaxBountiesPerJedi", "Core3.MissionManager.PlayerBountyCooldown", "Core3.MissionManager.AnonymousBountyTerminals", "Core3.MissionManager.PrivateStructureJediMissions", "Core3.MissionManager.BountyExpirationTime"],
        paths=[SRC + "objects/mission/Bounty*", SRC + "objects/mission/PlayerBounty*", SRC + "objects/mission/bountyhunter", SRC + "managers/visibility"],
        cmds=[],
        probe="BH agent takes an NPC bounty, calls a seeker droid, tracks and kills the target; assert payout. Player bounty needs a second agent with a bounty placed.",
        fix="Add the kill observer; decide whether BH skill should set mission level."),
    dict(
        id="22", group="Creatures",
        name="Creature spawning, lairs, herds and creature AI",
        status="implemented",
        gaps=["AI TODOs: reaction attacks (`AiAgentImplementation.cpp:1735`), indoor follow pathing (`FollowActions.h:492`)."],
        evidence=["`managers/creature/` (30 files: CreatureManager, SpawnAreaMap, LairObserver, DynamicSpawnObserver, CreatureHerdObserver)", "Behaviour trees `objects/creature/ai/bt/`; 1870 lair templates, 492 spawn groups (`bin/scripts/mobile/`)",
                  "Local Hoth and Ossus creature spawns (commits c402e480, 80b66e65)"],
        switches=["Core3.Regions.DisableWorldSpawns", "Core3.Regions.minimumLairSpawnInterval", "Core3.Regions.spawnCheckRange"],
        paths=[SRC + "managers/creature/CreatureManager*", SRC + "managers/creature/Spawn*", SRC + "managers/creature/Lair*", SRC + "managers/creature/Dynamic*", SRC + "managers/creature/CreatureHerd*", SRC + "objects/creature/ai", SRC + "objects/region/SpawnArea*"],
        cmds=["harvestcorpse", "conceal", "maskscent", "areatrack", "animalattack", "animalcalm", "animalscare", "throwtrap", "deploytrap"],
        probe="Agent walks into a spawn region and kills one lair; assert the lair spawns defenders and repopulates.",
        fix="None for play."),
    dict(
        id="23", group="Creatures",
        name="Pets: taming, Creature Handler training, Bio-Engineer DNA and pet crafting",
        status="implemented",
        gaps=["CH skill mods `private_creature_empathy`, `private_creature_training`, `private_creature_management` have no reader.",
              "Balance and pet AI reliability never measured (`Documentation-support/creature-handler-top-tier-plan.md`).",
              "`/sampleDNA` has no `characterAbility` in the command table; the handler's BE Novice check (`SampleDNACommand.h:39`) is the only gate."],
        evidence=["`managers/creature/PetManagerImplementation.cpp`, `objects/intangible/PetControlDeviceImplementation.cpp` (command training gated per CH box `:1296-1309`, mount training `:1339`)",
                  "`managers/creature/DnaManager.cpp`, `objects/tangible/component/dna/`, `objects/tangible/deed/pet/PetDeed*`; `bin/scripts/managers/crafting/bio_dna_sets.lua`, `bio_skill_mods.lua`; 155 BE schematics",
                  "All 26 pet commands `implemented` in the audit"],
        switches=[],
        paths=[SRC + "managers/creature/PetManager*", SRC + "managers/creature/Dna*", SRC + "objects/intangible/PetControlDevice*", SRC + "objects/tangible/component/dna", SRC + "objects/tangible/deed/pet", CMD + "pet", CMD + "TameCommand.h", CMD + "SampleDNACommand.h", SCR + "managers/pet_manager.lua", SCR + "managers/dna_manager.lua"],
        cmds=["tame", "sampledna", "emboldenpets", "enragepets", "tellpet", "healpet"],
        probe="CH agent tames a baby creature, trains 'follow' and 'attack' by chat, calls it on a target; BE agent samples DNA from the same species; assert the pet device and the DNA component.",
        fix="Measure first (CH plan); then decide whether to wire the three dead CH mods."),
    dict(
        id="24", group="Creatures",
        name="Mounts",
        status="implemented",
        gaps=["`/dismountAndStore` is a stub (its body is commented out); use `/dismount`, then store from the control device."],
        evidence=["Mount training `PetControlDeviceImplementation.cpp:1339`, `managers/creature/MountSpeedData.h`, `ValidMountScaleRange.h`; `/gallop`, `/gallopStop`"],
        switches=[],
        paths=[SRC + "managers/creature/Mount*", SRC + "managers/creature/ValidMount*", CMD + "Mount*", CMD + "Dismount*", CMD + "Gallop*"],
        cmds=["gallop", "gallopstop", "dismountandstore"],
        probe="CH agent with Support IV trains a tamed pet as a mount and rides it; assert mounted speed.",
        fix="Optional: make `/dismountAndStore` dismount then store."),
    dict(
        id="25", group="Vehicles",
        name="Vehicles: deeds, calling, riding, repair at garages, decay, customisation",
        status="implemented",
        gaps=["`/customizeVehicle` (granted by Master Artisan) is a stub; customisation kits work from their radial (`VehicleCustomKitObjectMenuComponent.cpp`).",
              "BARC speeder template fixed locally (740b2426); check other custom-content vehicles the same way."],
        evidence=["`objects/creature/VehicleObjectImplementation.cpp` (garage tax `:238`), `objects/intangible/VehicleControlDeviceImplementation.cpp`, `objects/tangible/deed/vehicle/VehicleDeed*`, `RepairVehicleSuiCallback.h`",
                  "Templates `bin/scripts/object/mobile/vehicle/` (landspeeders, speeder bikes, swoop, jetpack); sandbox run speed 30 m/s"],
        switches=[],
        paths=[SRC + "objects/creature/VehicleObject*", SRC + "objects/intangible/VehicleControl*", SRC + "objects/tangible/deed/vehicle", SRC + "objects/tangible/components/VehicleCustomKit*", CMD + "CustomizeVehicle*", SCR + "object/mobile/vehicle"],
        cmds=["mount", "dismount", "customizevehicle"],
        probe="Agent uses a speederbike deed, calls, mounts and drives 200 m, then repairs at a garage; assert speed and the repair charge (agent historically passed deed/call).",
        fix="Point `/customizeVehicle` at the kit code if the client sends it."),
    dict(
        id="26", group="Travel",
        name="Shuttles, starports, tickets, travel coupons and shuttle beacons",
        status="implemented",
        gaps=["Player-city shuttleport's own placement check is commented out (`ShuttleInstallationImplementation.cpp:11-30`), covered by the general civic checks.",
              "No instant-travel terminals or vehicles exist (a later feature); 'instant' travel here = travel coupons and the shuttle-beacon event perk."],
        evidence=["`objects/building/components/ShuttleZoneComponent.cpp`, `managers/planet/PlanetTravelPointList.h` (city travel tax `:98`), `PurchaseTicketCommand.h`, `BoardShuttleCommand.h`, `objects/tangible/ticket/`, `objects/tangible/terminal/ticketcollector/`",
                  "`TravelCouponUseSuiCallback.h`, `objects/tangible/eventperk/ShuttleBeacon*`; sandbox shuttle timings 10 s away, 2 s landing, 600 s landed",
                  "Local Hoth and Ossus travel points (5b2a858f, 2ada3784)"],
        switches=["Core3.PlanetManager.Shuttleport*/Starport* times", "Core3.ShuttleZoneComponent.BootDelay"],
        paths=[SRC + "objects/building/components/Shuttle*", SRC + "objects/building/travel", SRC + "managers/planet/PlanetTravel*", SRC + "managers/planet/TravelFare.h", SRC + "objects/tangible/ticket", SRC + "objects/tangible/terminal/travel", SRC + "objects/tangible/terminal/ticketcollector", SRC + "objects/installation/shuttle", CMD + "PurchaseTicket*", CMD + "BoardShuttle*"],
        cmds=["purchaseticket", "boardshuttle"],
        probe="Agent buys a Mos Eisley to Coronet ticket and boards; assert the planet change (already part of the routine bot runs).",
        fix="None."),
    dict(
        id="27", group="Social",
        name="Groups, chat channels, mail, friends and ignore, waypoints",
        status="implemented",
        gaps=["`/splitCreditsWithGroup` is a stub (looted credits auto-split, `GroupLootTask.h:126`).",
              "`/getFriendList`, `/getIgnoreList`, `/spatialChat`, `/social` are stubs; the *internal* variants and client packets do the work.",
              "Test-side gap: the agent body cannot send or read tells (feature register F24)."],
        evidence=["`managers/group/GroupManager.cpp`, `objects/group/GroupObject*` (galaxy-wide grouping switch)", "`server/chat/ChatManagerImplementation.cpp`, chat rooms, `PersistentMessage` mail, `SendMailTask.h`"],
        switches=["Core3.PlayerManager.GalaxyWideGrouping", "Core3.PlayerManager.DisableGroupVisibility", "Core3.CleanupMailCount", "Core3.ChatManager.PvpBroadcastChannel"],
        paths=[SRC + "managers/group", SRC + "objects/group", MM + "src/server/chat", SRC + "objects/waypoint"],
        cmds=["groupchat", "groupsay", "gsay", "gtell", "planetsay", "planet", "spatialchat", "spatialchatinternal", "socialinternal", "social", "setmood", "setmoodinternal", "invite", "uninvite", "join", "decline", "leavegroup", "disband", "dismissgroupmember", "makeleader", "addfriend", "removefriend", "findfriend", "getfriendlist", "addignore", "removeignore", "getignorelist", "waypoint", "setwaypointname", "setwaypointactivestatus", "requestwaypointatposition", "find", "getmaplocations", "addmaplocation", "splitcreditswithgroup", "comm", "systemmessage"],
        probe="Two agents group, one mails the other; assert group membership and the mail in the inbox (grouping already tested).",
        fix="Give the agent body tells (F24) before testing chat."),
    dict(
        id="28", group="Social",
        name="Guilds",
        status="implemented",
        gaps=["`/paWithdraw` (guild treasury) is a stub."],
        evidence=["`managers/guild/GuildManagerImplementation.cpp`: create, rename, sponsor, kick, titles, permissions, guild wars, leader elections, guild hall transfer (`GuildManager.idl:71-204`)"],
        switches=[],
        paths=[SRC + "managers/guild", SRC + "objects/guild", SCR + "managers/guild_manager.lua"],
        cmds=["guild", "guildremove", "guildsay", "guildstatus", "pawithdraw", "g"],
        probe="Agent creates a guild at a guild terminal and sponsors a second agent; assert both in the member list.",
        fix="None for play."),
    dict(
        id="29", group="Quests",
        name="Quests and themeparks, dungeons, caves and POIs",
        status="implemented",
        gaps=["Corellian Corvette spawns at fixed spots (TODO `corellianCorvette.lua:698,843`).",
              "Implemented in Lua; individual quest steps have not been played through here."],
        evidence=["Themeparks `screenplays/themepark/`: Jabba, Imperial (with Emperor's Retreat), Rebel, Nym, Marauder (3), Nightsister, SMC (3), Valarian, helper droid",
                  "Dungeons `screenplays/dungeon/`: Corellian Corvette, Death Watch Bunker, Geonosian Lab, Warren; 39 caves and bunkers, 59 POIs, 184 task screenplays, events (Life Day, Bestine election and museum, COA, race droid)",
                  "637 active `includeFile` lines in `screenplays/screenplays.lua`, none commented out; local Hoth quest chain and The Beginning (MTG)"],
        switches=[],
        paths=[SCR + "screenplays/themepark", SCR + "screenplays/dungeon", SCR + "screenplays/caves", SCR + "screenplays/poi", SCR + "screenplays/tasks", SCR + "screenplays/events", SCR + "screenplays/quest_tasks", SCR + "managers/quest"],
        cmds=["requestquesttimersandcounters"],
        probe="Agent talks to a Jabba themepark giver and completes step one; assert the quest waypoint (agent already observes quest waypoints) and the reward.",
        fix="None in code; play-through testing."),
    dict(
        id="30", group="Jedi",
        name="Force-sensitive unlock path (Village of Aurilia)",
        status="implemented",
        gaps=["Hologrind progression exists (`hologrind_jedi_manager.lua`) but is not selected: `jediProgressionType = VILLAGEJEDIPROGRESSION` (`managers/jedi/jedi_manager.lua:14`).",
              "Village phases shortened to 7 days in the sandbox (`village_jedi_manager_township.lua:12`; the comment still says 3 weeks)."],
        evidence=["84 village screenplays `screenplays/village/` (phases 1-4, raids, community crafting), Jedi trials `screenplays/jedi/`", "`managers/jedi/JediManager`, staff `/gmFsVillage`, `/gmJediState` implemented"],
        switches=["jedi_manager.lua jediProgressionType", "VILLAGE_PHASE_DURATION", "Core3.Sandbox.JediXpMultiplier"],
        paths=[SRC + "managers/jedi", SCR + "managers/jedi", SCR + "screenplays/village", SCR + "screenplays/jedi"],
        cmds=["checkforcestatus"],
        probe="Staff `/gmJediState` an agent to force-sensitive, run one village quest; assert the FS branch box and quest state.",
        fix="Owner decision: keep Village or switch to Hologrind for an older pre-CU feel (config)."),
    dict(
        id="31", group="Jedi",
        name="Jedi skill trees, Force powers, visibility, Force Ranking System",
        status="implemented",
        gaps=["`/forceProtection` is a stub; staff `/gmForceRank` and `/overridePadawanTrialsEligibility` are stubs.",
              "`/regainConsciousness` has message TODOs (`RegainConsciousnessCommand.h:39,48`)."],
        evidence=["Force commands on `JediCombatQueueCommand`, `ForcePowersQueueCommand`, `ForceHealQueueCommand`, `JediQueueCommand` (113 commands mapped to this row)",
                  "FRS: `managers/frs/` (11 files), `bin/scripts/managers/jedi/frs_manager.lua` (`frsEnabled = 1`, enclave voting, arena challenges, rank XP)",
                  "Visibility: `managers/visibility/`, `visibility_manager.lua`"],
        switches=["frs_manager.lua frsEnabled", "Core3.FrsManager.ImmediateMaintXpDeduction"],
        paths=[SRC + "managers/frs", SRC + "managers/visibility", CMD + "Force*", CMD + "Jedi*", CMD + "Saber*", SCR + "managers/jedi/frs_manager.lua", SCR + "managers/jedi/visibility_manager.lua"],
        cmds=["channelforce", "drainforce", "transferforce", "regainconsciousness", "showcouncilrank", "avoidincapacitation", "forcemeditate"],
        probe="Staff-granted Padawan agent uses one Force power on a creature and one heal on itself; assert Force pool drop and visibility rise.",
        fix="None for play."),
    dict(
        id="32", group="Space",
        name="Space (Jump to Lightspeed): ships, components, space zones, combat, quests, POB ships",
        status="partial",
        gaps=["Upstream default is off: `Core3.JTL.JTLEnabled` and `Core3.JTL.LaunchFromDevice` default false; the sandbox profile records both on (set in config-local.lua, not read here). Space NPC conversations check `isJtlEnabled()`.",
              "22 space combat commands have no Lua script, so defaults apply (bstrike, epulse, eshields, ethrust, eweapons, iffscramble, inspace*, jstart, nblast, ptrap, pumpreactor, vrepair...).",
              "`/repairShipComponentInSlot`, `/unassociateDroidControlDeviceWithShip` are stubs; `/installShipComponent` has a TODO; space spawner doesn't refill to max (`SpaceSpawnObserverImplementation.cpp:45`)."],
        evidence=["`managers/space`, `managers/ship`, `managers/spacecombat`, `managers/spacecollision`; ship classes `objects/ship/` (Fighter, POB, MultiPassenger, Capital, ship AI)",
                  "10 space zones in `bin/conf/config.lua` `SpaceZonesEnabled`; 1925 ship mobiles; quests `screenplays/space/` (patrol, destroy, assassinate; 9 squadron screenplays)",
                  "Shipwright crafting: 336 space schematics"],
        switches=["Core3.JTL.JTLEnabled (default false)", "Core3.JTL.LaunchFromDevice (default false)", "Core3.SpaceZonesEnabled", "Core3.Regions.DisableSpaceSpawns"],
        paths=[SRC + "managers/space", SRC + "managers/ship", SRC + "managers/spacecombat", SRC + "managers/spacecollision", SRC + "objects/ship", SCR + "screenplays/space", SCR + "managers/space", CMD + "SpaceQueueCommand.h", CMD + "*Ship*"],
        cmds=["pilotship", "unpilotship", "launchintospace", "hyperspace", "aborthyperspace", "dock", "undock", "eject", "escapepod", "launchmissile", "launchcountermeasure", "lightenginescramble", "installshipcomponent", "uninstallshipcomponent", "insertitemintoshipcomponentslot", "repairshipcomponentinslot", "associatedroidcontroldevicewithship", "unassociatedroidcontroldevicewithship", "requestspacetrainer", "serverasteroiddatalisten", "serverasteroiddatastoplistening", "boosteron", "boosteroff", "leavestation", "openwings", "closewings", "inspect", "bstrike1", "bstrike2", "bstrike3", "epulse1", "epulse2", "epulse3", "eshields", "ethrust", "eweapons", "iffscramble", "inspacereload", "inspacerepair", "inspacerr", "jstart1", "jstart2", "jstart3", "nblast", "ptrap1", "ptrap2", "pumpreactor", "vrepair", "vrepairother"],
        probe="Agent launches a starter ship from its device into space_tatooine and destroys one tier-1 NPC; assert the kill and the ship's damage state. Needs a flying agent (not built).",
        fix="Flight testing first; then scripts for the 22 unscripted commands and the component repair command."),
    dict(
        id="33", group="Smaller systems",
        name="Badges and exploration badges",
        status="implemented", gaps=[],
        evidence=["`objects/player/badges/` (BadgeList, Badges), `objects/area/BadgeActiveArea*`, `/requestBadges`, staff `/grantBadge`/`/revokeBadge`"],
        switches=[], paths=[SRC + "objects/player/badges", SRC + "objects/area/BadgeActiveArea*", CMD + "*Badge*"],
        cmds=["requestbadges"],
        probe="Agent walks into an exploration badge area; assert the badge in `/requestBadges`.", fix="None."),
    dict(
        id="34", group="Smaller systems",
        name="Collections",
        status="missing",
        gaps=["No collection system (only loot-group 'collections'). Collections are NGE; note only."],
        evidence=["No collection code in `src/server/zone/objects/player/`"], switches=[], paths=[], cmds=[],
        probe="Not applicable.", fix="Leave out for pre-CU."),
    dict(
        id="35", group="Smaller systems",
        name="New-player tutorial",
        status="disabled",
        gaps=["`Core3.PlayerCreationManager.EnableTutorial` defaults false and is not set in `bin/conf/config.lua` (config-local.lua not read, so the live value is unsure). The `tutorial` zone is loaded and its screenplays exist."],
        evidence=["`PlayerCreationManager.cpp:400`; `screenplays/tutorial/` (12 includes); stat migration is free in the tutorial zone (`RequestSetStatMigrationDataCommand.h:86-94`)"],
        switches=["Core3.PlayerCreationManager.EnableTutorial (default false)"],
        paths=[SCR + "screenplays/tutorial"], cmds=[],
        probe="Create a character with the switch on; assert it starts in the tutorial zone.",
        fix="Owner choice: turn on if new players should get the tutorial."),
    dict(
        id="36", group="Smaller systems",
        name="Gambling mini-games (slot machines, roulette, sabacc)",
        status="partial",
        gaps=["Sabacc is commented out (`GamblingTerminal.idl:59`); only slot machines and roulette work. Pazaak is not in the game (and not pre-CU)."],
        evidence=["`managers/minigames/GamblingManagerImplementation.cpp`, `objects/tangible/terminal/gambling/GamblingTerminal*`, `/bet`"],
        switches=[], paths=[SRC + "managers/minigames/Gambling*", SRC + "objects/tangible/terminal/gambling"],
        cmds=["bet"],
        probe="Agent uses a slot machine in a cantina and `/bet`s 10; assert credits change.",
        fix="Sabacc needs a full card game and UI: large; skip unless wanted."),
    dict(
        id="37", group="Smaller systems",
        name="Swoop and speeder racing",
        status="implemented", gaps=[],
        evidence=["`screenplays/racetracks/` engine plus 6 tracks (Agrilat swamp, Keren, Lok, Mos Espa, Narmle, Nashal)"],
        switches=[], paths=[SCR + "screenplays/racetracks"], cmds=[],
        probe="Agent on a speeder starts the Mos Espa race and passes every waypoint; assert the finish time message.", fix="None."),
    dict(
        id="38", group="Smaller systems",
        name="Camps",
        status="implemented", gaps=[],
        evidence=["`objects/area/CampSiteActiveAreaImplementation.cpp`, camp kit and terminal menu components, `CampAbandonTask`, `CampDespawnTask`"],
        switches=[], paths=[SRC + "objects/area/Camp*", SRC + "objects/area/events/Camp*", SRC + "objects/tangible/components/Camp*"], cmds=[],
        probe="Scout agent drops a basic camp kit outdoors; assert the camp terminal and the healing-in-camp effect.", fix="None."),
    dict(
        id="39", group="Smaller systems",
        name="Foraging and fishing",
        status="implemented",
        gaps=["Fishing TODOs: water vegetation and density not modelled, bait stacks consumed whole (`FishingManager.idl:136-412`)."],
        evidence=["`managers/minigames/ForageManagerImplementation.cpp`, `FishingManagerImplementation.cpp`, `/forage`, `/fish`, fishing pole/bait/fish objects"],
        switches=[], paths=[SRC + "managers/minigames/Forag*", SRC + "managers/minigames/Fish*", SRC + "objects/tangible/fishing"],
        cmds=["forage", "fish"],
        probe="Scout agent `/forage`s 3 times outdoors; assert an item appears. Fishing: equip pole and bait, `/fish` at water.", fix="None for play."),
    dict(
        id="40", group="Smaller systems",
        name="Food, drink, Chef buffs and spice",
        status="implemented",
        gaps=["`/eat` is a stub (eating works from the item radial); instant-effect foods share one generic handler (TODO `ConsumableImplementation.cpp:306`)."],
        evidence=["`objects/tangible/consumable/ConsumableImplementation.cpp`, `DelayedBuffObserver`, spice buffs and downers (`objects/creature/buffs/SpiceBuff*`); 123 food and 17 spice schematics"],
        switches=[], paths=[SRC + "objects/tangible/consumable", SRC + "objects/creature/buffs/Spice*"],
        cmds=["eat"],
        probe="Agent uses a crafted food from the radial; assert the buff on the character.", fix="None."),
    dict(
        id="41", group="Smaller systems",
        name="Droids and Droid Engineer modules",
        status="implemented",
        gaps=["`/assignDroid` and `/customizeDroid` are stubs."],
        evidence=["`objects/tangible/components/droid/` (46 files: armor, combat, crafting, harvest, medical, merchant barker, stimpack, trap, repair, storage, playback, personality, detonation...)", "`/detonateDroid`, `/healDroidDamage`, `/healDroidWound`, droid pet commands"],
        switches=[], paths=[SRC + "objects/tangible/components/droid", SRC + "objects/creature/ai/DroidObject*", SRC + "managers/crafting/labratories/DroidLabratory*"],
        cmds=["droid", "detonatedroid", "healdroiddamage", "healdroidwound", "assigndroid", "customizedroid"],
        probe="Droid Engineer agent crafts a droid with one module and calls it; assert the module's radial option.", fix="None for play."),
    dict(
        id="42", group="Smaller systems",
        name="Slicing (Smuggler)",
        status="implemented",
        gaps=["Smuggler perk `language_all_comprehend` has no reader."],
        evidence=["`objects/player/sessions/SlicingSessionImplementation.cpp` (skill by box name `:242-261`), slicing tools, GCW security slicing (`managers/gcw/tasks/SecuritySliceTask.h`)"],
        switches=[], paths=[SRC + "objects/player/sessions/SlicingSession*", SRC + "objects/tangible/tool/smuggler"], cmds=[],
        probe="Smuggler agent slices a weapon with a tool kit; assert the changed weapon stat.", fix="Wire the language perk if wanted."),
    dict(
        id="43", group="World",
        name="NPC conversations and social reactions",
        status="implemented",
        gaps=["Ship AI has no reaction chat (`ShipAiAgentImplementation.cpp:1970`)."],
        evidence=["`managers/conversation/`, 306 conversation templates (`bin/scripts/mobile/conversations/`), `managers/reaction/` with `reaction_manager.lua`"],
        switches=[], paths=[SRC + "managers/conversation", SRC + "managers/reaction", SCR + "managers/reaction_manager.lua"],
        cmds=["npcconversationselect", "npcconversationstart", "npcconversationstop"],
        probe="Agent opens and closes a conversation with a trainer; assert the options list.", fix="None."),
    dict(
        id="44", group="World",
        name="Weather",
        status="implemented", gaps=[],
        evidence=["`managers/weather/` (4 files), `bin/scripts/managers/weather_manager.lua`"],
        switches=[], paths=[SRC + "managers/weather", SCR + "managers/weather_manager.lua"], cmds=[],
        probe="Staff changes weather on one planet; assert the client weather packet.", fix="None."),
    dict(
        id="45", group="World",
        name="Veteran rewards and event perks",
        status="implemented",
        gaps=["Staff `/hasVeteranReward`, `/setVeteranReward` are stubs; `/launchFirework` is a stub (fireworks launch from the item radial; check)."],
        evidence=["`managers/player/VeteranReward.h`, `/claimVeteranReward`; event perks `objects/tangible/eventperk/` (lottery droid, shuttle beacon, flag game, ...), `screenplays/events/eventPerkData.lua`"],
        switches=[], paths=[SRC + "objects/tangible/eventperk", SRC + "managers/player/VeteranReward.h"],
        cmds=["claimveteranreward", "getveteranrewardtime", "getveteranrewardtimecs", "overrideactivemonths", "launchfirework", "flashspeeder"],
        probe="Agent claims a veteran reward; assert the item in inventory.", fix="None."),
    dict(
        id="46", group="Admin",
        name="Customer service tickets and in-game bug reports",
        status="stub",
        gaps=["All ten `/cs*` ticket commands, `/report` and `/executeKnowledgeBaseMessage` are stubs.",
              "Holocron bug reports write to the Mantis database, but the reply packet is disabled (`HolocronManager.cpp:92`); `Core3.AccountManager.HolocronTicketsEnabled` defaults false."],
        evidence=["`managers/holocron/HolocronManager.cpp`; stub headers `objects/creature/commands/Cs*.h`"],
        switches=["Core3.AccountManager.HolocronTicketsEnabled (default false)"],
        paths=[SRC + "managers/holocron", CMD + "Cs*"],
        cmds=["report", "executeknowledgebasemessage"],
        probe="Not worth a bot probe on a LAN server.", fix="Leave out; use Discord or a text file for reports."),
    dict(
        id="47", group="Admin",
        name="Admin and staff tools",
        status="partial",
        gaps=["Staff commands that are stubs include `/money`, `/setRank`, `/getRank`, `/planetWarp`, `/editBank`, `/editStats`, `/maxStats`, `/grantTitle`, spawner controls (`/startSpawner`, `/stopSpawner`, `/setMinimumSpawnTime`...), `/setLoginMessage`. See `Documentation-support/core3-command-audit.md`.",
              "Web and REST admin off by default (`MakeWeb = 0`, `RESTServerPort = 0`)."],
        evidence=["117 staff commands; `/setGodMode`, `/teleport`, `/grantSkill`, `/credits`, `/broadcast`, `/script`, `/server`, `/createCreature` etc. are real",
                  "Character builder terminal on (`CharacterBuilderEnabled = \"true\"` in `bin/conf/config.lua`); local `/spawnStatus` and `/showSpawnRegion` made real (34d4772a)"],
        switches=["Core3.CharacterBuilderEnabled", "Core3.MakeWeb", "Core3.RESTServerPort", "Core3.CommandConfigManager.DumpAdminCommands"],
        paths=[MM + "bin/scripts/staff", SRC + "managers/director", CMD + "Server*", CMD + "Admin*"],
        cmds=["gc", "starttracelogging", "stoptracelogging", "secretspawnspam", "npc", "objvar", "remote", "setgodmode", "serverdestroyobject", "serversysgroup", "gmforcecommand", "unsnoop"],
        probe="Staff agent runs each staff command once in a test galaxy and records whether anything changed (stub list already known).",
        fix="Write the handful of stubs the owner actually uses (`/money`, `/planetWarp`, `/setRank`, spawner controls)."),
    dict(
        id="48", group="Infrastructure",
        name="Login, logout, containers, inventory and UI plumbing",
        status="implemented",
        gaps=["`/logout` is a stub while `/logoutServer` is implemented; unsure which one the client's logout uses, so check the 30-second countdown in game. `/joinGame`, `/leaveGame`, `/transferItem` are stubs (the typed `/transferItem*` variants are real)."],
        evidence=["`objects/player/PlayerObjectImplementation.cpp` link-dead and logout handling (`Core3.PlayerObject.LinkDeadDelay`, `AlwaysSafeLogout`)", "`/openContainer`, `/closeContainer`, `/transferItemArmor`/`Misc`/`Weapon` implemented"],
        switches=["Core3.PlayerObject.LinkDeadDelay", "Core3.PlayerObject.AlwaysSafeLogout", "Core3.UnloadContainers"],
        paths=[CMD + "Logout*", CMD + "TransferItem*", CMD + "OpenContainer*", CMD + "CloseContainer*"],
        cmds=["logout", "logoutserver", "joingame", "leavegame", "reconnecttotransferserver", "opencontainer", "closecontainer", "transferitem", "transferitemarmor", "transferitemmisc", "transferitemweapon", "synchronizeduilisten", "synchronizeduistoplistening", "unstick", "setspeed"],
        probe="Agent logs out from the menu; assert the countdown messages and the character offline after 30 s.", fix="None expected."),
    dict(
        id="49", group="Local additions",
        name="Local sandbox additions (agent body, leash, mercenaries, world bosses, Hoth, Ossus, Chiss, Botanist)",
        status="implemented",
        gaps=["Test-only or dev-only; see `SWG-feature-register.md` F14-F31, F46. Not part of the pre-CU baseline."],
        evidence=["Local commits on top of upstream 403893d9: `/agentgear`, `/agentpath`, `/agentskill`, `/leash`, mercenary broker, world boss rotation, Hoth and Ossus zones, Chiss species, Botanist trainer"],
        switches=["Core3.AgentGear (default false)", "Core3.AgentAccounts", "Core3.LeashEnabled"],
        paths=[SCR + "screenplays/sandbox", SCR + "managers/planet/hoth_regions.lua", SCR + "managers/planet/ossus_regions.lua"],
        cmds=["agentgear", "agentpath", "agentskill", "leash"],
        probe="Covered by the existing bot squads.", fix="Keep separate from baseline work."),
]

BIGGEST_GAPS = [
    ("32", "Space (Jump to Lightspeed)", "Only partly done and off by default upstream: 22 space combat commands have no script, component repair is a stub, and nothing has been flight-tested here. It is the largest system on the list."),
    ("47", "Staff tools", "43 of 117 staff commands are still stubs, among them `/money`, `/planetWarp`, `/setRank`, `/grantTitle` and the spawner controls (the audit counted 45; `/spawnStatus` and `/showSpawnRegion` have since been made real locally). This affects running the server every day."),
    ("15", "Player cities and Politician", "Two of eight specialisations (Clone Lab, Entertainment District) cost 80,000 credits and do nothing; militia have no law-enforcement powers; `/cityWarn` and city guards are missing; the weekly cadence hides everything in short tests."),
    ("18", "Battlefields", "Markers only, no rules, and the three battlefield commands do nothing. This is the main pre-CU PvP content gap."),
    ("7", "Image Designer", "The server trusts the client on colour palettes and holo-emote purchases, and stat migration only works in the 4 salon templates. Otherwise the code is complete, not bare bones."),
    ("21", "Bounty Hunter", "No mission failure when someone else kills the target; `bounty_mission_level` is unread."),
    ("23", "Creature Handler and pets", "Owner priority. The code is complete, but the three CH skill mods (`private_creature_empathy`, `_training`, `_management`) are read nowhere, and pet balance and AI reliability have never been measured."),
    ("36", "Gambling", "Sabacc is commented out; only slot machines and roulette work."),
    ("35", "Tutorial", "Off by default although the zone is loaded (owner choice)."),
    ("10", "Stubs to check in game", "`/harvesterHarvest`, `/harvesterMakeCrate`, `/harvesterTakeSurvey` and `/lootAll` are stubs that matter only if the pre-CU client sends them: check before building anything."),
]

# Families of commands not listed by name above.
JEDI_BASES = {"JediCombatQueueCommand", "ForcePowersQueueCommand", "ForceHealQueueCommand", "JediQueueCommand"}
CMD_RULES = [
    ("49", lambda r: r["command"] in {"agentgear", "agentpath", "agentskill", "leash"}),
    ("47", lambda r: any(g.startswith("admin_") for g in r["granted_by"])),
    ("NAMED", None),  # explicit cmds lists are applied at this point
    ("32", lambda r: r["base"] == "SpaceQueueCommand"),
    ("31", lambda r: r["base"] in JEDI_BASES or re.match(r"^(force|saber|jedi)", r["command"])),
    ("23", lambda r: r["command"].startswith("pet")),
    ("46", lambda r: r["command"].startswith("cs")),
    ("5", lambda r: re.match(r"^(heal|tend|cure|apply)", r["command"]) or r["base"] in {"CurePackCommand", "DotPackCommand", "TendCommand"}),
    ("2", lambda r: r["base"] in {"CombatQueueCommand", "SquadLeaderCommand"}),
]


# --------------------------------------------------------------------------
# WSL helpers (read-only)
# --------------------------------------------------------------------------
def to_wsl(path):
    path = os.path.abspath(path).replace("\\", "/")
    m = re.match(r"^([A-Za-z]):/(.*)$", path)
    return "/mnt/%s/%s" % (m.group(1).lower(), m.group(2)) if m else path


def sh_quote(s):
    return "'" + s.replace("'", "'\"'\"'") + "'"


def run_wsl(script_text):
    fd, path = tempfile.mkstemp(prefix="systems_baseline_", suffix=".sh")
    with os.fdopen(fd, "w", newline="\n", encoding="utf-8") as f:
        f.write(script_text)
    env = dict(os.environ, MSYS_NO_PATHCONV="1")
    try:
        p = subprocess.run(["wsl", "-d", DISTRO, "-u", "root", "--", "bash", to_wsl(path)],
                           capture_output=True, env=env)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
    out = p.stdout.decode("utf-8", "replace")
    if p.returncode != 0 and not out:
        sys.exit("WSL script failed: " + p.stderr.decode("utf-8", "replace")[:2000])
    return out


def collect_repo_data(stub_files, token_out):
    lines = ["set -u", "cd %s || exit 1" % REPO, "G='git -c safe.directory=*'",
             'echo "@@HEAD $($G log -1 --format=\'%h %ad %s\' --date=short | cut -c1-150)"',
             'echo "@@LOCALCOMMITS $($G rev-list --count 403893d9..HEAD 2>/dev/null)"']
    for s in SYSTEMS:
        if not s["paths"]:
            lines.append('echo "@@SYS %s files=0 loc=0 todo=0"' % s["id"])
            continue
        specs = " ".join(sh_quote(p) for p in s["paths"])
        lines += [
            "F=$($G ls-files -- %s)" % specs,
            'NF=$(printf "%s" "$F" | grep -c . || true)',
            'LOC=$(printf "%s\\n" "$F" | grep . | xargs -r cat 2>/dev/null | wc -l)',
            "$G grep -n -I -i -E %s -- %s > /tmp/sb_hits.$$ 2>/dev/null || true" % (sh_quote(TODO_RE), specs),
            'echo "@@SYS %s files=$NF loc=$LOC todo=$(wc -l < /tmp/sb_hits.$$)"' % s["id"],
            'head -4 /tmp/sb_hits.$$ | cut -c1-200 | sed "s/^/@@HIT %s /"' % s["id"],
            "rm -f /tmp/sb_hits.$$",
        ]
    # Re-check audit stubs: count lines in the handler beyond the stub boilerplate.
    lines.append("for f in %s; do" % " ".join(sh_quote(f) for f in stub_files))
    lines.append(r"""  if [ -f "MMOCoreORB/$f" ]; then n=$(perl -0777 -pe 's{/\*.*?\*/}{}gs' "MMOCoreORB/$f" | awk '/doQueueCommand/{on=1} on' | grep -v -E '^\s*$|^\s*//|doQueueCommand|checkStateMask|checkInvalidLocomotions|return (INVALIDSTATE|INVALIDLOCOMOTION|SUCCESS);|^\s*[{}];?\s*$|^#endif|^\s*\};' | wc -l); echo "@@STUB $f $n"; else echo "@@STUB $f missing"; fi""")
    lines.append("done")
    lines.append("$G grep -h -o -I -E '\"[A-Za-z0-9_]{3,70}\"' -- MMOCoreORB/src ':!MMOCoreORB/src/client' MMOCoreORB/bin/scripts ':!MMOCoreORB/bin/scripts/object/custom_content' ':!MMOCoreORB/bin/scripts/mobile/custom_content' | sort -u > %s" % sh_quote(to_wsl(token_out)))
    lines.append('echo "@@TOKENS done"')
    out = run_wsl("\n".join(lines) + "\n")
    data = {"head": "", "local_commits": "", "sys": {}, "hits": collections.defaultdict(list), "stub": {}}
    for line in out.splitlines():
        if line.startswith("@@HEAD "):
            data["head"] = line[7:].strip()
        elif line.startswith("@@LOCALCOMMITS "):
            data["local_commits"] = line[15:].strip()
        elif line.startswith("@@SYS "):
            parts = line.split()
            kv = dict(p.split("=", 1) for p in parts[2:])
            data["sys"][parts[1]] = {k: int(v) for k, v in kv.items()}
        elif line.startswith("@@HIT "):
            _, sid, rest = line.split(" ", 2)
            data["hits"][sid].append(rest.replace("MMOCoreORB/", "", 1))
        elif line.startswith("@@STUB "):
            _, f, n = line.split(" ", 2)
            data["stub"][f] = n
    return data


# --------------------------------------------------------------------------
# Commands and professions
# --------------------------------------------------------------------------
def map_commands(audit_rows, stub_recheck):
    named = {}
    for s in SYSTEMS:
        for c in s["cmds"]:
            named.setdefault(c, s["id"])
    out = collections.defaultdict(list)
    for r in audit_rows:
        status = r["status"]
        if status == "stub":
            n = stub_recheck.get(r["file"].replace("MMOCoreORB/", ""), "0")
            if n not in ("0", "missing"):
                status = "implemented*"  # was a stub when the audit ran; has code now
        sid = None
        for rid, rule in CMD_RULES:
            if rid == "NAMED":
                if r["command"] in named:
                    sid = named[r["command"]]
                    break
            elif rule(r):
                sid = rid
                break
        out[sid or "unassigned"].append(dict(command=r["command"], status=status, base=r["base"],
                                             staff=any(g.startswith("admin_") for g in r["granted_by"])))
    return out


def summarise_cmds(rows):
    c = collections.Counter(r["status"] for r in rows)
    return dict(total=len(rows), implemented=c["implemented"] + c["implemented*"], base_class=c["base-class"],
                inherits=c["inherits"], todo=c["todo"], stub=c["stub"],
                fixed_since_audit=sorted(r["command"] for r in rows if r["status"] == "implemented*"),
                stub_names=sorted(r["command"] for r in rows if r["status"] == "stub"),
                todo_names=sorted(r["command"] for r in rows if r["status"] == "todo"))


def profession_refs(tokens):
    if not os.path.exists(PROFESSIONS_JSON):
        return []
    prof = json.load(open(PROFESSIONS_JSON, encoding="utf-8"))
    res = []
    for pr in prof["professions"]:
        mods, flags = {}, {}
        for b in pr["boxes"]:
            for m in b["skill_mods"]:
                mods[m] = 1
            slash = {c["ability"]: c["slash"] for c in b.get("commands", [])}
            for a in b["abilities"]:
                if not slash.get(a):
                    flags[a] = 1
        res.append(dict(profession=pr["name"], english=pr.get("english_name", ""),
                        skill_mods=len(mods), mods_no_reader=sorted(m for m in mods if m not in tokens),
                        ability_flags=len(flags), flags_no_reader=sorted(a for a in flags if a not in tokens)))
    return res


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------
def md_cell(text):
    return text.replace("|", "\\|").replace("\n", " ")


def write_outputs(repo, cmdmap, profs, audit_meta):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    systems = []
    for s in SYSTEMS:
        code = repo["sys"].get(s["id"], {"files": 0, "loc": 0, "todo": 0})
        systems.append(dict(
            id=s["id"], group=s["group"], name=s["name"], status=s["status"], gaps=s["gaps"],
            evidence=s["evidence"], config_switches=s["switches"],
            code=dict(paths=s["paths"], files=code["files"], lines=code["loc"], todo_hits=code["todo"],
                      todo_samples=repo["hits"].get(s["id"], [])),
            commands=summarise_cmds(cmdmap.get(s["id"], [])),
            bot_probe=s["probe"], fix_work=s["fix"]))
    counts = collections.Counter(s["status"] for s in SYSTEMS)
    status_counts = {k: counts.get(k, 0) for k in STATUSES}
    unassigned = summarise_cmds(cmdmap.get("unassigned", []))
    meta = dict(generated=now, generator="outputs/Systems-baseline/build_systems.py", repo=REPO,
                head=repo["head"], local_commits_since_upstream_403893d9=repo["local_commits"],
                command_audit=audit_meta, method=(
                    "Static reading of server source only; 'implemented' means code exists, not that it was "
                    "tested. Code counts are git ls-files/git grep over each system's paths; TODO hits match "
                    + TODO_RE + ". Commands from the command audit, stubs re-checked against the current headers."))
    doc = dict(meta=meta, status_counts=status_counts,
               biggest_gaps=[dict(system=i, label=l, text=t) for i, l, t in BIGGEST_GAPS],
               systems=systems, unassigned_commands=unassigned, professions=profs)
    with open(os.path.join(HERE, "systems.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)

    byid = {s["id"]: s for s in systems}
    L = []
    L.append("# Core3 systems baseline (static code layer)")
    L.append("")
    L.append("Generated %s by `build_systems.py` (re-run it after server changes). Source: `%s` at `%s`; %s local commits on top of upstream SWGEmu Core3 `403893d9`. Commands from `tools/core3_audit/command_audit.json` (%s), with every audit stub re-checked against today's headers." % (now, REPO, repo["head"], repo["local_commits"], audit_meta))
    L.append("")
    L.append("**This is the static layer only.** \"Implemented\" means the code exists and looks complete, not that it works in game. Bot probes in the last-but-one column are the next layer. A slash command marked stub is not necessarily a missing feature: many features run on client packets or radial menus instead.")
    L.append("")
    L.append("**Status counts (%d systems):** %s." % (len(SYSTEMS), ", ".join("%s %d" % (k, v) for k, v in status_counts.items())))
    L.append("")
    L.append("## Biggest gaps, ranked by effect on play")
    L.append("")
    for n, (sid, label, text) in enumerate(BIGGEST_GAPS, 1):
        L.append("%d. **%s** (row %s, %s). %s" % (n, label, sid, byid[sid]["status"], text))
    L.append("")
    L.append("Deep dive on Image Designer, Politician and thin professions: [id-politician-gaps.md](id-politician-gaps.md).")
    L.append("")
    L.append("## Systems")
    L.append("")
    L.append("Code = files / lines / TODO-FIXME-\"not implemented\" hits in the system's paths (see `systems.json` for the paths and sample hits). Commands = implemented (incl. shared-engine and inherited) / stub / todo, from the audit.")
    L.append("")
    L.append("| # | System | Status | Evidence | Commands impl / stub / todo | Bot probe | Fix or build work |")
    L.append("|---|---|---|---|---|---|---|")
    for s in systems:
        c = s["commands"]
        impl = c["implemented"] + c["base_class"] + c["inherits"]
        status = "**%s**" % s["status"]
        if s["gaps"]:
            status += ": " + " ".join(s["gaps"])
        ev = "; ".join(s["evidence"])
        ev += ". Code %d files / %d lines / %d TODO." % (s["code"]["files"], s["code"]["lines"], s["code"]["todo_hits"])
        if s["config_switches"]:
            ev += " Switches: " + ", ".join(s["config_switches"]) + "."
        cm = "%d / %d / %d" % (impl, c["stub"], c["todo"])
        if c["stub_names"]:
            cm += "; stubs: " + ", ".join("`/%s`" % x for x in c["stub_names"][:12]) + (" ..." if len(c["stub_names"]) > 12 else "")
        if c["fixed_since_audit"]:
            cm += "; fixed since audit: " + ", ".join("`/%s`" % x for x in c["fixed_since_audit"])
        L.append("| %s | %s | %s | %s | %s | %s | %s |" % (s["id"], md_cell(s["name"]), md_cell(status), md_cell(ev), md_cell(cm), md_cell(s["bot_probe"]), md_cell(s["fix_work"])))
    L.append("")
    L.append("## Professions: perks with no server reader")
    L.append("")
    L.append("For each profession, how many of its skill mods and non-command ability flags (from `skills.iff`) never appear as a string anywhere in `src/` or `bin/scripts/` (custom content excluded). Many flags are client-side tooltips while the server checks the skill box name instead, and some names are built at runtime, so treat these as leads. Checked examples of false leads: Merchant fee perks (checked by skill box in `AuctionManagerImplementation.cpp:744-749`), Creature Handler pet commands (by box, `PetControlDeviceImplementation.cpp:1296-1309`), Smuggler slicing (by box, `SlicingSessionImplementation.cpp:242-261`), damage mitigation (name built at runtime, `CombatManager.cpp:1281-1298`). Professions with nothing unread are left out.")
    L.append("")
    L.append("`private_*_combat_difficulty` names are unread for every combat profession and are probably client-side difficulty markers; `private_place_*` mods are client-side too (the server checks the `place_*` ability). Flags named `private_<profession>_<box>` are box markers and are left out of the last column.")
    L.append("")
    L.append("| Profession | Mods unread / total | Unread mods | Unread ability flags (excluding box markers) |")
    L.append("|---|---|---|---|")
    for p in profs:
        flags = [a for a in p["flags_no_reader"] if not a.startswith("private_")]
        if not p["mods_no_reader"] and not flags:
            continue
        L.append("| %s | %d / %d | %s | %s |" % (p["profession"], len(p["mods_no_reader"]), p["skill_mods"], ", ".join("`%s`" % m for m in p["mods_no_reader"]) or "-", (", ".join("`%s`" % a for a in flags[:10]) + (" ..." if len(flags) > 10 else "")) or "-"))
    L.append("")
    L.append("## Commands not mapped to a system")
    L.append("")
    L.append("%d commands (%d stub): %s" % (unassigned["total"], unassigned["stub"], ", ".join("`/%s`" % r["command"] for r in cmdmap.get("unassigned", []))))
    L.append("")
    L.append("## Method and caveats")
    L.append("")
    L.append("- Read-only: `git ls-files`/`git grep`/`git log` in `%s`; `bin/conf/config-local.lua` was not read, so values set only there (JTL on, sandbox multipliers) come from `outputs/SWG-sandbox-settings.json`." % REPO)
    L.append("- Statuses and gap text are hand-written in `SYSTEMS` inside `build_systems.py`; counts are recomputed each run.")
    L.append("- TODO counts include harmless notes; read the samples in `systems.json` before treating a count as a gap.")
    L.append("- Where a cell says \"check in game\" or \"unsure\", the code did not settle it.")
    with open(os.path.join(HERE, "systems.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    return status_counts


def main():
    audit = json.load(open(AUDIT_JSON, encoding="utf-8"))
    audit_meta = "%d commands, file dated %s" % (len(audit["rows"]), datetime.datetime.fromtimestamp(os.path.getmtime(AUDIT_JSON)).strftime("%Y-%m-%d %H:%M"))
    stub_files = sorted({r["file"].replace("MMOCoreORB/", "") for r in audit["rows"] if r["status"] == "stub"})
    fd, token_path = tempfile.mkstemp(prefix="systems_tokens_", suffix=".txt")
    os.close(fd)
    try:
        repo = collect_repo_data(stub_files, token_path)
        tokens = set(l.strip().strip('"') for l in open(token_path, encoding="utf-8", errors="ignore"))
    finally:
        try:
            os.remove(token_path)
        except OSError:
            pass
    cmdmap = map_commands(audit["rows"], repo["stub"])
    profs = profession_refs(tokens)
    counts = write_outputs(repo, cmdmap, profs, audit_meta)
    print("HEAD", repo["head"])
    print("status counts", counts)
    print("wrote", os.path.join(HERE, "systems.md"), "and systems.json")


if __name__ == "__main__":
    main()
