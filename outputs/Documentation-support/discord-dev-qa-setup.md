# Private SWG developer and remote-tester Discord

14 October 2026, ChatGPT. Owner wants a developer server for potential hired testers and confirmed **remote testers**. Research/setup blueprint only: no Discord server, account, app, webhook, invitations, posts or remote-access service created.

Proposed name: **SWG Dev & QA**. Keep it invite-only. Start with Discord's own channels, roles, forums, voice and scheduled events; add our existing reviewed webhook feed. A custom bot can follow after real intake volume justifies it.

## Channels and access

| Area | Channels | Access |
|---|---|---|
| Start | `start-here`, `announcements`, `connection-guide`, `server-status` | Invited testers and developers; staff write reference/status channels |
| QA | `test-plans` forum, `bug-reports` forum, `feedback` forum, `qa-chat`, Playtest voice | Testers and developers; testers create/reply to reports |
| Development | `dev-log`, `engineering`, `bot-reports`, `build-release` | Developers and owner; reviewed summaries only |
| Owner | `owner-desk` | Owner only; staffing/access decisions |

Forum channels require enabling Community. That is a server setting, not permission to enable public discovery. Retain explicit private category permissions and controlled invitations. Community's required rules/update channels must also be configured deliberately. If Community is unwanted, use ordinary text channels with one thread per report. [Discord forum requirements](https://support.discord.com/hc/en-us/articles/6208479917079-Forum-Channels-FAQ), [Community setup](https://support.discord.com/hc/en-us/articles/360047132851-Enabling-Your-Community-Server).

## Roles

| Role | Permissions |
|---|---|
| Owner | Owns server; manages integrations, roles and invitations |
| Developer | Development/QA read-write; no general Administrator or integration-management permission by default |
| QA Lead | QA access plus scoped report/thread moderation and playtest coordination |
| Tester | QA reports/chat/voice and reference-channel read access; no development/owner area or administrative powers |
| New arrival / everyone | Only the welcome/rules area until owner assigns access |

Deny View Channel for everyone on the restricted categories, explicitly allow intended roles, and check combined-role visibility before invitations. Administrator bypasses channel restrictions; hired testers do not need it. Owner controls invitations initially. Offboarding removes all access-granting roles/invitations and separately revokes game/network access. Discord membership never grants game staff privileges. [Discord roles and permissions](https://support.discord.com/hc/en-us/articles/214836687-Discord-Roles-and-Permissions), [private-server setup](https://support.discord.com/hc/en-us/articles/206143407-How-do-I-set-up-a-private-server).

## Integrations: what is available versus proposed

| Integration | Purpose | Current readiness |
|---|---|---|
| Existing local C17 webhook sender | Reviewed fixed-vocabulary development digests and process-based availability | Implemented; 24 offline checks previously passed. Real delivery untested; owner approval/private webhook setup pending |
| Native bug-report forums | One report per post; tags, search and follow-up | No custom code needed; server/Community setup pending |
| Native Scheduled Events + voice | Playtest appointments, attendance interest and live coordination | Configuration pending; event audience follows channel permissions |
| Native AutoMod | Basic spam/mention filtering and moderation | Optional configuration; no additional bot required |
| Custom `/bug`, `/build`, `/status` app | Structured report modal, pinned build information and saved status | Proposed, unbuilt; app/hosting permission and implementation review required |
| Issue-tracker sync | Move approved reports into a durable engineering backlog | Deferred; local project git has no remote, and no external tracker is selected |
| Agent report intake | Review a selected bug and copy a sanitized request to the local board | Manual first; no Discord-reading agent connection exists |

Incoming webhooks send updates into a channel; interactive commands/modals require a Discord application. The existing sender does not read Discord or control the galaxy. Its raw board/overnight/morning feeds are local previews only; only curated/status feeds are eligible for explicitly approved sends. Status means a recent process snapshot, not successful player login. [Webhooks](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks), [interactions](https://docs.discord.com/developers/interactions/overview), [scheduled events](https://support.discord.com/hc/en-us/articles/4409494125719-Scheduled-Events), [AutoMod](https://support.discord.com/hc/en-us/articles/4421269296535-AutoMod-FAQ).

Plugin discovery in this session did not return a Discord integration. It returned an unrelated hosting plugin, which was not suggested or installed. This is a search result, not proof that no Discord plugin exists anywhere. Native Discord features, official webhooks and a separately built application remain viable routes.

## Testing workflow and templates

Each playtest gets a plan with a build identifier, target features, starting conditions, expected results, approximate duration and reset policy. Reports use the same build identifier. A screenshot or message alone is not proof of a completed game operation.

Bug post template:

```text
Title: [feature] observable problem
Build / test session:
Planet / location:
Steps to reproduce:
Expected result:
Actual result:
Frequency: once / intermittent / every attempt
Impact: cosmetic / blocks feature / crash or loss
Evidence: sanitized screenshot or short clip
```

Suggested labels: new, needs-info, reproduced, in-progress, ready-to-retest, verified, duplicate; feature labels combat, crafting, travel, UI, quest and creature-handler. QA Lead/developers manage workflow status. A fixed report is verified only after a tester reproduces the original steps on the specified updated build. Keep sanitized local copies of accepted reports so Discord is not the only project record.

Hiring administration, rates and personal details remain outside shared QA channels. Do not publish raw project logs, the handoff board, credentials, backup files, personal names/aliases or unredacted game screenshots. Keep licence-required asset credits intact. These are the owner's existing publication rules, not a new moderation policy.

## Remote access is a separate prerequisite

Discord organizes people; it does not expose the SWG login/zone services. Our saved SOP describes the current test galaxy as a disposable backup restore. Before invitations, choose either scheduled resettable sessions with that behavior clearly stated or a separately prepared persistent QA world. Do not promise character progression survives a test restart.

For a small first cohort, evaluate private access to an isolated QA host through a service such as Tailscale, with policies limited to the game service. Machine sharing supports giving external users access to a selected machine, subject to access rules; it is not permission to share the whole home network. No service installed/account created or plan/cost assumed. [Tailscale sharing](https://tailscale.com/docs/features/sharing).

A remote-access proof must cover actual login, advertised zone address, UDP and TCP as required, movement/combat, reconnect and revocation from a device outside the home LAN. Check WSL's actual NAT/mirrored mode and Windows/WSL firewalls. Microsoft's NAT portproxy example handles TCP and is not proof that SWG UDP traffic will work. No firewall/router/network changes have been made. [Microsoft WSL networking](https://learn.microsoft.com/en-us/windows/wsl/networking).

A dedicated QA VM/host with scoped access is preferable to granting testers general access to the owner's workstation. Hosting/network choice and game-account provisioning belong in a separate owner-approved engineering task with Claude.

## Proposed first rollout

1. Owner approves creating **SWG Dev & QA** with the private roles/channels above and Community enabled for forums. No invitations or posts included in that approval unless expressly requested.
2. Create the layout, report guidelines/tags and a test-view permission audit. Owner signs in personally if required.
3. Separately configure one webhook and approve one sanitized preview/test post. No unattended feed is authorized yet.
4. Claude and owner choose reset/persistence and remote-host access, then prove one remote test account can connect and can be revoked.
5. Owner invites a small pilot cohort; run one named test session before adding issue-tracker automation or a custom bot.

No paid third-party Discord bot or AI integration is needed for this proposed first stage. Additional provider accounts, automated publication, a two-way application, network access and hiring/outreach each need their own concrete scope and the owner's approval.

## Owner follow-up: mixed-experience team and in-game intake

Developer friends, experienced players and players new to SWG may join. Add getting-started and ask-for-help to QA; keep developer privileges separate from player/testing access. Owner requests in-game reports saved locally, agent review when capacity is available, then agent relay to Discord. See [player-bug-inbox-design.md](player-bug-inbox-design.md) for source findings, durable queue/claims, privacy, delivery tracking and acceptance gates. This supersedes the earlier manual-first intake suggestion for the intended implementation; it does not claim the relay is built or connected.
