# Review of ChatGPT's research, 13–14 October

Claude, 14 October 2026, at the owner's request ("take a look at all the research codex did"). Read-only review: no source, server or client changes came from it. (The Hoth crash fix the same night is separate; see `hoth-port-log.md`.)

## What was read

- **Content:** the active catalogue (and the historical one it replaces), EiF and Uprising, dormant client objects, the C11 download-record review, and the feature register.
- **History and inspiration:** official plans and cut content, the two KOTOR permission audits, the Storyteller and flamethrower files (README, authenticity register, historical reports, the Prophecy follow-up).
- **Hoth and planets:** C12 adaptation table, C14 planet lore and coordinates, the galaxy-map calibration.
- **Operations and bots:** C13 server SOPs, C10 mapping and coverage plan, macro routines, the TortoiseBots brief, the setting and encounter policy, the C8–C10 validation, and the daily reports (13 Oct, human-client follow, travel UI).

Not read line by line: the large JSON and CSV evidence files and the 690-row weapon index. Only their summaries and spot checks were read.

## Overall

The research is careful and honest about its limits. Every document separates what was observed, inferred, untested and blocked. Rights are handled well:
- permission is kept apart from availability and compatibility;
- one creator's grant is never stretched to other contributors;
- failed page fetches are recorded as access failures, not as findings.

Nothing claims a test that wasn't run. The weak points are presentation, a few stale lines, and one shared blind spot about what the real client loads (finding 1).

## Findings, most important first

1. **The client never loaded the MTG archives, and every "the client has it from MTG" conclusion inherited that.**
   - **Cause:** `work/install_community_content.py` (13 Oct) appended the 23 MTG lines to the end of `SWG-client/swgemu_live.cfg`, after its `[Station]` header. The client reads `searchTree` only inside `[SharedFile]`.
   - **Why nobody saw it:** Bellum's `cfg_priorities()` counts lines in any section, and our Hoth closure, the Storyteller inventory ("config priorities are reader-reported") and the catalogue all relied on it. This crashed the owner's client on Hoth tonight.
   - **Live risk:** the live server's character builder offers an "MTG Content Library" of **8,051 MTG objects** (`object/sandbox/mtg_catalog.lua`, included on live and dev), and the live server loads the MTG archives. The live client doesn't. Spawning one of those objects on live will probably crash the client or show nothing. Until the client config is fixed, don't use that menu on live.
   - **Fix:** one `[SharedFile]` line before the MTG block in `swgemu_live.cfg`, with the owner's OK. Test sessions are already fixed through `Play SWG Test Galaxy.cmd`.
   - **Check tool:** `tools/hoth/client_load_order.py` shows what the client really loads. Use it for any future client-file claim.
2. **SOPs (C13), two corrections:**
   - **§7 says the client's crash-log location is undocumented. It is now known:** `SWG-client/SWGEmu.exe-stage.<build>-<UTC time>.txt`, plus an `.mdmp` alongside. The `.txt` holds the FATAL line, the terrain, the player's position and the last templates loaded. That is how tonight's crash was read.
   - **§2.4 ("client uses higher searchTree number"):** add "only inside `[SharedFile]` and below `maxSearchPriority`; check with `client_load_order.py`".
3. **C12 (Hoth adaptation table) is usable for the creature slice, but:**
   - 172 of its 228 rows repeat one sentence (the loot and reward rows). The working content is in the critical deviations, about 50 `adapt` and merge rows, and the acceptance list, which is good.
   - Collapsing the loot rows into one group row would make the table readable. That's optional; the JSON keeps the per-file hashes.
4. **A Hoth caveat worth carrying into testing.** From the cut-content document: the Hoth author reported bitmap-region instability at high admin speeds (2017), plus Echo Base and mount caveats (2016).
   - So: test Hoth movement at normal speed, and keep bots at walking or running speed there.
   - Added to the watch list for the Hoth port.
5. **Stale lines:**
   - The macro document (00:43) says a squad time limit doesn't interrupt a running round, and that Codex's WSL check was denied. Both have been superseded: ChatGPT's `run_control` (00:52) halts at checkpoints, and `Agent/live/status.md` now gives Codex status every 5 minutes.
   - The C11 review asks for corrections in the download records. Most were made when D1 was added; the "partial completion" wording is still worth a check.
6. **Formatting:**
   - Several ChatGPT documents lose the space before numbers: "14October2026", "all76", "RMSE:67.85px", "October2026". This appears in C14, the calibration note, the setting policy, the Storyteller README and C12's owner note.
   - `C8-C10-validation.md` has mojibake ("C8â€“C10", "Â·"): UTF-8 read back as cp1252.
   - All easy fixes for ChatGPT.
7. **Privacy (Prophecy and handle follow-up):**
   - It searched the owner's brother's game handles at the owner's request, and stayed careful: no real-world identity was inferred, unrelated matches were discarded, and nothing was contacted.
   - Keep it that way. Look only for item and server evidence, and don't build profiles of named third parties (such as former server staff).
8. **Lore (C14):** the grid squares match the Essential Atlas values I know:
   - Hoth and Bespin K-18; Endor H-16; Tatooine R-16; Naboo and Rori O-17; Corellia and Talus M-11;
   - Dantooine L-4; Dathomir O-6; Yavin P-6; Kashyyyk P-9; Mustafar L-19; Dagobah M-19; Alderaan M-10;
   - Coruscant and Chandrila L-9; Korriban and Dromund Kaas R-5; Nal Hutta S-12; Mandalore O-7.

   I did not check Lok Q-17, Taanab O-8 or Jakku I-13. Jakku is canon-only, and the doc rightly flags it against the owner's Legends 130–138 ABY setting. The text is original, as the CC BY-SA rule needs.

## What is most useful, and when

| Now (Hoth and bots) | Later | Owner curiosity, open |
|---|---|---|
| C12 deviations and acceptance checks; C13 SOPs and their 10 gaps; C10 mapping plan and schema; the TortoiseBots brief (session epoch + sequence, failure backoff) | Catalogue permission codes (MTG planets, Borrie and Abi packs); EiF 2017 species source (37 options, art terms open); cut-content design leads (courier contracts, HoloNet terminal, dynamic POIs); KOTOR audits (56 releases, **none cleared** for import) | Storyteller weapons and the brother's flamethrower: unresolved; needs a server, character or item name, or a dated screenshot from the owner |

## Asks and follow-up (updated 14 Oct, after the owner's "do everything except the stuff related to my brother and the storyteller weapons")

- **Storyteller and the brother's weapon: out of scope for Claude** (owner). The owner and ChatGPT have made progress on it separately, so the "open" note in the table above is out of date.
- **Done by Claude:**
  - finding 2: SOP §2.4 and §7 updated;
  - finding 5: the stale macro lines are marked as superseded;
  - finding 6: the spacing fixes, as an exact replacement list, in AGENTS.md, C14, the calibration note, the setting policy, C12, the SOPs, the TortoiseBots brief and the C11 review; the mojibake in `C8-C10-validation.md`;
  - `hoth_closure.py` now uses the real load order (`client_load_order.py`, `--login FILE`). For a test session it gives the same 487 files as on 13 Oct (41 from MTG; the same 2 missing shader names), so C12's client claims hold for test sessions. With the live config as it is, Hoth's terrain and snapshot are missing.
- **Still open, finding 1 (live client):** adding the `[SharedFile]` line to `swgemu_live.cfg` was stopped by Claude Code's permission check as a production change. It needs the owner to approve that edit explicitly, or to make it by hand: put a line `[SharedFile]` just above `; MTG additional assets below the pre-CU archive priorities.` near the end of `SWG-client/swgemu_live.cfg`. Then `python -I outputs/tools/hoth/client_load_order.py` should list the 23 MTG archives as loaded. After that, `Play SWG Test Galaxy.cmd` should stop adding them a second time (Claude will remove those lines).
- **ChatGPT:** nothing to redo; please don't re-apply findings 2, 5 and 6.
