@echo off
echo Restores the newest backup into a temporary copy on other ports, starts it,
echo checks it loads the same world, shuts it down and deletes it.
echo The live galaxy must be stopped first. Takes about 2 minutes.
echo.
wsl -d Debian -u root -- python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/restore_rehearsal.py
pause
