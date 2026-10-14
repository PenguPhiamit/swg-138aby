@echo off
rem Opens the live server code (branch sandbox) and the dev copy (branch dev) in VS Code,
rem running inside Debian as the swgemu user. Source Control and Git Graph show every change.
call "%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd" --file-uri "vscode-remote://wsl+Debian/opt/swg/home/swg-server.code-workspace"
