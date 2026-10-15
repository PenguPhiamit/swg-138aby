"""stage_npc_names.stage_npc_names(stage_dir, base): the five Ossus NPCs' names in the client (Claude, 15 Oct 2026).

The NPC templates in mobile/ name themselves "@mob/creature_names:<var>", like the creatures in Local-model-ossus-fauna/.
Each var gets one entry in string/en/mob/creature_names.stf, from npc_names.tsv ("a Ysanna hunter"). New keys only:
existing entries and ids stay, new ids continue from next_id (stf_add). Idempotent. Runs after stage_creature_names.
Not in the chain yet: it goes in with the next archive build, after the MTG shadow audit.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'tools'))
from swgfmt import swg_tables as st  # noqa: E402

STF = 'string/en/mob/creature_names.stf'


def load_names():
    names = {}
    with open(os.path.join(HERE, 'npc_names.tsv'), encoding='utf-8') as f:
        for line in f:
            if line.strip():
                var, text = line.rstrip('\n').split('\t')
                names[var] = text
    return names


NAMES = load_names()


def stage_npc_names(stage_dir, base):
    data = base(STF)   # the staging base reads the creatures' staged copy first
    stf = st.read_stf(data)
    assert st.write_stf(stf) == data, 'creature_names.stf does not round-trip'
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
