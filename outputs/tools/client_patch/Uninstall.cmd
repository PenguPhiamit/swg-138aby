@echo off
rem Removes the local_planets patch. Drag your SWGEmu folder onto this file, or run it and paste the folder.
set "CLIENT=%~1"
if "%CLIENT%"=="" set /p "CLIENT=SWGEmu client folder (for example C:\SWGEmu): "
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Uninstall-ClientPatch.ps1" -ClientDir "%CLIENT%"
pause
