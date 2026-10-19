@echo off
rem Ossus O15 mirage (Claude, 18 Oct 2026): build the proxy d3d9.dll and mirage_test.exe (32-bit, like SWGEmu.exe)
rem into ..\..\..\work\o15-mirage. Needs Visual Studio 2022 (C tools) and the Windows SDK (fxc). Run blade_ids.py first
rem if the blade programs change.
setlocal
set "HERE=%~dp0"
for %%i in ("%HERE%..\..\..\work\o15-mirage") do set "OUT=%%~fi"
set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
for /f "usebackq delims=" %%i in (`"%VSWHERE%" -latest -property installationPath`) do set "VS=%%i"
call "%VS%\VC\Auxiliary\Build\vcvarsall.bat" x86 >nul || exit /b 1
if not exist "%OUT%\gen" mkdir "%OUT%\gen"
fxc /nologo /T ps_2_0 /E main /Vn g_mask_ps_code /Fh "%OUT%\gen\mask_ps.h" "%HERE%src\mask_ps.hlsl" || exit /b 1
fxc /nologo /T ps_2_0 /E main /Vn g_haze_ps_code /Fh "%OUT%\gen\haze_ps.h" "%HERE%src\haze_ps.hlsl" || exit /b 1
fxc /nologo /T vs_2_0 /E main /Vn g_test_vs_code /Fh "%OUT%\gen\test_vs.h" "%HERE%src\test_vs.hlsl" || exit /b 1
cl /nologo /O2 /W3 /MT /D_CRT_SECURE_NO_WARNINGS /LD /I "%OUT%\gen" /Fo"%OUT%\gen\\" "%HERE%src\mirage.c" /Fe"%OUT%\d3d9.dll" ^
   /link /DEF:"%HERE%src\d3d9.def" user32.lib || exit /b 1
cl /nologo /O2 /W3 /MT /D_CRT_SECURE_NO_WARNINGS /Fo"%OUT%\gen\\" /I "%OUT%\gen" "%HERE%src\mirage_test.c" /Fe"%OUT%\mirage_test.exe" ^
   /link user32.lib || exit /b 1
echo built %OUT%\d3d9.dll and %OUT%\mirage_test.exe
