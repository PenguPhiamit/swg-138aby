"""The C29 chain plus the gem names (Claude, 14 Oct 2026): Hoth build > stage_ossus > stage_species chiss > stage_ossus_minerals
> stage_lore_materials > stage_gem_names. Packs names/local_planets-names.tre, compares it with the installed lore archive
(lore/local_planets-lore.tre, fbf62971). Only resource_tree may change, and in it only the deepest CLASS text of the five
gem rows: same rows, same order, every other cell and every other entry byte-identical. Writes names/checks.json.
    python -I build_names_archive.py
"""
import hashlib
import io
import json
import os
import shutil
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
R3 = os.path.dirname(HERE)
OUTPUTS = os.path.dirname(R3)
# The chain's base files are the client's winning copies (swgfmt.trn_iff.client_index, from client_load_order). While the
# test launcher has written swgemu_login.cfg, that load order includes our own local_planets.tre, so the base would already
# hold Chiss and Ossus and the species step would stage nothing. Build from the stock and MTG archives only.
sys.path.insert(0, os.path.join(OUTPUTS, 'tools', 'hoth'))
import client_load_order as clo  # noqa: E402
_load_order = clo.load_order


def _without_ours(login=None):
    trees, ignored, top = _load_order(login)
    return [t for t in trees if t[1].lower() != 'local_planets.tre'], ignored, top


clo.load_order = _without_ours
sys.path.insert(0, os.path.join(R3, 'lore'))
import build_lore_archive as lore  # noqa: E402  (sets up the chain's paths and modules; its main() is not run)
sys.path.insert(0, HERE)
import stage_gem_names  # noqa: E402

LORE_TRE = os.path.join(R3, 'lore', 'local_planets-lore.tre')
LORE_SHA = 'fbf62971bbbf2b65e613c7972e2a65ea78b98740d0fa39e26e1613beb97d95b1'


def main():
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
    names = stage_gem_names.stage_gem_names(stage, base)
    twice = stage_gem_names.stage_gem_names(stage, base)   # idempotence
    out_tre = os.path.join(HERE, 'local_planets-names.tre')
    data, _ = lore.tre_write.pack_dir(stage, out_tre)
    ours = lore.tre_write.read(data)[0]
    ref_bytes = open(LORE_TRE, 'rb').read()
    ref = lore.tre_write.read(ref_bytes)[0]
    changed = sorted(n for n in ref if n in ours and ref[n] != ours[n])
    new = sorted(n for n in ours if n not in ref)
    gone = sorted(n for n in ref if n not in ours)
    t_new, ci = lore.r3.tree_rows(ours[stage_gem_names.TREE])
    t_old, _ = lore.r3.tree_rows(ref[stage_gem_names.TREE])
    same_rows = [r[1] for r in t_new['rows']] == [r[1] for r in t_old['rows']]
    cells = []   # (enum, column, old, new) for every cell that differs
    for a, b in zip(t_old['rows'], t_new['rows']):
        for k, (x, y) in enumerate(zip(a, b)):
            if x != y:
                cells.append((a[1], t_old['columns'][k], x, y))
    expected = sorted((e, o, n) for e, (o, n) in stage_gem_names.NAMES.items())
    only_names = sorted((e, x, y) for e, col, x, y in cells) == expected and all(col.startswith('CLASS ') for _, col, _, _ in cells)
    out = {'built': '2026-10-14', 'archive': os.path.basename(out_tre), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data), 'entries': len(ours),
           'reference': {'file': 'lore/' + os.path.basename(LORE_TRE), 'sha256_expected': LORE_SHA, 'sha256_ok': hashlib.sha256(ref_bytes).hexdigest() == LORE_SHA},
           'against_lore': {'changed': changed, 'new_entries': new, 'missing_entries': gone},
           'resource_tree': {'rows': len(t_new['rows']), 'same_rows_same_order': same_rows, 'cells_changed': cells, 'only_the_five_names': only_names,
                             'idempotent': twice['renamed'] == [] and twice['sha256'] == names['sha256']},
           'ok': changed == [stage_gem_names.TREE] and not new and not gone and same_rows and only_names and twice['renamed'] == []}
    out['ok'] = out['ok'] and out['reference']['sha256_ok']
    with open(os.path.join(HERE, 'checks.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))
    return 0 if out['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
