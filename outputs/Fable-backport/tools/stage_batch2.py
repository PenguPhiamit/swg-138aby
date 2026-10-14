"""Stage backport batch 2 for Core3-dev (writes only under Fable-backport/). Builds on batch 1: the allobjects.lua
diff is against batch 1's staged copy, so batch 1 is applied first.

Batch 2a, wiring: four Mod the Galaxy serverobjects.lua files that Core3-dev imported but never includes, so
their server templates never load. Each gets one includeFile() line in its parent:
  custom_content/tangible/holiday/empire_day/component/serverobjects.lua   32 Empire Day crafting components
  custom_content/building/player/construction/serverobjects.lua            10 construction markers (TCG houses)
  custom_content/tangible/content/eow/serverobjects.lua                      2 Empire of Wookiees data disks
  custom_content/static/base/serverobjects.lua (+ its objects.lua)           1 flagpole base
Left alone on purpose: custom_content/draft_schematic/vehicle/serverobjects.lua (11 vehicle schematics) is part
of the Hoth vehicle chain Claude is porting.

Batch 2b, new templates (client file present, no registration anywhere):
  8 Tatooine wall statics  object/static/structure/tatooine/wall_tatooine_large_style_{100,200,500,1000,2000,2500,4200,8000}
  1 Mustafar static        object/static/creature/som_droid_mining_facility
  1 furniture              object/tangible/furniture/space/frn_chair_y8_passenger_s01 (SOE original: also on the owner's disc)
Outputs: staged-batch2/, diffs-batch2/, batch2.diff, apply-manifest-batch2.tsv, work/batch2_objects.json.

Run: python -I tools/stage_batch2.py   (after tools/stage_batch1.py)
"""
import difflib, hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
W = os.path.join(ROOT, 'work')
ORIG = os.path.join(W, 'core3_orig')
STAGED1 = os.path.join(ROOT, 'staged', 'MMOCoreORB', 'bin', 'scripts', 'object')
STAGED = os.path.join(ROOT, 'staged-batch2', 'MMOCoreORB', 'bin', 'scripts', 'object')
DIFFS = os.path.join(ROOT, 'diffs-batch2')
sys.path.insert(0, HERE)
import swg_iff  # noqa: E402
from swg_iff import scd  # noqa: E402

SEP = b'--**********************************************************************************************************************************'
WALLS = ['100', '200', '500', '1000', '2000', '2500', '4200', '8000']


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read(rel, from_batch1=False):
    p = os.path.join(STAGED1 if from_batch1 else ORIG, rel)
    with open(p, 'rb') as f:
        return f.read()


def write_staged(rel, data):
    p = os.path.join(STAGED, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'wb') as f:
        f.write(data)


def write_diff(rel, old, new, combined):
    a = old.decode('latin-1').splitlines(keepends=True) if old is not None else []
    b = new.decode('latin-1').splitlines(keepends=True)
    text = ''.join(difflib.unified_diff(a, b, fromfile=('a/' + rel) if old is not None else '/dev/null', tofile='b/' + rel))
    if text and not text.endswith('\n'):
        text += '\n'
    p = os.path.join(DIFFS, rel + '.diff')
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'wb') as f:
        f.write(text.encode('latin-1'))
    combined.append(text)


def nl_of(data):
    return b'\r\n' if b'\r\n' in data else b'\n'


def insert_line(data, anchor, new_line, before):
    nl = nl_of(data)
    lines = data.split(nl)
    idx = [i for i, l in enumerate(lines) if l.strip() == anchor.encode('ascii')]
    assert len(idx) == 1, (anchor, idx)
    assert not any(l.strip() == new_line.encode('ascii') for l in lines), (new_line, 'already present')
    lines.insert(idx[0] if before else idx[0] + 1, new_line.encode('ascii'))
    return nl.join(lines)


def append_lines(data, new_lines, separator=None):
    """Append lines in the file's own line ending; add a line break first if the file does not end with one."""
    nl = nl_of(data)
    out = data if data.endswith(nl) or not data else data + nl
    for block in new_lines:
        out += nl.join(l.encode('ascii') for l in block) + nl
        if separator is not None:
            out += separator + nl
    return out


def main():
    scd._build_index()
    manifest, objects, combined = [], [], []
    server_by_file = {}
    for line in open(os.path.join(W, 'core3_server_templates_files.tsv'), encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        if len(p) == 3:
            server_by_file.setdefault(p[0], []).append(p[2])
    edges = {}
    for line in open(os.path.join(W, 'core3_include_edges.tsv'), encoding='utf-8'):
        p = line.rstrip('\n').split('\t')
        if len(p) == 2:
            edges.setdefault(p[0], []).append(p[1])

    def change(rel, new, old, note):
        write_staged(rel, new)
        write_diff(rel, old, new, combined)
        manifest.append((rel, sha256(old)))

    def wired_objects(serverobjects_rel, note):
        out = []
        for f in edges.get(serverobjects_rel, []):
            for sp in server_by_file.get(f, []):
                h, t = sp.rsplit('/', 1)
                out.append({'batch': '2a', 'kind': 'wired', 'server': sp, 'shared': h + '/shared_' + t, 'files': [f], 'via': serverobjects_rel, 'note': note})
        return out

    # ---- 2a: wiring -------------------------------------------------------------------------------------
    rel = 'custom_content/tangible/holiday/empire_day/serverobjects.lua'
    old = read(rel)
    change(rel, insert_line(old, 'includeFile("custom_content/tangible/holiday/empire_day/aa1n_vebrobrain_protocol_droid_component_crate.lua")',
                            'includeFile("custom_content/tangible/holiday/empire_day/component/serverobjects.lua")', before=True), old, 'empire day components')
    objects += wired_objects('custom_content/tangible/holiday/empire_day/component/serverobjects.lua', 'Empire Day crafting component (NGE event); loads but has no recipe yet')

    rel = 'custom_content/building/player/serverobjects.lua'
    old = read(rel)
    change(rel, insert_line(old, 'includeFile("custom_content/building/player/city/serverobjects.lua")',
                            'includeFile("custom_content/building/player/construction/serverobjects.lua")', before=False), old, 'construction markers')
    objects += wired_objects('custom_content/building/player/construction/serverobjects.lua', 'construction marker for a TCG/NGE player structure; used only once its deed chain exists')

    rel = 'custom_content/tangible/content/serverobjects.lua'
    old = read(rel)
    change(rel, insert_line(old, 'includeFile("custom_content/tangible/content/wod_crafting_alter_1.lua")',
                            'includeFile("custom_content/tangible/content/eow/serverobjects.lua")', before=True), old, 'eow data disks')
    objects += wired_objects('custom_content/tangible/content/eow/serverobjects.lua', 'Empire of Wookiees quest data disk; quest not ported')

    rel = 'custom_content/static/serverobjects.lua'
    old = read(rel)
    change(rel, insert_line(old, 'includeFile("custom_content/static/christmas/serverobjects.lua")',
                            'includeFile("custom_content/static/base/serverobjects.lua")', before=True), old, 'static base')
    objects += wired_objects('custom_content/static/base/serverobjects.lua', 'flagpole base template (MTG registers it as a building template)')

    # allobjects.lua: on top of batch 1
    rel = 'allobjects.lua'
    old = read(rel, from_batch1=True)
    new = insert_line(old, 'includeFile("custom_content/static/christmas/objects.lua")', 'includeFile("custom_content/static/base/objects.lua")', before=True)
    new = insert_line(new, 'includeFile("custom_content/tangible/furniture/tatooine/objects.lua")', 'includeFile("custom_content/tangible/furniture/space/objects.lua")', before=True)
    change(rel, new, old, 'allobjects (after batch 1)')

    # ---- 2b: new templates --------------------------------------------------------------------------------
    def new_object(kind, folder, name, template_class, body=''):
        shared = f'object/{folder}/shared_{name}.iff'
        server = f'object/{folder}/{name}.iff'
        base = folder.replace('/', '_')
        var, svar = f'object_{base}_{name}', f'object_{base}_shared_{name}'
        info = swg_iff.resolved(shared)
        win = scd._index.get(shared.lower())
        entry = [f'{svar} = {template_class}:new {{', f'\tclientTemplateFileName = "{shared}"', '}',
                 f'ObjectTemplates:addClientTemplate({svar}, "{shared}")']
        srel = f'custom_content/{folder}/{name}.lua'
        srv = (f'-- Fable backport batch 2 (14 Oct 2026). Client template {shared} ({os.path.basename(win[0]) if win else "?"}), '
               f'form {info["form"] if info else "?"}.\n\n{var} = {svar}:new {{\n{body}}}\n\nObjectTemplates:addTemplate({var}, "{server}")\n')
        write_staged(srel, srv.encode('ascii'))
        write_diff(srel, None, srv.encode('ascii'), combined)
        manifest.append((srel, 'new'))
        objects.append({'batch': '2b', 'kind': 'new', 'server': server, 'shared': shared, 'var': var, 'shared_var': svar,
                        'files': [srel, f'custom_content/{folder}/objects.lua', f'custom_content/{folder}/serverobjects.lua'], 'line_endings': 'LF'})
        return entry, f'includeFile("{srel}")'

    # Tatooine walls: extend the existing custom_content folder files (CRLF, "--***" separators)
    entries, includes = [], []
    for s in WALLS:
        e, inc = new_object('static', 'static/structure/tatooine', f'wall_tatooine_large_style_{s}', 'SharedStaticObjectTemplate')
        entries.append(e)
        includes.append([inc])
    rel = 'custom_content/static/structure/tatooine/objects.lua'
    old = read(rel)
    change(rel, append_lines(old, entries, separator=SEP), old, 'walls')
    rel = 'custom_content/static/structure/tatooine/serverobjects.lua'
    old = read(rel)
    change(rel, append_lines(old, includes), old, 'walls')

    # Mustafar mining facility static
    e, inc = new_object('static', 'static/creature', 'som_droid_mining_facility', 'SharedStaticObjectTemplate')
    rel = 'custom_content/static/creature/objects.lua'
    old = read(rel)
    change(rel, append_lines(old, [[''] + e]), old, 'mining facility')
    rel = 'custom_content/static/creature/serverobjects.lua'
    old = read(rel)
    change(rel, append_lines(old, [[inc]]), old, 'mining facility')

    # Y-8 passenger chair: new folder custom_content/tangible/furniture/space
    e, inc = new_object('tangible', 'tangible/furniture/space', 'frn_chair_y8_passenger_s01', 'SharedTangibleObjectTemplate')
    folder = 'custom_content/tangible/furniture/space'
    obj = ('-- Fable backport batch 2 (14 Oct 2026): shared template for the Y-8 passenger chair (SOE original, also on the owner\'s disc).\n'
           '-- Style as custom_content/tangible/furniture/tatooine/objects.lua.\n\n' + '\n'.join(e) + '\n')
    srv = '-- Fable backport batch 2 (14 Oct 2026): server objects for custom_content/tangible/furniture/space.\n\n' + inc + '\n'
    for fname, data in ((f'{folder}/objects.lua', obj), (f'{folder}/serverobjects.lua', srv)):
        write_staged(fname, data.encode('ascii'))
        write_diff(fname, None, data.encode('ascii'), combined)
        manifest.append((fname, 'new'))
    rel = 'custom_content/tangible/furniture/serverobjects.lua'
    old = read(rel)
    change(rel, insert_line(old, 'includeFile("custom_content/tangible/furniture/tatooine/serverobjects.lua")',
                            'includeFile("custom_content/tangible/furniture/space/serverobjects.lua")', before=True), old, 'furniture space')

    # ---- outputs -------------------------------------------------------------------------------------------
    with open(os.path.join(ROOT, 'batch2.diff'), 'wb') as f:
        f.write(''.join(combined).encode('latin-1'))
    with open(os.path.join(ROOT, 'apply-manifest-batch2.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# path relative to MMOCoreORB/bin/scripts/object<TAB>sha256 of the file this was diffed against (allobjects.lua: batch 1 staged copy), or new\n')
        for rel, h in manifest:
            f.write(f'{rel}\t{h}\n')
    with open(os.path.join(W, 'batch2_objects.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'objects': objects, 'manifest': manifest}, f, indent=1)
    kinds = {}
    for o in objects:
        kinds[o['kind']] = kinds.get(o['kind'], 0) + 1
    print(f'staged {len(manifest)} files: {sum(1 for _, h in manifest if h != "new")} changed, {sum(1 for _, h in manifest if h == "new")} new; objects: {kinds}')


if __name__ == '__main__':
    main()
