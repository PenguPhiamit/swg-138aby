# Ossus NPCs: the local model's second content job (15 Oct 2026)

Five NPC templates for Ossus in 138–139 ABY: three of the native Ysanna, and two of the One Sith (also raid trash for
`Documentation-support/krayt-raid-design.md`). They were written by the owner's local model (`gpt-oss:20b`, through
`tools/agents/local/local_agent.py`) from Claude's brief (`BRIEF.md`), and reviewed by Claude. Staged only.

**Run:** 16 model turns, 343 s, 9,884 output tokens.

**Claude's review:**
- Diffed against each stock base: only the fields the brief allows changed, and each matches the table.
  - Ysanna: social group `ysanna`, faction cleared, the `KILLER` flag dropped. They're neutral natives: attackable,
    not aggressive.
  - One Sith: social group `one_sith`, faction cleared, flags as the bases.
- `luac5.3 -p` passes on all five.
- The model wrote 4-space indents where the stock files use tabs. That was converted back mechanically; no content
  changed.
- The top comments repeat the brief's facts almost word for word. Fine for comments.
- Lesson for future briefs: say "keep the base file's tabs".

| file | var | base | social group | level | note |
|---|---|---|---|---|---|
| `mobile/ysanna_hunter.lua` | ossus_ysanna_hunter | janta_hunter | ysanna | 50 | Dantari bodies: placeholder, the Ysanna are human |
| `mobile/ysanna_warrior.lua` | ossus_ysanna_warrior | janta_warrior | ysanna | 70 | as above |
| `mobile/ysanna_shaman.lua` | ossus_ysanna_shaman | janta_shaman | ysanna | 60 | healer |
| `mobile/one_sith_acolyte.lua` | ossus_one_sith_acolyte | dark_adept | one_sith | 140 | raid trash level |
| `mobile/one_sith_warrior.lua` | ossus_one_sith_warrior | dark_jedi_knight | one_sith | 265 | raid trash or elite level |

**Not done yet:**
1. Bodies: human models in tribal dress and ritual masks for the Ysanna, and red-and-black tattooed Sith. The bases'
   bodies stand in for now.
2. Loot: the Janta and dark-Jedi loot groups stand in. The Ysanna want their own, without lightsaber parts; the One
   Sith get the raid tables.
3. Names in the client (`npc_names.tsv`, the same step as the creatures in `Local-model-ossus-fauna/`).
4. Server wiring and spawns: Ysanna camps in Ossus's wilderness; One Sith only in the raid and at a few hidden sites.
5. Levels: the One Sith are 140 and 265, raid-tier. Open-world Ossus ones would need lower variants.
6. Examine texts: `detail.tsv` (15 Oct). The local model drafted them; Claude rewrote all five in neutral, in-era wording. They wait on the same step as the bodies: their own shared templates. The creatures' README, item 6, explains why.
