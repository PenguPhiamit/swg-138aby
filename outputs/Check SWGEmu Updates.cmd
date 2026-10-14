@echo off
echo Checks the official SWGEmu Core3 project for new work. Changes nothing.
echo.
wsl -d Debian -u root -- python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/upstream_sync.py
pause
