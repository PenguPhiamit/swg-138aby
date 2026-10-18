<#
.SYNOPSIS
  Installs (or upgrades to) the local_planets.tre patch in a SWGEmu client folder. No admin rights needed.

.DESCRIPTION
  Run it from the unpacked kit folder (Install.cmd does that for you):
    powershell -NoProfile -ExecutionPolicy Bypass -File Install-ClientPatch.ps1 -ClientDir "C:\SWGEmu"
  It refuses a folder that is not a SWGEmu client, a damaged kit, missing MTG archives, a running client,
  and (without -AllowDowngrade) an older version than the one installed.
  On a stock client (maxSearchPriority=26) it also moves swgemu_live.cfg's stock archives up to the server's layout.
  Whatever it replaces goes to <client>\local_planets-patch\backup\ first. Uninstall-ClientPatch.ps1 undoes it.
  Exit codes: 0 done, 1 error, 2 not a client folder, 3 requirements, 4 kit damaged, 5 client running, 6 downgrade.
#>
param(
    [Parameter(Mandatory = $true)][string]$ClientDir,
    [switch]$DeepCheck,          # also hash every MTG archive (slow: about 5 GB)
    [switch]$AllowDowngrade,
    [switch]$Status              # only report what is installed
)
$ErrorActionPreference = 'Stop'
$Kit = $PSScriptRoot
$Include = '.include "local_planets.cfg"'
$Latin1 = [Text.Encoding]::GetEncoding(28591)

function Fail($code, $text) { Write-Host "STOPPED: $text"; exit $code }
function Hash($path) { (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLower() }

function Test-ClientFolder($dir) {
    $exe = (Test-Path -LiteralPath (Join-Path $dir 'SWGEmu.exe')) -or (Test-Path -LiteralPath (Join-Path $dir 'SwgClient_r.exe'))
    $need = @('swgemu.cfg', 'swgemu_live.cfg', 'bottom.tre', 'data_other_00.tre', 'patch_14_00.tre')
    $missing = @($need | Where-Object { -not (Test-Path -LiteralPath (Join-Path $dir $_)) })
    if (-not $exe) { $missing += 'SWGEmu.exe' }
    return $missing
}

# The client's config chain: swgemu.cfg and its .include files, [Section] headers, key=value lines.
function Read-CfgChain($dir, $name, $section, $list) {
    $path = Join-Path $dir $name
    if (-not (Test-Path -LiteralPath $path)) { return $section }
    foreach ($raw in [IO.File]::ReadAllLines($path, $Latin1)) {
        $line = ($raw -split ';', 2)[0].Trim()
        if ($line -eq '' -or $line.StartsWith('#')) { continue }
        if ($line -match '^\.include\s+"([^"]+)"') {
            [void](Read-CfgChain $dir $Matches[1] $null $list)    # an included file starts with no section
        } elseif ($line.StartsWith('[') -and $line.EndsWith(']')) {
            $section = $line.Substring(1, $line.Length - 2).Trim()
        } elseif ($line.Contains('=')) {
            $kv = $line -split '=', 2
            $list.Add([pscustomobject]@{ File = $name; Section = $section; Key = $kv[0].Trim(); Value = $kv[1].Trim() })
        }
    }
    return $section
}

# Archives the client loads: @{ name(lower) = priority }, optionally ignoring lines from one file.
function Get-LoadedArchives($dir, $skipFile) {
    $list = New-Object System.Collections.Generic.List[object]
    [void](Read-CfgChain $dir 'swgemu.cfg' $null $list)
    $shared = @($list | Where-Object { $_.Section -eq 'SharedFile' -and $_.File -ne $skipFile })
    $top = 0
    foreach ($e in $shared) { if ($e.Key -eq 'maxSearchPriority') { $top = [Math]::Max($top, [int]$e.Value) } }
    $loaded = @{}
    foreach ($e in $shared) {
        if ($e.Key -match '^searchTree_(\d+)_(\d+)$' -and [int]$Matches[2] -lt $top) {
            $loaded[$e.Value.ToLower()] = [int]$Matches[2]
        }
    }
    return $loaded
}

# The highest maxSearchPriority in the chain's [SharedFile] sections (0 when there is none).
function Get-SearchTop($dir) {
    $list = New-Object System.Collections.Generic.List[object]
    [void](Read-CfgChain $dir 'swgemu.cfg' $null $list)
    $top = 0
    foreach ($e in $list) { if ($e.Section -eq 'SharedFile' -and $e.Key -eq 'maxSearchPriority') { $top = [Math]::Max($top, [int]$e.Value) } }
    return $top
}

# swgemu_live.cfg with its [SharedFile] stock lines moved $shift levels up and maxSearchPriority set to $newTop. Lines
# for the MTG archives and ours stay where they are. Also returns the lowest stock level before the move, how many
# lines moved and whether the file had a maxSearchPriority line to raise.
function Move-LiveCfg($text, $shift, $newTop, $keep) {
    $section = $null; $low = [int]::MaxValue; $moved = 0; $topSet = $false
    $out = foreach ($raw in ($text -split '(?<=\n)')) {
        $body = ($raw -split ';', 2)[0].Trim()
        if ($body.StartsWith('[') -and $body.EndsWith(']')) { $section = $body.Substring(1, $body.Length - 2).Trim() }
        elseif ($section -eq 'SharedFile' -and $body -match '^maxSearchPriority\s*=') {
            $raw = $raw -replace '(maxSearchPriority\s*=\s*)\d+', ('${1}' + $newTop); $topSet = $true
        } elseif ($section -eq 'SharedFile' -and $body -match '^searchTree_\d+_(\d+)\s*=\s*(.+)$' -and -not $keep.ContainsKey($Matches[2].Trim().ToLower())) {
            $n = [int]$Matches[1]; $low = [Math]::Min($low, $n); $moved++
            $raw = $raw -replace "(searchTree_\d+_)$n(?=\s*=)", ('${1}' + ($n + $shift))
        }
        $raw
    }
    return @{ Text = ($out -join ''); Low = $low; Moved = $moved; TopSet = $topSet }
}

function Write-Ascii($path, $text) { [IO.File]::WriteAllText($path, $text, [Text.Encoding]::ASCII) }

# --- checks -------------------------------------------------------------------------------------------
$ClientDir = (Resolve-Path -LiteralPath $ClientDir).Path
$missing = Test-ClientFolder $ClientDir
if ($missing.Count -gt 0) { Fail 2 "$ClientDir does not look like a SWGEmu client folder (missing: $($missing -join ', '))." }

$PatchDir = Join-Path $ClientDir 'local_planets-patch'
$StateFile = Join-Path $PatchDir 'state.json'
$State = $null
if (Test-Path -LiteralPath $StateFile) { $State = Get-Content -LiteralPath $StateFile -Raw | ConvertFrom-Json }
$Target = Join-Path $ClientDir 'local_planets.tre'

if ($Status) {
    if ($State -eq $null) { Write-Host 'Not installed by this kit.'; exit 0 }
    $now = 'missing'
    if (Test-Path -LiteralPath $Target) { $now = Hash $Target }
    $ok = 'OK'
    if ($now -ne $State.sha256) { $ok = 'CHANGED since install' }
    Write-Host "Installed: version $($State.version), sha256 $($State.sha256) ($ok)"
    exit 0
}

$Manifest = Get-Content -LiteralPath (Join-Path $Kit 'manifest.json') -Raw | ConvertFrom-Json
$Source = Join-Path $Kit $Manifest.archive.file
if (-not (Test-Path -LiteralPath $Source) -or (Hash $Source) -ne $Manifest.archive.sha256) {
    Fail 4 'the kit is damaged: local_planets.tre does not match manifest.json. Get the kit again.'
}

$running = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.Path -and $_.Path.StartsWith($ClientDir.TrimEnd([char]92) + [char]92, [StringComparison]::OrdinalIgnoreCase) })
if ($running.Count -gt 0) { Fail 5 'a program in the client folder is running (the SWG client?). Close it and run this again.' }

$bad = @()
foreach ($r in $Manifest.requires) {
    $p = Join-Path $ClientDir $r.file
    if (-not (Test-Path -LiteralPath $p)) { $bad += "$($r.file) (missing)"; continue }
    if ((Get-Item -LiteralPath $p).Length -ne [long]$r.size) { $bad += "$($r.file) (different size)"; continue }
    if ($DeepCheck -and $r.sha256 -and (Hash $p) -ne $r.sha256) { $bad += "$($r.file) (different contents)" }
}
if ($bad.Count -gt 0) { Fail 3 ("these MTG archives must be in the client folder first: " + ($bad -join ', ')) }

$new = [version]$Manifest.version
if ($State -ne $null -and -not $AllowDowngrade -and $new -lt [version]$State.version) {
    Fail 6 "version $($State.version) is installed, newer than this kit ($($Manifest.version)). Use -AllowDowngrade to go back."
}

# A stock SWGEmu client loads only below maxSearchPriority=26, its own archives at 25 and down. The server is built on
# the owner's layout: the stock archives 24 levels higher (49..24 under maxSearchPriority=50), the MTG archives under
# them (23..1) and ours at 49 on top. A client whose cap is too low for ours gets the same move in swgemu_live.cfg
# (the original goes to backup\original first; Uninstall-ClientPatch.ps1 puts it back). Anything else stops here.
$LiveCfg = Join-Path $ClientDir 'swgemu_live.cfg'
$want = [int]$Manifest.archive.priority + 1
$top = Get-SearchTop $ClientDir
$LiveMove = $null
if ($top -lt $want) {
    $keep = @{ ($Manifest.archive.file.ToLower()) = $true }
    $mtgTop = 0
    foreach ($r in $Manifest.requires) { $keep[$r.file.ToLower()] = $true; $mtgTop = [Math]::Max($mtgTop, [int]$r.priority) }
    $shift = $want - $top
    $LiveMove = Move-LiveCfg ([IO.File]::ReadAllText($LiveCfg, $Latin1)) $shift $want $keep
    if (-not $LiveMove.TopSet -or $LiveMove.Moved -eq 0 -or $LiveMove.Low + $shift -le $mtgTop) {
        Fail 1 "this client's archive list (maxSearchPriority $top) is laid out differently from the server's, so nothing was changed. Send the owner your swgemu_live.cfg."
    }
}

# --- install ------------------------------------------------------------------------------------------
$Original = Join-Path $PatchDir 'backup\original'
New-Item -ItemType Directory -Force -Path $Original | Out-Null
$firstRun = ($State -eq $null)

function Save-Backup($file, $folder) {
    $src = Join-Path $ClientDir $file
    if (-not (Test-Path -LiteralPath $src)) { return }
    New-Item -ItemType Directory -Force -Path $folder | Out-Null
    $dst = Join-Path $folder $file
    if (-not (Test-Path -LiteralPath $dst)) { Copy-Item -LiteralPath $src -Destination $dst }
}

$same = (Test-Path -LiteralPath $Target) -and ((Hash $Target) -eq $Manifest.archive.sha256)
if (-not $same) {
    if ($firstRun) { Save-Backup 'local_planets.tre' $Original }
    else { Save-Backup 'local_planets.tre' (Join-Path $PatchDir ('backup\' + $State.version)) }
    $tmp = $Target + '.new'
    Copy-Item -LiteralPath $Source -Destination $tmp -Force
    if ((Hash $tmp) -ne $Manifest.archive.sha256) { Remove-Item -LiteralPath $tmp; Fail 1 'the copy did not verify (disk full?).' }
    Move-Item -LiteralPath $tmp -Destination $Target -Force
}

$liveMoved = $false
if ($State -ne $null) { $liveMoved = [bool]$State.live_cfg_moved }
if ($LiveMove) {
    Save-Backup 'swgemu_live.cfg' $Original
    [IO.File]::WriteAllText($LiveCfg, $LiveMove.Text, $Latin1)
    $liveMoved = $true
}

# The cfg block: our archive, plus any required MTG archive the client's own cfg files do not load yet.
$loaded = Get-LoadedArchives $ClientDir 'local_planets.cfg'
$lines = @("searchTree_00_$($Manifest.archive.priority)=$($Manifest.archive.file)")
$added = @()
foreach ($r in $Manifest.requires) {
    if (-not $loaded.ContainsKey($r.file.ToLower())) { $lines += "searchTree_00_$($r.priority)=$($r.file)"; $added += $r.file }
}
$cfgPath = Join-Path $ClientDir 'local_planets.cfg'
# A run that stopped before writing state.json (kits before 18 Oct) left our own file here: not the friend's original.
$cfgOurs = (Test-Path -LiteralPath $cfgPath) -and ([IO.File]::ReadAllText($cfgPath, $Latin1) -match 'Written by Install-ClientPatch\.ps1')
if ($firstRun -and -not $cfgOurs) { Save-Backup 'local_planets.cfg' $Original }
$cfgText = "; Loads the owner's server content. Written by Install-ClientPatch.ps1; Uninstall-ClientPatch.ps1 removes it.`r`n[SharedFile]`r`n"
foreach ($l in $lines) { $cfgText += "`t$l`r`n" }
Write-Ascii $cfgPath $cfgText

$mainCfg = Join-Path $ClientDir 'swgemu.cfg'
$mainText = [IO.File]::ReadAllText($mainCfg, $Latin1)
$includeRe = '(?m)^\s*\.include\s+"local_planets\.cfg"\s*$'
$includeAdded = $false
if ($State -ne $null) { $includeAdded = [bool]$State.include_added }
else {
    # Same case: that run saved swgemu.cfg before adding the line, so the backup without it says the line is ours.
    $savedMain = Join-Path $Original 'swgemu.cfg'
    if ((Test-Path -LiteralPath $savedMain) -and -not ([IO.File]::ReadAllText($savedMain, $Latin1) -match $includeRe)) { $includeAdded = $true }
}
if (-not ($mainText -match $includeRe)) {
    Save-Backup 'swgemu.cfg' $Original
    if ($mainText.Length -gt 0 -and -not $mainText.EndsWith("`n")) { $mainText += "`r`n" }
    [IO.File]::WriteAllText($mainCfg, $mainText + $Include + "`r`n", $Latin1)
    $includeAdded = $true
}

# State before the check, so a stopped install can still be undone by Uninstall-ClientPatch.ps1 or run again.
$stateObj = [ordered]@{
    version = $Manifest.version; sha256 = $Manifest.archive.sha256; installed = (Get-Date).ToString('yyyy-MM-dd h:mm tt')
    include_added = $includeAdded; mtg_lines_added = $added; previous = $(if ($State -ne $null) { $State.version } else { $null })
    live_cfg_moved = $liveMoved; live_cfg_top = $want
}
Write-Ascii $StateFile (($stateObj | ConvertTo-Json) + "`r`n")

# --- verify -------------------------------------------------------------------------------------------
$after = Get-LoadedArchives $ClientDir $null
if ($after['local_planets.tre'] -ne [int]$Manifest.archive.priority) {
    Fail 1 "local_planets.tre is not loaded at priority $($Manifest.archive.priority) after the change; see $cfgPath."
}
$notLoaded = @($Manifest.requires | Where-Object { -not $after.ContainsKey($_.file.ToLower()) } | ForEach-Object { $_.file })
if ($notLoaded.Count -gt 0) { Fail 1 ("still not loaded: " + ($notLoaded -join ', ')) }

Write-Host "Installed local_planets version $($Manifest.version) (sha256 $($Manifest.archive.sha256.Substring(0, 12))...)."
if ($added.Count -gt 0) { Write-Host "Also told the client to load: $($added -join ', ')" }
if ($LiveMove) { Write-Host "Moved the stock archives in swgemu_live.cfg up $shift levels (maxSearchPriority $want), as on the server's own client." }
Write-Host "Backups: $PatchDir\backup"
exit 0
