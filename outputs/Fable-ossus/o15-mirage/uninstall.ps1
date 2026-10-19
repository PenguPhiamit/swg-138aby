# Ossus O15 mirage (Claude, 18 Oct 2026): take the proxy out again; DXVK goes back to being d3d9.dll.
#   powershell -ExecutionPolicy Bypass -File uninstall.ps1 [-Client <SWG-client folder>]
# mirage.ini and mirage.log stay (they do nothing without the proxy).
param([string]$Client = (Join-Path $PSScriptRoot '..\..\SWG-client'))
$ErrorActionPreference = 'Stop'
$Client = (Resolve-Path $Client).Path
if (Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match '^SWGEmu' }) {
    throw 'An SWGEmu process is running. Close the game (and its setup) first.'
}
$d3d9 = Join-Path $Client 'd3d9.dll'
$dxvk = Join-Path $Client 'dxvk_d3d9.dll'
if (-not (Test-Path $dxvk)) { throw "No dxvk_d3d9.dll in $Client; the proxy is not installed there." }
if ((Test-Path $d3d9) -and (Get-Item $d3d9).Length -ge 2MB) { throw "$d3d9 looks like DXVK, not the proxy; stopping." }
if (Test-Path $d3d9) { Remove-Item $d3d9 }
Rename-Item $dxvk 'd3d9.dll'
Write-Host 'Proxy removed; DXVK is d3d9.dll again.'
