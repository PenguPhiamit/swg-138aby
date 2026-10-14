# Esk route scenario used Tatooine destinations on Hoth

Found by ChatGPT, 14 October 2026 05:03, in an already-running shared squad job `20261014-045724`; this session did not launch that job. First-round report: `Bot-reports/Esk/20261014-050244-esk-routes.json`, 0/5, 319 seconds. The cantina cell was rejected as belonging to another zone; Lira/Tovan became incapacitated while following destinations intended for Tatooine. All three had recovered from death at run start but remained on Hoth.

Cause: `tools/bots/scenarios/esk-routes.py` assumed Mos Eisley without checking the crew's planet. The new C16 fallback movement guard only covers fallback assignments, so it did not protect this pre-existing main scenario.

Fix: before gear or movement, require every member to be on Tatooine; otherwise emit BLOCKED and return. Offline regression loads the actual scenario with fake Hoth bots and verifies no walking, parallel movement or gear calls. Passed. **Fixed scenario has not been tested in-game.** No kit changes or server edits.

Containment: ChatGPT wrote the shared `Bot-reports/runs/STOP` at 05:03 and told Claude. At 05:04:31 the runner recorded RunStopped for Dorn/Esk, consumed STOP and removed ACTIVE. This confirms the cooperative run stopped; it does not log out bots or stop the galaxy. The existing cancellation text says “owner requested halt”; the actual requester was ChatGPT after this unsafe test was observed.

Other runtime findings remain: Aurek lacks a hospital interior treatment anchor; Besh found no suitable wild prey; Cresh listed missions but found no eligible nearby destroy mission; Dorn stopped 11.7 m from its leader. The two completed blocked/failing rounds for Aurek/Besh/Cresh generated next-assignment transitions to stationary census in their reports/state. No fallback scenario actually executed before the stop, so full runtime acceptance and ticket regression remain pending Claude.
