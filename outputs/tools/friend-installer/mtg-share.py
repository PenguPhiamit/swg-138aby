r"""Serve the MTG archives to friends over Tailscale; the friend installer downloads the ones a friend is missing.

    python -I mtg-share.py              this PC's Tailscale IPv4, port 43480 ("Share MTG files.cmd" runs this)
    python -I mtg-share.py --verify     also check every file's sha256 first (reads about 5 GB)
    python -I mtg-share.py --bind 127.0.0.1 --port 43499 --dir <folder> --manifest <kit manifest.json>   (tests)

Serves only the files the client patch kit's manifest lists under "requires", by exact name, from
Community-content/MTG-assets. For the Fractured Galaxy launcher it also serves:
  /update.json          what the launcher compares against: the server's local_planets.tre (size, sha256, a version
                        from its time), the MTG list, the newest launcher and news.txt
  /local_planets.tre    the archive the server loads (--archive; read-only, through \\wsl.localhost)
  /FracturedGalaxy.exe  build\out\FracturedGalaxy.exe, with its version from FracturedGalaxy.version (build.ps1)
  /addon/<file>         the graphics add-on (owner, 18 Oct: on for everyone): DXVK 3.1.1 (dxvk_d3d9.dll) with the
                        Ossus O15 hook in front of it (d3d9.dll; it bends the light whip and adds the ghostfire haze),
                        from the owner's client, plus O15's default mirage.ini and the client's dxvk.conf. Offered only
                        while the owner's client has exactly that DXVK and a mirage build, so friends get what runs here
                        and whose blade ids match the server's archive.
GET and HEAD only, and only to Tailscale (100.64.0.0/10) or loopback addresses.
Nothing else on this PC is reachable through it. Ctrl+C stops it.
"""
import argparse, hashlib, http.server, ipaddress, json, shutil, subprocess, sys, time, urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
TAILNET = ipaddress.ip_network('100.64.0.0/10')
TAILSCALE = Path(r'C:\Program Files\Tailscale\tailscale.exe')
DXVK_SHA = '265888c31ca78dffa290c39cb7e50bfb02762590e41927906e46fb32f01497fa'   # DXVK 3.1.1 x32 d3d9.dll, official release
ADDON = ('dxvk_d3d9.dll', 'd3d9.dll', 'mirage.ini', 'dxvk.conf')


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


class Live:
    """A file that can change while we serve it (the server's archive, a rebuilt launcher): read whole, hashed once
    per change, so update.json and the download always describe the same bytes."""
    def __init__(self, path):
        self.path, self.key, self.data, self.sha = Path(path), None, b'', ''

    def get(self):
        try:
            st = self.path.stat()
        except OSError:
            return None
        if self.key != (st.st_mtime_ns, st.st_size):
            data = self.path.read_bytes()
            self.key, self.data, self.sha = (st.st_mtime_ns, st.st_size), data, hashlib.sha256(data).hexdigest()
        return self


class Handler(http.server.BaseHTTPRequestHandler):
    server_version = 'mtg-share'
    sys_version = ''
    files = {}
    requires = []
    archive = launcher = None
    launcher_version = news = None
    addon = {}

    @classmethod
    def addon_files(cls):
        got = {n: l.get() for n, l in cls.addon.items()}
        if len(got) != len(ADDON) or not all(got.values()):
            return None
        if got['dxvk_d3d9.dll'].sha != DXVK_SHA or b'mirage.ini' not in got['d3d9.dll'].data:
            return None
        return got

    def update_info(self):
        info = {'format': 1, 'requires': self.requires, 'news': self.news.read_text(encoding='utf-8').strip() if self.news and self.news.is_file() else ''}
        a = self.archive.get() if self.archive else None
        if a:
            info['patch'] = {'file': 'local_planets.tre', 'size': len(a.data), 'sha256': a.sha,
                             'version': time.strftime('%Y.%m.%d.%H%M', time.localtime(a.key[0] / 1e9))}
        l = self.launcher.get() if self.launcher else None
        if l and self.launcher_version and self.launcher_version.is_file():
            info['launcher'] = {'file': 'FracturedGalaxy.exe', 'size': len(l.data), 'sha256': l.sha,
                                'version': self.launcher_version.read_text().strip()}
        ad = self.addon_files()
        if ad:
            info['addon'] = {n: {'file': 'addon/' + n, 'size': len(g.data), 'sha256': g.sha} for n, g in ad.items()}
        return json.dumps(info, indent=1).encode()

    def send_bytes(self, body, body_too, kind='application/octet-stream'):
        self.send_response(200)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        if body_too:
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass

    def allowed_client(self):
        ip = ipaddress.ip_address(self.client_address[0])
        return ip in TAILNET or ip.is_loopback

    def send(self, body_too):
        if not self.allowed_client():
            self.send_error(403)
            return
        name = urllib.parse.unquote(urllib.parse.urlsplit(self.path).path).lstrip('/')
        live = {'local_planets.tre': self.archive, 'FracturedGalaxy.exe': self.launcher}.get(name)
        if name == 'update.json':
            self.send_bytes(self.update_info(), body_too, 'application/json')
            return
        if name.startswith('addon/'):
            ad = self.addon_files()
            got = ad.get(name[6:]) if ad else None
            if got is None:
                self.send_error(404)
                return
            self.send_bytes(got.data, body_too)
            if body_too:
                print(f"{time.strftime('%I:%M %p').lstrip('0')}  {self.client_address[0]}  {name}  (graphics add-on)", flush=True)
            return
        if live is not None:
            got = live.get()
            if got is None:
                self.send_error(404)
                return
            self.send_bytes(got.data, body_too)
            if body_too:
                print(f"{time.strftime('%I:%M %p').lstrip('0')}  {self.client_address[0]}  {name}  (launcher update)", flush=True)
            return
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
    ap.add_argument('--archive', default=r'\\wsl.localhost\Debian\opt\swg\tre\local_planets.tre',
                    help="the local_planets.tre the server loads (read-only)")
    ap.add_argument('--launcher', default=str(HERE / 'build' / 'out' / 'FracturedGalaxy.exe'))
    ap.add_argument('--news', default=str(HERE / 'news.txt'))
    ap.add_argument('--addon-client', default=str(HERE.parent.parent / 'SWG-client'),
                    help="the client folder the add-on's d3d9.dll, dxvk_d3d9.dll and dxvk.conf come from")
    ap.add_argument('--addon-ini', default=str(HERE.parent.parent / 'Fable-ossus' / 'o15-mirage' / 'mirage.ini'))
    a = ap.parse_args()
    manifest = a.manifest or default_manifest()
    Handler.files = load_files(a.dir, manifest, a.verify)
    Handler.requires = [{k: r[k] for k in ('file', 'size', 'sha256')} for r in json.loads(Path(manifest).read_text())['requires']]
    Handler.archive, Handler.launcher, Handler.news = Live(a.archive), Live(a.launcher), Path(a.news)
    Handler.launcher_version = Path(a.launcher).with_suffix('.version')
    Handler.addon = {n: Live(Path(a.addon_client) / n) for n in ADDON if n != 'mirage.ini'}
    Handler.addon['mirage.ini'] = Live(a.addon_ini)
    if Handler.archive.get() is None:
        print(f"Note: {a.archive} can't be read (is WSL running?); launchers will be told there's no patch to compare.")
    if Handler.addon_files() is None:
        print("Note: the graphics add-on is not offered (the client's dxvk_d3d9.dll isn't DXVK 3.1.1, or d3d9.dll isn't the hook).")
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
