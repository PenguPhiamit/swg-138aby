# Farming art gap fill: unbranded industrial frontier

14 October 2026, ChatGPT. Owner direction: like Star Wars, without branding. Bounded follow-up to `farming-open-art-shortlist.md`. Public source pages researched; no downloads, installations, account actions, author contact, imports or server changes. No model files/viewer renders inspected; visual suitability below is proposed art direction, not a tested appearance claim.

## Selected direction

Practical agricultural machinery: exposed pipes, service panels, replaceable tanks, metal troughs, caged lamps, muted paint and local wear. Add unusual crop silhouettes and restrained status lights. Avoid franchise insignia, recognizable copied props, modern product labels and a uniform neon cyberpunk finish. These are our design choices, not claims that a source asset already has the whole appearance.

## Gap-to-source matrix

| Missing asset | Best source and permission evidence | Work still needed |
|---|---|---|
| Enclosed hydroponic planter | [Sci-Fi Gardening Capsule](https://www.blendkit.com/asset-gallery-detail/69b5cb28-76fb-4cee-ac72-17de42326c29/), Zoltán Péter Fáth — creator listing Free + Creative Commons Zero | Listing describes sprinkler, indicators/light and adjustable subdivision; 21,032 polygons. Plant shown inside is explicitly separate and not cleared by this listing. Reduce complexity, inspect transparency, bake Blender materials and add our selected crop |
| Open planting bed/trough | [Planter Box 01](https://polyhaven.com/a/planter_box_01), Poly Haven — CC0 under asset page and [library licence](https://polyhaven.com/license); alternative [Brick Planters](https://opengameart.org/content/brick-planters-low-poly-style), tiko479 — CC0 | Wooden/brick terrestrial bases need material/silhouette changes for industrial metal troughs. Prefer simple original metal structure if rebuilding is easier than converting |
| Larger hydroponic pipe arrangement | [Hydroponic Farming Setup](https://sketchfab.com/3d-models/hydroponic-farming-setup-1486c6b628ba44f8a5e579927f51a7f7), Deepak Singh / dy4in — creator states entirely made in Blender, CC Attribution | Approximately 2.1M triangles for full scene: reference or source of simplified components, not direct SWG import. Exact CC version/package dependencies still to record |
| Water/nutrient tanks, processing-machine parts, panels, vents | [High Quality Industrial Asset Pack](https://opengameart.org/content/high-quality-industrial-asset-pack), rubberduck — author explicitly says models/textures CC0, some textures Yughues; [PBR update](https://opengameart.org/content/pbr-industrial-asset-pack), a52 — CC0 | Strong reusable machinery parts. PBR update notes baked models lack some updated maps; compare versions. Original diffuse/specular/normal maps may be closer to legacy-client needs than PBR workflow. Preview-only background is separately CC BY-SA and is not part of original pack |
| Additional large tanks | [Industrial Extension Pack 1: tanks](https://opengameart.org/content/industrial-extension-pack-1-tanks), rubberduck — CC0 | Two tanks, baked textures, ladders separate. Resize and reduce textures for chosen use |
| Modular irrigation pipes | [3D LOD Pipe-construction-set](https://opengameart.org/content/3d-lod-pipe-construction-set), rubberduck — CC0, creator's own metal texture | Author supplies three geometry resolutions (6/12/24), not a verified SWG LOD file. Assemble manifolds and create/export SWG distance LOD separately |
| Overhead grow-lamp housing | [Hanging Industrial Lamp](https://polyhaven.com/a/hanging_industrial_lamp), Poly Haven — CC0 | Adapt to agricultural lighting; do not assume Blender lights/emission automatically work in SWG |
| Small lamp / pipe-mounted fixture | [Industrial Pipe Lamp](https://polyhaven.com/a/industrial_pipe_lamp), Mateusz Sadek / Poly Haven — CC0 | Prefer original source. [Eclair conversion](https://eclair-assets.itch.io/industrial-pipe-lamp-01-free-cc0-glb-prop) explicitly identifies this source and CC0, but no conversion package acquired |
| Drying/curing rack base | [Steel Frame Shelves 02](https://polyhaven.com/a/steel_frame_shelves_02), Poly Haven — CC0 | Shelf is not a purpose-built dryer. Add original perforated trays, hooks, airflow housing and crop contents |
| Curing jars / ingredient containers | [Low Poly Medieval Jars, Potion](https://opengameart.org/content/low-poly-medieval-jars-potion), cgruslan — CC0, jars.blend listed | Adapt caps/materials; exact mesh inventory unknown. Useful rustic containers, not verified sealed scientific glassware |
| Controller / workstation | [Cyberpunk work station — Quaternius remix](https://opengameart.org/content/cyberpunk-work-station-quaternius-remix), anarres + Quaternius — CC0; original [Cyberpunk Game Kit](https://quaternius.com/packs/cyberpunkgamekit.html) also CC0 | Remix directly identifies Computer.blend from original kit; Quaternius comments acknowledge it. Restyle screens/paint for an industrial farm controller |
| Screen/indicator textures | [Sci-Fi interface textures](https://opengameart.org/content/sci-fi-interface-textures), rubberduck — CC0 with editable sources | Use sparingly; texture atlas and client material conversion still required |
| Growing plant | [Green plant](https://iamsujitcu.itch.io/green-plant), iamsujitcu — CC0; FBX, PNG and growing animation documented | Strong growth-stage source. Small/big vertex counts given as 935/3,631. Animation transfer to SWG unverified; sampling a few static stages is an alternative |
| More greenhouse vegetation | [Greenhouse Foliage](https://sketchfab.com/3d-models/greenhouse-foliage-12379c14d8284592a9c5cdb93d80b03f), Mats de Wind — author says plants made for own project, CC Attribution | 11.2k triangles total listing; exact version, selected meshes and textures need audit. Combine with earlier Yughues CC0 plants for variety |
| Watering tool / irrigation nozzle | [Watering Can Metal 01](https://polyhaven.com/a/watering_can_metal_01) and [Garden Sprinkler 01](https://polyhaven.com/a/garden_sprinkler_01), Poly Haven — CC0 | Convert to static prop or new tool only after checking SWG attachment/use needs. Strip any real-world marks found during inspection |
| Fertilizer sack | [Compost Bag 02](https://polyhaven.com/a/compost_bag_02), Poly Haven — CC0 | Replace visible label graphics with our original in-world label; confirm texture contents before choosing |

All Poly Haven entries above are actual model pages, not HDRI names mistaken for geometry. The assets are CC0; the site's logos, thumbnails and other web content are not automatically covered. Keep original source/author information even when attribution is optional. For creator uploads, the published grant is evidence, not proof of every packaged dependency; inspect readmes, linked inputs and files before import.

## What remains custom

1. **A coherent modular greenhouse shell.** No ready open-licensed unbranded shell with verified dependencies was selected. Build original structural ribs/glass panels around these parts, or adapt previously listed CC0 modular station pieces. Interior gameplay needs an additional collision/cell design; exterior scenery alone is a different scope.
2. **Purpose-built dryer, extractor and grinder.** We found reusable rack, tank, pipe and control parts rather than a complete open machine for each. Assemble original machines with clear player-facing silhouettes. A processing function does not require mechanically accurate internal meshes.
3. **Crop-specific seedling/mature/harvested/dead stages.** One growth-animation source is promising, but a complete matching multi-crop lifecycle pack was not established. Derive stages from selected CC0 plants or make original meshes. No promise of skeletal/FBX animation compatibility.
4. **Matching style and game conversion.** Repaint/rebake the selected sources to one palette, simplify silhouettes, create LOD/collision and package SWG static appearances. All imported assets remain untested until client checks pass.

Recommendation: capsule + industrial base pack + LOD pipes + hanging lamp + steel shelves + growing plant, with original tray/rack attachments. This covers a credible prototype's main visible functions using openly licensed unbranded parts. It is a proposed batch, not downloaded or installed.

## Held or unsuitable leads

- Brandon Westlake's [Greenhouse FREE](https://sketchfab.com/3d-models/greenhouse-free-0a0fe027a28949fab36e14d25e3ccbcf) now lists Free Standard and NoAI, not a verified CC grant. Do not infer openness from Free in title or historical terms.
- AetherFarm marketplace listing has conflicting commercial-use description versus Editorial licence label; not selected or purchased.
- Generic grow-light 3D-print listings commonly prohibit redistribution/derivatives. No STL-to-game conversion assumed permitted.
- Poly Haven Abandoned Greenhouse is an HDRI, not a greenhouse mesh; not counted as filling the shell gap.
- New generated CC0 libraries appeared in search results, but weren't needed to fill these prototype slots. No AI service calls made.

## MODLOG / research evidence

Read board, roadmap and inbox; claimed follow-up; used the already-applied Universal Modder public web-research workflow. Expanded queries from branded Star Wars props to hydroponic/planter/grow-light/industrial/tank/pipe/rack/jar/growth-stage sources. Prioritized original creator pages over aggregators; followed industrial update back to its original author and lamp conversion back to Poly Haven. Exact URLs are in the matrix. Credibility: creator licence and dependency statements strongest; remaining package contents/technical suitability unverified. No screenshots or downloaded-file hashes exist because only research was performed. No project Git commit or server edits. Next engineering step is a small selected-source download/file audit, then one planter conversion proof, rather than collecting the entire catalogue.
