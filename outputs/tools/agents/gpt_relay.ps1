# GPT relay: hands the next queued task (outputs/Agent/gpt-queue.json) to ChatGPT through Codex's
# non-interactive mode when GPT's usage allows. Claude's scheduled check runs "-Dispatch" every 30 minutes.
#
#   powershell -ExecutionPolicy Bypass -File gpt_relay.ps1 -Dispatch   probe GPT; if ready, start the next open task
#   powershell -ExecutionPolicy Bypass -File gpt_relay.ps1 -Status     what is queued, running and done
#
# Runs use GPT-6.1 Sol with full access (-s danger-full-access), so GPT can run WSL: the owner chose full access on
# 14 Oct 05:58 (it replaced the 13 Oct workspace-write + --approve-for-me setup; Codex won't combine -s with that flag). Results: outputs/Agent/relay/<time>-<task>.md (GPT's final answer) and .log.
param([switch]$Dispatch, [switch]$Status, [string]$Run = '')

$ErrorActionPreference = 'Stop'
# The app's own CLI (it has the sandbox command runner beside it); the newest version folder wins.
$codex = Get-ChildItem (Join-Path $env:LOCALAPPDATA 'OpenAI\Codex\bin') -Recurse -Filter 'codex.exe' -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1 -ExpandProperty FullName
if (-not $codex) { $codex = Join-Path $env:USERPROFILE '.codex\.sandbox-bin\codex.exe' }
$h = 'C:\Users\Pengw\Documents\Codex\2026-10-13\h'
$queuePath = Join-Path $h 'outputs\Agent\gpt-queue.json'
$relayDir = Join-Path $h 'outputs\Agent\relay'
$lock = Join-Path $relayDir 'RUNNING'
$statusLog = Join-Path $relayDir 'status.log'
$model = 'gpt-6.1-sol'
New-Item -ItemType Directory -Force $relayDir | Out-Null

function Note([string]$text) {
    $line = (Get-Date -Format 'yyyy-MM-dd HH:mm') + '  ' + $text
    Add-Content -Path $statusLog -Value $line -Encoding UTF8
    Write-Output $line
}

function Load-Queue { Get-Content $queuePath -Raw -Encoding UTF8 | ConvertFrom-Json }

function Save-Queue($queue) { $queue | ConvertTo-Json -Depth 6 | Set-Content -Path $queuePath -Encoding UTF8 }

function Busy {
    if (-not (Test-Path $lock)) { return $null }
    $parts = (Get-Content $lock -Raw).Trim() -split '\s+'
    $process = Get-Process -Id ([int]$parts[0]) -ErrorAction SilentlyContinue
    if ($process) { return "$($parts[1]) (pid $($parts[0]), since $($parts[2]))" }
    Remove-Item $lock -Force  # stale: the run ended without cleaning up
    return $null
}

if ($Status) {
    $queue = Load-Queue
    foreach ($task in $queue.tasks) { Write-Output ("{0,-8} {1}" -f $task.status, $task.id) }
    $b = Busy; if ($b) { Write-Output "running: $b" }
    if (Test-Path $statusLog) { Get-Content $statusLog -Tail 5 }
    exit 0
}

if ($Run) {
    $queue = Load-Queue
    $task = $queue.tasks | Where-Object { $_.id -eq $Run } | Select-Object -First 1
    $stamp = Get-Date -Format 'yyyyMMdd-HHmm'
    $answer = Join-Path $relayDir "$stamp-$Run.md"
    $log = Join-Path $relayDir "$stamp-$Run.log"
    $exitCode = 1
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
    $queue = Load-Queue
    $task = $queue.tasks | Where-Object { $_.id -eq $Run } | Select-Object -First 1
    if ($exitCode -eq 0 -and (Test-Path $answer) -and (Get-Item $answer).Length -gt 0) { $task.status = 'done' } else { $task.status = 'failed' }
    Save-Queue $queue
    Remove-Item $lock -Force -ErrorAction SilentlyContinue
    Note "finished $Run with exit $exitCode -> $($task.status); answer $answer"
    exit 0
}

if ($Dispatch) {
    $b = Busy
    if ($b) { Note "busy: $b"; exit 0 }
    $queue = Load-Queue
    $next = $queue.tasks | Where-Object { $_.status -eq 'open' } | Select-Object -First 1
    if (-not $next) { Note 'queue empty'; exit 0 }
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
    $next.status = 'running'
    Save-Queue $queue
    # Started through WMI so the worker outlives the shell that dispatched it.
    $command = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Run $($next.id)"
    $made = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $command }
    if ($made.ReturnValue -ne 0) { $next.status = 'open'; Save-Queue $queue; Note "could not start worker ($($made.ReturnValue))"; exit 1 }
    Set-Content -Path $lock -Value "$($made.ProcessId) $($next.id) $(Get-Date -Format 'HH:mm')"
    Note "started $($next.id) (effort $($next.effort)) as pid $($made.ProcessId)"
    exit 0
}

Write-Output 'Use -Dispatch or -Status (see the top of this file).'
