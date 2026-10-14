"""Index the owner's SWG disc archives (SOE originals, extracted read-only by Claude) by file name.

Runs inside Debian as swgemu, because the disc extraction lives under /opt/swg:
  python3 -I /mnt/c/.../Fable-backport/tools/disc_index.py [--hash LISTFILE]

Reads only archive indexes (names) with Bellum's TRE reader (tre_inventory.py, read as text and exec'd, the
same way tools/hoth/client_load_order.py does). With --hash LISTFILE (one object path per line) it also
reads those files from every disc archive that holds them and records sha256 per (path, archive), so a disc
copy can be compared with the MTG copy the client loads. Writes work/disc_index.json. Nothing under /opt/swg
is changed.
"""
import hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
H = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
BELLUM = os.path.join(H, 'work', 'research', 'Miphstoe_BellumGero-Live', 'MMOCoreORB', 'tools', 'newplanets')
DISC = '/opt/swg/disc-extracted/SWG-group/files/SWG'
SHA = '/opt/swg/disc-extracted/SWG-group/tre.sha256'
OUT = os.path.join(HERE, '..', 'work', 'disc_index.json')

with open(os.path.join(BELLUM, 'tre_inventory.py'), encoding='utf-8') as f:
    exec(f.read().split('if __name__')[0])  # defines read_tre and _inflate


def main(argv):
    want = set()
    if argv[:1] == ['--hash'] and len(argv) == 2:
        with open(argv[1], encoding='utf-8') as f:
            want = {line.strip().lower() for line in f if line.strip()}
    if not os.path.exists(SHA):
        print(f'{SHA} missing: extraction not finished; not indexing')
        return 1
    archives = sorted(n for n in os.listdir(DISC) if n.lower().endswith('.tre'))
    index = {}      # lower path -> [archive]
    hashes = {}     # lower path -> {archive: sha256}
    sizes = {}
    for name in archives:
        path = os.path.join(DISC, name)
        try:
            entries = read_tre(path)
        except Exception as exc:
            print(f'{name}: {exc}')
            continue
        sizes[name] = os.path.getsize(path)
        for e in entries:
            key = e['name'].lower()
            if not (key.startswith('object/') or key.startswith('misc/') or key.startswith('string/')):
                continue
            index.setdefault(key, []).append(name)
            if key in want:
                with open(path, 'rb') as f:
                    f.seek(e['offset'])
                    blob = f.read(e['comp_size'] if e['comp'] else e['size'])
                data = _inflate(blob, e['comp'], e['size'])
                hashes.setdefault(key, {})[name] = hashlib.sha256(data).hexdigest()
    with open(SHA, encoding='utf-8', errors='replace') as f:
        sha_lines = sum(1 for _ in f)
    result = {'disc_dir': DISC, 'sha256_file': SHA, 'sha256_lines': sha_lines, 'archives': archives,
              'archive_sizes': sizes, 'files': index, 'hashes': hashes}
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(result, f, indent=0, sort_keys=True)
    print(f'{len(archives)} archives, {len(index)} object/misc/string paths, {len(hashes)} hashed -> {OUT}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
