# GPT relay: hands queued tasks (outputs/Agent/gpt-queue.json) to ChatGPT through Codex's non-interactive mode when
# GPT's usage allows. Claude's scheduled check runs "-Dispatch" every 30 minutes.
#
#   powershell -ExecutionPolicy Bypass -File gpt_relay.ps1 -Dispatch   probe GPT; if ready, start the next open task per lane
#   powershell -ExecutionPolicy Bypass -File gpt_relay.ps1 -Status     what is queued, running and done
#
# Runs use GPT-6.1 Sol with full access (-s danger-full-access), so GPT can run WSL: the owner chose full access on
# 14 Oct 05:58 (it replaced the 13 Oct workspace-write + --approve-for-me setup; Codex won't combine -s with that flag).
# Results: outputs/Agent/relay/<time>-<task>.md (GPT's final answer) and .log.
#
# Since 15 Oct (owner: "can gpt run the bots parallel to the sweep?", "tune the gpt overnight relay a bit better"):
#   * Lanes. A task's "lane" is "desk" (reading, reviews, code; the default) or "bots" (it drives test-galaxy bots).
#     One task runs per lane, so a bot job and a desk job can run side by side. Locks: Agent/relay/RUNNING (desk) and
#     Agent/relay/RUNNING-bots.
#   * Memory guard. No task starts while Windows has under 6 GB of commit headroom or 1.5 GB of free RAM (15 Oct 07:31:
#     a run crashed at once with "memory allocation failed" while the local model held 22 GB).
#   * One retry. A run that crashes (an exit code outside 0-255) within 10 minutes goes back to "open" once ("retries").
#   * Orphans. A task still marked "running" with no live worker for its lane (the PC restarted, the worker was killed)
#     goes back to "open" once, then "failed".
param([switch]$Dispatch, [switch]$Status, [string]$Run = '')

$ErrorActionPreference = 'Stop'
# The app's own CLI (it has the sandbox command runner beside it); the newest version folder wins.
$codex = Get-ChildItem (Join-Path $env:LOCALAPPDATA 'OpenAI\Codex\bin') -Recurse -Filter 'codex.exe' -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1 -ExpandProperty FullName
if (-not $codex) { $codex = Join-Path $env:USERPROFILE '.codex\.sandbox-bin\codex.exe' }
$h = 'C:\Users\Pengw\Documents\Codex\2026-10-13\h'
$queuePath = Join-Path $h 'outputs\Agent\gpt-queue.json'
$relayDir = Join-Path $h 'outputs\Agent\relay'
$statusLog = Join-Path $relayDir 'status.log'
$model = 'gpt-6.1-sol'
$lanes = @('desk', 'bots')
$minCommitGB = 6
$minFreeGB = 1.5
$maxRetries = 1
New-Item -ItemType Directory -Force $relayDir | Out-Null

function Note([string]$text) {
    $line = (Get-Date -Format 'yyyy-MM-dd HH:mm') + '  ' + $text
    Add-Content -Path $statusLog -Value $line -Encoding UTF8
    Write-Output $line
}

function Load-Queue { Get-Content $queuePath -Raw -Encoding UTF8 | ConvertFrom-Json }

function Save-Queue($queue) { $queue | ConvertTo-Json -Depth 6 | Set-Content -Path $queuePath -Encoding UTF8 }

function Lane-Of($task) { if ($task.PSObject.Properties['lane'] -and $task.lane -eq 'bots') { 'bots' } else { 'desk' } }

function Lock-Of([string]$lane) { if ($lane -eq 'bots') { Join-Path $relayDir 'RUNNING-bots' } else { Join-Path $relayDir 'RUNNING' } }

function Set-Field($task, [string]$name, $value) {
    if ($task.PSObject.Properties[$name]) { $task.$name = $value } else { $task | Add-Member -NotePropertyName $name -NotePropertyValue $value }
}

function Retries($task) { if ($task.PSObject.Properties['retries']) { [int]$task.retries } else { 0 } }

function Busy([string]$lane) {
    $lock = Lock-Of $lane
    if (-not (Test-Path $lock)) { return $null }
    $parts = (Get-Content $lock -Raw).Trim() -split '\s+'
    $process = Get-Process -Id ([int]$parts[0]) -ErrorAction SilentlyContinue
    if ($process) { return "$($parts[1]) (pid $($parts[0]), since $($parts[2]))" }
    Remove-Item $lock -Force  # stale: the run ended without cleaning up
    return $null
}

function Memory {
    $os = Get-CimInstance Win32_OperatingSystem
    [pscustomobject]@{ CommitFreeGB = [math]::Round($os.FreeVirtualMemory / 1MB, 1); FreeGB = [math]::Round($os.FreePhysicalMemory / 1MB, 1) }
}

if ($Status) {
    $queue = Load-Queue
    foreach ($task in $queue.tasks) { Write-Output ("{0,-8} {1}" -f $task.status, $task.id) }
    foreach ($lane in $lanes) { $b = Busy $lane; if ($b) { Write-Output "running: $b [$lane]" } }
    $m = Memory
    Write-Output "memory: $($m.CommitFreeGB) GB commit headroom, $($m.FreeGB) GB free"
    if (Test-Path $statusLog) { Get-Content $statusLog -Tail 5 }
    exit 0
}

if ($Run) {
    $queue = Load-Queue
    $task = $queue.tasks | Where-Object { $_.id -eq $Run } | Select-Object -First 1
    $lane = Lane-Of $task
    $stamp = Get-Date -Format 'yyyyMMdd-HHmm'
    $answer = Join-Path $relayDir "$stamp-$Run.md"
    $log = Join-Path $relayDir "$stamp-$Run.log"
    $exitCode = 1
    $began = Get-Date
    $promptFile = Join-Path $relayDir "$stamp-$Run.prompt.txt"
    Set-Content -Path $promptFile -Value $task.prompt -Encoding UTF8
    try {
        # The prompt goes in on stdin ("-"): no quoting problems with long text.
        $p = Start-Process -FilePath $codex -PassThru -Wait -NoNewWindow -RedirectStandardInput $promptFile `
            -RedirectStandardOutput $log -RedirectStandardError "$log.err" -ArgumentList @('exec', '--skip-git-repo-check',
            '-C', $h, '-m', $model, '-c', "model_reasoning_effort=$($task.effort)",
            '-s', 'danger-full-access', '-o', $answer, '-')
        $exitCode = $p.ExitCode
    } catch {
        Add-Content -Path $log -Value ("relay error: " + $_.Exception.Message)
    }
    $seconds = [int]((Get-Date) - $began).TotalSeconds
    $queue = Load-Queue
    $task = $queue.tasks | Where-Object { $_.id -eq $Run } | Select-Object -First 1
    $crashed = ($exitCode -lt 0 -or $exitCode -gt 255) -and $seconds -lt 600
    if ($exitCode -eq 0 -and (Test-Path $answer) -and (Get-Item $answer).Length -gt 0) {
        $task.status = 'done'
    } elseif ($crashed -and (Retries $task) -lt $maxRetries) {
        $task.status = 'open'
        Set-Field $task 'retries' ((Retries $task) + 1)
    } else {
        $task.status = 'failed'
    }
    Save-Queue $queue
    Remove-Item (Lock-Of $lane) -Force -ErrorAction SilentlyContinue
    $how = if ($task.status -eq 'open') { ' (crashed early; requeued once)' } else { '' }
    Note "finished $Run with exit $exitCode after $seconds s -> $($task.status)$how; answer $answer"
    exit 0
}

if ($Dispatch) {
    $queue = Load-Queue
    $changed = $false
    # Orphans: "running" with no live worker in its lane.
    foreach ($task in @($queue.tasks | Where-Object { $_.status -eq 'running' })) {
        if (-not (Busy (Lane-Of $task))) {
            if ((Retries $task) -lt $maxRetries) { $task.status = 'open'; Set-Field $task 'retries' ((Retries $task) + 1) } else { $task.status = 'failed' }
            Note "orphan: $($task.id) was running with no worker -> $($task.status)"
            $changed = $true
        }
    }
    if ($changed) { Save-Queue $queue }
    $want = @()
    foreach ($lane in $lanes) {
        $b = Busy $lane
        if ($b) { Note "busy [$lane]: $b"; continue }
        $next = $queue.tasks | Where-Object { $_.status -eq 'open' -and (Lane-Of $_) -eq $lane } | Select-Object -First 1
        if ($next) { $want += $next }
    }
    if ($want.Count -eq 0) { Note 'nothing to start'; exit 0 }
    $m = Memory
    if ($m.CommitFreeGB -lt $minCommitGB -or $m.FreeGB -lt $minFreeGB) {
        Note "not ready: low memory ($($m.CommitFreeGB) GB commit headroom, $($m.FreeGB) GB free)"
        exit 0
    }
    # Probe: a one-word answer costs almost nothing and fails fast while GPT's usage limit is reached.
    $probeOut = Join-Path $env:TEMP 'gpt-relay-probe.txt'
    $probeIn = Join-Path $env:TEMP 'gpt-relay-probe-in.txt'
    Set-Content -Path $probeIn -Value 'Reply with exactly the word READY and nothing else.' -Encoding ASCII
    $probe = Start-Process -FilePath $codex -PassThru -NoNewWindow -RedirectStandardInput $probeIn -RedirectStandardOutput $probeOut `
        -RedirectStandardError "$probeOut.err" -ArgumentList @('exec', '--ephemeral', '--skip-git-repo-check', '-C', $h,
        '-m', $model, '-c', 'model_reasoning_effort=low', '-s', 'read-only', '-')
    if (-not $probe.WaitForExit(180000)) { $probe.Kill(); Note 'not ready: probe timed out'; exit 0 }
    $said = ((Get-Content $probeOut -Raw -ErrorAction SilentlyContinue) + '')
    if ($said -notmatch 'READY') {
        $why = ((Get-Content "$probeOut.err" -Tail 3 -ErrorAction SilentlyContinue) -join ' ').Trim()
        if ($why.Length -gt 300) { $why = $why.Substring(0, 300) }
        Note "not ready: $why"
        exit 0
    }
    foreach ($next in $want) {
        $queue = Load-Queue
        $task = $queue.tasks | Where-Object { $_.id -eq $next.id } | Select-Object -First 1
        $lane = Lane-Of $task
        $task.status = 'running'
        Save-Queue $queue
        # Started through WMI so the worker outlives the shell that dispatched it.
        $command = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Run $($task.id)"
        $made = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $command }
        if ($made.ReturnValue -ne 0) { $task.status = 'open'; Save-Queue $queue; Note "could not start worker ($($made.ReturnValue))"; continue }
        Set-Content -Path (Lock-Of $lane) -Value "$($made.ProcessId) $($task.id) $(Get-Date -Format 'HH:mm')"
        Note "started $($task.id) [$lane] (effort $($task.effort)) as pid $($made.ProcessId)"
    }
    exit 0
}

Write-Output 'Use -Dispatch or -Status (see the top of this file).'
