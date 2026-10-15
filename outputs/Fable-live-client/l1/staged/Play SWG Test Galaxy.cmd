@echo off
title SWG - TEST galaxy client
rem Play on the TEST galaxy: a disposable copy of the live galaxy on ports 46xxx (Hoth and other dev content,
rem plus the bot squads). Nothing done there reaches the live galaxy. Log in with your usual account.
rem Points the client at the test login server, then puts the live login back when the client closes.
cd /d "%~dp0SWG-client"
set WSLIP=
for /f "tokens=1" %%i in ('wsl -d Debian -u swgemu -- hostname -I') do if not defined WSLIP set WSLIP=%%i
if not defined WSLIP (
  echo Could not read the WSL address. Is Debian running?
  pause
  exit /b 1
)
wsl -d Debian -u swgemu -- ss -lun | findstr /c:":46453 " >nul
if errorlevel 1 (
  echo The test galaxy is not running right now. Ask Claude to start it.
  pause
  exit /b 1
)
if not exist swgemu_login.live.cfg copy /y swgemu_login.cfg swgemu_login.live.cfg >nul
> swgemu_login.cfg echo [ClientGame]
>> swgemu_login.cfg echo loginServerPort0=46453
>> swgemu_login.cfg echo loginServerAddress0=%WSLIP%
rem Test-only archives, for this session only (owner's OK, 14 Oct). Check: python -I tools\hoth\client_load_order.py
rem  - local_planets.tre: Hoth in the planet lists, ticket screen and planetary map. Priority 49, the top level the
rem    client loads (maxSearchPriority 50, as stock 26 had 25 at most); default_patch.tre shares 49 but has none of
rem    its six files.
rem  - The 23 MTG archives (Hoth's terrain, snapshot, map image, planet model) are loaded by swgemu_live.cfg
rem    itself since 14 Oct: the owner OKd a [SharedFile] header above them. Before that they sat after its
rem    [Station] header, where the client ignores them, which caused the 14 Oct Hoth crash.
>> swgemu_login.cfg echo [SharedFile]
if not exist local_planets.cfg if exist local_planets.tre >> swgemu_login.cfg echo searchTree_00_49=local_planets.tre
if exist local_planets.tre echo Test content: Hoth (local_planets.tre and the MTG archives) is loaded for this session.

echo Starting the client on the TEST galaxy (%WSLIP%:46453).
echo Keep this window open: it switches the client back to the live galaxy when you quit.
start "" /wait SWGEmu.exe
move /y swgemu_login.live.cfg swgemu_login.cfg >nul
echo Client closed; the login is back on the live galaxy.
timeout /t 5 >nul
