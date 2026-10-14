@echo off
echo Checking server Lua scripts for syntax errors (uncommitted and new files)...
wsl -d Debian -u root -- python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/check_lua.py %*
pause
