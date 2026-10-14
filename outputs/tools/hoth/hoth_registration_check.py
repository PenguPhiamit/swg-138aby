"""Hoth step 2 pre-check: is Hoth already registered in the client files that list planets?

    python -I tools/hoth/hoth_registration_check.py [planet]      default: hoth

For each file the client uses to know about a planet (names, travel, ticket UI, planet map, CRC tables, music,
environment), find the version that wins in our load order and say whether it mentions the planet. Read-only;
uses our TRE reader (outputs/tools/swgfmt) the same way hoth_closure.py does.
"""
import os, re, sys

H = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
CLIENT = os.path.join(H, 'outputs', 'SWG-client')
sys.path.insert(0, os.path.join(H, 'outputs', 'tools'))
from swgfmt.fmt_tools import read_tre, _inflate, walk_tres  # noqa: E402  (ours)

# What each file is for, and a pattern for the files to look at (internal paths, lower case).
WANTED = [
    ('planet display names', r'^string/en/planet_n\.stf$'),
    ('travel points / routes', r'^datatables/travel/travel\.iff$'),
    ('ticket purchase UI', r'^ui/ui_ticketpurchase\.inc$'),
    ('planetary map UI', r'^ui/ui_planet_map\.inc$'),
    ('planet CRC string table', r'^misc/planet_crc_string_table\.iff$'),
    ('planet-related datatables', r'^datatables/.*planet.*\.iff$'),
    ('per-planet environment / music', r'^(datatables/(music|environment|sky)|misc/).*hoth.*'),
    ('anything else named hoth', r'hoth'),
]


def main(planet):
    winners = {}
    for tre in walk_tres(CLIENT):
        try:
            for entry in read_tre(tre):
                winners[entry['name'].lower()] = (tre, entry)
        except Exception:
            pass

    def data(path):
        tre, entry = winners[path]
        with open(tre, 'rb') as stream:
            stream.seek(entry['offset'])
            blob = stream.read(entry['comp_size'] if entry['comp'] else entry['size'])
        return _inflate(blob, entry['comp'], entry['size'])

    word = planet.encode().lower()
    for label, pattern in WANTED:
        hits = sorted(p for p in winners if re.search(pattern, p))
        if label == 'anything else named hoth':
            folders = {}
            for p in hits:
                folders.setdefault(p.split('/')[0], []).append(p)
            print(f'{label}: {len(hits)} files: ' + ', '.join(f'{k} {len(v)}' for k, v in sorted(folders.items())))
            continue
        if not hits:
            print(f'{label}: no such file in the client')
        for path in hits[:12]:
            body = data(path).lower()
            # .stf strings are UTF-16: look for the planet name both ways
            mention = word in body or word.decode().encode('utf-16-le') in body
            print(f'{label}: {path} [{os.path.basename(winners[path][0])}] -> '
                  + ('mentions ' + planet if mention else 'no ' + planet))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'hoth')
