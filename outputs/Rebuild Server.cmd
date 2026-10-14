@echo off
echo Recompiles the live server after C++ changes. Stop the galaxy first.
echo Lua-only changes do not need this; use Check Lua Scripts.cmd and restart.
echo.
wsl -d Debian -u root -- python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/rebuild_server.py
pause
