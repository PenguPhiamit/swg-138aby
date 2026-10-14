@echo off
title SWG process check
chcp 65001 >nul
rem Report galaxies, bots, helpers, the GPT relay and memory; stop known-safe leftovers (stale bot input holders,
rem stuck scratchpad scripts). Report only: remove --clean below.
python "%~dp0tools\proc_check.py" --clean
pause
