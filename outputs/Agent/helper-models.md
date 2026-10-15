# Helper models for the main Claude chat

Set up by Claude (side session), 15 Oct 2026. The owner asked for "a model to help with the main chat's processes" and chose:
bulk reading, first-pass review, report digests and cheap pieces of work, **without a local model** (the PC can't spare the
RAM, see the 07:31 out-of-memory entry). So the helpers are cheaper Claude models that the main chat hands work to. The
main chat keeps the decisions, the server lock, live changes and every cross-review sign-off.

## The helpers

Defined in `outputs/.claude/agents/` (one file each; the `model:` line is the only thing to change to move one up or down).

| Helper | Model | Writes? | Hand it |
|---|---|---|---|
| `swg-reader` | Haiku | no | "Where/how does X work", "which files mention Y", "what does this scenario check" when that takes more than about five file reads. Returns a short answer plus `path:line` evidence. Reads Core3 in WSL (`-u swgemu`). |
| `swg-reviewer` | Sonnet | no | A commit, range or file list for a first pass: ranked findings with a failing case each, plus "looks fine" and "not checked". **Notes for the real review, never the sign-off** (AGENTS.md cross-review stays with ChatGPT or the owner). |
| `swg-digest` | Haiku | no | Gate, overnight and bot reports, test output, live status: at most 12 lines with the numbers quoted exactly and the first error line of each failure. |
| `swg-mechanic` | Sonnet | yes, outside `/opt/swg` only | A fully specified mechanical edit: renames, moves, table rows, the same small change across files. Stops and asks instead of guessing; commits only when told, with `git commit -o` and explicit paths. |

A fifth helper, `swg-listener` (Haiku), runs the owner's input listener for the main chat: start, stop, pause, "what did
I just do?" and notes. It only runs `tools/listener/listener.py` commands; the recorder itself is a plain script, not a model.
See `tools/listener/README.md` for exactly when it listens and what it keeps.

Call one with the Agent tool: `subagent_type: "swg-reader"`, and a prompt that names the question, the starting paths and the
answer size you want. For a piece big enough to deserve its own conversation, start a side session with a cheaper `model`
instead.

## When it pays, and when it doesn't

- It pays when the helper reads a lot and returns little: it saves the main chat's context and the Opus-priced reading. A
  helper call has a start-up cost, so for fewer than about five file reads just read them.
- Open the one or two cited lines a decision rests on. Haiku is good at finding and citing, and it can still misread; the
  reader and digest helpers are told to mark inferences and list what they did not check.
- Don't hand over: design choices, anything that needs the server lock or touches `/opt/swg`, live deploys, Kael or bot
  driving, the owner's questions, or the "reviewed by X" line on the board.
- All four are read-only except `swg-mechanic`, which is told never to write under `/opt/swg`, never to push, stash, reset
  or amend, and to keep each file's line endings.

## What was tested (15 Oct)

- Reader instructions on Haiku, run through a general-purpose agent that read `swg-reader.md` first: two questions (this
  folder's `ollama_url.py` settings; where `AgentAccounts` is read in `/opt/swg/Core3-dev/MMOCoreORB/src`). Every
  `path:line` it cited matched a grep of mine; the WSL read worked with `MSYS_NO_PATHCONV=1 wsl -d Debian -u swgemu -- ...`.
  It stayed read-only and kept to the report format.
- **Not tested:** the other three helpers; calling any of them by name. Claude Code reads agent files when a session
  starts, so the main chat needs a restart (or a new session) before `swg-*` appear as agent types. Sonnet's reviewer
  quality on a real diff is unknown until its first use; judge it on the first one or two.

## Changing them

Edit the file in `outputs/.claude/agents/` (front matter: `name`, `description`, `tools`, `model`). The `description` is what
makes the main chat pick a helper, so keep it specific. A new helper is a new file; don't put other `.md` files in that
folder (every file there is read as a helper).
