"""Follow the owner's test-galaxy session (14 Oct 2026, Claude). Inside Debian, as root:

    python3 -u watch_test_session.py

Tails the running test galaxy's log/player.log, log/admin/admin.log and log/core3.log and prints one short line per event
worth a look: player log lines (logins, zone changes, link-dead), staff commands, and core3 errors (ERROR, FATAL, Lua
errors, stack traces), plus any core3 line naming a character seen in player.log. Repeats of the same message within
two minutes are folded into a count. Prints nothing else, so it can feed a chat monitor. Account ids and IPs are not
printed. Running it also keeps a WSL session open, so Windows does not stop the idle Linux side under the server.
"""
import json, os, re, subprocess, sys, time

LOG = '/opt/swg/testgalaxy/Core3/MMOCoreORB/bin/log'
FILES = [f'{LOG}/player.log', f'{LOG}/admin/admin.log', f'{LOG}/core3.log']
ERROR = re.compile(r'\b(ERROR|FATAL)\b|[Ll]ua error|StackTrace|[Ee]xception|[Ss]egmentation|assert', re.I)
NOISE = re.compile(r'could not open lua derv|ship_chassis_player_.*not found', re.I)
IP = re.compile(r'\b\d{1,3}(\.\d{1,3}){3}\b')

names = set()
last = {}  # message -> (time, folded count)


def say(text):
    text = IP.sub('<ip>', text)[:300]
    now = time.monotonic()
    seen, count = last.get(text, (0.0, 0))
    if now - seen < 120:
        last[text] = (seen, count + 1)
        return
    last[text] = (now, 0)
    extra = f'  [+{count} more of this line since it was last shown]' if count else ''
    print(time.strftime('%H:%M:%S ') + text + extra, flush=True)


def handle(path, line):
    line = line.strip()
    if not line:
        return
    if path.endswith('player.log'):
        try:
            event = json.loads(line)
        except ValueError:
            return
        name = event.get('first_name') or '?'
        names.add(name)
        say(f"player {name}: {event.get('log', '')}")
    elif path.endswith('admin.log'):
        match = re.search(r'\[AdminCommands\] \w+ - (.*)', line)
        say('staff: ' + (match.group(1) if match else line))
    else:
        if NOISE.search(line):
            return
        body = re.sub(r'^.*?\(\d+ s\) (Thread \d+ - )?', '', line)
        if ERROR.search(line):
            say('server: ' + body)
        elif names and any(n in line for n in names):
            say('server: ' + body)


def main():
    for path in FILES:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, 'a').close()
    tail = subprocess.Popen(['tail', '-n0', '-F'] + FILES, stdout=subprocess.PIPE, text=True, errors='replace')
    current = FILES[-1]
    print(time.strftime('%H:%M:%S ') + 'watching the test galaxy logs', flush=True)
    for line in tail.stdout:
        header = re.match(r'==> (.*) <==', line)
        if header:
            current = header.group(1)
            continue
        handle(current, line)


if __name__ == '__main__':
    sys.exit(main())
