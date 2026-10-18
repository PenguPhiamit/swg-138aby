"""History-wide pre-push scan of the filtered export (Claude, 18 Oct 2026). Inside Debian, as root:

    python3 history_scan.py /mnt/c/Users/Pengw/AppData/Local/Temp/h-github-export.git

prepush_scan.py checks the files git tracks today; GitHub gets every version of every file. This reads every blob
reachable in the export (the repository that is actually pushed) and every commit's author and committer, and looks for:
  * the real secret values prepush_scan.py collects, the owner's email, and its secret-looking patterns;
  * Discord webhook URLs, fal keys, bearer tokens and Slack tokens;
  * public IPv4 addresses (private and loopback ranges are skipped; version numbers can look like one);
  * SOE game data by file extension in any version, and blobs over 50 MB (GitHub refuses files over 100 MB).
It prints paths and short labels; a secret value is never printed. Exit code 1 when anything needs a look.
"""
import ipaddress
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prepush_scan as base  # noqa: E402

REPO = sys.argv[1]
GIT = ['git', '-c', 'safe.directory=*', '--git-dir', REPO]
EXTRA = [('Discord webhook', re.compile(r'discord(?:app)?\.com/api/webhooks/\d+/[\w-]{20,}')),
         ('fal key', re.compile(r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}:[0-9a-f]{32}\b')),
         ('bearer token', re.compile(r'(?i)\bbearer\s+[A-Za-z0-9._~+/-]{24,}')),
         ('Slack token', re.compile(r'\bxox[abprs]-[A-Za-z0-9-]{10,}'))]
PATTERNS = [p for p in base.PATTERNS if p[0] != 'password assignment'] + EXTRA
IPV4 = re.compile(r'(?<![\d.])(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?![\d.])')


def public_ip(text):
    try:
        ip = ipaddress.IPv4Address(text)
    except ValueError:
        return False
    return ip.is_global


def main():
    objects = subprocess.run(GIT + ['rev-list', '--objects', '--all'], capture_output=True, check=True).stdout.decode()
    paths = {}
    for line in objects.splitlines():
        sha, _, path = line.partition(' ')
        if path:
            paths.setdefault(sha, path)
    batch = subprocess.run(GIT + ['cat-file', '--batch-check'], input='\n'.join(paths).encode(),
                           capture_output=True, check=True).stdout.decode().splitlines()
    blobs = [(l.split()[0], int(l.split()[2])) for l in batch if l.split()[1] == 'blob']
    values = base.secrets()
    print(f'{len(blobs)} blobs, {sum(s for _, s in blobs) / 2**20:.1f} MB; {len(values)} secret values to look for')
    findings, ips = set(), {}
    proc = subprocess.Popen(GIT + ['cat-file', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    for sha, size in blobs:
        proc.stdin.write(sha.encode() + b'\n')
        proc.stdin.flush()
        proc.stdout.readline()
        data = proc.stdout.read(size + 1)[:-1]
        path = paths[sha]
        if Path(path).suffix.lower() in base.GAME_EXT and path not in base.OURS:
            findings.add((path, 'SOE game data extension'))
        if size > 50 * 2**20:
            findings.add((path, f'blob of {size / 2**20:.0f} MB'))
        if b'\0' in data[:4096]:
            continue
        text = data.decode('utf-8', errors='replace')
        if any(v in text for v in values):
            findings.add((path, 'contains a real secret value'))
        if base.EMAIL and base.EMAIL in text:
            findings.add((path, "the owner's email"))
        for label, rx in PATTERNS:
            if rx.search(text):
                findings.add((path, label))
        for m in IPV4.finditer(text):
            if public_ip(m.group(1)):
                ips.setdefault(m.group(1), set()).add(path)
    proc.stdin.close()
    people = subprocess.run(GIT + ['log', '--all', '--format=%an <%ae>%n%cn <%ce>'], capture_output=True,
                            check=True).stdout.decode().splitlines()
    print('commit identities:', sorted(set(people)))
    if base.EMAIL and any(base.EMAIL in p for p in people):
        findings.add(('(commit metadata)', "the owner's email"))
    for path, what in sorted(findings):
        print(f'  {what}: {path}')
    for ip, where in sorted(ips.items()):
        print(f'  public IPv4 {ip}: {len(where)} files, e.g. {sorted(where)[0]}')
    print('clean' if not findings and not ips else f'{len(findings)} findings, {len(ips)} public IPv4 addresses')
    return 1 if findings or ips else 0


if __name__ == '__main__':
    sys.exit(main())
