"""Memory guard for the local model on this PC (Claude, 15 Oct 2026).

Why: Ollama's runner keeps every finished prompt's KV state in a host-RAM prompt cache. With qwen3:8b that is about
0.5 GB per request of ~4K tokens, and it grew Windows' commit charge by ~15 GB in 25 requests on 15 Oct (the
log says "making room for prompt cache entry"); the 07:31 out-of-memory crash on 15 Oct very likely had the same
cause. Unloading the model (keep_alive 0) empties the cache. So the local-model scripts check the commit headroom
before each request and unload the model every few requests.

    commit_headroom_gb()        free commit (GB) on Windows, from Windows itself or from WSL; None if unknown
    unload(base, model)         ask Ollama at base to unload model now (errors ignored)
    MIN_HEADROOM_GB             below this, stop or don't start (the GPT relay's own guard is 6 GB too)

commit_headroom_gb() is about this PC only, so the callers skip it for a server on another PC (REMOTE-OLLAMA.md). The
regular unload applies to every server (17 Oct): the prompt cache grows the same way in the other PC's RAM.
"""
import json
import subprocess
import sys
import urllib.request

MIN_HEADROOM_GB = 6.0
POWERSHELL = '/mnt/c/WINDOWS/System32/WindowsPowerShell/v1.0/powershell.exe'


def _windows_headroom_gb():
    import ctypes

    class MemoryStatus(ctypes.Structure):
        _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                    ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong),
                    ('ullTotalPageFile', ctypes.c_ulonglong), ('ullAvailPageFile', ctypes.c_ulonglong),
                    ('ullTotalVirtual', ctypes.c_ulonglong), ('ullAvailVirtual', ctypes.c_ulonglong),
                    ('ullAvailExtendedVirtual', ctypes.c_ulonglong)]
    status = MemoryStatus()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        return None
    return status.ullAvailPageFile / 2**30


def _wsl_headroom_gb():
    """From inside WSL, ask Windows (interop; the timer's tasklist.exe check uses the same route)."""
    try:
        out = subprocess.run([POWERSHELL, '-NoProfile', '-NonInteractive', '-Command',
                              '(Get-CimInstance Win32_OperatingSystem).FreeVirtualMemory'],
                             capture_output=True, text=True, timeout=60).stdout
        return int(out.strip().splitlines()[-1]) / 2**20   # KB -> GB
    except (OSError, subprocess.SubprocessError, ValueError, IndexError):
        return None


def commit_headroom_gb():
    """Windows' available commit in GB (what is left before allocations fail), or None when it can't be read."""
    if sys.platform == 'win32':
        try:
            return _windows_headroom_gb()
        except (OSError, AttributeError):
            return None
    return _wsl_headroom_gb()


def unload(base, model):
    """Unload model on the Ollama server at base (drops its prompt cache too). Never raises."""
    body = json.dumps({'model': model, 'messages': [], 'keep_alive': 0}).encode()
    try:
        request = urllib.request.Request(base.rstrip('/') + '/api/chat', body, {'Content-Type': 'application/json'})
        urllib.request.urlopen(request, timeout=60).read()
    except Exception:
        pass
