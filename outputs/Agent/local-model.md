# The local model: what it does, and how Claude and ChatGPT use it

Claude, 17 Oct 2026 (owner: "install our local model on our friend's PC and set up the workflow so both Claude and
ChatGPT can use it"). The local model drafts and does first passes. It does not check things: every result is a draft
until Claude or ChatGPT has checked it against the source.

## Where it runs

| Server | Models | Used when |
|---|---|---|
| The friend's PC (RTX 4070 Super 12 GB, 32 GB RAM), on the home network | `qwen3.6:35b-a3b` (research), `qwen3.5:9b` (fast jobs), `gemma4:12b` (bot chat), `qwen3:8b`, `gpt-oss:20b` and `gpt-oss-20b-64k` (the older defaults, for comparisons), WaifuGemma4 26B-A4B (role-play drafts) | whenever it answers |
| This PC | `qwen3:8b` at 16K | fallback, when the friend's PC is off, asleep or Ollama is quit |

- **The list is one file:** `outputs/tools/agents/local/ollama-url.txt` (gitignored, because it holds a home-network
  address). It has one server per line, in order, each with its model and context size. Copy
  `ollama-url.example.txt` to start one. Every script uses the first server that answers within 3 seconds.
- **What is in use now:** in WSL, run
  `python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/agents/local/ollama_url.py`, and
  `idle_research.py status` in the same folder.
- **Setup and undo on the friend's PC:** [tools/agents/local/friend-pc/README.md](../tools/agents/local/friend-pc/README.md).
  The design notes (idle detection for another PC, settings order) are in
  [REMOTE-OLLAMA.md](../tools/agents/local/REMOTE-OLLAMA.md).
- **Memory guard, kept:** on any server the model is unloaded every 5 requests and at the end of a job, because its
  prompt cache grows in that PC's RAM (it took this PC down on 15 Oct). On this PC the jobs also stop below 6 GB of
  commit headroom, start only above 8 GB, and wait while the owner's SWG client runs.
- **Owner pause:** creating `Agent/local-research/STOP` stops new topics on every server.

## Which jobs go to it

| Job | How | Model on the friend's PC |
|---|---|---|
| **Research topic:** explain a Core3 mechanic from the source, for a bot test | queue topic (no `kind`) | default `qwen3.6:35b-a3b`, up to 120,000 characters of source |
| **Chunk job:** `proofread`, `bot-gaps` (local_jobs.py) | queue topic with `"kind": "map", "job": "..."` | add `"model": "qwen3.5:9b"`. Each chunk is small, and the big model would reload every 5 chunks. |
| **Bot chat drafts** (social play, later) | a new local_jobs.py job, then a queue topic | `"model": "gemma4:12b"` |
| **Role-play and NPC dialogue drafts** (owner's OK, 17 Oct) | a chunk job (`local_map.py` sends `think: false`, which this model needs) | `"model": "hf.co/hiwaifu-research/WaifuGemma4-26b-a4b-v1-i1-GGUF:IQ4_XS", "ctx": 8192`. Its card says 18+ only with no extra safety tuning, so the job's instruction sets the content rules. A drafter only: every line is reviewed before it goes into the game ([MODEL-LICENCES.md](../tools/agents/local/friend-pc/MODEL-LICENCES.md)). |
| **A quick one-off**: summarise a log, list files that mention X | run `local_map.py` or `local_agent.py` by hand (below) | any |

Not for the friend's PC: decisions, reviews and sign-offs, anything that must be right the first time, credentials or
account data, and **text with real people's names**. A topic that must read such text is marked `"local_only": true`.
It then waits for this PC's model and never goes over the network (AGENTS.md, Privacy; the friend agreed to source,
bot notes and game text only).

### Queued by the owner: the names delta sweep (17 Oct)

The owner, 17 Oct: "save it for the local model we are setting up". It runs before the repository goes public, and
it is a drafting job, so Claude or ChatGPT reviews its list before any push.

- **Where:** this PC only (`local_only`), because its input is the text that may hold real names. If the owner wants
  it on the friend's PC instead, that needs their explicit OK for this job, because it sends those lines over the
  home network.
- **Scope:** the files in `h` changed since 2026-10-15 11:40 AM (324 when it was queued). Only the lines added since
  then are checked (`git log --since="2026-10-15 11:40" -p`, added lines only).
- **Rules:** `work/names-sweep/RULES.md`, plus the owner's decisions in `work/names-sweep/decisions-2026-10-17.json`.
  Keep credits for community creators, whole source links, family mentions without a name, and the owner's own
  characters listed there. Flag other real people's names, handles that are not credits, and e-mail addresses.
- **Output:** `work/names-sweep/delta-2026-10.json`, in the same shape as `new-names.json`. Everything stays under
  `work/` (gitignored, never exported). **No found name goes into a tracked file**: not the queue, LOG.md, the
  board, or this page.
- **How:** it needs a chunk job in `local_jobs.py` (`names-delta`: prepare the added lines, the instruction from
  RULES.md and the decisions, a report that writes the JSON under `work/`). That job is not written yet. Until it
  is, nothing is queued, so a topic can't put input copies under `Agent/local-research/`, which git tracks.
- **Review:** the agent that runs the push check (Claude or ChatGPT) goes through every flagged line before the push.

## How each agent queues work

Both agents use the same queue, `outputs/Agent/local-research/queue.json`. The WSL timer (`swg-idle-research.timer`,
every 5 minutes) starts the next open topic once the server in use has been idle for 10 minutes. It runs one topic at
a time, in queue order. A topic that can't run on the server in use (`local_only`, or a `model` it lacks) is skipped
and stays open.

Add a topic as one object in `topics`, with valid JSON. The runner re-reads the file before it writes, so a small edit
while a topic runs is safe.

```json
{
  "id": "short-kebab-id",
  "title": "What the report is about",
  "added_by": "ChatGPT, 17 Oct (why: which test or note needs it)",
  "review_by": "ChatGPT",
  "status": "open",
  "question": "The question, with what the test saw (for example the bot note).",
  "sources": ["src/server/zone/.../File.cpp:100-400", "h:outputs/tools/bots/scenarios/x.py"],
  "model": "qwen3.5:9b",
  "ctx": 32768,
  "local_only": false
}
```

`model`, `ctx` (context size in tokens), `local_only` and `review_by` are optional. Without `review_by`, the agent in `added_by` reviews it. Sources
are Core3-dev paths relative to `MMOCoreORB` (optional `:START-END`), or `h:` paths in the project.

- **ChatGPT** edits `queue.json` directly (it has WSL with full access since 14 Oct). If its sandbox can't reach WSL,
  it asks Claude in `Agent/to-claude.md`. To have Claude review a report, it sets `"review_by": "Claude"`, adds one
  line in `to-claude.md`, and does the same the other way in `Agent/to-chatgpt.md`.
- **Claude** does the same. From the overnight relay, Claude can also queue ChatGPT a review task in
  `Agent/gpt-queue.json` that names the report.
- **By hand, for a one-off** (in WSL, as swgemu): first check that `idle_research.py status` doesn't say "a topic is
  running". The friend's PC runs one request at a time and keeps one model loaded, so a second job just waits or swaps
  models. The scripts pick the same server as the timer.
  - `python3 local_map.py --input IN.jsonl --instruction FILE --out DIR [--model M]`: one short JSON answer per chunk.
  - `python3 local_agent.py --workspace DIR --task "..." [--model M]`: reads files in DIR and writes its answer there.

## How results come back

- A finished topic sets its status to `review`. The report is in `Agent/local-research/<id>/report.md`, the run's
  output in `agent-output.txt` (or `map-output.txt`), and there is one line in `Agent/local-research/LOG.md`. A topic
  whose server went away mid-run goes back to `open`. One that failed says `failed`.
- **The reviewer** (`review_by`, else the agent in `added_by`) checks each claim against the lines it cites, then
  sets `"status": "done"` and `"reviewed": "<agent>, <date>: <one line on what held up>"`. The reviewer acts on the
  report (a scenario fix, a test-plan note) or sets `failed` with the reason. A report that has not been reviewed
  counts as untested and is never quoted as fact.
- **At the start of every session**, each agent looks in `queue.json` for topics in `review` that are theirs, and
  lists the open ones it is waiting for. The board gets a line only when a report changes a decision.

## The friend's PC

**Measured 17 Oct, 5:03 AM** (one short question each, from Miniverse; set up by hand that night, the firewall rule narrowed to Miniverse): `qwen3.6:35b-a3b` at 64K loads in 40 s and writes about 11 tokens/s with 36% of its 22.8 GB on the graphics card; `qwen3.5:9b` 65 tokens/s and `gemma4:12b` 90 tokens/s, both wholly on the card. `qwen3:8b` at 32K ran the first five research topics in 1-2 minutes each, but read too little (it skipped StructureManager.cpp at the 60,000-character budget) and once wrote no report; they were queued again for `qwen3.6:35b-a3b`.

- The friend agreed (owner, 17 Oct) to Ollama, to our jobs using their graphics card while Ollama is idle on our side,
  and to the job text (server source, bot notes, our game text) crossing the home network. It goes as plain `http`
  between the two PCs only. A firewall rule there admits Miniverse alone, and port 11434 is never forwarded on
  the router.
- The friend quits Ollama before gaming. Our side can't see their games, only whether Ollama answers. A quit Ollama
  looks like "off", and the jobs move to this PC.
- If the friend's address changes, update `ollama-url.txt`. If the owner's changes, the friend re-runs the installer
  with the new `-OwnerPC`.
