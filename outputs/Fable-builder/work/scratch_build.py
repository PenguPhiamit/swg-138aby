"""Run the patched builder in a scratch folder (its own STAGE/TRE), then compare with Claude's staging and archive."""
import hashlib, importlib.util, io, os, runpy, shutil, sys, tempfile
from contextlib import redirect_stdout
R = 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs'
H = 'C:/Users/Pengw/Documents/Codex/2026-10-13/h'
scratch = tempfile.mkdtemp()
stage, tre = os.path.join(scratch, 'local_planets'), os.path.join(scratch, 'local_planets.tre')
src = open(R + '/Fable-builder/patch/hoth_client_build.py', encoding='utf-8').read()
reps = [("H = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))", "H = %r" % H),
        ("STAGE = os.path.join(H, 'outputs', 'Local-content', 'local_planets')", "STAGE = %r" % stage),
        ("TRE = os.path.join(H, 'outputs', 'Local-content', 'local_planets.tre')", "TRE = %r" % tre)]
for a, b in reps:
    assert src.count(a) == 1, a
    src = src.replace(a, b)
builder = os.path.join(scratch, 'hoth_client_build.py')
open(builder, 'w', encoding='utf-8', newline='\n').write(src)
# the patched loader, registered before anything imports client_load_order
spec = importlib.util.spec_from_file_location('client_load_order', R + '/Fable-builder/patch/client_load_order.py')
mod = importlib.util.module_from_spec(spec); sys.modules['client_load_order'] = mod; spec.loader.exec_module(mod)
assert not hasattr(mod, 'BELLUM')
buf = io.StringIO()
with redirect_stdout(buf):
    try:
        runpy.run_path(builder, run_name='__main__')
    except SystemExit as e:
        print('exit', e.code)
log = buf.getvalue()
open(R + '/Fable-builder/work/scratch_build.log', 'w', encoding='utf-8').write(log)
print('builder log lines:', len(log.splitlines()), '| verified:', 'archive verified' in log, '| exit:', [l for l in log.splitlines() if l.startswith('exit')])
print('round trips:', sum('exact' in l for l in log.splitlines()), 'exact,', sum('DIFFERS' in l for l in log.splitlines()), 'DIFFERS')
# compare staging folders
ref = R + '/Local-content/local_planets'
def files(d): return sorted(os.path.relpath(os.path.join(a, f), d).replace(os.sep, '/') for a, _, fs in os.walk(d) for f in fs)
fa, fb = files(ref), files(stage)
print('staging file list identical:', fa == fb, len(fa), 'files')
diff = [n for n in fa if open(os.path.join(ref, n), 'rb').read() != open(os.path.join(stage, n), 'rb').read()]
print('staged files that differ:', diff)
# compare archives
sys.path.insert(0, R + '/Fable-builder/tools'); import tre_write
A = open(R + '/Local-content/local_planets.tre', 'rb').read(); B = open(tre, 'rb').read()
fa_, ha, ma = tre_write.read(A); fb_, hb, mb = tre_write.read(B)
print('archive entries before:', len(fa_), 'after:', len(fb_), 'same names:', sorted(fa_) == sorted(fb_))
print('entries whose bytes change:', [n for n in sorted(fa_) if fa_[n] != fb_[n]])
print('header fields equal:', {k: (ha[k], hb[k]) for k in ha if ha[k] != hb[k]} or 'all')
print('sha256 before %s after %s' % (hashlib.sha256(A).hexdigest()[:16], hashlib.sha256(B).hexdigest()[:16]))
print('tail table: before = md5 of unpacked data (tre_pack), after = md5 of stored bytes (stock rule)')
for n in [x for x in sorted(fa_) if fa_[x] != fb_[x]]:
    a, b = fa_[n], fb_[n]
    print('  %s: %d -> %d bytes; CRLF-only after: %s; bare CR before/after: %d/%d' % (n, len(a), len(b), b.count(b'\r\n') == b.count(b'\n'), a.count(b'\r\r\n'), b.count(b'\r\r\n')))
print('scratch:', scratch)
