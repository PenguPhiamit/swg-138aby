<#
.SYNOPSIS
  Offline test of friend-setup.ps1 on a dummy client folder with a dummy kit. Downloads nothing, installs nothing.
    powershell -NoProfile -ExecutionPolicy Bypass -File test-friend-setup.ps1 [-ProbeAddress 192.168.1.210]
  -ProbeAddress also sends one UDP session request to that address's login port (read-only).
#>
param([string]$ProbeAddress)
$ErrorActionPreference = 'Stop'
$here = $PSScriptRoot
$root = Join-Path $env:TEMP ('friend-setup-test-' + [guid]::NewGuid().ToString('N'))
$kit = Join-Path $root 'kit'; $client = Join-Path $root 'client'; $app = Join-Path $root 'app'
New-Item -ItemType Directory -Force -Path $kit, $client, $app | Out-Null
$ps = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
$script:fails = 0
function Check($name, $ok) { if ($ok) { Write-Host "PASS $name" } else { Write-Host "FAIL $name" -ForegroundColor Red; $script:fails++ } }
function Run([string[]]$a) {
    $res = Join-Path $root 'result.txt'; Remove-Item -LiteralPath $res -ErrorAction SilentlyContinue
    $out = & $ps -NoProfile -ExecutionPolicy Bypass -File (Join-Path $here 'friend-setup.ps1') @a -SettingsFile (Join-Path $root 'settings.json') -KitDir $kit -StateFile (Join-Path $app 'state.json') -ResultFile $res 2>&1 | Out-String
    $text = ''; if (Test-Path -LiteralPath $res) { $text = [IO.File]::ReadAllText($res) }
    return [pscustomobject]@{ Code = $LASTEXITCODE; Out = $out; Result = $text }
}
function Sha($p) { (Get-FileHash -Algorithm SHA256 -LiteralPath $p).Hash.ToLower() }
try {
    # A dummy kit: the real installer scripts, a fake archive, two fake MTG requirements.
    Copy-Item (Join-Path $here '..\client_patch\Install-ClientPatch.ps1'), (Join-Path $here '..\client_patch\Uninstall-ClientPatch.ps1') $kit
    [IO.File]::WriteAllBytes((Join-Path $kit 'local_planets.tre'), [byte[]](1..200 | ForEach-Object { $_ % 256 }))
    $m = [ordered]@{ format = 1; name = 'local_planets'; version = '2026.10.17.1'
        archive = [ordered]@{ file = 'local_planets.tre'; size = 200; sha256 = (Sha (Join-Path $kit 'local_planets.tre')); priority = 49 }
        requires = @([ordered]@{ file = 'mtg_patch_001.tre'; priority = 1; size = 10; sha256 = '' }, [ordered]@{ file = 'mtg_planets.tre'; priority = 21; size = 20; sha256 = '' }) }
    [IO.File]::WriteAllText((Join-Path $kit 'manifest.json'), ($m | ConvertTo-Json -Depth 5))
    $addr = if ($ProbeAddress) { $ProbeAddress } else { '192.0.2.1' }
    [IO.File]::WriteAllText((Join-Path $root 'settings.json'), (@{ ServerAddress = $addr; LoginPort = 46453; MtgHelpUrl = 'https://example.invalid/mtg'; ClientHelpUrl = 'https://www.swgemu.com/' } | ConvertTo-Json))

    # A dummy client: the shape the kit wants, the user's own login file, one MTG archive missing.
    foreach ($f in 'SWGEmu.exe', 'bottom.tre', 'data_other_00.tre', 'patch_14_00.tre', 'swgemu_live.cfg') { Set-Content -LiteralPath (Join-Path $client $f) -Value 'x' }
    Set-Content -LiteralPath (Join-Path $client 'swgemu.cfg') -Value ".include `"swgemu_login.cfg`"`r`n.include `"swgemu_live.cfg`"`r`n[SharedFile]`r`nmaxSearchPriority=50" -NoNewline
    Set-Content -LiteralPath (Join-Path $client 'swgemu_login.cfg') -Value "[ClientGame]`r`nloginServerAddress0=login.swgemu.com`r`nloginServerPort0=44453`r`n" -NoNewline
    [IO.File]::WriteAllBytes((Join-Path $client 'mtg_patch_001.tre'), (New-Object byte[] 10))

    $r = Run @('-Action', 'Check', '-ClientDir', $root); Check 'Check refuses a folder without SWGEmu.exe' ($r.Code -eq 2 -and $r.Result -match 'swgemu.com')
    $r = Run @('-Action', 'Check', '-ClientDir', $client); Check 'Check names the missing MTG archive and the link' ($r.Code -eq 3 -and $r.Result -match 'mtg_planets.tre \(missing\)' -and $r.Result -match 'example.invalid/mtg')
    [IO.File]::WriteAllBytes((Join-Path $client 'mtg_planets.tre'), (New-Object byte[] 5))
    $r = Run @('-Action', 'Check', '-ClientDir', $client); Check 'Check notices a wrong-size archive' ($r.Code -eq 3 -and $r.Result -match 'different version')
    [IO.File]::WriteAllBytes((Join-Path $client 'mtg_planets.tre'), (New-Object byte[] 20))
    $r = Run @('-Action', 'Check', '-ClientDir', $client); Check 'Check passes a complete client' ($r.Code -eq 0)

    $before = Get-ChildItem -LiteralPath $client -Recurse | ForEach-Object { "$($_.FullName)|$($_.Length)" }
    $r = Run @('-Action', 'Patch', '-ClientDir', $client, '-DryRun'); $after = Get-ChildItem -LiteralPath $client -Recurse | ForEach-Object { "$($_.FullName)|$($_.Length)" }
    Check 'Patch -DryRun changes nothing' ($r.Code -eq 0 -and (Compare-Object @($before) @($after)) -eq $null -and -not (Test-Path (Join-Path $app 'state.json')))

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
    Check 'state.json records the client folder' ((Get-Content -Raw (Join-Path $app 'state.json') | ConvertFrom-Json).ClientDir -eq $client)

    $r = Run @('-Action', 'Uninstall')   # client folder from state.json
    $login = [IO.File]::ReadAllText((Join-Path $client 'swgemu_login.cfg'))
    $main = [IO.File]::ReadAllText((Join-Path $client 'swgemu.cfg'))
    Check 'Uninstall restores the login file and the cfg, removes the archive' ($r.Code -eq 0 -and $login -match 'login.swgemu.com' -and $main -notmatch 'local_planets' -and -not (Test-Path (Join-Path $client 'local_planets.tre')))

    $r = Run @('-Action', 'Detect'); Check "Detect runs ($(($r.Result -split "`r`n")[1]))" ($r.Code -eq 0 -or $r.Code -eq 2)
    if ($ProbeAddress) { $r = Run @('-Action', 'Probe'); Check "Probe $ProbeAddress`:46453 ($(($r.Result -split "`r`n")[1]))" ($r.Code -eq 0) }
    else { $r = Run @('-Action', 'Probe'); Check 'Probe reports no answer from 192.0.2.1 (TEST-NET) without hanging' ($r.Code -eq 7) }
} finally {
    Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue
}
if ($script:fails) { Write-Host "$script:fails failed"; exit 1 }
Write-Host 'all passed'
