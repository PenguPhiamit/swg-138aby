<#
.SYNOPSIS
  Offline test of friend-setup.ps1 and mtg-share.py on a dummy client folder with a dummy kit. Downloads nothing
  from outside this PC, installs nothing.
    powershell -NoProfile -ExecutionPolicy Bypass -File test-friend-setup.ps1 [-ProbeAddress 192.168.1.210]
  -ProbeAddress also sends one UDP session request to that address's login port (read-only).
  mtg-share.py runs on 127.0.0.1:43499 for a few seconds (needs python on PATH).
#>
param([string]$ProbeAddress, [switch]$Keep, [string]$Launcher)   # -Keep leaves the dummy folders in %TEMP% for a look; -Launcher tests another FracturedGalaxy.exe than build\out's
$ErrorActionPreference = 'Stop'
$here = $PSScriptRoot
$root = Join-Path $env:TEMP ('friend-setup-test-' + [guid]::NewGuid().ToString('N'))
$kit = Join-Path $root 'kit'; $client = Join-Path $root 'client'; $app = Join-Path $root 'app'; $share = Join-Path $root 'share'; $dl = Join-Path $root 'dl'
New-Item -ItemType Directory -Force -Path $kit, $client, $app, $share, $dl | Out-Null
$ps = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
$port = 43499
$script:fails = 0
$plain = Join-Path $root 'settings.json'; $withMtg = Join-Path $root 'settings-mtg.json'
$script:settings = $plain
function Check($name, $ok) { if ($ok) { Write-Host "PASS $name" } else { Write-Host "FAIL $name" -ForegroundColor Red; $script:fails++ } }
function Run([string[]]$a) {
    $res = Join-Path $root 'result.txt'; Remove-Item -LiteralPath $res -ErrorAction SilentlyContinue
    $out = & $ps -NoProfile -ExecutionPolicy Bypass -File (Join-Path $here 'friend-setup.ps1') @a -SettingsFile $script:settings -KitDir $kit -StateFile (Join-Path $app 'state.json') -ResultFile $res 2>&1 | Out-String
    $text = ''; if (Test-Path -LiteralPath $res) { $text = [IO.File]::ReadAllText($res) }
    return [pscustomobject]@{ Code = $LASTEXITCODE; Out = $out; Result = $text }
}
function Sha($p) { (Get-FileHash -Algorithm SHA256 -LiteralPath $p).Hash.ToLower() }
function Snapshot($dir) { Get-ChildItem -LiteralPath $dir -Recurse | ForEach-Object { "$($_.FullName)|$($_.Length)" } }
function Len($p) { if (Test-Path -LiteralPath $p) { (Get-Item -LiteralPath $p).Length } else { -1 } }
try {
    # A dummy kit: the real installer scripts, a fake archive, two fake MTG requirements (the owner's share has both).
    Copy-Item (Join-Path $here '..\client_patch\Install-ClientPatch.ps1'), (Join-Path $here '..\client_patch\Uninstall-ClientPatch.ps1') $kit
    [IO.File]::WriteAllBytes((Join-Path $kit 'local_planets.tre'), [byte[]](1..200 | ForEach-Object { $_ % 256 }))
    [IO.File]::WriteAllBytes((Join-Path $share 'mtg_patch_001.tre'), [byte[]](1..10))
    [IO.File]::WriteAllBytes((Join-Path $share 'mtg_planets.tre'), [byte[]](1..20))
    $m = [ordered]@{ format = 1; name = 'local_planets'; version = '2026.10.17.1'
        archive = [ordered]@{ file = 'local_planets.tre'; size = 200; sha256 = (Sha (Join-Path $kit 'local_planets.tre')); priority = 49 }
        requires = @([ordered]@{ file = 'mtg_patch_001.tre'; priority = 1; size = 10; sha256 = (Sha (Join-Path $share 'mtg_patch_001.tre')) },
                     [ordered]@{ file = 'mtg_planets.tre'; priority = 21; size = 20; sha256 = (Sha (Join-Path $share 'mtg_planets.tre')) }) }
    [IO.File]::WriteAllText((Join-Path $kit 'manifest.json'), ($m | ConvertTo-Json -Depth 5))
    $addr = if ($ProbeAddress) { $ProbeAddress } else { '192.0.2.1' }
    [IO.File]::WriteAllText($plain, (@{ ServerAddress = $addr; LoginPort = 46453; MtgHelpUrl = 'https://example.invalid/mtg'; ClientHelpUrl = 'https://www.swgemu.com/' } | ConvertTo-Json))
    [IO.File]::WriteAllText($withMtg, (@{ ServerAddress = $addr; LoginPort = 46453; MtgBaseUrl = "http://127.0.0.1:$port/"; ClientHelpUrl = 'https://www.swgemu.com/' } | ConvertTo-Json))

    # A dummy client: the shape the kit wants, the user's own login file, one MTG archive missing.
    foreach ($f in 'SWGEmu.exe', 'bottom.tre', 'data_other_00.tre', 'patch_14_00.tre', 'swgemu_live.cfg') { Set-Content -LiteralPath (Join-Path $client $f) -Value 'x' }
    Set-Content -LiteralPath (Join-Path $client 'swgemu.cfg') -Value ".include `"swgemu_login.cfg`"`r`n.include `"swgemu_live.cfg`"`r`n[SharedFile]`r`nmaxSearchPriority=50" -NoNewline
    Set-Content -LiteralPath (Join-Path $client 'swgemu_login.cfg') -Value "[ClientGame]`r`nloginServerAddress0=login.swgemu.com`r`nloginServerPort0=44453`r`n" -NoNewline
    [IO.File]::WriteAllBytes((Join-Path $client 'mtg_patch_001.tre'), (New-Object byte[] 10))

    $r = Run @('-Action', 'Check', '-ClientDir', $root); Check 'Check refuses a folder without SWGEmu.exe' ($r.Code -eq 2 -and $r.Result -match 'swgemu.com')
    $r = Run @('-Action', 'Check', '-ClientDir', $client); Check 'Check without MtgBaseUrl names the missing MTG archive and the link' ($r.Code -eq 3 -and $r.Result -match 'mtg_planets.tre \(missing\)' -and $r.Result -match 'example.invalid/mtg')
    [IO.File]::WriteAllBytes((Join-Path $client 'mtg_planets.tre'), (New-Object byte[] 5))
    $r = Run @('-Action', 'Check', '-ClientDir', $client); Check 'Check notices a wrong-size archive' ($r.Code -eq 3 -and $r.Result -match 'different version')
    [IO.File]::WriteAllBytes((Join-Path $client 'mtg_planets.tre'), (New-Object byte[] 20))
    $r = Run @('-Action', 'Check', '-ClientDir', $client); Check 'Check passes a complete client' ($r.Code -eq 0)

    # The MTG download: the friend has another version of one archive and lacks the other.
    [IO.File]::WriteAllBytes((Join-Path $client 'mtg_patch_001.tre'), [byte[]](1..7))
    Remove-Item -LiteralPath (Join-Path $client 'mtg_planets.tre')
    $script:settings = $withMtg
    $list = Join-Path $root 'mtg-needed.txt'
    $r = Run @('-Action', 'Check', '-ClientDir', $client, '-MtgListFile', $list)
    $lines = @(Get-Content -LiteralPath $list -ErrorAction SilentlyContinue)
    $want0 = "http://127.0.0.1:$port/mtg_patch_001.tre`tmtg_patch_001.tre`t$($m.requires[0].sha256)"
    Check 'Check with MtgBaseUrl lists both archives with link and sha256 (exit 4)' ($r.Code -eq 4 -and $lines.Count -eq 2 -and $lines[0] -eq $want0 -and $lines[1] -match '/mtg_planets\.tre\tmtg_planets\.tre\t[0-9a-f]{64}$' -and $r.Result -match 'kept in')
    Copy-Item (Join-Path $share '*.tre') $dl
    $before = Snapshot $client
    $r = Run @('-Action', 'PlaceMtg', '-ClientDir', $client, '-From', $dl, '-DryRun')
    Check 'PlaceMtg -DryRun changes nothing' ($r.Code -eq 0 -and (Compare-Object @($before) @(Snapshot $client)) -eq $null -and (Len (Join-Path $dl 'mtg_planets.tre')) -eq 20)
    Remove-Item -LiteralPath (Join-Path $dl 'mtg_planets.tre')
    $r = Run @('-Action', 'PlaceMtg', '-ClientDir', $client, '-From', $dl)
    Check 'PlaceMtg stops on an incomplete download and changes nothing' ($r.Code -eq 1 -and $r.Result -match 'mtg_planets.tre' -and (Compare-Object @($before) @(Snapshot $client)) -eq $null)
    Copy-Item (Join-Path $share 'mtg_planets.tre') $dl
    $r = Run @('-Action', 'PlaceMtg', '-ClientDir', $client, '-From', $dl)
    $st = Get-Content -Raw (Join-Path $app 'state.json') | ConvertFrom-Json
    $bk = Join-Path $client 'local_planets-patch\backup\friends-installer\mtg'
    if ($Keep) { Write-Host "  PlaceMtg: code $($r.Code); $($r.Result -replace "`r`n", ' / '); client 001=$(Len (Join-Path $client 'mtg_patch_001.tre')) planets=$(Len (Join-Path $client 'mtg_planets.tre')); backup 001=$(Len (Join-Path $bk 'mtg_patch_001.tre')); added=$($st.MtgAdded -join ','); replaced=$($st.MtgReplaced -join ',')" }
    Check 'PlaceMtg moves the downloads in and keeps the friend''s own version' ($r.Code -eq 0 -and (Len (Join-Path $client 'mtg_patch_001.tre')) -eq 10 -and (Len (Join-Path $client 'mtg_planets.tre')) -eq 20 -and
        (Len (Join-Path $bk 'mtg_patch_001.tre')) -eq 7 -and @($st.MtgAdded) -contains 'mtg_planets.tre' -and @($st.MtgReplaced) -contains 'mtg_patch_001.tre' -and -not (Test-Path (Join-Path $dl 'mtg_planets.tre')))
    $r = Run @('-Action', 'Check', '-ClientDir', $client, '-MtgListFile', $list); Check 'Check passes after the download' ($r.Code -eq 0)
    $script:settings = $plain

    $before = Snapshot $client; $stBefore = Get-Content -Raw (Join-Path $app 'state.json')
    $r = Run @('-Action', 'Patch', '-ClientDir', $client, '-DryRun')
    Check 'Patch -DryRun changes nothing' ($r.Code -eq 0 -and (Compare-Object @($before) @(Snapshot $client)) -eq $null -and (Get-Content -Raw (Join-Path $app 'state.json')) -eq $stBefore)

    $key = Join-Path $root 'invite.txt'; Set-Content -LiteralPath $key -Value 'tskey-auth-TESTONLY0000-notarealkey' -NoNewline
    $r = Run @('-Action', 'Tailscale', '-KeyFile', $key, '-DryRun')
    Check 'Tailscale -DryRun deletes the key file and never prints the key' (-not (Test-Path $key) -and $r.Out -notmatch 'TESTONLY' -and $r.Result -notmatch 'TESTONLY')
    Set-Content -LiteralPath $key -Value 'not-a-key' -NoNewline
    $r = Run @('-Action', 'Tailscale', '-KeyFile', $key, '-DryRun'); Check 'Tailscale refuses a non-key' ($r.Code -eq 1 -and -not (Test-Path $key))

    $r = Run @('-Action', 'Patch', '-ClientDir', $client)
    $login = [IO.File]::ReadAllText((Join-Path $client 'swgemu_login.cfg'))
    Check 'Patch installs the kit and points the login at the server' ($r.Code -eq 0 -and (Test-Path (Join-Path $client 'local_planets.tre')) -and $login -match "loginServerAddress0=$([regex]::Escape($addr))" -and $login -match 'loginServerPort0=46453')
    Check 'Patch keeps the friend''s own login file' ((Get-Content -Raw (Join-Path $client 'local_planets-patch\backup\friends-installer\swgemu_login.cfg')) -match 'login.swgemu.com')
    $r = Run @('-Action', 'Patch', '-ClientDir', $client); Check 'Patch again is harmless' ($r.Code -eq 0)
    $st = Get-Content -Raw (Join-Path $app 'state.json') | ConvertFrom-Json
    Check 'state.json records the client folder and keeps the MTG record' ($st.ClientDir -eq $client -and @($st.MtgAdded) -contains 'mtg_planets.tre')

    # The SWGEmu launcher puts its stock cfg files back (archive cap 26) after the Fractured Galaxy launcher installed
    # a newer local_planets.tre than the kit's. -LayoutOnly (what the launcher runs) must move the layout up again and
    # leave the newer archive and its version alone.
    $tre = Join-Path $client 'local_planets.tre'; $kitStateFile = Join-Path $client 'local_planets-patch\state.json'
    [IO.File]::WriteAllBytes($tre, [byte[]](1..300 | ForEach-Object { ($_ * 7) % 256 }))
    $newer = Sha $tre
    $ks = Get-Content -Raw $kitStateFile | ConvertFrom-Json
    $ks.version = '2026.10.18.5'; $ks.sha256 = $newer
    [IO.File]::WriteAllText($kitStateFile, ($ks | ConvertTo-Json))
    function Reset-Cfg {
        Set-Content -LiteralPath (Join-Path $client 'swgemu.cfg') -Value ".include `"swgemu_login.cfg`"`r`n.include `"swgemu_live.cfg`"`r`n" -NoNewline
        Set-Content -LiteralPath (Join-Path $client 'swgemu_live.cfg') -NoNewline -Value ("[SharedFile]`r`n`tmaxSearchPriority=26`r`n`tsearchTree_00_25=patch_14_00.tre`r`n" +
            "`tsearchTree_00_2=data_other_00.tre`r`n`tsearchTree_00_0=bottom.tre`r`n")
    }
    function Test-Layout {
        $live = [IO.File]::ReadAllText((Join-Path $client 'swgemu_live.cfg')); $main = [IO.File]::ReadAllText((Join-Path $client 'swgemu.cfg'))
        $k = Get-Content -Raw $kitStateFile | ConvertFrom-Json
        return ($live -match 'maxSearchPriority=50' -and $live -match 'searchTree_00_49=patch_14_00\.tre' -and $live -match 'searchTree_00_24=bottom\.tre' -and
            $main -match '(?m)^\.include "local_planets\.cfg"' -and (Sha $tre) -eq $newer -and $k.version -eq '2026.10.18.5' -and $k.sha256 -eq $newer -and $k.live_cfg_moved)
    }
    Reset-Cfg
    $plainKit = Join-Path $root 'kit-plain'; New-Item -ItemType Directory -Force -Path $plainKit | Out-Null
    Copy-Item (Join-Path $here '..\client_patch\Install-ClientPatch.ps1'), (Join-Path $kit 'manifest.json') $plainKit    # no archive, as the launcher runs it
    $out = & $ps -NoProfile -ExecutionPolicy Bypass -File (Join-Path $plainKit 'Install-ClientPatch.ps1') -ClientDir $client 2>&1 | Out-String
    Check 'a plain kit run on the reset client stops (kit older than the archive) and changes nothing' ($LASTEXITCODE -ne 0 -and ([IO.File]::ReadAllText((Join-Path $client 'swgemu_live.cfg'))) -match 'maxSearchPriority=26' -and (Sha $tre) -eq $newer)
    $out = & $ps -NoProfile -ExecutionPolicy Bypass -File (Join-Path $plainKit 'Install-ClientPatch.ps1') -ClientDir $client -LayoutOnly 2>&1 | Out-String
    if ($Keep) { Write-Host "  LayoutOnly: code $LASTEXITCODE; $($out.Trim() -replace "`r?`n", ' / ')" }
    Check 'kit -LayoutOnly moves the reset layout up again and keeps the newer archive and its version' ($LASTEXITCODE -eq 0 -and (Test-Layout))
    $out = & $ps -NoProfile -ExecutionPolicy Bypass -File (Join-Path $plainKit 'Install-ClientPatch.ps1') -ClientDir $client -LayoutOnly 2>&1 | Out-String
    Check 'kit -LayoutOnly again is harmless' ($LASTEXITCODE -eq 0 -and (Test-Layout))

    # The built launcher, headless: the same reset, fixed by FracturedGalaxy.exe --repair (as on its start and Play).
    $exe = if ($Launcher) { $Launcher } else { Join-Path $here 'build\out\FracturedGalaxy.exe' }
    if (-not (Test-Path -LiteralPath $exe)) { Write-Host 'SKIP launcher --repair: no build\out\FracturedGalaxy.exe (run build.ps1 first)' -ForegroundColor Yellow }
    else {
        Copy-Item $exe $app; Copy-Item $plain (Join-Path $app 'settings.json')
        New-Item -ItemType Directory -Force -Path (Join-Path $app 'kit') | Out-Null; Copy-Item (Join-Path $kit 'manifest.json') (Join-Path $app 'kit')
        function Repair-Launcher {
            $o = Join-Path $root 'repair-out.txt'
            $p = Start-Process -FilePath (Join-Path $app 'FracturedGalaxy.exe') -ArgumentList '--repair' -Wait -PassThru -RedirectStandardOutput $o
            return [pscustomobject]@{ Code = $p.ExitCode; Out = [IO.File]::ReadAllText($o).Trim() }
        }
        Reset-Cfg
        Set-Content -LiteralPath (Join-Path $client 'swgemu_login.cfg') -Value "[ClientGame]`r`nloginServerAddress0=login.swgemu.com`r`n" -NoNewline
        $r = Repair-Launcher
        if ($Keep) { Write-Host "  --repair: code $($r.Code); $($r.Out)" }
        Check "launcher --repair puts the layout, the .include line and the login back on a reset client ($($r.Out))" ($r.Code -eq 0 -and (Test-Layout) -and
            ([IO.File]::ReadAllText((Join-Path $client 'swgemu_login.cfg'))) -match "loginServerAddress0=$([regex]::Escape($addr))")
        $before = Snapshot $client; $r = Repair-Launcher
        Check 'launcher --repair on a client that loads our files changes nothing' ($r.Code -eq 0 -and (Compare-Object @($before) @(Snapshot $client)) -eq $null)
        Reset-Cfg
        Remove-Item -LiteralPath (Join-Path $app 'kit\manifest.json')
        $r = Repair-Launcher
        Check "launcher --repair reports a layout it could not put back (exit 1: $($r.Out))" ($r.Code -eq 1 -and $r.Out -match 'archive cap 26')
        Copy-Item (Join-Path $kit 'manifest.json') (Join-Path $app 'kit'); $r = Repair-Launcher
        Check 'launcher --repair fixes it once the kit manifest is back' ($r.Code -eq 0 -and (Test-Layout))

        # The graphics add-on, headless (--update) against mtg-share.py on loopback, with the add-on files from the
        # owner's client (read only). The friend here already has this DXVK as d3d9.dll, so Undo-Addon below must put
        # it back. Skipped when the owner's client doesn't have the add-on the share would offer.
        $src = Join-Path $here '..\..\SWG-client'
        $py = (Get-Command python -ErrorAction SilentlyContinue).Source
        if (-not $py -or -not (Test-Path -LiteralPath (Join-Path $src 'dxvk_d3d9.dll')) -or -not (Test-Path -LiteralPath (Join-Path $src 'd3d9.dll'))) { Write-Host 'SKIP graphics add-on: no python or no add-on in SWG-client' -ForegroundColor Yellow }
        else {
            Copy-Item $withMtg (Join-Path $app 'settings.json') -Force
            Copy-Item $tre (Join-Path $root 'server.tre')
            $shareArgs = @('-I', "`"$(Join-Path $here 'mtg-share.py')`"", '--bind', '127.0.0.1', '--port', $port, '--dir', "`"$share`"", '--manifest', "`"$(Join-Path $kit 'manifest.json')`"",
                '--archive', "`"$(Join-Path $root 'server.tre')`"", '--launcher', "`"$(Join-Path $root 'no-launcher.exe')`"", '--addon-client', "`"$src`"")
            $srv = Start-Process -FilePath $py -ArgumentList $shareArgs -PassThru -NoNewWindow -RedirectStandardOutput (Join-Path $root 'addon-share-out.txt') -RedirectStandardError (Join-Path $root 'addon-share-err.txt')
            try {
                for ($i = 0; $i -lt 40; $i++) { try { $c = New-Object Net.Sockets.TcpClient('127.0.0.1', $port); $c.Close(); break } catch { Start-Sleep -Milliseconds 250 } }
                function Update-Launcher([string[]]$more) {
                    $o = Join-Path $root 'update-out.txt'
                    $p = Start-Process -FilePath (Join-Path $app 'FracturedGalaxy.exe') -ArgumentList (@('--update') + $more) -Wait -PassThru -RedirectStandardOutput $o
                    return [pscustomobject]@{ Code = $p.ExitCode; Out = ([IO.File]::ReadAllText($o).Trim() -replace "`r?`n", ' / ') }
                }
                $d3d9 = Join-Path $client 'd3d9.dll'; $dxvk = Join-Path $client 'dxvk_d3d9.dll'; $rec = Join-Path $client 'local_planets-patch\addon.json'
                $hookSha = Sha (Join-Path $src 'd3d9.dll'); $dxvkSha = Sha (Join-Path $src 'dxvk_d3d9.dll')
                Copy-Item (Join-Path $src 'dxvk_d3d9.dll') $d3d9    # the friend's own copy of this DXVK
                $before = Snapshot $client; $r = Update-Launcher @('--dry-run')
                if ($Keep) { Write-Host "  --update --dry-run: code $($r.Code); $($r.Out)" }
                Check "launcher --update --dry-run downloads the add-on and changes nothing ($($r.Out))" ($r.Out -match 'DRY RUN: would install the graphics add-on' -and (Compare-Object @($before) @(Snapshot $client)) -eq $null)
                $r = Update-Launcher @()
                if ($Keep) { Write-Host "  --update: code $($r.Code); $($r.Out)" }
                $rj = Get-Content -Raw $rec | ConvertFrom-Json
                Check "launcher --update puts DXVK in as dxvk_d3d9.dll and the hook as d3d9.dll, keeps the friend's d3d9.dll ($($r.Out))" ($r.Code -eq 0 -and
                    (Sha $d3d9) -eq $hookSha -and (Sha $dxvk) -eq $dxvkSha -and (Test-Path (Join-Path $client 'mirage.ini')) -and (Test-Path (Join-Path $client 'dxvk.conf')) -and
                    (Sha (Join-Path $client 'local_planets-patch\backup\friends-installer\addon\d3d9.dll')) -eq $dxvkSha -and @($rj.added) -notcontains 'd3d9.dll' -and @($rj.added) -contains 'dxvk_d3d9.dll' -and
                    -not (Get-ChildItem -LiteralPath $client -Filter *.part))
                $before = Snapshot $client; $r = Update-Launcher @()
                Check "launcher --update again changes nothing ($($r.Out))" ($r.Code -eq 0 -and $r.Out -notmatch 'graphics add-on' -and (Compare-Object @($before) @(Snapshot $client)) -eq $null)
                Remove-Item -LiteralPath $d3d9; $before = Snapshot $client; $r = Update-Launcher @()
                Check "launcher --update leaves a deleted d3d9.dll deleted ($($r.Out))" ($r.Code -eq 0 -and $r.Out -match 'off \(its d3d9.dll was deleted\)' -and (Compare-Object @($before) @(Snapshot $client)) -eq $null)
                Set-Content -LiteralPath $d3d9 -Value 'someone else''s d3d9.dll' -NoNewline; $before = Snapshot $client; $r = Update-Launcher @()
                Check "launcher --update leaves a d3d9.dll it doesn't know alone ($($r.Out))" ($r.Code -eq 0 -and $r.Out -match "isn't one it knows" -and (Compare-Object @($before) @(Snapshot $client)) -eq $null)
                Copy-Item (Join-Path $src 'd3d9.dll') $d3d9 -Force
            } finally { Stop-Process -Id $srv.Id -Force -ErrorAction SilentlyContinue }
            Copy-Item $plain (Join-Path $app 'settings.json') -Force
        }
    }

    $r = Run @('-Action', 'Uninstall')   # client folder from state.json
    $login = [IO.File]::ReadAllText((Join-Path $client 'swgemu_login.cfg'))
    $main = [IO.File]::ReadAllText((Join-Path $client 'swgemu.cfg'))
    Check 'Uninstall restores the login file and the cfg, removes the archive' ($r.Code -eq 0 -and $login -match 'login.swgemu.com' -and $main -notmatch 'local_planets' -and -not (Test-Path (Join-Path $client 'local_planets.tre')))
    Check 'Uninstall removes the downloaded MTG archive and puts the friend''s own version back' (-not (Test-Path (Join-Path $client 'mtg_planets.tre')) -and (Len (Join-Path $client 'mtg_patch_001.tre')) -eq 7 -and -not (Test-Path (Join-Path $bk 'mtg_patch_001.tre')))
    if ($hookSha) {
        Check "Uninstall takes the graphics add-on out and puts the friend's own d3d9.dll back ($(($r.Result -split "`r`n") -match 'graphics add-on'))" ((Sha (Join-Path $client 'd3d9.dll')) -eq $dxvkSha -and
            -not (Test-Path (Join-Path $client 'dxvk_d3d9.dll')) -and -not (Test-Path (Join-Path $client 'mirage.ini')) -and -not (Test-Path (Join-Path $client 'dxvk.conf')) -and
            -not (Test-Path (Join-Path $client 'local_planets-patch\addon.json')))
    }

    $r = Run @('-Action', 'Detect'); Check "Detect runs ($(($r.Result -split "`r`n")[1]))" ($r.Code -eq 0 -or $r.Code -eq 2)
    if ($ProbeAddress) { $r = Run @('-Action', 'Probe'); Check "Probe $ProbeAddress`:46453 ($(($r.Result -split "`r`n")[1]))" ($r.Code -eq 0) }
    else { $r = Run @('-Action', 'Probe'); Check 'Probe reports no answer from 192.0.2.1 (TEST-NET) without hanging' ($r.Code -eq 7) }

    # mtg-share.py: serves the listed archives and nothing else; refuses to start on a share that doesn't match.
    $py = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $py) { Check 'mtg-share.py: python on PATH' $false }
    else {
        $shareArgs = @('-I', "`"$(Join-Path $here 'mtg-share.py')`"", '--bind', '127.0.0.1', '--port', $port, '--dir', "`"$share`"", '--manifest', "`"$(Join-Path $kit 'manifest.json')`"")
        $srv = Start-Process -FilePath $py -ArgumentList $shareArgs -PassThru -NoNewWindow -RedirectStandardOutput (Join-Path $root 'share-out.txt') -RedirectStandardError (Join-Path $root 'share-err.txt')
        try {
            $up = $false
            for ($i = 0; $i -lt 40 -and -not $up; $i++) {
                try { $c = New-Object Net.Sockets.TcpClient('127.0.0.1', $port); $c.Close(); $up = $true } catch { Start-Sleep -Milliseconds 250 }
            }
            Check 'mtg-share.py starts on loopback' $up
            $got = Join-Path $root 'got.tre'
            Invoke-WebRequest -Uri "http://127.0.0.1:$port/mtg_planets.tre" -OutFile $got -UseBasicParsing
            Check 'mtg-share.py serves a listed archive byte for byte' ((Sha $got) -eq $m.requires[1].sha256)
            $codes = foreach ($p in @('manifest.json', '..%2Fkit%2Fmanifest.json', 'MTG_PLANETS.TRE', '')) {
                try { (Invoke-WebRequest -Uri "http://127.0.0.1:$port/$p" -UseBasicParsing).StatusCode } catch { [int]$_.Exception.Response.StatusCode }
            }
            Check "mtg-share.py refuses everything not on the list ($($codes -join ', '))" (@($codes | Where-Object { $_ -ne 404 }).Count -eq 0)
        } finally { Stop-Process -Id $srv.Id -Force -ErrorAction SilentlyContinue }
        [IO.File]::WriteAllBytes((Join-Path $share 'mtg_planets.tre'), [byte[]](1..19))
        $ErrorActionPreference = 'Continue'   # python's message on stderr is the expected result here
        $out = & $py -I (Join-Path $here 'mtg-share.py') --bind 127.0.0.1 --port $port --dir $share --manifest (Join-Path $kit 'manifest.json') 2>&1 | Out-String
        $code = $LASTEXITCODE
        $ErrorActionPreference = 'Stop'
        Check 'mtg-share.py refuses to start when a file does not match the kit' ($code -ne 0 -and $out -match 'mtg_planets.tre \(size 19')
    }
} finally {
    if ($Keep) { Write-Host "Kept $root" } else { Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue }
}
if ($script:fails) { Write-Host "$script:fails failed"; exit 1 }
Write-Host 'all passed'
