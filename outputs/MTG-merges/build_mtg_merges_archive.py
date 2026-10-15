"""The chain up to the Ossus creature names, plus the MTG merges (Claude, 15 Oct 2026). It runs:

    ... > stage_gem_names > stage_creature_names > stage_mtg_merges

Packs local_planets-mtgmerge.tre and compares it with the installed fauna archive (Local-model-ossus-fauna, 6556537d).
Only the five merged files may be new; every other entry stays byte-identical. In each merged file every stock row or
string is kept. Writes checks.json.

    python -I build_mtg_merges_archive.py
"""
import hashlib
import io
import json
import os
import shutil
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(OUTPUTS, 'Local-model-ossus-fauna'))
import build_fauna_archive as fauna  # noqa: E402  (brings the stock-only load order and the whole chain)
sys.path.insert(0, HERE)
import stage_mtg_merges as smm  # noqa: E402

REF_TRE = os.path.join(OUTPUTS, 'Local-model-ossus-fauna', 'local_planets-fauna.tre')
REF_SHA = '6556537d589c411f9b0c1697c2a4f5bdd792800f96d0ee517d38cd3cd3dcb072'


def main():
    names, lore = fauna.names, fauna.names.lore
    stage = os.path.join(HERE, 'work', 'local_planets')
    for p in (stage, stage + '.new'):
        if os.path.isdir(p):
            shutil.rmtree(p)
    builder = lore.r3.load_patched_builder()
    builder.STAGE, builder.TRE = stage, os.path.join(HERE, 'work', 'local_planets.tre')
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = builder.main()
    assert rc == 0 and 'archive verified' in buf.getvalue(), 'the Hoth build failed'
    base = lore.stage_ossus.staging_base(stage)
    lore.stage_ossus.stage_ossus(stage, base)
    lore.species_tables.stage_species(['chiss'], stage, base=base)
    lore.ossus_minerals.stage_ossus_minerals(stage, base)
    lore.stage_lore_materials.stage_lore_materials(stage, base)
    names.stage_gem_names.stage_gem_names(stage, base)
    fauna.scn.stage_creature_names(stage, base)
    merged = smm.stage_mtg_merges(stage, base)
    twice = smm.stage_mtg_merges(stage, base)
    out_tre = os.path.join(HERE, 'local_planets-mtgmerge.tre')
    data, _ = lore.tre_write.pack_dir(stage, out_tre)
    ours = lore.tre_write.read(data)[0]
    ref_bytes = open(REF_TRE, 'rb').read()
    ref = lore.tre_write.read(ref_bytes)[0]
    changed = sorted(n for n in ref if n in ours and ref[n] != ours[n])
    new = sorted(n for n in ours if n not in ref)
    gone = sorted(n for n in ref if n not in ours)
    expected = sorted(list(smm.TABLES) + smm.STRINGS)
    out = {'built': '2026-10-15', 'archive': os.path.basename(out_tre), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
           'entries': len(ours),
           'reference': {'file': 'Local-model-ossus-fauna/local_planets-fauna.tre', 'sha256_expected': REF_SHA,
                         'sha256_ok': hashlib.sha256(ref_bytes).hexdigest() == REF_SHA},
           'against_fauna': {'changed': changed, 'new_entries': new, 'missing_entries': gone},
           'merged': merged,
           'idempotent': all(twice[k]['sha256'] == merged[k]['sha256'] for k in merged)}
    out['ok'] = (not changed and not gone and sorted(new) == expected and out['idempotent'] and out['reference']['sha256_ok']
                 and all(merged[k]['barc_keys'] for k in merged))
    with open(os.path.join(HERE, 'checks.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1, default=list)
    print(json.dumps({k: v for k, v in out.items() if k != 'merged'}, indent=1))
    for k, v in merged.items():
        print(f'  {k}: +{v["added"]} {v["from"]}; BARC: {v["barc_keys"][:4]}')
    return 0 if out['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
