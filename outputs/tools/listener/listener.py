"""Input listener for the owner's own SWGEmu client (Claude, 15 Oct 2026; owner's request: "a listener for my
character/client that the main chat can tell what to do ... tracks my inputs on my keys and in game ONLY while im
logged into the client"). Windows Python, standard library only; nothing is installed and nothing leaves this PC.

    python -I listener.py setup              # once: read the owner's character names from the client's character list
    python -I listener.py start | stop       # the recorder runs in the background (no window); there is no autostart
    python -I listener.py pause | resume     # hold off without stopping
    python -I listener.py status             # running? gate open or closed, and why
    python -I listener.py summary [--minutes 10]   # what the owner did: keys, clicks, typing, where
    python -I listener.py tail [N]           # the last N events, readable
    python -I listener.py mark "boss fight"  # a note in the log
    python -I listener.py forget             # delete everything recorded

WHEN IT LISTENS. The recorder reads NO key or mouse state unless all of these hold, and checks them continuously:
  1. the SWGEmu client window is the front window (any other program in front: nothing is read);
  2. the server's player list (log/who.json of the test or the live galaxy, rewritten on every login and logout)
     shows one of the owner's characters online, and that file is fresh;
  3. no PAUSE or STOP file in Agent/listener/.
Anything unreadable or unclear closes the gate. At the login and character-select screens no character is online, so
nothing is read there and a password is never recorded.

WHAT IT WRITES (Agent/listener/events-<day>-<hour>.jsonl, kept 48 hours, gitignored, local): each key press with its name
and how long it was held, mouse buttons with the position inside the window, the character's zone and position from the
player list, and gate open/close times. It never writes window titles, other programs, screenshots or typed text: after
Enter (chat) or / (a slash command) the letters, digits and punctuation are only counted, and so is any run of typing-like
letters and punctuation (six presses, four different keys, under 1.2 s apart; digits and F-keys are exempt so hotbar use
is kept). Letters are held back for 7 s before writing so such a run can be recognised first. Known limit: typing slower
than 1.2 s per key outside chat would be written key by key, which is why the gate above is the real protection.

This is an exception to live_map.py's rule that the owner is never logged: it exists because the owner asked for it.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUTS = HERE.parent.parent
DATA = OUTPUTS / 'Agent' / 'listener'
CONFIG = HERE / 'listener-config.json'
CHARACTER_LIST = OUTPUTS / 'SWG-client' / 'characterlist_owner.txt'
GROUPS = OUTPUTS / 'tools' / 'bots' / 'groups.json'
DEFAULTS = {
    'characters': [],                       # first names of the owner's characters (made by `setup`; gitignored)
    'client_exes': ['swgemu.exe'],
    'who_files': [r'\\wsl.localhost\Debian\opt\swg\testgalaxy\Core3\MMOCoreORB\bin\log\who.json',
                  r'\\wsl.localhost\Debian\opt\swg\Core3\MMOCoreORB\bin\log\who.json'],
    'who_max_age_s': 400,                   # live galaxy rewrites it every 300 s and on every login/logout
    'keep_hours': 48,
    'movement_keys': [],    # keys NOT counted towards the typing-like rule, e.g. ["W","A","S","D"] if fast strafing is
                            # being mistaken for typing; none by default, because a password made of those letters
                            # would then be written out
}
POLL_S, FG_S, WHO_S, STATE_S = 0.02, 0.25, 2.0, 2.0
HOLD_S, BURST_N, BURST_DISTINCT, BURST_GAP_S = 7.0, 6, 4, 1.2
IDLE_EXPLICIT_S, IDLE_IMPLICIT_S = 20.0, 3.0

LETTERS = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
DIGITS = set('0123456789')
VK_NAMES = {0x01: 'MouseLeft', 0x02: 'MouseRight', 0x04: 'MouseMiddle', 0x08: 'Backspace', 0x09: 'Tab', 0x0D: 'Enter',
            0x10: 'Shift', 0x11: 'Ctrl', 0x12: 'Alt', 0x1B: 'Esc', 0x20: 'Space', 0x21: 'PageUp', 0x22: 'PageDown',
            0x23: 'End', 0x24: 'Home', 0x25: 'Left', 0x26: 'Up', 0x27: 'Right', 0x28: 'Down', 0x2D: 'Insert',
            0x2E: 'Delete', 0xBA: 'Semicolon', 0xBB: 'Equals', 0xBC: 'Comma', 0xBD: 'Minus', 0xBE: 'Period',
            0xBF: 'Slash', 0xC0: 'Backtick', 0xDB: 'LBracket', 0xDC: 'Backslash', 0xDD: 'RBracket', 0xDE: 'Quote'}
VK_NAMES.update({0x30 + i: str(i) for i in range(10)})
VK_NAMES.update({0x41 + i: chr(0x41 + i) for i in range(26)})
VK_NAMES.update({0x60 + i: f'Num{i}' for i in range(10)})
VK_NAMES.update({0x70 + i: f'F{i + 1}' for i in range(12)})
PUNCT = {'Semicolon', 'Equals', 'Comma', 'Minus', 'Period', 'Slash', 'Backtick', 'LBracket', 'Backslash', 'RBracket',
         'Quote'}
TYPED = LETTERS | DIGITS | PUNCT | {'Space', 'Backspace'} | {f'Num{i}' for i in range(10)}
WATCHED = sorted(VK_NAMES)                  # the key codes the poller asks about (never the whole keyboard blindly)


def now_s():
    return time.time()


def load_config(path=None):
    path = CONFIG if path is None else path
    cfg = dict(DEFAULTS)
    try:
        cfg.update(json.loads(path.read_text(encoding='utf-8')))
    except (OSError, ValueError):
        pass
    return cfg


# ---------------------------------------------------------------- redaction: what may be written
class Redactor:
    """Turns raw key/mouse events into the events that are allowed in the log (see the module note). Pure: no clock,
    no files. feed() takes {'t', 'kind': 'down'|'up', 'k', optional 'x', 'y'}; tick(now) releases held-back events and
    ends idle typing; flush(now) is for the gate closing."""

    def __init__(self, movement=DEFAULTS['movement_keys']):
        self.burst_keys = (LETTERS | PUNCT) - set(movement)
        self.holds, self.pending, self.typing = {}, [], None

    def _press(self, t, k, held_ms, x=None, y=None):
        ev = {'t': round(t, 3), 'k': k, 'ms': held_ms}
        if x is not None:
            ev.update(x=x, y=y)
        return ev

    def _end_typing(self, now, how):
        typing, self.typing = self.typing, None
        return [{'t': round(typing['since'], 3), 'typed': typing['n'], 'ms': round((typing['last'] - typing['since']) * 1000),
                 'end': how}]

    def feed(self, ev):
        t, k, out = ev['t'], ev['k'], []
        if ev['kind'] == 'down':
            if self.typing and k in TYPED:
                self.typing['n'] += 1
                self.typing['last'] = t
            elif self.typing and k in ('Enter', 'Esc'):
                out += self._end_typing(t, 'sent' if k == 'Enter' else 'cancelled')
                out.append(self._press(t, k, 0))
            elif not self.typing and k == 'Enter':          # opens the chat line
                self.typing = {'since': t, 'last': t, 'n': 0, 'explicit': True}
                out.append(self._press(t, k, 0))
            elif not self.typing and k == 'Slash':          # starts a slash command: the text that follows is not kept
                self.typing = {'since': t, 'last': t, 'n': 1, 'explicit': True}
            else:
                self.holds[k] = (t, ev.get('x'), ev.get('y'))
        else:
            held = self.holds.pop(k, None)
            if held:
                press = self._press(held[0], k, round((t - held[0]) * 1000), held[1], held[2])
                if k in self.burst_keys and not self.typing:
                    press['end'] = t
                    out += self._pend(press)
                else:
                    out.append(press)
        return out

    def _pend(self, press):
        """Hold a letter/punctuation press back; if the last few look like typing, turn them into a count."""
        self.pending.append(press)
        run = [press]
        for earlier in reversed(self.pending[:-1]):
            if run[0]['t'] - earlier['t'] > BURST_GAP_S:
                break
            run.insert(0, earlier)
        if len(run) >= BURST_N and len({p['k'] for p in run}) >= BURST_DISTINCT:
            self.pending = [p for p in self.pending if p not in run]
            self.typing = {'since': run[0]['t'], 'last': press['end'], 'n': len(run), 'explicit': False}
        return []

    def tick(self, now):
        out = []
        if self.typing:
            idle = IDLE_EXPLICIT_S if self.typing['explicit'] else IDLE_IMPLICIT_S
            if now - self.typing['last'] > idle:
                out += self._end_typing(now, 'idle')
        keep = []
        for press in self.pending:
            if now - press['end'] >= HOLD_S:
                press = {key: value for key, value in press.items() if key != 'end'}
                out.append(press)
            else:
                keep.append(press)
        self.pending = keep
        return out

    def flush(self, now):
        """The gate closed: keys still held are written as they are; held-back letters and any typing become a count."""
        out = [self._press(t, k, round((now - t) * 1000), x, y) for k, (t, x, y) in self.holds.items()]
        n = len(self.pending) + (self.typing['n'] if self.typing else 0)
        if self.typing:
            out += self._end_typing(now, 'closed')
        elif n:
            out.append({'t': round(now, 3), 'typed': n, 'ms': 0, 'end': 'closed'})
        self.holds, self.pending, self.typing = {}, [], None
        return out


# ---------------------------------------------------------------- the gate: when it may listen
def read_who(paths, characters, now, max_age_s, reader=None):
    """(online, info, why): is one of the owner's characters online in a fresh player list? Core3 replaces who.json by
    deleting and renaming it every couple of seconds, so a missing file is tried again before it counts as unreadable."""
    reader = reader or (lambda path: (json.loads(Path(path).read_text(encoding='utf-8')), Path(path).stat().st_mtime))
    names = {c.lower() for c in characters}
    if not names:
        return False, None, 'no characters configured (run setup)'
    reason = 'player list not readable'
    for path in paths:
        data = None
        for attempt in range(3):
            try:
                data, mtime = reader(path)
                break
            except (OSError, ValueError):
                time.sleep(0.05)
        if data is None:
            continue
        if now - mtime > max_age_s:
            reason = 'player list is stale'
            continue
        for c in data.get('clients', []):
            if str(c.get('firstName', '')).lower() in names and c.get('isOnline', True) is not False:
                return True, {'zone': c.get('zone'), 'x': c.get('worldPositionX'), 'y': c.get('worldPositionY')}, 'online'
        reason = 'no owner character online'
    return False, None, reason


def gate(paused, fg_exe, client_exes, who):
    """(open, why). `who` is read_who()'s answer, or None when it wasn't asked."""
    if paused:
        return False, 'paused'
    if (fg_exe or '').lower() not in [e.lower() for e in client_exes]:
        return False, 'client not in front'
    if not who or not who[0]:
        return False, who[2] if who else 'player list not checked'
    return True, 'client in front, character online'


# ---------------------------------------------------------------- Windows
class WindowsInput:
    """The only code that touches key state. fg_exe() names the front program; key_down(vk) is called only by the
    poller, and the recorder runs the poller only while the gate is open."""

    def __init__(self):
        import ctypes
        from ctypes import wintypes
        self.ct, self.wt = ctypes, wintypes
        self.u32, self.k32 = ctypes.WinDLL('user32', use_last_error=True), ctypes.WinDLL('kernel32', use_last_error=True)
        self.u32.GetAsyncKeyState.argtypes, self.u32.GetAsyncKeyState.restype = [ctypes.c_int], ctypes.c_short
        self.u32.GetForegroundWindow.restype = wintypes.HWND
        self.u32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        self.u32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
        self.u32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        self.k32.OpenProcess.argtypes, self.k32.OpenProcess.restype = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD], wintypes.HANDLE
        self.k32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR,
                                                        ctypes.POINTER(wintypes.DWORD)]
        self.k32.CloseHandle.argtypes = [wintypes.HANDLE]

    def fg_exe(self):
        try:
            hwnd = self.u32.GetForegroundWindow()
            pid = self.wt.DWORD()
            self.u32.GetWindowThreadProcessId(hwnd, self.ct.byref(pid))
            handle = self.k32.OpenProcess(0x1000, False, pid.value)      # PROCESS_QUERY_LIMITED_INFORMATION
            if not handle:
                return ''
            try:
                buf, size = self.ct.create_unicode_buffer(520), self.wt.DWORD(520)
                ok = self.k32.QueryFullProcessImageNameW(handle, 0, buf, self.ct.byref(size))
                return os.path.basename(buf.value).lower() if ok else ''
            finally:
                self.k32.CloseHandle(handle)
        except Exception:
            return ''

    def key_down(self, vk):
        return bool(self.u32.GetAsyncKeyState(vk) & 0x8000)

    def cursor_in_window(self):
        """Cursor position relative to the front window's top-left corner, or (None, None)."""
        try:
            point, rect = self.wt.POINT(), self.wt.RECT()
            self.u32.GetCursorPos(self.ct.byref(point))
            self.u32.GetWindowRect(self.u32.GetForegroundWindow(), self.ct.byref(rect))
            return point.x - rect.left, point.y - rect.top
        except Exception:
            return None, None


class Poller:
    """Edges of the watched keys between two polls. The first poll after a reset only learns what is already held."""

    def __init__(self, platform, vks=WATCHED):
        self.platform, self.vks, self.prev = platform, vks, None

    def reset(self):
        self.prev = None

    def poll(self, t):
        cur = {vk for vk in self.vks if self.platform.key_down(vk)}
        events = []
        if self.prev is not None:
            for vk in sorted(cur - self.prev):
                ev = {'t': t, 'kind': 'down', 'k': VK_NAMES[vk]}
                if vk in (1, 2, 4):
                    ev['x'], ev['y'] = self.platform.cursor_in_window()
                events.append(ev)
            events += [{'t': t, 'kind': 'up', 'k': VK_NAMES[vk]} for vk in sorted(self.prev - cur)]
        self.prev = cur
        return events


# ---------------------------------------------------------------- log files
class EventLog:
    def __init__(self, folder, keep_hours=48):
        self.folder, self.keep_s = Path(folder), keep_hours * 3600
        self.folder.mkdir(parents=True, exist_ok=True)

    def write(self, ev):
        name = time.strftime('events-%Y%m%d-%H.jsonl', time.localtime(ev['t']))
        with (self.folder / name).open('a', encoding='utf-8', newline='') as f:
            f.write(json.dumps(ev, separators=(',', ':')) + '\n')

    def prune(self, now):
        for path in self.folder.glob('events-*.jsonl'):
            try:
                if now - path.stat().st_mtime > self.keep_s:
                    path.unlink()
            except OSError:
                pass

    def read(self, since):
        events = []
        for path in sorted(self.folder.glob('events-*.jsonl')):
            try:
                if path.stat().st_mtime < since:
                    continue
                for line in path.read_text(encoding='utf-8').splitlines():
                    try:
                        ev = json.loads(line)
                    except ValueError:
                        continue          # a half-written last line
                    if ev.get('t', 0) >= since:
                        events.append(ev)
            except OSError:
                pass
        return sorted(events, key=lambda e: e['t'])


# ---------------------------------------------------------------- the recorder
class Recorder:
    def __init__(self, cfg, platform, log, folder=DATA, who_reader=None):
        self.cfg, self.platform, self.log, self.folder, self.who_reader = cfg, platform, log, Path(folder), who_reader
        self.poller, self.redactor = Poller(platform), Redactor(cfg['movement_keys'])
        self.open, self.why, self.fg, self.who = False, 'starting', '', None
        self.last_fg = self.last_who = self.last_state = self.last_pos = None
        self.started = None
        self.counts = Counter()

    def _emit(self, events):
        for ev in events:
            self.log.write(ev)
            self.counts['events'] += 1

    def paused(self):
        return (self.folder / 'PAUSE').exists()

    def stopping(self):
        return (self.folder / 'STOP').exists()

    def step(self, now):
        self.started = self.started or now
        if self.last_fg is None or now - self.last_fg >= FG_S:
            self.fg, self.last_fg = self.platform.fg_exe(), now
        in_front = self.fg.lower() in [e.lower() for e in self.cfg['client_exes']]
        if not in_front:
            self.who, self.last_who = None, None          # nothing is looked up for other programs
        elif self.who is None or now - self.last_who >= WHO_S:
            self.last_who = now
            self.who = read_who(self.cfg['who_files'], self.cfg['characters'], now, self.cfg['who_max_age_s'],
                                self.who_reader)
        was = self.open
        self.open, self.why = gate(self.paused(), self.fg, self.cfg['client_exes'], self.who)
        if self.open and not was:
            self.poller.reset()
            self._emit([{'t': round(now, 3), 'gate': 'open'}])
        elif was and not self.open:
            self._emit(self.redactor.flush(now) + [{'t': round(now, 3), 'gate': 'closed', 'why': self.why}])
            self.poller.reset()
        if self.open:
            for raw in self.poller.poll(now):
                self._emit(self.redactor.feed(raw))
            if self.who and self.who[1] and self.who[1] != self.last_pos:
                self.last_pos = self.who[1]
                self._emit([{'t': round(now, 3), 'pos': self.who[1]}])
            self._emit(self.redactor.tick(now))
        if self.last_state is None or now - self.last_state >= STATE_S:
            self.last_state = now
            self.write_state(now)

    def write_state(self, now):
        state = {'pid': os.getpid(), 't': round(now, 3), 'started': round(self.started or now, 3), 'open': self.open,
                 'why': self.why, 'fg': self.fg, 'events': self.counts['events']}
        tmp = self.folder / 'state.json.tmp'
        tmp.write_text(json.dumps(state), encoding='utf-8')
        tmp.replace(self.folder / 'state.json')

    def close(self, now):
        if self.open:
            self._emit(self.redactor.flush(now) + [{'t': round(now, 3), 'gate': 'closed', 'why': 'listener stopped'}])
            self.open = False
        self.why = 'stopped'
        self.write_state(now)


def run():
    if os.name != 'nt':
        sys.exit('the recorder reads Windows input and runs on Windows')
    cfg = load_config()
    DATA.mkdir(parents=True, exist_ok=True)
    if pid_alive(read_state().get('pid')) and read_state().get('pid') != os.getpid():
        sys.exit('already running')
    (DATA / 'STOP').unlink(missing_ok=True)
    log = EventLog(DATA, cfg['keep_hours'])
    rec = Recorder(cfg, WindowsInput(), log)
    last_prune = 0
    try:
        while not rec.stopping():
            now = now_s()
            rec.step(now)
            if now - last_prune > 3600:
                last_prune = now
                log.prune(now)
            time.sleep(POLL_S)
    finally:
        rec.close(now_s())
        (DATA / 'STOP').unlink(missing_ok=True)


# ---------------------------------------------------------------- the commands
def read_state():
    try:
        return json.loads((DATA / 'state.json').read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


def pid_alive(pid):
    """Is that process running? (os.kill(pid, 0) would END the process on Windows, so it is never used.)"""
    if not pid:
        return False
    if os.name != 'nt':
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    import ctypes
    k32 = ctypes.WinDLL('kernel32', use_last_error=True)
    k32.OpenProcess.restype = ctypes.c_void_p
    handle = k32.OpenProcess(0x1000, False, pid)
    if not handle:
        return False
    code = ctypes.c_ulong()
    k32.GetExitCodeProcess(ctypes.c_void_p(handle), ctypes.byref(code))
    k32.CloseHandle(ctypes.c_void_p(handle))
    return code.value == 259                                         # STILL_ACTIVE


def running(state=None):
    state = read_state() if state is None else state
    return pid_alive(state.get('pid')) and time.time() - state.get('t', 0) < 15


def cmd_setup():
    try:
        lines = CHARACTER_LIST.read_text(encoding='utf-8', errors='replace').splitlines()
    except OSError:
        sys.exit(f'no character list at {CHARACTER_LIST}')
    names = set()
    for line in lines:
        fields = line.split(',')
        if len(fields) >= 2:
            names.add(re.sub(r'\s*\(.*\)\s*$', '', fields[1]).strip().split(' ')[0])
    bots = {'Kael'}
    try:
        for info in json.loads(GROUPS.read_text(encoding='utf-8'))['groups'].values():
            bots |= {m.get('name', '').split(' ')[0] for m in info.get('members', [])}
    except (OSError, ValueError, KeyError):
        pass
    mine = sorted(n for n in names if n and n not in bots)
    cfg = load_config()
    cfg['characters'] = mine
    CONFIG.write_text(json.dumps(cfg, indent=1), encoding='utf-8')
    print(f'{len(mine)} character(s) of yours will open the gate ({len(names) - len(mine)} left out because a bot has '
          'that first name). Saved to tools/listener/listener-config.json, which is not in git; edit "characters" there.')


def cmd_start():
    if running():
        return cmd_status()
    if not load_config()['characters']:
        sys.exit('no characters configured: run `listener.py setup` first')
    exe = Path(sys.executable)
    pythonw = exe.with_name('pythonw.exe')
    flags = 0x00000008 | 0x00000200 | 0x08000000                    # DETACHED_PROCESS | NEW_PROCESS_GROUP | NO_WINDOW
    subprocess.Popen([str(pythonw if pythonw.exists() else exe), '-I', str(Path(__file__).resolve()), 'run'],
                     creationflags=flags, close_fds=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)
    for _ in range(40):
        time.sleep(0.25)
        if running():
            break
    return cmd_status()


def cmd_stop():
    if not running():
        (DATA / 'STOP').unlink(missing_ok=True)
        print('not running')
        return
    (DATA / 'STOP').write_text('stop', encoding='utf-8')
    for _ in range(40):
        time.sleep(0.25)
        if not running():
            print('stopped')
            return
    subprocess.run(['taskkill', '/PID', str(read_state().get('pid')), '/F'], capture_output=True)
    (DATA / 'STOP').unlink(missing_ok=True)
    print('stopped (had to end the process)')


def cmd_status():
    state = read_state()
    if not running(state):
        print('not running' + (' (paused file present)' if (DATA / 'PAUSE').exists() else ''))
        return
    print(f"running (pid {state['pid']}, up {int(time.time() - state['started'])} s); listening: "
          f"{'YES' if state['open'] else 'no'} - {state['why']}; events written: {state['events']}"
          + ('; PAUSED' if (DATA / 'PAUSE').exists() else ''))


def fmt(ev):
    stamp = time.strftime('%H:%M:%S', time.localtime(ev['t']))
    if 'k' in ev:
        where = f" at {ev['x']},{ev['y']}" if ev.get('x') is not None else ''
        return f"{stamp} {ev['k']} held {ev['ms']} ms{where}"
    if 'typed' in ev:
        return f"{stamp} typed {ev['typed']} characters over {ev['ms']} ms ({ev['end']}; text not kept)"
    if 'pos' in ev:
        return f"{stamp} position {ev['pos'].get('zone')} {ev['pos'].get('x')},{ev['pos'].get('y')}"
    if 'gate' in ev:
        return f"{stamp} listening {ev['gate']}" + (f" ({ev['why']})" if ev.get('why') else '')
    return f"{stamp} note: {ev.get('mark')}"


def summarize(events, minutes):
    lines = []
    keys = [e for e in events if 'k' in e]
    opened = sum(1 for e in events if e.get('gate') == 'open')
    lines.append(f'last {minutes:g} min: {len(events)} events, listening opened {opened} time(s)')
    if keys:
        top = Counter(e['k'] for e in keys).most_common(10)
        lines.append('keys pressed: ' + ', '.join(f'{k} x{n}' for k, n in top))
        held = Counter()
        for e in keys:
            held[e['k']] += e['ms']
        lines.append('held longest: ' + ', '.join(f'{k} {ms / 1000:.1f} s' for k, ms in held.most_common(3)))
    clicks = Counter(e['k'] for e in keys if e['k'].startswith('Mouse'))
    if clicks:
        lines.append('mouse: ' + ', '.join(f'{k[5:].lower()} x{n}' for k, n in clicks.items()))
    typed = [e for e in events if 'typed' in e]
    if typed:
        lines.append(f"typing: {len(typed)} time(s), {sum(e['typed'] for e in typed)} characters (text not kept)")
    pos = [e['pos'] for e in events if 'pos' in e]
    if pos:
        lines.append(f"position: {pos[0].get('zone')} {pos[0].get('x')},{pos[0].get('y')} -> "
                     f"{pos[-1].get('zone')} {pos[-1].get('x')},{pos[-1].get('y')}")
    marks = [e['mark'] for e in events if 'mark' in e]
    if marks:
        lines.append('notes: ' + '; '.join(marks[-5:]))
    if not keys and not pos:
        lines.append('nothing recorded in that time (the client was not in front, or no character was online)')
    return lines


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = parser.add_subparsers(dest='cmd', required=True)
    for name in ('setup', 'start', 'stop', 'pause', 'resume', 'status', 'run', 'forget'):
        sub.add_parser(name)
    s = sub.add_parser('summary')
    s.add_argument('--minutes', type=float, default=10)
    t = sub.add_parser('tail')
    t.add_argument('n', nargs='?', type=int, default=20)
    m = sub.add_parser('mark')
    m.add_argument('text')
    args = parser.parse_args(argv)
    DATA.mkdir(parents=True, exist_ok=True)
    log = EventLog(DATA, load_config()['keep_hours'])
    if args.cmd == 'setup':
        cmd_setup()
    elif args.cmd == 'start':
        cmd_start()
    elif args.cmd == 'stop':
        cmd_stop()
    elif args.cmd == 'status':
        cmd_status()
    elif args.cmd == 'pause':
        (DATA / 'PAUSE').write_text('paused', encoding='utf-8')
        print('paused: nothing is read until `resume`')
    elif args.cmd == 'resume':
        (DATA / 'PAUSE').unlink(missing_ok=True)
        print('resumed')
    elif args.cmd == 'summary':
        print('\n'.join(summarize(log.read(time.time() - args.minutes * 60), args.minutes)))
    elif args.cmd == 'tail':
        print('\n'.join(fmt(e) for e in log.read(time.time() - 48 * 3600)[-args.n:]) or 'nothing recorded')
    elif args.cmd == 'mark':
        log.write({'t': round(time.time(), 3), 'mark': args.text[:200]})
        print('noted')
    elif args.cmd == 'forget':
        for path in DATA.glob('events-*.jsonl'):
            path.unlink(missing_ok=True)
        print('everything recorded has been deleted')
    elif args.cmd == 'run':
        run()


if __name__ == '__main__':
    main()
