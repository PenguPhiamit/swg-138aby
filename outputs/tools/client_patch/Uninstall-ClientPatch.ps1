<#
.SYNOPSIS
  Removes the local_planets.tre patch from a SWGEmu client folder and puts back what it replaced. No admin rights.

.DESCRIPTION
    powershell -NoProfile -ExecutionPolicy Bypass -File Uninstall-ClientPatch.ps1 -ClientDir "C:\SWGEmu"
  Restores the files saved in <client>\local_planets-patch\backup\original\ (the state before the first install),
  removes the kit's local_planets.tre and local_planets.cfg, and takes the one .include line out of swgemu.cfg.
  A local_planets.tre that is not the kit's (changed since install) is moved to backup\removed-<time>\, not deleted.
  The backup folder stays; delete it by hand once you are happy.
  Exit codes: 0 done (or nothing to do), 1 error, 2 not a client folder, 5 client running.
#>
param([Parameter(Mandatory = $true)][string]$ClientDir)
$ErrorActionPreference = 'Stop'
$Latin1 = [Text.Encoding]::GetEncoding(28591)

function Fail($code, $text) { Write-Host "STOPPED: $text"; exit $code }
function Hash($path) { (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLower() }

$ClientDir = (Resolve-Path -LiteralPath $ClientDir).Path
$exe = (Test-Path -LiteralPath (Join-Path $ClientDir 'SWGEmu.exe')) -or (Test-Path -LiteralPath (Join-Path $ClientDir 'SwgClient_r.exe'))
if (-not $exe -or -not (Test-Path -LiteralPath (Join-Path $ClientDir 'swgemu.cfg'))) {
    Fail 2 "$ClientDir does not look like a SWGEmu client folder."
}
$running = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.Path -and $_.Path.StartsWith($ClientDir.TrimEnd([char]92) + [char]92, [StringComparison]::OrdinalIgnoreCase) })
if ($running.Count -gt 0) { Fail 5 'a program in the client folder is running (the SWG client?). Close it and run this again.' }

$PatchDir = Join-Path $ClientDir 'local_planets-patch'
$StateFile = Join-Path $PatchDir 'state.json'
$Original = Join-Path $PatchDir 'backup\original'
if (-not (Test-Path -LiteralPath $StateFile)) { Write-Host 'Nothing to remove: this kit has not installed anything here.'; exit 0 }
$State = Get-Content -LiteralPath $StateFile -Raw | ConvertFrom-Json
$stamp = (Get-Date).ToString('yyyyMMdd-HHmmss')

# swgemu.cfg: take out only the line the installer added.
$mainCfg = Join-Path $ClientDir 'swgemu.cfg'
if ([bool]$State.include_added) {
    $text = [IO.File]::ReadAllText($mainCfg, $Latin1)
    $clean = [regex]::Replace($text, '(?m)^[ \t]*\.include[ \t]+"local_planets\.cfg"[ \t]*\r?\n?', '')
    if ($clean -ne $text) { [IO.File]::WriteAllText($mainCfg, $clean, $Latin1) }
}

# local_planets.cfg and local_planets.tre: the original back if there was one, else remove the kit's copy.
foreach ($name in @('local_planets.cfg', 'local_planets.tre')) {
    $path = Join-Path $ClientDir $name
    $saved = Join-Path $Original $name
    if (Test-Path -LiteralPath $path) {
        $ours = ($name -eq 'local_planets.cfg') -or ((Hash $path) -eq $State.sha256)
        if (-not $ours) {
            $keep = Join-Path $PatchDir "backup\removed-$stamp"
            New-Item -ItemType Directory -Force -Path $keep | Out-Null
            Move-Item -LiteralPath $path -Destination (Join-Path $keep $name)
            Write-Host "$name had changed since the install; moved to $keep"
        } else {
            Remove-Item -LiteralPath $path
        }
    }
    if (Test-Path -LiteralPath $saved) { Copy-Item -LiteralPath $saved -Destination $path; Write-Host "Restored your original $name" }
}

Move-Item -LiteralPath $StateFile -Destination (Join-Path $PatchDir "uninstalled-$stamp.json")
Write-Host "Removed local_planets version $($State.version). Backups are still in $PatchDir; delete that folder when you no longer need them."
exit 0
