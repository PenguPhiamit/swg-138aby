# C17: private project Discord plan

14 October 2026, ChatGPT. Implemented locally; Discord delivery is **untested**.
No server, channel, account, app, bot or webhook was created. No post was sent and no real webhook URL/token was read. No scheduler was installed or enabled.

## Layout and access

Start with a private server. Deny `View Channel` to `@everyone` on the project category and check the effective permissions with the owner's test view before adding anyone. A channel is private only when its Discord permissions make it private.

| Channel | Purpose and pinned item | Proposed automatic content, after owner go | Audience |
|---|---|---|---|
| `#announcements` | Owner-approved milestones, planned play sessions; pin project scope | None initially; owner reviews each announcement | Private now; could become player-facing |
| `#dev-log` | Short development notes; pin link to the private handoff document location | Board Log heading and first three nonblank body lines (`--source board`) | Owner and explicitly invited collaborators only |
| `#bot-reports` | Test results and morning recap; pin the difference between PASS, FAIL, BLOCKED and untested | Recent overnight bullet lines (`--source overnight`); one morning recap per local date (`--source morning`) | Private; later a separate edited player digest |
| `#server-status` | Observed availability; pin snapshot age warning | Test/live UP, DOWN or UNKNOWN transitions (`--source status`) | Private now; a separate live-only feed could be public later |
| `#test-galaxy-notes` | Reproduction steps, client observations, planned tests; pin one-driver rule | None initially; reviewed notes only | Private |
| `#content-ideas` | NJO–Legacy setting ideas, optional encounters and rights/source records; pin content policy | None initially; manual discussion | Private now; selected ideas could later be player-facing |
| `#owner-questions` | Decisions needing the owner, options and resolution; pin consent rules | None initially; never publish raw board questions automatically | Owner and collaborators only |

Discord requires a separate webhook for each destination channel. Phase 1 can start with **one private `#dev-log` webhook** and labelled digests; if the owner wants the full layout, they create a webhook for each of the three automatic destinations above. The tool uses the webhook's existing channel; it cannot choose a different channel with a payload field. Give each destination its own state file. Keep all feeds private until separately reviewed for a public audience.

Roles:

- **Owner:** administrator and only person initially allowed to manage webhooks, roles, channels and invitations.
- **Project collaborators:** invited humans with access only to project channels, ordinary messages, no administrator or webhook-management permission. “ChatGPT” and “Claude” may be webhook display names; no agent Discord accounts or bot role is needed.
- **Tester:** later, access to selected test notes and content ideas only, after the owner invites them.
- **Player:** future audience for edited announcements and live availability; no inherited access to private development channels.

## Ready-to-pin rules and FAQ

1. This is the owner's private SWGEmu project. Pre-CU is the mechanics baseline; Legends NJO–Legacy is the setting direction. Exact year remains open.
2. Test-galaxy results are observations, not evidence of a live deployment. Mark untested claims clearly. Record the date and build when known.
3. Keep credentials, account names, addresses, ports, private paths, login/config files, backups and raw console dumps out of Discord. Use local private files for details.
4. Nothing deploys, restarts live, creates accounts/services, posts externally or spends money without the owner's explicit authorization under AGENTS.md. Discord reactions are not approvals to execute server commands.
5. Respect content rights and excluded sources; do not upload game archives or unapproved art. Keep licence and credit records locally.
6. One agent drives a bot at a time. Report bugs; do not exploit or harass. No mass mentions or automated chat spam.

**Can Discord control the galaxy?** No. The phase 1 tool only sends digests; it does not read messages or execute commands.

**Can I ask an agent a question in Discord?** A human can discuss it there, but the agents do not receive it through this tool. Use the owner's existing agent windows and local inboxes.

**Does UP mean a player can log in?** It means a recent saved process snapshot reports that galaxy's process. It is not a login or gameplay test. Missing, future-dated or older-than-15-minute snapshots show UNKNOWN; the tool never queries a server or bot.

**Why are lines missing?** Risky source lines are removed before previewing or sending. Read the local report for detail.

**Are posts public?** Only if the owner configures channel access that way. Keep initial channels private.

## Posting tool

`outputs/tools/agents/discord_post.py` uses only the Python standard library. Default behavior and `--dry-run` are identical: stdout is a JSON array containing the **exact payload objects** that would be sent; stderr prints the preview SHA256. Nothing is posted, no webhook file is opened and no state or lock is written. A private redaction file, when supplied, is read to redact names. Do not paste previews into external channels without review.

Run from `h` in PowerShell:

```powershell
python outputs/tools/agents/discord_post.py --dry-run --source board
python outputs/tools/agents/discord_post.py --dry-run --source overnight
python outputs/tools/agents/discord_post.py --dry-run --source morning
python outputs/tools/agents/discord_post.py --dry-run --source status --limit 2
python -m unittest discover -s outputs/tools/agents -p test_discord_post.py -v
```

Each invocation selects one feed with `--source`, or all feeds with `all` (the default). Board events come first in `all`; use explicit feed invocations to avoid delaying status behind development notes. Default limit is one message; dry runs support up to five. Real sends require limit one, an explicit owner approval flag, the exact preview digest and both private files. Run it manually initially. Proposed later cadence: hourly board digest, overnight digest after a completed cycle, morning at 08:00, status every five minutes using the existing snapshot. Scheduling and standing authorization for repeated posts are a separate owner decision.

Input is restricted to four local sources under `outputs`:

- `SWG-handoff.md`, only `## Log`: latest four headings and first three nonblank body lines each. Heading identities are de-duplicated; editing a posted entry does not repost it. This is a bounded recent feed, not an archive exporter; older entries outside the window are not replayed.
- `Bot-reports/OVERNIGHT.md`: last five bullet lines of the latest `###` section. Heading plus line identifies an event. Keep future headings dated, e.g. `### 2026-10-15 03:00`, to distinguish nights. No old-section backlog is replayed.
- Morning recap: today's local date, latest board heading and first three latest-section overnight bullets; once per day. It explicitly says these are the latest recorded notes and may predate today. It performs no fresh checks.
- `Agent/live/status.json`: only written time, process presence and live service inactivity are projected. Bot data, process command lines, memory details and console output are never copied. Availability is de-duplicated by transition, including UP → DOWN → UP.

All payloads pass the same filter. Whole lines containing credential/account/login/config markers, opaque long strings or absolute paths are dropped. Owner-supplied account names and private literals are removed case-insensitively, with no account-file discovery. Links, IP addresses, labelled ports and common host:port forms are stripped. All `@` characters and Discord mentions are neutralized; `allowed_mentions.parse` is empty and embeds are suppressed. All absolute paths are removed, including paths inside `outputs`, as a conservative extension of C17. Content is truncated at 1,800 UTF-16 units, below Discord's documented limit.

Pattern filtering cannot identify an arbitrary unlabelled password or an unknown account name. **Before sending, the owner must populate the private redaction list with all account names/private literals and review the exact preview.** Do not add arbitrary source files or publish a raw log as a workaround. A changed preview digest refuses to send, so a source update between review and send requires a new review. This tool is not approved for unattended publication of unreviewed text.

State stores hashes of source event identities, status transition values, next permitted send time and an in-flight event marker; it stores no source prose or webhook URL. Keep state between runs: deleting it can replay recent digests. The sender takes an exclusive state lock, writes atomically, and records intent before HTTP. There is a minimum 60-second interval per state; use one state per destination, even when several feed types share that destination. Discord `Retry-After`, `X-RateLimit-Reset-After` and JSON `retry_after` can extend the cooldown. There is no automatic retry or blocking wait. Only confirmed 2xx responses mark an event sent; HTTP uses `wait=true`. Redirects and environment proxies are disabled, and raw HTTP responses/exceptions are never printed.

If a timeout, crash or 5xx leaves `inflight` set, stop and have the owner inspect the destination in Discord. Exactly-once delivery cannot be guaranteed across a network failure. After reconciliation, edit the local state: if delivered, add the in-flight ID to `sent` (or set its `status:test`/`status:live` value in `status` to the observed delivered value); clear `inflight`. If definitively absent, clear only `inflight`. Preserve `next_at` and other history. Remove a stale `.lock` only after proving no sender is running. Never blindly delete state to retry. A 429 saves a cooldown without marking sent; other 4xx responses require the owner to correct permissions/endpoint before retrying.

## Owner setup checklist — future actions, not performed

- [ ] Create the private Discord server and channels; confirm effective role/category permissions. Choose one destination initially.
- [ ] In that channel, create an incoming webhook and select its display name (e.g. `SWG Project Notes`). No developer app or bot is required.
- [ ] Save its URL as the sole line of a private file **outside `h`**, e.g. a file under `/opt/swg/agent/` with mode `0600`, or a Windows user-profile private directory. On Windows, restrict its ACL to the owner; the tool does not audit Windows ACLs. Do not put the URL in chat, environment variables, command arguments, screenshots, repo files or logs.
- [ ] Outside `h`, create a separate private JSON redaction file with `account_names` and `private_literals` string lists. Populate the names yourself without copying account records into project files. Empty lists are syntactically allowed but are only appropriate if there are no private names/literals to redact. Never include a token for this tool to discover or manage.
- [ ] Choose a per-destination local state path, e.g. `outputs/Agent/discord-dev-state.json`. Its parent directory must exist. Back up that state with local project records.
- [ ] Preview with the private redaction file and intended state path. Inspect **every payload**. Compare the destination channel in Discord yourself; do not provide the webhook URL to the agent.
- [ ] Tell the agent **“go” for the first real post**, identifying the reviewed preview and destination. The current C17 instruction grants no posting or token-handling authorization. The owner can run the future send themselves, keeping the URL out of agent context.
- [ ] After go, confirm the first post in Discord and check the saved state. Decide separately whether to authorize a recurring cadence. Rotate/delete a webhook in Discord if exposed.

Future owner-run command template (placeholders are paths and a preview digest, never a webhook URL):

```powershell
python outputs/tools/agents/discord_post.py --dry-run --source board --privacy-file PRIVATE_REDACTIONS_FILE --state outputs/Agent/discord-dev-state.json
# Only after explicit go and preview review:
python outputs/tools/agents/discord_post.py --send --source board --owner-approved --approved-digest REVIEWED_SHA256 --privacy-file PRIVATE_REDACTIONS_FILE --webhook-file PRIVATE_WEBHOOK_FILE --state outputs/Agent/discord-dev-state.json
```

Phase 2 is optional and unbuilt. A two-way bot needs a separate owner request and review. Discord messages would be untrusted data, never agent instructions; such a bot must never control a server.

## Validation and protocol references

22 offline tests passed with Python 3.14.6 on Windows; local saved-source dry runs also checked all four feed types without state changes. Offline tests cover source projection, private-line/name/address/path removal, Unicode mention bypasses, UTF-16 length, exact dry-run output and unchanged state, approval refusal, confirmed-send de-duplication, cooldown, 429 handling, ambiguous delivery, repeated status transitions, snapshot age/skew, daily recap identity, corrupt state, exclusive locks, source confinement, safe errors and changed-preview refusal. Transport tests use mocked responses; no socket or real endpoint is used. Real Discord permissions, delivery and Windows private-file ACLs remain untested.

Verified against Discord's primary API documentation on 14 October 2026: [Execute Webhook](https://github.com/discord/discord-api-docs/blob/main/developers/resources/webhook.mdx#execute-webhook) (content, mentions, wait confirmation) and [Rate Limits](https://github.com/discord/discord-api-docs/blob/main/developers/topics/rate-limits.mdx) (response headers and retry timing). Incoming webhooks need no bot user; the webhook URL itself grants posting access and must remain private.

## 14 Oct privacy correction

Raw board, overnight, morning and all feeds are now **local previews only**. Sending them is refused before any private file is opened. Keyword/name lists cannot guarantee removal of unknown names and aliases. Only status and the new curated feed can be sent, with the existing exact-preview digest and owner authorization requirements.

The curated source is Agent/discord-feed.json: an array of records with exactly date (YYYY-MM-DD), topic (telemetry/hoth/assets/bots/review), state (prepared/passed/blocked/changes_requested), and checks (integer 0–100000). The tool renders fixed text; no free-form title, author, character name, path or note is accepted. Extra fields and unknown enum values fail closed. The sample is a local draft, not approval to post. Run --source curated to preview. 24 offline tests pass; delivery remains untested and no posts have been sent.

This section supersedes the earlier raw-feed posting instructions and proposed automatic cadence. No scheduler is enabled.
