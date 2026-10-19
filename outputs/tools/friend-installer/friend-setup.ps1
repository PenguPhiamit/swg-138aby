<#
.SYNOPSIS
  The friend installer's worker. SWG-Friends-Setup.exe (friend-installer.iss) runs it; nobody needs to run it by hand.

.DESCRIPTION
  One action per run:
    Detect           print SWGEmu client folders found on this PC, best first
    Check            is -ClientDir a SWGEmu client with every MTG archive the server needs? (changes nothing)
                     With MtgBaseUrl in settings.json, missing archives are listed in -MtgListFile for Setup to
                     download (exit 4) instead of stopping Setup.
    PlaceMtg         move the archives Setup downloaded (in -From) into the client; a friend's own different
                     version goes to local_planets-patch\backup\friends-installer\mtg first
    Tailscale        install Tailscale if missing (signed download from pkgs.tailscale.com) and join the owner's
                     network with the invite key in -KeyFile (the file is deleted as soon as it is read)
    Patch            install the client patch (the C57 kit's Install-ClientPatch.ps1) and point the login at the server
    Probe            does the server's login port answer? (one UDP session request, read-only)
    Play             put the login and patch lines back if the SWGEmu launcher reset them, then start the game
    Uninstall        take the patch, the login change, the MTG archives Setup added and the launcher's graphics
                     add-on out again, and restore the friend's own files
    TailscaleLogout  log this PC out of Tailscale
    TailscaleRemove  uninstall Tailscale
  -DryRun prints what would change and changes nothing (no download, no install, no file written in the client).
  -ResultFile gets "OK", "WARN" or "ERR" on the first line and a message for the friend after it.
  The invite key is never printed, logged, kept or written anywhere except the -KeyFile the installer made.
  Exit codes: 0 done, 1 error, 2 not a client folder, 3 missing archives, 4 archives to download, 5 client running,
  6 not enough disk space, 7 no answer.
#>
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Detect', 'Check', 'Tailscale', 'PlaceMtg', 'Patch', 'Probe', 'Play', 'Uninstall', 'TailscaleLogout', 'TailscaleRemove')]
    [string]$Action,
    [string]$ClientDir,
    [string]$KeyFile,
    [string]$MtgListFile,
    [string]$From,
    [string]$SettingsFile,
    [string]$KitDir,
    [string]$StateFile,
    [string]$ResultFile,
    [switch]$DryRun
)
# Defaults next to this script. Not in param(): Windows PowerShell 5.1 leaves $PSScriptRoot empty there when
# another program starts the script, which broke every call that relied on them (uninstaller, launcher).
$Here = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (-not $SettingsFile) { $SettingsFile = Join-Path $Here 'settings.json' }
if (-not $KitDir) { $KitDir = Join-Path $Here 'kit' }
if (-not $StateFile) { $StateFile = Join-Path $Here 'state.json' }
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$Latin1 = [Text.Encoding]::GetEncoding(28591)
$TailscaleExe = Join-Path $env:ProgramFiles 'Tailscale\tailscale.exe'
$LoginMarker = '; Written by the SWG friends installer'

function Finish([string]$Kind, [string]$Text, [int]$Code) {
    Write-Host "$Kind`: $Text"
    if ($ResultFile) { [IO.File]::WriteAllText($ResultFile, "$Kind`r`n$Text", [Text.Encoding]::UTF8) }
    exit $Code
}
function Note([string]$Text) { Write-Host $Text }
function Would([string]$Text) { Write-Host "DRY RUN: would $Text" }

function Read-Json($path) { Get-Content -LiteralPath $path -Raw | ConvertFrom-Json }
function Get-Settings {
    if (-not (Test-Path -LiteralPath $SettingsFile)) { Finish 'ERR' "settings.json is missing next to the installer's files." 1 }
    $s = Read-Json $SettingsFile
    if (-not $s.ServerAddress -or -not $s.LoginPort) { Finish 'ERR' 'settings.json has no ServerAddress or LoginPort.' 1 }
    return $s
}
function Get-State {
    if (Test-Path -LiteralPath $StateFile) { return Read-Json $StateFile }
    return [pscustomobject]@{}
}
function Save-State($state) {
    if ($DryRun) { Would "write $StateFile"; return }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $StateFile) | Out-Null
    [IO.File]::WriteAllText($StateFile, ($state | ConvertTo-Json) + "`r`n", [Text.Encoding]::ASCII)
}
function Set-StateValue($state, [string]$name, $value) {
    $state | Add-Member -NotePropertyName $name -NotePropertyValue $value -Force
}
function Resolve-ClientDir {
    if (-not $ClientDir) {
        $s = Get-State
        if ($s.ClientDir) { $script:ClientDir = $s.ClientDir } else { Finish 'ERR' 'No client folder given.' 1 }
    }
    if (-not (Test-Path -LiteralPath $ClientDir -PathType Container)) { Finish 'ERR' "The folder $ClientDir does not exist." 2 }
    $script:ClientDir = (Resolve-Path -LiteralPath $ClientDir).Path.TrimEnd([char]92)
}

# --- the client folder ---------------------------------------------------------------------------------
function Test-ClientShape($dir) {
    # The same files the C57 kit's Install-ClientPatch.ps1 requires.
    $missing = @()
    if (-not ((Test-Path -LiteralPath (Join-Path $dir 'SWGEmu.exe')) -or (Test-Path -LiteralPath (Join-Path $dir 'SwgClient_r.exe')))) { $missing += 'SWGEmu.exe' }
    foreach ($f in @('swgemu.cfg', 'swgemu_live.cfg', 'bottom.tre', 'data_other_00.tre', 'patch_14_00.tre')) {
        if (-not (Test-Path -LiteralPath (Join-Path $dir $f))) { $missing += $f }
    }
    return $missing
}
function Test-ClientRunning($dir) {
    $prefix = $dir.TrimEnd([char]92) + [char]92
    return @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.Path -and $_.Path.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase) }).Count -gt 0
}
function Find-Clients {
    $seen = New-Object System.Collections.Generic.List[string]
    $add = { param($d) if ($d -and (Test-Path -LiteralPath (Join-Path $d 'SWGEmu.exe'))) { $d = $d.TrimEnd([char]92); if (-not $seen.Contains($d)) { $seen.Add($d) } } }
    # 1. Shortcuts that start SWGEmu.exe (desktop and Start menu).
    $shell = New-Object -ComObject WScript.Shell
    $places = @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('CommonDesktopDirectory'),
                [Environment]::GetFolderPath('StartMenu'), [Environment]::GetFolderPath('CommonStartMenu'))
    foreach ($p in $places) {
        if (-not $p -or -not (Test-Path -LiteralPath $p)) { continue }
        foreach ($lnk in Get-ChildItem -LiteralPath $p -Filter *.lnk -Recurse -ErrorAction SilentlyContinue) {
            try { $t = $shell.CreateShortcut($lnk.FullName).TargetPath } catch { continue }
            if ($t -and $t -match 'swgemu|swgclient') { & $add (Split-Path -Parent $t) }
        }
    }
    # 2. The usual install folders on every fixed drive.
    $drives = @(Get-PSDrive -PSProvider FileSystem -ErrorAction SilentlyContinue | Where-Object { $_.Root -match '^[A-Z]:\\$' } | ForEach-Object { $_.Root })
    foreach ($root in $drives) {
        foreach ($sub in @('SWGEmu', 'SWGEmu\SWGEmu', 'Games\SWGEmu', 'SWG', 'SWGEmu Client', 'Program Files (x86)\SWGEmu', 'Program Files\SWGEmu',
                           'Program Files (x86)\StarWarsGalaxies', 'Program Files (x86)\Sony\Star Wars Galaxies')) {
            & $add (Join-Path $root $sub)
        }
    }
    # 3. Uninstall entries that look like SWG.
    $keys = @('HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*', 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*',
              'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*')
    foreach ($e in Get-ItemProperty -Path $keys -ErrorAction SilentlyContinue) {
        if ($e.DisplayName -match 'SWG|Star Wars Galaxies' -and $e.InstallLocation) { & $add $e.InstallLocation }
    }
    # Best first: a folder that already has every file the checks need.
    return @($seen | Sort-Object { (Test-ClientShape $_).Count })
}
function Get-MtgNeeds($dir) {
    # The MTG archives the kit requires that the client lacks, or has in another size (another version).
    $m = Read-Json (Join-Path $KitDir 'manifest.json')
    $need = @()
    foreach ($r in $m.requires) {
        $p = Join-Path $dir $r.file
        $why = $null
        if (-not (Test-Path -LiteralPath $p)) { $why = 'missing' }
        elseif ((Get-Item -LiteralPath $p).Length -ne [long]$r.size) { $why = 'a different version' }
        if ($why) { $need += [pscustomobject]@{ File = [string]$r.file; Size = [long]$r.size; Sha256 = [string]$r.sha256; Why = $why } }
    }
    return $need
}
function Get-MtgSizes {
    $sizes = @{}
    foreach ($r in (Read-Json (Join-Path $KitDir 'manifest.json')).requires) { $sizes[[string]$r.file] = [long]$r.size }
    return $sizes
}
function Format-GB([long]$bytes) { return '{0:N1} GB' -f ($bytes / 1GB) }
function Test-Room([long]$bytes) {
    # Setup downloads into its temp folder, then moves the files into the client: across drives that is a copy.
    $need = @{}
    $tmpRoot = [IO.Path]::GetPathRoot([IO.Path]::GetFullPath($env:TEMP))
    $need[$tmpRoot] = $bytes
    $cliRoot = [IO.Path]::GetPathRoot($ClientDir)
    if ($cliRoot -ne $tmpRoot) { $need[$cliRoot] = $bytes }
    foreach ($root in $need.Keys) {
        try { $free = (New-Object IO.DriveInfo($root)).AvailableFreeSpace } catch { continue }
        $want = $need[$root] + 1GB
        if ($free -lt $want) { return "Not enough free space on $root for the MTG download: it needs $(Format-GB $want), and $(Format-GB $free) is free." }
    }
    return $null
}
function Invoke-Check {
    Resolve-ClientDir
    $s = Get-Settings
    $missing = Test-ClientShape $ClientDir
    if ($missing.Count -gt 0) {
        Finish 'ERR' ("$ClientDir is not a SWGEmu client folder (missing: $($missing -join ', ')).`r`n`r`n" +
            "Pick the folder that holds SWGEmu.exe. If you don't have SWGEmu yet, install it first: $($s.ClientHelpUrl)") 2
    }
    if (Test-ClientRunning $ClientDir) { Finish 'ERR' 'The game (or its launcher) is running. Close it and click Next again.' 5 }
    $need = @(Get-MtgNeeds $ClientDir)
    if ($need.Count -gt 0) {
        $list = ($need | ForEach-Object { "$($_.File) ($($_.Why))" }) -join "`r`n  "
        if (-not $s.MtgBaseUrl) {
            Finish 'ERR' ("Your client is missing the Mod The Galaxy (MTG) archives our server is built on:`r`n  " + $list +
                "`r`n`r`nGet them here: $($s.MtgHelpUrl)`r`nCopy them into $ClientDir and run Setup again.") 3
        }
        $bytes = [long]($need | Measure-Object -Property Size -Sum).Sum
        $short = Test-Room $bytes
        if ($short) { Finish 'ERR' $short 6 }
        if ($MtgListFile) {
            # One line per file for Setup's download page: url, file name, sha256 (Setup checks it), tab-separated.
            $base = ([string]$s.MtgBaseUrl).TrimEnd('/')
            $lines = $need | ForEach-Object { "$base/$([Uri]::EscapeDataString($_.File))`t$($_.File)`t$($_.Sha256)" }
            [IO.File]::WriteAllText($MtgListFile, (($lines -join "`r`n") + "`r`n"), [Text.Encoding]::ASCII)
        }
        $own = ''
        if (@($need | Where-Object { $_.Why -ne 'missing' }).Count -gt 0) {
            $own = "`r`n`r`nYour own copies of the files marked 'a different version' are kept in $ClientDir\local_planets-patch\backup and go back when you uninstall."
        }
        Finish 'WARN' ("Your client needs $($need.Count) of the Mod The Galaxy (MTG) archives the server is built on ($(Format-GB $bytes)):`r`n  " + $list +
            "`r`n`r`nSetup downloads them from Miniverse after it joins the owner's network. Miniverse must be on and sharing them; " +
            "depending on the owner's upload speed this can take up to an hour or two." + $own) 4
    }
    Finish 'OK' "$ClientDir has everything the server needs." 0
}
function Invoke-PlaceMtg {
    Resolve-ClientDir
    if (Test-ClientRunning $ClientDir) { Finish 'ERR' 'The game (or its launcher) is running. Close it, then click Install again.' 5 }
    if (-not $From -or -not (Test-Path -LiteralPath $From -PathType Container)) { Finish 'ERR' 'No download folder given.' 1 }
    $state = Get-State
    $added = @($state.MtgAdded | Where-Object { $_ })
    $replaced = @($state.MtgReplaced | Where-Object { $_ })
    $backup = Join-Path $ClientDir 'local_planets-patch\backup\friends-installer\mtg'
    $need = @(Get-MtgNeeds $ClientDir)
    # Every download first, so a missing one changes nothing in the client.
    foreach ($n in $need) {
        $src = Join-Path $From $n.File
        if (-not (Test-Path -LiteralPath $src) -or (Get-Item -LiteralPath $src).Length -ne $n.Size) {
            Finish 'ERR' "The download of $($n.File) is missing or incomplete. Run Setup again." 1
        }
    }
    if ($DryRun) {
        foreach ($n in $need) { Would "move the downloaded $($n.File) into $ClientDir$(if ($n.Why -ne 'missing') { ', after saving your own copy to ' + $backup })" }
        Finish 'OK' 'Dry run: MTG archives checked.' 0
    }
    $placed = 0
    try {
        foreach ($n in $need) {
            $dest = Join-Path $ClientDir $n.File
            if (Test-Path -LiteralPath $dest) {
                # The friend's own, different version: keep it for the uninstaller (once; a later copy is not theirs).
                New-Item -ItemType Directory -Force -Path $backup | Out-Null
                $saved = Join-Path $backup $n.File
                if (Test-Path -LiteralPath $saved) { Remove-Item -LiteralPath $dest -Force }
                else { Move-Item -LiteralPath $dest -Destination $saved }
                if ($replaced -notcontains $n.File) { $replaced += $n.File }
            } elseif ($added -notcontains $n.File -and $replaced -notcontains $n.File) { $added += $n.File }
            Move-Item -LiteralPath (Join-Path $From $n.File) -Destination $dest
            $placed++
        }
    } finally {
        # Recorded even if a move fails part way, so the uninstaller still knows what to undo.
        Set-StateValue $state 'ClientDir' $ClientDir
        Set-StateValue $state 'MtgAdded' ([string[]]$added)
        Set-StateValue $state 'MtgReplaced' ([string[]]$replaced)
        Save-State $state
    }
    Finish 'OK' "Placed $placed MTG archives in $ClientDir." 0
}

# --- Tailscale -----------------------------------------------------------------------------------------
function Get-TailscaleStatus {
    if (-not (Test-Path -LiteralPath $TailscaleExe)) { return $null }
    try { return (& $TailscaleExe status --json 2>$null | Out-String | ConvertFrom-Json) } catch { return $null }
}
function Test-TailscaleSigned([string]$path) {
    $sig = Get-AuthenticodeSignature -LiteralPath $path
    return ($sig.Status -eq 'Valid' -and $sig.SignerCertificate.Subject -match '(^|,\s*)CN="?Tailscale Inc\.')
}
function Install-Tailscale($s, $state) {
    $arch = 'amd64'
    if ($env:PROCESSOR_ARCHITECTURE -eq 'ARM64' -or $env:PROCESSOR_ARCHITEW6432 -eq 'ARM64') { $arch = 'arm64' }
    $url = "https://pkgs.tailscale.com/stable/tailscale-setup-latest-$arch.msi"
    if ($DryRun) { Would "download $url, check it is signed by Tailscale Inc., and install it silently"; return }
    $dir = Join-Path $env:TEMP ('swg-friends-ts-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $dir | Out-Null
    $msi = Join-Path $dir "tailscale-setup-$arch.msi"
    try {
        Note "Downloading Tailscale from $url"
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $url -OutFile $msi -UseBasicParsing
        if (-not (Test-TailscaleSigned $msi)) { Finish 'ERR' 'The Tailscale download is not signed by Tailscale Inc. Nothing was installed. Try again later, or tell the server owner.' 1 }
        Note 'Signed by Tailscale Inc. Installing.'
        $p = Start-Process -FilePath "$env:SystemRoot\System32\msiexec.exe" -ArgumentList @('/i', "`"$msi`"", '/quiet', '/norestart') -Wait -PassThru
        if ($p.ExitCode -ne 0 -and $p.ExitCode -ne 3010) { Finish 'ERR' "The Tailscale installer stopped with code $($p.ExitCode)." 1 }
    } finally {
        Remove-Item -LiteralPath $dir -Recurse -Force -ErrorAction SilentlyContinue
    }
    Set-StateValue $state 'TailscaleInstalledBySetup' $true
}
function Wait-Tailscale([int]$seconds, [string[]]$states) {
    $until = (Get-Date).AddSeconds($seconds)
    do {
        $st = Get-TailscaleStatus
        if ($st -and $states -contains $st.BackendState) { return $st }
        Start-Sleep -Seconds 2
    } while ((Get-Date) -lt $until)
    return Get-TailscaleStatus
}
function Read-Key {
    if (-not $KeyFile -or -not (Test-Path -LiteralPath $KeyFile)) { return $null }
    try { $k = ([IO.File]::ReadAllText($KeyFile)).Trim() }
    finally {
        # Overwrite, then delete: the key never stays on disk.
        try { $len = (Get-Item -LiteralPath $KeyFile).Length; [IO.File]::WriteAllBytes($KeyFile, (New-Object byte[] $len)) } catch {}
        Remove-Item -LiteralPath $KeyFile -Force -ErrorAction SilentlyContinue
    }
    if ($k -eq '') { return $null }
    return $k
}
function Invoke-Tailscale {
    $s = Get-Settings
    $key = Read-Key
    if ($key -and $key -notmatch '^tskey-[A-Za-z0-9_-]+$') { Finish 'ERR' 'That does not look like an invite key (it starts with tskey-). Copy the whole key from the owner''s message.' 1 }
    $state = Get-State
    if (-not (Test-Path -LiteralPath $TailscaleExe)) { Install-Tailscale $s $state }
    else { Note 'Tailscale is already installed.' }
    if ($DryRun) {
        if ($key) { Would 'run tailscale up with the invite key (the key is not shown)' } else { Would 'use the Tailscale connection that is already there' }
        Finish 'OK' 'Dry run: Tailscale step checked.' 0
    }
    if (-not (Get-Service -Name Tailscale -ErrorAction SilentlyContinue)) { Finish 'ERR' 'Tailscale installed, but its service is missing. Restart the PC and run Setup again.' 1 }
    $st = Wait-Tailscale 30 @('Running', 'NeedsLogin', 'Stopped', 'NoState')
    if ($st -and $st.BackendState -eq 'Running' -and (Test-Login $s).Ok) {
        Save-State $state
        Finish 'OK' 'Tailscale is connected to the owner''s network already.' 0
    }
    if (-not $key) { Finish 'ERR' 'Paste the invite key the server owner sent you (Back, then the invite key page).' 1 }
    # Already signed in to another Tailscale network: add the owner's as a second account instead of replacing it.
    $verb = 'up'
    if ($st -and $st.BackendState -eq 'Running') { $verb = 'login' }
    $out = Join-Path $env:TEMP ('swg-friends-ts-' + [guid]::NewGuid().ToString('N') + '.txt')
    $p = Start-Process -FilePath $TailscaleExe -ArgumentList @($verb, "--auth-key=$key", '--timeout=60s') -NoNewWindow -Wait -PassThru -RedirectStandardError $out
    $key = $null
    $err = ''
    if (Test-Path -LiteralPath $out) { $err = (Get-Content -LiteralPath $out -Raw); Remove-Item -LiteralPath $out -Force }
    if ($p.ExitCode -ne 0) {
        if ($err -match 'invalid key|expired|not valid') { Finish 'ERR' 'Tailscale did not accept the invite key (used before, or expired). Ask the server owner for a new one.' 1 }
        Finish 'ERR' "Tailscale could not join the owner's network (code $($p.ExitCode)). Ask the server owner for a new invite key." 1
    }
    $st = Wait-Tailscale 30 @('Running')
    Set-StateValue $state 'TailscaleJoined' (Get-Date).ToString('yyyy-MM-dd h:mm tt')
    Save-State $state
    Finish 'OK' 'Joined the owner''s network.' 0
}
function Invoke-TailscaleLogout {
    if (-not (Test-Path -LiteralPath $TailscaleExe)) { Finish 'OK' 'Tailscale is not installed.' 0 }
    if ($DryRun) { Would 'run tailscale logout'; Finish 'OK' 'Dry run.' 0 }
    & $TailscaleExe logout 2>$null | Out-Null
    Finish 'OK' 'Logged out of Tailscale.' 0
}
function Invoke-TailscaleRemove {
    $keys = @('HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*', 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*')
    $e = @(Get-ItemProperty -Path $keys -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -eq 'Tailscale' -and $_.UninstallString }) | Select-Object -First 1
    if (-not $e) { Finish 'OK' 'Tailscale is not installed.' 0 }
    if ($DryRun) { Would "uninstall Tailscale ($($e.PSChildName))"; Finish 'OK' 'Dry run.' 0 }
    if (Test-Path -LiteralPath $TailscaleExe) { & $TailscaleExe logout 2>$null | Out-Null }
    if ($e.PSChildName -match '^\{[0-9A-Fa-f-]+\}$') {
        $p = Start-Process -FilePath "$env:SystemRoot\System32\msiexec.exe" -ArgumentList @('/x', $e.PSChildName, '/quiet', '/norestart') -Wait -PassThru
    } elseif ($e.QuietUninstallString) {
        $p = Start-Process -FilePath "$env:ComSpec" -ArgumentList @('/c', $e.QuietUninstallString) -Wait -PassThru
    } else {
        $p = Start-Process -FilePath "$env:ComSpec" -ArgumentList @('/c', $e.UninstallString + ' /quiet') -Wait -PassThru
    }
    if ($p.ExitCode -ne 0 -and $p.ExitCode -ne 3010) { Finish 'WARN' "Tailscale's uninstaller stopped with code $($p.ExitCode). Remove it from Settings > Apps." 1 }
    Finish 'OK' 'Tailscale removed.' 0
}

# --- the server's login port ---------------------------------------------------------------------------
function Test-Login($s) {
    # One SOE "session request" (opcode 00 01, CRC length 2, a random connection id, 496-byte packets). A Core3
    # login server answers with a session response (00 02). The half-open session times out on the server.
    $result = [pscustomobject]@{ Ok = $false; Text = '' }
    try { $ip = @([Net.Dns]::GetHostAddresses([string]$s.ServerAddress) | Where-Object { $_.AddressFamily -eq 'InterNetwork' })[0] }
    catch { $result.Text = "cannot find $($s.ServerAddress) (is Tailscale connected?)"; return $result }
    if (-not $ip) { $result.Text = "cannot find $($s.ServerAddress)"; return $result }
    $id = New-Object byte[] 4; (New-Object Random).NextBytes($id)
    $pkt = [byte[]](@(0, 1, 0, 0, 0, 2) + $id + @(0, 0, 1, 0xF0))
    $udp = New-Object Net.Sockets.UdpClient
    try {
        $udp.Client.ReceiveTimeout = 3000
        for ($try = 1; $try -le 2; $try++) {
            [void]$udp.Send($pkt, $pkt.Length, (New-Object Net.IPEndPoint($ip, [int]$s.LoginPort)))
            try {
                $from = New-Object Net.IPEndPoint([Net.IPAddress]::Any, 0)
                $r = $udp.Receive([ref]$from)
                if ($r.Length -ge 2 -and $r[0] -eq 0 -and $r[1] -eq 2) { $result.Ok = $true; $result.Text = "the login server at $ip`:$($s.LoginPort) answered"; return $result }
            } catch {}
        }
    } finally { $udp.Close() }
    $result.Text = "no answer from $ip`:$($s.LoginPort) (the server may be off, or Tailscale is not connected)"
    return $result
}
function Invoke-Probe {
    $r = Test-Login (Get-Settings)
    if ($r.Ok) { Finish 'OK' "Connected: $($r.Text)." 0 }
    Finish 'WARN' "Not reachable yet: $($r.Text)." 7
}

# --- the client patch and the login line ---------------------------------------------------------------
function Get-LoginText($s) {
    return "$LoginMarker; the uninstaller puts your own file back.`r`n[ClientGame]`r`nloginServerAddress0=$($s.ServerAddress)`r`nloginServerPort0=$($s.LoginPort)`r`n"
}
function Set-Login($s, $state) {
    $path = Join-Path $ClientDir 'swgemu_login.cfg'
    $want = Get-LoginText $s
    $have = ''
    if (Test-Path -LiteralPath $path) { $have = [IO.File]::ReadAllText($path, $Latin1) }
    if ($have -eq $want) { Note 'The login already points at the server.'; return }
    $backup = Join-Path $ClientDir 'local_planets-patch\backup\friends-installer'
    $saved = Join-Path $backup 'swgemu_login.cfg'
    if ($DryRun) { Would "save swgemu_login.cfg to $backup and point the login at $($s.ServerAddress):$($s.LoginPort)"; return }
    if (-not $have.StartsWith($LoginMarker) -and (Test-Path -LiteralPath $path)) {
        New-Item -ItemType Directory -Force -Path $backup | Out-Null
        if (-not (Test-Path -LiteralPath $saved)) { Copy-Item -LiteralPath $path -Destination $saved }
    }
    [IO.File]::WriteAllText($path, $want, $Latin1)
    Set-StateValue $state 'LoginReplaced' $true
    $main = [IO.File]::ReadAllText((Join-Path $ClientDir 'swgemu.cfg'), $Latin1)
    if ($main -notmatch '(?mi)^\s*\.include\s+"swgemu_login\.cfg"') { Note 'Note: swgemu.cfg does not include swgemu_login.cfg; the login line may be ignored.' }
}
function Invoke-KitInstall {
    $kit = Join-Path $KitDir 'Install-ClientPatch.ps1'
    if ($DryRun) {
        Would "run the client patch kit ($kit) on $ClientDir"
        return
    }
    $out = & "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File $kit -ClientDir $ClientDir -AllowDowngrade 2>&1 | Out-String
    # -AllowDowngrade: the launcher may have installed a newer server patch since; this kit's goes back in and the
    # launcher brings the server's current one again on its next start.
    $code = $LASTEXITCODE
    Note $out.Trim()
    if ($code -ne 0) { Finish 'ERR' ("The client patch did not install:`r`n" + $out.Trim()) $code }
}
function Invoke-Patch {
    Resolve-ClientDir
    $s = Get-Settings
    $state = Get-State
    Invoke-KitInstall
    Set-Login $s $state
    Set-StateValue $state 'ClientDir' $ClientDir
    Set-StateValue $state 'Installed' (Get-Date).ToString('yyyy-MM-dd h:mm tt')
    Save-State $state
    Finish 'OK' "Client patch installed and the login points at $($s.ServerAddress):$($s.LoginPort)." 0
}
# The launcher's graphics add-on (DXVK and the O15 hook), from its record local_planets-patch\addon.json: take out the
# files it added and put back the friend's own ones it replaced. A file that changed since (not the add-on's copy) stays.
function Undo-Addon {
    $rec = Join-Path $ClientDir 'local_planets-patch\addon.json'
    if (-not (Test-Path -LiteralPath $rec)) { return @() }
    $r = Read-Json $rec
    $added = @($r.added | Where-Object { $_ })
    $keep = Join-Path $ClientDir 'local_planets-patch\backup\friends-installer\addon'
    $done = @()
    foreach ($name in 'd3d9.dll', 'dxvk_d3d9.dll', 'mirage.ini', 'dxvk.conf') {
        $p = Join-Path $ClientDir $name
        $saved = Join-Path $keep $name
        if (-not (Test-Path -LiteralPath $p)) { continue }
        $ours = if ($name -like '*.dll') { (Get-FileHash -Algorithm SHA256 -LiteralPath $p).Hash.ToLower() -eq $r.sha256.$name } else { $added -contains $name }
        if (-not $ours) { continue }
        if (Test-Path -LiteralPath $saved) {
            if ($DryRun) { Would "put back your own $name" } else { Copy-Item -LiteralPath $saved -Destination $p -Force }
            $done += $name
        } elseif ($added -contains $name) {
            if ($DryRun) { Would "remove $name (the graphics add-on)" } else { Remove-Item -LiteralPath $p -Force }
            $done += $name
        }
    }
    if ($added -contains 'd3d9.dll') {
        # Logs only the add-on writes (there was no d3d9.dll before it).
        foreach ($log in @(Get-ChildItem -LiteralPath $ClientDir -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^(mirage\.log|mirage-draws-\d+\.log|.*_d3d9\.log)$' })) {
            if ($DryRun) { Would "remove $($log.Name)" } else { Remove-Item -LiteralPath $log.FullName -Force }
        }
    }
    if (-not $DryRun) { Remove-Item -LiteralPath $rec -Force }
    if ($done) { return @("Took the graphics add-on out ($($done -join ', ')).") }
    return @()
}
function Invoke-Uninstall {
    Resolve-ClientDir
    $state = Get-State
    $msgs = @()
    $kit = Join-Path $KitDir 'Uninstall-ClientPatch.ps1'
    if (Test-ClientRunning $ClientDir) { Finish 'ERR' 'The game is running. Close it, then uninstall again.' 5 }
    $msgs += Undo-Addon
    if ($DryRun) { Would "run $kit on $ClientDir" }
    else {
        $out = & "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File $kit -ClientDir $ClientDir 2>&1 | Out-String
        $msgs += $out.Trim()
    }
    $path = Join-Path $ClientDir 'swgemu_login.cfg'
    $saved = Join-Path $ClientDir 'local_planets-patch\backup\friends-installer\swgemu_login.cfg'
    $ours = (Test-Path -LiteralPath $path) -and ([IO.File]::ReadAllText($path, $Latin1).StartsWith($LoginMarker))
    if ($ours) {
        if ($DryRun) { Would 'put back your own swgemu_login.cfg' }
        elseif (Test-Path -LiteralPath $saved) { Copy-Item -LiteralPath $saved -Destination $path -Force; $msgs += 'Restored your own swgemu_login.cfg.' }
        else { Remove-Item -LiteralPath $path; $msgs += 'Removed the login file the installer wrote (there was none before).' }
    }
    # MTG archives: remove the ones Setup added (only if still the size it downloaded), put the friend's own back.
    $sizes = Get-MtgSizes
    $gone = 0; $back = 0
    foreach ($f in @($state.MtgAdded | Where-Object { $_ })) {
        $p = Join-Path $ClientDir $f
        if ((Test-Path -LiteralPath $p) -and (Get-Item -LiteralPath $p).Length -eq $sizes[$f]) {
            if ($DryRun) { Would "remove $f (Setup downloaded it)" } else { Remove-Item -LiteralPath $p -Force }
            $gone++
        }
    }
    $backup = Join-Path $ClientDir 'local_planets-patch\backup\friends-installer\mtg'
    foreach ($f in @($state.MtgReplaced | Where-Object { $_ })) {
        $saved = Join-Path $backup $f
        if (Test-Path -LiteralPath $saved) {
            if ($DryRun) { Would "put back your own $f" } else { Move-Item -LiteralPath $saved -Destination (Join-Path $ClientDir $f) -Force }
            $back++
        }
    }
    if ($gone) { $msgs += "Removed $gone MTG archives Setup had downloaded." }
    if ($back) { $msgs += "Put back your own copies of $back MTG archives." }
    Finish 'OK' ($msgs -join "`r`n") 0
}
function Invoke-Play {
    Add-Type -AssemblyName System.Windows.Forms
    Resolve-ClientDir
    $s = Get-Settings
    $state = Get-State
    if (Test-ClientRunning $ClientDir) { [void][Windows.Forms.MessageBox]::Show('The game is already running.', 'SWG'); exit 0 }
    # The SWGEmu launcher can reset swgemu.cfg and swgemu_login.cfg; put our lines back first.
    $main = [IO.File]::ReadAllText((Join-Path $ClientDir 'swgemu.cfg'), $Latin1)
    if ($main -notmatch '(?m)^\s*\.include\s+"local_planets\.cfg"') { Invoke-KitInstall }
    Set-Login $s $state
    $r = Test-Login $s
    if (-not $r.Ok) {
        $go = [Windows.Forms.MessageBox]::Show("The server is not answering: $($r.Text).`r`n`r`nCheck that Tailscale is connected (its icon by the clock) and that the owner has the server on.`r`n`r`nStart the game anyway?", 'SWG', 'YesNo', 'Warning')
        if ($go -ne 'Yes') { exit 7 }
    }
    if ($DryRun) { Would "start $ClientDir\SWGEmu.exe"; exit 0 }
    Start-Process -FilePath (Join-Path $ClientDir 'SWGEmu.exe') -WorkingDirectory $ClientDir
    exit 0
}

switch ($Action) {
    'Detect' {
        $found = Find-Clients
        if ($found.Count -eq 0) { Finish 'WARN' 'No SWGEmu client found.' 2 }
        Finish 'OK' ($found -join "`r`n") 0
    }
    'Check' { Invoke-Check }
    'Tailscale' { Invoke-Tailscale }
    'PlaceMtg' { Invoke-PlaceMtg }
    'Patch' { Invoke-Patch }
    'Probe' { Invoke-Probe }
    'Play' { Invoke-Play }
    'Uninstall' { Invoke-Uninstall }
    'TailscaleLogout' { Invoke-TailscaleLogout }
    'TailscaleRemove' { Invoke-TailscaleRemove }
}
