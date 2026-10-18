<#
.SYNOPSIS
  Builds SWG-Friends-Setup-<version>.exe from owner-settings.json and the client patch kit.

.DESCRIPTION
    powershell -NoProfile -ExecutionPolicy Bypass -File build.ps1            # check, write build\, compile
    powershell -NoProfile -ExecutionPolicy Bypass -File build.ps1 -DryRun    # check and write build\ only
  owner-settings.json (not in git; copy owner-settings.example.json) says which server address the installer
  points friends at and which kit folder it carries. The kit is checked against its manifest (sha256) first.
  Writes build\settings.iss and build\settings.json, then runs Inno Setup's ISCC.exe. The result is
  build\out\SWG-Friends-Setup-<version>.exe. build\ is gitignored: never commit the .exe.
#>
param([switch]$DryRun, [string]$Settings = (Join-Path $PSScriptRoot 'owner-settings.json'), [switch]$AllowLanAddress)
$ErrorActionPreference = 'Stop'
function Fail($text) { Write-Host "STOPPED: $text" -ForegroundColor Red; exit 1 }

if (-not (Test-Path -LiteralPath $Settings)) { Fail "no $Settings. Copy owner-settings.example.json to owner-settings.json and fill it in (owner-setup.ps1 -WriteSettings does it)." }
$s = Get-Content -LiteralPath $Settings -Raw | ConvertFrom-Json
foreach ($k in @('ServerAddress', 'LoginPort', 'KitDir', 'ClientHelpUrl')) {
    if (-not $s.$k -or "$($s.$k)" -match '<|>') { Fail "owner-settings.json: fill in $k." }
}
function Test-Tailnet([string]$h) { return ($h -match '\.ts\.net$') -or ($h -match '^100\.(6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d+\.\d+$') }
$addr = [string]$s.ServerAddress
if (-not (Test-Tailnet $addr) -and -not $AllowLanAddress) { Fail "ServerAddress $addr is not a Tailscale address (100.64.x.x to 100.127.x.x, or a .ts.net name). Use -AllowLanAddress for a LAN-only test build." }
if ([int]$s.LoginPort -ne 46453 -and [int]$s.LoginPort -ne 44453) { Fail "LoginPort $($s.LoginPort) is neither the test galaxy's 46453 nor live's 44453." }
# The MTG archives: Setup downloads the missing ones from MtgBaseUrl (files side by side under it). Without it,
# Setup stops and sends the friend to MtgHelpUrl instead.
$mtgBase = if ("$($s.MtgBaseUrl)" -notmatch '<') { [string]$s.MtgBaseUrl } else { '' }
$mtgHelp = if ("$($s.MtgHelpUrl)" -notmatch '<') { [string]$s.MtgHelpUrl } else { '' }
if (-not $mtgBase -and -not $mtgHelp) { Fail 'owner-settings.json: fill in MtgBaseUrl (owner-setup.ps1 -WriteSettings) or MtgHelpUrl.' }
if ($mtgBase) {
    try { $u = [Uri]$mtgBase } catch { Fail "MtgBaseUrl $mtgBase is not a link." }
    if ($u.Scheme -eq 'http' -and -not (Test-Tailnet $u.Host) -and -not $AllowLanAddress) { Fail "MtgBaseUrl $mtgBase is plain http outside Tailscale; use https for a public host." }
    if ($u.Scheme -ne 'http' -and $u.Scheme -ne 'https') { Fail "MtgBaseUrl $mtgBase must be an http or https link." }
}

$kit = $s.KitDir
if (-not [IO.Path]::IsPathRooted($kit)) { $kit = Join-Path $PSScriptRoot $kit }
$kit = (Resolve-Path -LiteralPath $kit).Path
$m = Get-Content -LiteralPath (Join-Path $kit 'manifest.json') -Raw | ConvertFrom-Json
foreach ($f in @('local_planets.tre', 'manifest.json', 'Install-ClientPatch.ps1', 'Uninstall-ClientPatch.ps1')) {
    if (-not (Test-Path -LiteralPath (Join-Path $kit $f))) { Fail "the kit $kit has no $f." }
}
$sha = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $kit $m.archive.file)).Hash.ToLower()
if ($sha -ne $m.archive.sha256) { Fail "the kit's local_planets.tre does not match its manifest ($sha)." }
Write-Host "Kit $($m.version): local_planets.tre $($sha.Substring(0, 12))... matches its manifest; $(@($m.requires).Count) MTG archives required."
Write-Host "Server: ${addr}:$($s.LoginPort)"
if ($mtgBase) { Write-Host "MTG archives: friends download the missing ones from $mtgBase (sha256 from the kit manifest)." }
else { Write-Host "MTG archives: not downloaded; Setup sends friends to $mtgHelp." }
Write-Host "Check before you hand it out: the server's /opt/swg/tre/local_planets.tre must have the same sha256 (client-patch-for-friends.md, check-server)."

$build = Join-Path $PSScriptRoot 'build'
New-Item -ItemType Directory -Force -Path $build | Out-Null
$friend = [ordered]@{ ServerAddress = $addr; LoginPort = [int]$s.LoginPort; MtgBaseUrl = $mtgBase; MtgHelpUrl = $mtgHelp; ClientHelpUrl = $s.ClientHelpUrl; KitVersion = $m.version }
[IO.File]::WriteAllText((Join-Path $build 'settings.json'), ($friend | ConvertTo-Json) + "`r`n", [Text.Encoding]::ASCII)
$iss = "; Written by build.ps1 from owner-settings.json. Not in git.`r`n#define KitVersion `"$($m.version)`"`r`n#define KitDir `"$kit`"`r`n"
[IO.File]::WriteAllText((Join-Path $build 'settings.iss'), $iss, [Text.Encoding]::ASCII)
Write-Host "Wrote $build\settings.json and settings.iss."

$iscc = @("${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe", "$env:ProgramFiles\Inno Setup 6\ISCC.exe", "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe") |
    Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if ($DryRun) { Write-Host "DRY RUN: would compile friend-installer.iss with $(if ($iscc) { $iscc } else { 'ISCC.exe (not installed)' })."; exit 0 }
if (-not $iscc) { Fail 'Inno Setup 6 is not installed (ISCC.exe not found). Install it from https://jrsoftware.org/isdl.php first.' }
& $iscc /Q (Join-Path $PSScriptRoot 'friend-installer.iss')
if ($LASTEXITCODE -ne 0) { Fail "ISCC stopped with code $LASTEXITCODE." }
$exe = Join-Path $build "out\SWG-Friends-Setup-$($m.version).exe"
Write-Host "Built $exe ($([math]::Round((Get-Item -LiteralPath $exe).Length / 1MB, 1)) MB). Send it to friends directly; never commit it."
