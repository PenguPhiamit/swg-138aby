from pathlib import Path
import json, re, subprocess

root = Path('/opt/swg/Core3')
binpath = root / 'MMOCoreORB/bin'
def run(args):
    result = subprocess.run(args, text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else {'exit': result.returncode, 'error': result.stderr.strip()[:700]}

local = (binpath/'conf/config-local.lua').read_text()
public_keys = ['AutoReg', 'CharacterBuilderEnabled', 'ZoneProcessingThreads', 'MaxNavMeshJobs', 'MantisHost', 'JTL.JTLEnabled']
settings = {}
for key in public_keys:
    found = re.search(r'^Core3\.' + re.escape(key) + r'\s*=\s*(.+)$', local, re.M)
    settings[key] = found.group(1) if found else '(upstream default)'

report = {
    'distribution': Path('/etc/os-release').read_text(),
    'server_revision': run(['runuser','-u','swgemu','--','git','-C',str(root),'rev-parse','HEAD']),
    'engine_revision': run(['runuser','-u','swgemu','--','git','-C',str(root/'MMOCoreORB/utils/engine3'),'rev-parse','HEAD']),
    'source_changes': run(['runuser','-u','swgemu','--','git','-C',str(root),'status','--short']),
    'build_cache': [line for line in (root/'MMOCoreORB/build/local/CMakeCache.txt').read_text().splitlines() if re.match(r'(CMAKE_BUILD_TYPE|CMAKE_CXX_COMPILER|COMPILE_TESTS|ENABLE_BUILD_CLIENT|BUILD_IDL|RUN_GIT):',line)],
    'dependencies': run(['dpkg-query','-W','-f=${Package} ${Version}\n','clang-19','libdb5.3-dev','liblua5.3-dev','libmariadb-dev','mariadb-server','cmake','ninja-build','gdb','libjemalloc-dev']),
    'settings': settings,
    'services': run(['systemctl','show','swg-local','-p','ActiveState','-p','SubState','-p','User','-p','KillMode','-p','TimeoutStopUSec']),
    'galaxy_metadata': run(['mariadb','-Nse','SELECT count(*) AS accounts FROM swgemu.accounts; SELECT count(*) AS characters FROM swgemu.characters; SELECT * FROM swgemu.db_metadata;']),
    'size': run(['du','-sh',str(root), str(binpath/'databases'),'/opt/swg/tre']),
    'ports': run(['ss','-lunp']),
}
logs = run(['journalctl','-u','swg-local','-n','300','--no-pager','-o','cat'])
if isinstance(logs,str):
    report['recent_log_findings'] = [line for line in logs.splitlines() if re.search('ERROR|FATAL|initialized|shutdown|Mantis|Access denied',line,re.I)][-30:]
print(json.dumps(report,indent=2))
