"""T1: build t1/staged/ = outputs/tools/swgfmt/ (the package), the thin shims at the old module paths, and the patched
importers, plus t1/patch/*.patch (unified diffs against the current files). Every edit asserts its anchor once."""
import os
import subprocess

OUTPUTS = 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs'
T1 = OUTPUTS + '/Fable-resources2/t1'
PKG = T1 + '/staged/tools/swgfmt'
BELLUM_LINE = "BELLUM = os.path.join(H, 'work', 'research', 'Miphstoe_BellumGero-Live', 'MMOCoreORB', 'tools', 'newplanets')\n"
EXEC_LINE = "exec(open(os.path.join(BELLUM, 'tre_inventory.py'), encoding='utf-8').read().split('if __name__')[0])\n"


def read(rel):
    with open(OUTPUTS + '/' + rel, encoding='utf-8', newline='') as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)


def edited(text, reps, label):
    for old, new in reps:
        assert text.count(old) == 1, (label, old[:70], text.count(old))
        text = text.replace(old, new)
    return text


# ---------------------------------------------------------------- 1. the package
FIND_H = '''def _find_h():
    """The project root: the nearest parent holding outputs/SWG-client, so the module works from any folder under it."""
    d = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.isdir(os.path.join(d, 'outputs', 'SWG-client')):
            return d
        up = os.path.dirname(d)
        if up == d:
            return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
        d = up


H = _find_h()
'''
MODULES = {
    'swg_tables': ('Fable-ossus/tools/swg_tables.py', [
        ("sys.path.insert(0, os.path.join(HERE, '..', '..', 'Fable-planet-test', 'tools'))\nfrom trn_iff import Writer, build, chunk, form, parse  # noqa: E402\n",
         "from .trn_iff import Writer, build, chunk, form, parse  # noqa: E402\n")]),
    'trn_iff': ('Fable-planet-test/tools/trn_iff.py', [
        ("H = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))\n", FIND_H)]),
    'tre_write': ('Fable-builder/tools/tre_write.py', [
        ("    sys.path.insert(0, os.path.join(outputs, 'Fable-planet-test', 'tools'))\n", ""),
        ("    import trn_iff\n", "    from . import trn_iff\n")]),
    'ui_inc': ('Fable-ossus/o4/tools/ui_inc.py', []),
    'fmt_tools': ('Fable-builder/tools/fmt_tools.py', [
        ("for rel in ('Fable-ossus/tools', 'Fable-planet-test/tools', 'Fable-builder/tools'):\n    p = os.path.join(OUTPUTS, rel)\n    if p not in sys.path:\n        sys.path.insert(0, p)\nimport swg_tables as st  # noqa: E402\nimport trn_iff  # noqa: E402\nimport tre_write  # noqa: E402\n",
         "from . import swg_tables as st  # noqa: E402\nfrom . import trn_iff  # noqa: E402\nfrom . import tre_write  # noqa: E402\n"),
        ("The byte work is swg_tables (Fable-ossus/tools), trn_iff (Fable-planet-test/tools) and tre_write (here).",
         "    walk_tres(root) / cfg_priorities(root) / extract_entry(tre, entry, out_root)   the archive walk the Hoth scripts use\nThe byte work is swg_tables, trn_iff and tre_write beside this file (outputs/tools/swgfmt)."),
    ]),
    'hoth_ui': ('Fable-builder/tools/hoth_ui.py', [
        ("for rel in ('Fable-ossus/o4/tools', 'Fable-planet-test/tools'):\n    p = os.path.join(OUTPUTS, rel)\n    if p not in sys.path:\n        sys.path.insert(0, p)\nimport ui_inc  # noqa: E402\n",
         "from . import ui_inc  # noqa: E402\n")]),
    'ws_read': ('Fable-hoth-caves/tools/ws_read.py', [
        ("sys.path.insert(0, os.path.join(HERE, '..', '..', 'Fable-planet-test', 'tools'))\nfrom trn_iff import Reader, load, parse  # noqa: E402\n",
         "from .trn_iff import Reader, load, parse  # noqa: E402\n")]),
}
WALK = r'''

# ---------------------------------------------------------------- the archive walk the Hoth scripts use (was tre_inventory)

def cfg_priorities(root):
    """{archive basename (lower): NN} from every searchTree_XX_NN=<file> line of every *.cfg in root, whatever the
    section (the client itself reads [SharedFile] only: client_load_order.py does that; this keeps the older scripts'
    contract)."""
    import re
    pri = {}
    try:
        cfgs = [f for f in os.listdir(root) if f.lower().endswith('.cfg')]
    except OSError:
        return pri
    pat = re.compile(r'^\s*searchTree_\d+_(\d+)\s*=\s*(\S+)', re.I)
    for cfg in cfgs:
        with open(os.path.join(root, cfg), encoding='latin-1') as f:
            for line in f:
                m = pat.match(line)
                if m:
                    pri[os.path.basename(m.group(2)).lower()] = int(m.group(1))
    return pri


def walk_tres(root):
    """Every .tre under root, lowest priority first (a later archive wins), archives the cfg does not list or that sit
    in a subfolder first of all, alphabetical within a rank."""
    found = []
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if fn.lower().endswith('.tre'):
                found.append(os.path.join(dirpath, fn))
    pri = cfg_priorities(root)
    top = os.path.normcase(os.path.abspath(root))

    def rank(p):
        if os.path.normcase(os.path.dirname(os.path.abspath(p))) != top:
            return -1
        return pri.get(os.path.basename(p).lower(), -1)
    return sorted(found, key=lambda p: (rank(p), os.path.basename(p).lower()))


def extract_entry(tre_path, entry, out_root):
    """Write one archive entry under out_root at its internal path; returns the path written."""
    with open(tre_path, 'rb') as f:
        f.seek(entry['offset'])
        blob = f.read(entry['comp_size'] if entry['comp'] else entry['size'])
    data = _inflate(blob, entry['comp'], entry['size'])
    out_path = os.path.join(out_root, *entry['name'].split('/'))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'wb') as o:
        o.write(data)
    return out_path
'''
WS_OBJECTS = '''

def ws_objects(buf):
    """(object id, parent id, template, x, height, y) for every node of a .ws snapshot, in file order (the shape
    tools/hoth/hoth_snapshot.py reads)."""
    nodes = read_ws(buf)
    nodes = nodes['nodes'] if isinstance(nodes, dict) else nodes[0] if isinstance(nodes, tuple) else nodes
    return [(n['id'], n['parent'], n['template'], n['x'], n['z'], n['y']) for n in nodes]
'''
for name, (rel, reps) in MODULES.items():
    text = edited(read(rel), reps, name)
    if name == 'fmt_tools':
        text += WALK
    if name == 'ws_read':
        text += WS_OBJECTS
    write(PKG + '/' + name + '.py', text)
write(PKG + '/__init__.py', '''"""swgfmt: our SWG client-format tools in one place (Fable T1, 14 Oct 2026).

    sys.path.insert(0, '<...>/outputs/tools'); from swgfmt import swg_tables, trn_iff, tre_write, ui_inc, fmt_tools, hoth_ui, ws_read

swg_tables   CSTB / DTII / STF readers and writers, SOE CRC          trn_iff   IFF parse/build, TRE reading, the client's load order
tre_write    TRE writer                                               ui_inc    planet blocks for the two UI includes
fmt_tools    the builder's call shapes (stf/dt/cstb/tre_pack, read_tre, walk_tres)   hoth_ui   Hoth's UI blocks   ws_read   .ws snapshots
The old module paths (Fable-*/tools/<name>.py) are shims that hand their imports to these files.
"""
''')

# ---------------------------------------------------------------- 2. shims at the old paths
SHIM = '''"""Moved to outputs/tools/swgfmt/{name}.py (Fable T1, 14 Oct 2026). This shim hands every import of the old path to the
package, so `import {name}` here and `from swgfmt import {name}` are the same module object."""
import importlib
import os
import runpy
import sys

_tools = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), {up}, 'tools'))
if _tools not in sys.path:
    sys.path.insert(0, _tools)
if __name__ == '__main__':
    runpy.run_module('swgfmt.{name}', run_name='__main__', alter_sys=True)
else:
    sys.modules[__name__] = importlib.import_module('swgfmt.{name}')
'''
UPS = {'Fable-ossus/tools/swg_tables.py': "'..', '..'", 'Fable-planet-test/tools/trn_iff.py': "'..', '..'",
       'Fable-builder/tools/tre_write.py': "'..', '..'", 'Fable-builder/tools/fmt_tools.py': "'..', '..'", 'Fable-builder/tools/hoth_ui.py': "'..', '..'",
       'Fable-ossus/o4/tools/ui_inc.py': "'..', '..', '..'", 'Fable-hoth-caves/tools/ws_read.py': "'..', '..'"}
for rel, up in UPS.items():
    write(T1 + '/staged/' + rel, SHIM.format(name=os.path.basename(rel)[:-3], up=up))

# ---------------------------------------------------------------- 3. patched importers
PATCHES = {
    'tools/hoth/hoth_client_build.py': [
        ("sys.path.insert(0, os.path.join(H, 'outputs', 'Fable-builder', 'tools'))\nfrom fmt_tools import stf_tool, dt_tool, cstb_tool, tre_pack, read_tre, _inflate  # noqa: E402  (ours: swg_tables, trn_iff, tre_write)\nimport hoth_ui  # noqa: E402  (ours: ui_inc)\n",
         "sys.path.insert(0, os.path.join(H, 'outputs', 'tools'))\nfrom swgfmt.fmt_tools import stf_tool, dt_tool, cstb_tool, tre_pack, read_tre, _inflate  # noqa: E402  (ours: swg_tables, trn_iff, tre_write)\nfrom swgfmt import hoth_ui  # noqa: E402  (ours: ui_inc)\n"),
        ("Format tools are ours: Fable's swg_tables, ui_inc and tre_write behind Fable-builder/tools/fmt_tools.py.",
         "Format tools are ours: outputs/tools/swgfmt (swg_tables, ui_inc, tre_write behind fmt_tools)."),
    ],
    'tools/hoth/client_load_order.py': [
        ("sys.path.insert(0, os.path.join(H, 'outputs', 'Fable-builder', 'tools'))\nfrom fmt_tools import read_tre, _inflate  # noqa: E402  (ours; was Bellum's tre_inventory)\n",
         "sys.path.insert(0, os.path.join(H, 'outputs', 'tools'))\nfrom swgfmt.fmt_tools import read_tre, _inflate  # noqa: E402  (ours; was Bellum's tre_inventory)\n"),
    ],
    'tools/hoth/hoth_client_files.py': [
        (BELLUM_LINE, ""),
        ("sys.path.insert(0, BELLUM)\n" + EXEC_LINE + "import stf_tool, dt_tool, cstb_tool  # noqa: E402  (Bellum's)\n",
         "sys.path.insert(0, os.path.join(H, 'outputs', 'tools'))\nfrom swgfmt.fmt_tools import read_tre, walk_tres, extract_entry, stf_tool, dt_tool, cstb_tool  # noqa: E402  (ours)\n"),
        ("Format tools come from Bellum Gero's planet tools (AGPL-3.0, pinned in work/research, read before use).",
         "Format tools are ours (outputs/tools/swgfmt)."),
    ],
    'tools/hoth/hoth_registration_check.py': [
        (BELLUM_LINE, ""),
        (EXEC_LINE, "sys.path.insert(0, os.path.join(H, 'outputs', 'tools'))\nfrom swgfmt.fmt_tools import read_tre, _inflate, walk_tres  # noqa: E402  (ours)\n"),
        ("uses Bellum's TRE reader the same way hoth_closure.py does.", "uses our TRE reader (outputs/tools/swgfmt) the same way hoth_closure.py does."),
    ],
    'tools/hoth/hoth_snapshot.py': [
        (BELLUM_LINE, ""),
        ("sys.path.insert(0, BELLUM)\n" + EXEC_LINE + "import iff_tool  # noqa: E402  (Bellum's; ws_objects is defined at module level)\n",
         "sys.path.insert(0, os.path.join(H, 'outputs', 'tools'))\nfrom swgfmt.fmt_tools import read_tre, _inflate, walk_tres  # noqa: E402  (ours)\nfrom swgfmt import ws_read  # noqa: E402  (ours)\n"),
        ("    objects = iff_tool.ws_objects(data)\n", "    objects = ws_read.ws_objects(data)\n"),
        ("taken from other servers' scripts (Bellum's Hoth was built on a different snapshot). Read-only; uses Bellum's\nTRE and IFF readers (AGPL-3.0, read before use).",
         "taken from other servers' scripts (Bellum's Hoth was built on a different snapshot). Read-only; uses our TRE and\nsnapshot readers (outputs/tools/swgfmt)."),
    ],
    'tools/hoth/hoth_closure.py': [
        ("for module in ('tre_inventory.py', 'iff_tool.py'):\n    exec(open(os.path.join(BELLUM, module), encoding='utf-8').read().split('if __name__')[0])\n",
         "sys.path.insert(0, os.path.join(H, 'outputs', 'tools'))\nfrom swgfmt.fmt_tools import read_tre, _inflate  # noqa: E402  (ours; was Bellum's tre_inventory)\n# refs(): Bellum's asset-reference scanner (iff_tool.py); our readers have no equivalent yet, so it stays.\nexec(open(os.path.join(BELLUM, 'iff_tool.py'), encoding='utf-8').read().split('if __name__')[0])\n"),
    ],
    'Fable-hoth-mapnames/tools/hoth_names.py': [
        ("for rel in ('Fable-ossus/tools', 'Fable-planet-test/tools'):\n    p = os.path.join(OUTPUTS, rel)\n    if p not in sys.path:\n        sys.path.insert(0, p)\nimport swg_tables as st  # noqa: E402\nimport trn_iff  # noqa: E402\n",
         "if os.path.join(OUTPUTS, 'tools') not in sys.path:\n    sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))\nfrom swgfmt import swg_tables as st  # noqa: E402\nfrom swgfmt import trn_iff  # noqa: E402\n"),
    ],
    'Fable-ossus/o4/tools/stage_ossus.py': [
        ("for rel in ('Fable-ossus/tools', 'Fable-planet-test/tools', 'Fable-ossus/o4/tools'):\n    p = os.path.join(OUTPUTS, rel)\n    if p not in sys.path:\n        sys.path.insert(0, p)\nimport swg_tables as st  # noqa: E402\nimport trn_iff  # noqa: E402\nimport ui_inc  # noqa: E402\n",
         "if os.path.join(OUTPUTS, 'tools') not in sys.path:\n    sys.path.insert(0, os.path.join(OUTPUTS, 'tools'))\nfrom swgfmt import swg_tables as st  # noqa: E402\nfrom swgfmt import trn_iff  # noqa: E402\nfrom swgfmt import ui_inc  # noqa: E402\n"),
    ],
    'Fable-ossus/o3/tools/map_art.py': [
        ("for rel in ('Fable-planet-test/tools', 'Fable-ossus/tools', 'Fable-ossus/o3/tools'):\n    p = os.path.join(OUTPUTS, rel)\n    if p not in sys.path:\n        sys.path.insert(0, p)\nimport trn_iff  # noqa: E402\nimport trn_read  # noqa: E402\nimport swg_tables as st  # noqa: E402\n",
         "for rel in ('tools', 'Fable-planet-test/tools', 'Fable-ossus/tools', 'Fable-ossus/o3/tools'):   # trn_read, trn_road and dds stay beside their batches\n    p = os.path.join(OUTPUTS, rel)\n    if p not in sys.path:\n        sys.path.insert(0, p)\nfrom swgfmt import trn_iff  # noqa: E402\nimport trn_read  # noqa: E402\nfrom swgfmt import swg_tables as st  # noqa: E402\n"),
    ],
}
os.makedirs(T1 + '/patch', exist_ok=True)
for rel, reps in PATCHES.items():
    new = edited(read(rel), reps, rel)
    write(T1 + '/staged/' + rel, new)
    out = T1 + '/patch/' + os.path.basename(rel)[:-3] + '.patch'
    p = subprocess.run(['diff', '-u', '--label', 'a/' + rel, '--label', 'b/' + rel, OUTPUTS + '/' + rel, T1 + '/staged/' + rel], capture_output=True, text=True)
    write(out, p.stdout)
    print('patched', rel, '->', len(p.stdout.splitlines()), 'diff lines')
for rel in UPS:
    p = subprocess.run(['diff', '-u', '--label', 'a/' + rel, '--label', 'b/' + rel, OUTPUTS + '/' + rel, T1 + '/staged/' + rel], capture_output=True, text=True)
    write(T1 + '/patch/shim-' + os.path.basename(rel)[:-3] + '.patch', p.stdout)
print('package files:', sorted(os.listdir(PKG)))
