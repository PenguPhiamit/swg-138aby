"""Serve the MTG archives to friends over Tailscale; the friend installer downloads the ones a friend is missing.

    python -I mtg-share.py              this PC's Tailscale IPv4, port 43480 ("Share MTG files.cmd" runs this)
    python -I mtg-share.py --verify     also check every file's sha256 first (reads about 5 GB)
    python -I mtg-share.py --bind 127.0.0.1 --port 43499 --dir <folder> --manifest <kit manifest.json>   (tests)

Serves only the files the client patch kit's manifest lists under "requires", by exact name, from
Community-content/MTG-assets. GET and HEAD only, and only to Tailscale (100.64.0.0/10) or loopback addresses.
Nothing else on this PC is reachable through it. Ctrl+C stops it.
"""
import argparse, hashlib, http.server, ipaddress, json, shutil, subprocess, sys, time, urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
TAILNET = ipaddress.ip_network('100.64.0.0/10')
TAILSCALE = Path(r'C:\Program Files\Tailscale\tailscale.exe')


def default_manifest():
    settings = json.loads((HERE / 'owner-settings.json').read_text())
    kit = Path(settings['KitDir'])
    return (kit if kit.is_absolute() else HERE / kit) / 'manifest.json'


def tailscale_ip():
    out = subprocess.run([str(TAILSCALE), 'ip', '-4'], capture_output=True, text=True, timeout=15)
    ip = out.stdout.strip().splitlines()[0] if out.returncode == 0 and out.stdout.strip() else ''
    if not ip or ipaddress.ip_address(ip) not in TAILNET:
        sys.exit('STOPPED: Tailscale is not connected on this PC, so there is no address to share on.')
    return ip


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        while chunk := f.read(8 * 1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def load_files(folder, manifest, verify):
    files, bad = {}, []
    for r in json.loads(Path(manifest).read_text())['requires']:
        p = Path(folder) / r['file']
        if not p.is_file():
            bad.append(f"{r['file']} (missing)")
        elif p.stat().st_size != r['size']:
            bad.append(f"{r['file']} (size {p.stat().st_size}, the kit expects {r['size']})")
        elif verify and sha256(p) != r['sha256']:
            bad.append(f"{r['file']} (sha256 differs from the kit's)")
        else:
            files[r['file']] = (p, r['size'])
    if bad:
        sys.exit('STOPPED: these files in ' + str(folder) + ' do not match the kit:\n  ' + '\n  '.join(bad))
    return files


class Handler(http.server.BaseHTTPRequestHandler):
    server_version = 'mtg-share'
    sys_version = ''
    files = {}

    def allowed_client(self):
        ip = ipaddress.ip_address(self.client_address[0])
        return ip in TAILNET or ip.is_loopback

    def send(self, body_too):
        if not self.allowed_client():
            self.send_error(403)
            return
        name = urllib.parse.unquote(urllib.parse.urlsplit(self.path).path).lstrip('/')
        entry = self.files.get(name)
        if entry is None:
            self.send_error(404)
            return
        path, size = entry
        self.send_response(200)
        self.send_header('Content-Type', 'application/octet-stream')
        self.send_header('Content-Length', str(size))
        self.end_headers()
        if not body_too:
            return
        start = time.time()
        try:
            with path.open('rb') as f:
                shutil.copyfileobj(f, self.wfile, 1024 * 1024)
            mb = size / 2**20
            print(f"{time.strftime('%I:%M %p').lstrip('0')}  {self.client_address[0]}  {name}  {mb:,.0f} MB in {time.time() - start:,.0f} s", flush=True)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            print(f"{time.strftime('%I:%M %p').lstrip('0')}  {self.client_address[0]}  {name}  stopped part way (the friend cancelled or lost the connection)", flush=True)

    def do_GET(self):
        self.send(True)

    def do_HEAD(self):
        self.send(False)

    def log_message(self, *args):
        pass


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--bind', help="address to listen on (default: this PC's Tailscale IPv4)")
    ap.add_argument('--port', type=int, default=43480)
    ap.add_argument('--dir', default=str(HERE.parent.parent / 'Community-content' / 'MTG-assets'))
    ap.add_argument('--manifest', help='the client patch kit manifest (default: from owner-settings.json KitDir)')
    ap.add_argument('--verify', action='store_true', help="check every file's sha256 before serving")
    a = ap.parse_args()
    Handler.files = load_files(a.dir, a.manifest or default_manifest(), a.verify)
    bind = a.bind or tailscale_ip()
    server = http.server.ThreadingHTTPServer((bind, a.port), Handler)
    server.daemon_threads = True
    total = sum(size for _, size in Handler.files.values()) / 2**30
    print(f"Sharing {len(Handler.files)} MTG archives ({total:.1f} GB) at http://{bind}:{a.port}/ with Tailscale devices only.")
    print('Leave this window open while a friend runs Setup. Close it (or Ctrl+C) to stop sharing.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
