# Ollama on the friend's PC: how-to

For the owner, at the friend's PC (Claude, 17 Oct 2026). The friend has agreed to all of it (owner, 17 Oct). One
script installs Ollama, downloads the project's models, lets **only Miniverse** use them over the home network, and tests
them. Miniverse then sends its local-model jobs there, and uses its own model whenever this PC is off.
How the two agents use it: [Agent/local-model.md](../../../../Agent/local-model.md).

## What the friend agreed to

- **Ollama** (ollama.com's official installer) is installed for their Windows user, with about 73 GB of models.
- **Their graphics card runs our jobs** while Ollama is idle on the owner's side: research topics, proofreading,
  sorting bot notes, and later drafting bot chat lines. The biggest model also uses about 15 GB of their RAM while it
  is loaded.
- **What crosses the home network:** the text of each job. That means server source code, bot test notes, our game
  text and the model's answers, sent as plain `http` between the two PCs only. Jobs that hold real people's names
  stay on Miniverse.
- **One firewall rule** lets Miniverse in: port 11434, from that one address, on the Private (home) network only.
  Ollama has no password, so **never forward port 11434 on the router**.

## Before you start

- About **80 GB free** on drive C: for all seven models. With less, the script takes them in the order below and says
  which it left out.
- The **Miniverse address**: on Miniverse, `ipconfig` shows it as "IPv4 Address" (192.168.1.something).
- The friend's Windows account, signed in. It needs to be an administrator account, or you need one for the firewall
  prompt.
- Time: the downloads are about 73 GB (less if some models are already there).

## Run it

1. Copy this folder (`install-ollama-lan.ps1` and `install.cmd`) to the friend's PC, for example to Downloads.
2. Open **PowerShell** (Start menu, type PowerShell, open it normally, **not** as administrator) and run, with the
   owner's address:

   ```
   powershell -ExecutionPolicy Bypass -File "$HOME\Downloads\install-ollama-lan.ps1" -OwnerPC 192.168.1.x
   ```

   Or double-click `install.cmd`, which asks for the address. If Windows says "Windows protected your PC", click
   More info, then Run anyway.
3. What happens, in order:
   - **Checks:** Windows, RAM, graphics card and driver, the network (it must be Private), disk space. Nothing is
     changed if a check stops it.
   - **1. Ollama:** downloaded from ollama.com and installed, but only if the file is signed by Ollama Inc.
   - **2. Settings:** three user variables (Ollama listens on the network, one model in memory at a time, one job at
     a time).
   - **3. Firewall:** Windows asks for an administrator once. Click Yes.
   - **4. Sleep:** it asks whether to stop the PC sleeping while plugged in, so jobs can run while the friend is
     away. Say yes for the week away. The screen still turns off and the PC still locks.
   - **5. Models**, in this order: `qwen3.6:35b-a3b` (24 GB, the research model), `qwen3.5:9b` (7 GB, fast
     jobs), `gemma4:12b` (8 GB, bot chat), `qwen3:8b` (5 GB, the same model as Miniverse), `gpt-oss:20b`
     (14 GB, the older research default), `gpt-oss-20b-64k`, built from gpt-oss:20b with a 64K window (no
     download), and WaifuGemma4 26B-A4B (13.9 GB, from Hugging Face; role-play and NPC dialogue drafts; its card
     says 18+ only). The progress shows in the window. Models already there are not downloaded again.
   - **6. Self-test:** each model answers one short question. The script prints its speed and how much of it ran on
     the graphics card.
4. At the end it prints **"Tell Claude on Miniverse this address: http://192.168.1.y:11434"**. Give that line
   to Claude. It is also saved in `%LOCALAPPDATA%\swg-ollama-lan\last-run.txt`.

If Windows shows "Allow Ollama on networks?" at any point, tick **Private** only, click Allow, and run the script again.
It then offers to switch off the extra rule Windows made.

## Afterwards

- **Ask the router to keep both addresses fixed** (a "DHCP reservation" in the router's settings) for the friend's PC
  and Miniverse. If an address changes anyway: a new friend address goes to Claude; a new owner address means
  running the script again with the new `-OwnerPC`.
- **Before gaming:** quit Ollama (tray icon by the clock, Quit Ollama), and start it again from the Start menu
  afterwards. Miniverse sees only Ollama, not the game, so it can't tell the friend is busy.
- **Check later**, changing nothing: the same command with `-CheckOnly` at the end.
- **Undo:** the same command with `-Remove` (no `-OwnerPC` needed). It removes the firewall rule and the three
  variables, puts the sleep setting back and restarts Ollama for this PC only. Ollama and the models stay. To remove
  them as well: Settings, Apps, Ollama, Uninstall, then delete the folder `%USERPROFILE%\.ollama`.

## Will the models fit?

The friend's PC has an RTX 4070 Super (12 GB) and 32 GB of RAM, the same card size as the owner's RTX 5070, so the
memory table in `Documentation-support/ollama-model-options.md` (section 2) applies. Ollama keeps one model in memory
at a time, so they never add up. These are estimates until the self-test prints the real GPU share:

| Model | Window | Graphics card (about 11 GB usable) | RAM while loaded |
|---|---|---|---|
| `qwen3:8b` | 16K / 32K / 64K | fits (8.6 GB) / borderline (11 GB) / no, about 5 GB spills | about 1 GB / 1-2 GB / about 6 GB |
| `qwen3.5:9b` | 32K / 64K | fits (8.7-9.7 GB) / fits, tight (9.7-10.7 GB) | about 1 GB |
| `gemma4:12b` | 32K / 64K | fits (9.6-9.9 GB) / tight (10.1-10.4 GB), if Ollama keeps its sliding-window layers short | about 1 GB |
| `gpt-oss:20b`, `gpt-oss-20b-64k` | 32K / 64K | **does not fit** (15 / 16 GB) | 4-5 GB spills to RAM: works, slower |
| WaifuGemma4 26B-A4B (IQ4_XS) | 8K | **does not fit** (13.9 GB + a small 8K context) | 3-4 GB spills to RAM: works, only 3.8B of it active per word |
| `qwen3.6:35b-a3b` | 64K | **does not fit** (25-26 GB) | about 14 GB in RAM: works while games are closed |

So: qwen3.5:9b, gemma4:12b and qwen3:8b (up to 32K) run entirely on the card. gpt-oss:20b, WaifuGemma4 and qwen3.6:35b-a3b run
split between the card and the 32 GB of RAM, which has room for any one of them, but they are slower. The self-test skips a
big model when less RAM is free than it needs. The licences are in [MODEL-LICENCES.md](MODEL-LICENCES.md): all
Apache 2.0.

## If something goes wrong

| What you see | What to do |
|---|---|
| "Windows calls this network Public" | Let the script set it to Private, or: Settings, Network & internet, the connection, Network profile type, Private. |
| "the firewall rule was not added" | The administrator prompt was declined or failed; run the script again and click Yes. |
| "Ollama listens on 127.0.0.1" | Quit Ollama from the tray icon, sign out of Windows and back in, then run with `-CheckOnly`. In Ollama's own settings, "Expose Ollama to the network" also works. |
| A model "skipped: only N GB of RAM free" | Close other programs (browsers, games), then run again with `-SkipPull` to test without downloading. |
| Miniverse can't connect, but `-CheckOnly` is all green | Another security program (antivirus with its own firewall) may block port 11434. Allow it there for the owner's address only. |
