"""Produce Fable-builder/patch/hoth_client_build.py (patched) and client_load_order.py (patched) from the originals."""
import os, re
R = 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs'
def transform(src, out, reps):
    s = open(src, encoding='utf-8', newline='').read()
    for old, new in reps:
        assert s.count(old) == 1, ('not exactly once:', old[:60], s.count(old))
        s = s.replace(old, new)
    open(out, 'w', encoding='utf-8', newline='').write(s)
    print('wrote', out, len(s))
nl = '\r\n' if '\r\n' in open(R + '/tools/hoth/hoth_client_build.py', encoding='utf-8', newline='').read() else '\n'
print('builder newline:', repr(nl))
B = [
 ("Format tools are Bellum Gero's (AGPL-3.0, pinned in work/research, read before use).",
  "Format tools are ours: Fable's swg_tables, ui_inc and tre_write behind Fable-builder/tools/fmt_tools.py."),
 ("BELLUM = os.path.join(H, 'work', 'research', 'Miphstoe_BellumGero-Live', 'MMOCoreORB', 'tools', 'newplanets')" + nl, ""),
 ("sys.path.insert(0, BELLUM)" + nl + "import stf_tool, dt_tool, cstb_tool, tre_pack, merge_ticket_ui as ui  # noqa: E402  (Bellum's)" + nl +
  "exec(open(os.path.join(BELLUM, 'tre_inventory.py'), encoding='utf-8').read().split('if __name__')[0])" + nl,
  "sys.path.insert(0, os.path.join(H, 'outputs', 'Fable-builder', 'tools'))" + nl +
  "from fmt_tools import stf_tool, dt_tool, cstb_tool, tre_pack, read_tre, _inflate  # noqa: E402  (ours: swg_tables, trn_iff, tre_write)" + nl +
  "import hoth_ui  # noqa: E402  (ours: ui_inc)" + nl),
 ("GALAXY_SPOT = (425, 225)" + nl + "ENDOR_BUTTON = (23, 302)" + nl, "GALAXY_SPOT = (425, 225)" + nl),
]
s = open(R + '/tools/hoth/hoth_client_build.py', encoding='utf-8', newline='').read()
a = s.index('def shift(line, dx, dy):'); b = s.index('def archive_file(archive, path):')
old_block = s[a:b]
new_block = ('def ui_includes():' + nl +
             '    """Endor\'s blocks cloned for Hoth in both UI includes (Fable\'s ui_inc through hoth_ui): the stock bytes outside' + nl +
             '    the inserted blocks stay as they are, the bare carriage returns in the OnShow/OnHide scripts included."""' + nl +
             "    return hoth_ui.stage_hoth_ui(STAGE, base=lambda path: open(src(path), 'rb').read(), spot=GALAXY_SPOT)" + nl + nl + nl)
B.append((old_block, new_block))
B.append(("strings(); crc_table(); travel(); waypoints(); ticket_ui(); planet_map_ui()", "strings(); crc_table(); travel(); waypoints(); ui_includes()"))
B.append(('"""The stock .inc files use CRLF; ui.load() normalises to LF, so make sure we wrote CRLF back."""',
          '"""The stock .inc files use CRLF; hoth_ui keeps every stock byte, so only make sure the stock copy is pure CRLF."""'))
os.makedirs(R + '/Fable-builder/patch', exist_ok=True)
transform(R + '/tools/hoth/hoth_client_build.py', R + '/Fable-builder/patch/hoth_client_build.py', B)
# client_load_order.py: the exec of Bellum's tre_inventory -> our read_tre
c = open(R + '/tools/hoth/client_load_order.py', encoding='utf-8', newline='').read()
nl2 = '\r\n' if '\r\n' in c else '\n'
C = [("BELLUM = os.path.join(H, 'work', 'research', 'Miphstoe_BellumGero-Live', 'MMOCoreORB', 'tools', 'newplanets')" + nl2, ""),
     ("exec(open(os.path.join(BELLUM, 'tre_inventory.py'), encoding='utf-8').read().split('if __name__')[0])" + nl2,
      "sys.path.insert(0, os.path.join(H, 'outputs', 'Fable-builder', 'tools'))" + nl2 + "from fmt_tools import read_tre, _inflate  # noqa: E402  (ours; was Bellum's tre_inventory)" + nl2)]
transform(R + '/tools/hoth/client_load_order.py', R + '/Fable-builder/patch/client_load_order.py', C)
