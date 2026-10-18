"""S6: local_planets-s6.tre = the C29 chain (Hoth build > stage_ossus > stage_species chiss > stage_ossus_minerals > stage_lore_materials)
+ stage_s6 (Nautolan male, Togruta female). Compares with the C29 archive (fbf62971...): every entry S6 touches must be a
superset of C29's (rows, blocks, keys, text), every added row/block/key must name one of the two species, every C29
appearance in the ACST must resolve identically (so the Chiss output is unchanged), and the closure of the two player
templates must resolve from our archive plus the client's load order. Writes checks.json and work/closure.json.
    python -I build_test_archive.py
"""
import hashlib
import io
import json
import os
import re
import shutil
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
SPECIES = os.path.dirname(HERE)
OUTPUTS = os.path.dirname(SPECIES)
R3 = os.path.join(OUTPUTS, 'Fable-resources3')
sys.path.insert(0, R3)
import build_test_archive as r3  # noqa: E402  (sets up the tool paths)
sys.path.insert(0, os.path.join(R3, 'lore'))
sys.path.insert(0, os.path.join(HERE, 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'Fable-live-client', 't2', 'staged', 'tools', 'swgfmt'))
from swgfmt import tre_write, trn_iff  # noqa: E402
from swgfmt import swg_tables as st  # noqa: E402
from swgfmt.trn_iff import parse, build  # noqa: E402
import asset_refs  # noqa: E402
import stage_ossus  # noqa: E402
import species_tables  # noqa: E402
import ossus_minerals  # noqa: E402
import stage_lore_materials  # noqa: E402
import stage_s6  # noqa: E402
import acst  # noqa: E402

C29_TRE = os.path.join(R3, 'lore', 'local_planets-lore.tre')
C29_SHA = 'fbf62971bbbf2b65e613c7972e2a65ea78b98740d0fa39e26e1613beb97d95b1'
OUT_TRE = os.path.join(HERE, 'local_planets-s6.tre')
SEEDS = ['object/creature/player/shared_nautolan_male.iff', 'object/creature/player/shared_togruta_female.iff']
NEW = ('nautolan', 'togruta')
IFF_RE = re.compile(rb'[A-Za-z0-9_/\.]+\.iff')


def names_species(text):
    t = text.lower()
    return [s for s in NEW if s in t]


def superset_dtii(old, new):
    """new's rows = old's rows in order with extra rows, each naming a new species."""
    to, tn = st.read_dtii(old), st.read_dtii(new)
    if to['columns'] != tn['columns'] or to['types'] != tn['types']:
        return {'ok': False, 'why': 'schema changed'}
    i, extra = 0, []
    for r in tn['rows']:
        if i < len(to['rows']) and r == to['rows'][i]:
            i += 1
        else:
            extra.append(r)
    ok = i == len(to['rows']) and all(names_species(json.dumps(r)) for r in extra)
    return {'ok': ok, 'rows_before': len(to['rows']), 'rows_after': len(tn['rows']), 'added': len(extra), 'old_rows_kept_in_order': i == len(to['rows'])}


def superset_ptmp(old, new):
    vo, vn = parse(old)[0].children[0], parse(new)[0].children[0]
    bo = [build([c]) for c in vo.children]
    bn = [build([c]) for c in vn.children]
    extra = bn[len(bo):]
    ok = bn[:len(bo)] == bo and all(names_species(b.decode('latin-1')) for b in extra)
    return {'ok': ok, 'blocks_before': len(bo), 'blocks_after': len(bn), 'added': len(extra)}


def superset_stf(old, new):
    ko, kn = dict(st.stf_items(st.read_stf(old))), dict(st.stf_items(st.read_stf(new)))
    extra = {k: v for k, v in kn.items() if k not in ko}
    ok = all(ko[k] == kn.get(k) for k in ko) and all(names_species(k) for k in extra)
    return {'ok': ok, 'keys_before': len(ko), 'keys_after': len(kn), 'added': sorted(extra)}


def superset_text(old, new):
    lo, ln = old.decode('latin-1').split('\r\n'), new.decode('latin-1').split('\r\n')
    i, extra = 0, []
    for l in ln:
        if i < len(lo) and l == lo[i]:
            i += 1
        else:
            extra.append(l)
    ok = i == len(lo) and all(names_species(l) or l.strip() in ('', '/>') or l.strip().startswith(('<Data', 'cameraoffset')) for l in extra)
    return {'ok': ok, 'lines_before': len(lo), 'lines_after': len(ln), 'added_lines': len(extra), 'added_blocks': sum(1 for l in extra if l.strip().startswith('<Data'))}


def acst_unchanged(old, new):
    do, dn = acst.read_acst(old), acst.read_acst(new)
    acst._tables(do); acst._tables(dn)
    bad = [crc for crc, k in do['cidx'] if crc not in dn['_c'] or acst.flatten(acst.resolve(do, k)) != acst.flatten(acst.resolve(dn, dn['_c'][crc]))]
    added = [crc for crc, _ in dn['cidx'] if crc not in do['_c']]
    return {'ok': not bad, 'appearances_before': len(do['cidx']), 'appearances_after': len(dn['cidx']), 'changed': len(bad), 'added_crcs': ['0x%08X' % c for c in added]}


def main():
    stage = os.path.join(HERE, 'work', 'local_planets')
    for p in (stage, stage + '.new'):
        if os.path.isdir(p):
            shutil.rmtree(p)
    builder = r3.load_patched_builder()
    builder.STAGE, builder.TRE = stage, os.path.join(HERE, 'work', 'local_planets.tre')
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = builder.main()
    assert rc == 0 and 'archive verified' in buf.getvalue(), 'the Hoth build failed'
    base = stage_ossus.staging_base(stage)
    stage_ossus.stage_ossus(stage, base)
    species_tables.stage_species(['chiss'], stage, base=base)
    ossus_minerals.stage_ossus_minerals(stage, base)
    stage_lore_materials.stage_lore_materials(stage, base)
    c29_bytes = open(C29_TRE, 'rb').read()
    c29 = tre_write.read(c29_bytes)[0]
    rebuilt, _ = tre_write.pack_dir(stage)
    c29_rebuilt_identical = rebuilt == c29_bytes
    # the copies the species step starts from (staging_base prefers staged files, so snapshot before stage_s6 writes)
    pre = {rel: base(rel) for rel in ['datatables/creation/racial_mods.iff', 'datatables/creation/attribute_limits.iff', 'datatables/skill/skills.iff',
                                      'ui/ui_avatardata.inc', 'string/en/player_species.stf', 'string/en/skl_n.stf', 'string/en/skl_d.stf',
                                      'customization/asset_customization_manager.iff'] + species_tables.CUSTOMIZATION_TABLES + species_tables.PTMP_TABLES}
    rep = stage_s6.stage_s6(stage, base)
    data, names = tre_write.pack_dir(stage, OUT_TRE)
    ours = tre_write.read(data)[0]
    changed = sorted(n for n in c29 if n in ours and c29[n] != ours[n])
    new = sorted(n for n in ours if n not in c29)
    identical = sum(1 for n in c29 if n in ours and c29[n] == ours[n])
    per_file = {}
    for n in changed + new:
        old = c29.get(n)
        if old is None:  # a new entry: compare with the copy the species step started from (the stock copy the C29 chain served)
            old = pre[n]
            assert old is not None
        if n.endswith('.inc'):
            per_file[n] = superset_text(old, ours[n])
        elif n.endswith('.stf'):
            per_file[n] = superset_stf(old, ours[n])
        elif n == 'customization/asset_customization_manager.iff':
            per_file[n] = acst_unchanged(old, ours[n])
        elif n.startswith('creation/'):
            per_file[n] = superset_ptmp(old, ours[n])
        else:
            per_file[n] = superset_dtii(old, ours[n])
        per_file[n]['status'] = 'changed' if n in c29 else 'new (vs the chain base copy)'
    # Chiss: every Chiss-naming row/block/key/line of C29 is in S6 (implied by the supersets); count them for the record
    chiss_rows = {}
    for n in changed:
        if n.endswith('.iff') and not n.startswith('creation/') and n != 'customization/asset_customization_manager.iff':
            chiss_rows[n] = (sum(1 for r in st.read_dtii(c29[n])['rows'] if 'chiss' in json.dumps(r).lower()), sum(1 for r in st.read_dtii(ours[n])['rows'] if 'chiss' in json.dumps(r).lower()))
    # registration and the species list
    crc = {name for _, name in st.read_cstb(ours['misc/planet_crc_string_table.iff'])['entries']}
    ui = ours['ui/ui_avatardata.inc'].decode('latin-1')
    species_listed = re.findall(r"Name='([a-z_]+)'", ui[ui.find("Name='SpeciesSelection'"):ui.find('</DataSource>', ui.find("Name='SpeciesSelection'"))])
    # closure of the two templates through our archive and the client's load order
    idx = trn_iff.client_index()

    def get(path):
        if path in ours:
            return ours[path], 'local_planets-s6.tre'
        arc = idx.get(path)
        return (None, None) if arc is None else (trn_iff.open_tre_entry(os.path.join(trn_iff.CLIENT, arc), path), os.path.basename(str(arc)))
    seen, queue, closure = set(), list(SEEDS), {}
    while queue:
        p = queue.pop()
        if p in seen:
            continue
        seen.add(p)
        d, src = get(p)
        if d is None:
            closure[p] = {'source': 'MISSING'}
            continue
        closure[p] = {'source': src, 'bytes': len(d), 'sha256': hashlib.sha256(d).hexdigest()}
        if p.endswith(('.dds', '.tga', '.wav', '.snd', '.flr', '.pal')):
            continue
        for r in asset_refs.refs(d):
            if r not in seen:
                queue.append(r)
    missing = sorted(p for p, v in closure.items() if v['source'] == 'MISSING')
    by_source = {}
    for v in closure.values():
        by_source[v['source']] = by_source.get(v['source'], 0) + 1
    with open(os.path.join(HERE, 'work', 'closure.json'), 'w', encoding='utf-8') as f:
        json.dump({'seeds': SEEDS, 'files': closure}, f, indent=1, sort_keys=True)
    out = {'built': '2026-10-14', 'archive': 's6/local_planets-s6.tre', 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data), 'entries': len(ours),
           'c29_reference': {'sha256_expected': C29_SHA, 'sha256_ok': hashlib.sha256(c29_bytes).hexdigest() == C29_SHA, 'chain_rebuild_identical_to_c29': c29_rebuilt_identical},
           'against_c29': {'entries_c29': len(c29), 'identical': identical, 'changed_by_s6': changed, 'new_entries': new, 'per_file': per_file,
                           'all_supersets_ok': all(v['ok'] for v in per_file.values()), 'chiss_rows_c29_vs_s6': chiss_rows},
           'species_stage': rep,
           'registration': {'planet_crc': {p: p in crc for p in ('hoth', 'ossus')}, 'species_listed': species_listed},
           'closure': {'seeds': SEEDS, 'files': len(closure), 'by_source': by_source, 'missing': missing,
                       'missing_only_voice_snd': all(m.endswith('.snd') for m in missing)},
           }
    out['ok'] = (out['c29_reference']['sha256_ok'] and c29_rebuilt_identical and out['against_c29']['all_supersets_ok'] and not [n for n in new if not n.startswith(('creation/', 'datatables/', 'string/', 'ui/', 'customization/'))]
                 and all(s in species_listed for s in NEW) and 'chiss' in species_listed and out['closure']['missing_only_voice_snd'] and rep.get('ok', False))
    with open(os.path.join(HERE, 'checks.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ('species_stage', 'against_c29')}, indent=1))
    print('changed:', changed)
    print('new:', new)
    for n, v in per_file.items():
        print('  ', 'ok ' if v['ok'] else 'BAD', n, {k: vv for k, vv in v.items() if k != 'ok'})
    print('species stage ok:', rep.get('ok'), rep.get('notes'))
    return 0 if out['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
