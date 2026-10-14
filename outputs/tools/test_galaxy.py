"""A disposable test galaxy for trying dev-branch scripts without touching the live galaxy.

Restores a backup into /opt/swg/testgalaxy with its own database (swgemu_test) and ports
46xxx, replaces bin/scripts with the dev worktree's, and runs it beside the live galaxy.

Inside Debian, as root:
  python3 test_galaxy.py start [--backup DIR] [--set FILE:KEY=VALUE ...] [--config KEY=VALUE ...] [--dev-server]
  python3 test_galaxy.py status
  python3 test_galaxy.py stop                                              # clean exit + delete

--set tweaks a Lua table value in the test copy only, e.g. to shorten timers:
  --set screenplays/sandbox/sandbox_world_bosses.lua:lifetime=240
--config appends a line to the test copy's config-local.lua, e.g. --config 'AgentAccounts={"agent01"}'
--dev-server runs the dev worktree's core3 build instead of the backup's (to test server C++ changes)
Bots reach it with: core3client --login-host <WSL IP> --login-port 46453 ...
"""
from pathlib import Path
import json, re, shutil, subprocess, sys, time

BACKUPS = Path('/opt/swg/backups')
DEV_SCRIPTS = Path('/opt/swg/Core3-dev/MMOCoreORB/bin/scripts')
DEV_CORE3 = Path('/opt/swg/Core3-dev/MMOCoreORB/bin/core3')
LOCAL_TRE = Path('/opt/swg/tre/local_planets.tre')  # test-only archive; live's config doesn't list it
TEST_ZONES = ['hoth']  # zones whose client data ships in LOCAL_TRE (added only when it exists)
SHUTTLE_BOOT_DELAY_MS = 30 * 1000  # stock Core3 waits 5 minutes after a start before scheduling shuttles
TARGET = Path('/opt/swg/testgalaxy')
MARKER = TARGET/'.test-galaxy'
BIN = TARGET/'Core3/MMOCoreORB/bin'
FIFO = TARGET/'console.in'
LOG = TARGET/'console.log'
DB = 'swgemu_test'
USER = "'swgemu'@'127.0.0.1'"
PORTS = {'LoginPort': 46453, 'PingPort': 46462, 'StatusPort': 46455, 'ORBPort': 46419, 'ZoneServerPort': 46463}


def run(args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def sql(query, database=None):
    return subprocess.check_output(['mariadb', '-Nse', query] + ([database] if database else []), text=True).strip()


def pids():
    out = subprocess.run(['pgrep', '-x', 'core3'], capture_output=True, text=True).stdout.split()
    return [p for p in out if Path(f'/proc/{p}/cwd').exists()]


def test_pids():
    return [p for p in pids() if Path(f'/proc/{p}/cwd').resolve() == BIN]


def cleanup():
    sql(f'DROP DATABASE IF EXISTS {DB}')
    if sql(f"SELECT count(*) FROM mysql.db WHERE Db='{DB}'") != '0':
        sql(f'REVOKE ALL PRIVILEGES ON `{DB}`.* FROM {USER}')
    subprocess.run(['pkill', '-f', f'sleep infinity # test-galaxy-holder'])
    if MARKER.exists():
        shutil.rmtree(TARGET)


def start(args):
    if TARGET.exists():
        raise SystemExit('A test galaxy already exists; run stop first.')
    free_gb = int(open('/proc/meminfo').read().split('MemAvailable:')[1].split()[0]) / 2**20
    if free_gb < 6.5:
        raise SystemExit(f'Only {free_gb:.1f} GiB free in Debian; a galaxy needs about 6.')
    backup = Path(args[args.index('--backup') + 1]) if '--backup' in args else max(
        (p for p in BACKUPS.iterdir() if (p/'manifest.json').exists()), key=lambda p: p.name.rsplit('-', 1)[-1])
    print(f'Test galaxy from {backup.name} with dev scripts', flush=True)
    TARGET.mkdir(mode=0o750)
    MARKER.write_text('Disposable test galaxy; safe to delete.\n')
    try:
        run(['tar', '-xzf', str(backup/'server.tar.gz'), '-C', str(TARGET)])
        shutil.rmtree(BIN/'scripts')
        shutil.copytree(DEV_SCRIPTS, BIN/'scripts', symlinks=True)
        if '--dev-server' in args:
            shutil.copy2(DEV_CORE3, BIN/'core3')
            print('  dev server build (core3 from the dev worktree)', flush=True)
        for item in (a for i, a in enumerate(args) if i > 0 and args[i - 1] == '--set'):
            rel, assignment = item.split(':', 1)
            key, value = assignment.split('=', 1)
            path = BIN/'scripts'/rel
            text, count = re.subn(rf'(\n\s*{re.escape(key)}\s*=\s*)[^,\n]+', rf'\g<1>{value}', path.read_text(), count=1)
            if not count:
                raise SystemExit(f'--set: {key} not found in {rel}')
            path.write_text(text)
            print(f'  test-only setting: {rel} {key} = {value}')

        dump = (backup/'galaxy.sql').read_text(errors='surrogateescape').splitlines(keepends=True)
        skip = {i for i, l in enumerate(dump) if re.match(r'CREATE DATABASE .*`swgemu`', l) or l.strip() == 'USE `swgemu`;'}
        if len(skip) != 2 or any('`swgemu`.' in l for i, l in enumerate(dump) if i not in skip):
            raise SystemExit('Unexpected SQL dump layout; refusing to import.')
        (TARGET/'galaxy-test.sql').write_text(''.join(l for i, l in enumerate(dump) if i not in skip), errors='surrogateescape')
        sql(f'CREATE DATABASE {DB}')
        with (TARGET/'galaxy-test.sql').open('rb') as stream:
            run(['mariadb', DB], stdin=stream)
        sql(f'GRANT ALL PRIVILEGES ON `{DB}`.* TO {USER}')
        host = subprocess.check_output(['hostname', '-I'], text=True).split()[0]
        sql(f"UPDATE galaxy SET name='Test Galaxy', address='{host}', port={PORTS['ZoneServerPort']}, "
            f"pingport={PORTS['PingPort']} WHERE galaxy_id=2", DB)

        config = BIN/'conf/config-local.lua'
        # Our test-only client data archive goes first in the server's archive list (the first entry wins). Since 14 Oct
        # the server needs it: Hoth's resource types live in its merged resource_tree.iff (tools/hoth/hoth_client_build.py).
        local_tre = '' if not LOCAL_TRE.exists() else f'table.insert(Core3.TreFiles, 1, "{LOCAL_TRE.name}")\n'
        if local_tre:
            print(f'  {LOCAL_TRE.name} first in the server archive list (test only)', flush=True)
            # The test-only zones that archive's content needs (Hoth). Until 14 Oct this was a --config by hand, so a
            # restart through `squad.py galaxy` (or the overnight script) silently dropped Hoth.
            for zone in TEST_ZONES:
                local_tre += (f'Core3.ZonesEnabled = (function(t) for _, z in ipairs(t) do if z == "{zone}" then return t end '
                              f'end table.insert(t, "{zone}") return t end)(Core3.ZonesEnabled)\n')
            print(f'  test zones enabled: {", ".join(TEST_ZONES)}', flush=True)
        # Core3 holds every shuttle for 5 minutes after a start (ShuttleZoneComponent.cpp, BootDelay); until then a travel
        # point has no shuttle and /purchaseTicket fails without a message (14 Oct: bots' tickets failed for minutes
        # after each test restart). The test galaxy starts its shuttles after 30 s; live keeps the stock delay.
        shuttles = f'Core3.ShuttleZoneComponent = {{ BootDelay = {SHUTTLE_BOOT_DELAY_MS} }}\n'
        print(f'  shuttles in service {SHUTTLE_BOOT_DELAY_MS // 1000} s after the start (stock: 300 s)', flush=True)
        with config.open('a') as stream:
            stream.write('\n-- TEST GALAXY OVERRIDES (disposable copy)\n'
                         f'Core3.DBName = "{DB}"\nCore3.MakeWeb = 0\n' + local_tre + shuttles +
                         ''.join(f'Core3.{k} = {v}\n' for k, v in PORTS.items()) +
                         ''.join(f'Core3.{a}\n' for i, a in enumerate(args) if i > 0 and args[i - 1] == '--config'))
        run(['chown', '-R', 'swgemu:swgemu', str(TARGET)])
        run(['runuser', '-u', 'swgemu', '--', 'mkfifo', str(FIFO)])
        # Hold the console pipe open so core3 never sees end-of-input; stop writes "exit".
        # Detach fully (no inherited stdout) so callers piping this script are not held open.
        quiet = dict(start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.Popen(['runuser', '-u', 'swgemu', '--', 'bash', '-c',
                          f'exec 3>{FIFO}; sleep infinity # test-galaxy-holder'], **quiet)
        subprocess.Popen(['runuser', '-u', 'swgemu', '--', 'bash', '-c', f'cd {BIN} && exec ./core3 < {FIFO} > {LOG} 2>&1'],
                         **quiet)
        started = time.monotonic()
        while '[Core] initialized' not in (LOG.read_text(errors='replace') if LOG.exists() else ''):
            if time.monotonic() - started > 600:
                raise SystemExit('Test galaxy did not initialize within 10 minutes; see ' + str(LOG))
            if time.monotonic() - started > 20 and not test_pids():
                raise SystemExit('Test galaxy exited during startup; see ' + str(LOG))
            time.sleep(2)
        print(f'Test galaxy ready in {round(time.monotonic() - started)} s: login {host}:{PORTS["LoginPort"]}', flush=True)
    except BaseException:
        stop([], quiet=True)
        raise


def stop(args, quiet=False):
    if not TARGET.exists():
        if not quiet:
            print('No test galaxy.')
        return
    if test_pids():
        with open(FIFO, 'w') as stream:
            stream.write('exit\n')
        for _ in range(300):
            if not test_pids():
                break
            time.sleep(1)
        for pid in test_pids():
            subprocess.run(['kill', '-9', pid])
    shutil.copy2(LOG, '/opt/swg/agent/logs/test-galaxy-last.log') if LOG.exists() else None
    clean = LOG.exists() and '[Core] server closed' in LOG.read_text(errors='replace')
    cleanup()
    print(f'Test galaxy stopped ({"clean exit" if clean else "forced"}) and deleted. Log kept at /opt/swg/agent/logs/test-galaxy-last.log')


def status(args):
    if not TARGET.exists():
        print('No test galaxy.')
        return
    log = LOG.read_text(errors='replace') if LOG.exists() else ''
    errors = [l for l in log.splitlines() if re.search(r'\bERROR\b|FATAL|[Ll]ua error', l)]
    print(json.dumps({'running': bool(test_pids()), 'initialized': '[Core] initialized' in log,
                      'error_lines': len(errors), 'last_errors': errors[-5:]}, indent=2))


if __name__ == '__main__':
    command = sys.argv[1] if len(sys.argv) > 1 else 'status'
    {'start': start, 'stop': stop, 'status': status}[command](sys.argv[1:])
