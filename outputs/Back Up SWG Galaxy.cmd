@echo off
echo This saves and briefly stops a running galaxy, makes a verified backup, then restarts it.
echo Keep Start SWG Server.cmd open while playing; reopen it after the backup if it has stopped.
wsl -d Debian -u root -- python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/backup_server.py
pause
