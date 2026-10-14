@echo off
echo Live galaxy console (last 60 lines, then new lines as they happen).
echo Closing this window does NOT stop the galaxy. Keep the Start window open while playing.
echo.
wsl -d Debian -u root -- journalctl -u swg-local -f -n 60 -o cat
pause
