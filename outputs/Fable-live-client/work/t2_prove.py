"""T2: run the staged hoth_closure.py (asset_refs from the staged file, registered as swgfmt.asset_refs) with OUT redirected; compare the TSV."""
import importlib.util, os, subprocess, sys, tempfile, json
R = 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs'
T2 = R + '/Fable-live-client/t2'
out = tempfile.mkdtemp()
src = open(T2 + '/staged/tools/hoth/hoth_closure.py', encoding='utf-8').read()
real = R + '/tools/hoth/hoth_closure.py'
a = "OUT = os.path.join(H, 'outputs', 'Documentation-support', 'hoth')"
assert src.count(a) == 1
src = src.replace(a, 'OUT = %r' % out)
code = ("import sys, importlib.util; sys.path.insert(0, %r); import swgfmt; "
        "spec = importlib.util.spec_from_file_location('swgfmt.asset_refs', %r); m = importlib.util.module_from_spec(spec); "
        "sys.modules['swgfmt.asset_refs'] = m; spec.loader.exec_module(m); sys.argv = [%r]; "
        "exec(compile(%r, %r, 'exec'), {'__file__': %r, '__name__': '__main__'})"
        % (R + '/tools', T2 + '/staged/tools/swgfmt/asset_refs.py', real, src, real, real))
p = subprocess.run([sys.executable, '-I', '-c', code], capture_output=True, text=True, timeout=1200)
new = os.path.join(out, 'hoth-closure.tsv'); old = R + '/Documentation-support/hoth/hoth-closure.tsv'
same = os.path.exists(new) and open(new, 'rb').read() == open(old, 'rb').read()
res = {'rc': p.returncode, 'stdout': [l for l in p.stdout.splitlines() if 'swgemu_login' not in l][:6], 'stderr': p.stderr[-500:], 'tsv_identical': same}
if os.path.exists(new) and not same:
    a_ = open(old, encoding='utf-8').read().splitlines(); b_ = open(new, encoding='utf-8').read().splitlines()
    res['only_in_recorded'] = sorted(set(a_) - set(b_))[:40]; res['only_in_new'] = sorted(set(b_) - set(a_))[:40]; res['rows'] = (len(a_), len(b_))
json.dump(res, open(T2 + '/proof.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != 'stderr'}, indent=1)); print(res['stderr'][-300:])
