"""Build and check the client patch kit friends install to play on the owner's server (C57).

    python -I tools/client_patch/client_patch.py build --archive FILE --version 2026.10.16.1 --notes FILE [--out DIR]
    python -I tools/client_patch/client_patch.py verify KIT                  # the kit's files match its manifest
    python -I tools/client_patch/client_patch.py check-server KIT (--server-sha SHA | --server-file FILE)

A kit is one folder (and a zip of it) holding:
    local_planets.tre        our archive (Hoth, Ossus, the playable Hutt and its floater, Nal Hutta), unchanged
    manifest.json            version, size and sha256 of the archive, the cfg block, the MTG archives it needs
    local_planets.cfg        the [SharedFile] block that loads it (the installer writes its own copy)
    RELEASE-NOTES.txt        what changed, from --notes
    Install-ClientPatch.ps1, Uninstall-ClientPatch.ps1, Install.cmd, Uninstall.cmd, README.md (the friends' guide)

The archive is never edited: the kit is a wrapper round the exact file the server loads, so the server's
/opt/swg/tre/local_planets.tre and the client's must have the same sha256 (check-server).
The MTG archives are listed as requirements (name, priority, size, sha256 from the owner's client), not shipped.
Reads the owner's client folder only to learn those. Never installs, uploads or sends anything.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import zipfile

HERE = Path(__file__).resolve().parent
OUTPUTS = HERE.parents[1]
CLIENT = OUTPUTS / 'SWG-client'
GUIDE = OUTPUTS / 'Documentation-support' / 'client-patch-for-friends.md'
sys.path.insert(0, str(OUTPUTS / 'tools'))
sys.path.insert(0, str(OUTPUTS / 'tools' / 'hoth'))

ARCHIVE = 'local_planets.tre'
CFG = 'local_planets.cfg'
PRIORITY = 49                      # the highest the client loads below maxSearchPriority 50 (Play SWG Test Galaxy.cmd)
SCRIPTS = ('Install-ClientPatch.ps1', 'Uninstall-ClientPatch.ps1', 'Install.cmd', 'Uninstall.cmd')
VERSION = re.compile(r'^\d{4}\.\d{1,2}\.\d{1,2}\.\d{1,3}$')   # year.month.day.build: sorts as a System.Version
CRLF = '\r\n'


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(chunk), b''):
            h.update(block)
    return h.hexdigest()


def cfg_block(lines):
    """The cfg text for [(priority, archive)], CRLF like the stock cfg files."""
    out = ['; Loads the owner\'s server content. Written by Install-ClientPatch.ps1; Uninstall-ClientPatch.ps1 removes it.',
           '[SharedFile]']
    out += ['\tsearchTree_00_%d=%s' % (p, name) for p, name in lines]
    return CRLF.join(out) + CRLF


def requirements(client):
    """The MTG archives the owner's client loads: [(priority, name)], read from its cfg chain."""
    import client_load_order as clo
    clo.CLIENT = str(client)
    trees, _, _ = clo.load_order()
    return sorted(((p, n) for p, n in trees if n.lower().startswith('mtg_')), reverse=True)


def build(args):
    if not VERSION.match(args.version):
        sys.exit('version must look like 2026.10.16.1 (year.month.day.build)')
    archive = Path(args.archive)
    data_sha = sha256(archive)
    if args.expect_sha and not data_sha.startswith(args.expect_sha.lower()):
        sys.exit('archive sha256 %s does not start with %s' % (data_sha, args.expect_sha))
    notes = Path(args.notes).read_text(encoding='utf-8').strip()
    out = Path(args.out or OUTPUTS.parent / 'work' / 'client-patch' / args.version)
    if out.exists() and any(out.iterdir()):
        sys.exit('%s exists and is not empty; pick a new version or remove it' % out)
    out.mkdir(parents=True, exist_ok=True)
    client = Path(args.client)
    reqs = []
    for priority, name in requirements(client):
        path = client / name
        reqs.append({'file': name, 'priority': priority, 'size': path.stat().st_size,
                     'sha256': None if args.no_hash_requirements else sha256(path)})
    manifest = {
        'format': 1,
        'name': 'local_planets',
        'version': args.version,
        'archive': {'file': ARCHIVE, 'size': archive.stat().st_size, 'sha256': data_sha, 'priority': PRIORITY},
        'cfg': {'file': CFG, 'include_line': '.include "%s"' % CFG, 'include_in': 'swgemu.cfg'},
        'requires': reqs,
        'server_file': '/opt/swg/tre/local_planets.tre',
        'notes': notes,
        'source': {'path': archive.name},
    }
    shutil.copyfile(archive, out / ARCHIVE)
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    (out / CFG).write_bytes(cfg_block([(PRIORITY, ARCHIVE)]).encode('ascii'))
    (out / 'RELEASE-NOTES.txt').write_bytes(('Version %s%s%s%s' % (args.version, CRLF * 2, notes.replace('\n', CRLF), CRLF)).encode('utf-8'))
    for name in SCRIPTS:
        shutil.copyfile(HERE / name, out / name)
    if GUIDE.exists():
        shutil.copyfile(GUIDE, out / 'README.md')
    problems = verify_kit(out)
    if problems:
        sys.exit('kit does not check: %s' % problems)
    zip_path = out.parent / ('local_planets-%s.zip' % args.version)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(out.iterdir()):
            info = zipfile.ZipInfo('local_planets-%s/%s' % (args.version, f.name), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, f.read_bytes())
    print(json.dumps({'kit': str(out), 'zip': str(zip_path), 'zip_sha256': sha256(zip_path), 'version': args.version,
                      'archive_sha256': data_sha, 'requires': len(reqs)}, indent=2))


def verify_kit(kit):
    """A list of problems with a kit folder (empty when it checks)."""
    kit = Path(kit)
    problems = []
    try:
        m = json.loads((kit / 'manifest.json').read_text(encoding='utf-8'))
    except (OSError, ValueError) as e:
        return ['manifest.json: %s' % e]
    if m.get('format') != 1 or not VERSION.match(str(m.get('version', ''))):
        problems.append('manifest format or version')
    a = kit / ARCHIVE
    if not a.exists():
        problems.append('%s missing' % ARCHIVE)
    elif a.stat().st_size != m['archive']['size'] or sha256(a) != m['archive']['sha256']:
        problems.append('%s does not match the manifest' % ARCHIVE)
    for name in SCRIPTS + ('RELEASE-NOTES.txt', CFG):
        if not (kit / name).exists():
            problems.append('%s missing' % name)
    return problems


def verify(args):
    problems = verify_kit(args.kit)
    print('kit OK' if not problems else '\n'.join(problems))
    return 1 if problems else 0


def check_server(args):
    m = json.loads((Path(args.kit) / 'manifest.json').read_text(encoding='utf-8'))
    want = m['archive']['sha256']
    have = (args.server_sha or sha256(args.server_file)).split()[0].lower()
    same = have == want
    print('%s: kit %s %s, server %s' % ('MATCH' if same else 'MISMATCH', m['version'], want[:12], have[:12]))
    return 0 if same else 1


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build')
    b.add_argument('--archive', required=True, help='the local_planets.tre to ship (the one the server loads)')
    b.add_argument('--version', required=True)
    b.add_argument('--notes', required=True, help='a UTF-8 text file: what changed, in plain words')
    b.add_argument('--out', help='kit folder (default ../work/client-patch/<version>)')
    b.add_argument('--expect-sha', help='refuse unless the archive sha256 starts with this')
    b.add_argument('--client', default=str(CLIENT), help='client folder to read the MTG requirements from')
    b.add_argument('--no-hash-requirements', action='store_true', help='record sizes only (faster; tests)')
    v = sub.add_parser('verify')
    v.add_argument('kit')
    c = sub.add_parser('check-server')
    c.add_argument('kit')
    g = c.add_mutually_exclusive_group(required=True)
    g.add_argument('--server-sha', help='output of: wsl -d Debian -u swgemu -- sha256sum /opt/swg/tre/local_planets.tre')
    g.add_argument('--server-file')
    args = p.parse_args(argv)
    return {'build': build, 'verify': verify, 'check-server': check_server}[args.cmd](args) or 0


if __name__ == '__main__':
    sys.exit(main())
