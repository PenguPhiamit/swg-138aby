"""Read-only C46 probe. Called by Windows discord_feed.py through WSL as swgemu.

No service/start/stop: run python3 watchdog_probe.py for an incremental numeric cursor.
Never emits log text. Missing/unreadable log exits nonzero; caller preserves its cursor.
"""
import argparse
import json
from pathlib import Path


def probe(path, offset=0, file_id=''):
    try:
        st = path.stat()
    except FileNotFoundError:
        return {'file_id': '0:0', 'offset': 0, 'hits': 0}
    ident = f'{st.st_dev}:{st.st_ino}'
    # Initial read establishes a baseline. On rotation, scan the new file for new events.
    baseline = not file_id
    start = st.st_size if baseline else offset if ident == file_id and offset <= st.st_size else 0
    with path.open('rb') as stream:
        stream.seek(start)
        chunk = stream.read(1 << 20)
    end = chunk.rfind(b'\n') + 1
    hits = sum(b'botpop despawn' in line.lower() for line in chunk[:end].splitlines())
    return {'file_id': ident, 'offset': start + end, 'hits': hits}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offset', type=int, default=0)
    parser.add_argument('--file-id', default='')
    args = parser.parse_args()
    try:
        print(json.dumps(probe(Path('/var/tmp/swg-bots/watchdog.log'), max(0, args.offset), args.file_id)))
        return 0
    except OSError:
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
