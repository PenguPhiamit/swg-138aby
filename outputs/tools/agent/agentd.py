"""SWG agent daemon: keeps the agent character's headless client running between orders.

Runs inside Debian as the swgemu user. Owns one core3client process in --agent-control
mode (the "body"), records every game event, and answers requests on a Unix socket.
The MCP server (mcp_server.py) starts this automatically; it can also be run directly:

    python3 agentd.py            # foreground, logs to /opt/swg/agent/logs/agentd.log
"""
from pathlib import Path
from collections import deque
from datetime import datetime
import json, os, queue, socket, subprocess, threading, time

STATE = Path('/opt/swg/agent')
SOCKET = STATE/'agentd.sock'
ACCOUNT = STATE/'agent-account.json'
# Pinned copy used for play; dev builds land in Core3-dev/.../build/dev and are tested as
# core3client-next before being promoted here (see outputs/tools/agent/README.md).
CLIENT = STATE/'bin'/'core3client'
OUTPUTS = Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs')
EVENT_LOG_DIR = OUTPUTS/'Agent'/'logs'
PREFIX = '@@AGENT '

lock = threading.Lock()
events = deque(maxlen=5000)
seq = 0
pending = {}
next_id = 0
body = None
ready = threading.Event()
started_at = None


def log(message):
    with (STATE/'logs'/'agentd.log').open('a') as stream:
        stream.write(f'{datetime.now():%Y-%m-%d %H:%M:%S} {message}\n')


def record(event):
    global seq
    with lock:
        seq += 1
        event = {'seq': seq, 'time': datetime.now().strftime('%H:%M:%S'), **event}
        events.append(event)
    EVENT_LOG_DIR.mkdir(parents=True, exist_ok=True)
    with (EVENT_LOG_DIR/f'events-{datetime.now():%Y-%m-%d}.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + '\n')


def read_body(process):
    with (STATE/'logs'/'body.log').open('a', errors='replace') as raw:
        for line in process.stdout:
            if not line.startswith(PREFIX):
                raw.write(line)
                continue
            try:
                message = json.loads(line[len(PREFIX):])
            except ValueError:
                continue
            if 'reply' in message and isinstance(message.get('id'), int):
                waiter = pending.pop(message['id'], None)
                if waiter is not None:
                    waiter.put(message)
                    continue
            if message.get('event') == 'ready':
                ready.set()
            if 'event' in message:
                record(message)
    record({'event': 'body_exited', 'code': process.wait()})
    ready.clear()


def running():
    return body is not None and body.poll() is None


def connect():
    global body, started_at
    if running():
        return {'ok': True, 'already_connected': True}
    account = json.loads(ACCOUNT.read_text())
    host = subprocess.check_output(['hostname', '-I'], text=True).split()[0]
    env = dict(os.environ, CORE3_CLIENT_USERNAME=account['username'],
               CORE3_CLIENT_PASSWORD=account['password'], CORE3_CLIENT_LOGINHOST=host)
    (STATE/'log').mkdir(exist_ok=True)
    ready.clear()
    body = subprocess.Popen([str(CLIENT), '--character-firstname', account['character'], '--agent-control'],
                            cwd=STATE, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, bufsize=1)
    started_at = time.time()
    threading.Thread(target=read_body, args=(body,), daemon=True).start()
    log(f'body started for {account["character"]} (pid {body.pid})')
    if not ready.wait(90):
        return {'ok': False, 'error': 'the character did not finish zoning in within 90 s; is the galaxy running?'}
    time.sleep(8)  # let nearby objects and their names finish arriving
    return {'ok': True, 'character': account['character']}


def send(cmd, timeout):
    global next_id
    if not running() or not ready.is_set():
        return {'ok': False, 'error': 'not connected; call connect first'}
    with lock:
        next_id += 1
        request_id = next_id
    waiter = queue.Queue()
    pending[request_id] = waiter
    body.stdin.write(json.dumps({**cmd, 'id': request_id}) + '\n')
    body.stdin.flush()
    try:
        return waiter.get(timeout=timeout)
    except queue.Empty:
        pending.pop(request_id, None)
        return {'ok': False, 'error': f'no reply within {timeout} s'}


def disconnect():
    if not running():
        return {'ok': True, 'already_disconnected': True}
    send({'cmd': 'quit'}, 10)
    try:
        body.wait(30)
    except subprocess.TimeoutExpired:
        body.kill()
    return {'ok': True}


def handle(request):
    op = request.get('op')
    if op == 'connect':
        return connect()
    if op == 'disconnect':
        return disconnect()
    if op == 'body':
        return send(request['cmd'], float(request.get('timeout', 30)))
    if op == 'events':
        since, limit = int(request.get('since', 0)), int(request.get('limit', 50))
        with lock:
            selected = [e for e in events if e['seq'] > since][-limit:]
            last = seq
        return {'ok': True, 'events': selected, 'last_seq': last}
    if op == 'state':
        return {'ok': True, 'connected': running() and ready.is_set(), 'last_seq': seq,
                'uptime_seconds': round(time.time() - started_at) if started_at and running() else 0}
    return {'ok': False, 'error': f'unknown op {op}'}


def serve(connection):
    with connection:
        data = b''
        while not data.endswith(b'\n'):
            chunk = connection.recv(65536)
            if not chunk:
                return
            data += chunk
        try:
            reply = handle(json.loads(data))
        except Exception as error:  # report, never crash the daemon
            reply = {'ok': False, 'error': f'{type(error).__name__}: {error}'}
        connection.sendall((json.dumps(reply, ensure_ascii=False) + '\n').encode())


def main():
    (STATE/'logs').mkdir(parents=True, exist_ok=True)
    if SOCKET.exists():
        SOCKET.unlink()
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(str(SOCKET))
    os.chmod(SOCKET, 0o600)
    server.listen(8)
    log('agentd listening')
    while True:
        connection, _ = server.accept()
        threading.Thread(target=serve, args=(connection,), daemon=True).start()


if __name__ == '__main__':
    main()
