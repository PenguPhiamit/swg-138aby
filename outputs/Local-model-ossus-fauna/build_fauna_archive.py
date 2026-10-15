"""The chain up to the gem names, plus the Ossus creature names (Claude, 15 Oct 2026). It runs:

    Hoth build > stage_ossus > stage_species chiss > stage_ossus_minerals > stage_lore_materials > stage_gem_names
    > stage_creature_names

Packs local_planets-fauna.tre and compares it with the installed names archive (Fable-resources3/names/,
39a89e6c). Only string/en/mob/creature_names.stf may change, by the six new keys; every existing key, its text and
every other entry stays byte-identical. Writes checks.json.

    python -I build_fauna_archive.py
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
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-resources3', 'names'))
import build_names_archive as names  # noqa: E402  (stock-only load order, the chain's modules)
sys.path.insert(0, HERE)
import stage_creature_names as scn  # noqa: E402

REF_TRE = os.path.join(OUTPUTS, 'Fable-resources3', 'names', 'local_planets-names.tre')
REF_SHA = '39a89e6c1bfdf72811e6b68be035d0228542f6dd9886c2c0ca1438a780d977db'


def main():
    lore = names.lore
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
    result = scn.stage_creature_names(stage, base)
    twice = scn.stage_creature_names(stage, base)
    out_tre = os.path.join(HERE, 'local_planets-fauna.tre')
    data, _ = lore.tre_write.pack_dir(stage, out_tre)
    ours = lore.tre_write.read(data)[0]
    ref_bytes = open(REF_TRE, 'rb').read()
    ref = lore.tre_write.read(ref_bytes)[0]
    changed = sorted(n for n in ref if n in ours and ref[n] != ours[n])
    new = sorted(n for n in ours if n not in ref)
    gone = sorted(n for n in ref if n not in ours)
    old_items = dict(names.lore.r3.st.stf_items(names.lore.r3.st.read_stf(ref[scn.STF])))
    new_items = dict(names.lore.r3.st.stf_items(names.lore.r3.st.read_stf(ours[scn.STF])))
    kept = all(new_items.get(k) == v for k, v in old_items.items())
    added = {k: new_items[k] for k in new_items if k not in old_items}
    out = {'built': '2026-10-15', 'archive': os.path.basename(out_tre), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
           'entries': len(ours),
           'reference': {'file': 'Fable-resources3/names/local_planets-names.tre', 'sha256_expected': REF_SHA,
                         'sha256_ok': hashlib.sha256(ref_bytes).hexdigest() == REF_SHA},
           'against_names': {'changed': changed, 'new_entries': new, 'missing_entries': gone},
           'creature_names': {'keys_before': len(old_items), 'keys_after': len(new_items), 'added': added, 'existing_kept': kept,
                              'idempotent': twice['added'] == [] and twice['sha256'] == result['sha256']}}
    out['ok'] = (changed == [scn.STF] and not new and not gone and kept and added == scn.NAMES
                 and out['creature_names']['idempotent'] and out['reference']['sha256_ok'])
    with open(os.path.join(HERE, 'checks.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))
    return 0 if out['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
