"""Offline tests for the client patch kit: dummy client folders in a temp folder, the real PowerShell scripts.

    python -I tools/client_patch/test_client_patch.py [-v]

Needs Windows PowerShell (powershell.exe). Touches nothing outside the temp folder.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / 'hoth'))
import client_patch as cp  # noqa: E402
from swgfmt import tre_write  # noqa: E402

CRLF = '\r\n'
STOCK = ['patch_14_00.tre', 'patch_05.tre', 'data_other_00.tre', 'bottom.tre']
MTG = [(23, 'mtg_patch_023.tre'), (16, 'mtg_patch_016.tre')]
INCLUDE = '.include "local_planets.cfg"'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_client(folder, mtg_in_cfg=True, mtg_files=True, extra=None, top=50, levels=(47, 46, 45, 44)):
    """A folder that looks like a SWGEmu client: exe, cfg chain, stock and MTG archive stand-ins. The default is the
    owner's layout; top=26, levels=(23, 5, 1, 0) is a stock SWGEmu Launchpad client."""
    folder = Path(folder)
    folder.mkdir(parents=True)
    (folder / 'SWGEmu.exe').write_bytes(b'MZ dummy')
    (folder / 'swgemu.cfg').write_bytes(CRLF.join(['.include "swgemu_login.cfg"', '.include "swgemu_live.cfg"',
                                                   '.include "user.cfg"']).encode() + b'\r\n')
    (folder / 'swgemu_login.cfg').write_bytes(b'[ClientGame]\r\nloginServerPort0=44453\r\n')
    live = ['[SharedFile]', '\tmaxSearchPriority=%d' % top] + ['\tsearchTree_00_%d=%s' % (p, n) for p, n in zip(levels, STOCK)]
    live += ['', '[Station]', 'subscriptionFeatures=1']
    if mtg_in_cfg:
        live += ['[SharedFile]'] + ['\tsearchTree_00_%d=%s' % (p, n) for p, n in MTG]
    (folder / 'swgemu_live.cfg').write_bytes((CRLF.join(live) + CRLF).encode())
    (folder / 'user.cfg').write_bytes(b'[ClientGraphics]\r\nscreenWidth=1280\r\n')
    for n in STOCK:
        (folder / n).write_bytes(b'EERT stock ' + n.encode())
    if mtg_files:
        for _, n in MTG:
            (folder / n).write_bytes(b'EERT mtg ' + n.encode() * 10)
    for name, data in (extra or {}).items():
        (folder / name).write_bytes(data)
    return folder


def ps(script, *args):
    exe = shutil.which('powershell') or shutil.which('powershell.exe')
    r = subprocess.run([exe, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(script)] + [str(a) for a in args],
                       capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout + r.stderr


def loaded(client):
    import client_load_order as clo
    clo.CLIENT = str(client)
    trees, _, _ = clo.load_order()
    return {n.lower(): p for p, n in trees}


@unittest.skipUnless(shutil.which('powershell') or shutil.which('powershell.exe'), 'needs Windows PowerShell')
class KitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix='client-patch-test-'))
        cls.owner = make_client(cls.tmp / 'owner')
        cls.kits = {}
        for version, payload in (('2026.10.16.1', b'first'), ('2026.10.17.1', b'second')):
            archive = cls.tmp / ('local_planets-%s.tre' % version)
            archive.write_bytes(tre_write.pack({'misc/c57_test.txt': payload}))
            notes = cls.tmp / ('notes-%s.txt' % version)
            notes.write_text('Test build %s.\nSecond line.' % version, encoding='utf-8')
            out = cls.tmp / 'kits' / version
            cp.main(['build', '--archive', str(archive), '--version', version, '--notes', str(notes), '--out', str(out),
                     '--client', str(cls.owner)])
            cls.kits[version] = out
        cls.v1, cls.v2 = cls.kits['2026.10.16.1'], cls.kits['2026.10.17.1']

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def client(self, name, **kw):
        return make_client(self.tmp / 'friends' / name, **kw)

    def install(self, kit, client, *extra):
        return ps(kit / 'Install-ClientPatch.ps1', '-ClientDir', client, *extra)

    def uninstall(self, kit, client):
        return ps(kit / 'Uninstall-ClientPatch.ps1', '-ClientDir', client)

    # --- the packaging tool -----------------------------------------------------------------------------
    def test_kit_contents(self):
        m = json.loads((self.v1 / 'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(m['version'], '2026.10.16.1')
        self.assertEqual(m['archive']['sha256'], sha(self.v1 / 'local_planets.tre'))
        self.assertEqual(m['archive']['priority'], 49)
        self.assertEqual([(r['priority'], r['file']) for r in m['requires']], MTG)
        self.assertTrue(all(r['sha256'] == sha(self.owner / r['file']) for r in m['requires']))
        self.assertEqual(cp.verify_kit(self.v1), [])
        self.assertIn(b'searchTree_00_49=local_planets.tre\r\n', (self.v1 / 'local_planets.cfg').read_bytes())
        self.assertTrue((self.tmp / 'kits' / 'local_planets-2026.10.16.1.zip').exists())

    def test_bad_version_and_reused_folder_refused(self):
        with self.assertRaises(SystemExit):
            cp.main(['build', '--archive', str(self.v1 / 'local_planets.tre'), '--version', 'v2', '--notes',
                     str(self.tmp / 'notes-2026.10.16.1.txt'), '--out', str(self.tmp / 'x'), '--client', str(self.owner)])
        with self.assertRaises(SystemExit):
            cp.main(['build', '--archive', str(self.v1 / 'local_planets.tre'), '--version', '2026.10.16.1', '--notes',
                     str(self.tmp / 'notes-2026.10.16.1.txt'), '--out', str(self.v1), '--client', str(self.owner)])

    def test_check_server(self):
        self.assertEqual(cp.main(['check-server', str(self.v1), '--server-file', str(self.v1 / 'local_planets.tre')]), 0)
        self.assertEqual(cp.main(['check-server', str(self.v1), '--server-sha', sha(self.v2 / 'local_planets.tre') + '  /opt/swg/tre/local_planets.tre']), 1)

    # --- install and uninstall --------------------------------------------------------------------------
    def test_install_reinstall_uninstall_restores_everything(self):
        c = self.client('plain')
        before = {p.name: p.read_bytes() for p in c.iterdir()}
        code, out = self.install(self.v1, c)
        self.assertEqual(code, 0, out)
        self.assertEqual(sha(c / 'local_planets.tre'), sha(self.v1 / 'local_planets.tre'))
        self.assertEqual(loaded(c).get('local_planets.tre'), 49)                 # the Python reader agrees
        self.assertEqual((c / 'swgemu.cfg').read_bytes().count(INCLUDE.encode()), 1)
        state = json.loads((c / 'local_planets-patch' / 'state.json').read_text())
        self.assertEqual(state['version'], '2026.10.16.1')
        self.assertEqual(state['mtg_lines_added'], [])                         # this client already loads them
        code, out = self.install(self.v1, c)                                   # again: no second include line
        self.assertEqual(code, 0, out)
        self.assertEqual((c / 'swgemu.cfg').read_bytes().count(INCLUDE.encode()), 1)
        code, out = self.uninstall(self.v1, c)
        self.assertEqual(code, 0, out)
        after = {p.name: p.read_bytes() for p in c.iterdir() if p.name != 'local_planets-patch'}
        self.assertEqual(after, before)
        self.assertNotIn('local_planets.tre', loaded(c))
        code, out = self.uninstall(self.v1, c)
        self.assertEqual(code, 0, out)
        self.assertIn('Nothing to remove', out)

    def test_mtg_lines_added_when_the_client_does_not_load_them(self):
        c = self.client('no-mtg-cfg', mtg_in_cfg=False)
        self.assertNotIn('mtg_patch_023.tre', loaded(c))
        code, out = self.install(self.v1, c)
        self.assertEqual(code, 0, out)
        got = loaded(c)
        self.assertEqual((got.get('local_planets.tre'), got.get('mtg_patch_023.tre'), got.get('mtg_patch_016.tre')), (49, 23, 16))
        code, out = self.uninstall(self.v1, c)
        self.assertEqual(code, 0, out)
        self.assertNotIn('mtg_patch_023.tre', loaded(c))

    def test_stock_client_gets_the_server_layout(self):
        # Microverse, 18 Oct: a fresh Launchpad client caps at 26, so 49 was never loaded.
        c = self.client('stock26', mtg_in_cfg=False, top=26, levels=(23, 5, 1, 0))
        before = {p.name: p.read_bytes() for p in c.iterdir()}
        code, out = self.install(self.v1, c)
        self.assertEqual(code, 0, out)
        got = loaded(c)
        self.assertEqual([got.get(n) for n in ('local_planets.tre', 'patch_14_00.tre', 'bottom.tre', 'mtg_patch_023.tre', 'mtg_patch_016.tre')],
                         [49, 47, 24, 23, 16])
        self.assertTrue(json.loads((c / 'local_planets-patch' / 'state.json').read_text())['live_cfg_moved'])
        code, out = self.install(self.v1, c)                                   # again: not moved a second time
        self.assertEqual(code, 0, out)
        self.assertEqual(loaded(c).get('patch_14_00.tre'), 47)
        code, out = self.uninstall(self.v1, c)
        self.assertEqual(code, 0, out)
        after = {p.name: p.read_bytes() for p in c.iterdir() if p.name != 'local_planets-patch'}
        self.assertEqual(after, before)

    def test_other_layout_refused_unchanged(self):
        # Moving these up to cap 50 would put bottom.tre (0 + 10) among the MTG archives: stop instead.
        c = self.client('odd', mtg_in_cfg=False, top=40, levels=(37, 10, 1, 0))
        before = {p.name: p.read_bytes() for p in c.iterdir()}
        code, out = self.install(self.v1, c)
        self.assertEqual(code, 1, out)
        self.assertIn('laid out differently', out)
        self.assertEqual({p.name: p.read_bytes() for p in c.iterdir()}, before)

    def test_rerun_after_a_stopped_install(self):
        # What an older kit left on Microverse: our tre, our cfg, the include line and a swgemu.cfg backup, no state.
        c = self.client('stopped', mtg_in_cfg=False, top=26, levels=(23, 5, 1, 0))
        before = {p.name: p.read_bytes() for p in c.iterdir()}
        original = c / 'local_planets-patch' / 'backup' / 'original'
        original.mkdir(parents=True)
        shutil.copyfile(c / 'swgemu.cfg', original / 'swgemu.cfg')
        (c / 'swgemu.cfg').write_bytes((c / 'swgemu.cfg').read_bytes() + INCLUDE.encode() + b'\r\n')
        shutil.copyfile(self.v1 / 'local_planets.cfg', c / 'local_planets.cfg')
        shutil.copyfile(self.v1 / 'local_planets.tre', c / 'local_planets.tre')
        code, out = self.install(self.v1, c)
        self.assertEqual(code, 0, out)
        self.assertEqual(loaded(c).get('local_planets.tre'), 49)
        self.assertFalse((original / 'local_planets.cfg').exists())             # ours is not the friend's original
        code, out = self.uninstall(self.v1, c)
        self.assertEqual(code, 0, out)
        after = {p.name: p.read_bytes() for p in c.iterdir() if p.name != 'local_planets-patch'}
        self.assertEqual(after, before)

    def test_existing_archive_backed_up_and_restored(self):
        theirs = b'EERT somebody else\'s archive'
        c = self.client('own-archive', extra={'local_planets.tre': theirs})
        code, out = self.install(self.v1, c)
        self.assertEqual(code, 0, out)
        self.assertEqual((c / 'local_planets-patch' / 'backup' / 'original' / 'local_planets.tre').read_bytes(), theirs)
        code, out = self.uninstall(self.v1, c)
        self.assertEqual(code, 0, out)
        self.assertEqual((c / 'local_planets.tre').read_bytes(), theirs)

    def test_upgrade_then_downgrade(self):
        c = self.client('upgrade')
        self.assertEqual(self.install(self.v1, c)[0], 0)
        code, out = self.install(self.v2, c)
        self.assertEqual(code, 0, out)
        self.assertEqual(sha(c / 'local_planets.tre'), sha(self.v2 / 'local_planets.tre'))
        self.assertEqual(sha(c / 'local_planets-patch' / 'backup' / '2026.10.16.1' / 'local_planets.tre'), sha(self.v1 / 'local_planets.tre'))
        state = json.loads((c / 'local_planets-patch' / 'state.json').read_text())
        self.assertEqual((state['version'], state['previous']), ('2026.10.17.1', '2026.10.16.1'))
        code, out = self.install(self.v1, c)
        self.assertEqual(code, 6, out)
        self.assertEqual(sha(c / 'local_planets.tre'), sha(self.v2 / 'local_planets.tre'))
        code, out = self.install(self.v1, c, '-AllowDowngrade')
        self.assertEqual(code, 0, out)
        self.assertEqual(sha(c / 'local_planets.tre'), sha(self.v1 / 'local_planets.tre'))
        code, out = ps(self.v1 / 'Install-ClientPatch.ps1', '-ClientDir', c, '-Status')
        self.assertIn('version 2026.10.16.1', out)
        self.assertIn('(OK)', out)
        self.assertEqual(self.uninstall(self.v1, c)[0], 0)
        self.assertFalse((c / 'local_planets.tre').exists())

    def test_refusals_change_nothing(self):
        # not a client folder
        d = self.tmp / 'friends' / 'documents'
        d.mkdir(parents=True)
        (d / 'swgemu.cfg').write_text('x')
        code, out = self.install(self.v1, d)
        self.assertEqual(code, 2, out)
        self.assertEqual(sorted(p.name for p in d.iterdir()), ['swgemu.cfg'])
        # missing MTG archives
        c = self.client('no-mtg', mtg_files=False)
        before = sorted(p.name for p in c.iterdir())
        code, out = self.install(self.v1, c)
        self.assertEqual(code, 3, out)
        self.assertIn('mtg_patch_023.tre (missing)', out)
        self.assertEqual(sorted(p.name for p in c.iterdir()), before)
        # MTG archive with other contents: size check passes, -DeepCheck catches it
        c = self.client('other-mtg')
        (c / 'mtg_patch_016.tre').write_bytes(b'EERT mtg ' + b'X' * len(b'mtg_patch_016.tre' * 10))
        code, out = self.install(self.v1, c, '-DeepCheck')
        self.assertEqual(code, 3, out)
        self.assertIn('different contents', out)
        # damaged kit
        broken = self.tmp / 'kits' / 'broken'
        shutil.copytree(self.v1, broken)
        data = bytearray((broken / 'local_planets.tre').read_bytes())
        data[-1] ^= 1
        (broken / 'local_planets.tre').write_bytes(bytes(data))
        c = self.client('damaged-kit')
        code, out = self.install(broken, c)
        self.assertEqual(code, 4, out)
        self.assertFalse((c / 'local_planets.tre').exists())

    def test_running_client_refused(self):
        c = self.client('running')
        ping = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32' / 'PING.EXE'
        shutil.copyfile(ping, c / 'SWGEmu.exe')
        p = subprocess.Popen([str(c / 'SWGEmu.exe'), '-n', '30', '127.0.0.1'], stdout=subprocess.DEVNULL)
        try:
            time.sleep(0.5)
            code, out = self.install(self.v1, c)
            self.assertEqual(code, 5, out)
            self.assertFalse((c / 'local_planets.tre').exists())
        finally:
            p.kill()
            p.wait()


if __name__ == '__main__':
    unittest.main()
