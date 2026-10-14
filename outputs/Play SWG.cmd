@echo off
cd /d "%~dp0SWG-client"
rem If a test-galaxy session was closed early, switch the login back to the live galaxy first.
if exist swgemu_login.live.cfg move /y swgemu_login.live.cfg swgemu_login.cfg >nul
start "" SWGEmu.exe
