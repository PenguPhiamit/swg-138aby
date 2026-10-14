"""Which archives the real client loads, and which archive each file comes from. Read-only.

    python -I tools/hoth/client_load_order.py [--login FILE] [path ...]

Reads the client's config chain the way the client does: swgemu.cfg and its .include lines, with [Section]
headers. Only searchTree_XX_NN lines inside [SharedFile] count, below maxSearchPriority; a higher NN wins.
--login replaces swgemu_login.cfg (for example with what `Play SWG Test Galaxy.cmd` writes for a session).
Prints the archives in load order, then the winning archive for each path (default: the files Hoth needs).

Why it exists (14 Oct 2026): Bellum's cfg_priorities() and our hoth_closure.py counted every searchTree line in
any .cfg file. The MTG lines in swgemu_live.cfg sit under [Station], so the client never loaded them, and Hoth
crashed the client ("terrain/hoth.trn is not a valid terrain file") although the closure said the file was there.
"""
import os, re, sys

H = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
CLIENT = os.path.join(H, 'outputs', 'SWG-client')
sys.path.insert(0, os.path.join(H, 'outputs', 'tools'))
from swgfmt.fmt_tools import read_tre, _inflate  # noqa: E402  (ours; was Bellum's tre_inventory)

HOTH = ['terrain/hoth.trn', 'snapshot/hoth.ws', 'texture/ui_map_hoth.dds', 'appearance/ui_planet_sel_hoth.apt',
        'string/en/planet_n.stf', 'misc/planet_crc_string_table.iff', 'datatables/travel/travel.iff',
        'datatables/player/waypoint_planets.iff', 'ui/ui_ticketpurchase.inc', 'ui/ui_planet_map.inc']


def read_cfg(name, login, out, section=None):
    """Append (section, key, value) for every line of name and its includes, in reading order."""
    path = login if (login and name.lower() == 'swgemu_login.cfg') else os.path.join(CLIENT, name)
    if not os.path.exists(path):
        print(f'# {name}: not found')
        return section
    for raw in open(path, encoding='latin-1'):
        line = raw.split(';', 1)[0].strip()
        if not line or line.startswith('#'):
            continue
        include = re.match(r'\.include\s+"([^"]+)"', line)
        if include:
            read_cfg(include[1], login, out)  # an included file starts with no section of its own
        elif line.startswith('[') and line.endswith(']'):
            section = line[1:-1].strip()
        elif '=' in line:
            key, value = (s.strip() for s in line.split('=', 1))
            out.append((section, key, value))
    return section


def load_order(login=None):
    lines = []
    read_cfg('swgemu.cfg', login, lines)
    shared = [(k, v) for s, k, v in lines if s == 'SharedFile']
    top = max([int(v) for k, v in shared if k.lower() == 'maxsearchpriority'] or [0])
    trees, ignored = [], [(s, k, v) for s, k, v in lines if k.lower().startswith('searchtree') and s != 'SharedFile']
    for k, v in shared:
        m = re.match(r'searchTree_(\d+)_(\d+)$', k, re.I)
        if not m:
            continue
        if int(m[2]) < top:  # stock had maximum 26 and used 25 at most, so the maximum itself is taken as excluded
            trees.append((int(m[2]), v))
        else:
            ignored.append(('SharedFile', k, v))
    return sorted(trees, key=lambda t: -t[0]), ignored, top


def main(argv):
    login = None
    if argv[:1] == ['--login']:
        login, argv = argv[1], argv[2:]
    trees, ignored, top = load_order(login)
    print(f'maxSearchPriority {top}; {len(trees)} archives loaded (highest priority first):')
    for priority, name in trees:
        print(f'  {priority:3d} {name}' + ('' if os.path.exists(os.path.join(CLIENT, name)) else '   (FILE MISSING)'))
    if ignored:
        print(f'{len(ignored)} searchTree lines the client ignores (outside [SharedFile], or at/above the maximum):')
        for s, k, v in ignored[:30]:
            print(f'  [{s}] {k}={v}')
    winner = {}
    for priority, name in reversed(trees):  # lowest first, so higher priorities overwrite
        path = os.path.join(CLIENT, name)
        if os.path.exists(path):
            for entry in read_tre(path):
                winner[entry['name'].lower()] = f'{name} ({priority})'
    print('files:')
    for want in argv or HOTH:
        print(f'  {want}: {winner.get(want.lower(), "NOT LOADED")}')
    return 0 if all(w.lower() in winner for w in argv or HOTH) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
