# Instructions for the roadmap and board digest (for a Haiku agent)

Regenerate when `python -I tools/agents/roadmap_digest.py check` says STALE. First run `python -I tools/agents/roadmap_digest.py snap` (remembers what the agent will read). Then run one Haiku agent (model haiku, background) with this file as its
instruction; afterwards run `python -I tools/agents/roadmap_digest.py stamp`, which writes the real sizes and hashes into the `Stamp:` line.

You are making a short lookup digest of two long project documents for a private Star Wars Galaxies emulator project, so that another AI agent
can find things without reading about 100 KB each time. Read, with the Read tool only (pages of 400 lines; if a page is refused as too large,
read it in smaller pieces), both files completely:

1. `C:\Users\Pengw\Documents\Codex\2026-10-13\h\outputs\SWG-roadmap.md`
2. `C:\Users\Pengw\Documents\Codex\2026-10-13\h\outputs\SWG-handoff.md` (the task board: Server lock, Questions for the owner, Task board,
   Task instructions, Log)

Use no other tool for reading, open no other file, touch nothing under /opt/swg. Write exactly ONE file with the Write tool:
`C:\Users\Pengw\Documents\Codex\2026-10-13\h\outputs\Agent\notes\roadmap-digest.md` (plain Markdown, at most 12 KB).

Structure, in this order:

0. First line `# Roadmap and board digest`, then a line `Stamp: (filled in by tools/agents/roadmap_digest.py stamp)`, then: "Derived, not authoritative:
   find the cited row or heading in the source before acting on a claim. Regenerate with Agent/notes/roadmap-digest-prompt.md when
   `roadmap_digest.py check` says STALE." Then a key: who = CL Claude, GP ChatGPT, OW owner.
1. **Now** (at most 12 lines): who holds the server lock and what for, what is paused, which build the test galaxy runs, what the owner is doing
   right now, the newest Log entry in one line.
2. **Route for the first month** (roadmap, at most 15 lines): the tracks, their order, what is parked, what still waits for the owner's OK.
3. **Phases** table: phase | status | goal in one line.
4. **Task lookup**: one row per task id or named task row on the board (C1 to C42, F numbers, and the unnumbered rows), grouped open / blocked or
   on hold / done: id or name | who | status in at most 12 words | main file or report path. Note at the top which ids the board does not list
   (they may exist only in `Agent/gpt-queue.json`).
5. **Open owner questions**: id or number | one-line subject | answered or open (and where the answer is).
6. **Rules to remember**: the house rules and safety rules (server lock, commits, no pushes, no downloads without the owner's OK, test-galaxy-only
   changes, live deploys need cross-review and the owner's OK), at most 15 bullets.

Rules for the content:

- **Cite by anchor, not by line number**: every entry names its source as (roadmap, "<heading>") or (board, "<section>, <row id or first words>"), so a
  reader can grep for it after the files change. A line number may follow as a hint (`~L123`). Never invent a fact, number or path; if unsure,
  write "?" and keep the anchor.
- **No real person's name, username, handle, alias or credit anywhere.** Say "the owner"; name projects and tools (TortoiseBots, MTG, Core3, Ossus,
  Hoth); if a task label contains an author's handle or a forum alias, replace it with a neutral description ("the world-boss source", "the forum
  archive"). The project's own bot characters are fine. A file path may stay if you shorten the part that holds such a word with "...".
- Terse fragments, not prose; do not copy long passages.

Final message: counts only (lines read per file, task rows, open questions listed, size of the digest in bytes).
