"""Which Core3-dev object Lua files are reachable through includeFile() from the two roots the server loads:
object/main.lua (allobjects.lua = shared templates, serverobjects.lua = server templates). Uses the edge dump
work/core3_include_edges.tsv (file<TAB>include target, both relative to bin/scripts/object) and the file list
work/core3_lua_files.txt. Optionally takes extra edges/files from a staged tree so a staged batch can be
checked the same way.

Run: python -I tools/include_reach.py [--staged DIR]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(HERE, '..', 'work')


def load(staged=None):
    edges = {}
    files = set()
    with open(os.path.join(W, 'core3_include_edges.tsv'), encoding='utf-8') as f:
        for line in f:
            parts = line.rstrip('\n').split('\t')
            if len(parts) == 2:
                edges.setdefault(parts[0], []).append(parts[1])
    with open(os.path.join(W, 'core3_lua_files.txt'), encoding='utf-8') as f:
        files = {line.strip() for line in f if line.strip()}
    import re
    for staged_dir in ([staged] if isinstance(staged, str) else (staged or [])):
        base = os.path.join(staged_dir, 'MMOCoreORB', 'bin', 'scripts', 'object')
        for root, dirs, names in os.walk(base):
            for n in names:
                if not n.endswith('.lua'):
                    continue
                p = os.path.join(root, n)
                rel = os.path.relpath(p, base).replace(os.sep, '/')
                files.add(rel)
                with open(p, encoding='latin-1') as f:
                    text = f.read()
                # a staged copy replaces the old edges; later trees override earlier ones; comments ignored
                edges[rel] = [m.group(1) for m in re.finditer(r'^[ \t]*includeFile\("([^"]+)"\)', text, re.M)]
    return edges, files


def reach(edges, files, root):
    seen, todo, missing = set(), [root], []
    while todo:
        f = todo.pop()
        if f in seen:
            continue
        seen.add(f)
        if f not in files:
            missing.append(f)
            continue
        todo.extend(edges.get(f, []))
    return seen, missing


def main(argv):
    staged = argv[argv.index('--staged') + 1] if '--staged' in argv else None
    edges, files = load(staged)
    reach_all, miss_all = reach(edges, files, 'main.lua')
    print(f'files {len(files)}, reachable from main.lua {len(reach_all)}, includes of missing files {len(miss_all)}')
    for m in miss_all[:40]:
        print('   missing:', m)
    unreached = sorted(f for f in files if f not in reach_all and f.split('/')[-1] in ('objects.lua', 'serverobjects.lua'))
    print(f'objects.lua/serverobjects.lua files not reached: {len(unreached)}')
    for u in unreached[:40]:
        print('   unreached:', u)
    return reach_all, miss_all, unreached


if __name__ == '__main__':
    main(sys.argv[1:])
