"""stage_creature_names.stage_creature_names(stage_dir, base): the six Ossus creatures' names in the client (Claude, 15 Oct 2026).

The mobile templates in mobile/ name themselves "@mob/creature_names:<var>". The client shows that key's text from
string/en/mob/creature_names.stf, so each var gets one entry, written the stock way ("a falumpaset", "a womp rat"). New
keys only: existing entries and ids stay, new ids continue from next_id (stf_add). Idempotent.
Last step of the chain, after stage_gem_names (Fable-resources3/names/).
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'tools'))
from swgfmt import swg_tables as st  # noqa: E402

STF = 'string/en/mob/creature_names.stf'
NAMES = {   # var -> in-game name (creature_names.tsv, in the stock "a/an ..." form)
    'ossus_mud_yak': 'a mud yak',
    'ossus_kirruk': 'a kirruk',
    'ossus_gokob': 'a gokob',
    'ossus_tree_frog': 'an Ossus tree frog',
    'ossus_tribis': 'a tribis',
    'ossus_kaddyr_bug': 'a kaddyr bug',
}


def stage_creature_names(stage_dir, base):
    data = base(STF)
    stf = st.read_stf(data)
    assert st.write_stf(stf) == data, 'creature_names.stf base does not round-trip'
    have = dict(st.stf_items(stf))
    added = []
    for key, text in NAMES.items():
        if key in have:
            assert have[key] == text, f'{key} already has another text: {have[key]!r}'
            continue
        st.stf_add(stf, key, text)
        added.append(key)
    out = st.write_stf(stf)
    back = dict(st.stf_items(st.read_stf(out)))
    assert all(back[k] == v for k, v in have.items()) and all(back[k] == v for k, v in NAMES.items())
    path = os.path.join(stage_dir, STF.replace('/', os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(out)
    return {'file': STF, 'keys': len(back), 'added': added, 'sha256': hashlib.sha256(out).hexdigest()}


if __name__ == '__main__':
    print(__doc__)
