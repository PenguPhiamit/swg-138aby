# Ossus O15 mirage (Claude, 18 Oct 2026): put the proxy in front of DXVK in an SWG client folder. The owner's own PC
# only, with the game closed. Undo with uninstall.ps1.
#   powershell -ExecutionPolicy Bypass -File install.ps1 [-Client <SWG-client folder>] [-Build <folder with d3d9.dll>]
# DXVK's d3d9.dll becomes dxvk_d3d9.dll (the proxy loads it from there), the proxy becomes d3d9.dll, and mirage.ini is
# copied in if the folder has none.
param(
    [string]$Client = (Join-Path $PSScriptRoot '..\..\SWG-client'),
    [string]$Build = (Join-Path $PSScriptRoot '..\..\..\work\o15-mirage')
)
$ErrorActionPreference = 'Stop'
$Client = (Resolve-Path $Client).Path
if (Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match '^SWGEmu' }) {
    throw 'An SWGEmu process is running. Close the game (and its setup) first.'
}
$proxy = Join-Path $Build 'd3d9.dll'
$d3d9 = Join-Path $Client 'd3d9.dll'
$dxvk = Join-Path $Client 'dxvk_d3d9.dll'
if (-not (Test-Path $proxy)) { throw "No proxy at $proxy; run build.cmd first." }
if (-not (Test-Path $dxvk)) {
    # first install: the d3d9.dll there must be DXVK (about 7.8 MB; the proxy is far smaller)
    if (-not (Test-Path $d3d9)) { throw "No d3d9.dll in ${Client}: DXVK is not installed there." }
    if ((Get-Item $d3d9).Length -lt 2MB) { throw "$d3d9 is not DXVK; not touching it." }
    Rename-Item $d3d9 'dxvk_d3d9.dll'
    Write-Host "DXVK's d3d9.dll is now dxvk_d3d9.dll"
}
Copy-Item $proxy $d3d9 -Force
Write-Host "proxy installed as $d3d9 (sha256 $((Get-FileHash $d3d9).Hash.Substring(0, 8).ToLower()))"
$ini = Join-Path $Client 'mirage.ini'
if (-not (Test-Path $ini)) {
    Copy-Item (Join-Path $PSScriptRoot 'mirage.ini') $ini
    Write-Host "settings: $ini"
}
Write-Host 'Done. Start the game; the proxy writes mirage.log next to SWGEmu.exe.'
