"""Process check for the SWG project (Windows Python): galaxies, bots, helpers, GPT relay, memory.

    python tools/proc_check.py            report only
    python tools/proc_check.py --clean    also stop known-safe leftovers in WSL (see proc_check_wsl.py)

Writes the newest report to Agent/proc-check.md and keeps a one-line history in Agent/proc-check-history.log.
Windows processes are only reported, never stopped.
"""
import json, subprocess, sys, time
from datetime import datetime
from pathlib import Path

OUTPUTS = Path(__file__).resolve().parents[1]
WSL_HALF = '/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/proc_check_wsl.py'
RELAY_MINUTES = 90  # a codex exec worker running longer than this is probably stuck on an approval


def wsl_half(clean):
    args = ['wsl', '-d', 'Debian', '-u', 'root', '--', 'python3', WSL_HALF] + (['--clean'] if clean else [])
    try:
        run = subprocess.run(args, capture_output=True, text=True, timeout=60)
        return json.loads(run.stdout.strip().splitlines()[-1])
    except Exception as exc:  # WSL down or the script failed: say so instead of crashing
        return {'error': f'WSL check failed: {exc}', 'flags': [], 'cleaned': []}


def windows_half():
    script = ("Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(codex|python|vmmemWSL)' } | "
              "ForEach-Object { [pscustomobject]@{pid=$_.ProcessId; name=$_.Name; mb=[int]($_.WorkingSetSize/1MB); "
              "started=$_.CreationDate.ToString('o'); cmd=[string]$_.CommandLine} } | ConvertTo-Json -Compress")
    try:
        run = subprocess.run(['powershell', '-NoProfile', '-Command', script], capture_output=True, text=True, timeout=60)
        rows = json.loads(run.stdout or '[]')
        return rows if isinstance(rows, list) else [rows]
    except Exception as exc:
        return [{'error': str(exc)}]


def main():
    clean = '--clean' in sys.argv
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    print('Checking the galaxies, bots, helpers and memory (takes about 20 seconds)...', flush=True)
    now = datetime.now()
    linux, windows = wsl_half(clean), windows_half()
    flags = [f.get('what', '') + (f" ({f['fifo']})" if f.get('fifo') else '') for f in linux.get('flags', [])]
    if linux.get('error'):
        flags.append(linux['error'])

    workers = []
    for row in windows:
        # Relay workers are "codex exec --approve-for-me ..." (gpt_relay.ps1); the app's own "exec-server" is not one.
        if row.get('name', '').startswith('codex') and ' exec ' in row.get('cmd', '') + ' ' and '--approve-for-me' in row.get('cmd', ''):
            minutes = (now.astimezone() - datetime.fromisoformat(row['started'])).total_seconds() / 60
            workers.append(f"pid {row['pid']}, {minutes:.0f} min")
            if minutes > RELAY_MINUTES:
                flags.append(f"GPT relay worker pid {row['pid']} running {minutes:.0f} min (waiting on an approval?)")
    vmmem = next((r['mb'] for r in windows if r.get('name') == 'vmmemWSL'), None)

    queue = OUTPUTS / 'Agent' / 'gpt-queue.json'
    tasks = json.loads(queue.read_text(encoding='utf-8')).get('tasks', []) if queue.exists() else []
    states = {}
    for task in tasks:
        states.setdefault(task.get('status'), []).append(task.get('id'))
    if states.get('running') and not workers:
        flags.append(f"queue says running ({', '.join(states['running'])}) but no codex exec worker is alive")

    servers = linux.get('servers', [])
    mem = linux.get('memory_mb', {})
    lines = [f'# Process check, {now:%Y-%m-%d %H:%M}', '',
             '**' + (f'{len(flags)} thing(s) need a look' if flags else 'All clear') + '**' +
             (f" · cleaned {len(linux.get('cleaned', []))}" if clean else ''), '']
    lines += [f'- ⚠ {f}' for f in flags]
    lines += ['', '| What | State |', '|---|---|',
              f"| Live galaxy (swg-local) | {linux.get('live_galaxy', '?')} |",
              '| Server processes | ' + ('; '.join(f"{s['which']} pid {s['pid']}, {s['minutes']:.0f} min, {s['rss_mb']} MB" for s in servers) or 'none') + ' |',
              f"| Bots logged in | {len(linux.get('bots', []))}: {', '.join(linux.get('bots', [])) or '-'} |",
              f"| Squad run | {linux.get('squad_run', 'none active')} |",
              f"| GPT relay workers | {', '.join(workers) or 'none'} |",
              '| GPT queue | ' + (', '.join(f'{k}: {len(v)}' for k, v in states.items()) or 'empty') + ' |',
              f"| MCP servers (swg-agent) | {linux.get('mcp_servers', '?')} |",
              f"| /tmp (RAM disk) | {linux.get('tmp_used_pct', '?')}% used |",
              f"| Memory (WSL) | {mem.get('available', '?')} MB free of {mem.get('total', '?')}, swap used {mem.get('swap_used', '?')} MB"
              + (f'; vmmemWSL {vmmem} MB' if vmmem else '') + ' |', '']
    for item in linux.get('cleaned', []):
        lines.append(f"- cleaned: {item.get('what')} (pid {item.get('pid')})")
    report = '\n'.join(lines) + '\n'
    (OUTPUTS / 'Agent' / 'proc-check.md').write_text(report, encoding='utf-8')
    with (OUTPUTS / 'Agent' / 'proc-check-history.log').open('a', encoding='utf-8') as log:
        log.write(f"{now:%Y-%m-%d %H:%M} flags={len(flags)} bots={len(linux.get('bots', []))} servers={len(servers)} "
                  f"free_mb={mem.get('available', '?')} cleaned={len(linux.get('cleaned', []))}" +
                  (' | ' + ' / '.join(flags)[:300] if flags else '') + '\n')
    print(report)
    return 1 if flags else 0


if __name__ == '__main__':
    sys.exit(main())
