# Running the local model on the friend's PC

For the owner and the friend (Claude, 15 Oct 2026). The project's local-model scripts (idle research, the names sweep,
`local_agent.py`) normally talk to Ollama on Miniverse. This page moves that to the friend's Windows PC (RTX 4070)
on the same home network, which frees about 5 GB of RAM and the CPU on Miniverse and keeps its GPU free for the
game client. Nothing changes until the owner creates `ollama-url.txt` (step 4); delete that file to go back.

## Before you start: the owner's call

- **What crosses the network:** every request the scripts send, which means the research brief **and the project text
  the model is asked to read** (Core3 server source, scenario files, board text), plus everything the model answers.
  It goes as plain `http://` over the home network, so anyone on that network could read it, and the friend's PC sees
  it all. Ollama only receives text; it cannot read the owner's files. At default settings Ollama's own log records
  request lines, not prompt text (`OLLAMA_DEBUG` would change that).
- AGENTS.md says nothing that leaves this PC may name real people, except author credits that a licence requires. Source
  file headers carry such credits, so the owner decides whether sending project text to a friend's PC is acceptable.
- **The friend's PC must be on, awake and not busy.** Miniverse can see only what Ollama reports, not the friend's
  games, so the friend should **quit Ollama (tray icon, Quit Ollama) before gaming**. Research then waits by itself and
  starts again 10 quiet minutes after Ollama is back.
- Speed is untested. An RTX 4070 has 12 GB, and `gpt-oss:20b` needs about 14 GB, so it is split between the GPU and the
  CPU there too (as on Miniverse); the friend's better CPU is what should help.

## 1. On the friend's PC

1. Install Ollama for Windows from ollama.com/download (it runs as a tray icon).
2. Open a terminal and pull the model (about 14 GB; keep 20 GB of disk free):

   ```
   ollama pull gpt-oss:20b
   ```

   No Modelfile is needed: the scripts ask for a 64K context in every request.
3. Make Ollama listen on the network. It listens on this PC only unless told otherwise. Set a user variable (no admin
   rights needed), then **quit Ollama from the tray icon and start it again** (a running Ollama doesn't see new variables):

   ```
   setx OLLAMA_HOST "0.0.0.0:11434"
   ```

   Check after the restart: `netstat -ano | findstr 11434` shows `0.0.0.0:11434` in the LISTENING state.
   Leave `OLLAMA_KEEP_ALIVE` unset (the default 5 minutes); the owner's idle check relies on models timing out.
4. Open the firewall for the home network only. In PowerShell **as administrator**:

   ```
   New-NetFirewallRule -DisplayName "Ollama LAN 11434" -Direction Inbound -Protocol TCP -LocalPort 11434 -Action Allow -RemoteAddress LocalSubnet -Profile Private
   ```

   The rule applies when Windows calls the network **Private** (Settings, Network & internet, the connection, Network
   profile type). If Windows asks "allow Ollama on networks", allow Private only. `LocalSubnet` means other PCs on the
   same subnet; nothing from the internet.
5. **Never port-forward 11434 on the router** (and don't enable UPnP for it). Ollama has no password: anyone who can
   reach the port can run the friend's GPU and read the model list.
6. Find the PC's address with `ipconfig` (IPv4 Address, for example 192.168.x.y). Ask the router to always give this
   PC the same address (a DHCP reservation), or the address in step 4 below will go stale.

## 2. Test from Miniverse

Use the friend's address in place of `<friend-ip>`. This is the only request to try; it lists the models.

From Windows (PowerShell; say `curl.exe`, because plain `curl` is a different command there):

```
curl.exe http://<friend-ip>:11434/api/tags
```

From WSL Debian (it uses mirrored networking, so it reaches the home network directly):

```
wsl -d Debian -u swgemu -- curl -s http://<friend-ip>:11434/api/tags
```

Both should print JSON that includes `gpt-oss:20b`. If not:

| What you see | Likely cause |
|---|---|
| Hangs, then times out | Windows Firewall: the rule is missing, or the network is "Public"; or the address is wrong |
| "Connection refused" | Ollama still listens on this PC only: `OLLAMA_HOST` isn't set for that Windows user, or Ollama wasn't restarted |
| Works from Windows but not from WSL | WSL isn't in mirrored networking (the owner's Debian is); check `.wslconfig` |
| JSON without `gpt-oss:20b` | `ollama pull gpt-oss:20b` didn't finish on the friend's PC |

## 3. Point the scripts at it

Create `outputs/tools/agents/local/ollama-url.txt` with one line (Notepad is fine; PowerShell's `>` also works):

```
http://<friend-ip>:11434
```

The file is gitignored, because a home-network address is private. One line, optionally with `#` comment lines above it.
`192.168.x.y` alone also works (`http://` and `:11434` are added).

The Ollama address comes from `ollama_url.py`, in this order: the `OLLAMA_URL` environment variable, then this file,
then `http://127.0.0.1:11434` (Ollama on this PC). A variable set in a terminal affects only commands started from that
terminal; the WSL timer never sees it, so use the file for the timer. Check what a script will use:

```
wsl -d Debian -u swgemu -- python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/agents/local/ollama_url.py
wsl -d Debian -u swgemu -- python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/agents/local/idle_research.py status
```

The first prints the address ("this PC" or "another PC"), the model and the context size. A typo in a file or variable
is an error, not a quiet fallback to the default. For one run:
`python -I local_agent.py --workspace DIR --task "..." --ollama-url http://<friend-ip>:11434 [--model M] [--ctx N]`.
Scripts you write should call `ollama_url.api('/api/chat')` instead of a fixed address.

### Model and context size

Which model the scripts ask for, and how big a context window, are set the same way (variable, then file, then default),
wherever the server is:

| Setting | Variable | File (gitignored, one line) | Default |
|---|---|---|---|
| address | `OLLAMA_URL` | `ollama-url.txt` | `http://127.0.0.1:11434` |
| model | `OLLAMA_MODEL` | `ollama-model.txt` | `gpt-oss:20b` |
| context size, in tokens | `OLLAMA_CTX` | `ollama-ctx.txt` | `65536` |

The files live in `outputs/tools/agents/local/` and are read on this PC, so they apply to whichever server the address
points at. A model that fits entirely on a 12 GB card keeps the RAM and CPU use down. For example, to run `qwen3:8b`
with a 32K window, put `qwen3:8b` in `ollama-model.txt` and `32768` in `ollama-ctx.txt`; the friend's PC can later use
`gpt-oss:20b` and 65536 (the defaults) by deleting both files. The model must already be on the server
(`ollama pull qwen3:8b` there); if it isn't, `idle_research.py status` says so and no topic is started. The scripts
never pull or load anything themselves.

`idle_research.py` hands both to `local_agent.py` (`--model`, `--ctx`) and scales the amount of source it copies in
for a topic with the window: 120,000 characters at 65536 tokens, 60,000 at 32768. `qwen3:8b` with this tool loop is
untested: check the first report it writes before relying on it.

`swg-idle-research.timer` needs no change: it runs `idle_research.py check` every 5 minutes and reads the file each time.
If `outputs/Agent/local-research/STOP` exists (the owner paused research while Ollama ran out of memory on this PC),
delete it to let research run.

**To go back to Ollama on this PC:** delete `ollama-url.txt` (and unset `OLLAMA_URL`). Nothing else changes.

## How "idle" works with a server on another PC

On this PC the check reads Ollama's log, the GPU load and the SWG client; none of that exists for another PC, so those
checks are skipped. Instead each timer run asks the server which models are loaded and when they expire (`/api/ps`).
A finished request moves a model's expiry, so:

- the same answer on consecutive timer runs means nobody used the server in between; **10 minutes of that** (counted in
  `Agent/local-research/state.json`, which holds a hash, not the address) start the next topic. The first topic
  therefore starts on the third timer run, 10 minutes after the first look (and `status` alone never records a look);
- any use by anyone, a model loaded or unloaded early, a model past its expiry (a long request in progress), or the
  server not answering restarts the count;
- the runner's own topics don't restart it, so topics still follow each other;
- if the friend's PC goes off mid-topic, that topic goes back to `open` instead of `failed`.

What this cannot see: the friend gaming, other GPU programs, or Ollama requests with `keep_alive: 0`. That is why the
friend quits Ollama before gaming. If a model never expires (`OLLAMA_KEEP_ALIVE=-1`), use can't be told and research
won't start; `status` says so.

## Tests

`test_ollama_url.py` (offline: a fake Ollama on 127.0.0.1; it fails if a test tries any other address) covers the
address order, the idle rules for this PC and for another PC, a skewed clock on the other PC, and the run bookkeeping:

```
wsl -d Debian -u swgemu -- python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/agents/local/test_ollama_url.py
```

Not tested: a real second PC (it wasn't set up when this was written).
