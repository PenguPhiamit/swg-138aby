# C46 staging: Discord feed and public bot map

Implemented offline; delivery, pinning, tunnel and real browser serving are untested.
Claude must review the public allowlist and route handler before starting anything.
No galaxy or bot commands are involved. All state, previews and tunnel logs are
gitignored under `Agent/discord-feed/`; the webhook stays outside the project.

The public page has anonymous server bots, planet selection, profession toggles,
state/level tooltips, fixed stock city labels and an original coordinate grid.
It does not redistribute the client's bitmap maps. There are no private dashboard
pages or routes, real-player/squad rows, original bot names, account details, arbitrary
activity strings, logs, filesystem paths or addresses in its JSON. City labels use
approximate fixed coordinates; player settlement names are never imported.

The feed renders a panel for every populated planet, uses the private browser's
profession colours, and attaches that PNG to one status embed. It creates the first
message with `wait=true`, saves the returned ID, then PATCHes that same ID with a new
attachment every minute. The owner pins that first message manually once. Alerts
and the morning digest are separate messages. Both successful transition observations
and queued deliveries persist across restarts. Missing map data is unknown and never
triggers a false server-down or run-ended alert. The first poll establishes a baseline;
the watchdog probe ignores historical lines on its first read.

`live_map.py` also adds numeric `feed` metadata to its private JSON. **Claude needs to
reload that map process on 8765 after review**, so the feed can obtain the mission
counter, run identity and freshness-based server status. No galaxy restart is needed.
An old readable server sample becomes down after 180 seconds unless who.json is
still fresh (60 seconds). This is telemetry freshness, not a process-health assertion.
The mission counter counts explicit `mission_done` events in the current log/run;
the morning table can also include completions inferred by the separate analysis tool.

The 07:00 digest uses the Windows PC's local timezone and the newest report by file
modification time. It extracts only numeric values from the last row of its run
comparison table, never report prose. Starting the feed after 07:00 sends that day's
digest once; absent or malformed reports wait for a later cycle. A note states that
the report may predate today. Rate-limit retries preserve the queue and honour the
longer of Discord's response/header cooldown and 60 seconds. An unconfirmed request
leaves `inflight` set and stops the sender; reconcile it before restarting to prevent
duplicate new messages. A deleted card is not silently replaced (404 stops delivery).

## Reviewed start and stop

These commands are documentation only; none were run during staging.

1. As `swgemu`, reload the private map process, then run the public process:

   ```sh
   python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/live_map.py --public --port 8766
   ```

2. In another WSL shell as `swgemu`, start the wrapper (approved binary already installed):

   ```sh
   bash /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/bots/public_tunnel.sh
   ```

   The wrapper checks the public schema first, records its PID, extracts only a bare
   HTTPS `trycloudflare.com` URL, and atomically publishes `public-url.txt`. It removes
   the URL on exit. A quick-tunnel URL changes on a new launch; the embed picks up the
   current file on its next cycle. A killed wrapper can leave a stale file after an
   uncatchable crash; inspect that folder before reuse.

3. From the project root in Windows, preview first:

   ```powershell
   & C:/Users/Pengw/miniconda3/python.exe outputs/tools/bots/discord_feed.py --once
   ```

   After review and the owner's posting go, create the private webhook file and run:

   ```powershell
   & C:/Users/Pengw/miniconda3/python.exe outputs/tools/bots/discord_feed.py --send
   ```

4. Stop foreground processes with Ctrl+C. For a background tunnel, inside WSL:

   ```sh
   kill -TERM "$(cat /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Agent/discord-feed/tunnel.pid)"
   ```

   Stop the map/feed by their own PID or console, never a broad process-name kill.
   No services are installed and no galaxy process is touched.

## Offline verification

```powershell
& C:/Users/Pengw/miniconda3/python.exe -m unittest discover -s outputs/tools/bots -p test_discord_feed.py -v
& C:/Users/Pengw/miniconda3/python.exe -m unittest discover -s outputs/tools -p test_live_map.py -v
```

Tests use saved synthetic JSON with explicit private-name/address/path sentinels,
mock HTTP transports, temporary files and mocked server construction; no listener,
tunnel or Discord connection is opened. The saved JSON exercises multiple planets,
PNG output, embed/attachment shape, route denial, roster/logger isolation, unknown
telemetry, run transitions, digest timing, watchdog cursors, edit identity, 429 cooldown
and uncertain-delivery protection. Existing map shaping tests remain required.

Staging result, 16 Oct: 18 C46 + 11 existing map + 24 existing Discord privacy tests
pass (53 total); shell syntax check passes; the saved two-planet PNG was visually
inspected. Tests ran with the owner's Windows Python/Pillow. No feed/map/tunnel
process was started, no webhook was read and no Discord request was sent.

API references: [Discord webhooks](https://docs.discord.com/developers/resources/webhook)
documents `wait=true`, multipart attachments and editing a webhook message;
[Cloudflare quick tunnels](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/)
documents the temporary public hostname and development/testing scope.
