"""C21 checkpoint 3a: classify saved catalogue records; no downloads or server edits."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INPUTS = ['outputs/Content-catalogue/active-content-catalogue.json',
          'outputs/Fable-species/provenance.json', 'outputs/Fable-species/checks.json']
LORE = {
    'Chiss': ('https://starwars.fandom.com/wiki/Chiss/Legends', 'Near-human species; blue skin/red eyes; owner selected first.'),
    'Nautolan': ('https://starwars.fandom.com/wiki/Nautolan/Legends', 'Regular species; Glee Anselm origin is separately supported by its Legends world article.'),
    'Togruta': ('https://starwars.fandom.com/wiki/Togruta/Legends', 'Regular species; Shili origin separately supported by Shili/Legends.'),
    'Nightsister': ('https://starwars.fandom.com/wiki/Nightsisters/Legends', 'Faction/coven identity, not a distinct biological species; this package uses a human female option. Do not infer that every Nightsister is Human in all Legends sources.'),
    'Singing Mountain Clan Witch': ('https://starwars.fandom.com/wiki/Singing_Mountain_Clan', 'Clan/cultural option, not a separate species; preserve as optional identity content.'),
    'IG-100 Droid': ('https://starwars.fandom.com/wiki/IG-100_MagnaGuard/Legends', 'Droid model option; do not equate with the separately labelled NK3 implementation.'),
}
ALIASES = {'Ishi Tib': 'ishi_tib', 'Singing Mountain Clan Witch': 'smc'}


def run():
    catalogue, provenance, checks = [json.loads((ROOT / p).read_text(encoding='utf-8-sig')) for p in INPUTS]
    package = provenance['packages']['newspecies-original.zip']
    templates = package['species_tre']['player_templates']
    rows = []
    for source in catalogue['rows']:
        if source['kind'] != 'Species':
            continue
        name = source['name']
        kind = ('human faction/clan option' if name in ('Nightsister', 'Singing Mountain Clan Witch')
                else 'droid implementation/model option' if 'Droid' in name else 'biological species candidate')
        slug = ALIASES.get(name, name.lower().replace(' ', '_'))
        exact = [p for p in templates if p.startswith('shared_' + slug + '_')]
        genders = [p.removeprefix('shared_' + slug + '_').removesuffix('.iff') for p in exact]
        row = dict(id=source['id'], name=name, classification=kind,
                   inherited_permission_label=source['status_label'],
                   original_package_templates=exact, original_package_gender_variants=genders,
                   inherited_source_variants=[e.get('gender') for e in source.get('model_evidence', [])],
                   runtime_validated=False, lore_audit='not refreshed in this checkpoint',
                   implementation='Creation UI/tables, race IDs, species skill/certifications, rig/customization, clothing and relog/death tests required.',
                   effort='High, low confidence')
        if name in LORE:
            row.update(lore_url=LORE[name][0], lore_note=LORE[name][1],
                       lore_audit='2026-10-14 search-index extract; direct article blocked')
        if source['status'] == 'S':
            row['rights_gate'] = 'Server source and client art are separate: client reuse unresolved; original replacement remains possible.'
        elif source['status'] == 'U':
            row['rights_gate'] = 'Later implementation documented; exact reusable package and contributors unverified.'
        else:
            row['rights_gate'] = 'Published species-mod purpose per saved audit; retain exact credit/terms and validate selected dependencies. No blanket art permission inferred.'
        if name == 'Chiss':
            row.update(implementation='S3 staged fragments/checks exist; Claude owns integration. Missing female hairstyle s33 omitted; splice tables rather than replace stock. Species IDs, skill/certs and clothing remain acceptance gates.',
                       effort='Medium-High remaining; game validation pending')
        if kind == 'human faction/clan option':
            row['implementation'] = 'Treat as optional character identity/cosmetic/quest content. Do not count as a new regular species or introduce hybrid biology.'
        if name == 'Hutt':
            row['implementation'] += ' Package male/female filenames are technical variants, not a verified biological sex model; human-rig upright appearance needs owner review.'
        rows.append(row)
    counts = {kind: sum(r['classification'] == kind for r in rows) for kind in
              ('biological species candidate', 'human faction/clan option', 'droid implementation/model option')}
    assert len(rows) == 40 and list(counts.values()) == [36, 2, 2]
    result = dict(date='2026-10-14', scope='40 saved additional-option records; not all Legends species or installed playable count',
                  counts=counts, original_package_option_labels=len(package['species_added']),
                  original_package_player_templates=len(templates),
                  original_package_regular_species=sum(bool(r['original_package_templates']) and r['classification'] == 'biological species candidate' for r in rows),
                  input_hashes={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in INPUTS}, rows=rows)
    out = ROOT / 'outputs/Documentation-support/server-species-census.json'
    out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    lines = ['# C21 checkpoint 3a: additional species and option census', '',
             '14 October 2026. Saved evidence classification only; no imports, deploys or new game tests.', '',
             '**40 labels = 36 biological species candidates + 2 human faction/clan options + 2 droid implementation/model options.** These are candidates, not 40 working playable species.', '',
             'The original species package supplies 16 option labels / 20 player template variants: 14 regular species and two human faction options. Gendered filenames count technical variants, not additional species. The later EiF evidence is a separate reference; client availability does not grant art reuse.', '',
             '| Candidate | Classification | Original-package variants | Rights / evidence |', '|---|---|---|---|']
    for row in rows:
        lines.append(f"| {row['name']} | {row['classification']} | {', '.join(row['original_package_gender_variants']) or 'none in original package'} | {row['inherited_permission_label']} |")
    lines += ['', '## Selected lore checks', '',
              'Fresh search-index extracts were available for the following Wookieepedia articles; direct-page access was blocked. They support identity classification only, not a complete Legacy-era population/history audit. No article text or images are imported.', '']
    for name, (url, note) in LORE.items():
        lines.append(f'- [{name}]({url}): {note}')
    lines += ['', '## Implementation and rights gates', '',
              'Chiss remains first by owner choice. Fable S3 records a complete dependency map and offline staged fragments; this census does not supersede Claude integration or declare those fragments working. The original package has old table schemas, duplicate Aqualish/Bith racial rows, incorrect human species IDs for four options, missing species skill rows, and an absent Chiss hairstyle. Its Wookieepedia-derived descriptions need replacement with our own wording. Keep per-file rights/credits with imports.', '',
              'Do not add hybrid species before regular species. The faction options remain available as concepts; the no-hybrids rule does not require discarding their human implementations. Hutt human-rig presentation needs owner review. Droid player rules require a separate design for equipment, healing, food, cloning and certifications; the two labels are not interchangeable.', '',
              'Next checkpoint: actual mobile/pet model families and wild/BE taming eligibility from current client/server data. Then remaining species lore/dependency audits. Overall C21 remains open; no additional research pass is implied by this checkpoint.']
    out.with_suffix('.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('rows', 'input_hashes')}))


if __name__ == '__main__':
    run()
