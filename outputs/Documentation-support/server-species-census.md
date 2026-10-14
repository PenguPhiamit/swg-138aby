# C21 checkpoint 3a: additional species and option census

14 October 2026. Saved evidence classification only; no imports, deploys or new game tests.

**40 labels = 36 biological species candidates + 2 human faction/clan options + 2 droid implementation/model options.** These are candidates, not 40 working playable species.

The original species package supplies 16 option labels / 20 player template variants: 14 regular species and two human faction options. Gendered filenames count technical variants, not additional species. The later EiF evidence is a separate reference; client availability does not grant art reuse.

| Candidate | Classification | Original-package variants | Rights / evidence |
|---|---|---|---|
| Hutt | biological species candidate | female, male | Published for server use |
| Nautolan | biological species candidate | male | Published for server use |
| Togruta | biological species candidate | female | Published for server use |
| Chiss | biological species candidate | female, male | Published for server use |
| Devaronian | biological species candidate | male | Published for server use |
| Gran | biological species candidate | male | Published for server use |
| Ishi Tib | biological species candidate | male | Published for server use |
| Nightsister | human faction/clan option | female | Published for server use |
| Nikto | biological species candidate | male | Published for server use |
| Quarren | biological species candidate | male | Published for server use |
| Singing Mountain Clan Witch | human faction/clan option | female | Published for server use |
| Weequay | biological species candidate | male | Published for server use |
| Aqualish | biological species candidate | female, male | Published for server use |
| Bith | biological species candidate | female, male | Published for server use |
| Gotal | biological species candidate | male | Published for server use |
| Talz | biological species candidate | male | Published for server use |
| Abyssin | biological species candidate | none in original package | Published server code; client asset reuse unresolved |
| Arcona | biological species candidate | none in original package | Published server code; client asset reuse unresolved |
| Cerean | biological species candidate | none in original package | Published server code; client asset reuse unresolved |
| Duros | biological species candidate | none in original package | Published server code; client asset reuse unresolved |
| Gungan | biological species candidate | none in original package | Published server code; client asset reuse unresolved |
| Iktotchi | biological species candidate | none in original package | Published server code; client asset reuse unresolved |
| Jenet | biological species candidate | none in original package | Published server code; client asset reuse unresolved |
| Kel Dor | biological species candidate | none in original package | Published server code; client asset reuse unresolved |
| Kubaz | biological species candidate | none in original package | Published server code; client asset reuse unresolved |
| Sanyassan | biological species candidate | none in original package | Published server code; client asset reuse unresolved |
| Chadra-Fan | biological species candidate | none in original package | Published server code; client asset reuse unresolved |
| Droid (NK3 label in source; not verified IG-100) | droid implementation/model option | none in original package | Published server code; client asset reuse unresolved |
| Dug | biological species candidate | none in original package | Published server code; client asset reuse unresolved |
| Ewok | biological species candidate | none in original package | Published server code; client asset reuse unresolved |
| Feeorin | biological species candidate | none in original package | Published server code; client asset reuse unresolved |
| Geonosian | biological species candidate | none in original package | Published server code; client asset reuse unresolved |
| Ortolan | biological species candidate | none in original package | Published server code; client asset reuse unresolved |
| Togorian | biological species candidate | none in original package | Published server code; client asset reuse unresolved |
| Toydarian | biological species candidate | none in original package | Published server code; client asset reuse unresolved |
| Mirialan | biological species candidate | none in original package | Published server code; client asset reuse unresolved |
| Zeltron | biological species candidate | none in original package | Published server code; client asset reuse unresolved |
| Arkanian | biological species candidate | none in original package | Later EiF implementation; reusable complete package unverified |
| Echani | biological species candidate | none in original package | Later EiF implementation; reusable complete package unverified |
| IG-100 Droid | droid implementation/model option | none in original package | Later EiF implementation; reusable complete package unverified |

## Selected lore checks

Fresh search-index extracts were available for the following Wookieepedia articles; direct-page access was blocked. They support identity classification only, not a complete Legacy-era population/history audit. No article text or images are imported.

- [Chiss](https://starwars.fandom.com/wiki/Chiss/Legends): Near-human species; blue skin/red eyes; owner selected first.
- [Nautolan](https://starwars.fandom.com/wiki/Nautolan/Legends): Regular species; Glee Anselm origin is separately supported by its Legends world article.
- [Togruta](https://starwars.fandom.com/wiki/Togruta/Legends): Regular species; Shili origin separately supported by Shili/Legends.
- [Nightsister](https://starwars.fandom.com/wiki/Nightsisters/Legends): Faction/coven identity, not a distinct biological species; this package uses a human female option. Do not infer that every Nightsister is Human in all Legends sources.
- [Singing Mountain Clan Witch](https://starwars.fandom.com/wiki/Singing_Mountain_Clan): Clan/cultural option, not a separate species; preserve as optional identity content.
- [IG-100 Droid](https://starwars.fandom.com/wiki/IG-100_MagnaGuard/Legends): Droid model option; do not equate with the separately labelled NK3 implementation.

## Implementation and rights gates

Chiss remains first by owner choice. Fable S3 records a complete dependency map and offline staged fragments; this census does not supersede Claude integration or declare those fragments working. The original package has old table schemas, duplicate Aqualish/Bith racial rows, incorrect human species IDs for four options, missing species skill rows, and an absent Chiss hairstyle. Its Wookieepedia-derived descriptions need replacement with our own wording. Keep per-file rights/credits with imports.

Do not add hybrid species before regular species. The faction options remain available as concepts; the no-hybrids rule does not require discarding their human implementations. Hutt human-rig presentation needs owner review. Droid player rules require a separate design for equipment, healing, food, cloning and certifications; the two labels are not interchangeable.

Next checkpoint: actual mobile/pet model families and wild/BE taming eligibility from current client/server data. Then remaining species lore/dependency audits. Overall C21 remains open; no additional research pass is implied by this checkpoint.
