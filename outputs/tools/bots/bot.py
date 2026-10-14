"""Drive dev core3client bodies against the TEST galaxy (port 46453), one per bot, through FIFOs.
Run inside Debian as swgemu. TEST galaxy only (start it with ../test_galaxy.py; list the bot accounts in
--config 'AgentAccounts={"agent01","bot02","bot03"}' so they can use /agentpath). Each bot is ~12 MB RAM.
New characters land in the skip-tutorial room: send newbieSelectStartingLocation mos_eisley.
Character creation is limited to one per account per hour (a test galaxy restart resets it).


  bot.py NAME init "Firstname"                  make /opt/swg/agent/bots/NAME.json (random password, 0600)
  bot.py NAME start [--create race profession]  log in (optionally creating the character first)
  bot.py NAME send '<json>' [wait_s]            send one command, print @@AGENT lines that arrive
  bot.py NAME stop
NAME "kael" uses /opt/swg/agent/agent-account.json. Credentials are never printed.
"""
import json, os, secrets, subprocess, sys, time
from pathlib import Path

CLIENT = '/opt/swg/Core3-dev/MMOCoreORB/build/dev/src/client/core3client'
BOTS = Path('/opt/swg/agent/bots')


def paths(name):
    run = Path('/var/tmp/swg-bots') / name  # on the WSL disk, not the /tmp RAM disk
    return run, run / 'in', run / 'out.log'


def account(name):
    if name == 'kael':
        return json.loads(Path('/opt/swg/agent/agent-account.json').read_text())
    return json.loads((BOTS / f'{name}.json').read_text())


def lines_from(log, offset):
    data = log.read_bytes()
    return [l[8:] for l in data[offset:].decode('utf-8', 'replace').splitlines() if l.startswith('@@AGENT ')]


def init(name, character):
    BOTS.mkdir(mode=0o700, exist_ok=True)
    path = BOTS / f'{name}.json'
    if path.exists():
        print(f'{path} exists'); return
    path.write_text(json.dumps({'username': name, 'password': secrets.token_urlsafe(18), 'character': character}))
    path.chmod(0o600)
    print(f'created {path} (character {character})')


def start(name, create):
    run, fifo, log = paths(name)
    (run / 'log').mkdir(parents=True, exist_ok=True)
    if not fifo.exists():
        os.mkfifo(fifo)
    acc = account(name)
    host = subprocess.check_output(['hostname', '-I'], text=True).split()[0]
    env = dict(os.environ, CORE3_CLIENT_USERNAME=acc['username'], CORE3_CLIENT_PASSWORD=acc['password'],
               CORE3_CLIENT_LOGINHOST=host, CORE3_CLIENT_LOGINPORT='46453')
    holder = subprocess.Popen(f'exec sleep infinity > {fifo}', shell=True, start_new_session=True,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # don't hold the caller's pipes open
    (run / 'holder').write_text(str(holder.pid))
    args = [CLIENT]
    if create:
        args += ['--create-character', '--char-name', acc['character'], '--char-race', create[0],
                 '--char-profession', create[1]]
    else:
        args += ['--character-firstname', acc['character'].split()[0]]
    args += ['--agent-control']
    body = subprocess.Popen(args, cwd=run, env=env, stdin=open(fifo, 'rb'), stdout=open(log, 'wb'),
                            stderr=subprocess.STDOUT, start_new_session=True)
    (run / 'pid').write_text(str(body.pid))
    for _ in range(120):
        time.sleep(1)
        events = lines_from(log, 0)
        if any('"ready"' in e for e in events):
            time.sleep(8)
            print('\n'.join(e for e in lines_from(log, 0) if '"ready"' in e or 'scene_start' in e or 'sui_page' in e)[:3000])
            return
        if body.poll() is not None:
            break
    print('NOT READY; tail:\n' + log.read_text(errors='replace')[-2500:])


def send(name, cmd, wait):
    run, fifo, log = paths(name)
    offset = len(log.read_bytes())
    try:  # non-blocking: if the body has exited there is no reader and open() would hang
        fd = os.open(fifo, os.O_WRONLY | os.O_NONBLOCK)
    except OSError:
        print('{"ok": false, "error": "body not running"}')
        return
    os.write(fd, (cmd.strip() + '\n').encode())
    os.close(fd)
    time.sleep(wait)
    print('\n'.join(lines_from(log, offset)))


def stop(name):
    run, fifo, log = paths(name)
    try:
        send(name, '{"cmd":"quit"}', 3)
    except Exception:
        pass
    for item in ('holder', 'pid'):
        try:
            os.kill(int((run / item).read_text()), 15)
        except Exception:
            pass


if __name__ == '__main__':
    name, action = sys.argv[1], sys.argv[2]
    if action == 'init':
        init(name, sys.argv[3])
    elif action == 'start':
        start(name, sys.argv[4:6] if '--create' in sys.argv else None)
    elif action == 'send':
        send(name, sys.argv[3], float(sys.argv[4]) if len(sys.argv) > 4 else 3)
    else:
        stop(name)
