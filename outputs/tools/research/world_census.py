"""C21-2 bounded world inventory: saved manifests only, no server or network actions."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'outputs/Documentation-support'
INPUTS = ['outputs/Content-catalogue/active-content-catalogue.json',
          'outputs/Content-catalogue/MTG-inventory-summary.json',
          'outputs/Content-catalogue/downloaded-package-evidence.json',
          'outputs/Documentation-support/planets-coordinates.json']


def main():
    data = [json.loads((ROOT / p).read_text(encoding='utf-8-sig')) for p in INPUTS]
    active, assets, packages, lore = data
    lore_by_zone = {r['zone']: r for r in lore['planets']}
    fresh = {
        'Ossus': ('https://starwars.fandom.com/wiki/Ossus/Legends', 'Temple destroyed in 137 ABY; choose the exact story point before placing an intact academy.'),
        'Centerpoint Station': ('https://starwars.fandom.com/wiki/Centerpoint_Station', 'Destroyed in 40 ABY; an intact Legacy-era station needs an explicit alternate-history premise or historical scenario.'),
        'Otoh Gunga': ('https://starwars.fandom.com/wiki/Otoh_Gunga/Legends', 'City on Naboo, not an additional planet; design a city/interior destination.'),
        'Geonosis': ('https://starwars.fandom.com/wiki/Geonosis/Legends', 'Rocky desert planet; do not substitute the Yavin IV bio-lab for a completed planetary release.'),
        'Zeltros': ('https://starwars.fandom.com/wiki/Zeltros/Legends', 'Legends homeworld of Zeltrons; species and world implementation are separate dependencies.'),
        'Tansarii Point Station': ('https://starwars.fandom.com/wiki/Tansarii_Point_Station/Legends', 'Station near Ord Mantell, with the same design as Nova Orion; shared design does not prove shared usable game geometry.'),
        'Jakku': ('https://starwars.fandom.com/wiki/Jakku', 'Explicit canon exception; do not import its canon history into Legends by default.'),
    }
    rows = []
    for r in active['rows']:
        if r['kind'] not in ('Planet', 'Station', 'Candidate world', 'Legacy/test world'):
            continue
        zone = r.get('zone')
        inherited = lore_by_zone.get(zone, {})
        evidence = r.get('local_asset_evidence', [])
        row = dict(id=r['id'], name=r['name'], zone=zone, catalogue_kind=r['kind'],
                   physical_kind='city' if r['name'] == 'Otoh Gunga' else 'test-terrain family' if r['kind'] == 'Legacy/test world'
                   else 'station' if r['kind'] == 'Station' else 'ground-world candidate',
                   permission_label=r['status_label'], source_urls=r['sources'],
                   exact_asset_paths=[x['path'] for x in evidence],
                   terrain_paths=[p for p in assets['terrain_files'] if zone and p == f'terrain/{zone}.trn'],
                   snapshot_paths=[p for p in assets['snapshot_files'] if zone and p == f'snapshot/{zone}.ws'],
                   inherited_lore_sources=inherited.get('sources', []),
                   lore_access='inherited C14 search extracts; not refreshed' if inherited else 'article audit pending',
                   maturity='saved catalogue candidate; current runtime unverified',
                   remaining_work='Verify licence/art provenance and transitive dependencies; port zone/travel/regions, gameplay and client UI; run round-trip/relog checks.',
                   effort='High, low confidence', notes=r['notes'])
        if r['name'] in fresh:
            row.update(lore_access='fresh search-index article extract, 2026-10-14; direct-page audit unavailable',
                       lore_url=fresh[r['name']][0], era_or_identity_gate=fresh[r['name']][1])
        if 'permission' in r['status_label'].lower():
            row['remaining_work'] = 'Creator implementation/art rights hold; original replacement remains an option. ' + row['remaining_work']
        if r['name'] == 'Hoth':
            row.update(maturity='dev/test adaptation; 14 Oct 13:38 saved bot content run 32/33, not real-client acceptance',
                       remaining_work='Latest saved failure: salvage-detail camp props (0). Reconcile C22 findings/fixes, real-client cave/terrain/render checks, loot/resource/quest receipts and return travel.',
                       effort='Medium-High remaining, low confidence')
        if r['name'] == 'Zeltros':
            row['downloaded_packages'] = [dict(name=p['name'], members=len(p['files']), sha256=p['sha256']) for p in packages if p['name'].startswith('zeltros_')]
            row['remaining_work'] = 'Downloaded client/server packages require MTG dependencies and old object-path/API adaptation. CC-BY-NC claim/version/contributors must be reconciled with the project NC-out rule before import; no clearance inferred.'
        if r['name'] == 'Otoh Gunga':
            row['terrain_paths'] = [p for p in assets['terrain_files'] if p == 'terrain/otoh_gunga.trn']
            row['remaining_work'] = 'Inspect legacy terrain; build bubble-city geometry, interiors, safe arrivals, water presentation and routing. Avoid assuming underwater movement support.'
            row['effort'] = 'Very high, low confidence'
        if r['kind'] == 'Station':
            row['effort'] = 'High-Very high, low confidence'
        rows.append(row)
    rows.append(dict(id='owner-ossus', name='Ossus', zone='ossus', catalogue_kind='owner addition', physical_kind='ground-world candidate',
        permission_label='project-original staged data; referenced stock dependencies need validation',
        exact_asset_paths=['outputs/Fable-ossus/staged/client/terrain/ossus.trn'],
        lore_access='fresh search-index article extract, 2026-10-14; direct-page audit unavailable', lore_url=fresh['Ossus'][0],
        era_or_identity_gate=fresh['Ossus'][1], maturity='O1 staged, not deployed or game-tested in this census',
        remaining_work='Merge registration tables with Hoth instead of overwriting; validate terrain writer and stock shader/flora closure; snapshot, travel/server zone, safe spawn/navmesh, quests/encounters and story-date decision.',
        effort='High-Very high, low confidence', source_urls=['outputs/Fable-ossus/README.md']))
    result = dict(scope='24 saved catalogue rows + owner-selected Ossus; not all SWG or all Legends worlds',
                  audited='2026-10-14', input_hashes={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in INPUTS},
                  counts=dict(records=len(rows), ground_world_candidates=sum(r['physical_kind'] == 'ground-world candidate' for r in rows),
                              stations=3, cities=1, test_terrain_families=1, exact_catalogue_terrain_snapshot_pairs=11,
                              fresh_article_extracts=7), rows=rows)
    assert len(rows) == 25
    (OUT / 'server-world-census.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result['counts']))


if __name__ == '__main__':
    main()
