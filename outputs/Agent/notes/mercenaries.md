# Mercenary checks — 13 October 2026

## Broker workflow (verified in-game)
- Dax Venn: Tatooine 3552, -4782; oid 281474994095833 during these sessions. Talk within 5 m. Options 0 Hire, 1 Dismiss all, 2 Not today.
- Follow-up session hired Fabe Tetao (oid 281474994125308) and Nado (oid 281474994125352). Both followed from the broker via 3554,-4620 and 3800,-4620 to the dwarf nuna group, and back. Last observed beside broker at 4.8 m / 4.3 m.
- Dismiss all at 12:05:35 PDT returned gone events for both exact companion IDs and Contracts closed dialogue. Subsequent look within 15 m showed only Dax. PASS for dismissing two companions.
- Previous session's Faehu Emo and Sesxe Egi were absent after relog both at the outskirts and at the broker. Supports logout cleanup, but no direct despawn packet was observed during that earlier disconnect.

## Combat probe (attempted; assistance inconclusive)
- Kael: human Master Brawler / Master Teras Kasi, unarmed, no staff commands.
- On 13 October at 12:02:09 PDT, from approx 3836.66,-4491.80, attack target dwarf nuna oid 281474994124570. Tool returned sent attack and two @base_player:prose_grant_xp events. Target still appeared 4.3 m away in immediate look, then emitted gone at 12:02:19.
- Both companions remained near Kael in the immediate post-attack look (3834,-4490.3, 3.1 m away). No individual damage events, HAM or target posture available. XP messages plus disappearance are consistent with a very quick kill, but do NOT prove companion assistance or assign kill credit.
- No failed-command, incap or death messages observed. Issued peace; received @cbt_spam:peace_single. Both companions followed back to town.
- Nearby dwarf eopie are even weaker in upstream data (level 3, HAM 90–110 versus nuna level 5, HAM 135–165). Did not escalate to dangerous enemies without health visibility. Live target statistics not exposed or independently verified.

## Next
- Add or expose own/target HAM, posture, combat state, attacker IDs and damage events in the agent body; use the dev/test galaxy workflow and review rules.
- Then repeat the weak-creature assist test with an encounter long enough to distinguish companion damage. Do not mark A4 combat assistance passed or failed from this probe alone.
