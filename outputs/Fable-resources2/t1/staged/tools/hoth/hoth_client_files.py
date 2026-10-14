"""Hoth step 2: the client files that list planets: extract the stock copies and prove we can rewrite them exactly.

    python -I tools/hoth/hoth_client_files.py extract     winning stock copies -> Documentation-support/hoth/client-base/
    python -I tools/hoth/hoth_client_files.py roundtrip   read + write each copy back with Bellum's format tools; the
                                                          bytes must match before we change anything (UM's
                                                          reverse-engineering rule: reader -> writer -> reader)

Format tools are ours (outputs/tools/swgfmt).
"""
import filecmp, os, sys, tempfile

H = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
CLIENT = os.path.join(H, 'outputs', 'SWG-client')
BASE = os.path.join(H, 'outputs', 'Documentation-support', 'hoth', 'client-base')
sys.path.insert(0, os.path.join(H, 'outputs', 'tools'))
from swgfmt.fmt_tools import read_tre, walk_tres, extract_entry, stf_tool, dt_tool, cstb_tool  # noqa: E402  (ours)

FILES = {  # internal path -> format
    'string/en/planet_n.stf': 'stf',
    'datatables/travel/travel.iff': 'datatable',
    'datatables/player/waypoint_planets.iff': 'datatable',
    'misc/planet_crc_string_table.iff': 'crc table',
    'ui/ui_ticketpurchase.inc': 'ui text',
    'ui/ui_planet_map.inc': 'ui text',
}


def local(path):
    return os.path.join(BASE, *path.split('/'))


def extract():
    winners = {}
    for tre in walk_tres(CLIENT):
        try:
            for entry in read_tre(tre):
                winners[entry['name'].lower()] = (tre, entry)
        except Exception:
            pass
    for path in FILES:
        tre, entry = winners[path]
        out = extract_entry(tre, entry, BASE)
        print(f'{path}  from {os.path.basename(tre)}  {entry["size"]} bytes -> {os.path.relpath(out, H)}')


def roundtrip():
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        for path, kind in FILES.items():
            src, out = local(path), os.path.join(tmp, os.path.basename(path))
            if kind == 'stf':
                stf_tool.write(stf_tool.read(src), out)
            elif kind == 'datatable':
                dt_tool.write(dt_tool.read(src), out)
            elif kind == 'crc table':
                cstb_tool.write(cstb_tool.read(src), out)
            else:
                text = open(src, 'rb').read().decode('latin-1')
                open(out, 'wb').write(text.encode('latin-1'))
            same = filecmp.cmp(src, out, shallow=False)
            ok &= same
            print(f'{"SAME" if same else "DIFFERENT"}  {path} ({kind}, {os.path.getsize(src)} -> {os.path.getsize(out)} bytes)')
    print('all round trips exact' if ok else 'NOT all exact: fix the writer before editing that file')
    return 0 if ok else 1


if __name__ == '__main__':
    command = sys.argv[1] if len(sys.argv) > 1 else ''
    if command == 'extract':
        extract()
    elif command == 'roundtrip':
        sys.exit(roundtrip())
    else:
        print(__doc__)
