"""stage_gem_names.stage_gem_names(stage_dir, base): Ossus's five gem leaves get Adegan crystal names (Claude, 14 Oct 2026).

The owner asked to rename the placeholder gems ("Ossus Type 1/2 ... Gemstone"). Wookieepedia (Legends, "Adegan crystal")
names five grades, from the most common to the rarest: kathracite, relacite, danite, mephite, pontite. The first were found
on Ossus. Ossus has exactly five gem leaves (R3 part 2's two amorphous and two crystalline, and C29's Adegan leaf), so each
grade gets one. The crystalline gems become kathracite, mephite and pontite. Relacite and danite take the two amorphous
slots, the way stock's "Bal'ta'ran Crystal Amorphous Gemstone" puts a crystal in the amorphous class. Only the deepest
CLASS text changes. The ENUMs (the zone restriction and the pool lines key on them), attributes, pools, order and every
other cell stay. Core3 copies the class text into a spawn when it creates it (ResourceSpawner: setName(getFinalClass())),
so spawns already in the galaxy keep the old names until they expire or are despawned.
Last step of the chain, after stage_lore_materials. Idempotent.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R3 = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(R3), 'tools'))
sys.path.insert(0, os.path.join(R3, 'tools'))
from swgfmt import swg_tables as st  # noqa: E402
import ossus_minerals as om  # noqa: E402

TREE = om.TREE
# enum -> (placeholder text, new text), most common grade first
NAMES = {
    'crystalline_ossus_1': ('Ossus Type 1 Crystalline Gemstone', 'Kathracite Crystalline Gemstone'),
    'armophous_ossus_1': ('Ossus Type 1 Amorphous Gemstone', 'Relacite Crystal Amorphous Gemstone'),
    'armophous_ossus_2': ('Ossus Type 2 Amorphous Gemstone', 'Danite Crystal Amorphous Gemstone'),
    'crystalline_adegan_ossus': ('Adegan Crystal Crystalline Gemstone', 'Mephite Crystalline Gemstone'),
    'crystalline_ossus_2': ('Ossus Type 2 Crystalline Gemstone', 'Pontite Crystalline Gemstone'),
}


def stage_gem_names(stage_dir, base):
    data = base(TREE)
    tree = st.read_dtii(data)
    assert st.write_dtii(tree) == data, 'resource tree base does not round-trip'
    ci = {c: i for i, c in enumerate(tree['columns'])}
    depth, _, _ = om._analyse(tree['rows'], ci)
    rows = [list(r) for r in tree['rows']]
    by = {r[1]: r for r in rows}
    renamed = []
    for enum, (old, new) in NAMES.items():
        assert enum in by, f'{enum} missing: run after stage_ossus_minerals and stage_lore_materials'
        r = by[enum]
        col = ci['CLASS %d' % depth(r)]
        assert r[col] in (old, new), f'{enum}: unexpected text {r[col]!r}'
        if r[col] == old:
            r[col] = new
            renamed.append({'enum': enum, 'old': old, 'new': new})
    out = st.write_dtii({'version': tree['version'], 'columns': tree['columns'], 'types': tree['types'], 'rows': rows})
    back = st.read_dtii(out)
    assert [r[1] for r in back['rows']] == [r[1] for r in tree['rows']]
    path = os.path.join(stage_dir, TREE.replace('/', os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(out)
    return {'file': TREE, 'rows': len(back['rows']), 'renamed': renamed, 'sha256': hashlib.sha256(out).hexdigest()}


if __name__ == '__main__':
    print(__doc__)
