"""Creation fixes: the INSTALLED local_planets.tre (f0191ab5, chain-1017) + two stock creation-data fixes.

The creation sweep (run 25, 17 Oct 6:17 AM; functional-test-plan.md section 2) found two SOE data bugs that only our
archive can fix, since local_planets.tre is first in both the client's and the server's load order:
  B1  string/en/player_species.stf (patch_12_00, copied unchanged): desc_sullustan's ATTRIBUTES block shows the Zabrak's
      numbers and desc_ithorian's shows the Mon Calamari's. Only the nine +N values of those two blocks change; the
      prose and every other text stay as they are.
  B2  creation/profession_defaults_combat_brawler.iff: the Ithorian male gets ith_jacket_s16, which has no template on
      the server or in the client (3 ERROR lines per creation, no jacket). The human male Brawler wears jacket_s16,
      "Cold Weather Jacket"; the closest Ithorian one is ith_jacket_s12, "Ithorian Warm Jacket", which exists on both
      sides. The female Brawler's block has no jacket. Same path length, so the swap is a byte-for-byte replacement.
Every other entry stays byte-identical (checked after packing).
    C:/Users/Pengw/miniconda3/python.exe -I build_creation_fixes.py
Writes local_planets-creation-fixes.tre and checks.json beside this file. Nothing is installed.
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
from swgfmt import tre_write  # noqa: E402
from swgfmt import swg_tables as st  # noqa: E402
from swgfmt import trn_iff as iff  # noqa: E402

INSTALLED = os.path.join(OUTPUTS, 'SWG-client', 'local_planets.tre')
INSTALLED_SHA = 'f0191ab533911c7cd91df667d79a6b589fbab210e2982db456385a5610019808'  # board lock line, 17 Oct
OUT_TRE = os.path.join(HERE, 'local_planets-creation-fixes.tre')

ATTRIBUTES = ['Health', 'Strength', 'Constitution', 'Action', 'Quickness', 'Stamina', 'Mind', 'Focus', 'Willpower']
SPECIES_TEXT = 'string/en/player_species.stf'
RACIAL = 'datatables/creation/racial_mods.iff'
# The racial rows as the sweep read them on 17 Oct; also read from racial_mods.iff below and must agree.
FIXES_B1 = {'desc_sullustan': ('sullustan_male', [150, 0, 0, 250, 50, 50, 200, 100, 100]),
            'desc_ithorian': ('ithorian_male', [400, 100, 100, 100, 0, 0, 200, 0, 0])}
BRAWLER = 'creation/profession_defaults_combat_brawler.iff'
OLD_JACKET = b'object/tangible/wearables/ithorian/shared_ith_jacket_s16.iff\x00'
NEW_JACKET = b'object/tangible/wearables/ithorian/shared_ith_jacket_s12.iff\x00'
ALLOWED_CHANGES = {SPECIES_TEXT, BRAWLER}


def shown(text):
    """The nine +N values of a description's ATTRIBUTES block (as creation-sweep.attribute_block reads them)."""
    found = dict(re.findall(r'\\>024(\w+):\s*\\>128\+?(-?\d+)', text.split('ATTRIBUTES', 1)[1]))
    return [int(found[a]) for a in ATTRIBUTES]


def fix_block(text, values):
    head, block = text.split('ATTRIBUTES', 1)
    for name, value in zip(ATTRIBUTES, values):
        block, n = re.subn(r'(\\>024%s:\s*\\>128)\+?-?\d+' % name, lambda m: '%s+%d' % (m.group(1), value), block)
        assert n == 1, name
    return head + 'ATTRIBUTES' + block


def fix_species_text(data, racial):
    stf = st.read_stf(data)
    keys = dict((k, sid) for sid, k in stf['keys'])
    texts = []
    for sid, crc, text in stf['texts']:
        for key, (template, values) in FIXES_B1.items():
            if sid == keys[key]:
                assert racial[template] == values, (template, racial[template])
                text = fix_block(text, values)
        texts.append((sid, crc, text))
    stf['texts'] = texts
    return st.write_stf(stf)


def ithorian_brawler(data):
    root = iff.parse(data)
    out = {}
    for b in root[0].children[0].children:
        if b.is_form and b.form == 'PTMP' and b'ithorian' in b.children[0].data:
            who = b.children[0].data.rstrip(b'\0').decode().rsplit('/', 1)[-1]
            out[who] = [re.search(rb'object/\S+?\.iff', c.data).group(0).decode() for c in b.children[1:]]
    return out


def main():
    installed_bytes = open(INSTALLED, 'rb').read()
    sha = hashlib.sha256(installed_bytes).hexdigest()
    assert sha == INSTALLED_SHA, 'the installed archive is not f0191ab5 (%s); rebuild on the new chain' % sha[:8]
    base = tre_write.read(installed_bytes)[0]

    racial = {}
    for row in st.read_dtii(base[RACIAL])['rows']:
        for template in row[:2]:
            if template:
                racial[template] = list(row[2:11])

    ours = dict(base)
    ours[SPECIES_TEXT] = fix_species_text(base[SPECIES_TEXT], racial)
    assert base[BRAWLER].count(OLD_JACKET) == 1 and len(OLD_JACKET) == len(NEW_JACKET)
    ours[BRAWLER] = base[BRAWLER].replace(OLD_JACKET, NEW_JACKET)
    # The new jacket exists in the client archives (its object template and its appearance).
    index = iff.client_index()
    for rel in (NEW_JACKET.rstrip(b'\0').decode(), 'appearance/ith_jacket_s12_f.sat'):
        assert rel in index, rel

    data = tre_write.pack(ours)
    with open(OUT_TRE, 'wb') as f:
        f.write(data)
    packed = tre_write.read(data)[0]
    changed = sorted(n for n in base if n in packed and base[n] != packed[n])
    missing = sorted(n for n in base if n not in packed)
    new = sorted(n for n in packed if n not in base)
    assert not missing and not new, (missing, new)
    assert set(changed) == ALLOWED_CHANGES, changed

    # B1 in the packed archive: the two blocks show their racial rows; every other text is unchanged.
    before = dict(st.stf_items(st.read_stf(base[SPECIES_TEXT])))
    after = dict(st.stf_items(st.read_stf(packed[SPECIES_TEXT])))
    assert before.keys() == after.keys()
    differ = sorted(k for k in before if before[k] != after[k])
    assert differ == sorted(FIXES_B1), differ
    for key, (template, values) in FIXES_B1.items():
        assert shown(after[key]) == values == racial[template], key
        assert after[key].split('ATTRIBUTES', 1)[0] == before[key].split('ATTRIBUTES', 1)[0], key  # prose untouched
    # B2 in the packed archive: only the one item changed.
    was, now = ithorian_brawler(base[BRAWLER]), ithorian_brawler(packed[BRAWLER])
    assert was['shared_ithorian_female.iff'] == now['shared_ithorian_female.iff']
    assert [a for a in was['shared_ithorian_male.iff'] if 'jacket' not in a] == \
           [a for a in now['shared_ithorian_male.iff'] if 'jacket' not in a]
    assert 'object/tangible/wearables/ithorian/shared_ith_jacket_s12.iff' in now['shared_ithorian_male.iff']
    assert b'ith_jacket_s16' not in packed[BRAWLER]

    checks = {
        'installed': {'path': 'SWG-client/local_planets.tre', 'bytes': len(installed_bytes), 'sha256': sha,
                      'entries': len(base)},
        'out': {'path': os.path.relpath(OUT_TRE, OUTPUTS).replace(os.sep, '/'), 'bytes': len(data),
                'sha256': hashlib.sha256(data).hexdigest(), 'entries': len(packed)},
        'untouched_identical': len(base) - len(changed), 'changed': changed, 'new': new, 'dropped': missing,
        'B1': {k: {'was': shown(before[k]), 'now': shown(after[k])} for k in FIXES_B1},
        'B2': {'ithorian_male_brawler_was': was['shared_ithorian_male.iff'],
               'ithorian_male_brawler_now': now['shared_ithorian_male.iff']},
    }
    with open(os.path.join(HERE, 'checks.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1)
    print(json.dumps(checks, indent=1))
    print('B1 and B2 verified in the packed archive; %d of %d entries byte-identical' % (len(base) - len(changed),
                                                                                         len(base)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
