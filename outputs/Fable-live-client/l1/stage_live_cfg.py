"""Stage the live-client variant (Fable L1, 14 Oct 2026): l1/staged/SWG-client/local_planets.cfg (new), swgemu.cfg with
one .include line, the optional one-line guard in Play SWG Test Galaxy.cmd, and the diffs; then run the checker on
(a) the client folder as it is and (b) a scratch copy of its cfgs with the staged files in place (archives read from the
real folder). Nothing in SWG-client is touched."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.normpath(os.path.join(HERE, '..', '..'))
CLIENT = os.path.join(OUTPUTS, 'SWG-client')
STAGED = os.path.join(HERE, 'staged')
PATCH = os.path.join(HERE, 'patch')
sys.path.insert(0, HERE)
import live_client_check  # noqa: E402

CRLF = b'\r\n'
SNIPPET = (b'; Hoth and the other new-planet files for this galaxy (local_planets.tre, built by tools/hoth/hoth_client_build.py).' + CRLF +
           b'; Priority 49 is the top level the client loads (maxSearchPriority 50 in swgemu_live.cfg); default_patch.tre shares 49' + CRLF +
           b'; and holds none of these files. Remove this file (and its .include line in swgemu.cfg) to roll back.' + CRLF +
           b'[SharedFile]' + CRLF + b'\tsearchTree_00_49=local_planets.tre' + CRLF)


def stage():
    os.makedirs(os.path.join(STAGED, 'SWG-client'), exist_ok=True)
    os.makedirs(PATCH, exist_ok=True)
    with open(os.path.join(STAGED, 'SWG-client', 'local_planets.cfg'), 'wb') as f:
        f.write(SNIPPET)
    cfg = open(os.path.join(CLIENT, 'swgemu.cfg'), 'rb').read()
    nl = CRLF if CRLF in cfg else b'\n'
    old = b'.include "swgemu_live.cfg"' + nl
    assert cfg.count(old) == 1 and b'local_planets.cfg' not in cfg
    new = cfg.replace(old, old + b'.include "local_planets.cfg"' + nl)
    with open(os.path.join(STAGED, 'SWG-client', 'swgemu.cfg'), 'wb') as f:
        f.write(new)
    cmd = open(os.path.join(OUTPUTS, 'Play SWG Test Galaxy.cmd'), 'rb').read()
    old_line = b'if exist local_planets.tre >> swgemu_login.cfg echo searchTree_00_49=local_planets.tre'
    assert cmd.count(old_line) == 1
    guard = b'if not exist local_planets.cfg if exist local_planets.tre >> swgemu_login.cfg echo searchTree_00_49=local_planets.tre'
    with open(os.path.join(STAGED, 'Play SWG Test Galaxy.cmd'), 'wb') as f:
        f.write(cmd.replace(old_line, guard))
    diffs = {}
    for rel, a, b in (('swgemu.cfg', os.path.join(CLIENT, 'swgemu.cfg'), os.path.join(STAGED, 'SWG-client', 'swgemu.cfg')),
                      ('local_planets.cfg', os.devnull, os.path.join(STAGED, 'SWG-client', 'local_planets.cfg')),
                      ('Play SWG Test Galaxy.cmd', os.path.join(OUTPUTS, 'Play SWG Test Galaxy.cmd'), os.path.join(STAGED, 'Play SWG Test Galaxy.cmd'))):
        label = 'outputs/SWG-client/' + rel if rel.endswith('.cfg') else 'outputs/' + rel
        p = subprocess.run(['diff', '-u', '--label', ('a/' + label) if a != os.devnull else '/dev/null', '--label', 'b/' + label, a, b], capture_output=True)
        out = os.path.join(PATCH, rel.replace(' ', '_') + '.patch')
        with open(out, 'wb') as f:
            f.write(p.stdout)
        diffs[rel] = len(p.stdout.splitlines())
    return diffs


def check_both():
    live = live_client_check.check(CLIENT)
    scratch = tempfile.mkdtemp()
    for f in os.listdir(CLIENT):
        if f.lower().endswith('.cfg'):
            shutil.copy2(os.path.join(CLIENT, f), scratch)
    shutil.copy2(os.path.join(STAGED, 'SWG-client', 'swgemu.cfg'), scratch)
    shutil.copy2(os.path.join(STAGED, 'SWG-client', 'local_planets.cfg'), scratch)
    staged = live_client_check.check(scratch, archives=CLIENT)
    # the test launcher's session login file on top of the staged live cfgs: does the duplicate line matter?
    with open(os.path.join(scratch, 'swgemu_login.cfg'), 'ab') as f:
        f.write(CRLF + b'[SharedFile]' + CRLF + b'searchTree_00_49=local_planets.tre' + CRLF)
    both = live_client_check.check(scratch, archives=CLIENT)
    shutil.rmtree(scratch)
    return live, staged, both


if __name__ == '__main__':
    diffs = stage()
    live, staged, both = check_both()
    summary = {'diff_lines': diffs,
               'client_today': {'verdict': live['verdict'], 'ours_loaded_at': live['ours_loaded_at'], 'archives_loaded': live['archives_loaded'], 'ignored_lines': live['ignored_lines'], 'mtg_loaded': live.get('mtg_loaded')},
               'staged_live_cfg': {'verdict': staged['verdict'], 'ours_loaded_at': staged['ours_loaded_at'], 'archives_loaded': staged['archives_loaded'], 'duplicates': staged['duplicates'], 'mtg_loaded': staged.get('mtg_loaded'), 'cfg_priorities_disagrees': staged['cfg_priorities_disagrees']},
               'staged_plus_test_launcher_line': {'verdict': both['verdict'], 'ours_loaded_at': both['ours_loaded_at'], 'duplicates': both['duplicates']},
               'entries_staged': staged['entries']}
    with open(os.path.join(HERE, 'checker-results.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k != 'entries_staged'}, indent=1))
    print('losing entries in the staged set:', [k for k, v in staged['entries'].items() if v != 'WINS'])
