"""S7 Level 1: build the playable Hutt's animation table, appearance/lat/hutt.lat. Our own code (Claude, 16 Oct 2026).

    python -I build_hutt_lat.py              # build staged/client/appearance/lat/hutt.lat, then run every check
    python -I build_hutt_lat.py --check      # re-run the checks on the staged file only
    python -I build_hutt_lat.py --stock FILE # build from a stock hutt.lat on disk instead of the client archives

Input 1: the stock hutt.lat, read from the client archives the way the live client resolves it (patch_05.tre wins; 206
ANIM entries) or from --stock. Input 2: animation-map.json (Fable's 631 mappings). Output: the stock table with the 631
entries appended and the entry count in the header corrected, written without timestamps so a rerun gives the same bytes.
Nothing is packed and nothing under /opt/swg is touched; build-notes.md explains the format and the packing step.

The format, as read from the stock tables (details in build-notes.md):
    FORM LATT > FORM 0000 > INFO  <ash path>NUL + uint16 LE number of ANIM forms
                          > FORM ANIM * count  > INFO <logical animation name>NUL, then ONE node
    nodes: PXAT (one .ans), TSCL (time scale + child), SPAT (speed blend), YWAT (yaw), DRAT (directions), AGAT (ambient
    gestures over a LOOP), SSAT (state variable switch), PBAT/COMP (pose blends)
"""
import argparse
import copy
import hashlib
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))                  # .../Fable-species/s7-hutt
OUTPUTS = os.path.normpath(os.path.join(ROOT, '..', '..'))          # .../outputs
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'tools', 'hoth'))
from swgfmt import trn_iff as iff  # noqa: E402
import client_load_order as clo  # noqa: E402

MAP_JSON = os.path.join(ROOT, 'animation-map.json')
OUT_LAT = os.path.join(ROOT, 'staged', 'client', 'appearance', 'lat', 'hutt.lat')
OUT_REPORT = os.path.join(ROOT, 'out', 'hutt-lat-check.json')
LAT_PATH = 'appearance/lat/hutt.lat'
ASH_PATH = 'appearance/ash/all_b.ash'
SKT_PATH = 'appearance/skeleton/hutt.skt'
ANS_DIR = 'appearance/animation/'
NUL = b'\x00'
TRANSITION_SCALE = 2.0          # TSCL time scale for transitions (Fable's map; the human trn_* entries use 1.25 to 3.0)
GESTURE_WEIGHT = 100.0          # the stock Hutt AGAT blocks all use 100.0 (Fable's note said 200; weights are relative)
# the stock Hutt table names its rifle stance loop_rifle; Fable's map says loop_rifle_standing
SOURCE_ALIAS = {'loop_rifle_standing': 'loop_rifle'}
# the human tables compared against: what the test launcher loads (local_planets.tre at 49 carries all_m.lat; all_f.lat is MTG's)
HUMAN_SPECS = ['tre:local_planets.tre:appearance/lat/all_m.lat', 'tre:mtg_patch_022.tre:appearance/lat/all_f.lat']
SKIP_RULES = [r'^force_', r'^jedi_', r'_jedi_combo_', r'^add_force', r'_attack_mask$']   # animation-map.json skipped_rules


# ----------------------------------------------------------------------------------------------------- small helpers

def cstr(s):
    return s.encode('latin-1') + NUL


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def read_cstrs(data, pos, n):
    out = []
    for _ in range(n):
        j = data.index(NUL, pos)
        out.append(data[pos:j].decode('latin-1'))
        pos = j + 1
    return out, pos


def anim_name(a):
    return a.children[0].data.rstrip(NUL).decode('latin-1')


def anim_node(a):
    return a.children[1]


def read_lat(data):
    """(ash path, count field, [ANIM nodes], LATT node) of a LAT file."""
    root = iff.parse(data)
    assert len(root) == 1 and root[0].is_form and root[0].form == 'LATT', 'not a LATT file'
    f0 = root[0].children[0]
    assert f0.form == '0000', 'unexpected LATT version ' + f0.form
    info = f0.children[0]
    assert info.tag == 'INFO'
    (ash,), pos = read_cstrs(info.data, 0, 1)
    assert len(info.data) == pos + 2, 'INFO is not path + uint16'
    count = struct.unpack_from('<H', info.data, pos)[0]
    anims = f0.children[1:]
    assert all(a.is_form and a.form == 'ANIM' for a in anims), 'a child of FORM 0000 is not an ANIM form'
    return ash, count, anims, root[0]


def ans_paths(node):
    """Every .ans path under a node, in file order (the INFO of each PXAT/0000)."""
    return [n.data[:-1].decode('latin-1') for _, n in iff.walk([node]) if n.tag == 'INFO' and n.data.endswith(b'.ans' + NUL)]


def punf_category(px):
    """The category of a PXAT node (first string of its PUNF), or None."""
    for c in px.children[0].children:
        if c.tag == 'PUNF':
            return c.data.split(NUL)[0].decode('latin-1')
    return None


def agat_gestures(agat_form):
    """(min s, max s, [(action, weight)], loop child) of an AGAT form."""
    f0 = agat_form.children[0]
    lo, hi = struct.unpack('<ff', f0.children[0].data)
    actn = f0.children[1].data
    n, pos, out = struct.unpack_from('<H', actn)[0], 2, []
    for _ in range(n):
        (g,), pos = read_cstrs(actn, pos, 1)
        out.append((g, struct.unpack_from('<f', actn, pos)[0]))
        pos += 4
    assert pos == len(actn)
    return lo, hi, out, f0.children[2].children[0]


# ----------------------------------------------------------------------------------------------------- node writers

def pxat(ans, category=None):
    """PXAT/0000 = INFO <ans>NUL [+ PUNF <category>NUL<category>NUL]. The Hutt table's std_* entries carry no PUNF."""
    kids = [iff.chunk('INFO', cstr(ans))]
    if category:
        kids.append(iff.chunk('PUNF', cstr(category) + cstr(category)))
    return iff.form('PXAT', iff.form('0000', *kids))


def tscl(scale, child):
    """TSCL/0000 = INFO float32 time scale + one child node."""
    return iff.form('TSCL', iff.form('0000', iff.chunk('INFO', struct.pack('<f', scale)), child))


def spat(children):
    """SPAT/0000 = INFO uint8 child count + children. The client picks the child whose motion speed fits (idle =
    zero_speed, the others locomotion), so the order is free: the stock DRAT sets list run, idle, walk."""
    return iff.form('SPAT', iff.form('0000', iff.chunk('INFO', bytes([len(children)])), *children))


def agat(min_s, max_s, gestures, loop_child, weight=GESTURE_WEIGHT):
    """AGAT/0000 = INFO float32 min, float32 max seconds + ACTN (uint16 n, n x (action name NUL, float32 weight)) + FORM LOOP."""
    actn = struct.pack('<H', len(gestures)) + b''.join(cstr(g) + struct.pack('<f', weight) for g in gestures)
    return iff.form('AGAT', iff.form('0000', iff.chunk('INFO', struct.pack('<ff', min_s, max_s)),
                                     iff.chunk('ACTN', actn), iff.form('LOOP', loop_child)))


def anim(name, node):
    return iff.form('ANIM', iff.chunk('INFO', cstr(name)), node)


# ----------------------------------------------------------------------------------------------------- the animation state hierarchy

def parse_state(stat):
    kids = stat.children
    st = {'name': None, 'loop': None, 'actions': {}, 'links': [], 'children': []}
    (st['name'], st['loop']), _ = read_cstrs(kids[0].data, 0, 2)
    for c in kids[1:]:
        if c.form == 'ACTS':                      # INFO uint16 count, then ACTN (action NUL anim NUL + flags) or MVAC (2 ACTN)
            for a in c.children[1:]:
                for x in ([a] if a.tag == 'ACTN' else a.children):
                    (act, an), _ = read_cstrs(x.data, 0, 2)
                    st['actions'].setdefault(act, []).append(an)
        elif c.form == 'LNKS':                    # LINK = uint16 n, n state names, byte flag, transition animation NUL
            for link in c.children[1:]:
                n = struct.unpack_from('<H', link.data)[0]
                names, pos = read_cstrs(link.data, 2, n)
                (trn,), end = read_cstrs(link.data, pos + 1, 1)
                assert end == len(link.data), 'unexpected LINK layout'
                st['links'].append((names, trn))
        elif c.form == 'CHLD':
            st['children'] += [parse_state(s) for s in c.children[1:]]
    return st


def load_ash():
    root = iff.parse(iff.load('client:' + ASH_PATH))[0]
    return parse_state(root.children[0].children[0])


def walk_states(st):
    yield st
    for c in st['children']:
        yield from walk_states(c)


def ash_names(ash):
    """Every animation name the ash can ask the table for: state loops, action targets, link transitions ('default' is the ash's no-op)."""
    names = set()
    for s in walk_states(ash):
        names.add(s['loop'])
        for anims in s['actions'].values():
            names.update(anims)
        names.update(t for _, t in s['links'] if t)
    names.discard('default')
    return names


def gesture_action(ash, wanted):
    """AGAT gestures are ash ACTION names (stock Hutt: 'angry' -> emt_pound_fist_palm), not .lat names. Fable's list gives
    animation names; return the root-state action that plays it (the action named like the animation minus 'emt_' when
    several do)."""
    acts = ash['actions']
    if wanted in acts:
        return wanted
    cands = sorted(a for a, targets in acts.items() if wanted in targets)
    if not cands:
        raise KeyError('no ash action plays ' + wanted)
    bare = wanted[4:] if wanted.startswith('emt_') else wanted
    return bare if bare in cands else cands[0]


# ----------------------------------------------------------------------------------------------------- reading the client

_TREES = []


def loaded_archives():
    """[(priority, archive)] the live cfg chain loads (swgemu.cfg and its includes, [SharedFile] below maxSearchPriority), highest first."""
    if not _TREES:
        _TREES.extend(clo.load_order()[0])
    return _TREES


def archive_path(name):
    return os.path.join(iff.CLIENT, name)


def holders(path):
    """[(priority, archive)] of every loaded archive that holds path, highest priority first."""
    return [(pri, name) for pri, name in loaded_archives()
            if os.path.exists(archive_path(name)) and path.lower() in iff.list_tre(archive_path(name))]


def read_stock():
    pri, name = holders(LAT_PATH)[0]
    return iff.open_tre_entry(archive_path(name), LAT_PATH), name, pri


def lat_names(data):
    return [anim_name(a) for a in read_lat(data)[2]]


def skeleton_bones():
    root = iff.parse(iff.load('client:' + SKT_PATH))[0]
    lod0 = root.children[0].children[1]                       # the first SKTM = LOD 0
    names = next(c for c in lod0.children[0].children if c.tag == 'NAME').data
    return set(names.decode('latin-1').split('\x00')) - {''}


def ans_bones(data):
    top = iff.parse(data)
    return top[0].form, {n.data[:n.data.index(NUL)].decode('latin-1') for _, n in iff.walk(top) if n.tag == 'XFIN'}


# ----------------------------------------------------------------------------------------------------- the build

def source_entry(spec, stock_by_name, want_kind):
    m = re.match(r'^hutt (\S+)', spec)
    assert m, 'cannot read the source entry in ' + repr(spec)
    name = SOURCE_ALIAS.get(m.group(1), m.group(1))
    src = stock_by_name[name]
    assert anim_node(src).form == want_kind, f'{name} is {anim_node(src).form}, expected {want_kind}'
    return name, src


def build(stock, mapping, ash):
    ash_path, count, stock_anims, _ = read_lat(stock)
    assert count == len(stock_anims), 'stock count field does not match its ANIM forms'
    stock_by_name = {anim_name(a): a for a in stock_anims}
    assert len(stock_by_name) == len(stock_anims)
    entries = mapping['entries']
    by_action = {e['action']: e for e in entries}
    log = {'copied_from': {}, 'gestures': None}

    new = []
    for e in entries:
        name, kind, cat, ans = e['action'], e['hutt_kind'], e['category'], e['hutt_ans']
        if name in stock_by_name:
            raise ValueError(name + ' is already in the stock table')
        if kind == 'PXAT':
            node = pxat(ans, cat)
        elif kind == 'TSCL/PXAT':
            node = tscl(TRANSITION_SCALE, pxat(ans, cat))
        elif kind in ('DRAT', 'YWAT'):
            src_name, src = source_entry(e['copy_structure_of'], stock_by_name, kind)
            node = copy.deepcopy(anim_node(src))
            log['copied_from'][name] = src_name
            have = ans_paths(node)
            if kind == 'YWAT':
                assert sorted(have) == sorted(ans), f'{name}: the map lists {ans}, {src_name} holds {have}'
            else:
                n = int(re.match(r'same (\d+) files', ans).group(1))
                assert len(have) == n, f'{name}: the map says {n} files, {src_name} holds {len(have)}'
        elif kind == 'SPAT':
            idle, crawl = ans            # loop_crouched / loop_prone: idle + the unused stock crawl as the only locomotion
            node = spat([pxat(idle, 'zero_speed'), pxat(crawl, 'locomotion')])
        elif kind == 'AGAT over LOOP':
            spec = e if 'gestures' in e else by_action['loop_skill']
            actions = [gesture_action(ash, g) for g in spec['gestures']]
            lo, hi = spec['interval_seconds']
            node = agat(lo, hi, actions, pxat(ans, 'zero_speed'))
            log['gestures'] = dict(zip(spec['gestures'], actions))
        else:
            raise ValueError(f'{name}: unknown kind {kind}')
        new.append(anim(name, node))

    total = len(stock_anims) + len(new)
    assert total < 65536
    info = iff.chunk('INFO', cstr(ash_path) + struct.pack('<H', total))
    out = iff.build([iff.form('LATT', iff.form('0000', info, *stock_anims, *new))])
    return out, log


# ----------------------------------------------------------------------------------------------------- checks

def check(out, stock, mapping, ash, log):
    """Re-parse the output and test it. Returns the report dict; report['pass'] is True only if every test passed."""
    R = {'tests': {}, 'numbers': {}}
    N = R['numbers']

    def test(name, ok, detail=None):
        R['tests'][name] = {'pass': bool(ok), **({'detail': detail} if detail is not None else {})}

    s_ash, s_count, s_anims, _ = read_lat(stock)
    o_ash, o_count, o_anims, _ = read_lat(out)
    o_names = [anim_name(a) for a in o_anims]
    out_set, stock_set = set(o_names), set(lat_names(stock))
    entries = mapping['entries']
    new_anims = o_anims[len(s_anims):]

    # 1. structure and count
    test('round trip', iff.build(iff.parse(out)) == out, 'parse -> build gives the same bytes')
    test('header', o_ash == s_ash == ASH_PATH, o_ash)
    test('count field equals the ANIM forms', o_count == len(o_anims), f'{o_count} == {len(o_anims)}')
    test('count = stock + map', len(o_anims) == len(s_anims) + len(entries), f'{len(s_anims)} + {len(entries)} = {len(o_anims)}')
    test('stock entries untouched, in order', len(o_anims) >= len(s_anims) and all(iff.build([a]) == iff.build([b]) for a, b in zip(o_anims, s_anims)),
         f'first {len(s_anims)} entries byte-identical')
    test('names unique', len(out_set) == len(o_names))
    test('every map action added, in map order', [anim_name(a) for a in new_anims] == [e['action'] for e in entries])

    raw = {'anims': 0}                           # a second walker that uses only struct, not trn_iff

    def walk_raw(buf, i, end):
        while i < end:
            size = struct.unpack_from('>I', buf, i + 4)[0]
            if buf[i:i + 4] == b'FORM':
                if buf[i + 8:i + 12] == b'ANIM':
                    raw['anims'] += 1
                else:
                    walk_raw(buf, i + 12, i + 8 + size)
            i += 8 + size
    walk_raw(out, 0, len(out))
    test('independent walker counts the same ANIM forms', raw['anims'] == len(o_anims), raw['anims'])

    # 2. coverage of the human tables
    human, per_table = set(), {}
    for spec in HUMAN_SPECS:
        names = lat_names(iff.load(spec))
        per_table[spec] = {'entries': len(names), 'distinct': len(set(names))}
        human |= set(names)
    absent = sorted(human - out_set)
    unexplained = [n for n in absent if not any(re.search(p, n) for p in SKIP_RULES)]
    test('every human action is present except the skip rules', not unexplained, {'absent': len(absent), 'absent_not_covered_by_a_rule': unexplained})
    N['human_tables'] = per_table
    N['human_distinct'] = len(human)
    N['absent_by_skip_rule'] = len(absent)
    N['human_names_in_stock_hutt'] = len(human & stock_set)
    N['human_names_missing_from_stock_hutt'] = len(human - stock_set)
    N['human_names_in_new_hutt'] = len(human & out_set)
    N['hutt_only_names'] = sorted(out_set - human)
    N['mapped_though_a_skip_rule_matches'] = sorted(e['action'] for e in entries if any(re.search(p, e['action']) for p in SKIP_RULES))

    # 3. node kinds, and no human bone masks
    kinds = {}
    for a in new_anims:
        kinds[anim_node(a).form] = kinds.get(anim_node(a).form, 0) + 1
    N['added_by_top_node'] = dict(sorted(kinds.items()))
    new_tags = {n.tag for a in new_anims for _, n in iff.walk([a])}
    test('no PPTR (human bone masks) in the added entries', 'PPTR' not in new_tags, sorted(new_tags))

    # 4. every .ans exists, is a Hutt animation that fits hutt.skt, and which archive wins
    all_ans = sorted({p for a in o_anims for p in ans_paths(a)})
    stock_ans = {p for a in s_anims for p in ans_paths(a)}
    added_ans = {p for a in new_anims for p in ans_paths(a)}
    bones = skeleton_bones()
    wins, ties, missing, bad_prefix, bad_form, off_skeleton = {}, [], [], [], [], {}
    for p in all_ans:
        h = holders(p)
        if not h:
            missing.append(p)
            continue
        wins[p] = h[0]
        top = [x for x in h if x[0] == h[0][0]]
        if len(top) > 1:
            ties.append((p, [n for _, n in top]))
        if not os.path.basename(p).startswith('hutt_'):
            bad_prefix.append(p)
        form, used = ans_bones(iff.open_tre_entry(archive_path(h[0][1]), p))
        if form not in ('CKAT', 'KFAT'):
            bad_form.append((p, form))
        if used - bones:
            off_skeleton[p] = sorted(used - bones)
    by_arch = {}
    for p, (pri, name) in wins.items():
        by_arch[f'{name} (priority {pri})'] = by_arch.get(f'{name} (priority {pri})', 0) + 1
    test('every referenced .ans exists in the loaded client archives', not missing, missing)
    test('every .ans is a hutt_* file', not bad_prefix, bad_prefix)
    test('no .ans is held at the same top priority by two archives', not ties, ties)
    test('every .ans is a CKAT/KFAT animation', not bad_form, bad_form)
    test('every .ans animates only bones that hutt.skt has', not off_skeleton, off_skeleton)
    client_hutt = sorted({n for _, arch in loaded_archives() if os.path.exists(archive_path(arch))
                          for n in iff.list_tre(archive_path(arch)) if n.startswith(ANS_DIR + 'hutt_') and n.endswith('.ans')})
    N['hutt_ans_in_client'] = len(client_hutt)
    N['ans_distinct_in_new_table'] = len(all_ans)
    N['ans_distinct_in_stock_table'] = len(stock_ans)
    N['ans_distinct_in_added_entries'] = len(added_ans)
    N['ans_new_to_the_table'] = sorted(added_ans - stock_ans)
    N['ans_winning_archive'] = dict(sorted(by_arch.items()))
    N['hutt_ans_unreferenced_after'] = [n for n in client_hutt if n not in set(all_ans)]

    # 5. the AGAT gestures are real ash actions that lead to table entries
    gest_bad, gest_all = [], {}
    for a in o_anims:
        for _, n in iff.walk([a]):
            if n.is_form and n.form == 'AGAT':
                for g, w in agat_gestures(n)[2]:
                    targets = ash['actions'].get(g)
                    gest_all[g] = targets
                    if not targets or any(t not in out_set for t in targets) or w <= 0:
                        gest_bad.append((anim_name(a), g, targets, w))
    test('every AGAT gesture is an ash action whose animation is in the table', not gest_bad, gest_bad)
    N['agat_gestures'] = dict(sorted(gest_all.items()))
    N['dance_gestures_from_map'] = log['gestures']

    # 6. what the ash can still ask for that the table lacks
    wanted = ash_names(ash)
    loops = {s['loop'] for s in walk_states(ash)} - {'default'}
    N['ash_state_loops'] = len(loops)
    N['ash_state_loops_missing_before'] = sorted(loops - stock_set)
    test('every state loop animation the ash can enter is in the table (nothing freezes in a posture)', not (loops - out_set), sorted(loops - out_set))
    miss_after = sorted(wanted - out_set)
    N['ash_names'] = len(wanted)
    N['ash_names_missing_before'] = len(wanted - stock_set)
    N['ash_names_missing_after'] = len(miss_after)
    N['ash_names_missing_after_list'] = miss_after

    # 7. the writers reproduce real entries byte for byte
    ok = tot = 0
    for a in s_anims:
        n = anim_node(a)
        if n.form == 'PXAT' and [c.tag for c in n.children[0].children] == ['INFO', 'PUNF']:
            tot += 1
            ok += iff.build([pxat(ans_paths(n)[0], punf_category(n))]) == iff.build([n])
    test('pxat() reproduces the stock PXAT entries', tot > 0 and ok == tot, f'{ok}/{tot}')
    loop_standing = anim_node({anim_name(a): a for a in s_anims}['loop_standing'])
    ag = next(n for _, n in iff.walk([loop_standing]) if n.is_form and n.form == 'AGAT')
    lo, hi, gl, loop_child = agat_gestures(ag)
    weights = {w for _, w in gl}
    test('agat() reproduces a stock AGAT block', len(weights) == 1 and iff.build([agat(lo, hi, [g for g, _ in gl], loop_child, weights.pop())]) == iff.build([ag]),
         f'{[g for g, _ in gl]} every {lo}-{hi} s')
    h_anims = read_lat(iff.load(HUMAN_SPECS[0]))[2]
    h_by = {anim_name(a): a for a in h_anims}
    tsc = next((a for a in h_anims if anim_node(a).form == 'TSCL' and anim_node(a).children[0].children[1].form == 'PXAT'), None)
    ok_tscl = False
    if tsc is not None:
        t0 = anim_node(tsc).children[0]
        px = t0.children[1]
        ok_tscl = iff.build([tscl(struct.unpack('<f', t0.children[0].data)[0], pxat(ans_paths(px)[0], punf_category(px)))]) == iff.build([anim_node(tsc)])
    test('tscl() reproduces a human TSCL entry', ok_tscl, anim_name(tsc) if tsc is not None else None)
    kids = anim_node(h_by['loop_crouched']).children[0].children
    test('spat() reproduces the human loop_crouched',
         iff.build([spat([pxat(ans_paths(kids[1])[0], 'transition'), pxat(ans_paths(kids[2])[0], 'locomotion')])]) == iff.build([anim_node(h_by['loop_crouched'])]))

    N['entries'] = len(o_anims)
    N['output_bytes'], N['output_sha256'] = len(out), sha256(out)
    N['stock_bytes'], N['stock_sha256'] = len(stock), sha256(stock)
    R['pass'] = all(t['pass'] for t in R['tests'].values())
    return R


def print_report(R):
    for name, t in R['tests'].items():
        d = t.get('detail')
        print(('PASS  ' if t['pass'] else 'FAIL  ') + name + ('' if d is None or t['pass'] else '  -> ' + json.dumps(d)[:400]))
    n = R['numbers']
    print(f"entries {n['entries']}  bytes {n['output_bytes']}  sha256 {n['output_sha256']}")
    print(f"stock   {n['stock_bytes']} bytes  sha256 {n['stock_sha256']}")
    print('added by top node:', n['added_by_top_node'])
    print(f"human names {n['human_distinct']}: in stock Hutt {n['human_names_in_stock_hutt']}, in new Hutt {n['human_names_in_new_hutt']}, absent by rule {n['absent_by_skip_rule']}")
    print(f".ans: {n['ans_distinct_in_new_table']} distinct in the table ({len(n['ans_new_to_the_table'])} new to it); winners {n['ans_winning_archive']}")
    print(f"ash state loops {n['ash_state_loops']}: missing before {len(n['ash_state_loops_missing_before'])}; the 'every state loop' test above covers the after")
    print(f"ash names {n['ash_names']}: missing before {n['ash_names_missing_before']}, after {n['ash_names_missing_after']}")
    print('RESULT:', 'PASS' if R['pass'] else 'FAIL')


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--check', action='store_true', help='only re-check the staged file')
    ap.add_argument('--stock', help='stock hutt.lat on disk (default: the winning copy in the client archives)')
    ap.add_argument('--out', default=OUT_LAT)
    ap.add_argument('--report', default=OUT_REPORT)
    args = ap.parse_args(argv)

    with open(MAP_JSON, encoding='utf-8') as f:
        mapping = json.load(f)
    if args.stock:
        with open(args.stock, 'rb') as f:
            stock, src_name, src_pri = f.read(), os.path.basename(args.stock), None
    else:
        stock, src_name, src_pri = read_stock()
    assert iff.build(iff.parse(stock)) == stock, 'the stock file does not round-trip'
    print(f'stock hutt.lat: {len(stock)} bytes from {src_name}' + (f' (priority {src_pri})' if src_pri is not None else '') + f', sha256 {sha256(stock)[:16]}...')
    ash = load_ash()

    if args.check:
        with open(args.out, 'rb') as f:
            out = f.read()
        loop_skill = next(e for e in mapping['entries'] if e['action'] == 'loop_skill')
        log = {'gestures': {g: gesture_action(ash, g) for g in loop_skill['gestures']}}
    else:
        out, log = build(stock, mapping, ash)
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, 'wb') as f:
            f.write(out)
        with open(args.out, 'rb') as f:
            assert f.read() == out
        print('wrote', os.path.relpath(args.out, OUTPUTS))
    R = check(out, stock, mapping, ash, log)
    R['stock_source'] = {'archive': src_name, 'priority': src_pri}
    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    with open(args.report, 'w', encoding='utf-8') as f:
        json.dump(R, f, indent=1, sort_keys=True)
    print_report(R)
    return 0 if R['pass'] else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
