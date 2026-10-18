# The local model: what it does, and how Claude and ChatGPT use it

Claude, 17 Oct 2026 (owner: "install our local model on our friend's PC and set up the workflow so both Claude and
ChatGPT can use it"). The local model drafts and does first passes. It does not check things: every result is a draft
until Claude or ChatGPT has checked it against the source.

## Where it runs

| Server | Models | Used when |
|---|---|---|
| The friend's PC (RTX 4070 Super 12 GB, 32 GB RAM), on the home network | `qwen3.6:35b-a3b` (research), `saluki` (claim checks; Underdog Saluki 27B at IQ2, 7.9 GB, 43 tokens/s, since 18 Oct), `qwen3.5:9b` (fast jobs), `gemma4:12b` (bot chat), `qwen3:8b` and `gpt-oss:20b` (older, for comparisons), `qwen-heretic` (Qwen3.8 27B Q4, 17 GB: more than the card holds, so slow; not used). qwen3.5, qwen3.6 and gemma4 also read images. WaifuGemma4 (the npc-dialogue model) is no longer there (checked 18 Oct 1:35 AM). | whenever it answers |
| This PC (RTX 5070 12 GB) | `saluki` at 16K with its vision projector (since 18 Oct 2:10 AM: 50 tokens/s, all on the card), also `qwen3:8b`, WaifuGemma4 (npc-dialogue), `gpt-oss:20b` | fallback, when the friend's PC is off, asleep or Ollama is quit; and chunk jobs Claude runs here by hand (status `here`) while the friend's PC does research |

- **The list is one file:** `outputs/tools/agents/local/ollama-url.txt` (gitignored, because it holds a home-network
  address). It has one server per line, in order, each with its model and context size. Copy
  `ollama-url.example.txt` to start one. Every script uses the first server that answers within 10 seconds.
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
- **Status `here`** (18 Oct): a topic run by hand on Miniverse while the friend's PC works through the queue. The
  runner starts only `open` topics, so it leaves it alone. The by-hand run uses the runner's own steps
  (`idle_research.run()` with this PC's server), which set `review` and write the LOG.md line.
- **It pauses itself when the friend's queue finishes** (owner, 17 Oct: "when the que finishes on their PC please have
  it pause"). When a timer run finds nothing open that the friend's PC can run, it writes STOP with the time and the
  topics still waiting (for example a model that isn't pulled), and adds a line to `LOG.md`. Nothing more runs, on
  either PC, until someone deletes STOP. New topics added while it is paused just wait.
- **One after another on the friend's PC:** while it is the server, the next topic starts 2 minutes after one
  finishes (owner, 17 Oct: 5 minutes in the morning, then "shorten timer to 2 mins between"). Each timer run stays within its 4 hours, and chaining stops
  after 3 failures in a row. This PC runs one topic per timer run. A rerun keeps the previous report as
  `report.previous.md`.

## Which jobs go to it

| Job | How | Model on the friend's PC |
|---|---|---|
| **Research topic:** explain a Core3 mechanic from the source, for a bot test | queue topic (no `kind`) | default `qwen3.6:35b-a3b`, up to 120,000 characters of source |
| **Chunk job:** `proofread`, `bot-gaps`, `report-digest` (local_jobs.py; digests the newest bot-run findings) | queue topic with `"kind": "map", "job": "..."` | add `"model": "qwen3.5:9b"`. Each chunk is small, and the big model would reload every 5 chunks. |
| **Bot chat drafts** (social play): job `bot-chat`, about 40 situations, three lines each | queue topic with `"kind": "map", "job": "bot-chat"` | `"model": "gemma4:12b"` |
| **Role-play and NPC dialogue drafts** (owner's OK, 17 Oct): job `npc-dialogue`, briefs from DIR/briefs.txt or the Ossus roster | a chunk job (`local_map.py` sends `think: false`, which this model needs) | `"model": "hf.co/hiwaifu-research/WaifuGemma4-26b-a4b-v1-i1-GGUF:IQ4_XS", "ctx": 8192`. Its card says 18+ only with no extra safety tuning, so the job's instruction sets the content rules. A drafter only: every line is reviewed before it goes into the game ([MODEL-LICENCES.md](../tools/agents/local/friend-pc/MODEL-LICENCES.md)). |
| **Era check:** job `era-check`, the proofread lines checked against 138-139 ABY | queue topic with `"kind": "map", "job": "era-check"` | `"model": "qwen3.6:35b-a3b"` (lore knowledge) |
| **Pre-check of the research reports** (17 Oct): every cited claim against its cited lines, and each rerun against the previous report | queue topics with `"kind": "map", "job": "claim-check"` or `"job": "report-diff"` (precheck.py) | `"model": "saluki"` since 18 Oct (it was `qwen3.5:9b`; on the 130 claims qwen disputed, Saluki was right on 62 of the 70 it changed, `Agent/local-research/claim-recheck/report.md`). Citations that don't resolve are listed without the model. Each claim is the sentence around its citation, not the row's first 400 characters (fixed 18 Oct). The reviewer starts with the "contradicted" and "not shown" claims, and still checks the rest: Saluki errs both ways and trusts stale source comments. |
| **Test-plan index** (17 Oct): section 3 of every report as setup / do / expect steps | `"job": "test-index"` | `"model": "qwen3.5:9b"`; queue it after the research topics it should include |
| **Scenario first pass** (17 Oct; ChatGPT's review work while it is out until 22 Oct) | `"job": "scenario-review"` | `"model": "qwen3.6:35b-a3b"`. Commands the server doesn't know are found without the model; the rest are leads for Claude, or for ChatGPT when it is back, since the scenarios are ChatGPT's |
| **Log triage** (18 Oct): the ERROR and WARNING lines of `core3.log` since the server's last start, one line per pattern (numbers, addresses and object names masked) with its count and first time seen; the model sorts each into known, new or crash risk | `"job": "log-triage"`; add `"log": "live"` (or a path) for the live galaxy, the test galaxy is the default. By hand: `local_jobs.py prepare log-triage DIR [test\|live\|PATH]` | `"model": "saluki"`. Patterns listed in `tools/agents/local/log-known.txt` (a part of a pattern, a tab, then why; no such file yet) are reported as known without the model. The report is one table, crash risks first. The test galaxy's run of 17 Oct 9:46 PM gave 208 patterns. |
| **Board trim** (18 Oct): each `### date time` log entry on `SWG-handoff.md` older than two days, as one proposed line | `"job": "board-trim"` | `"model": "saluki"`. The job edits nothing. The report names any commit hash, run number or owner quote a line dropped; Claude checks the lines, then moves the entries to `SWG-handoff-archive.md` |
| **Scenario drafts** (18 Oct): one bot scenario per area still open in test plan section 3 (trainers, vehicles, buffs, surveys, groups/mail/guilds, bazaar/vendors/trade, housing/harvesters/cities/factions) | `"job": "scenario-draft"`; queue it after the research topics it draws on | `"model": "qwen3.6:35b-a3b"`. The input is section 3 of the area's research reports and the plan's gaps and pass lines. The instruction carries `squad.py`'s Bot API and `aurek-hunt.py` as the example. Drafts go to `<topic>/drafts/<area>.py`, never `tools/bots/scenarios/`. The report checks syntax, unknown slash commands and calls outside the Bot API without the model. An answer is capped at 1,536 tokens (`local_map.py`), so each draft is at most about 80 lines |
| **A quick one-off**: summarise a log, list files that mention X | run `local_map.py` or `local_agent.py` by hand (below) | any |

Not for the friend's PC: decisions, reviews and sign-offs, anything that must be right the first time, credentials or
account data, and **text with real people's names**. A topic that must read such text is marked `"local_only": true`.
It then waits for this PC's model and never goes over the network (AGENTS.md, Privacy; the friend agreed to source,
bot notes and game text only).

### What else they can do (Claude, 18 Oct 2:00 AM; owner: "figure out what else our local models can do")

Claude's weekly limit is 73% used, with 4.8 days to the reset, and GPT is out until 22 Oct. So the best local jobs are the
ones that save Claude's own reading. Ranked by that:

**Queued 18 Oct (no new code):**
1. **Saluki claim pass over every report** (`report-precheck-saluki`). The research reports in `review` then reach
   Claude with the doubtful claims listed first. It takes about 20 minutes.
2. **The two open mission bugs as research topics:**
   - `bounty-offers`: why a bounty terminal lists no NPC bounty;
   - `easy-destroy`: how a group gets an easy lair for the group-pay check.
   - `bounty-offers-saluki` asks Saluki the same bounty question, so its first research report can be compared with
     qwen3.6's.

**Each needs one small job written in `local_jobs.py`** (Claude, or ChatGPT after 22 Oct). Jobs 3 to 5 were
written 18 Oct as `log-triage`, `scenario-draft` and `board-trim` (in the job table above; not queued yet):

3. **Log triage after every restart and overnight run.**
   - The new error and warning lines in `core3.log` are deduplicated by pattern, with counts, and the model sorts each into known and harmless, new, or crash risk.
   - This replaces Claude reading the log ("log clean at start").
   - Model: `saluki` or `qwen3.5:9b`.
4. **First drafts of bot scenarios from the research reports.**
   - Section 3 of each report already lists setup, do and expect steps.
   - With `tools/bots/squad.py`'s Bot API and one finished scenario as the example, `qwen3.6:35b-a3b` drafts a scenario for each untested area in test plan section 3: trainers, vehicles, buffs, surveys, groups/mail/guilds, bazaar/vendors/trade, housing/harvesters/cities/factions.
   - Claude reviews and runs them. Writing scenarios is most of the test work left, so this saves the most.
5. **Board trim.**
   - Each log entry on `SWG-handoff.md` older than two days becomes one line, and the full entry moves to `SWG-handoff-archive.md`.
   - Every session reads the board, so this cuts every session's cost.
   - Model: `saluki`. Claude checks the lines before the move.
6. **Item names and examine texts for new content** (Hoth rewards, Ossus loot, Nal Hutta).
   - The model drafts them; then the era check runs and the owner picks.
   - Model: `qwen3.6:35b-a3b`.

**Needs a download on the friend's PC (the owner does it there):**

7. **A search index for the project.**
   - A small embedding model (for example `nomic-embed-text` or `embeddinggemma`, under 1 GB) indexes the reports, `Documentation-support/` and the Core3 source.
   - A "where is X handled" question then gets file:line answers from the friend's PC instead of a Claude reader agent.
   - It also needs a short indexing script on this PC.

**Image jobs (the models are already there: `qwen3.5:9b`, `gemma4:12b`, `qwen3.6:35b-a3b`):**

8. **Art pre-sort.**
   - From a ComfyUI batch, keep the images that match the brief: the right object, a plain background for TRELLIS input, and no text or watermark. The owner then looks at a few instead of all of them.
   - Tested 18 Oct on `Local-art/trellis2-test/crate_compare.png`:
     - all three described the crate well, in 12 s (qwen3.5), 23 s (gemma4) and 31 s (qwen3.6);
     - none saw that the right-hand mesh has crumpled handles and a wavy rim.
   - So they sort images but don't check meshes. Any new vision model the owner finds should be tried on that image first.
   - **Update, 18 Oct 2:10 AM: Saluki with its vision projector (this PC) passed.**
     - In 11 s it reported "mesh tearing and pinching on the handles (especially in the right panel)" and said no to the prop.
     - It is the only one of the four models that did. Use it for art checks here.
     - Microverse can get the same check by adding the projector there (`mmproj-Underdog-Saluki-27B-1.0-Q8_0.gguf`, 0.63 GB, and a Modelfile like `tools/agents/local/models/saluki.Modelfile`).
9. **Reading bot screenshots** (a stuck character, an error window).
   - Screenshots of the owner's client stay on this PC, so this needs a vision model here: `qwen3.5:9b`, 6.6 GB, a download, so it needs the owner's OK.

**Later:**

10. **The local-model bot driver** (proposal card `task_aed46fe5`): bots that chat and choose with a local model.
11. **A first pass over dev commits with `saluki`** while GPT is out.
    - It lists likely bugs: null checks, locks, comparison signs.
    - It does not replace the cross-review that live needs.

Still not for local models:
- decisions and sign-offs;
- real names over the network;
- checking meshes for defects.

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
