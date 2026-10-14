"""Rehearse a full galaxy restore in a disposable copy without touching the live galaxy.

Restores a backup into /opt/swg/rehearsal and the database swgemu_rehearsal, starts that
copy on alternate ports (45xxx), checks it loads the same world, shuts it down cleanly,
then deletes the copy. The live galaxy must be stopped (memory, and to rule out mix-ups).

Inside Debian, as root:  python3 restore_rehearsal.py [BACKUP_DIR] [--keep]
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, re, shutil, subprocess, sys, time

BACKUPS = Path('/opt/swg/backups')
LIVE_BIN = Path('/opt/swg/Core3/MMOCoreORB/bin')
TARGET = Path('/opt/swg/rehearsal')
MARKER = TARGET/'.restore-rehearsal'
DB = 'swgemu_rehearsal'
USER = "'swgemu'@'127.0.0.1'"
OUTPUTS = Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs')
PORTS = {'LoginPort': 45453, 'PingPort': 45462, 'StatusPort': 45455,
         'ORBPort': 45419, 'ZoneServerPort': 45463}

def run(args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)

def sql(query, database=None):
    args = ['mariadb', '-Nse', query] + ([database] if database else [])
    return subprocess.check_output(args, text=True).strip()

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def live_fingerprint():
    files = sorted((p.name, p.stat().st_size, p.stat().st_mtime_ns)
                   for p in (LIVE_BIN/'databases').iterdir() if p.is_file())
    tables = sql('CHECKSUM TABLE swgemu.accounts, swgemu.characters, swgemu.galaxy')
    return {'world_files': files, 'sql_checksums': tables}

def counts(database):
    return {'accounts': int(sql('SELECT count(*) FROM accounts', database)),
            'characters': int(sql('SELECT count(*) FROM characters', database))}

def last_match(pattern, text):
    found = re.findall(pattern, text)
    return found[-1] if found else None

def remove_previous():
    if TARGET.exists():
        if not MARKER.exists():
            raise SystemExit(f'{TARGET} exists but is not a rehearsal copy; refusing to delete it.')
        shutil.rmtree(TARGET)
    sql(f'DROP DATABASE IF EXISTS {DB}')

def cleanup():
    sql(f'DROP DATABASE IF EXISTS {DB}')
    if sql(f"SELECT count(*) FROM mysql.db WHERE Db='{DB}'") != '0':
        sql(f'REVOKE ALL PRIVILEGES ON `{DB}`.* FROM {USER}')
    if MARKER.exists():
        shutil.rmtree(TARGET)

args = [a for a in sys.argv[1:] if not a.startswith('--')]
keep = '--keep' in sys.argv
backup = Path(args[0]) if args else max(
    (p for p in BACKUPS.iterdir() if (p/'manifest.json').exists()), key=lambda p: p.name.rsplit('-', 1)[-1])
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
report = {'started_utc': stamp, 'backup': str(backup), 'checks': {}, 'result': 'failed'}
checks = report['checks']
os.umask(0o077)

if subprocess.run(['systemctl', 'is-active', '--quiet', 'swg-local']).returncode == 0:
    raise SystemExit('Stop the live galaxy first (Stop SWG Server.cmd).')
run(['systemctl', 'start', 'mariadb'])
sockets = subprocess.check_output(['ss', '-lntu'], text=True)
busy = [p for p in PORTS.values() if f':{p} ' in sockets]
if busy:
    raise SystemExit(f'Rehearsal ports already in use: {busy}')

print(f'Rehearsing restore of {backup.name}', flush=True)
before = live_fingerprint()
expected = counts('swgemu')
manifest = json.loads((backup/'manifest.json').read_text())
checks['server_archive_checksum'] = digest(backup/'server.tar.gz') == manifest['server_archive_sha256']
checks['sql_dump_checksum'] = digest(backup/'galaxy.sql') == manifest['sql_sha256']
if not (checks['server_archive_checksum'] and checks['sql_dump_checksum']):
    raise SystemExit('Backup checksums do not match its manifest.')

remove_previous()
process = None
completed = False
try:
    print('Extracting server archive...', flush=True)
    TARGET.mkdir(mode=0o750)
    MARKER.write_text('Disposable restore rehearsal copy; safe to delete.\n')
    run(['tar', '-xzf', str(backup/'server.tar.gz'), '-C', str(TARGET)])
    run(['chown', '-R', 'swgemu:swgemu', str(TARGET)])
    bin_dir = TARGET/'Core3/MMOCoreORB/bin'

    print('Importing SQL into a separate database...', flush=True)
    dump = (backup/'galaxy.sql').read_text(errors='surrogateescape').splitlines(keepends=True)
    create = [i for i, l in enumerate(dump) if re.match(r'CREATE DATABASE .*`swgemu`', l)]
    use = [i for i, l in enumerate(dump) if l.strip() == 'USE `swgemu`;']
    if len(create) != 1 or len(use) != 1:
        raise RuntimeError('Unexpected SQL dump layout; refusing to import.')
    filtered = [l for i, l in enumerate(dump) if i not in (create[0], use[0])]
    if any('`swgemu`.' in l for l in filtered):
        raise RuntimeError('SQL dump references swgemu tables by name; refusing to import.')
    rehearsal_sql = TARGET/'galaxy-rehearsal.sql'
    rehearsal_sql.write_text(''.join(filtered), errors='surrogateescape')
    sql(f'CREATE DATABASE {DB}')
    with rehearsal_sql.open('rb') as stream:
        run(['mariadb', DB], stdin=stream)
    sql(f'GRANT ALL PRIVILEGES ON `{DB}`.* TO {USER}')
    sql(f"UPDATE galaxy SET address='127.0.0.1', port={PORTS['ZoneServerPort']}, "
        f"pingport={PORTS['PingPort']} WHERE galaxy_id=2", DB)
    restored = counts(DB)
    checks['sql_counts_match_live'] = restored == expected
    report['sql_counts'] = {'live': expected, 'restored': restored}

    config = bin_dir/'conf/config-local.lua'
    overrides = '\n-- RESTORE REHEARSAL OVERRIDES (disposable copy)\n'
    overrides += f'Core3.DBName = "{DB}"\nCore3.MakeWeb = 0\n'
    overrides += ''.join(f'Core3.{key} = {value}\n' for key, value in PORTS.items())
    with config.open('a') as stream:
        stream.write(overrides)
    checks['config_has_no_live_paths'] = '/opt/swg/Core3' not in config.read_text()

    print('Starting the rehearsal galaxy on ports 45xxx...', flush=True)
    log_path = TARGET/'rehearsal-console.log'
    log = log_path.open('wb')
    process = subprocess.Popen(['runuser', '-u', 'swgemu', '--', './core3'], cwd=bin_dir,
                               stdin=subprocess.PIPE, stdout=log, stderr=subprocess.STDOUT,
                               start_new_session=True)
    started = time.monotonic()
    while '[Core] initialized' not in log_path.read_text(errors='replace'):
        if process.poll() is not None:
            raise RuntimeError('Rehearsal galaxy exited during startup.')
        if time.monotonic() - started > 600:
            raise RuntimeError('Rehearsal galaxy did not initialize within 10 minutes.')
        time.sleep(2)
    report['startup_seconds'] = round(time.monotonic() - started)
    time.sleep(5)
    sockets = subprocess.check_output(['ss', '-lunp'], text=True)
    checks['rehearsal_ports_listening'] = all(f':{PORTS[k]} ' in sockets
                                              for k in ('LoginPort', 'PingPort', 'ZoneServerPort'))
    checks['live_ports_untouched'] = not any(f':{p} ' in sockets for p in (44453, 44462, 44463))

    console = log_path.read_text(errors='replace')
    journal = subprocess.check_output(['journalctl', '-u', 'swg-local', '--no-pager', '-o', 'cat'],
                                      text=True, errors='replace')
    markers = {'resources': r'Resource Map Built with (\d+) resources',
               'character_names': r'loaded (\d+) character names in memory',
               'ground_zones': r'Total Enabled Ground Zones: (\d+)'}
    report['markers'] = {name: {'live_last_start': last_match(p, journal),
                                'rehearsal': last_match(p, console)} for name, p in markers.items()}
    checks['world_markers_match_live'] = all(m['rehearsal'] is not None and
                                             m['rehearsal'] == m['live_last_start']
                                             for m in report['markers'].values())
    report['startup_error_lines'] = [l for l in console.splitlines()
                                     if re.search(r'\bERROR\b|FATAL|[Ll]ua error', l)][:20]

    print('Initialized. Shutting the rehearsal galaxy down cleanly...', flush=True)
    process.stdin.write(b'exit\n')
    process.stdin.flush()
    process.wait(timeout=600)
    console = log_path.read_text(errors='replace')
    checks['clean_shutdown'] = '[Core] server closed' in console
    report['objects_at_shutdown'] = {'rehearsal': last_match(r'total objects in map (\d+)', console),
                                     'live_last_shutdown': last_match(r'total objects in map (\d+)', journal)}
    shutil.copy2(log_path, OUTPUTS/'Documentation-support'/f'restore-rehearsal-{stamp}.log')
    completed = True
finally:
    if process is not None and process.poll() is None:
        # runuser leads its own session; kill the whole group so core3 cannot linger.
        os.killpg(process.pid, 9)
        process.wait()
        checks['clean_shutdown'] = False
    after = live_fingerprint()
    checks['live_world_files_unchanged'] = after['world_files'] == before['world_files']
    checks['live_sql_unchanged'] = after['sql_checksums'] == before['sql_checksums']
    if keep:
        report['kept'] = f'{TARGET} and database {DB} were kept (--keep).'
    else:
        cleanup()
        report['cleaned_up'] = not TARGET.exists() and sql(f"SHOW DATABASES LIKE '{DB}'") == ''
    report['result'] = 'passed' if completed and all(checks.values()) else 'failed'
    out = OUTPUTS/'Documentation-support'/f'restore-rehearsal-{stamp}.json'
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2), flush=True)
    print(f'\nRehearsal {report["result"].upper()}. Report: {out}', flush=True)
