# Saved squad report triage

Generate with `python outputs/tools/squad_health_report.py` from project root. Default reads latest timestamped JSON per group and writes only this triage folder. It never connects/stops clients, starts services or changes original reports. Custom fixture folders: --reports PATH --output PATH.

Read latest.md first; latest.json is machine-readable. Reports can come from different times/builds: no pooled pass rate is calculated. ERROR includes malformed records and count inconsistencies; FAIL preserves failed checks even alongside blocked notes; BLOCKED prevents safe prerequisite stops becoming full gameplay passes; NOT_RUN and NO_CHECKS stay explicit. These states are triage, not automatic server-defect diagnosis.

Offline regression command: `python outputs/tools/check_squad_health_report.py`. Tests cover all-passed-but-blocked, no-check blocked, mixed failure/block, inconsistent totals, malformed JSON and missing squads. No TortoiseBots implementation was copied.
