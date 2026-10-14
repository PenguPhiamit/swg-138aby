"""Bot squads: five named groups of bots on the TEST galaxy, driven by short scenario scripts.

Run inside Debian as swgemu. From Windows (Codex):
  wsl -d Debian -u swgemu -- python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/bots/squad.py <command>

  squad.py accounts                     the AgentAccounts value for test_galaxy.py --config
  squad.py galaxy                       print the root commands that restart the test galaxy for the squads
  squad.py setup [GROUP ...]            log in every member (creating characters on a fresh galaxy), move them
                                        out of the tutorial room, form each group. Safe to repeat.
  squad.py status [GROUP ...]           one line per bot
  squad.py run SCENARIO.py ... [--group G ...] [--rounds N] [--minutes M] [--detach]
                                        run scenarios at the same time (each names its GROUP, or --group picks
                                        groups for one shared scenario); prints a short summary per run.
                                        --rounds/--minutes repeat them, logging offline bots back in between
                                        rounds; --detach runs in the background (Bot-reports/runs/<time>.txt,
                                        and <time>-summary.md rewritten after every round)
  squad.py activity                     saved squad states and age (no bot commands)
  squad.py last                         print the newest run summary
  squad.py halt                         a background run requests a cooperative stop (outstanding body commands must finish)
  squad.py tidy                         zip old reports, rotate long LOG.md files, drop offline bots' logs
                                        (long runs do this every 5 rounds)
  squad.py send NAME '<json>' [wait_s]  one raw command to one bot (by first name), filtered events
  squad.py stop [GROUP ...]

Groups and members are in groups.json; each group's leader carries the group's name. Every run writes
outputs/Bot-reports/<Group>/<time>-<scenario>.json and adds one line to outputs/Bot-reports/<Group>/LOG.md,
so anyone can pick up what each group did. Scenario API: see scenarios/README.md.

Credentials live in /opt/swg/agent/bots/<account>.json (0600) and are never printed.
"""
import importlib.util, json, os, secrets, subprocess, sys, threading, time, traceback
from datetime import datetime
from pathlib import Path
from run_control import RunControl, RunStopped, read_activity
from fallback import Chooser

HERE = Path(__file__).resolve().parent
OUTPUTS = HERE.parents[1]
REPORTS = OUTPUTS / 'Bot-reports'
CLIENT = '/opt/swg/Core3-dev/MMOCoreORB/build/dev/src/client/core3client'
CREDS = Path('/opt/swg/agent/bots')
RUNS = Path('/var/tmp/swg-bots')  # on the WSL disk: /tmp is a RAM disk (filled on 13 Oct and broke MariaDB)
LOGIN_PORT = '46453'
KEEP_EVENTS = 400  # notable events kept per bot in a report
TEST_GALAXY = Path(__file__).resolve().parents[1] / 'test_galaxy.py'


def load_spec():
    return json.loads((HERE / 'groups.json').read_text(encoding='utf-8'))


class BotDown(Exception):
    pass


def short(value, limit=300):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
    return text if len(text) <= limit else text[:limit] + '…'


def proc_start(pid):
    """A process's start time in clock ticks since boot (/proc/<pid>/stat field 22), or None."""
    try:
        return int(Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[19])
    except (OSError, ValueError, IndexError):
        return None


def newest_server_start():
    """Start time of the newest running core3 server (only the test galaxy's while live is stopped), or None."""
    starts = []
    for entry in Path('/proc').iterdir():
        if entry.name.isdigit():
            try:
                if (entry / 'cmdline').read_bytes().split(b'\0')[0] == b'./core3':
                    starts.append(proc_start(int(entry.name)))
            except OSError:
                pass
    return max((s for s in starts if s is not None), default=None)


def compact(event):
    """A report-sized copy of an event."""
    if event.get('event') == 'sui_page':
        page = event.get('page', {})
        texts = [c.get('wide', [''])[0] for c in page.get('commands', []) if c.get('wide')]
        return {'event': 'sui_page', 'page_id': page.get('page_id'), 'script': page.get('script'),
                'text': short(' | '.join(t for t in texts if t), 400)}
    return {k: (short(v) if isinstance(v, (str, list, dict)) else v) for k, v in event.items()}


class Bot:
    def __init__(self, member, group):
        self.member, self.group = member, group
        self.account, self.name = member['account'], member['name']
        self.first = self.name.split()[0]
        self.dir = RUNS / self.account
        self.fifo, self.log = self.dir / 'in', self.dir / 'out.log'
        self.offset, self.partial = 0, b''
        self.inbox = []    # events since the last command (all but "gone")
        self.history = []  # notable events for the report
        self.oid = None
        self.started = time.time()
        self._skip_to_end()

    # ---- process ----
    def pid(self):
        try:
            pid = int((self.dir / 'pid').read_text())
            cmdline = Path(f'/proc/{pid}/cmdline').read_bytes()
        except (OSError, ValueError):
            return None
        return pid if b'core3client' in cmdline else None

    def running(self):
        return self.pid() is not None

    def stale(self):
        """The body logged in before the newest core3 started. The game runs over UDP, so a body whose galaxy was
        restarted under it can still say connected while the new server has never heard of it (14 Oct 05:32)."""
        pid, server = self.pid(), newest_server_start()
        return pid is not None and server is not None and proc_start(pid) < server

    def creds(self):
        path = CREDS / f'{self.account}.json'
        if path.exists():
            data = json.loads(path.read_text())
            if data.get('character') != self.name:
                data['character'] = self.name
                path.write_text(json.dumps(data))
            return data
        CREDS.mkdir(mode=0o700, exist_ok=True)
        data = {'username': self.account, 'password': secrets.token_urlsafe(18), 'character': self.name}
        path.write_text(json.dumps(data))
        path.chmod(0o600)
        return data

    def start(self, create=False, wait=120):
        """Start the body. Returns 'ready', 'created', 'missing' (no such character) or 'failed: …'."""
        self.stop()
        (self.dir / 'log').mkdir(parents=True, exist_ok=True)
        # The client's own logger writes 100 MB pieces under log/ (rotated to log/zArchive). /tmp is a RAM disk shared
        # with MariaDB's temporary files: on 13 Oct 7.5 GB of these filled it and broke every login. Start clean.
        for old in (self.dir / 'log').rglob('core3client-*.log'):
            old.unlink(missing_ok=True)
        if not self.fifo.exists():
            os.mkfifo(self.fifo)
        acc = self.creds()
        host = subprocess.check_output(['hostname', '-I'], text=True).split()[0]
        env = dict(os.environ, CORE3_CLIENT_USERNAME=acc['username'], CORE3_CLIENT_PASSWORD=acc['password'],
                   CORE3_CLIENT_LOGINHOST=host, CORE3_CLIENT_LOGINPORT=LOGIN_PORT)
        holder = subprocess.Popen(f'exec sleep infinity > {self.fifo}', shell=True, start_new_session=True,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        (self.dir / 'holder').write_text(str(holder.pid))
        args = [CLIENT]
        if create:
            args += ['--create-character', '--char-name', self.name,
                     '--char-race', f'object/creature/player/{self.member["race"]}.iff',
                     '--char-profession', self.member['profession']]
        else:
            args += ['--character-firstname', self.first]
        args += ['--agent-control']
        body = subprocess.Popen(args, cwd=self.dir, env=env, stdin=open(self.fifo, 'rb'), stdout=open(self.log, 'wb'),
                                stderr=subprocess.STDOUT, start_new_session=True)
        (self.dir / 'pid').write_text(str(body.pid))
        self.offset, self.partial, self.inbox = 0, b'', []
        deadline, entered = time.time() + wait, False
        while time.time() < deadline:
            time.sleep(1)
            for event in self._read():
                if event.get('event') == 'ready':
                    self.oid = event.get('self')
                    time.sleep(5)  # let the world fill in
                    self._read()
                    return 'ready'
                if event.get('event') == 'position_set_by_server':
                    entered = True
            if not create and b'firstname not found' in self.log.read_bytes():
                self.stop()
                return 'missing'
            if body.poll() is not None:
                body.wait()
                if create and entered:
                    return 'created'
                text = self.log.read_text(errors='replace')
                if 'firstname not found' in text:
                    return 'missing'
                lines = [l for l in text.splitlines() if 'ERROR' in l or 'rror' in l or 'declined' in l]
                return 'failed: ' + short(' / '.join(lines[-3:]) or text[-300:], 300)
        self.stop()
        return f'failed: no answer in {wait} s'

    def stop(self):
        if self.running():
            try:
                self._write({'cmd': 'quit'})
                time.sleep(2)
            except BotDown:
                pass
        for item, marker in (('pid', b'core3client'), ('holder', b'sleep')):
            try:  # only signal our own processes, never a recycled pid
                pid = int((self.dir / item).read_text())
                if marker in Path(f'/proc/{pid}/cmdline').read_bytes():
                    os.kill(pid, 15)
            except (OSError, ValueError):
                pass

    # ---- protocol ----
    def _skip_to_end(self):
        try:
            self.offset = self.log.stat().st_size
        except OSError:
            self.offset = 0

    def _read(self):
        try:
            with open(self.log, 'rb') as stream:
                stream.seek(self.offset)
                new = stream.read()
        except OSError:
            return []
        if not new:
            return []
        self.offset += len(new)
        lines = (self.partial + new).split(b'\n')
        self.partial = lines.pop()
        events = []
        for raw in lines:
            if not raw.startswith(b'@@AGENT '):
                continue
            try:
                event = json.loads(raw[8:].decode('utf-8', 'replace'))
            except ValueError:
                continue
            events.append(event)
            kind = event.get('event')
            if kind == 'gone':
                continue
            self.inbox.append(event)
            if 'reply' in event or (kind == 'chat' and event.get('from') not in self.group.member_names):
                continue  # replies go in the step log; NPC chatter is noise
            self.history.append(dict(compact(event), t=round(time.time() - self.started, 1)))
            del self.history[:-KEEP_EVENTS]
        return events

    def _write(self, request):
        try:
            fd = os.open(self.fifo, os.O_WRONLY | os.O_NONBLOCK)
        except OSError:
            raise BotDown(f'{self.first} is not logged in (squad.py setup {self.group.name})')
        os.write(fd, (json.dumps(request) + '\n').encode())
        os.close(fd)

    def request(self, cmd, within=30, **args):
        """Send one body command and wait up to `within` s for its reply (a dict; ok=False with an error on failure).
        Keyword arguments go to the body as-is (including the body's own `timeout` for move/fight)."""
        self.group.checkpoint()
        if self.group.control:
            self.group.control.publish('running', f'{self.first}: {cmd}')
        self._read()
        self.inbox = []
        request = {'cmd': cmd, **args}
        self._write(request)
        deadline = time.time() + within
        while time.time() < deadline:
            for event in self._read():
                if event.get('reply') in (cmd, 'error'):
                    self.group.step(self, request, event)
                    self.group.checkpoint()
                    return event
            time.sleep(0.2)
            if not self.running():
                raise BotDown(f'{self.first} disconnected during {cmd}')
        reply = {'reply': cmd, 'ok': False, 'error': f'no reply in {within} s'}
        self.group.step(self, request, reply)
        return reply

    def wait_for(self, match, timeout=10):
        """The first event since the last command whose JSON contains `match` (any case), or for which
        match(event) is true. None after `timeout` seconds."""
        test = match if callable(match) else (lambda e, m=match.lower(): m in json.dumps(e).lower())
        deadline, seen = time.time() + timeout, 0
        while True:
            self.group.checkpoint()
            self._read()
            for event in self.inbox[seen:]:
                if test(event):
                    return event
            seen = len(self.inbox)
            if time.time() >= deadline:
                return None
            time.sleep(0.2)

    def idle(self, seconds):
        """Wait, collecting events (they stay in the inbox until the next command)."""
        self.group.sleep(seconds)
        self._read()
        return list(self.inbox)

    def messages(self):
        """System-message texts since the last command."""
        self._read()
        return [e.get('text', '') for e in self.inbox if e.get('event') == 'system']

    # ---- conveniences ----
    def status(self):
        reply = self.request('status', 10)
        self.oid = reply.get('self', self.oid)
        return reply

    def look(self, radius=64, type='', limit=60):
        return self.request('look', 10, radius=radius, type=type, limit=limit).get('objects', [])

    def find(self, name, radius=96, type='', where=None):
        """Nearest object whose name contains `name` (any case) and, if given, where(object) is true."""
        for obj in self.look(radius, type, 400):
            if name.lower() in str(obj.get('name', '')).lower() and (where is None or where(obj)):
                return obj
        return None

    def move(self, x, y, z=None, cell=None, timeout=90):
        args = {'x': x, 'y': y, 'timeout': timeout}
        if z is not None:
            args['z'] = z
        if cell:
            args['cell'] = cell
        return self.request('move', timeout + 15, **args)

    def walk(self, x, y, z=None, cell=None, tries=3):
        """move, repeated while it times out but gets closer (one move is capped at 95 s). Returns the last reply
        with 'seconds' = total time."""
        began, reply, last = time.time(), {}, None
        for _ in range(tries):
            reply = self.move(x, y, z, cell, 95)
            if reply.get('arrived') or not reply.get('ok', True) and 'timeout' not in str(reply.get('error', '')):
                break
            here = (reply.get('x'), reply.get('y'))
            if here == last:
                break  # not getting anywhere
            last = here
        return dict(reply, seconds=round(time.time() - began, 1))

    def go(self, obj, timeout=90):
        """Walk to an object from look/find (in the bot's current cell, if indoors)."""
        cell = self.status().get('cell') or None
        return self.move(obj['x'], obj['y'], obj.get('z') if cell else None, cell, timeout)

    def say(self, text):
        return self.request('say', 5, text=text)

    def slash(self, name, args='', target=0, wait=2.0):
        """Run a slash command; returns the events of the next `wait` seconds."""
        self.request('command', 5, name=name, args=args, target=target)
        return self.idle(wait)

    def fight(self, target, timeout=60):
        return self.request('fight', timeout + 15, target=target, timeout=timeout)

    def talk(self, target, wait=3.0):
        self.request('talk', 5, target=target)
        return self.idle(wait)

    def choose(self, index, wait=3.0):
        self.request('choose', 5, index=index)
        return self.idle(wait)

    def radial(self, target):
        """The object's right-click menu: the radial_menu event (items with radial_id, name, label), or {} if none."""
        self.request('radial_menu', 10, target=target)
        return self.wait_for(lambda e: e.get('event') == 'radial_menu' and e.get('target') == target, 5) or {}

    def select(self, target, radial_id, wait=2.0):
        """Open the object's menu, then pick radial_id (20 = use). Returns the events of the next `wait` s."""
        self.radial(target)
        self.request('select_radial', 10, target=target, radial_id=radial_id)
        return self.idle(wait)

    def sui_pages(self):
        return self.request('sui_pages', 5)

    def sui_respond(self, page_id, event=0, args=None, wait=2.0):
        self.request('sui_respond', 5, page_id=page_id, event=event, args=args or [])
        return self.idle(wait)

    def inventory(self):
        return self.request('inventory', 10)

    def inspect(self, target):
        return self.request('inspect', 10, target=target)

    def gear(self, kit='basic'):
        """Test-galaxy gear (/agentgear basic|boss): equips what fits, the rest goes to the inventory. Skipped
        when the bot already wears that kit's armor. Returns the server's answer (equipped/inventory/failed)."""
        armor = 'armor_composite' if kit == 'boss' else 'armor_bone'
        if any(armor in str(i.get('name')) for i in self.inventory().get('items', [])):
            return {'skipped': f'already has {armor}'}
        self.slash('agentGear', kit, wait=0)
        answer = self.wait_for(lambda e: str(e.get('text', '')).startswith('[agentgear]'), 8)
        try:
            return json.loads(answer['text'][len('[agentgear] '):])
        except (TypeError, KeyError, ValueError):
            return {'error': 'no answer (is Core3.AgentGear on?)'}

    def locate(self, text, radius=800, x=None, y=None):
        """The server's object search: the nearest objects (up to 30) whose template, name key or displayed name
        contains text, including inside buildings (then with cell, local x/y/z and building). Each object has
        oid, template, name, key, x, y, z, distance. Bot accounts only (/agentpath find)."""
        args = {'text': text, 'radius': radius}
        if x is not None:
            args.update(x=x, y=y)
        return self.request('find', 15, **args).get('objects', [])

    def tell(self, name, text):
        """A private message (tell) to a character by first name."""
        return self.request('tell', 5, name=name, text=text)

    def missions(self):
        """Mission objects the bot knows: a terminal's list (container = mission bag) and accepted ones
        (container = datapad). Each has type, title, reward, difficulty, start/end/waypoint, target."""
        return self.request('missions', 5).get('missions', [])

    def mission_list(self, terminal, wait=4.0):
        self.request('mission_list', 5, target=terminal)
        time.sleep(wait)
        return self.missions()

    def accept_mission(self, mission, terminal, wait=3.0):
        self.request('mission_accept', 5, target=mission, terminal=terminal)
        return self.idle(wait)

    def posture(self):
        return self.status().get('me', {}).get('posture')

    def recover(self, wait=90):
        """Bring a downed bot back: wait out incapacitation, accept the clone offer if dead.
        Returns (posture before, posture after)."""
        before = after = self.posture()
        deadline = time.time() + wait
        while after in ('incapacitated', 'dead') and time.time() < deadline:
            if after == 'dead':
                pages = [p for p in self.sui_pages().get('pages', []) if 'revive' in json.dumps(p)]
                if pages:
                    self.sui_respond(pages[-1]['page_id'], 0, ['0', '@base_player:revive_title'], wait=8)
            time.sleep(3)
            after = self.posture()
        return before, after


class Group:
    def __init__(self, name, spec):
        self.control = None
        self.name, self.focus = name, spec['focus']
        self.training = spec.get('training', {})  # first name -> skill boxes (/agentskill, test galaxy)
        self.member_names = [m['name'] for m in spec['members']] + [m['name'].split()[0] for m in spec['members']]
        self.checks, self.notes, self.steps = [], [], []
        self.started = time.time()
        self.bots = [Bot(m, self) for m in spec['members']]

    def checkpoint(self):
        if self.control:
            self.control.checkpoint()

    def sleep(self, seconds):
        if self.control:
            self.control.sleep(seconds)
        else:
            time.sleep(seconds)

    def __getitem__(self, first):
        for bot in self.bots:
            if first.lower() in (bot.first.lower(), bot.account.lower()):
                return bot
        raise KeyError(f'{first} is not in group {self.name}')

    @property
    def leader(self):
        return self.bots[0]

    def check(self, label, ok, detail=''):
        """Record a pass/fail check; returns ok."""
        self.checks.append({'label': label, 'ok': bool(ok), 'detail': short(detail, 300),
                            't': round(time.time() - self.started, 1)})
        return bool(ok)

    def note(self, text):
        self.notes.append(short(text, 500))

    def step(self, bot, request, reply):
        self.steps.append({'t': round(time.time() - self.started, 1), 'bot': bot.first, 'request': short(request, 200),
                           'reply': short({k: v for k, v in reply.items() if k != 'reply'}, 300)})

    def parallel(self, *jobs):
        """Run callables at the same time (e.g. one per bot); returns their results (or the exception)."""
        results = [None] * len(jobs)

        def work(i, job):
            try:
                results[i] = job()
            except Exception as exc:  # recorded, not raised, so the other jobs finish
                results[i] = exc
                frames = [f for f in traceback.extract_tb(exc.__traceback__) if 'scenarios' in f.filename]
                where = f' (line {frames[-1].lineno}: {frames[-1].line})' if frames else ''
                self.note(f'ERROR in a parallel job: {type(exc).__name__}: {exc}{where}')

        threads = [threading.Thread(target=work, args=(i, job)) for i, job in enumerate(jobs)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        return results


# ---- commands ----

def groups_from(names, spec):
    chosen = names or list(spec['groups'])
    for name in chosen:
        if name not in spec['groups']:
            raise SystemExit(f'Unknown group {name}; groups: {", ".join(spec["groups"])}')
    return [Group(name, spec['groups'][name]) for name in chosen]


def setup_group(group, city, out):
    lines = []
    for bot in group.bots:
        # A body that outlived its server (the galaxy restarted under it) still runs: log it in afresh.
        if not bot.running() or bot.stale() or bot.status().get('connected') is False:
            result = bot.start()
            if result == 'missing':
                result = bot.start(create=True, wait=150)
                if result != 'created':
                    lines.append(f'{bot.first}: could not create {bot.name}: {result}')
                    continue
                result = bot.start()
            if result != 'ready':
                lines.append(f'{bot.first}: login {result}')
                continue
        status = bot.status()
        if status.get('planet') == 'tutorial':
            bot.slash('newbieSelectStartingLocation', city, wait=0.5)
            bot.wait_for('"scene_start"', 45)
            time.sleep(3)
            status = bot.status()
        before, after = bot.recover()
        if before != after:
            status = bot.status()
        lines.append(f'{bot.first}: {status.get("planet")} {status.get("x", 0):.0f} {status.get("y", 0):.0f}'
                     + (f' ({before} -> {after})' if before != after else ''))
    for bot in group.bots:  # trained characters for this group's role (test-galaxy helper; repeats are harmless)
        boxes = group.training.get(bot.first)
        if boxes and bot.running():
            bot.slash('agentSkill', ' '.join(boxes), wait=0)
            answer = bot.wait_for(lambda e: str(e.get('text', '')).startswith('[agentskill]'), 8)
            lines.append(f'{bot.first}: training ' + (answer['text'][len('[agentskill] '):] if answer else 'no answer'))
    leader = group.leader
    if leader.running():
        for bot in group.bots[1:]:
            if not bot.running() or not bot.oid:
                continue
            leader.slash('invite', target=bot.oid, wait=1.5)
            bot.request('command', 5, name='join', args='', target=0)
            joined = bot.wait_for(lambda e: e.get('event') == 'group_joined' or 'already' in str(e.get('text', '')), 6)
            lines.append(f'{bot.first}: ' + ('grouped with ' + leader.first if joined else
                                              'group join not confirmed: ' + short(bot.messages(), 150)))
    out[group.name] = lines


def cmd_setup(names):
    spec = load_spec()
    groups = groups_from(names, spec)
    out = {}
    threads = [threading.Thread(target=setup_group, args=(g, spec.get('city', 'mos_eisley'), out)) for g in groups]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    for group in groups:
        print(f'== {group.name}')
        for line in out.get(group.name, ['(no output)']):
            print('  ' + line)


def cmd_status(names):
    for group in groups_from(names, load_spec()):
        print(f'== {group.name} — {group.focus}')
        for bot in group.bots:
            if not bot.running():
                print(f'  {bot.first:<7} offline')
                continue
            if bot.stale():
                print(f'  {bot.first:<7} offline (body logged in before the galaxy restarted; setup logs it in again)')
                continue
            s = bot.status()
            if s.get('connected') is False:
                print(f'  {bot.first:<7} offline (body running, server connection lost; setup logs it in again)')
                continue
            me = s.get('me', {})
            ham = me.get('ham', {})
            print(f'  {bot.first:<7} {s.get("planet", "?"):<9} {s.get("x", 0):8.1f} {s.get("y", 0):8.1f} '
                  f'cell {s.get("cell", 0):<12} {me.get("posture", "?"):<14} '
                  f'H{ham.get("health")} A{ham.get("action")} M{ham.get("mind")} lvl {me.get("level")}')


def cmd_stop(names):
    for group in groups_from(names, load_spec()):
        for bot in group.bots:
            bot.stop()
        print(f'{group.name}: stopped')


def cmd_send(name, raw, wait):
    spec = load_spec()
    for group in groups_from([], spec):
        for bot in group.bots:
            if bot.first.lower() == name.lower():
                request = json.loads(raw)
                cmd = request.pop('cmd')
                reply = bot.request(cmd, max(wait, 5) + 90 if cmd in ('move', 'path', 'fight') else max(wait, 5), **request)
                print(short(reply, 2000))
                for event in bot.idle(wait if cmd not in ('move', 'path', 'fight') else 0):
                    if 'reply' not in event:
                        print(short(event, 400))
                return
    raise SystemExit(f'No bot named {name}')


def run_job(path, group_name, spec, results, deadline=None, assignment=None):
    group = Group(group_name, spec['groups'][group_name])
    group.control = RunControl(REPORTS / 'runs', group_name, path.name, deadline)
    group.control.publish('running', 'starting scenario')
    error = None
    if assignment:
        group.note('ASSIGNMENT: ' + json.dumps(assignment, sort_keys=True))
    try:
        module_spec = importlib.util.spec_from_file_location(f'scenario_{path.stem.replace("-", "_")}_{group_name}', path)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        for bot in group.bots:
            if not bot.running():
                raise BotDown(f'{bot.first} is not logged in; run: squad.py setup {group_name}')
        downed = group.parallel(*[lambda b=b: (b.first, b.recover()) for b in group.bots])
        for item in downed:
            if isinstance(item, tuple) and item[1][0] in ('incapacitated', 'dead'):
                group.note(f'before the run {item[0]} was {item[1][0]}; now {item[1][1]}')
        group.checkpoint()
        if assignment and assignment.get('fallback') and 'census' not in path.name and 'crafting' not in path.name and group.leader.status().get('planet') != 'tatooine':
            group.note('BLOCKED: fallback requires Tatooine; Hoth spawn exploration is held')
        else:
            module.run(group)
        group.checkpoint()
    except Exception as exc:
        frames = [f for f in traceback.extract_tb(exc.__traceback__) if f.filename == str(path)]
        where = f' (scenario line {frames[-1].lineno}: {frames[-1].line})' if frames else ''
        error = f'{type(exc).__name__}: {exc}{where}'
    state = ('stopped' if error and error.startswith('RunStopped:') else
             'error' if error or any(n.startswith('ERROR') for n in group.notes) else
             'blocked' if any(n.startswith('BLOCKED') for n in group.notes) else
             'failed' if any(not c['ok'] for c in group.checks) else
             'finished' if group.checks else 'no_checks')
    group.control.publish(state, error or 'scenario ended; bots may remain logged in')
    seconds = round(time.time() - group.started)
    passed = sum(c['ok'] for c in group.checks)
    stamp = datetime.now()
    folder = REPORTS / group_name
    folder.mkdir(parents=True, exist_ok=True)
    report = folder / f'{stamp:%Y%m%d-%H%M%S}-{path.stem}.json'
    report.write_text(json.dumps({
        'group': group_name, 'focus': group.focus, 'scenario': path.name, 'started': f'{stamp:%Y-%m-%d %H:%M:%S}',
        'state': state, 'seconds': seconds, 'passed': passed, 'total': len(group.checks), 'error': error,
        'assignment': assignment,
        'members': {b.first: b.name for b in group.bots}, 'checks': group.checks, 'notes': group.notes,
        'steps': group.steps[-300:], 'events': {b.first: b.history for b in group.bots},
    }, indent=1, ensure_ascii=False, default=str), encoding='utf-8')
    log = folder / 'LOG.md'
    if not log.exists():
        log.write_text(f'# Group {group_name}: run log\n\nFocus: {group.focus}\n\nMembers: '
                       + ', '.join(f'{b.name} ({b.member["profession"]})' for b in group.bots)
                       + '\n\nOne line per scenario run, newest last. Full detail in each JSON report.\n\n', encoding='utf-8')
    failed = [c['label'] for c in group.checks if not c['ok']]
    line = (f'- {stamp:%Y-%m-%d %H:%M} · `{path.name}` · {passed}/{len(group.checks)} checks passed · {seconds} s'
            + (' · ✘ ' + '; '.join(failed) if failed else '') + (f' · error: {short(error, 160)}' if error else '')
            + (' · notes: ' + short(' / '.join(group.notes), 200) if group.notes else '') + f' · [report]({report.name})\n')
    with log.open('a', encoding='utf-8') as stream:
        stream.write(line)
    try:  # the shared timing record (tools/timings.py, Bot-reports/timings.csv)
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        import timings
        timings.add('scenario', f'{path.name}:{group_name}', seconds, f'{passed}/{len(group.checks)}', 'error' if error else '')
    except Exception:
        pass
    results[(path.name, group_name)] = (group, error, seconds, report)


KEEP_REPORTS = 20        # newest JSON reports kept loose per group; older ones are zipped by month
LOG_LINES = 300          # LOG.md lines kept; older lines move to LOG-archive.md
KEEP_RUNS = 30           # background-run files kept loose
BODY_LOG_LIMIT = 50 << 20  # a running bot whose body log passes this is logged out and back in (new log)


def cmd_tidy(quiet=False):
    """Keep Bot-reports small and fast to read: zip old reports, rotate long LOG.md files, zip old run files,
    and drop the body logs of bots that are offline."""
    import zipfile
    said = []
    for folder in sorted(p for p in REPORTS.iterdir() if p.is_dir()) if REPORTS.exists() else []:
        reports = sorted(folder.glob('*.json'))
        old = reports[:-KEEP_REPORTS] if folder.name != 'runs' else []
        if folder.name == 'runs':
            old = sorted(folder.glob('*.txt'))[:-KEEP_RUNS] + sorted(folder.glob('*-summary.md'))[:-KEEP_RUNS]
        for item in old:
            month = item.name[:6] if item.name[:6].isdigit() else 'old'
            with zipfile.ZipFile(folder / f'archive-{month}.zip', 'a', zipfile.ZIP_DEFLATED) as archive:
                archive.write(item, item.name)
            item.unlink()
        if old:
            said.append(f'{folder.name}: zipped {len(old)} old files')
        log = folder / 'LOG.md'
        if log.exists():
            lines = log.read_text(encoding='utf-8').splitlines(keepends=True)
            head = [l for l in lines if not l.startswith('- ')]
            entries = [l for l in lines if l.startswith('- ')]
            if len(entries) > LOG_LINES:
                with (folder / 'LOG-archive.md').open('a', encoding='utf-8') as stream:
                    stream.writelines(entries[:-LOG_LINES])
                log.write_text(''.join(head) + ''.join(entries[-LOG_LINES:]), encoding='utf-8')
                said.append(f'{folder.name}: moved {len(entries) - LOG_LINES} LOG.md lines to LOG-archive.md')
    spec = load_spec()
    for group in groups_from([], spec):
        for bot in group.bots:
            if not bot.running() and bot.log.exists() and bot.log.stat().st_size > (1 << 20):
                bot.log.unlink()
                said.append(f'{bot.first}: removed an old body log')
            rotated = list((bot.dir / 'log' / 'zArchive').glob('core3client-*.log'))  # closed pieces, safe to drop
            if rotated:
                for old in rotated:
                    old.unlink(missing_ok=True)
                said.append(f'{bot.first}: removed {len(rotated)} rotated client logs')
    if not quiet:
        print('\n'.join(said) or 'Already tidy.')
    return said


def relog_heavy(spec, names):
    """Log out and back in any bot whose body log has grown past BODY_LOG_LIMIT (it starts a fresh log)."""
    for name in names:
        group = Group(name, spec['groups'][name])
        for bot in group.bots:
            if bot.running() and bot.log.exists() and bot.log.stat().st_size > BODY_LOG_LIMIT:
                bot.stop()
                print(f'{bot.first}: body log over {BODY_LOG_LIMIT >> 20} MB; relogging')
        if not all(b.running() for b in group.bots):
            out = {}
            setup_group(group, spec.get('city', 'mos_eisley'), out)


def parse_run(args, spec):
    flags = {'--rounds': 1, '--minutes': 0}
    for flag in flags:
        if flag in args:
            flags[flag] = float(args[args.index(flag) + 1])
    paths = [Path(a).resolve() for a in args if a.endswith('.py')]
    chosen = [a for i, a in enumerate(args) if i > 0 and args[i - 1] == '--group']
    jobs = []
    for path in paths:
        if not path.exists():
            raise SystemExit(f'No scenario {path}')
        if chosen:
            jobs += [(path, g) for g in chosen]
        else:
            text = path.read_text(encoding='utf-8')
            names = [g for g in spec['groups'] if f"GROUP = '{g}'" in text or f'GROUP = "{g}"' in text]
            if len(names) != 1:
                raise SystemExit(f'{path.name}: set GROUP = "<name>" in the file, or pass --group')
            jobs.append((path, names[0]))
    groups_used = [g for _, g in jobs]
    if len(set(groups_used)) != len(groups_used):
        raise SystemExit('One scenario per group at a time (they would share the same bots).')
    return jobs, int(flags['--rounds']), flags['--minutes']


def print_round(jobs, results):
    for path, group_name in jobs:
        if (path.name, group_name) not in results:
            print(f'== {group_name} · {path.name} · crashed before reporting')
            continue
        group, error, seconds, report = results[(path.name, group_name)]
        passed = sum(c['ok'] for c in group.checks)
        print(f'== {group_name} · {path.name} · {passed}/{len(group.checks)} passed · {seconds} s')
        for c in group.checks:
            print(f'  {"PASS" if c["ok"] else "FAIL"} {c["label"]}' + (f' — {c["detail"]}' if c['detail'] else ''))
        for n in group.notes:
            print(f'  note: {n}')
        if error:
            print(f'  ERROR {error}')
        print(f'  report: {report.relative_to(OUTPUTS)}')


def write_summary(path, stamp, done, began, jobs, tally, errors):
    lines = [f'# Squad run {stamp}: {done} round(s), {round((time.time() - began) / 60)} min', '']
    for name in sorted({g for _, g in jobs}):
        keys = [k for k in tally if k[0] == name]
        passed = sum(tally[k]['pass'] for k in keys)
        total = passed + sum(tally[k]['fail'] for k in keys)
        lines.append(f'## {name}: {passed}/{total} checks passed')
        for k in sorted(keys):
            t = tally[k]
            if t['fail']:
                lines.append(f'- FAIL {t["fail"]}/{t["pass"] + t["fail"]}: {k[2]} ({k[1]}). Last: {short(t["last_fail"], 160)}')
        steady = [k[2] for k in sorted(keys) if not tally[k]['fail']]
        if steady:
            lines.append(f'- always passed: {"; ".join(steady)}')
        for (g, scenario, text), count in sorted(errors.items()):
            if g == name:
                lines.append(f'- {count}x {text} ({scenario})')
        lines.append('')
    summary = '\n'.join(lines)
    path.write_text(summary, encoding='utf-8')
    return summary


def cmd_run(args):
    """Run scenarios together, optionally repeated: --rounds N, and/or --minutes M (no new round after M
    minutes). Offline bots are logged back in between rounds. --detach runs it in the background."""
    spec = load_spec()
    jobs, rounds, minutes = parse_run(args, spec)
    runs = REPORTS / 'runs'
    runs.mkdir(parents=True, exist_ok=True)
    if '--detach' in args:
        stamp = f'{datetime.now():%Y%m%d-%H%M%S}'
        log = runs / f'{stamp}.txt'
        rest = [a for a in args if a != '--detach']
        child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), 'run', *rest, '--stamp', stamp],
                                 stdout=open(log, 'w', encoding='utf-8'), stderr=subprocess.STDOUT,
                                 start_new_session=True, cwd=os.getcwd())
        print(f'Running in the background (pid {child.pid}). Progress: {log.relative_to(OUTPUTS)}')
        print(f'Summary (rewritten after every round): {(runs / (stamp + "-summary.md")).relative_to(OUTPUTS)}')
        print('squad.py last prints it; squad.py halt stops after the current round.')
        return
    stamp = args[args.index('--stamp') + 1] if '--stamp' in args else f'{datetime.now():%Y%m%d-%H%M%S}'
    active = runs / 'ACTIVE'
    try:
        other = int(active.read_text().split()[0])
        if other != os.getpid() and Path(f'/proc/{other}').exists():
            raise SystemExit(f'A background run (pid {other}) is using the bots. squad.py last shows its progress; '
                             'squad.py halt requests a cooperative stop.')
    except (OSError, ValueError, IndexError):
        pass
    active.write_text(f'{os.getpid()} {stamp}\n')
    stop_file = runs / 'STOP'
    stop_file.unlink(missing_ok=True)
    began, tally, errors, done = time.time(), {}, {}, 0
    summary = "No rounds completed."
    deadline = time.monotonic() + minutes * 60 if minutes else None
    main_jobs = list(jobs)
    fallback_file = HERE / 'fallback-plan.json'
    fallback_plan = json.loads(fallback_file.read_text(encoding='utf-8')) if fallback_file.exists() else {}
    state_file = runs / 'fallback-state.json'
    try:
        chooser = Chooser(json.loads(state_file.read_text(encoding='utf-8')))
    except (OSError, ValueError):
        chooser = Chooser()
    while True:
        if done >= rounds and not (minutes and time.time() - began < minutes * 60):
            break
        if minutes and time.time() - began >= minutes * 60:
            break
        if stop_file.exists():
            print('halt requested; stopping')
            stop_file.unlink(missing_ok=True)
            break
        if done:  # keep files small, then bring back anyone who dropped
            if done % 5 == 0:
                cmd_tidy(quiet=True)
            relog_heavy(spec, sorted({g for _, g in jobs}))
            for name in sorted({g for _, g in jobs}):
                group = Group(name, spec['groups'][name])
                if not all(b.running() for b in group.bots):
                    out = {}
                    setup_group(group, spec.get('city', 'mos_eisley'), out)
                    print(f'round {done + 1}: re-setup {name}: ' + ' / '.join(out.get(name, [])))
        results = {}
        assignments = {}
        jobs = []
        for main, name in main_jobs:
            if '--no-fallback' in args:
                path, assignment = main, None
            else:
                candidates = [HERE / 'scenarios' / f for f in fallback_plan.get(name, [])]
                path, assignment = chooser.select(name, main, candidates)
            jobs.append((path, name))
            assignments[name] = assignment
        round_minutes = float(args[args.index('--round-minutes') + 1]) if '--round-minutes' in args else 10.0
        if round_minutes <= 0:
            raise SystemExit('--round-minutes must be positive')
        round_deadline = time.monotonic() + round_minutes * 60
        if deadline is not None:
            round_deadline = min(deadline, round_deadline)
        threads = [threading.Thread(target=run_job, args=(p, g, spec, results, round_deadline, assignments[g])) for p, g in jobs]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        done += 1
        if rounds > 1 or minutes:
            print(f'\n######## round {done} · {datetime.now():%H:%M} · {round((time.time() - began) / 60)} min so far')
        print_round(jobs, results)
        for (scenario, group_name), (group, error, seconds, report) in results.items():
            if assignments[group_name] is not None:
                record = json.loads(report.read_text(encoding='utf-8'))
                change = chooser.observe(group_name, record)
                if change:
                    record['next_assignment'] = change
                    report.write_text(json.dumps(record, indent=1, ensure_ascii=False, default=str), encoding='utf-8')
                    line = f'- {datetime.now():%Y-%m-%d %H:%M} {group_name}: `{change["previous"]}` -> `{change["next"]}`: {change["reason"]}\n'
                    with (REPORTS / group_name / 'LOG.md').open('a', encoding='utf-8') as stream:
                        stream.write(line)
                    print('  NEXT ' + line.strip())
                with (REPORTS / 'fallback-coverage.md').open('a', encoding='utf-8') as stream:
                    stream.write(f'- {datetime.now():%Y-%m-%d %H:%M} {group_name}: `{scenario}` — '
                                 f'{record["state"]}, {record["passed"]}/{record["total"]}; '
                                 f'[report]({group_name}/{report.name})\n')
            for c in group.checks:
                entry = tally.setdefault((group_name, scenario, c['label']), {'pass': 0, 'fail': 0, 'last_fail': ''})
                entry['pass' if c['ok'] else 'fail'] += 1
                if not c['ok']:
                    entry['last_fail'] = c['detail']
            problems = ([error[:200]] if error else []) + [n[:200] for n in group.notes
                                                           if n.startswith('BLOCKED') or n.startswith('ERROR')]
            for text in problems:
                errors[(group_name, scenario, text)] = errors.get((group_name, scenario, text), 0) + 1
        summary = write_summary(runs / f'{stamp}-summary.md', stamp, done, began, jobs, tally, errors)
        if '--no-fallback' not in args:
            temporary = state_file.with_suffix('.tmp')
            temporary.write_text(json.dumps(chooser.state, indent=2), encoding='utf-8')
            temporary.replace(state_file)
        sys.stdout.flush()
    active.unlink(missing_ok=True)
    if rounds > 1 or minutes:
        print('\n' + summary)


def main():
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    command, rest = args[0], args[1:]
    if command == 'accounts':
        accounts = ['agent01'] + [m['account'] for g in load_spec()['groups'].values() for m in g['members']]
        print('AgentAccounts={' + ','.join(f'"{a}"' for a in accounts) + '}')
    elif command == 'galaxy':
        accounts = ['agent01'] + [m['account'] for g in load_spec()['groups'].values() for m in g['members']]
        value = 'AgentAccounts={' + ','.join(f'"{a}"' for a in accounts) + '}'
        print('# As root inside Debian. Restoring wipes characters made after the newest backup; squad.py setup remakes them.')
        print(f'python3 {TEST_GALAXY} stop')
        print(f"python3 {TEST_GALAXY} start --dev-server --config '{value}' --config 'AgentGear=true'")
    elif command == 'setup':
        cmd_setup(rest)
    elif command == 'status':
        cmd_status(rest)
    elif command == 'stop':
        cmd_stop(rest)
    elif command == 'send':
        cmd_send(rest[0], rest[1], float(rest[2]) if len(rest) > 2 else 3)
    elif command == 'run':
        cmd_run(rest)
    elif command == 'tidy':
        cmd_tidy()
    elif command == 'activity':
        rows = read_activity(REPORTS / 'runs')
        print(json.dumps(rows, indent=2) if rows else 'No activity records; current bot activity unknown.')
    elif command == 'halt':
        (REPORTS / 'runs').mkdir(parents=True, exist_ok=True)
        (REPORTS / 'runs' / 'STOP').write_text('cooperative stop requested\n')
        print('Stop requested; cooperative waits stop promptly, outstanding body commands must finish.')
    elif command == 'last':
        runs = sorted((REPORTS / 'runs').glob('*-summary.md'))
        print(runs[-1].read_text(encoding='utf-8') if runs else 'No runs yet.')
    else:
        raise SystemExit(__doc__)


if __name__ == '__main__':
    main()
