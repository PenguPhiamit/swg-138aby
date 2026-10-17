"""Ossus ghostfire quest, the client half: palette entry 32 for the ghostfire blade and its colour name (Claude, 17 Oct 2026).

The server gives a colour crystal with colour 32 (patch core3-dev-ossus-ghostfire.patch). A lightsaber's blade colour is
the customization variable /private/index_color_blade, an index into palette/wp_lightsaber.pal (stock: 32 entries,
0-31; 31 is the "no colour" white of power crystals). This step appends entry 32, a dim pearly white, and names it:
  palette/wp_lightsaber.pal       the stock palette (patch_09.tre) + entry 32 = GHOSTFIRE; entries 0-31 unchanged
  string/en/jedi_spam.stf         + saber_color_32 "Saa's Ghostfire" (the crystal's colour attribute reads this key)
Every other entry of the base comes through byte for byte (checked). Nothing is installed. Whether the client draws index
32 (or clamps to the stock range) is the render check in README.md; the fallback is to reuse a free index instead.

    C:/Users/Pengw/miniconda3/python.exe -I build_ghostfire.py [--base PATH] [--out PATH]
Default base: ../../../work/nal-hutta-life/local_planets-nalhutta-life.tre (installed, sha256 b01e9f44...).
Default out:  ../../../work/ossus-ghostfire/local_planets-ghostfire.tre (+ .sha256), checks in ./checks-ghostfire.json.
"""
import argparse
import hashlib
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.dirname(os.path.dirname(HERE))
H = os.path.dirname(OUTPUTS)
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
from swgfmt import swg_tables as st  # noqa: E402
from swgfmt import tre_write  # noqa: E402
from swgfmt import trn_iff  # noqa: E402

DEFAULT_BASE = os.path.join(H, 'work', 'nal-hutta-life', 'local_planets-nalhutta-life.tre')
DEFAULT_BASE_SHA_PREFIX = 'b01e9f44'
DEFAULT_OUT = os.path.join(H, 'work', 'ossus-ghostfire', 'local_planets-ghostfire.tre')
PAL = 'palette/wp_lightsaber.pal'
SPAM = 'string/en/jedi_spam.stf'
INDEX = 32
GHOSTFIRE = (196, 192, 212)      # dim pearly white with a faint lavender sheen; the stock 31 is f2f2f2
COLOR_NAME = ('saber_color_32', "Saa's Ghostfire")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read_pal(data):
    assert data[:4] == b'RIFF' and data[8:16] == b'PAL data', data[:16]
    riff_size, = struct.unpack('<I', data[4:8])
    data_size, version, count = struct.unpack('<IHH', data[16:24])
    assert riff_size == len(data) - 8 and data_size == 4 + 4 * count and len(data) == 24 + 4 * count, (riff_size, data_size, count)
    return version, [tuple(data[24 + 4 * i:28 + 4 * i]) for i in range(count)]


def write_pal(version, entries):
    body = b''.join(bytes(e) for e in entries)
    return b'RIFF' + struct.pack('<I', 16 + len(body)) + b'PAL data' + struct.pack('<IHH', 4 + len(body), version, len(entries)) + body


def source(base, rel):
    if rel in base:
        return base[rel], 'base'
    data = trn_iff.client_file(rel)
    assert data is not None, rel
    return data, trn_iff.client_index()[rel]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default=DEFAULT_BASE)
    ap.add_argument('--out', default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    base_bytes = open(args.base, 'rb').read()
    base_sha = sha(base_bytes)
    if os.path.abspath(args.base) == os.path.abspath(DEFAULT_BASE):
        assert base_sha.startswith(DEFAULT_BASE_SHA_PREFIX), 'default base is not the installed b01e9f44: ' + base_sha
    base = tre_write.read(base_bytes)[0]

    pal_src, pal_from = source(base, PAL)
    assert write_pal(*read_pal(pal_src)) == pal_src, 'palette does not round-trip'
    version, entries = read_pal(pal_src)
    assert len(entries) == INDEX, 'palette already has %d entries' % len(entries)
    pal = write_pal(version, entries + [GHOSTFIRE + (0,)])
    assert read_pal(pal)[1][:INDEX] == entries

    spam_src, spam_from = source(base, SPAM)
    s = st.read_stf(spam_src)
    assert st.write_stf(s) == spam_src, 'jedi_spam.stf does not round-trip'
    have = dict(st.stf_items(s))
    assert COLOR_NAME[0] not in have and 'saber_color_31' in have
    ids = {sid for sid, _ in s['keys']}
    if s['next_id'] <= max(ids, default=0):
        s['next_id'] = max(ids) + 1
    st.stf_add(s, *COLOR_NAME)
    spam = st.write_stf(s)
    assert dict(st.stf_items(st.read_stf(spam))) == {**have, COLOR_NAME[0]: COLOR_NAME[1]}

    files = dict(base)
    files[PAL], files[SPAM] = pal, spam
    out = tre_write.pack(files)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'wb') as f:
        f.write(out)
    out_sha = sha(out)
    with open(args.out + '.sha256', 'w', newline='\n') as f:
        f.write('%s *%s\n' % (out_sha, os.path.basename(args.out)))

    ours = tre_write.read(out)[0]
    changed = sorted(n for n in base if n in ours and base[n] != ours[n])
    new = sorted(n for n in ours if n not in base)
    dropped = sorted(n for n in base if n not in ours)
    checks = {
        'base': {'path': os.path.relpath(args.base, H).replace(os.sep, '/'), 'sha256': base_sha, 'entries': len(base)},
        'out': {'path': os.path.relpath(args.out, H).replace(os.sep, '/'), 'bytes': len(out), 'sha256': out_sha, 'entries': len(ours)},
        'untouched_identical': len(base) - len(changed) - len(dropped), 'changed': changed, 'new': new, 'dropped': dropped,
        'palette': {'from': pal_from, 'entries_before': len(entries), 'entries_after': INDEX + 1,
                    'entry_31': '%02x%02x%02x' % entries[31][:3], 'entry_32': '%02x%02x%02x' % GHOSTFIRE},
        'colour_name': {'from': spam_from, COLOR_NAME[0]: COLOR_NAME[1]},
    }
    with open(os.path.join(HERE, 'checks-ghostfire.json'), 'w', encoding='utf-8') as f:
        json.dump(checks, f, indent=1)
    assert not dropped and set(changed) | set(new) == {PAL, SPAM}, (changed, new)
    print(json.dumps({k: checks[k] for k in ('base', 'out', 'untouched_identical', 'changed', 'new', 'palette')}, indent=1))
    print('Ghostfire client step: PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
