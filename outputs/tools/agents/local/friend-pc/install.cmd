@echo off
rem Starts install-ollama-lan.ps1 from this folder (Windows won't run a double-clicked .ps1). Extra words are passed
rem on, for example:  install.cmd -OwnerPC 192.168.1.20   or   install.cmd -CheckOnly   or   install.cmd -Remove
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-ollama-lan.ps1" %*
echo.
pause
