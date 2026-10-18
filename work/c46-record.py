from datetime import datetime
from pathlib import Path
import re

stamp = datetime.now().strftime('%Y-%m-%d %H:%M')
board = Path('outputs/SWG-handoff.md')
text = board.read_bytes().decode('utf-8')
old = '| **C46: Discord feed + public bot map** | ChatGPT, Medium | claimed 2026-10-16; staging only | Offline tools/tests; Claude public-mode review required before start; no services, tunnel, posts or server writes |'
new = '| **C46: Discord feed + public bot map** | ChatGPT, Medium | offline complete 2026-10-16; staged for Claude review | `3150acf`; 53 tests pass + PNG visual/shell syntax checks; public serving/Discord/tunnel untested; nothing started or posted; start/stop docs in `Documentation-support/C46-discord-public-map.md` |'
assert old in text
text = text.replace(old, new, 1)
prefix, log = text.split('## Log\r\n', 1)
entries = re.findall(r'^### .*?(?=^### |\Z)', log, re.M | re.S)
assert len(entries) == 4
entry = f'### {stamp} ChatGPT: C46 Discord/public map staged\r\n\r\n- `3150acf`: anonymous public map, Windows PNG/status feed with PATCH identity, transition/watchdog alerts, 07:00 numeric digest and quick-tunnel wrapper; 53 offline tests pass, saved PNG visually checked, shell syntax clean. All runtime/delivery untested; no feed/map/tunnel started, no secrets read, posts, bots, server writes or restarts. Next: Claude reviews public mode, reloads the private map metadata and starts only after review/owner posting go; manual first-message pin. Start/stop guide: `Documentation-support/C46-discord-public-map.md`. Oldest Log entry archived.\r\n\r\n'
board.write_bytes((prefix + '## Log\r\n\r\n' + entry + ''.join(entries[:3])).encode('utf-8'))
archive = Path('outputs/SWG-handoff-archive.md')
with archive.open('ab') as out:
    out.write((f'\r\n## Moved {stamp} (C46 staging)\r\n\r\n' + ''.join(entries[3:])).encode('utf-8'))
roadmap = Path('outputs/SWG-roadmap.md')
text = roadmap.read_bytes().decode('utf-8')
needle = '- [ ] C17 owner setup, private redaction list, reviewed first post and explicit go; real Discord delivery untested.\r\n'
assert needle in text
addition = '- [x] C46 Discord bot feed + anonymous public-map/tunnel tools staged (16 Oct, ChatGPT), `3150acf`; 53 offline tests pass; PNG inspected; no services started or posts sent. `Documentation-support/C46-discord-public-map.md`.\r\n- [ ] C46 Claude public-mode review, reviewed start, webhook delivery/manual pin and browser/tunnel acceptance; runtime untested.\r\n'
roadmap.write_bytes(text.replace(needle, needle + addition, 1).encode('utf-8'))
inbox = Path('outputs/Agent/to-claude.md')
with inbox.open('ab') as out:
    out.write((f'\r\n### {stamp} ChatGPT: C46 staging ready for your public-mode review\r\n'
               '- Owner\'s C46 brief implemented in `3150acf`: Windows dry-run-default PNG/embed feed, persistent PATCH message ID, transition/watchdog alerts + 07:00 numeric digest; strict anonymous server-bot-only public routes and swgemu quick-tunnel wrapper. 53 offline tests pass, PNG inspected, bash syntax clean. No services, tunnel, webhook reads/posts, bot commands, /opt writes or restarts.\r\n'
               '- Please review `tools/live_map.py` PublicHandler/public_snapshot and `tools/bots/public_map_data.py` before starting. Reload only the private map process on 8765 to provide new numeric feed metadata; public default port 8766. Commands/limitations: `Documentation-support/C46-discord-public-map.md`; owner manually pins the first card once. Webhook is still owner-created outside the project. Runtime and Discord delivery untested. C48 remains the next task.\r\n').encode('utf-8'))
