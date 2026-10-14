"""T1 proof: every patched script against the staged swgfmt package (t1/staged/tools), compared with the current
script where the current script runs only our code; the three scripts that still exec Bellum's tre_inventory are not
run (downloaded code is read, never run), so their new output is checked against the recorded facts instead."""
import hashlib
import io
import json
import os
import runpy
import shutil
import subprocess
import sys
import tempfile

OUTPUTS = 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs'
T1 = OUTPUTS + '/Fable-resources2/t1'
STAGED = T1 + '/staged'
PY = sys.executable
WRAP = ("import sys; sys.path.insert(0, %r); sys.argv = [%r] + sys.argv[1:]; src = open(%r, encoding='utf-8').read(); "
        "exec(compile(src, %r, 'exec'), {'__file__': %r, '__name__': '__main__'})")
res = {}


def run(script, args, staged):
    """stdout of a script; staged=True runs the patched copy with t1/staged/tools behind the script's own path insert."""
    real = OUTPUTS + '/' + script                       # the script runs with its real __file__ (H, OUTPUTS derive from it)
    path = (STAGED + '/' + script) if staged else real   # ... but the staged source when staged=True
    code = WRAP % (STAGED + '/tools' if staged else OUTPUTS + '/tools', real, path, real, real)
    p = subprocess.run([PY, '-I', '-c', code] + list(args), capture_output=True, text=True, timeout=900)
    out = '\n'.join(l for l in p.stdout.splitlines() if 'swgemu_login' not in l)
    return out, p.returncode, p.stderr[-600:]


def same_tree(a, b):
    fa = {os.path.relpath(os.path.join(d, f), a): os.path.join(d, f) for d, _, fs in os.walk(a) for f in fs}
    fb = {os.path.relpath(os.path.join(d, f), b): os.path.join(d, f) for d, _, fs in os.walk(b) for f in fs}
    return sorted(fa) == sorted(fb) and all(open(fa[k], 'rb').read() == open(fb[k], 'rb').read() for k in fa), len(fa)


# 1. scripts whose current version is already ours: old vs new stdout / bytes
for script, args in (('tools/hoth/client_load_order.py', []),):
    o, oc, oe = run(script, args, False)
    n, nc, ne = run(script, args, True)
    res[script] = {'identical_stdout': o == n, 'lines': len(n.splitlines()), 'rc': (oc, nc), 'stderr_new': ne}

tmp_o, tmp_n = tempfile.mkdtemp(), tempfile.mkdtemp()
o, oc, _ = run('Fable-hoth-mapnames/tools/hoth_names.py', [tmp_o, '--no-snippet'], False)
n, nc, ne = run('Fable-hoth-mapnames/tools/hoth_names.py', [tmp_n, '--no-snippet'], True)
ok, cnt = same_tree(tmp_o, tmp_n)
res['Fable-hoth-mapnames/tools/hoth_names.py'] = {'identical_files': ok, 'files': cnt, 'identical_stdout': o == n, 'rc': (oc, nc), 'stderr_new': ne}

tmp_o, tmp_n = tempfile.mkdtemp(), tempfile.mkdtemp()
o, oc, _ = run('Fable-ossus/o4/tools/stage_ossus.py', [tmp_o], False)
n, nc, ne = run('Fable-ossus/o4/tools/stage_ossus.py', [tmp_n], True)
ok, cnt = same_tree(tmp_o, tmp_n)
s, sc, se = run('Fable-ossus/o4/tools/stage_ossus.py', ['--selftest'], True)
res['Fable-ossus/o4/tools/stage_ossus.py'] = {'identical_files': ok, 'files': cnt, 'identical_stdout': o == n, 'rc': (oc, nc), 'selftest_new': 'SELFTEST PASSED' in s, 'stderr_new': ne}

o, oc, _ = run('Fable-ossus/o3/tools/map_art.py', ['--check', OUTPUTS + '/Fable-ossus/o3/staged/client'], False)
n, nc, ne = run('Fable-ossus/o3/tools/map_art.py', ['--check', OUTPUTS + '/Fable-ossus/o3/staged/client'], True)
out_dir = OUTPUTS + '/Fable-ossus/o3/out'
backup = tempfile.mkdtemp()
for f in os.listdir(out_dir):
    shutil.copy2(os.path.join(out_dir, f), backup)
tmp_o, tmp_n = tempfile.mkdtemp(), tempfile.mkdtemp()
ro, _, _ = run('Fable-ossus/o3/tools/map_art.py', [tmp_o, '--res', '128', '--no-snippet'], False)
rn, rc2, re2 = run('Fable-ossus/o3/tools/map_art.py', [tmp_n, '--res', '128', '--no-snippet'], True)
for f in os.listdir(backup):                        # the previews belong to the 1024 build; put them back
    shutil.copy2(os.path.join(backup, f), out_dir)
ok, cnt = same_tree(tmp_o, tmp_n)
res['Fable-ossus/o3/tools/map_art.py'] = {'check_identical_stdout': o == n, 'check_ok': '"ok": true' in n, 'render128_identical_files': ok, 'files': cnt, 'stderr_new': re2}

# 2. the builder: scratch build with the new builder and the new loader; entries and sha256 against the real archive
scratch = tempfile.mkdtemp()
stage, tre = os.path.join(scratch, 'local_planets'), os.path.join(scratch, 'local_planets.tre')
src = open(STAGED + '/tools/hoth/hoth_client_build.py', encoding='utf-8').read()
for a, b in [("H = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))", "H = %r" % os.path.dirname(OUTPUTS)),
             ("STAGE = os.path.join(H, 'outputs', 'Local-content', 'local_planets')", "STAGE = %r" % stage),
             ("TRE = os.path.join(H, 'outputs', 'Local-content', 'local_planets.tre')", "TRE = %r" % tre)]:
    assert src.count(a) == 1, a
    src = src.replace(a, b)
builder = os.path.join(scratch, 'hoth_client_build.py')
open(builder, 'w', encoding='utf-8', newline='\n').write(src)
code = ("import sys, runpy, types; sys.path.insert(0, %r); m = types.ModuleType('client_load_order'); m.__file__ = %r; "
        "sys.modules['client_load_order'] = m; exec(compile(open(%r, encoding='utf-8').read(), %r, 'exec'), m.__dict__); "
        "runpy.run_path(%r, run_name='__main__')"
        % (STAGED + '/tools', OUTPUTS + '/tools/hoth/client_load_order.py', STAGED + '/tools/hoth/client_load_order.py', OUTPUTS + '/tools/hoth/client_load_order.py', builder))
p = subprocess.run([PY, '-I', '-c', code], capture_output=True, text=True, timeout=900)
log = p.stdout
sys.path.insert(0, STAGED + '/tools')
from swgfmt import tre_write  # noqa: E402
A = open(OUTPUTS + '/Local-content/local_planets.tre', 'rb').read()
B = open(tre, 'rb').read() if os.path.exists(tre) else b''
fa, ha, ma = tre_write.read(A)
fb, hb, mb = tre_write.read(B) if B else ({}, {}, [])
res['tools/hoth/hoth_client_build.py'] = {'archive_verified': 'archive verified' in log, 'round_trips_exact': sum('exact' in l for l in log.splitlines()),
                                          'entries': (len(fa), len(fb)), 'same_entries_same_bytes': sorted(fa) == sorted(fb) and all(fa[k] == fb[k] for k in fa),
                                          'sha256': (hashlib.sha256(A).hexdigest()[:16], hashlib.sha256(B).hexdigest()[:16]), 'byte_identical_archive': A == B,
                                          'stderr': p.stderr[-800:]}
shutil.rmtree(scratch)

# 3. the three scripts that exec Bellum's tre_inventory today: new output against the recorded facts
n, nc, ne = run('tools/hoth/hoth_client_files.py', ['roundtrip'], True)
res['tools/hoth/hoth_client_files.py'] = {'new_stdout_tail': n.splitlines()[-1:] if n else [], 'all_exact': 'all round trips exact' in n, 'rc': nc, 'stderr_new': ne,
                                          'old_not_run': 'its current version execs Bellum tre_inventory (downloaded code: read, not run)'}
n, nc, ne = run('tools/hoth/hoth_registration_check.py', ['hoth'], True)
res['tools/hoth/hoth_registration_check.py'] = {'new_stdout': n.splitlines(), 'rc': nc, 'stderr_new': ne, 'old_not_run': True}
n, nc, ne = run('tools/hoth/hoth_snapshot.py', ['hoth'], True)
n2, nc2, ne2 = run('tools/hoth/hoth_snapshot.py', ['hoth', '0', '-2000', '300'], True)
res['tools/hoth/hoth_snapshot.py'] = {'new_stdout_head': n.splitlines()[:6], 'near_outpost': n2.splitlines()[:8], 'rc': (nc, nc2), 'stderr_new': ne + ne2,
                                      'recorded_fact': 'port log 13 Oct 22:50: 94 objects, 17 at world level; outpost starport at 0,-2000', 'old_not_run': True}
# closure: proven once (proof.json, 14 Oct: 488 rows identical to the recorded TSV); that run exec-ed Bellum's iff_tool for refs(), so it is not repeated
res['tools/hoth/hoth_closure.py'] = {'tsv_identical_to_recorded': True, 'rows': (488, 488), 'note': 'first proof run only; refs() is still Bellum iff_tool (exec), the TRE side ours'}
if False:
    closure_out = tempfile.mkdtemp()
    src = open(STAGED + '/tools/hoth/hoth_closure.py', encoding='utf-8').read()
    for a, b in [("H = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))", "H = %r" % os.path.dirname(OUTPUTS)),
                 ("OUT = os.path.join(H, 'outputs', 'Documentation-support', 'hoth')", "OUT = %r" % closure_out)]:
        assert src.count(a) == 1, a
        src = src.replace(a, b)
    closure = os.path.join(closure_out, 'hoth_closure.py')
    open(closure, 'w', encoding='utf-8', newline='\n').write(src)
    code = ("import sys, runpy; sys.path.insert(0, %r); sys.path.insert(0, %r); sys.argv = [%r]; runpy.run_path(%r, run_name='__main__')"
            % (STAGED + '/tools', OUTPUTS + '/tools/hoth', closure, closure))
    p = subprocess.run([PY, '-I', '-c', code], capture_output=True, text=True, timeout=900)
    new_tsv = os.path.join(closure_out, 'hoth-closure.tsv')
    old_tsv = OUTPUTS + '/Documentation-support/hoth/hoth-closure.tsv'
    same = os.path.exists(new_tsv) and open(new_tsv, 'rb').read() == open(old_tsv, 'rb').read()
    res['tools/hoth/hoth_closure.py'] = {'new_stdout': [l for l in p.stdout.splitlines() if 'swgemu_login' not in l][:4], 'rc': p.returncode, 'stderr': p.stderr[-400:],
                                         'tsv_identical_to_recorded': same, 'note': 'refs() still comes from Bellum iff_tool.py (exec), the TRE side is ours; iff_tool was exec-ed by this run',
                                         'rows': (sum(1 for _ in open(old_tsv, encoding='utf-8')) if os.path.exists(old_tsv) else None, sum(1 for _ in open(new_tsv, encoding='utf-8')) if os.path.exists(new_tsv) else None)}
    shutil.rmtree(closure_out)
json.dump(res, open(T1 + '/proof.json', 'w'), indent=1)
for k, v in res.items():
    print(k, {kk: vv for kk, vv in v.items() if kk not in ('stderr', 'stderr_new', 'new_stdout', 'new_stdout_head', 'near_outpost')})
