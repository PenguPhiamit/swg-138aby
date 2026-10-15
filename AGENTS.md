# Shared rules for AI agents on this SWG server

Two agents work on this project for one owner: **ChatGPT** (Codex desktop app, project folder `h`) and **Claude** (Claude Code desktop app, folder `h/outputs`). The owner decides priorities; agents propose and carry them out.

## Start and end of every session

1. Read `outputs/SWG-handoff.md` (task board, server lock, questions for the owner, recent log) and `outputs/SWG-roadmap.md`, and your inbox: `outputs/Agent/to-chatgpt.md` (ChatGPT) or `outputs/Agent/to-claude.md` (Claude).
2. **Claim** a task on the board before starting it. Don't work on a task the other agent has claimed.
3. When you stop, add a dated log entry to `SWG-handoff.md`: what changed, commit hashes, what's untested, what's next. Tick the roadmap boxes you finished.

## Work split (owner, 13 Oct)

The owner splits the load so the agents don't edit the same files:

- **Claude: engineering inside `/opt/swg`.** Agent body C++ (`Core3-dev/.../src/client/agent/`), bot-only server helpers (for example `/agentpath`), the test galaxy, and live promotions or deploys after cross-review and the owner's OK. Claude normally holds the server lock for this.
- **ChatGPT (Codex + Universal Modder): everything outside `/opt/swg`.**
  - cross-reviews Claude's commits;
  - writes tools in `outputs/tools/` (for example the Phase 1 runner);
  - plays Kael through MCP for checks once a body is promoted;
  - runs real-client checks with Universal Modder's `um win`;
  - does research and file-format work (Universal Modder `game-research-websearch` and `reverse-engineering`), and later the asset pipeline.
- **ChatGPT's defaults (owner, 13 Oct):**
  - **Model and effort.** GPT-6.1 Sol. **High** for code reviews (C4-style), **Medium** for research, scenarios, tools and documentation, **Low** for downloads, record-keeping and answering messages. Each task row on the board names its level; use that. Don't use Astra, Max or Ultra unless the owner asks for it in that session.
  - **Research budget.** Each research task gets about **30 minutes or 20% of the remaining usage**, whichever comes first. Then write up what you have, with open questions listed, instead of starting another pass. A further pass needs the owner to ask for it.
  - **Closed research.** The KOTOR mod-author census ends at the 56 releases in `Documentation-support/KOTOR-mod-reuse-audit*.md`. Reopen it only to check one specific asset that has been chosen for import.
- **Bot work update (owner, 14 Oct):** ChatGPT owns Python bot scenarios, scheduling, diagnostics and reports, including while Claude is unavailable. ChatGPT may prepare isolated C++ bot-body edits when Claude is not editing that slice; record the claim and transfer the server lock before touching `/opt/swg`. Claude reviews before merge/deployment; live changes still require owner approval. This does not bypass app filesystem/WSL permissions.
- **Swapping a slice.** ChatGPT may take a self-contained C++ slice only after the owner transfers the server lock on the board. Claude reviews it before it is merged or promoted, and the reverse applies too.
- **One driver for Kael.** Only one agent drives Kael (or any bot account) at a time; claim it on the board. The test galaxy belongs to whoever holds the lock.
- **Universal Modder rules** (installed for both agents):
  - `um win` only after the owner has logged in and said they're at the PC. Agents never type the owner's password.
  - fal (paid, pay-as-you-go) only with the owner's OK for each batch; no key is configured yet.
  - Pull requests to its public knowledge base are outbound posts and need the owner's OK.
  - Its advice to use leaked SDKs or builds is overridden by the Ethics check below.

## Asking questions and passing messages (owner, 13 Oct)

Ask when you're blocked or unsure; don't guess, and don't stop silently.

- **Questions for the owner.**
  - In an interactive session, ask in your own chat window. The owner keeps both agent windows open side by side.
  - In an unattended run (the relay, overnight), add the question under **"Questions for the owner"** at the top of `outputs/SWG-handoff.md`, with your name, the time and the options you see. Then carry on with the parts that don't depend on the answer.
  - Anything under "Owner consent" in the Ethics check (downloads, installs, accounts, live changes, outbound messages, paid calls) always needs the owner's own answer. The other agent can't give it.
- **Questions and requests for the other agent.**
  - **ChatGPT → Claude:** append to `outputs/Agent/to-claude.md`, newest at the bottom, under a heading `### <YYYY-MM-DD HH:MM> ChatGPT`. While Claude is working, it watches that file (`tools/agents/watch_gpt.sh`) and wakes within about 30 seconds. Otherwise it reads the file at the start of its next session. Use it for "please run this test", "I need a file from `/opt/swg`", "I have no network", a review question, or a decision you want checked.
  - **Claude → ChatGPT:** `outputs/Agent/to-chatgpt.md`, same format. Read it at the start of every session, and again when you finish a task.
  - Answer in the other file, and say which message you're answering.
  - Keep messages short and concrete: what you need, why, and what you'll do meanwhile.
- **When you're blocked by your sandbox** (no WSL, no network, a denied approval), say so in `to-claude.md`. Claude has WSL and network access and can do that step, within the same rules and the owner's OK where it's needed.
- **Live status without WSL (owner, 14 Oct):** `outputs/Agent/live/status.md` (and `status.json`) is rewritten every 5 minutes by a WSL timer (`swg-live-status.timer`, running `outputs/tools/live_status.py` as root). It holds processes and memory, one status line per bot when no squad run is active (a run's activity records otherwise; it never sends a bot a command during a run), and the test galaxy's console tail without secrets. Read it before asking Claude for a runtime check.

## Server lock (most important)

Only the agent named in **Server lock** in `SWG-handoff.md` may stop, start, rebuild, back up, or edit files under `/opt/swg` (Core3, TREs, service, database). Take the lock by editing that line; set it back to `free` when done. If it's held, work only on research, docs, or files outside `/opt/swg`.

## WSL users

Debian's default user is **`swgemu`** (changed 13 Oct so VS Code edits files as the server's owner; the original setting is in `/etc/wsl.conf.before-vscode-20261013`). Always pass the user explicitly: `wsl -d Debian -u root -- …` for services, packages and backups; `-u swgemu` for git and editing server files. Never run git in `/opt/swg/Core3` as root: root-owned files in `.git` break the swgemu user's git.

## Source control

- Server code is in `/opt/swg/Core3` (WSL Debian), branch `sandbox`. Run git as the `swgemu` user: `runuser -u swgemu -- git -C /opt/swg/Core3 ...`
- One commit per logical change. End the message with a trailer naming the agent: `Agent: ChatGPT` or `Agent: Claude`.
- Git stays private: never push, never add remotes, never change the disabled push URL.
- `bin/conf/config-local.lua` and the world databases are deliberately not in git.
- **The project folder `h/` has local history too (owner, 14 Oct).** It's a Windows git repo: AGENTS.md, the outputs docs, board, tools and reports. There's no remote, and the same no-push rule applies.
  - Commit your own finished changes with Windows git (Git Bash), as the repo's local identity, ending the message with `Agent: Claude` or `Agent: ChatGPT`. Commit only your own files, never the other agent's work in progress.
  - Before adding a new folder, check `git status --ignored`. The `.gitignore` keeps out secrets, game files, images, downloads and per-run churn; extend it rather than force-adding.
  - Line endings are stored as-is (`core.autocrlf=false`): keep each file's own endings.

## Experiments and builds

- Never configure a second build directory inside `/opt/swg/Core3`: its build copies `core3` into the live `bin/` and generates code into `src/autogen`.
- Experimental C++ work goes in the dev worktree `/opt/swg/Core3-dev` (branch `dev`, Debug build in `MMOCoreORB/build/dev`, built by `outputs/tools/dev_build.py`). Merge it into `sandbox` when it's finished.
- Live rebuilds: `outputs/tools/rebuild_server.py` (galaxy stopped). Upstream updates: `outputs/tools/upstream_sync.py` (check), then `apply`.
- After risky restore or backup changes, prove them with `outputs/tools/restore_rehearsal.py`.
- Test galaxy (lock holder only): `outputs/tools/test_galaxy.py start [--dev-server] [--config 'AgentAccounts={"agent01"}']`. It is a disposable copy of the newest backup on ports 46xxx with the dev scripts. `--dev-server` runs the dev C++ build, and `--config` adds config-local lines.

## Routine

- Before any server change: run `Back Up SWG Galaxy.cmd` (`outputs/tools/backup_server.py`). It stops a running galaxy, so check the owner isn't playing.
- After Lua edits: `python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/check_lua.py`
- After a restart: `python3 .../outputs/tools/server_status.py`
- Nothing counts as working until it has been tested in-game; label it "untested" until then.

## Agent player (playing Kael through MCP)

- When the owner asks you to **play**, use the `swg-agent` MCP tools and follow `outputs/Agent/AGENT-GUIDE.md` (rules, limits, session start/end routine). Your memory is `outputs/Agent/notes/`; reports go to `outputs/Agent/reports/`; the raw event log is `outputs/Agent/logs/`.
- Playing does **not** need the server lock: it uses the bot account, not `/opt/swg` files. The galaxy must be running (`Server Status.cmd`).
- Code: `outputs/tools/agent/` (agentd.py daemon, mcp_server.py) plus `core3client --agent-control` in the dev worktree (branch `dev`, `src/client/agent/`). Account details are in `/opt/swg/agent/agent-account.json` (private: never print them).

## Content decisions

- **Setting direction (owner, 14 Oct):** Legends NJO–Legacy, after the Yuuzhan Vong War and Abeloth, with Darth Krayt's Empire as the intended reference. Pre-CU describes the game mechanics, not the story date. **Server year (owner, 14 Oct): around 138–139 ABY**, just after Krayt's final death on Coruscant (138 ABY): the One Sith go underground under his successors (Darth Nihl), the Ossus academy is in ruins and the Jedi are in hiding. Krayt's Empire is 130–138 ABY. The owner's general timeline: https://starwars.fandom.com/wiki/Timeline_of_Legends_media (our era index: `outputs/Documentation-support/legends-timeline-njo-legacy.md`; Fandom blocks the fetch tools, so read it in the browser pane).
- **Optional server-added encounters (owner, 14 Oct):** retain them as options unless genuinely infeasible to reintroduce or re-engineer. Missing art, old APIs, absent snapshot geometry or difficulty are adaptation/replacement tasks, not automatic rejection. Preserve rights/excluded-source gates; original replacements can retain a desired encounter concept without using unavailable material. Deferred means optional/pending, not discarded. No automatic live enablement.
- **Owner's SWG x SW5E book (owner, 14 Oct):** a reference for new professions, mats and consumables only, as optional content. Don't correct the book, and don't implement the SW5E rules. Where the book and real pre-CU SWG differ, real SWG wins; check the client data (`tools/owner_content/swg_client_data.py`), not memory. Guide: `outputs/Content-catalogue/owner-SWG-SW5E/README.md` (F87–F89).
- **Species (owner, 14 Oct):** no hybrid species until all the regular species are in.

- **Excluded by the owner:** Sentinel's Republic; BorrieBoBaka/SWG_D20_RP_TC, including its Progor-Chat bot.
- **Lore source (owner, 13 Oct): Wookieepedia, Legends continuity preferred, for everything it covers** (planets, creatures, species, factions, characters, places, ships, items, events). Read and cite it; write our own in-game text, since its text is CC BY-SA and its images aren't ours. Details: `outputs/Agent/knowledge-sources.md`, item 13.
- Keep credits/licenses with imported content (`outputs/Community-content/CREDITS-and-sources.txt`, `outputs/Content-catalogue/`).
- Client art needs its own permission check, separate from server code.

## Ethics check (applies to both agents, every session)

Before downloading, importing, deploying, or acting in-game, check:

1. **Source and rights.** No leaked, stolen or "not for distribution" material: don't search for it, download it, or reference it. That includes the 2026 "Legends" leak and the SWG-Source repositories (widely understood to derive from leaked SOE server code). Honour licences and creator terms (AGPL notices, MTG credit, art permissions). If rights are unclear, stop and ask the owner.
   - **Assets from other games or mods** (KOTOR and similar; from ChatGPT's 13 Oct audit):
     - Only creator-original work whose terms explicitly allow use in other games or conversions qualifies, with the author's required credit.
     - Stock game files are excluded unless their rights holder allows it. So are retextures, upscales and edited meshes made from stock files. A mod author's permission covers only their own contribution, not the original game's art or other contributors' work.
     - Owning the game, LAN-only use or a willingness to pay doesn't change this.
     - For every asset that gets imported, record the release and version, the files and hashes, the original licence or readme text, all contributors, and the credit wording, next to the asset.
     - Contacting or paying an author needs the owner's OK first.
     - CC0 and the project's own original work need no clearance beyond keeping their source and licence.
2. **Owner consent.** No live deploys, restarts, purchases, account changes, outbound messages/posts, or new external services without the owner's explicit OK for that action. "Hold until confirmation" means hold.
   - **Standing OK: test galaxy restarts (owner, 14 Oct 04:35).** Agents may restart the **test galaxy** (ports 46xxx, `squad.py galaxy`) without asking, but only when none of the owner's clients is running: no `SwgClient*` or `SWGEmu*` process in `tasklist`, and `SWG-client/swgemu_login.cfg` not pointing at port 46453. If the client is running, wait or ask. Log every restart in the board log (overnight runs: `Bot-reports/OVERNIGHT.md`) with the time and the reason. Since 15 Oct a stop keeps the copy and the next start resumes it (characters, items, bots and spawns survive; owner: "do we need it wiped everytime in the first place?"); `start --fresh` restores the newest backup (then run `squad.py setup`) and `stop --wipe` deletes the copy. This never covers the live galaxy (`swg-local`), deploys or merges to the live branch.
   - **Never restart the test galaxy during a squad round** (14 Oct 05:32: a restart 20 s into an overnight round left 17 of 18 bots logged in to a server that no longer knew them). Check `pgrep -f "squad.py run"` first, and wait for the round to end or `squad.py halt` it. Then run `squad.py setup`.
   - **ChatGPT has WSL (owner, 14 Oct 05:58: full access).** The relay runs Codex with `-s danger-full-access`; the owner sets the interactive Codex session the same way. The same rules apply as for Claude:
     - Write the server lock on the board before touching `/opt/swg`.
     - Run WSL commands as `swgemu`; use root only where it's needed.
     - Git only as swgemu, never as root in `/opt/swg/Core3`.
     - Never the live galaxy.
     - **Claude leads (owner, 14 Oct):** Claude keeps the dev tree `/opt/swg/Core3-dev`, dev builds and test-galaxy restarts unless the board hands them over. ChatGPT asks in `Agent/to-claude.md`.
     - **ChatGPT's server-code worktree (owner, 14 Oct: "give GPT some more responsibility"):** `/opt/swg/Core3-gpt`, branch `gpt/work` (made from `dev`), is ChatGPT's. ChatGPT edits and commits there as swgemu, one topic per commit, each message ending `Agent: ChatGPT`, and rebases on `dev` itself. Claude never edits it; ChatGPT never edits `/opt/swg/Core3-dev`. Claude reviews each commit, cherry-picks it into `dev`, then builds and tests it. No cmake/make in the worktree (the test galaxy and the dev build share the RAM): ask for a build in `Agent/to-claude.md`.
     - ChatGPT drives bots only with the driver claim on the board, and only outside overnight rounds, or after taking its groups out of `Agent/squad-plan.txt`; it puts them back when done.
3. **Honest reporting.** Report what was actually verified versus assumed. Label things "untested" and say plainly when something failed. Never claim a test you didn't run.
4. **Fair play in-game.** As Kael: no harassing or exploiting other players' characters, no griefing, no chat spam, no using staff commands except as `Agent/AGENT-GUIDE.md` allows. Bugs you find are reported, not exploited.
5. **Privacy and secrets.** See below. Never paste credentials into chat, docs or commits.

**Cross-review:** before any live deploy, the *other* agent (or the owner) reviews the change against this list and the diff, and records "reviewed by X" in the handoff log. Anything that fails a check goes to the owner first.

## Privacy

Never copy passwords, account hashes, or database secrets (`SWG-login.txt`, `config-local.lua`, backups) into docs, commits, or chat.

**Redact people's names when publishing (owner, 14 Oct).** Anything that leaves this PC must not name real people: a Discord post, a GitHub push (even to a private repo), a shared page or doc.
- That covers names, forum handles, aliases and character names that identify a real person: the owner's family, players, staff of other servers, and anyone named in the Storyteller research.
- Replace them with roles ("a player", "a former admin") or leave the line out.
- The one exception is the credit line an asset's licence requires (for example a CC-BY author credit). Keep that exactly as the licence asks.
- The owner's own name and email don't go out either, unless the owner says so for that item.
- Local files on this PC may keep names. Before anything is published, scan it for names and ask the owner when unsure.
