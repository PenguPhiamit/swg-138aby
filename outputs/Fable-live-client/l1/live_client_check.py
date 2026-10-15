"""live_client_check.py: would local_planets.tre win for each of its entries in a client folder? Read-only (Fable L1, 14 Oct 2026).

    python -I live_client_check.py <client folder> [--login FILE] [--archives DIR] [--archive NAME] [--json]

Reads the cfg chain the way the client does (client_load_order.load_order: swgemu.cfg, its .include files, [SharedFile]
sections only, priorities below maxSearchPriority), lists every loaded archive, then for each entry of the archive (default
local_planets.tre) names the loaded archive of the highest priority that holds the same path: WINS when it is ours.
Also shown: searchTree lines the client ignores (outside [SharedFile] or at/above the maximum), the same archive listed
twice, the Bellum-style view (`cfg_priorities`: every searchTree line in every *.cfg, any section) where it disagrees, and
whether the 23 MTG archives Hoth's terrain needs are loaded. --archives DIR takes the .tre files from DIR when the cfgs
are a copy (a staged set) without them.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))
sys.path.insert(0, os.path.join(OUTPUTS, 'tools', 'hoth'))
from swgfmt.fmt_tools import read_tre, cfg_priorities  # noqa: E402
import client_load_order as clo  # noqa: E402

MTG_NEEDED = ['mtg_planets.tre', 'mtg_patch_022.tre', 'mtg_patch_019.tre', 'mtg_patch_016.tre']   # terrain/snapshot/map/model, heroic buildings, Echo Base art


def check(client, login=None, archives=None, archive='local_planets.tre'):
    archives = archives or client
    clo.CLIENT = client                                   # client_load_order reads its cfgs from this folder
    trees, ignored, top = clo.load_order(login)
    loaded = []                                           # (priority, name, path) highest first
    missing = []
    for priority, name in trees:
        path = os.path.join(archives, os.path.basename(name))
        (loaded if os.path.exists(path) else missing).append((priority, name, path))
    counts = {}
    for _, name, _ in loaded:
        counts[name.lower()] = counts.get(name.lower(), 0) + 1
    duplicates = sorted(n for n, c in counts.items() if c > 1)
    ours_path = os.path.join(archives, archive)
    result = {'client': client, 'login': login, 'max_search_priority': top, 'archives_loaded': len(loaded), 'archives_missing_on_disk': [n for _, n, _ in missing],
              'ignored_lines': [f'[{s}] {k}={v}' for s, k, v in ignored], 'duplicates': duplicates, 'entries': {}, 'ours': archive}
    ours_loaded = [(p, n) for p, n, _ in loaded if n.lower() == archive.lower()]
    result['ours_loaded_at'] = [p for p, _ in ours_loaded]
    if not os.path.exists(ours_path):
        result['verdict'] = archive + ' is not in ' + archives
        return result
    index = {}                                            # path -> (priority, archive) of the winner among loaded archives
    for priority, name, path in sorted(loaded, key=lambda t: t[0]):   # lowest first, higher priorities overwrite
        for e in read_tre(path):
            index[e['name'].lower()] = (priority, name)
    wins = 0
    for e in read_tre(ours_path):
        winner = index.get(e['name'].lower())
        if winner is None:
            verdict = 'NOT LOADED (no loaded archive has it: ours is not in the search order)'
        elif winner[1].lower() == archive.lower():
            verdict = 'WINS'
            wins += 1
        else:
            verdict = 'LOSES to %s (%d)' % (winner[1], winner[0])
        result['entries'][e['name']] = verdict
    result['wins'] = wins
    result['total'] = len(result['entries'])
    result['mtg_loaded'] = {m: any(n.lower() == m for _, n, _ in loaded) for m in MTG_NEEDED}
    bellum_view = cfg_priorities(client)
    result['cfg_priorities_disagrees'] = sorted(n for n, p in bellum_view.items() if not any(n == x.lower() and p == pr for pr, x, _ in loaded))
    result['verdict'] = ('all %d entries win' % wins) if wins == len(result['entries']) and wins else ('%d of %d entries win' % (wins, len(result['entries'])))
    return result


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    client = argv[0]
    login = argv[argv.index('--login') + 1] if '--login' in argv else None
    archives = argv[argv.index('--archives') + 1] if '--archives' in argv else None
    archive = argv[argv.index('--archive') + 1] if '--archive' in argv else 'local_planets.tre'
    r = check(client, login, archives, archive)
    if '--json' in argv:
        print(json.dumps(r, indent=1))
    else:
        print('%s: maxSearchPriority %d, %d archives loaded, ours at %s; %s' % (client, r['max_search_priority'], r['archives_loaded'], r['ours_loaded_at'] or 'nowhere', r['verdict']))
        for k in ('archives_missing_on_disk', 'ignored_lines', 'duplicates', 'cfg_priorities_disagrees'):
            if r.get(k):
                print('  %s: %s' % (k, r[k][:12]))
        if 'mtg_loaded' in r:
            print('  MTG archives Hoth needs: ' + ', '.join('%s %s' % (m, 'yes' if v else 'NO') for m, v in r['mtg_loaded'].items()))
        for name, v in sorted(r['entries'].items()):
            print('  %-58s %s' % (name, v))
    return 0 if r.get('wins') == r.get('total') and r.get('total') else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
