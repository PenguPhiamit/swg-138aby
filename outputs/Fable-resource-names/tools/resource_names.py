"""resource_names.stage_resource_names(stage_dir, base, tree=None): audit every class row of a resource tree against
string/en/resource/resource_names.stf and write the merged string file with every missing key added (Fable R1, 14 Oct 2026;
outputs/Fable-resource-names/README.md).

    from resource_names import stage_resource_names, audit
    report = stage_resource_names(stage_dir, base=fn, tree=merged_tree_bytes)   # fn(name) -> bytes of the winning copy
    report = stage_resource_names(stage_dir, base=fn)                           # tree = base('datatables/resource/resource_tree.iff')
    report = stage_resource_names(stage_dir, base=fn, tree=..., extra=OSSUS)    # optional extra keys (name -> text)

What the player sees is NOT this file: Core3 names a resource type from the tree's own CLASS text (ResourceSpawner.cpp:387
`newSpawn->setName(entry->getFinalClass())`, sent as plain text in ResourceListForSurveyMessage), and no stock archive
even ships resource_names.stf (only MTG's two copies do; no client file refers to it). The string file is kept in step
anyway: every key gets the exact CLASS text of its tree row, so the two sources agree wherever a UI might read the file.
Keys already present are never changed; the base is round-tripped byte-exact before it is touched.

    python -I resource_names.py <stage_dir>      stage from the client's winning copies (tree: Local-content/local_planets.tre staging copy)
    python -I resource_names.py --audit          print the audit only
"""
import csv
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
OUTPUTS = os.path.dirname(OUT)
for rel in ('Fable-ossus/tools', 'Fable-planet-test/tools'):
    p = os.path.join(OUTPUTS, rel)
    if p not in sys.path:
        sys.path.insert(0, p)
import swg_tables as st  # noqa: E402
import trn_iff  # noqa: E402

NAMES = 'string/en/resource/resource_names.stf'
TREE = 'datatables/resource/resource_tree.iff'
MERGED_STAGING = os.path.join(OUTPUTS, 'Local-content', 'local_planets.tre')   # Claude's archive: the merged tree, for the CLI audit only
OSSUS_TSV = os.path.join(OUTPUTS, 'Fable-ossus', 'o2', 'resources', 'resource_names.tsv')

# stock's planet words, read from fiberplast_<planet> in the stock tree (Fable-resource-names/README.md, table 2)
PLANET_WORDS = {'corellia': 'Corellian', 'dantooine': 'Dantooine', 'dathomir': 'Dathomirian', 'endor': 'Endorian', 'lok': 'Lokian',
                'naboo': 'Nabooian', 'rori': 'Rori', 'talus': 'Talusian', 'tatooine': 'Tatooinian', 'yavin4': 'Yavinian',
                'hoth': 'Hothian', 'ossus': 'Ossus', 'kaas': 'Kaasian', 'taanab': 'Taanab'}
# the eleven classes MTG gave Hoth that stock never gives a planet; class text = the stock tree's generic row, or MTG's wording
CLASS_TEXT = {'wheat_wild': 'Wild Wheat', 'petrochem_fuel_liquid': 'Liquid Petro Fuel', 'petrochem_fuel_solid': 'Solid Petro Fuel',
              'radioactive': 'Radioactive', 'steel': 'Steel', 'iron': 'Iron', 'aluminum': 'Aluminum', 'copper': 'Copper',
              'ore_extrusive': 'Extrusive Ore', 'ore_intrusive': 'Intrusive Ore', 'gas_reactive': 'Reactive Gas'}


def default_base(name):
    idx = trn_iff.client_index()
    arc = idx.get(name.lower())
    return None if arc is None else trn_iff.open_tre_entry(os.path.join(trn_iff.CLIENT, arc), name)


def tree_rows(tree_bytes):
    """[(enum, class text, depth, planet)] for every row; class text = the deepest filled CLASS column (Core3's finalClass)."""
    t = st.read_dtii(tree_bytes)
    ci = {c: i for i, c in enumerate(t['columns'])}
    rows = []
    for r in t['rows']:
        depth = max((i for i in range(1, 9) if r[ci['CLASS %d' % i]]), default=0)
        enum = r[1]
        planet = next((p for p in PLANET_WORDS if enum.endswith('_' + p)), '')
        rows.append((enum, r[ci['CLASS %d' % depth]] if depth else '', depth, planet))
    return rows


def proposed_name(enum, class_text):
    """The text for a key with no name: the tree's own class text; failing that, stock's pattern <planet word> <class>."""
    if class_text:
        return class_text
    for p, word in PLANET_WORDS.items():
        if enum.endswith('_' + p):
            cls = enum[:-len(p) - 1]
            return word + ' ' + CLASS_TEXT.get(cls, cls.replace('_', ' ').title())
    return enum.replace('_', ' ').title()


def audit(tree_bytes, names_bytes):
    names = dict(st.stf_items(st.read_stf(names_bytes)))
    rows = tree_rows(tree_bytes)
    missing = [(e, c, p) for e, c, d, p in rows if not names.get(e)]
    differs = [(e, c, names[e]) for e, c, d, p in rows if names.get(e) and names[e] != c]
    by_planet = {}
    for e, c, p in missing:
        by_planet.setdefault(p or '(no planet)', []).append(e)
    return {'tree_rows': len(rows), 'stf_keys': len(names), 'missing': missing, 'missing_by_planet': by_planet,
            'text_differs': differs}


def ossus_extra(path=OSSUS_TSV):
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding='utf-8', newline='') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            k, v = line.rstrip('\n').split('\t')[:2]
            out[k] = v
    return out


def stage_resource_names(stage_dir, base=None, tree=None, extra=None):
    base = base or default_base
    names_data = base(NAMES)
    if names_data is None:
        raise FileNotFoundError(NAMES + ' has no base copy (the stock client has none; MTG ships it)')
    tree_data = tree if tree is not None else base(TREE)
    if tree_data is None:
        raise FileNotFoundError(TREE + ' has no base copy')
    stf = st.read_stf(names_data)
    if st.write_stf(stf) != names_data:
        raise AssertionError(NAMES + ': base copy does not round-trip')
    t = st.read_dtii(tree_data)
    if st.write_dtii(t) != tree_data:
        raise AssertionError(TREE + ': tree bytes do not round-trip')
    have = dict(st.stf_items(stf))
    ids = {sid for sid, _ in stf['keys']}
    if stf['next_id'] <= max(ids, default=0):
        stf['next_id'] = max(ids) + 1
    rep = audit(tree_data, names_data)
    added = []
    for enum, cls, planet in rep['missing']:
        if enum == 'resource':          # the root row: no stock copy names it either
            continue
        st.stf_add(stf, enum, proposed_name(enum, cls))
        added.append((enum, proposed_name(enum, cls)))
    extra_added = []
    for k, v in (extra or {}).items():
        if k not in have and k not in dict(added):
            st.stf_add(stf, k, v)
            extra_added.append((k, v))
    out = st.write_stf(stf)
    back = st.read_stf(out)
    assert dict(st.stf_items(back)) == {**have, **dict(added), **dict(extra_added)}
    path = os.path.join(stage_dir, NAMES.replace('/', os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(out)
    return {'file': NAMES, 'base_bytes': len(names_data), 'base_roundtrip': True, 'base_keys': len(have), 'tree_rows': rep['tree_rows'],
            'added': added, 'extra_added': extra_added, 'skipped_root': 'resource' in [m[0] for m in rep['missing']],
            'keys': len(back['keys']), 'next_id': back['next_id'], 'bytes': len(out), 'sha256': hashlib.sha256(out).hexdigest(),
            'text_differs': len(rep['text_differs'])}


def main(argv):
    tree = trn_iff.open_tre_entry(MERGED_STAGING, TREE) if os.path.exists(MERGED_STAGING) else None
    if '--audit' in argv:
        rep = audit(tree, default_base(NAMES))
        print(json.dumps({k: v for k, v in rep.items() if k != 'text_differs'}, indent=1))
        print('text differs (tree vs stf):', len(rep['text_differs']))
        for d in rep['text_differs']:
            print('  ', d)
        return 0
    if not argv:
        print(__doc__)
        return 2
    extra = ossus_extra() if '--ossus' in argv else None
    rep = stage_resource_names(argv[0], tree=tree, extra=extra)
    print(json.dumps(rep, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
