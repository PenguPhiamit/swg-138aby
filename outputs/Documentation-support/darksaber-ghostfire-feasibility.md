# Darksaber and Ghostfire with opalescent trails

14 October 2026, ChatGPT. Bounded source/asset research plus read-only local data probe; no saber downloads/imports, client modifications, game tests or server changes.

## Outcome

Both are plausible custom-content projects. A hilt/model source exists for Darksaber; its opaque dark blade and white edge need client material/geometry work, not just a colour change. Ghostfire can use an existing permitted hilt or an original hilt; the desired appearance primarily needs a dim blade plus custom pastel/pearlescent trail textures and client effects. Authentic multiple afterimages or angle-dependent iridescence are not proven with the current pre-CU client.

## Asset candidates and rights

| Source | Evidence | Decision |
|---|---|---|
| [Dark - Saber Blender 2.90](https://sketchfab.com/3d-models/dark-saber-blender-290-73bb3524d59445c580552c71bce7543d), Darth Iron | Author page index says model created by author, CC Attribution, 2.3k triangles. Also requests credit and notification of intended use. Direct page could not be fetched | Best Darksaber candidate. Reverify exact licence version and packaged contributors; hold import until notification request/terms handled. No message sent; owner authorization needed before contacting author |
| [Darksaber — eemil](https://sketchfab.com/3d-models/darksaber-starwars-a6fc4078b96e48aeb3e4227a8e0be75b) | Indexed original listing: .blend only, blade included, 16.9k triangles, CC Attribution-NonCommercial and NoAI | Restricted alternative, not preferred for a broadly reusable server pipeline. LAN ownership does not supply missing rights |
| [Weapon Slash Effect](https://opengameart.org/content/weapon-slash-effect), Cethiel | Creator page: CC0, five animated slash effects and four colour variants | Editable masks/flipbook source or visual reference; not a ready SWG trail implementation |
| [Particle Pack](https://kenney.nl/assets/particle-pack), Kenney | Official page: CC0, 80 files, 512×512 | Masks/soft glows for our own blade/trail texture work; actual selected texture suitability unverified |
| [Particle textures](https://opengameart.org/content/particle-textures), Starry Skydancer | Creator page CC0, small sparkle textures | Optional sparse motes; would keep subtle so Ghostfire does not become a bright particle cloud |

Fan-model CC labels cover rights the creator can grant, not a Lucasfilm licence. Existing Starfield adaptation requires author permission and credits another source for audio; it is not an unrestricted replacement for the original model. No third-party film/TV or game-extracted sounds selected. Excluded project sources are not candidates.

## Lore and proposed appearance

[Official Darksaber description](https://www.starwars.com/databank/darksaber): dark-energy blade with a white crackling edge. Use an opaque, tapered/flattened black silhouette and separate pale edge/glow treatment; merely tinting a normal additive lightsaber black may make it disappear instead of produce a dark core. That rendering warning is engineering reasoning, not a verified SWG test result.

[Wookieepedia Ghostfire crystal](https://starwars.fandom.com/wiki/Ghostfire_crystal) describes dim/translucent blades, little sound and illusory afterimages. The Legends URL was inaccessible in this pass, so exact Legends-specific sourcing remains open; do not silently claim all details verified in both continuities. Opalescent pastel trails are the owner's requested artistic interpretation, not a sourced crystal property. Write original item text when implemented, not copied wiki prose.

Proposed Ghostfire art: faint neutral/pearl blade; soft cyan, rose and lavender bands in the trailing afterimage, fading quickly; restrained light output. First aim for a textured pastel ribbon approximation. True view-dependent opalescence and separately delayed blade silhouettes are later research gates. No automatic combat bonuses, stealth effects or crystal-stat changes are part of this appearance request.

## Local client evidence — what was actually checked

Ran `outputs/tools/owner_content/saber_asset_probe.py` using the existing read-only TRE loader. Transcript: [saber-local-asset-probe.txt](saber-local-asset-probe.txt). The loader reported `swgemu_login.cfg` missing, so this is the files available through the base configuration it could resolve, not proof of the currently running client's exact effective configuration.

85 relevant names matched: blade `.lsb` appearances, `.sht` materials, `.dds` textures, `palette/wp_lightsaber.pal`, an `.eft` and pixel-program files. No path matching darksaber or ghostfire was found within that resolved index. Filename presence is not rendering support.

Read two local `.lsb` files in memory and three blade shaders, without extracting game assets. Observed LSA form, BASE appearance reference, lightsaber idle sound, BLAD/SHDR, WDTH and OPEN/CLOS tags. `shader/lightsaberblade.sht` is an SWSH form referencing four sub-shaders. Sub-shaders reference blade DDS textures, `effect/e_h_lightsaberblade.eft`, `index_color_blade`, and the lightsaber palette. These are binary-string dependencies, not fully decoded field semantics. Width/open/close numeric meanings and trail controls still need a format audit. Specialized blackwing/lava/permafrost names also exist; no claim of permission to reuse a community override or that a darksaber already exists follows from those names.

This supports a local, authorized-data investigation route without fetching excluded source repositories. The probe uses project-owned tooling and the installed client data; UM executable/decompiler was not run.

## Engineering sequence and difficulty

1. Resolve model rights/notification request, or make an original hilt. Inventory actual mesh/textures and hashes on authorized acquisition.
2. Pin a stock local saber chain and identify archive provenance; isolate copies in a new custom namespace. Decode relevant appearance/shader/palette fields and prove unchanged round-trip behavior before edits.
3. Build the simple Ghostfire approximation first: dim blade and original/CC0-derived pastel trail mask. Test whether trail uses independent customization/materials; global palette edits must not recolour every saber.
4. Build Darksaber hilt/flat silhouette and white-edge material. Verify facing, grip, hardpoint position, ignition/retraction, trail visibility and dark core against bright/dark backgrounds.
5. Test two clients, combat animations, sheathing, relog, indoor/outdoor lighting and low/high graphics settings. No live promotion without cross-review and owner approval.

Difficulty: medium for a hilt/static display; high for a functioning flat Darksaber and independent custom trail; high/uncertain for true Ghostfire afterimages or angle-dependent iridescence. Need a client rendering proof before promising full effects. These are proposed tests, none run in game.

## MODLOG

Read shared board/roadmap/inbox and claimed research. Queued 30 farming source entries under owner's download authorization in `farming-asset-download-queue.md`; no timer created or downloads performed. Searched creator-original Darksaber models and open VFX masks; inspected local client dependencies read-only. Public search surfaced excluded material incidentally; no excluded repository was opened, fetched, imported or used as implementation evidence. Next: authorized farming download session; saber prototype/file-format task requires claim and selected source, with contact approval only if author notification is pursued.
