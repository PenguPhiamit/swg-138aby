<#
Ollama for the SWG project on a second Windows PC (Claude, 17 Oct 2026). Installs Ollama for this Windows user,
downloads the project's models, and lets ONE other PC on the home network (the owner's) use it. Nothing else can
reach it. Run it at this PC, with this PC's owner's OK. README.md in this folder explains each step.

  powershell -ExecutionPolicy Bypass -File install-ollama-lan.ps1 -OwnerPC 192.168.1.x     install or repair
  ... -OwnerPC 192.168.1.x -CheckOnly     look only, change nothing (also the way to diagnose later)
  ... -Remove                             close it again: rule, settings, power setting; Ollama and models stay

What it changes on this PC (and -Remove undoes):
  1. Installs Ollama if it is missing: the official OllamaSetup.exe from ollama.com, run only if it carries a valid
     "Ollama Inc." signature. It installs for this user, under %LOCALAPPDATA%\Programs\Ollama.
  2. User variables: OLLAMA_HOST=0.0.0.0:11434 (listen on the network, not only on this PC),
     OLLAMA_MAX_LOADED_MODELS=1 (one model in memory at a time) and OLLAMA_NUM_PARALLEL=1.
  3. One inbound Windows Firewall rule, "SWG-Ollama-OwnerPC" (Windows asks for an administrator once): TCP port
     11434, for ollama.exe only, from Miniverse address only, on Private networks only.
  4. Optional (asks first): no sleep while plugged in, so jobs can run while nobody is at the PC.
  5. Downloads the models (about 39 GB for the default three) and tests each one.

Ollama has no password. Never forward port 11434 on the router.
#>
[CmdletBinding()]
param(
    [string]$OwnerPC,
    [string[]]$Models = @('qwen3.6:35b-a3b', 'qwen3.5:9b', 'gemma4:12b'),
    [switch]$CheckOnly,
    [switch]$SkipPull,
    [switch]$Remove
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$RuleName = 'SWG-Ollama-OwnerPC'
$RuleDisplay = 'Ollama for the SWG project (Miniverse only)'
$Port = 11434
$Local = "http://127.0.0.1:$Port"
$InstallDir = Join-Path $env:LOCALAPPDATA 'Programs\Ollama'
$StateDir = Join-Path $env:LOCALAPPDATA 'swg-ollama-lan'
$StateFile = Join-Path $StateDir 'state.json'
$Setup = 'https://ollama.com/download/OllamaSetup.exe'
$Vars = [ordered]@{ OLLAMA_HOST = "0.0.0.0:$Port"; OLLAMA_MAX_LOADED_MODELS = '1'; OLLAMA_NUM_PARALLEL = '1' }
# Sizes on disk from the Ollama library pages (GB); the test context is the window our jobs will ask for.
$SizeGB = @{ 'qwen3.6:35b-a3b' = 24; 'qwen3.5:9b' = 7.6; 'gemma4:12b' = 8.0; 'qwen3:8b' = 5.2 }
$TestCtx = @{ 'qwen3.6:35b-a3b' = 65536; 'qwen3.5:9b' = 32768 }

$script:Problems = New-Object System.Collections.ArrayList
$script:Result = New-Object System.Collections.ArrayList

function Say([string]$Text) { Write-Host $Text }
function Step([string]$Text) { Write-Host ''; Write-Host "== $Text" -ForegroundColor Cyan }
function Good([string]$Text) { Write-Host "   ok: $Text" -ForegroundColor Green }
function Warn([string]$Text) { Write-Host "   CHECK: $Text" -ForegroundColor Yellow; [void]$script:Problems.Add($Text) }
function Stop-Here([string]$Text) {
    Write-Host ''
    Write-Host "STOPPED: $Text" -ForegroundColor Red
    Write-Host 'Nothing after this point was changed. Fix the line above and run the script again.'
    exit 1
}
function Ask([string]$Question) {
    $answer = Read-Host "$Question (y/n)"
    return $answer -match '^(y|yes)$'
}

function Test-Admin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    return ([Security.Principal.WindowsPrincipal]$id).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Invoke-AsAdmin([string]$Code, [string]$What) {
    # Runs a short PowerShell block as administrator (one Windows prompt). Returns $true when it succeeded.
    New-Item -ItemType Directory -Force $StateDir | Out-Null
    $errFile = Join-Path $StateDir 'admin-error.txt'
    Remove-Item $errFile -ErrorAction SilentlyContinue
    $quotedErr = $errFile.Replace("'", "''")
    $wrapped = "`$ErrorActionPreference = 'Stop'`ntry {`n$Code`nexit 0`n} catch { `$_ | Out-String | Set-Content -Encoding UTF8 '$quotedErr'; exit 1 }"
    if (Test-Admin) {
        $tmp = Join-Path $StateDir 'admin-step.ps1'
        Set-Content -Encoding UTF8 $tmp $wrapped
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $tmp
        $code = $LASTEXITCODE
        Remove-Item $tmp -ErrorAction SilentlyContinue
    } else {
        Say "   Windows will ask for an administrator now ($What)."
        $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($wrapped))
        try {
            $p = Start-Process powershell.exe -Verb RunAs -Wait -PassThru -WindowStyle Hidden `
                -ArgumentList '-NoProfile', '-ExecutionPolicy', 'Bypass', '-EncodedCommand', $encoded
            $code = $p.ExitCode
        } catch {
            Say '   The administrator prompt was declined.'
            return $false
        }
    }
    if ($code -ne 0) {
        if (Test-Path $errFile) { Say ('   ' + ((Get-Content $errFile) -join ' ')) }
        return $false
    }
    return $true
}

function Get-State {
    try { return Get-Content $StateFile -Raw | ConvertFrom-Json } catch { return $null }
}

function Save-State($State) {
    New-Item -ItemType Directory -Force $StateDir | Out-Null
    $State | ConvertTo-Json | Set-Content -Encoding UTF8 $StateFile
}

function Find-Ollama {
    $exe = Join-Path $InstallDir 'ollama.exe'
    if (Test-Path $exe) { return $exe }
    $cmd = Get-Command ollama.exe -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    return $null
}

function Test-Signed([string]$Path) {
    $sig = Get-AuthenticodeSignature $Path
    return ($sig.Status -eq 'Valid' -and $sig.SignerCertificate.Subject -match '^CN=Ollama Inc\.')
}

function Get-Api([string]$Route, [int]$Timeout = 5) {
    try { return Invoke-RestMethod -Uri ($Local + $Route) -TimeoutSec $Timeout } catch { return $null }
}

function Stop-Ollama {
    Get-Process -Name 'ollama app', 'ollama' -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    for ($i = 0; $i -lt 20; $i++) {
        if (-not (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)) { return }
        Start-Sleep -Milliseconds 500
    }
}

function Start-Ollama([string]$Exe) {
    foreach ($name in $Vars.Keys) {   # the app passes its own environment on to the server it starts
        $value = [Environment]::GetEnvironmentVariable($name, 'User')
        if ($value) { Set-Item "env:$name" $value } else { Remove-Item "env:$name" -ErrorAction SilentlyContinue }
    }
    $app = Join-Path (Split-Path $Exe) 'ollama app.exe'
    if (Test-Path $app) { Start-Process $app } else { Start-Process $Exe -ArgumentList 'serve' -WindowStyle Hidden }
    for ($i = 0; $i -lt 60; $i++) {
        if (Get-Api '/api/version' 2) { return $true }
        Start-Sleep -Seconds 1
    }
    return $false
}

function Get-Listener {
    $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $conn) { return $null }
    $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
    return [pscustomobject]@{ Address = $conn.LocalAddress; Path = $(if ($proc) { $proc.Path } else { '' }) }
}

function Get-Lan {
    $cfg = Get-NetIPConfiguration | Where-Object { $_.IPv4DefaultGateway -and $_.NetAdapter.Status -eq 'Up' } |
        Select-Object -First 1
    if (-not $cfg) { return $null }
    $ip = @($cfg.IPv4Address)[0]
    return [pscustomobject]@{ Alias = $cfg.InterfaceAlias; IP = $ip.IPAddress; Prefix = $ip.PrefixLength
                              Category = "$($cfg.NetProfile.NetworkCategory)"; Index = $cfg.InterfaceIndex }
}

function Get-IpNumber([string]$Ip) {
    $n = [int64]0
    foreach ($octet in [Net.IPAddress]::Parse($Ip).GetAddressBytes()) { $n = $n * 256 + $octet }
    return $n
}

function Test-SameSubnet([string]$A, [string]$B, [int]$Prefix) {
    $block = [int64][math]::Pow(2, 32 - $Prefix)
    return ([math]::Floor((Get-IpNumber $A) / $block) -eq [math]::Floor((Get-IpNumber $B) / $block))
}

function Get-OtherRules([string]$Exe) {
    # Enabled inbound rules other than ours that cover ollama.exe or port 11434. A Windows "allow this app" prompt
    # makes rules like these: an Allow opens Ollama to more than Miniverse, a Block shuts Miniverse out.
    $found = @{}
    Get-NetFirewallApplicationFilter -ErrorAction SilentlyContinue | Where-Object { $_.Program -like '*\ollama*.exe' } |
        ForEach-Object { $r = $_ | Get-NetFirewallRule; if ($r) { $found[$r.Name] = $r } }
    Get-NetFirewallPortFilter -ErrorAction SilentlyContinue | Where-Object { "$($_.LocalPort)" -eq "$Port" } |
        ForEach-Object { $r = $_ | Get-NetFirewallRule; if ($r) { $found[$r.Name] = $r } }
    return @($found.Values | Where-Object { $_.Name -ne $RuleName -and $_.Direction -eq 'Inbound' -and "$($_.Enabled)" -eq 'True' })
}

function Show-Rule {
    $rule = Get-NetFirewallRule -Name $RuleName -ErrorAction SilentlyContinue
    if (-not $rule) { return $null }
    $addr = ($rule | Get-NetFirewallAddressFilter).RemoteAddress -join ','
    $prog = ($rule | Get-NetFirewallApplicationFilter).Program
    $ports = ($rule | Get-NetFirewallPortFilter).LocalPort -join ','
    return [pscustomobject]@{ Remote = $addr; Program = $prog; Port = $ports; Profile = "$($rule.Profile)"
                              Enabled = "$($rule.Enabled)"; Action = "$($rule.Action)" }
}

function Get-SleepAC {
    # Minutes until sleep on mains power for the active power plan (0 = never), or $null if unreadable.
    $out = powercfg /query SCHEME_CURRENT SUB_SLEEP STANDBYIDLE 2>$null
    $line = $out | Where-Object { $_ -match 'Current AC Power Setting Index:\s*0x([0-9a-fA-F]+)' } | Select-Object -First 1
    if ($line -and $line -match '0x([0-9a-fA-F]+)') { return [int]([Convert]::ToInt32($Matches[1], 16) / 60) }
    return $null
}

# ------------------------------------------------------------------------------------------------------- remove
if ($Remove) {
    Step 'Closing Ollama to the network again'
    $state = Get-State
    if (Get-NetFirewallRule -Name $RuleName -ErrorAction SilentlyContinue) {
        if (Invoke-AsAdmin "Remove-NetFirewallRule -Name '$RuleName'" 'to remove the firewall rule') { Good 'firewall rule removed' }
        else { Warn "could not remove firewall rule $RuleName (Windows Defender Firewall, Advanced settings, Inbound Rules)" }
    } else { Good 'no firewall rule to remove' }
    foreach ($name in $Vars.Keys) {
        if ([Environment]::GetEnvironmentVariable($name, 'User') -eq $Vars[$name]) {
            [Environment]::SetEnvironmentVariable($name, $null, 'User'); Good "$name cleared"
        }
    }
    if ($state -and $null -ne $state.SleepACMinutes) {
        powercfg /change standby-timeout-ac $state.SleepACMinutes | Out-Null
        Good "sleep on mains power set back to $($state.SleepACMinutes) min (0 = never)"
    }
    $exe = Find-Ollama
    if ($exe) { Stop-Ollama; [void](Start-Ollama $exe); Good 'Ollama restarted; it listens on this PC only now' }
    Remove-Item $StateFile -ErrorAction SilentlyContinue
    Say ''
    Say 'Ollama itself and the models are still installed. To remove them as well: Settings, Apps, Installed apps,'
    Say "Ollama, Uninstall; then delete the folder $env:USERPROFILE\.ollama (the models)."
    exit 0
}

# ------------------------------------------------------------------------------------------------------- checks
Step 'Checking this PC'
$Models = @($Models | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ })
if (-not $OwnerPC) {
    Say "Miniverse address: on Miniverse, ipconfig shows it as IPv4 Address (192.168.1.something)."
    $OwnerPC = (Read-Host "Address of Miniverse").Trim()
}
$parsed = $null
if (-not [Net.IPAddress]::TryParse($OwnerPC, [ref]$parsed) -or $parsed.AddressFamily -ne 'InterNetwork') {
    Stop-Here "'$OwnerPC' is not an IPv4 address like 192.168.1.20"
}
$b = $parsed.GetAddressBytes()
if (-not ($b[0] -eq 10 -or ($b[0] -eq 172 -and $b[1] -ge 16 -and $b[1] -le 31) -or ($b[0] -eq 192 -and $b[1] -eq 168))) {
    Stop-Here "$OwnerPC is not a home-network address (10.x, 172.16-31.x or 192.168.x). Ollama must never be opened to the internet."
}

$os = Get-CimInstance Win32_OperatingSystem
$ramGB = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
$freeGB = [math]::Round($os.FreePhysicalMemory / 1MB, 1)
Good "Windows $($os.Caption) $($os.Version); RAM $ramGB GB ($freeGB GB free now)"
$gpus = @(Get-CimInstance Win32_VideoController | Where-Object { $_.Name -match 'NVIDIA' })
if ($gpus.Count -eq 0) { Warn 'no NVIDIA graphics card found: Ollama would run on the CPU only (slow)' }
else {
    $driver = $null
    try { $driver = (& nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader 2>$null | Select-Object -First 1) } catch {}
    if ($driver) {
        Good "graphics card: $driver"
        $ver = ($driver -split ',')[1].Trim()
        if ([version]$ver -lt [version]'551.61') { Warn "NVIDIA driver $ver is older than 551.61 (Ollama's minimum): update it from nvidia.com or the NVIDIA app" }
    } else { Good "graphics card: $($gpus[0].Name) (nvidia-smi not found, driver version not checked)" }
}

$lan = Get-Lan
if (-not $lan) { Stop-Here 'no network connection with a router found' }
Good "network: $($lan.Alias), this PC is $($lan.IP)/$($lan.Prefix), Windows calls the network $($lan.Category)"
if ($lan.IP -eq $OwnerPC) { Stop-Here "$OwnerPC is this PC's own address. Give Miniverse address." }
if (-not (Test-SameSubnet $lan.IP $OwnerPC $lan.Prefix)) {
    Warn "$OwnerPC is not on this PC's network ($($lan.IP)/$($lan.Prefix)); check the address on Miniverse"
}
if ($lan.Category -eq 'Public') {
    Warn 'Windows calls this network Public, so the Private-only rule would not apply'
    if (-not $CheckOnly) {
        Say '   A home network should be Private (Settings, Network & internet, the connection, Network profile type).'
        if (Ask '   Set this network to Private now?') {
            if (Invoke-AsAdmin "Set-NetConnectionProfile -InterfaceIndex $($lan.Index) -NetworkCategory Private" 'to set the network to Private') {
                Good 'network set to Private'; $script:Problems.RemoveAt($script:Problems.Count - 1)
            }
        }
    }
}

$modelDir = [Environment]::GetEnvironmentVariable('OLLAMA_MODELS', 'User')
if (-not $modelDir) { $modelDir = Join-Path $env:USERPROFILE '.ollama\models' }
$drive = (Split-Path -Qualifier $modelDir).TrimEnd(':')
$diskFree = [math]::Round((Get-PSDrive $drive).Free / 1GB, 1)
$need = 0
foreach ($m in $Models) { if ($SizeGB.ContainsKey($m)) { $need += $SizeGB[$m] } else { $need += 10 } }
Good "models go to $modelDir ($diskFree GB free on ${drive}:; the models need about $need GB)"

$exe = Find-Ollama
$keep = [Environment]::GetEnvironmentVariable('OLLAMA_KEEP_ALIVE', 'User')
if ($keep) { Warn "OLLAMA_KEEP_ALIVE is set to '$keep': Miniverse tells 'idle' from models timing out, so delete it unless you need it" }

# ------------------------------------------------------------------------------------------------------- check only
if ($CheckOnly) {
    Step 'Ollama'
    if (-not $exe) { Warn 'Ollama is not installed' }
    else {
        $v = Get-Api '/api/version'
        if ($v) { Good "Ollama $($v.version) is running" } else { Warn 'Ollama is installed but not running (start it from the Start menu)' }
        if (-not (Test-Signed $exe)) { Warn "$exe does not carry a valid Ollama Inc. signature" }
    }
    foreach ($name in $Vars.Keys) {
        $now = [Environment]::GetEnvironmentVariable($name, 'User')
        if ($now -eq $Vars[$name]) { Good "$name = $now" } else { Warn "$name is '$now' (the script sets $($Vars[$name]))" }
    }
    $l = Get-Listener
    if ($l) {
        if ($l.Address -eq '0.0.0.0') { Good "listening on 0.0.0.0:$Port ($($l.Path))" }
        else { Warn "listening on $($l.Address):$Port only, so Miniverse can't reach it (quit Ollama from the tray icon and start it again)" }
    }
    $rule = Show-Rule
    if (-not $rule) { Warn "no firewall rule $RuleName" }
    else {
        Say "   rule: $($rule.Action) TCP $($rule.Port) from $($rule.Remote), profile $($rule.Profile), program $($rule.Program), enabled $($rule.Enabled)"
        if ($rule.Remote -ne $OwnerPC) { Warn "the rule allows $($rule.Remote), not $OwnerPC" }
        if ($l -and $l.Path -and $rule.Program -ne $l.Path) { Warn "the rule is for $($rule.Program), but $($l.Path) is listening" }
    }
    foreach ($r in (Get-OtherRules $exe)) { Warn "other firewall rule '$($r.DisplayName)': $($r.Action), profile $($r.Profile)" }
    $tags = Get-Api '/api/tags'
    if ($tags) {
        $have = @($tags.models | ForEach-Object { $_.name })
        foreach ($m in $Models) { if ($have -contains $m) { Good "model $m is here" } else { Warn "model $m is missing" } }
    }
    $sleep = Get-SleepAC
    if ($null -ne $sleep) { Say "   sleep on mains power after: $(if ($sleep -eq 0) { 'never' } else { "$sleep min" })" }
    Step "$($script:Problems.Count) thing(s) to check"
    exit $(if ($script:Problems.Count) { 1 } else { 0 })
}

if ($diskFree -lt ($need + 5) -and -not $SkipPull) {
    Stop-Here "only $diskFree GB free on ${drive}: and the models need about $need GB plus 5 GB spare. Free some space, or run with -Models qwen3.5:9b,gemma4:12b"
}

# ------------------------------------------------------------------------------------------------------- 1 install
Step '1. Ollama'
if ($exe) {
    if (-not (Test-Signed $exe)) { Stop-Here "$exe does not carry a valid Ollama Inc. signature; reinstall Ollama from ollama.com" }
    Good "already installed: $exe"
} else {
    $dl = Join-Path $env:TEMP 'swg-ollama-setup'
    New-Item -ItemType Directory -Force $dl | Out-Null
    $file = Join-Path $dl 'OllamaSetup.exe'
    Say "   Downloading $Setup (about 1 GB) ..."
    if (Get-Command curl.exe -ErrorAction SilentlyContinue) {
        & curl.exe -L --fail --progress-bar -o $file $Setup
        if ($LASTEXITCODE -ne 0) { Stop-Here 'the download failed' }
    } else { Invoke-WebRequest -Uri $Setup -OutFile $file -UseBasicParsing }
    if (-not (Test-Signed $file)) { Stop-Here 'the downloaded OllamaSetup.exe does not carry a valid Ollama Inc. signature; not running it' }
    Good 'signature: Ollama Inc. (valid)'
    Say '   Installing (if a setup window opens, click through it) ...'
    Start-Process $file -ArgumentList '/SILENT', '/SUPPRESSMSGBOXES', '/NORESTART' -Wait
    $exe = Find-Ollama
    if (-not $exe) { Stop-Here ('Ollama did not install; run OllamaSetup.exe by hand from ' + $dl) }
    Remove-Item $file -ErrorAction SilentlyContinue
    Good "installed: $exe"
}

# ------------------------------------------------------------------------------------------------------- 2 settings
Step '2. Settings'
Stop-Ollama
foreach ($name in $Vars.Keys) {
    [Environment]::SetEnvironmentVariable($name, $Vars[$name], 'User')
    Good "$name = $($Vars[$name])"
}

# ------------------------------------------------------------------------------------------------------- 3 firewall
Step '3. Firewall'
$others = Get-OtherRules $exe
$quotedExe = $exe.Replace("'", "''")
$ruleCode = @"
Get-NetFirewallRule -Name '$RuleName' -ErrorAction SilentlyContinue | Remove-NetFirewallRule
New-NetFirewallRule -Name '$RuleName' -DisplayName '$RuleDisplay' -Description 'Lets the SWG project owner''s PC ($OwnerPC) use Ollama here. Remove with install-ollama-lan.ps1 -Remove.' -Direction Inbound -Action Allow -Protocol TCP -LocalPort $Port -RemoteAddress '$OwnerPC' -Profile Private -Program '$quotedExe' | Out-Null
"@
if ($others.Count) {
    Say '   Other enabled rules cover Ollama or its port:'
    foreach ($r in $others) { Say "     '$($r.DisplayName)': $($r.Action), profile $($r.Profile)" }
    Say '   An Allow rule opens Ollama to more than the owner''s PC; a Block rule shuts the owner''s PC out.'
    if (Ask '   Disable these rules (they stay in the list and can be turned back on)?') {
        $names = ($others | ForEach-Object { "'" + $_.Name.Replace("'", "''") + "'" }) -join ','
        $ruleCode += "`nDisable-NetFirewallRule -Name $names"
    } else { Warn 'other firewall rules for Ollama are still enabled' }
}
if (-not (Invoke-AsAdmin $ruleCode 'to add the firewall rule')) { Stop-Here 'the firewall rule was not added' }
Good "rule $RuleName`: TCP $Port from $OwnerPC only, Private networks only, $exe only"

# ------------------------------------------------------------------------------------------------------- 4 power
Step '4. Sleep'
$state = Get-State
if (-not $state) { $state = New-Object psobject }
if (-not ($state.PSObject.Properties.Name -contains 'SleepACMinutes')) { $state | Add-Member SleepACMinutes $null }
$sleep = Get-SleepAC
if ($null -eq $sleep) { Say '   could not read the sleep setting; leaving it alone' }
elseif ($sleep -eq 0) { Good 'this PC never sleeps on mains power already' }
else {
    Say "   This PC sleeps after $sleep min without use. Asleep, it can't run jobs, and Miniverse uses its own model instead."
    if (Ask '   Turn sleep off while plugged in (screen and lock are not affected; -Remove sets it back)?') {
        powercfg /change standby-timeout-ac 0 | Out-Null
        if ($LASTEXITCODE -ne 0 -or (Get-SleepAC) -ne 0) { Warn 'could not turn sleep off (Settings, System, Power: Sleep, Never)' }
        else {
            if ($null -eq $state.SleepACMinutes) { $state.SleepACMinutes = $sleep }
            Good "sleep on mains power: never (was $sleep min)"
        }
    } else { Say '   left as it is' }
}
Save-State $state

# ------------------------------------------------------------------------------------------------------- start
Step 'Starting Ollama'
if (-not (Start-Ollama $exe)) { Stop-Here 'Ollama did not start within 60 s (look at %LOCALAPPDATA%\Ollama\server.log)' }
$v = Get-Api '/api/version'
Good "Ollama $($v.version) is running"
$l = Get-Listener
if (-not $l -or $l.Address -ne '0.0.0.0') {
    Warn "Ollama listens on $(if ($l) { $l.Address } else { 'nothing' }):$Port, so Miniverse can't reach it. Quit Ollama (tray icon, Quit), sign out of Windows and in again, then run this script with -CheckOnly"
} else { Good "listening on 0.0.0.0:$Port" }
if ($l -and $l.Path -and $l.Path -ne $exe) {
    Warn "the listening program is $($l.Path), not $exe; run the script again so the rule follows it"
}

# ------------------------------------------------------------------------------------------------------- 5 models
Step '5. Models'
$env:OLLAMA_HOST = "127.0.0.1:$Port"   # for the ollama command in this window only; the server keeps 0.0.0.0
if (-not $SkipPull) {
    foreach ($m in $Models) {
        Say "   ollama pull $m"
        & $exe pull $m
        if ($LASTEXITCODE -ne 0) { Warn "ollama pull $m failed (run the script again; finished downloads are kept)" }
    }
}
$tags = Get-Api '/api/tags' 10
$have = @(); if ($tags) { $have = @($tags.models | ForEach-Object { $_.name }) }

# ------------------------------------------------------------------------------------------------------- 6 test
Step '6. Self-test (each model answers once; speed and the GPU share are printed)'
foreach ($m in $Models) {
    if ($have -notcontains $m) { Warn "model $m is not here, not tested"; continue }
    $ctx = if ($TestCtx.ContainsKey($m)) { $TestCtx[$m] } else { 8192 }
    $free = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB, 1)
    $size = if ($SizeGB.ContainsKey($m)) { $SizeGB[$m] } else { 10 }
    if ($size -gt 12 -and $free -lt ($size - 10 + 6)) {
        Warn "$m skipped: only $free GB of RAM free (close other programs and run the script again with -SkipPull)"; continue
    }
    $body = @{ model = $m; prompt = 'In one short sentence: what is a moisture farm?'; stream = $false; think = $false
               keep_alive = '2m'; options = @{ num_ctx = $ctx; num_predict = 60; temperature = 0 } }
    $r = $null
    try { $r = Invoke-RestMethod -Uri "$Local/api/generate" -Method Post -ContentType 'application/json' -TimeoutSec 900 -Body ($body | ConvertTo-Json -Depth 4) }
    catch {
        $body.Remove('think')   # a model without a thinking switch refuses the flag
        try { $r = Invoke-RestMethod -Uri "$Local/api/generate" -Method Post -ContentType 'application/json' -TimeoutSec 900 -Body ($body | ConvertTo-Json -Depth 4) }
        catch { Warn "$m did not answer: $($_.Exception.Message)"; continue }
    }
    $speed = if ($r.eval_duration) { [math]::Round($r.eval_count / ($r.eval_duration / 1e9), 1) } else { 0 }
    $load = [math]::Round($r.load_duration / 1e9, 0)
    $gpu = '?'
    $ps = Get-Api '/api/ps'
    if ($ps) {
        $entry = $ps.models | Where-Object { $_.name -eq $m } | Select-Object -First 1
        if ($entry -and $entry.size) { $gpu = [math]::Round(100 * $entry.size_vram / $entry.size) }
    }
    $answer = (($r.response -replace '\s+', ' ').Trim())
    if ($answer.Length -gt 90) { $answer = $answer.Substring(0, 90) + '...' }
    Good "$m at $ctx tokens: $speed tokens/s, $gpu% on the GPU, loaded in $load s: `"$answer`""
    [void]$script:Result.Add("$m ctx $ctx : $speed tok/s, $gpu% GPU, load $load s")
    try { Invoke-RestMethod -Uri "$Local/api/generate" -Method Post -ContentType 'application/json' -TimeoutSec 60 -Body (@{ model = $m; keep_alive = 0 } | ConvertTo-Json) | Out-Null } catch {}
}

# ------------------------------------------------------------------------------------------------------- done
Step 'Done'
$line = "http://$($lan.IP):$Port"
Say "Tell Claude on Miniverse this address:   $line"
Say "(Miniverse can test it with:   curl.exe $line/api/tags )"
Say ''
Say 'Next:'
Say "  - Ask the router to keep this PC's address ($($lan.IP)) and the owner's ($OwnerPC) fixed (a DHCP reservation)."
Say '    If the owner''s address changes, run this script again with the new -OwnerPC.'
Say '  - Before gaming, quit Ollama (tray icon, Quit Ollama). Start it again from the Start menu afterwards.'
Say '  - To close it again: the same command with -Remove.'
$report = @("SWG Ollama setup, $(Get-Date -Format 'yyyy-MM-dd HH:mm')", "address: $line", "Miniverse: $OwnerPC",
            "Ollama: $($v.version)", "models: $($have -join ', ')") + $script:Result + ($script:Problems | ForEach-Object { "CHECK: $_" })
Set-Content -Encoding UTF8 (Join-Path $StateDir 'last-run.txt') $report
Say "  - This summary is saved in $StateDir\last-run.txt"
if ($script:Problems.Count) {
    Step "$($script:Problems.Count) thing(s) to check (yellow lines above)"
    foreach ($p in $script:Problems) { Say "  - $p" }
    exit 1
}
exit 0
