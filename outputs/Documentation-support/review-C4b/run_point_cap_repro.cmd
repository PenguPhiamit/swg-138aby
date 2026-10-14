@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul
if errorlevel 1 exit /b 1
cl /nologo /EHsc /std:c++17 /Fe:point_cap_repro.exe /Fo:point_cap_repro.obj point_cap_repro.cpp
if errorlevel 1 exit /b 1
point_cap_repro.exe
