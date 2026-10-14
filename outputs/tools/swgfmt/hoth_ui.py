"""hoth_ui.stage_hoth_ui(stage_dir, base): Hoth's ticket-purchase and planetary-map UI with our own cloner (Fable B1,
14 Oct 2026), reproducing what tools/hoth/hoth_client_build.py's ticket_ui() and planet_map_ui() add (its GALAXY_SPOT,
element names, the ui_map_hoth page, the code-data line) but byte-exact to the base outside the inserted blocks: no
blank lines at the stock files' bare carriage returns (Bellum's load() splits on '\\r' too).

    report = stage_hoth_ui(stage_dir, base, spot=GALAXY_SPOT)   # base(name) -> bytes of the stock copy (never one that has Hoth)
    python -I hoth_ui.py <stage_dir> [--diff DIR]   stage from the stock client-base copies; --diff compares with DIR's .inc files
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.normpath(os.path.join(HERE, '..', '..'))
from . import ui_inc  # noqa: E402

GALAXY_SPOT = (425, 225)          # hoth_client_build.GALAXY_SPOT: provisional, right of the map
TICKET, PLANET_MAP = 'ui/ui_ticketpurchase.inc', 'ui/ui_planet_map.inc'
STOCK_BASE = os.path.join(OUTPUTS, 'Documentation-support', 'hoth', 'client-base')
CR, LF, CRLF = '\r', '\n', '\r\n'


def stock_base(name):
    p = os.path.join(STOCK_BASE, name.replace('/', os.sep))
    with open(p, 'rb') as f:
        return f.read()


def stage_hoth_ui(stage_dir, base, spot=GALAXY_SPOT):
    ticket, pmap = base(TICKET), base(PLANET_MAP)
    for rel, raw in ((TICKET, ticket), (PLANET_MAP, pmap)):
        if raw.count(b'\r\n') != raw.count(b'\n'):
            raise AssertionError(rel + ': base is not CRLF throughout')
    t_out, p_out, rep = ui_inc.add_planet(ticket, pmap, 'Hoth', 'hoth', 'ui_planet_sel_hoth.apt', 'ui_map_hoth', spot, after=None)
    report = {'galaxy_spot': spot, 'ui': rep, 'files': {}}
    for rel, data, raw in ((TICKET, t_out, ticket), (PLANET_MAP, p_out, pmap)):
        path = os.path.join(stage_dir, rel.replace('/', os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data)
        report['files'][rel] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'base_bytes': len(raw),
                                'base_lines_kept': ui_inc.lines_kept(raw, data), 'crlf_only': data.count(b'\r\n') == data.count(b'\n'),
                                'bare_cr': (raw.count(b'\r\r\n'), data.count(b'\r\r\n'))}
    return report


def bellum_load(text):
    """What Bellum's merge_ticket_ui.load() does to a file: every CR LF and every lone CR becomes a line break."""
    return text.replace(CRLF, LF).replace(CR, LF).split(LF)


def explain_diff(ours, theirs, stock):
    """Line diff of our output against another build of the same file, each hunk classified."""
    import difflib
    a, b = ui_inc.split(ours), ui_inc.split(theirs)
    stock_lines = ui_inc.split(stock)
    bare = sum(l.count(CR) for l in stock_lines)          # bare carriage returns in the stock file
    hunks = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == 'equal':
            continue
        ours_lines, theirs_lines = a[i1:i2], b[j1:j2]
        kind = 'other'
        if bellum_load(CRLF.join(ours_lines)) == theirs_lines:   # Bellum's load() on our lines gives exactly theirs
            kind = 'bare CR: %d lone carriage return(s) in the stock lines; Bellum load() turned each into a line break, so an extra blank line' % sum(l.count(CR) for l in ours_lines)
        hunks.append({'op': tag, 'ours': (i1, i2), 'theirs': (j1, j2), 'ours_lines': ours_lines[:3], 'theirs_lines': theirs_lines[:3], 'kind': kind})
    return {'hunks': hunks, 'bare_cr_in_stock': bare, 'only_bare_cr': all(h['kind'].startswith('bare CR') for h in hunks)}


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    rep = stage_hoth_ui(argv[0], stock_base)
    if '--diff' in argv:
        other = argv[argv.index('--diff') + 1]
        rep['diff'] = {}
        for rel in (TICKET, PLANET_MAP):
            ours = open(os.path.join(argv[0], rel.replace('/', os.sep)), 'rb').read()
            theirs = open(os.path.join(other, rel.replace('/', os.sep)), 'rb').read()
            rep['diff'][rel] = explain_diff(ours, theirs, stock_base(rel))
    print(json.dumps(rep, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
