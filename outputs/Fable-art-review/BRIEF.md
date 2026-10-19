# Fable art review 1: the Vong look and the launcher banner

Brief written by Claude, 18 Oct 2026, 5:03 PM, for a Fable run after the weekly usage reset (Thursday 22 Oct,
10:00 PM). The owner can edit this file before then; the run reads it as it stands.

**Owner, 18 Oct about 5 PM:** "bring Fable back for art direction and design passes only, starting after Thursday's
reset. Opus keeps the engineering. Start with a Fable review of the Vong look and the banner."

## Your role and limits

- You are the art director. You look, judge and write direction. Claude (Opus) does all the making: ComfyUI and
  TRELLIS runs, bakes, client archives, server patches, installs and in-game checks.
- Read `h/AGENTS.md` first and follow it. In particular: never write anything under `/opt/swg`; download or install
  nothing; no real people's names in anything you write; Legends sources (Wookieepedia Legends articles) for lore.
- Don't run ComfyUI, TRELLIS, Blender, Universal Modder (`um`), the test galaxy or any build. Start no sessions and no
  subagents.
- Image prompts follow the project's practice: describe the materials, shapes and light, with no franchise, character
  or artist names (see the prompt table in `Documentation-support/vong-look-test.md`).
- **Budget.** Fable shares the all-models weekly limit with everything else and costs more per token than Opus. One
  pass, about 45 minutes. Don't start a second pass; list what you'd look at next instead.
- Other sessions share this checkout. Write only `outputs/Fable-art-review/README.md`, and commit only that file with a
  pathspec (`git commit -m "..." -- outputs/Fable-art-review/README.md`), ending the message with `Agent: Fable`. Don't
  edit the board; the session that started you reports to Claude.

## 1. The Vong look (a Yuuzhan Vong warrior NPC at Ossus point of interest 7)

**Read:** `Documentation-support/vong-look-test.md` (the plan, the rounds and the prompts) and `Vong-look/INSTALL.md`
(what is staged, and fix 1: the warrior first showed up as "just a fat human" because of the body template).

**Look at** (the Read tool shows images):
- `Vong-look/gen/`: the generated swatches (`vonduun_N.png`, with `_seamless` and `_tiled2x2` versions) and
  `round3_raw_sheet.png`. `comfy_manifest.jsonl` records each image's model, seed and prompt.
- `Vong-look/bake_mix/preview_sheet.png` and `preview_0.png` to `preview_2.png`: the current look, baked onto stock
  armour pieces.
- `Vong-look/bake/`: the earlier all-chitin bake that the owner dropped.

**The owner's picks so far:** swatch 12; then "Mix: bone + s02 collar", with no helmet.

**Constraints:** it is our own texture on the stock armour shapes and UVs, saved as DXT5 and drawn by the client's
own shaders. New meshes are possible (Blender 3.6 and the NSG SWG tools are installed and proven), but that is a much
bigger job; say when an idea needs one.

**Questions to answer:**
- Does it read as a Vong warrior at the distance and in the light a player sees it in SWG?
- What is the single biggest improvement?
- Colour, material, silhouette (spurs, shoulders), the bare head (ritual scars and tattoos), and the amphistaff and the
  patrol variants planned as step 7 in `vong-look-test.md`.
- Lore fit: vonduun crab armour, ooglith and the warrior caste, from Legends sources. Wookieepedia (Fandom) blocks the
  fetch tools, so use the built-in browser pane if you have it; otherwise use the project's notes and say so.

## 2. The launcher banner

**Read:** the banner section of `tools/friend-installer/OWNER-README.md`, the prompt files in
`tools/friend-installer/launcher/` (`banner-prompts-round9.sh`, `banner-prompts-round10.sh`, `banner-prompt-ossus.txt`,
`make-banner-art.sh`, `make-banner-edit.sh`), `make-banner.py` (it adds the title), and in `Launcher.cs` the size the
banner is drawn at in the launcher window.

**Look at:** `tools/friend-installer/launcher/banner.png` (the current banner: the owner's pick B_s303, 1536x512, with
the title) and the candidates and contact sheets in `tools/friend-installer/launcher/banners/` (55 files, for example
`picks.jpg`, `picks-6.jpg`, `round20.jpg` to `round23-towers.jpg`).

**Questions to answer:**
- Does it work at the size the launcher shows it? Is the title easy to read?
- Composition, mood and era fit: the server is set at 138-139 ABY, just after Darth Krayt's death, with the Ossus
  academy in ruins and the Jedi in hiding.
- Keep it, tweak it with an inpaint pass, or redo it? For a redo, give two or three prompt directions in the project's
  style.

## What to write: `outputs/Fable-art-review/README.md`

Plain words, short: the owner reads it.

- For each of the two: a one-line verdict (keep, tweak or redo); what works; what doesn't.
- Up to five ranked changes each. For every change: what Claude must do to make it (prompt run, inpaint, bake, client
  archive, mesh work) and a size (S, M or L).
- Any new prompts as ready-to-run text; leave the seeds to Claude.
- What you couldn't judge (for example in-game light without a screenshot), and which screenshot would settle it.
  Claude can take one with `um win shot` when the owner is at the PC.
- The owner's questions at the end, numbered.

End your run with a summary of six lines or fewer: the two verdicts, the top change for each, and the number of owner
questions.
