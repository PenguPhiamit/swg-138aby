"""Fresh-start check (functional-test-plan gap 1): create a new character with the dev core3client, then drive it
through a new player's first minutes. Run inside Debian as swgemu, TEST galaxy only (port 46453).

  fresh_start.py ACCOUNT run NAME RACE PROFESSION CITY [--tutorial] [--existing] --out FILE
                                                                   the whole check; one JSON row appended to FILE
  fresh_start.py ACCOUNT start NAME RACE PROFESSION [--tutorial]   create NAME and log it in (body kept running)
  fresh_start.py ACCOUNT login FIRSTNAME                            log an existing character in
  fresh_start.py ACCOUNT send '<json>' [wait_s]                    one agent command; prints @@AGENT lines
  fresh_start.py ACCOUNT stop
  fresh_start.py ACCOUNT log-offset | log-errors OFFSET            core3.log size now / ERROR lines since OFFSET

ACCOUNT is an existing bot account in /opt/swg/agent/bots (read only; its own character is left alone). RACE is a
player template name such as hutt_male. The options file (with the createCharacter action) and the run directory live
in /var/tmp/swg-freshstart; nothing under /opt/swg is written. Credentials are never printed.
"""
import contextlib, io, json, os, subprocess, sys, time
from pathlib import Path

CLIENT = '/opt/swg/Core3-dev/MMOCoreORB/build/dev/src/client/core3client'
BOTS = Path('/opt/swg/agent/bots')
CORE3_LOG = Path('/opt/swg/testgalaxy/Core3/MMOCoreORB/bin/log/core3.log')
ROOT = Path('/var/tmp/swg-freshstart')


def paths(account):
    run = ROOT / account
    return run, run / 'in', run / 'out.log'


def events(log, offset=0):
    data = log.read_bytes()[offset:]
    return [l[8:] for l in data.decode('utf-8', 'replace').splitlines() if l.startswith('@@AGENT ')]


def launch(account, args, env):
    run, fifo, log = paths(account)
    if not fifo.exists():
        os.mkfifo(fifo)
    holder = subprocess.Popen(f'exec sleep infinity > {fifo}', shell=True, start_new_session=True,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    (run / 'holder').write_text(str(holder.pid))
    body = subprocess.Popen([CLIENT] + args, cwd=run, env=env, stdin=open(fifo, 'rb'), stdout=open(log, 'wb'),
                            stderr=subprocess.STDOUT, start_new_session=True)
    (run / 'pid').write_text(str(body.pid))
    return body


def start(account, name, race, profession, tutorial):
    """Create with the JSON createCharacter action (the only way to choose the tutorial; it logs out once created),
    then log the new character in by first name with agent control."""
    run, fifo, log = paths(account)
    (run / 'log').mkdir(parents=True, exist_ok=True)
    os.chmod(ROOT, 0o700)
    acc = json.loads((BOTS / f'{account}.json').read_text())
    options = run / 'options.json'
    options.write_text(json.dumps({'actions': [{'action': 'createCharacter', 'name': name, 'profession': profession,
                                                'race': f'object/creature/player/{race}.iff',
                                                'skipTutorial': not tutorial}]}))
    options.chmod(0o600)
    host = subprocess.check_output(['hostname', '-I'], text=True).split()[0]
    env = dict(os.environ, CORE3_CLIENT_USERNAME=acc['username'], CORE3_CLIENT_PASSWORD=acc['password'],
               CORE3_CLIENT_LOGINHOST=host, CORE3_CLIENT_LOGINPORT='46453')
    began = time.time()
    body = launch(account, ['--options-json', str(options)], env)
    try:
        body.wait(120)
    except subprocess.TimeoutExpired:
        stop(account)
    stop(account)
    text = log.read_text(errors='replace')
    (run / 'create.log').write_text(text)
    created = [l.strip()[-200:] for l in text.splitlines() if 'Character creation SUCCESS' in l
               or 'creation failed' in l.lower() or 'ClientCreateCharacterFailed' in l or 'Creating character' in l
               or 'Skip Tutorial' in l or 'Race:' in l]
    first = [e for e in events(log) if 'scene_start' in e][:1]
    print(json.dumps({'create_s': round(time.time() - began), 'lines': created, 'first_scene': first}))
    if not any('SUCCESS' in l for l in created):
        print('NOT CREATED; ' + ' / '.join(l.strip()[-200:] for l in text.splitlines()
                                         if ('rror' in l and 'getTemplate' not in l) or 'failed' in l.lower())[-1500:])
        return
    login(account, name.split()[0], env)


def login(account, first, env=None):
    run, fifo, log = paths(account)
    if env is None:
        acc = json.loads((BOTS / f'{account}.json').read_text())
        host = subprocess.check_output(['hostname', '-I'], text=True).split()[0]
        env = dict(os.environ, CORE3_CLIENT_USERNAME=acc['username'], CORE3_CLIENT_PASSWORD=acc['password'],
                   CORE3_CLIENT_LOGINHOST=host, CORE3_CLIENT_LOGINPORT='46453')
    began = time.time()
    body = launch(account, ['--character-firstname', first, '--agent-control'], env)
    while time.time() - began < 150:
        time.sleep(1)
        if any('"ready"' in e for e in events(log)):
            time.sleep(8)
            print(json.dumps({'login_s': round(time.time() - began)}))
            print('\n'.join(e for e in events(log) if 'scene_start' in e or 'ready' in e or 'sui_page' in e)[:3000])
            return
        if body.poll() is not None:
            break
    text = log.read_text(errors='replace')
    print('NOT READY; ' + ' / '.join(l.strip()[-200:] for l in text.splitlines()
                                      if ('rror' in l and 'getTemplate' not in l) or 'failed' in l.lower())[-1500:])


def send(account, cmd, wait):
    run, fifo, log = paths(account)
    offset = len(log.read_bytes())
    try:  # non-blocking: if the body has exited there is no reader and open() would hang
        fd = os.open(fifo, os.O_WRONLY | os.O_NONBLOCK)
    except OSError:
        print('{"ok": false, "error": "body not running"}')
        return
    os.write(fd, (cmd.strip() + '\n').encode())
    os.close(fd)
    time.sleep(wait)
    print('\n'.join(events(log, offset)))


def stop(account):
    run, fifo, log = paths(account)
    try:
        send(account, '{"cmd":"quit"}', 3)
    except Exception:
        pass
    for item, marker in (('pid', b'core3client'), ('holder', b'sleep')):
        try:  # only signal our own processes, never a recycled pid
            pid = int((run / item).read_text())
            if marker in Path(f'/proc/{pid}/cmdline').read_bytes():
                os.kill(pid, 15)
        except (OSError, ValueError):
            pass


def log_errors(offset):
    with open(CORE3_LOG, 'rb') as stream:
        stream.seek(offset)
        for line in stream.read().decode('utf-8', 'replace').splitlines():
            if 'ERROR' in line or 'lock' in line.lower() and 'timeout' in line.lower():
                print(line[:300])


def template_crc(path):
    """The client's object-template CRC (CRC-32, polynomial 0x04C11DB7, not reflected)."""
    crc = 0xFFFFFFFF
    for byte in path.encode():
        crc ^= byte << 24
        for _ in range(8):
            crc = ((crc << 1) ^ 0x04C11DB7) & 0xFFFFFFFF if crc & 0x80000000 else (crc << 1) & 0xFFFFFFFF
    return crc ^ 0xFFFFFFFF


class Body:
    """Commands to a running body; each waits for its own reply line."""

    def __init__(self, account):
        self.run, self.fifo, self.log = paths(account)
        self.offset = len(self.log.read_bytes())

    def new(self):
        rows = []
        for raw in events(self.log, self.offset):
            try:
                rows.append(json.loads(raw))
            except ValueError:
                pass
        self.offset = len(self.log.read_bytes())
        return rows

    def ask(self, wait_s=10, **request):
        self.new()
        fd = os.open(self.fifo, os.O_WRONLY | os.O_NONBLOCK)
        os.write(fd, (json.dumps(request) + '\n').encode())
        os.close(fd)
        seen, deadline = [], time.time() + wait_s
        while time.time() < deadline:
            time.sleep(0.3)
            seen += self.new()
            for row in seen:
                if row.get('reply') == request['cmd']:
                    return row, seen
        return {'ok': False, 'error': f'no reply in {wait_s} s'}, seen

    def wait(self, test, timeout, prior=()):
        """The first row passing test: among prior (rows that arrived with a reply), else within timeout."""
        for row in prior:
            if test(row):
                return row, []
        seen, deadline = [], time.time() + timeout
        while time.time() < deadline:
            time.sleep(0.5)
            seen += self.new()
            for row in seen:
                if test(row):
                    return row, seen
        return None, seen


def sui_text(page):
    return [c['wide'][0] for c in page.get('commands', []) if c.get('kind') == 3 and c.get('wide')][:12]


OTHER_TRAINER = {'outdoors_scout': 'trainer_brawler'}  # a novice box someone new can buy without XP


def run_check(account, name, race, profession, city, tutorial, out, existing=False):
    """One new character through the first minutes; appends one JSON row to OUT. With existing, the character was
    created by an earlier run (one creation per account per hour) and is only logged in again."""
    result = {'account': account, 'name': name, 'race': race, 'profession': profession, 'city': city,
              'tutorial': tutorial, 'existing': existing, 'started': time.strftime('%I:%M:%S %p')}
    log_from = CORE3_LOG.stat().st_size
    run, fifo, log = paths(account)
    try:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            if existing:
                login(account, name.split()[0])
            else:
                start(account, name, race, profession, tutorial)
        text = buf.getvalue()
        result['create'] = text[:1500]
        if ('SUCCESS' not in text and not existing) or '"login_s"' not in text:
            result['fail'] = 'creation or login'
            return result
        body = Body(account)
        status, _ = body.ask(cmd='status')
        me = status.get('self')
        result['landed'] = {k: status.get(k) for k in ('planet', 'x', 'y', 'cell')}
        result['ham'] = status.get('me', {}).get('max_ham')
        result['level'] = status.get('me', {}).get('level')
        result['credits'] = {'cash': status.get('cash_credits'), 'bank': status.get('bank_credits')}
        own, _ = body.ask(cmd='inspect', target=me)
        expected = template_crc(f'object/creature/player/shared_{race}.iff')
        result['species'] = {'crc': own.get('crc'), 'expected': expected, 'match': own.get('crc') == expected,
                             'name': own.get('name')}
        room, _ = body.ask(cmd='look', radius=40)
        result['first_room'] = [o['name'] for o in room.get('objects', [])][:12]
        if tutorial:  # the tutorial is walked by hand (owner); record what a new player meets first
            pages, _ = body.ask(cmd='sui_pages')
            result['tutorial_pages'] = [sui_text(p)[:4] for p in pages.get('pages', [])][:4]
            return result
        if status.get('planet') == 'tutorial':  # the skip-tutorial room: choose the starting city (a,b: b if a fails)
            tries, scene = [], None
            for choice in city.split(','):
                reply, seen = body.ask(cmd='command', name='newbieSelectStartingLocation', args=choice)
                is_scene = lambda r: r.get('event') == 'scene_start'
                scene, more = body.wait(is_scene, 30, seen)
                tries.append({'city': choice, 'scene': scene, 'system': [r.get('text') for r in seen + more
                                                                         if r.get('event') == 'system'][:4]})
                if scene:
                    break
            result['city_move'] = tries
            if not scene:
                return result
            time.sleep(6)
        else:  # moved there by an earlier run
            result['city_move'] = 'earlier run'
        status, _ = body.ask(cmd='status')
        result['in_city'] = {k: status.get(k) for k in ('planet', 'x', 'y', 'cell')}
        home = (status.get('x'), status.get('y'))
        # Helper droid: appears within 60 s; its menu answers.
        began, droid = time.time(), None
        while time.time() - began < 60 and not droid:
            seen, _ = body.ask(cmd='look', radius=40)
            droid = next((o for o in seen.get('objects', []) if 'helper' in o['name']), None)
            if not droid:
                time.sleep(3)
        result['droid'] = {'found_after_s': round(time.time() - began), 'name': droid and droid['name']}
        if droid:
            t0 = time.time()
            _, seen = body.ask(cmd='radial_menu', target=droid['oid'])
            menu, _ = body.wait(lambda r: r.get('event') == 'radial_menu' and r.get('items'), 10, seen)
            result['droid']['menu_s'] = round(time.time() - t0, 2)
            items = (menu or {}).get('items', [])
            result['droid']['menu'] = [i.get('label') for i in items][:12]
            pick = next((i for i in items if 'how_to_travel' in i.get('label', '')), None)
            if pick:
                t0 = time.time()
                _, seen = body.ask(cmd='select_radial', target=droid['oid'], radial_id=pick['radial_id'])
                page, _ = body.wait(lambda r: r.get('event') == 'sui_page', 10, seen)
                result['droid']['answer_s'] = round(time.time() - t0, 2)
                result['droid']['answer'] = page and sui_text(page['page'])[-1:]
        # Trainer: another starter's novice box (the own one came with creation; boxes 2+ need XP).
        key = OTHER_TRAINER.get(profession, 'trainer_scout')
        found, _ = body.ask(wait_s=12, cmd='find', text=key.split('_')[1], radius=700)
        trainers = [o for o in found.get('objects', []) if o.get('key') == key and not o.get('cell')]
        result['trainer'] = {'key': key, 'found': len(trainers)}
        if trainers:
            t = trainers[0]
            result['trainer']['name'] = t['name']
            walk, _ = body.ask(wait_s=95, cmd='move', x=t['x'] + 1.2, y=t['y'] + 0.8)
            body.ask(cmd='move', x=t['x'] + 0.9, y=t['y'] + 0.6)  # one short step: the server validates it
            cash0 = body.ask(cmd='status')[0].get('cash_credits')
            is_opts = lambda r: r.get('event') == 'conversation_options'
            talk, seen = body.ask(cmd='talk', target=t['oid'])
            opts, more = body.wait(is_opts, 6, seen)
            if not opts:  # the server checks the last validated position: one more short step, then again
                body.ask(cmd='move', x=t['x'] + 0.7, y=t['y'] + 0.7)
                talk, seen = body.ask(cmd='talk', target=t['oid'])
                opts, more = body.wait(is_opts, 6, seen)
            steps = [r.get('text') for r in seen + more if r.get('event') == 'npc_says']
            for want in ('opt1_1', '@skl_n:', 'yes'):
                if not opts:
                    break
                index = next((i for i, o in enumerate(opts['options']) if want in o), None)
                if index is None:
                    steps.append(f'no option {want}: {opts["options"]}')
                    break
                if want == '@skl_n:':
                    result['trainer']['box'] = opts['options'][index]
                _, seen = body.ask(cmd='choose', index=index)
                opts, more = body.wait(is_opts, 6, seen)
                steps += [r.get('text') for r in seen + more if r.get('event') in ('npc_says', 'system')]
            cash1 = body.ask(cmd='status')[0].get('cash_credits')
            result['trainer'].update({'walk': walk.get('ok'), 'steps': steps[:8], 'cash': [cash0, cash1],
                                      'learned': any('skill_learned' in (s or '') for s in steps)})
            body.ask(cmd='command', name='npcconversationstop')
        # One fight with the nearest low creature; walk out of town if none is near.
        target = None
        for leg in range(3):
            seen, _ = body.ask(cmd='look', radius=150)
            near = sorted((o for o in seen.get('objects', []) if o['type'] == 'CREO' and
                           o['name'].startswith('@mob/creature_names:') and 'helper' not in o['name']),
                          key=lambda o: o['distance'])
            for candidate in near[:10]:  # a creature at most 8 levels up, not a town NPC (junk dealers are 100)
                level = body.ask(cmd='inspect', target=candidate['oid'])[0].get('creature', {}).get('level', 0)
                if 0 < level <= (result.get('level') or 1) + 8:
                    target = candidate
                    break
            if target:
                break
            x, y = status.get('x'), status.get('y')
            far = body.ask(wait_s=95, cmd='move', x=home[0] + 140 * (leg + 1), y=home[1] - 90 * (leg + 1))[0]
            status = {'x': far.get('x', x), 'y': far.get('y', y)}
        if target:
            fight, seen = body.ask(wait_s=80, cmd='fight', target=target['oid'], timeout=60)
            info = body.ask(cmd='inspect', target=target['oid'])[0]
            result['fight'] = {'target': target['name'], 'level': info.get('creature', {}).get('level'),
                               'reply': {k: v for k, v in fight.items() if k not in ('reply',)}}
            mine = body.ask(cmd='status')[0].get('me', {})
            result['fight']['after'] = {'ham': mine.get('ham'), 'posture': mine.get('posture')}
        else:
            result['fight'] = {'error': 'no creature within 150 m on three legs'}
        inv, _ = body.ask(cmd='inventory')
        result['inventory'] = sorted(i['name'] for i in inv.get('items', []))
        return result
    except Exception as exc:  # report, never leave a body behind
        result['exception'] = repr(exc)
        return result
    finally:
        with contextlib.redirect_stdout(io.StringIO()):
            stop(account)
        errors, noise = [], 0
        with open(CORE3_LOG, 'rb') as stream:
            stream.seek(log_from)
            for line in stream.read().decode('utf-8', 'replace').splitlines():
                if 'ERROR' in line:
                    if 'handleNetStatusRequest' in line:
                        noise += 1
                    else:
                        errors.append(line[:260])
        result['server_errors'] = errors[:20]
        result['server_errors_total'] = len(errors)
        result['netstatus_noise'] = noise
        result['ended'] = time.strftime('%I:%M:%S %p')
        with open(out, 'a') as stream:
            stream.write(json.dumps(result) + '\n')


if __name__ == '__main__':
    account, action = sys.argv[1], sys.argv[2]
    if action == 'run':  # run NAME RACE PROFESSION CITY [--tutorial] --out FILE
        out = sys.argv[sys.argv.index('--out') + 1]
        run_check(account, sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], '--tutorial' in sys.argv, out,
                  '--existing' in sys.argv)
    elif action == 'start':
        start(account, sys.argv[3], sys.argv[4], sys.argv[5], '--tutorial' in sys.argv)
    elif action == 'login':
        login(account, sys.argv[3])
    elif action == 'send':
        send(account, sys.argv[3], float(sys.argv[4]) if len(sys.argv) > 4 else 3)
    elif action == 'log-offset':
        print(CORE3_LOG.stat().st_size)
    elif action == 'log-errors':
        log_errors(int(sys.argv[3]))
    else:
        stop(account)
