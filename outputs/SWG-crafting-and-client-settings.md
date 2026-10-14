# Crafting tests and client settings

The client is configured for movable 1600×900 windows, multiple instances, an unconstrained mouse pointer, no pointer-mode edge camera panning, full-resolution texture mip levels, and a hardware cursor. Admin-command entry remains enabled. Restart each game client for these changes to take effect; the galaxy does not need a restart.

Launch Play SWG.cmd again for another client after the first client is fully loaded. Use a different account for simultaneous gameplay tests; the same character cannot be logged in twice. Each new game window may need the same administrator launch method used for the first client.

These are client preferences, not a graphics-engine upgrade. The game still uses its legacy DirectX 9 renderer. Your detected display is 1920×1080 at 60 Hz and your GPU is an RTX 5070. In-game terrain, shadow and character-detail preferences can be tuned further after the new display settings are loaded. The 60 Hz entry is a fullscreen refresh preference, not an FPS unlock.

**Resources through a menu**

Use your existing character-builder terminal, then choose **Deeds → Resource Deed**. Use the deed from your inventory to browse resource classes, choose a named resource, review its stats and confirm. One deed supplies 30,000 units and is consumed. Obtain another deed for another resource.

To create a deed directly on your owner character:

```text
/object createitem object/tangible/veteran_reward/resource.iff
```

For an early Artisan test, choose a metal and a chemical accepted by the schematic. Later professions may require specific resource subtypes, so check the ingredient requirements rather than choosing only by quality.

**Resources through a direct command**

```text
/resource list tatooine
/resource create RESOURCE_NAME 100000
```

Replace RESOURCE_NAME with the generated resource name from the list, not the category word “steel” or “metal.” This creates a stack from an existing resource spawn; it does not create a new perfect-stat resource or change the resource spawn cycle.

If testing a normal character, trade the resources and tools from the owner character or grant them through an appropriately scoped test tool. Keep a normal character's skills and crafting progression ordinary when checking normal gameplay.

**Mantis**

Mantis is an optional bug-tracker integration for the game's help/bug-report interface. It is separate from the game account database and world saves. It is unnecessary for a private crafting/test server. Subsequent baseline maintenance disables its host configuration after a galaxy backup; database credentials stay unchanged. See SWG-developer-baseline.md and SWG-baseline-checks.json for the maintenance result.

**Forum access**

The user signed in manually to the SWGEmu forum, and development documentation is now readable in that browser session. If the session expires, sign in yourself again. Never provide account passwords in the chat.

References: [client setup](https://github.com/[name removed]/mtgserver/wiki/Guide-Client-Setup), [mouse/window preferences](https://swgr.org/wiki/tech-issues-faq/), and the installed Core3 ResourceCommand, ResourceDeedSuiCallback, ResourceManager and character-builder menu source.
