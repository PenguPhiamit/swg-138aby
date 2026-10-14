from pathlib import Path
from datetime import datetime, timezone
import fcntl, hashlib, json, os, shutil, subprocess, tarfile

SERVER = Path('/opt/swg/Core3')
BIN = SERVER / 'MMOCoreORB/bin'
OUTPUTS = Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs')

def checked(args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)

def capture(args):
    return subprocess.check_output(args, text=True).strip()

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def backup(label='galaxy', after_snapshot=None):
    lock = open('/run/swg-local-backup.lock','w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    destination = Path('/opt/swg/backups') / (label + '-' + stamp)
    destination.mkdir(parents=True, mode=0o700)
    active = subprocess.run(['systemctl','is-active','--quiet','swg-local']).returncode == 0
    maintenance = Path('/run/swg-local-maintenance')
    maintenance.touch()
    try:
        if active:
            print('Saving the galaxy and stopping it for a consistent backup...', flush=True)
            checked(['systemctl','stop','swg-local'])
        if subprocess.run(['pgrep','-x','core3'], stdout=subprocess.DEVNULL).returncode == 0:
            raise RuntimeError('The game process is still running; backup cancelled.')
        checked(['systemctl','start','mariadb'])
        with (destination/'galaxy.sql').open('wb') as stream:
            checked(['mariadb-dump','--single-transaction','--routines','--events','--triggers','--databases','swgemu'], stdout=stream)
        # Save the existing database login/grants for recovery; never print them.
        with (destination/'database-user.sql').open('w') as stream:
            definition = capture(['mariadb','-Nse',"SHOW CREATE USER 'swgemu'@'127.0.0.1'"])
            # MariaDB versions return either one definition column or a label and definition.
            definition = definition.split('\t',1)[-1]
            if not definition.startswith('CREATE USER '):
                raise RuntimeError('Unexpected database account export format.')
            stream.write(definition + ';\n')
            grants = capture(['mariadb','-Nse',"SHOW GRANTS FOR 'swgemu'@'127.0.0.1'"])
            stream.write(';\n'.join(grants.splitlines()) + ';\n')
        print('Archiving world saves, server source, configuration and executable...', flush=True)
        checked(['tar','--exclude=Core3/MMOCoreORB/build','-czf',str(destination/'server.tar.gz'),
                 '-C','/opt/swg','Core3','server_service.py'])
        recovery = destination/'recovery'
        recovery.mkdir()
        shutil.copy2('/etc/systemd/system/swg-local.service', recovery/'swg-local.service')
        shutil.copytree('/etc/mysql', recovery/'mysql-config')
        with (recovery/'packages.txt').open('w') as stream:
            checked(['dpkg-query','-W','-f=${Package} ${Version}\n'], stdout=stream)
        config = destination/'client-settings'
        config.mkdir()
        client = OUTPUTS/'SWG-client'
        for path in client.glob('*.cfg'):
            shutil.copy2(path, config/path.name)
        if (client/'profiles').exists():
            shutil.copytree(client/'profiles',config/'profiles')
        for path in [*OUTPUTS.glob('*.cmd'), OUTPUTS/'SWG-login.txt']:
            shutil.copy2(path, recovery/path.name)
        shutil.copy2(OUTPUTS/'tools/start_server.py', recovery/'start_server.py')
        (recovery/'tools').mkdir()
        for path in (OUTPUTS/'tools').glob('*.py'):
            shutil.copy2(path, recovery/'tools'/path.name)
        git = ['runuser','-u','swgemu','--','git','-C',str(SERVER)]
        source_state = capture(git+['status','--short'])
        # Local work is committed on the private sandbox branch, so diff against the
        # upstream tag. The bulk MTG import is left out of the readable patch; the
        # full history is inside server.tar.gz.
        base = 'upstream-base' if subprocess.run(git+['rev-parse','-q','--verify','upstream-base'],
                                                 stdout=subprocess.DEVNULL).returncode == 0 else 'HEAD'
        with (recovery/'source-changes.patch').open('w') as stream:
            checked(git+['diff','--binary',base,'--','.',
                         ':(exclude)MMOCoreORB/bin/scripts/object/custom_content',
                         ':(exclude)MMOCoreORB/bin/scripts/mobile/custom_content'],stdout=stream)
        with (recovery/'local-commits.txt').open('w') as stream:
            checked(git+['log','--format=%h %ad %s','--date=short',base+'..HEAD'],stdout=stream)
        archives = {path.name:digest(path) for path in sorted(Path('/opt/swg/tre').glob('*.tre'))}
        metadata = {
            'created_utc':stamp,
            'server_revision':capture(git+['rev-parse','HEAD']),
            'server_branch':capture(git+['rev-parse','--abbrev-ref','HEAD']),
            'upstream_base':capture(git+['rev-parse',base]),
            'engine_revision':capture(['runuser','-u','swgemu','--','git','-C',str(SERVER/'MMOCoreORB/utils/engine3'),'rev-parse','HEAD']),
            'source_changes_note':'source_changes lists uncommitted files only; committed local work is in recovery/local-commits.txt and source-changes.patch.',
            'source_changes':source_state,
            'os_release':Path('/etc/os-release').read_text(),
            'server_archive_sha256':digest(destination/'server.tar.gz'),
            'sql_sha256':digest(destination/'galaxy.sql'),
            'required_server_assets_sha256':archives,
            'assets_note':'TRE assets and the complete client are retained in their existing installation folders, not duplicated in this backup. Match these hashes when restoring. Build intermediates are excluded; the source, Git history and running executable are included.',
        }
        with tarfile.open(destination/'server.tar.gz') as archive:
            names = archive.getnames()
        expected = ['Core3/MMOCoreORB/bin/core3','Core3/MMOCoreORB/bin/conf/config-local.lua','server_service.py']
        if not all(name in names for name in expected) or not any('/bin/databases/' in name and name.endswith('.db') for name in names):
            raise RuntimeError('Backup verification failed: expected server/save files were absent.')
        metadata['archive_verified'] = True
        (destination/'manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
        (destination/'RESTORE.txt').write_text(
            'GALAXY RECOVERY SNAPSHOT\n\n'
            'Contains SQL account/character metadata, Berkeley DB world saves, source and Git history,\n'
            'server executable, private configuration, database login/grants, service and client preferences.\n'
            'Contains account hashes and database secrets: keep this backup private.\n\n'
            'Required separately: the installed TRE assets and complete client. See manifest hashes.\n'
            'Restore only with the galaxy stopped. First preserve the current state. Restore the server\n'
            'archive to /opt/swg, import galaxy.sql, restore ownership to swgemu and service configuration.\n'
            'For a new Debian installation, install compatible dependencies and recreate the database\n'
            'login using database-user.sql (it is for a fresh database server). Restore the asset files\n'
            'at the configured TrePath, then use Start SWG Server.cmd to refresh the connection address.\n'
            'Never combine SQL from one snapshot with Berkeley DB saves from another.\n'
        )
        for path in destination.rglob('*'):
            if path.is_file():
                path.chmod(0o600)
        windows_copy = OUTPUTS/'Backups'/destination.name
        shutil.copytree(destination,windows_copy)
        if digest(windows_copy/'server.tar.gz') != metadata['server_archive_sha256']:
            raise RuntimeError('Windows backup copy checksum did not match.')
        print('Verified backup: '+str(windows_copy),flush=True)
        if after_snapshot is not None:
            after_snapshot(destination)
        return destination
    finally:
        if active:
            checked(['systemctl','start','swg-local'])
            print('Galaxy start requested. Keep Start SWG Server.cmd open while playing.',flush=True)
        maintenance.unlink(missing_ok=True)
        lock.close()

if __name__ == '__main__':
    os.umask(0o077)
    backup()
