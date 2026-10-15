"""Pre-push scan of the h repository (Claude, 15 Oct 2026). Inside Debian, as root:

    python3 prepush_scan.py

Before anything of h goes to a private GitHub repository (owner, 15 Oct: to share with Sagiroth), this checks every
file git tracks for:
  * the real secrets: the database settings in the live config-local.lua, passwords in outputs/SWG-login.txt, and
    every string value in the agent and bot account files under /opt/swg/agent (values longer than 5 characters);
  * secret-looking text: private keys, API tokens, 'password = ...' lines;
  * the owner's email address;
  * SOE game data (archives and extracted client files), which must not leave the PC;
  * files git tracks that .gitignore now excludes.
It prints file names and line numbers only, never a secret value. Exit code 1 when anything needs a look.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

H = Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h')
CONFIG = Path('/opt/swg/Core3/MMOCoreORB/bin/conf/config-local.lua')
LOGIN = H / 'outputs' / 'SWG-login.txt'
AGENT = Path('/opt/swg/agent')
EMAIL = '[email removed]'
GAME_EXT = {'.tre', '.toc', '.iff', '.stf', '.msh', '.mgn', '.lmg', '.lod', '.sat', '.apt', '.ans', '.lat', '.ash', '.dds',
            '.sht', '.trn', '.ws', '.snd', '.wav', '.mp3', '.cdf', '.flr', '.pob', '.mdmp'}
OURS = {'outputs/Fable-ossus/o2/staged/client/snapshot/ossus.ws', 'outputs/Fable-ossus/o4/staged/client/snapshot/ossus.ws'}  # written by our ws_write.py (87 own placements)
PATTERNS = [('private key', re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----')),
            ('GitHub token', re.compile(r'\bgh[pousr]_[A-Za-z0-9]{30,}')),
            ('API key', re.compile(r'\b(sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,})')),
            ('password assignment', re.compile(r'(?i)\b(pass(word)?|passwd|secret|DBPass|DBSecret)\s*[:=]\s*["\']?[^\s"\'{}<>()]{6,}'))]


def secrets():
    values = set()
    try:
        values.update(re.findall(r'^Core3\.DB(?:Pass|Secret)\s*=\s*"([^"]+)"', CONFIG.read_text(errors='replace'), re.M))
    except OSError:
        print('note: live config-local.lua not readable')
    try:
        values.update(re.findall(r'(?im)^\s*password\s*[:=]\s*(\S+)', LOGIN.read_text(errors='replace')))
    except OSError:
        pass
    for path in AGENT.rglob('*.json'):
        try:
            data = json.loads(path.read_text(errors='replace'))
        except (OSError, ValueError):
            continue
        stack = [data]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, str) and re.search(r'pass|secret|token|key', key, re.I):
                        values.add(value)
                    else:
                        stack.append(value)
            elif isinstance(item, list):
                stack.extend(item)
    return {v for v in values if len(v) > 5}


def main():
    tracked = subprocess.run(['git', '-c', 'safe.directory=*', '-C', str(H), 'ls-files', '-z'], capture_output=True, check=True).stdout.decode().split('\0')
    tracked = [t for t in tracked if t]
    ignored = subprocess.run(['git', '-c', 'safe.directory=*', '-C', str(H), 'ls-files', '-ci', '--exclude-standard', '-z'], capture_output=True).stdout.decode().split('\0')
    values = secrets()
    print(f'{len(tracked)} tracked files; {len(values)} secret values to look for')
    findings = []
    for name in tracked:
        path = H / name
        if Path(name).suffix.lower() in GAME_EXT and name not in OURS:
            findings.append((name, 0, 'SOE game data file'))
        if name.endswith('SWG-login.txt') or name.endswith('agent-account.json'):
            findings.append((name, 0, 'account file is tracked'))
        try:
            data = path.read_bytes()
        except OSError:
            continue
        if b'\0' in data[:4096]:
            continue
        text = data.decode('utf-8', errors='replace')
        for value in values:
            if value in text:
                line = text[:text.index(value)].count('\n') + 1
                findings.append((name, line, 'contains a real secret value'))
        for label, rx in PATTERNS:
            for m in rx.finditer(text):
                line = text[:m.start()].count('\n') + 1
                findings.append((name, line, label))
        if EMAIL in text:
            findings.append((name, text[:text.index(EMAIL)].count('\n') + 1, "the owner's email"))
    for name in [i for i in ignored if i]:
        findings.append((name, 0, 'tracked but now gitignored'))
    for name, line, what in sorted(set(findings)):
        print(f'  {what}: {name}' + (f':{line}' if line else ''))
    print('clean' if not findings else f'{len(set(findings))} findings')
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
