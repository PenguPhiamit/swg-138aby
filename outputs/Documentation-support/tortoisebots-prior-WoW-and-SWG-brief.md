# TortoiseBots: recovered WoW work and SWG design brief

13 October 2026 · ChatGPT · read-only study using UM game-research-websearch. Read alongside [Claude's existing study](tortoisebots-study.md), rather than replacing it. No WoW/SWG code, database, client or service changed; no downloaded program executed.

## Exact source and release distinction

Owner link: [v2026-10-13 release](https://github.com/Sagiroth/TortoiseBots/releases/tag/v2026-10-13). Direct release/API retrieval failed in this session, so asset names/hashes and the current hosted release body were **not independently fetched**.

Our archived source `work/research/Sagiroth_TortoiseBots` has main/ref tag `v2026-10-13` at `bc914eb3b5f484ede0d5161a68711f995161627d`; VERSION says **2026-10-13-v6**. Local tag/reference evidence is recorded below, not a claim about immutable hosted release assets. The old WoW chat observed **v3 at 78fbf506**; do not conflate its build/install result with v6 or assume the date tag's assets stayed identical.

[Repository](https://github.com/Sagiroth/TortoiseBots) targets Tortoise WoW1.18.1 with native C++ companions; a separate TortoiseBotsManager addon provides player controls. That is a different architecture from our packet-driven Core3 client. Its documented goal is persistent world bots plus player-owned alts and temporary hired companions, with deliberate separation of their lifecycle/economy. Source claims and our observed tests are different evidence levels.

## Recovered prior work — facts useful to Claude

Retrieved the actual prior **Document Setup And Lag Diagnostics** chat and its paired Codex history (local app read_thread). These are historical observations reported in that session, **not fresh tests of today's WoW installation**.

| Evidence | What the earlier work established | Limit |
|---|---|---|
| Module update turn 01a13456-154e-7250-bef4-a00778d85622 | Downloaded module revision 78fbf506, identified as v3; a preceding screenshot showed 78 updated files including world/character migrations | Not today'sv6 pin |
| Backup turn 01a1345e-0aa2-77cf-840d-ba383205f3ed | Four-database backup reported exit 0, 241669816 bytes (~230MiB), before applying rebuild | Did not prove a restore drill |
| Build turn 01a13466-55ec-71d3-8fae-7ce1d5c59fac | Release build produced mangosd.exe; C4834 warning did not prevent build | Installation/startup still pending in last verified reply; cmake install was requested, not observed completed |
| Release-note turn 01a1344e-b5fd-7706-9fb0-429784bb8e52 | v2 notes described recruiter Kerra95032 stationary movement migration and level 60 gear sets across 7 tiers/28 specs | Tier-selection quests/pricing were planned then; do not label current status from old notes |
| Performance turn 01a133d7-e10e-7698-984a-85264fc6fcbb | Map 0/1 slowdowns roughly 60 s apart; up to ~1.2 s map updates, example 1024/1195 ms in cells | Correlation identified periodic work, not yet its cause |
| Follow-up turn 01a13424-6da8-715e-bb88-65287fb6701b | Doubling autosave to 120000 ms did not shift spike interval; short test after CleanupTerrain=0 stopped minute-spaced stalls | Limited before/after run; residual startup/query delays remained; no universal lag cure |
| Dashboard clarification 01a1344e | tortoise-observability-windows-amd64.exe was a dashboard, not the world server | Updating that executable alone cannot install bot AI changes |

Historical working settings preserved during the update: `CleanupTerrain=0`, `PlayerSave.Interval=120000`. These are **WoW settings**, not recommendations to add those keys to SWG. The useful method is to correlate timestamps with a subsystem, change one variable, preserve the failed hypothesis, and measure RAM alongside latency.

Earlier work was under `C:/Users/Pengw/OneDrive/Documents/Solotortise/TWoWServerBots`; source core folder was `Source/tortise-wow` (historical spelling). No files there were modified or secrets copied now. Source chat IDs: ChatGPT6acdb5e1-befc-83e8-b410-edd8246e254c; paired Codex01a133e9-8eb0-7690-aab8-a05a69ffb010 and earlier 01a1338e-8197-7494-9c8e-a776cc7bf017.

A prior exported **SoloWoWServerSetupHistory.pdf** was reported as 36 pages preserving 21 original pages, with developer summary, failed diagnostics and screenshots. It was at the old cloud scratch `output/pdf/SoloWoWServerSetupHistory.pdf`; not available as a verified local file in this workspace, so this brief recovers the salient facts rather than claiming the PDF was copied or re-read.

## Source-backed design lessons for SWG

| Priority | Tortoise source to inspect | Transfer to our own implementation | Verification needed |
|---|---|---|---|
| P0 | runtime/ObservabilityEmitter.cpp; tools/observability/README.md | Publish complete roster snapshots with process epoch + sequence; expire old state instead of mixing server generations | Drop/reorder a chunk, restart seq at 0, confirm no phantom bots |
| P0 | ai/playerbot/strategy/ActionFailureBackoff.h; tools/test_engine_failure_backoff.cpp | Bounded per-action/target/failure backoff, TTL and success reset; independent decision functions | Repeated impossible terminal/route stops retrying, new scene/target clears stale suppression |
| P1 | tools/observability/README.md, runtime/PlayerLagWindow.h | Distinguish idle, resting, productive stationary work and stalled travel; server scheduling latency is different from ping | Combat/XP/healing must not falsely count as stuck; compare measured command latency against any estimate |
| P1 | docs/concepts/strategy-engine.md; runtime/BotTurnScheduler.h | Player orders first; prioritize combat/recovery and overdue work; avoid path/world scans every tick | Worst-case wait bounded under load; no starving ambient bots; no synchronous model call in combat |
| P1 | tools/pool_kpi_report.py; tools/pool_kpi_baseline_2026-10-02.json | Frozen baseline for pass/fail/blocked, incidents per hour and route/command latency | Same build/population/route conditions; dead/disconnected bots stay visible in denominators |
| P1 | docs/guides/observability-dashboard.md; tools/observability/README.md | One read model for map/status/reports; bounded incident episodes and clear active/resolved states | Permission/secret filtering; owner approval before a new service; static local report first |
| P2 | docs/concepts/architecture-invariants.md; host/ | Keep a narrow transport adapter; separate rules from world mechanics; bot features optional | Do not copy WoW session hooks into Core3. Our test-only helpers remain account/config-gated |
| P2 | CHANGELOG.md (quest boards, no-route trips, repeat giver loops) | Try alternate reachable objectives, suppress unavailable targets and verify object interaction types | Our doctor/terminal/crafting sessions need actual protocol capabilities, not another movement retry |

Observability docs specify snapshot protocol v9 and a session epoch, bounded event types and table pruning. Their lag figures are estimates of server action waiting, not network RTT; a source claim about 2000 bots cannot predict our SWG capacity. The same docs distinguish productive stationary work from a travel target making no progress. Those details are more useful than copying a dashboard screenshot.

Strategy docs describe a budgeted pool turn scheduler and failure backoff. Our Python squads currently execute bounded scenarios rather than live world AI, so introduce the smallest testable policy first; do not turn this research into a second server architecture. Core3 server-owned companions and external test players are distinct populations with different authority.

## Limits and rights

`docs/concepts/known-limitations.md` explicitly excludes autonomous dungeon clearing and describes LLM chat as disabled. Therefore the framework is not evidence that our bots can autonomously finish every dungeon or that a model is required for combat. README vision/future roadmap items are not runtime test results.

`LICENCE.md`, `docs/PROVENANCE.md` and `docs/LICENSE_AUDIT.md` must be read together. Original work carries AGPL-3.0 plus an attribution term; donor grants differ and their compatibility audit is open. The owner's reported author permission does not settle other contributors' rights. This pass takes ideas and structure, copies no implementation, and keeps credit: **TortoiseBots by Sagiroth — https://github.com/Sagiroth/TortoiseBots**. Any future selected file port needs exact donor/header review and retained notices.

## Concrete next slice

Implement an original **offline incident/policy layer** outside /opt/swg before any web service: consume squad reports, emit bounded evidence-linked incidents, distinguish BLOCKED from server defects, and compare fixed scenario baselines. Separately, add pure route/mission retry decisions with scene-epoch and deadline checks. Claude reviews before integration; bots remain under one driver. That is useful to Hoth now and needs neither copied code nor a new paid service.
