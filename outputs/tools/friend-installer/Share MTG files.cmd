@echo off
title Sharing the MTG archives with friends (close this window to stop)
rem Friends' Setup downloads the MTG archives they are missing from this PC, over Tailscale only.
cd /d "%~dp0"
python -I mtg-share.py %*
pause
