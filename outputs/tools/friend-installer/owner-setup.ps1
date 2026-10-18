<#
.SYNOPSIS
  The owner's side of friends-over-Tailscale: Tailscale on this PC, the firewall rules, the ACL, the settings file.

.DESCRIPTION
  Run from this folder. Each switch is one step; -DryRun prints what a step would change and changes nothing.
    owner-setup.ps1                     check only: Tailscale, this PC's tailnet address, WSL, firewall rules
    owner-setup.ps1 -InstallTailscale   download Tailscale's MSI, check it is signed by Tailscale Inc., install it,
                                        then open the sign-in (run as administrator)
    owner-setup.ps1 -Firewall           allow UDP 46453, 46462, 46463 (the galaxy) and TCP 43480 (mtg-share.py, the MTG
                                        archives) in from Tailscale addresses only (administrator)
    owner-setup.ps1 -RemoveFirewall     take those rules out again (administrator)
    owner-setup.ps1 -ShowAcl            print the ACL to paste into the Tailscale admin console
    owner-setup.ps1 -WriteSettings      write owner-settings.json with this PC's tailnet address and MTG link (not in git)
  Nothing here touches the galaxy or /opt/swg. The galaxy address change is the lock holder's (OWNER-README.md).
#>
param([switch]$InstallTailscale, [switch]$Firewall, [switch]$RemoveFirewall, [switch]$ShowAcl, [switch]$WriteSettings, [switch]$DryRun)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$Ports = @(46453, 46462, 46463)          # test galaxy login, ping, zone (tools/test_galaxy.py PORTS); UDP
$Tailnet = '100.64.0.0/10'
$WslId = '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}'   # WSL in the Hyper-V firewall
$Exe = Join-Path $env:ProgramFiles 'Tailscale\tailscale.exe'
$RuleName = 'SWG-Friends-Tailscale-UDP-In'
$MtgPort = 43480                          # mtg-share.py; a Windows program, so no Hyper-V (WSL) rule. Below WSL's
                                          # mirrored ephemeral range (44620-48715 here), which Windows cannot bind
$MtgRule = 'SWG-Friends-Tailscale-MTG-In'

function Good($t) { Write-Host "  ok: $t" -ForegroundColor Green }
function Warn($t) { Write-Host "  CHECK: $t" -ForegroundColor Yellow }
function Would($t) { Write-Host "  DRY RUN: would $t" -ForegroundColor Cyan }
function Test-Admin { ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) }
function Get-Status { if (Test-Path -LiteralPath $Exe) { try { return (& $Exe status --json 2>$null | Out-String | ConvertFrom-Json) } catch {} }; return $null }
function Get-TailnetIp($st) { if ($st -and $st.Self) { return @($st.Self.TailscaleIPs | Where-Object { $_ -match '^\d+\.\d+\.\d+\.\d+$' })[0] }; return $null }

if ($InstallTailscale) {
    if (Test-Path -LiteralPath $Exe) { Good 'Tailscale is already installed.' }
    elseif ($DryRun) { Would 'download https://pkgs.tailscale.com/stable/tailscale-setup-latest-amd64.msi, check the Tailscale Inc. signature, install it' }
    else {
        if (-not (Test-Admin)) { Write-Host 'Run this from PowerShell opened as administrator.'; exit 1 }
        $dir = Join-Path $env:TEMP ('owner-ts-' + [guid]::NewGuid().ToString('N')); New-Item -ItemType Directory -Path $dir | Out-Null
        $msi = Join-Path $dir 'tailscale-setup-amd64.msi'
        try {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            Invoke-WebRequest -Uri 'https://pkgs.tailscale.com/stable/tailscale-setup-latest-amd64.msi' -OutFile $msi -UseBasicParsing
            $sig = Get-AuthenticodeSignature -LiteralPath $msi
            if ($sig.Status -ne 'Valid' -or $sig.SignerCertificate.Subject -notmatch '(^|,\s*)CN="?Tailscale Inc\.') { Write-Host "STOPPED: the download is not signed by Tailscale Inc. ($($sig.Status))."; exit 1 }
            Good "signed by $($sig.SignerCertificate.Subject)"
            $p = Start-Process "$env:SystemRoot\System32\msiexec.exe" -ArgumentList @('/i', "`"$msi`"", '/passive', '/norestart') -Wait -PassThru
            if ($p.ExitCode -ne 0 -and $p.ExitCode -ne 3010) { Write-Host "STOPPED: the installer returned $($p.ExitCode)."; exit 1 }
        } finally { Remove-Item -LiteralPath $dir -Recurse -Force -ErrorAction SilentlyContinue }
        Good 'installed. Sign in with your own account in the browser window that opens.'
        & $Exe up
    }
}

if ($Firewall) {
    if ($DryRun) { Would "add '$RuleName' (Hyper-V firewall for WSL and Windows Defender): UDP $($Ports -join ',') in, from $Tailnet only"; Would "add '$MtgRule' (Windows Defender): TCP $MtgPort in, from $Tailnet only" }
    elseif (-not (Test-Admin)) { Write-Host 'Run this from PowerShell opened as administrator.'; exit 1 }
    else {
        Remove-NetFirewallHyperVRule -Name $RuleName -ErrorAction SilentlyContinue
        Remove-NetFirewallRule -Name $RuleName, $MtgRule -ErrorAction SilentlyContinue
        New-NetFirewallHyperVRule -Name $RuleName -DisplayName 'SWG test galaxy from Tailscale (UDP in)' -Direction Inbound -VMCreatorId $WslId -Protocol UDP -LocalPorts $Ports -RemoteAddresses $Tailnet -Action Allow | Out-Null
        New-NetFirewallRule -Name $RuleName -DisplayName 'SWG test galaxy from Tailscale (UDP in)' -Group 'SWG remote access' -Direction Inbound -Protocol UDP -LocalPort $Ports -RemoteAddress $Tailnet -Profile Any -Action Allow | Out-Null
        New-NetFirewallRule -Name $MtgRule -DisplayName 'SWG MTG archives for friends from Tailscale (TCP in)' -Group 'SWG remote access' -Direction Inbound -Protocol TCP -LocalPort $MtgPort -RemoteAddress $Tailnet -Profile Any -Action Allow | Out-Null
        Good "firewall rules added: UDP $($Ports -join ', ') and TCP $MtgPort from $Tailnet"
    }
}
if ($RemoveFirewall) {
    if ($DryRun) { Would "remove '$RuleName' and '$MtgRule'" }
    elseif (-not (Test-Admin)) { Write-Host 'Run this from PowerShell opened as administrator.'; exit 1 }
    else {
        Remove-NetFirewallHyperVRule -Name $RuleName -ErrorAction SilentlyContinue
        Remove-NetFirewallRule -Name $RuleName, $MtgRule -ErrorAction SilentlyContinue
        Good 'firewall rules removed'
    }
}

$st = Get-Status
$ip = Get-TailnetIp $st

if ($ShowAcl) {
    $server = if ($ip) { $ip } else { '100.x.y.z' }
    $ports = $Ports -join ','
@"
// Paste into https://login.tailscale.com/admin/acls (it replaces the default allow-all policy; keep a copy of the old one).
{
  "tagOwners": { "tag:swg-friend": ["autogroup:admin"] },
  "hosts": { "swg-server": "$server" },
  "acls": [
    // Your own devices reach each other as before.
    { "action": "accept", "src": ["autogroup:member"], "dst": ["autogroup:self:*"] },
    // Friends reach the test galaxy's login, ping and zone ports on this PC (UDP), and the MTG archive share
    // (mtg-share.py, TCP $MtgPort) that Setup downloads from. Nothing else, not each other.
    { "action": "accept", "src": ["tag:swg-friend"], "proto": "udp", "dst": ["swg-server:$ports"] },
    { "action": "accept", "src": ["tag:swg-friend"], "proto": "tcp", "dst": ["swg-server:$MtgPort"] }
  ],
  "tests": [
    { "src": "tag:swg-friend", "proto": "udp", "accept": ["swg-server:46453", "swg-server:46462", "swg-server:46463"],
      "deny": ["swg-server:44453", "swg-server:46419", "swg-server:46455"] },
    { "src": "tag:swg-friend", "proto": "tcp", "accept": ["swg-server:$MtgPort"],
      "deny": ["swg-server:11434", "swg-server:8765", "swg-server:8188", "swg-server:3306", "swg-server:22", "swg-server:46419"] }
  ]
}
"@ | Write-Host
}

if ($WriteSettings) {
    $path = Join-Path $PSScriptRoot 'owner-settings.json'
    if (-not $ip) { Write-Host 'STOPPED: Tailscale is not signed in on this PC, so there is no tailnet address yet.'; exit 1 }
    $s = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'owner-settings.example.json') -Raw | ConvertFrom-Json
    if (Test-Path -LiteralPath $path) { $s = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json }
    $s.ServerAddress = $ip
    # Friends' Setup downloads missing MTG archives from mtg-share.py on this PC. A later host (an https link where
    # the 23 files sit side by side) goes into MtgBaseUrl by hand; -WriteSettings only fills it while it is empty
    # or still points at a tailnet address.
    if (-not $s.MtgBaseUrl -or "$($s.MtgBaseUrl)" -match '<|^http://100\.') { $s | Add-Member -NotePropertyName MtgBaseUrl -NotePropertyValue "http://${ip}:$MtgPort/" -Force }
    if ($DryRun) { Would "write $path with ServerAddress $ip and MtgBaseUrl $($s.MtgBaseUrl)" }
    else { [IO.File]::WriteAllText($path, ($s | ConvertTo-Json) + "`r`n", [Text.Encoding]::ASCII); Good "wrote $path (ServerAddress $ip, MtgBaseUrl $($s.MtgBaseUrl))." }
}

# --- check (always) -------------------------------------------------------------------------------------
Write-Host ''
Write-Host 'Check:'
if (-not (Test-Path -LiteralPath $Exe)) { Warn 'Tailscale is not installed (-InstallTailscale).' }
elseif (-not $st -or $st.BackendState -ne 'Running') { Warn "Tailscale is installed but not connected ($(if ($st) { $st.BackendState } else { 'no status' }))." }
else {
    Good "Tailscale connected: $ip ($($st.Self.DNSName.TrimEnd('.')))"
    if ($st.Self.KeyExpiry) { Warn "this PC's Tailscale key expires $($st.Self.KeyExpiry); turn off key expiry for it in the admin console, or friends lose the server when it does." }
}
try {
    $wslAddr = (wsl.exe -d Debian -u swgemu -- ip -4 -o addr 2>$null | Out-String)
    if ($ip -and $wslAddr -match [regex]::Escape($ip)) { Good "WSL sees $ip (mirrored networking passes Tailscale through)" }
    elseif ($ip) { Warn "WSL does not list $ip. Mirrored networking may not carry Tailscale's adapter; test a friend login before relying on it." }
} catch { Warn 'could not ask WSL for its addresses.' }
$hv = Get-NetFirewallHyperVRule -Name $RuleName -ErrorAction SilentlyContinue
$fw = Get-NetFirewallRule -Name $RuleName -ErrorAction SilentlyContinue
if ($hv -and $fw) { Good 'firewall rules are in place' } else { Warn 'firewall rules are missing (-Firewall, as administrator).' }
if (Get-NetFirewallRule -Name $MtgRule -ErrorAction SilentlyContinue) { Good "firewall rule for the MTG share (TCP $MtgPort) is in place" } else { Warn "no firewall rule for the MTG share yet (-Firewall again, as administrator)." }
if (Get-NetTCPConnection -LocalPort $MtgPort -State Listen -ErrorAction SilentlyContinue) { Good "the MTG archives are being shared (port $MtgPort)" } else { Write-Host "  the MTG archives are not being shared right now; run 'Share MTG files.cmd' while a friend installs." }
$os = Join-Path $PSScriptRoot 'owner-settings.json'
if (Test-Path -LiteralPath $os) { Good 'owner-settings.json exists' } else { Warn 'no owner-settings.json yet (-WriteSettings).' }
