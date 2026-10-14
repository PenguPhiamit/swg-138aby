"""Offline verification of a staged backport batch. Writes checks.json and checks-summary.md (batch 1) or
checks-batch2.json / checks-batch2-summary.md. Read-only everywhere else.

Per object: the client shared .iff exists and which archive wins; the IFF form tag matches the template class
used; the shared path is in the merged CRC table the test client loads (Local-content/local_planets/misc/...) and
whether it is in the stock table too; no server-path or Lua-name collision with Core3-dev; the client name string
resolves. Per file: every includeFile() target exists (staged or in Core3-dev) and every staged objects.lua /
serverobjects.lua is reached from object/main.lua; luac5.3 -p results come from work/luac_<batch>.txt, produced
inside WSL by tools/luac_staged.sh.

Run: python -I tools/verify_batch.py [--batch 2]
"""
import json, os, re, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
OUTPUTS = os.path.normpath(os.path.join(ROOT, '..'))
W = os.path.join(ROOT, 'work')
sys.path.insert(0, HERE)
import swg_iff  # noqa: E402
from swg_iff import scd  # noqa: E402
import include_reach  # noqa: E402
from dormant_analysis import crc_table  # noqa: E402

MERGED = os.path.join(OUTPUTS, 'Local-content', 'local_planets', 'misc', 'object_template_crc_string_table.iff')


def main(argv):
    batch = argv[argv.index('--batch') + 1] if '--batch' in argv else '1'
    staged_dir = os.path.join(ROOT, 'staged' if batch == '1' else f'staged-batch{batch}')
    objs_file = os.path.join(W, f'batch{batch}_objects.json')
    luac_file = os.path.join(W, f'luac_batch{batch}.txt')
    out_json = os.path.join(ROOT, 'checks.json' if batch == '1' else f'checks-batch{batch}.json')
    out_md = os.path.join(ROOT, 'checks-summary.md' if batch == '1' else f'checks-batch{batch}-summary.md')

    data = json.load(open(objs_file, encoding='utf-8'))
    objects, manifest = data['objects'], data['manifest']
    scd._build_index()
    merged = crc_table(open(MERGED, 'rb').read())
    stock = set(l.strip() for l in open(os.path.join(W, 'crc_table_winner.txt'), encoding='utf-8'))
    server_reg, client_reg = {}, {}
    for line in open(os.path.join(W, 'core3_server_templates_files.tsv'), encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        if len(p) == 3:
            server_reg.setdefault(p[2], []).append(p[0])
    for line in open(os.path.join(W, 'core3_client_templates_files.tsv'), encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        if len(p) == 3:
            client_reg.setdefault(p[2], []).append(p[0])
    names = set(l.strip() for l in open(os.path.join(W, 'core3_names.txt'), encoding='utf-8'))
    core3_files = set(l.strip() for l in open(os.path.join(W, 'core3_lua_files.txt'), encoding='utf-8'))
    stf = {}

    def name_of(sid):
        if not sid:
            return None
        tbl, key = sid
        if tbl not in stf:
            d = scd.client_file(f'string/en/{tbl}.stf')
            stf[tbl] = scd.string_file(d) if d else None
        return (stf[tbl] or {}).get(key) if stf[tbl] is not None else None

    # staged file contents, for the registration and name checks
    staged_text = {}
    base = os.path.join(staged_dir, 'MMOCoreORB', 'bin', 'scripts', 'object')
    for root, dirs, files in os.walk(base):
        for fn in files:
            if fn.endswith('.lua'):
                p = os.path.join(root, fn)
                staged_text[os.path.relpath(p, base).replace(os.sep, '/')] = open(p, encoding='latin-1').read()

    results, problems = [], []
    for o in objects:
        shared, server = o['shared'], o['server']
        win = scd._index.get(shared.lower())
        info = swg_iff.resolved(shared) if win else None
        r = {'batch': o['batch'], 'kind': o['kind'], 'server': server, 'shared': shared,
             'client_file': bool(win), 'winning_archive': os.path.basename(win[0]) if win else None,
             'form': info['form'] if info else None,
             'template_class': swg_iff.TYPE_NAMES.get(info['form']) if info else None,
             'gameObjectType': hex(info['gameObjectType']) if info and info['gameObjectType'] is not None else None,
             'in_merged_crc_table': shared in merged, 'in_stock_crc_table': shared in stock,
             'client_name': name_of(info['objectName']) if info else None,
             'objectName': info['objectName'] if info else None}
        # registrations: the staged files must register exactly this server path once, and Core3-dev must not
        # register it elsewhere ('wired' objects keep their existing Core3-dev file, which must be the only one)
        # files that register this server path after the batch: staged copies win over Core3-dev copies
        reg_files = set()
        for f, t in staged_text.items():
            if any(m == server for m in re.findall(r'addTemplate\([A-Za-z0-9_]+, *"([^"]+)"\)', t)):
                reg_files.add(f)
        for f in server_reg.get(server, []):
            if f not in staged_text:
                reg_files.add(f)
        expected = set(o['files']) if o['kind'] in ('repair', 'new', 'wired') else None
        r['registered_in'] = sorted(reg_files)
        r['staged_registration_count'] = len(reg_files)
        others = sorted(f for f in reg_files if expected is not None and f not in expected)
        r['server_path_registered_elsewhere'] = others
        # client (shared) registration after the batch
        creg = set()
        for f, t in staged_text.items():
            if any(m == shared for m in re.findall(r'addClientTemplate\([A-Za-z0-9_]+, *"([^"]+)"\)', t)):
                creg.add(f)
        for f in client_reg.get(shared, []):
            if f not in staged_text:
                creg.add(f)
        r['shared_template_registered'] = sorted(creg)
        # the Lua class used for the shared template must match the IFF form
        cls = None
        for f in creg:
            t = staged_text.get(f)
            if t is None:
                continue
            m = re.search(r'=\s*(Shared[A-Za-z]+Template):new', t[t.find(shared) - 400 if t.find(shared) > 400 else 0:t.find(shared) + 1])
            cls = m.group(1) if m else cls
        r['shared_template_class_staged'] = cls
        form_ok = r['form'] in swg_iff.TYPE_NAMES and (cls is None or cls == swg_iff.TYPE_NAMES.get(r['form']))
        if o['kind'] == 'new':
            r['shared_registered_elsewhere'] = client_reg.get(shared, [])
            r['name_collision'] = [n for n in (o['var'], o['shared_var']) if n in names]
            r['new_file_exists_in_core3'] = [f for f in o['files'][:1] if f in core3_files]  # the server file; folder files may be extended
            if info:
                app = info['appearanceFilename']
                r['appearance'] = app
                r['appearance_in_client'] = bool(app) and app.lower() in scd._index
                if app and app.endswith('.sat'):
                    stem = re.sub(r'_[fm]\.sat$', '', app)
                    r['appearance_variants'] = sorted(k for k in scd._index if k.startswith(stem.lower() + '_') and k.endswith('.sat'))
        else:
            r['was'] = o.get('was')
        ok = (r['client_file'] and form_ok and r['in_merged_crc_table'] and r['staged_registration_count'] == 1
              and not others and not r.get('name_collision') and not r.get('new_file_exists_in_core3')
              and len(r['shared_template_registered']) == 1)
        r['ok'] = bool(ok)
        if not ok:
            problems.append(r)
        results.append(r)

    # include chain over Core3-dev plus every staged tree up to this batch (batch 2 builds on batch 1)
    trees = [os.path.join(ROOT, 'staged')] + ([staged_dir] if batch != '1' else [])
    edges, files = include_reach.load(trees)
    reach_all, missing = include_reach.reach(edges, files, 'main.lua')
    staged_rel = set(staged_text)
    unreached = sorted(f for f in staged_rel if f not in reach_all)
    include_targets = {t for f in staged_rel for t in edges.get(f, [])}
    missing_targets = sorted(t for t in include_targets if t not in files)
    # separate what the batch introduced from what Core3-dev already had (the same include in the original file)
    orig_edges, _ = include_reach.load(None)
    preexisting = sorted(t for t in missing_targets if any(t in orig_edges.get(f, []) for f in staged_rel))
    missing_targets = [t for t in missing_targets if t not in preexisting]

    # luac
    luac = {'ran': False}
    if os.path.exists(luac_file):
        txt = open(luac_file, encoding='utf-8', errors='replace').read()
        m = re.search(r'checked (\d+) files, (\d+) failed', txt)
        luac = {'ran': True, 'checked': int(m.group(1)) if m else None, 'failed': int(m.group(2)) if m else None,
                'report': luac_file, 'errors': [l for l in txt.splitlines() if ':' in l and 'luac' in l.lower()][:20]}

    summary = {
        'batch': batch, 'objects': len(results), 'ok': sum(1 for r in results if r['ok']), 'problems': len(problems),
        'files_staged': len(manifest), 'files_changed': sum(1 for _, h in manifest if h != 'new'), 'files_new': sum(1 for _, h in manifest if h == 'new'),
        'client_file_missing': [r['server'] for r in results if not r['client_file']],
        'not_in_merged_crc_table': [r['shared'] for r in results if not r['in_merged_crc_table']],
        'in_stock_crc_table': sum(1 for r in results if r['in_stock_crc_table']),
        'forms': {}, 'winning_archives': {},
        'client_name_missing': [r['server'] for r in results if r['client_name'] is None],
        'include_targets_missing': missing_targets, 'include_targets_missing_preexisting_in_core3': preexisting,
        'staged_files_unreached_from_main': unreached,
        'includes_of_missing_files_whole_tree': missing, 'luac': luac,
        'catalogue': data.get('catalogue'),
    }
    for r in results:
        summary['forms'][str(r['form'])] = summary['forms'].get(str(r['form']), 0) + 1
        summary['winning_archives'][str(r['winning_archive'])] = summary['winning_archives'].get(str(r['winning_archive']), 0) + 1
    with open(out_json, 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'summary': summary, 'objects': results}, f, indent=1)

    lines = [f'# Batch {batch} verification (offline)', '',
             f'- objects: {summary["objects"]}; all checks passed: {summary["ok"]}; with a problem: {summary["problems"]}',
             f'- files staged: {summary["files_staged"]} ({summary["files_changed"]} changed, {summary["files_new"]} new)',
             f'- client shared .iff present: {summary["objects"] - len(summary["client_file_missing"])} of {summary["objects"]}; winning archives: {summary["winning_archives"]}',
             f'- IFF form tags: {summary["forms"]} (STOT = SharedTangibleObjectTemplate, the class every staged object uses)',
             f'- in the merged CRC table (Local-content/local_planets): {summary["objects"] - len(summary["not_in_merged_crc_table"])} of {summary["objects"]}; in the stock table: {summary["in_stock_crc_table"]}',
             f'- server path or Lua name collisions with Core3-dev: {sum(1 for r in results if r["server_path_registered_elsewhere"] or r.get("name_collision") or r.get("new_file_exists_in_core3"))}',
             f'- client name string resolves: {summary["objects"] - len(summary["client_name_missing"])} of {summary["objects"]} (missing listed in checks.json: client_name_missing)',
             f'- includeFile targets missing because of this batch: {len(missing_targets)} (already missing in Core3-dev before the batch: {len(preexisting)}: {", ".join(preexisting) or "-"}); staged files not reached from object/main.lua: {len(unreached)}',
             f'- luac5.3 -p: ' + (f'{luac["checked"]} files checked, {luac["failed"]} failed' if luac['ran'] else 'not run'),
             '']
    if problems:
        lines.append('## Objects with a problem')
        for r in problems[:60]:
            lines.append(f'- {r["server"]}: client_file={r["client_file"]} form={r["form"]} class={r["shared_template_class_staged"]} merged_crc={r["in_merged_crc_table"]} server_regs={r["registered_in"]} client_regs={r["shared_template_registered"]}')
    if missing_targets or unreached:
        lines += ['## Include problems'] + [f'- missing target: {t}' for t in missing_targets] + [f'- unreached: {u}' for u in unreached]
    with open(out_md, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main(sys.argv[1:])
