import sys
from pathlib import Path
sys.path.insert(0,'/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools')
from backup_server import backup
destination = backup('before-sandbox-and-content')
Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/work/sandbox-backup-path.txt').write_text(str(destination))
