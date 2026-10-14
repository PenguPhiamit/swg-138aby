# Core3 staff commands that do nothing: grouped for the owner to pick

Claude, 14 Oct 2026. Source: `core3-command-audit.md` (`tools/core3_audit/command_audit.py`). These 45 staff commands are
**stubs**: the server accepts them and nothing happens. The owner asked for a list to pick from. "Purpose" is what
the command name and the SWG staff tools suggest; it isn't documented in Core3. "Covered by" names a command that
**does** work today and already does the job.

Working staff commands worth knowing (all have real code):
- `/credits <name> add|subtract <amount> cash|bank`
- `/gmrevive [<name>]`
- `/teleport <x> <z> <planet>`, `/teleportTo <name>`, `/teleportTarget <name>` (brings them to you)
- `/invulnerable` (and `/invulnerable invis`)
- `/setPlayerAppearance`, `/setHue`
- `/grantSkill`, `/revokeSkill`, `/setExperience`
- `/setFaction`, `/setFactionStanding`
- `/object`, `/createCreature`, `/createNpc`
- `/dumpZoneInformation`, `/findObject`, `/findPlayer`
- `/kill`, `/freezePlayer`, `/broadcast…`

Effort: **Low** is under an hour each in the dev tree, **Medium** is half a day, **High** is more. Everything goes
through the test galaxy and review before live.

**Owner, 14 Oct: build all four groups (A–D).** Skip the ones a working command already covers, and the six internal
debug hooks. Order:
1. B: `/spawnStatus` and `/showSpawnRegion` first.
2. C: the testing helpers.
3. A: the player tools.
4. D: the server tools.

Each batch is a dev commit, then a test-galaxy check, then ChatGPT's review (C4e) before any live deploy.

## A. Player tools (15)

| Command | Purpose | Covered by | Effort if built |
|---|---|---|---|
| `/money`, `/editBank`, `/editBankAccount` | give or take credits | **`/credits`** | skip |
| `/editAppearance` | change a player's look | **`/setPlayerAppearance`, `/setHue`** | skip |
| `/editStats` | set a player's health/action/mind | none | Low |
| `/getRank`, `/setRank` | GCW rank | partly `/setFaction`, `/setFactionStanding` | Low |
| `/setTef` | temporary enemy flag (GCW) | none | Low–Medium |
| `/grantTitle` | give a title | partly `/grantSkill` (boxes carry titles) | Low |
| `/hasVeteranReward`, `/setVeteranReward` | veteran rewards | `/clearVeteranReward` works | Low |
| `/getGameTime` | show game time | none | Low |
| `/addAllowedPlayer`, `/removeAllowedPlayer` | entry list of a structure or area | owners' own permission menus | Low–Medium |
| `/uncityBan` | lift a city ban | none for staff | Low |

## B. Spawn controls (9)

`/spawnStatus`, `/showSpawnRegion`, `/getSpawnDelays`, `/setMinimumSpawnTime`, `/setMaximumSpawnTime`, `/startSpawner`,
`/stopSpawner`, `/startTargetSpawner`, `/stopTargetSpawner`.

- **Purpose:** inspect and steer the creature spawner. These would help with testing new planets like Hoth: which region am I in, what can spawn here, pause or restart it.
- **Covered by:** partly `/dumpZoneInformation`.
- **Effort:** Medium. Core3's spawner (spawn areas and lairs) differs from the live game's, so each command has to be mapped onto it. `/spawnStatus` and `/showSpawnRegion` are the useful first two.

## C. Travel, combat and debug (14)

| Command | Purpose | Covered by | Effort if built |
|---|---|---|---|
| `/planetWarp`, `/planetWarpTarget` | send yourself or someone to a planet | **`/teleport`, `/teleportTarget`** | skip |
| `/harmless`, `/harmful` | can't be attacked / can be again | **`/invulnerable`** (harmless) | Low (harmful) |
| `/maxStats`, `/maxCombatAbility` | make a staff character strong for testing | none | Low |
| `/searchCorpse` | loot a corpse as staff | none | Low |
| `/destroy` | delete a targeted object | partly `/kill`, `/wipeItems` | Low |
| `/combat`, `/craft`, `/manufacture`, `/initializeComponent`, `/forceCommand`, `/lag` | internal developer test hooks | none | skip (no clear player value) |

## D. Server, Jedi and QA (7)

| Command | Purpose | Covered by | Effort if built |
|---|---|---|---|
| `/setLoginMessage`, `/setLoginTitle` | the message shown at login | `/resendLoginMessageToAll` resends the configured one | Low |
| `/setPlanetLimit` | cap players per planet | none | Low–Medium |
| `/gmForceRank` | set a Force (FRS) rank | partly `/gmJediState`, `/resetJedi` | Low–Medium |
| `/overridePadawanTrialsEligibility` | allow Padawan trials | **`/grantPadawanTrialsEligibility`** | skip |
| `/aiIgnore` | creatures ignore you (watch them without a fight) | partly `/invulnerable invis` | Low |
| `/showFactionInformation` | a target's faction details | none | Low |

## Not stubs, but worth knowing

- `/setGodMode <name|self> on|off` works. God Mode unlocks the staff commands; it doesn't make you immune.
- `/goto` works; it carries an optimisation TODO.
