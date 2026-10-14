#!/usr/bin/env python3
"""WSL half of the process check (run as root by tools/proc_check.py). Prints one JSON object.

Reads /proc only. With --clean it stops two kinds of leftovers, nothing else:
  - input holders ("sleep infinity" keeping a bot or test FIFO open) whose client has exited;
  - Claude scratchpad helper scripts (and their children) running longer than STUCK_MINUTES.
It never touches core3, core3client, mariadb, mcp_server/agentd, VS Code or the live service.
"""
import json, os, signal, subprocess, sys, time

STUCK_MINUTES = 60
HOLDER_MINUTES = 10  # a holder younger than this may belong to a bot that is still logging in
BUSY = ('squad.py setup', 'squad.py run', 'test_galaxy.py start', 'tg_squads', 'bot.py')  # never clean while these run
SCRATCH = '/mnt/c/Users/Pengw/AppData/Local/Temp/claude/'
HZ = os.sysconf('SC_CLK_TCK')
BOOT = time.time() - float(open('/proc/uptime').read().split()[0])


def processes():
    found = []
    for pid in os.listdir('/proc'):
        if not pid.isdigit():
            continue
        try:
            cmd = open(f'/proc/{pid}/cmdline', 'rb').read().replace(b'\0', b' ').decode(errors='replace').strip()
            stat = open(f'/proc/{pid}/stat').read().rsplit(')', 1)[1].split()
            rss = int(open(f'/proc/{pid}/statm').read().split()[1]) * os.sysconf('SC_PAGE_SIZE') >> 20
            fds = []
            for fd in os.listdir(f'/proc/{pid}/fd'):
                try:
                    fds.append(os.readlink(f'/proc/{pid}/fd/{fd}'))
                except OSError:
                    pass
        except (OSError, IndexError):
            continue
        if not cmd:
            continue
        found.append({'pid': int(pid), 'ppid': int(stat[1]), 'cmd': cmd, 'rss_mb': rss, 'fds': fds,
                      'minutes': round((time.time() - BOOT - int(stat[19]) / HZ) / 60, 1)})
    return found


def main():
    clean = '--clean' in sys.argv
    procs = processes()
    by_pid = {p['pid']: p for p in procs}
    out = {'flags': [], 'cleaned': []}

    live = subprocess.run(['systemctl', 'is-active', 'swg-local'], capture_output=True, text=True).stdout.strip()
    out['live_galaxy'] = live
    servers = [p for p in procs if p['cmd'].split(' ')[0].endswith('core3') and 'core3client' not in p['cmd']]
    out['servers'] = [{'pid': p['pid'], 'minutes': p['minutes'], 'rss_mb': p['rss_mb'],
                       'which': 'test' if any('testgalaxy' in f for f in p['fds']) or 'testgalaxy' in os.path.realpath(f"/proc/{p['pid']}/cwd") else 'live'}
                      for p in servers]

    clients = [p for p in procs if 'core3client' in p['cmd']]
    out['bots'] = sorted(p['cmd'].split('--character-firstname ')[-1].split(' ')[0] for p in clients)
    client_fifos = {f for p in clients for f in p['fds'] if f.endswith('/in')}

    busy = sorted({b for p in procs for b in BUSY if b in p['cmd']})
    if busy and clean:
        out['flags'].append({'what': 'cleaning skipped: bots are being set up or run (' + ', '.join(busy) + ')'})
        clean = False

    for p in procs:
        if p['cmd'] != 'sleep infinity' or p['minutes'] < HOLDER_MINUTES:
            continue
        fifos = [f for f in p['fds'] if f.endswith('/in') and f.startswith(('/tmp/', '/var/tmp/'))]
        if fifos and not any(f in client_fifos for f in fifos):
            item = {'pid': p['pid'], 'what': 'input holder with no client', 'fifo': fifos[0], 'minutes': p['minutes']}
            out['flags'].append(item)
            if clean:
                os.kill(p['pid'], signal.SIGTERM)
                out['cleaned'].append(item)

    for p in procs:
        if SCRATCH in p['cmd'] and p['minutes'] > STUCK_MINUTES and p['cmd'].startswith(('bash ', '/bin/bash ', 'sh ')):
            children = [c for c in procs if c['ppid'] == p['pid']]
            item = {'pid': p['pid'], 'what': f'scratchpad script running {p["minutes"]:.0f} min',
                    'cmd': p['cmd'][-120:], 'children': [c['cmd'][:80] for c in children]}
            out['flags'].append(item)
            if clean:
                for c in children:
                    os.kill(c['pid'], signal.SIGTERM)
                os.kill(p['pid'], signal.SIGTERM)
                out['cleaned'].append(item)

    out['mcp_servers'] = sum('mcp_server.py' in p['cmd'] for p in procs)
    active = '/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Bot-reports/runs/ACTIVE'
    if os.path.exists(active):
        out['squad_run'] = open(active).read().strip()[:200]
    st = os.statvfs('/tmp')  # a RAM disk here, shared by the bots' logs and MariaDB's temporary files
    tmp_pct = round(100 * (1 - st.f_bavail / st.f_blocks))
    out['tmp_used_pct'] = tmp_pct
    if tmp_pct >= 60:
        out['flags'].append({'what': f'/tmp is {tmp_pct}% full (RAM disk; MariaDB fails when it is full)'})
        if clean:  # rotated client log pieces are closed files
            removed = 0
            for root, _, files in os.walk('/var/tmp/swg-bots'):
                if root.endswith('/log/zArchive'):
                    for name in files:
                        if name.startswith('core3client-') and name.endswith('.log'):
                            os.unlink(os.path.join(root, name))
                            removed += 1
            out['cleaned'].append({'what': f'removed {removed} rotated bot client logs from /tmp', 'pid': '-'})
    mem = dict(line.split(':', 1) for line in open('/proc/meminfo'))
    kb = lambda k: int(mem[k].split()[0]) >> 10
    out['memory_mb'] = {'total': kb('MemTotal'), 'available': kb('MemAvailable'), 'swap_used': kb('SwapTotal') - kb('SwapFree')}
    if out['memory_mb']['available'] < 1500:
        out['flags'].append({'what': f"low memory: {out['memory_mb']['available']} MB available"})
    print(json.dumps(out))


if __name__ == '__main__':
    main()
