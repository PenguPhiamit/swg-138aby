"""MCP server "swg-agent": game tools for an AI agent playing a character on the local galaxy.

Speaks MCP (JSON-RPC 2.0, newline-delimited) on stdin/stdout. Started by Codex or Claude Code:
    wsl.exe -d Debian -u swgemu -- python3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/agent/mcp_server.py
It forwards to agentd.py (started automatically) over /opt/swg/agent/agentd.sock.
"""
from pathlib import Path
from datetime import datetime
import json, re, socket, subprocess, sys, time

HERE = Path(__file__).resolve().parent
SOCKET = '/opt/swg/agent/agentd.sock'
AGENT_DIR = Path('/mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Agent')
NOTES = AGENT_DIR/'notes'
REPORTS = AGENT_DIR/'reports'
last_seq = 0


def daemon(request, timeout=120):
    for attempt in range(2):
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.connect(SOCKET)
                s.sendall((json.dumps(request) + '\n').encode())
                data = b''
                while not data.endswith(b'\n'):
                    chunk = s.recv(65536)
                    if not chunk:
                        break
                    data += chunk
                return json.loads(data)
        except (FileNotFoundError, ConnectionRefusedError):
            if attempt:
                raise
            subprocess.Popen([sys.executable, str(HERE/'agentd.py')], start_new_session=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            for _ in range(50):
                time.sleep(0.1)
                if Path(SOCKET).exists():
                    break


def with_events(result):
    """Attach game events that happened since the last tool call."""
    global last_seq
    news = daemon({'op': 'events', 'since': last_seq, 'limit': 40})
    last_seq = news.get('last_seq', last_seq)
    if news.get('events'):
        result.setdefault('new_events', []).extend(
            {k: v for k, v in e.items() if k != 'seq'} for e in news['events'])
    return result


def body(cmd, timeout=30):
    return with_events(daemon({'op': 'body', 'cmd': cmd, 'timeout': timeout}, timeout + 10))


def safe_name(name):
    name = re.sub(r'[^A-Za-z0-9_-]+', '-', name).strip('-')
    return name or 'general'


def t_connect(a):
    global last_seq
    last_seq = daemon({'op': 'state'}).get('last_seq', last_seq)  # skip earlier sessions' events
    return with_events(daemon({'op': 'connect'}, 130))

def t_disconnect(a):
    return daemon({'op': 'disconnect'}, 60)

def t_status(a):
    state = daemon({'op': 'state'})
    if not state.get('connected'):
        return {'ok': True, 'connected': False, 'hint': 'call connect to log the character in'}
    return body({'cmd': 'status'})

def t_look(a):
    cmd = {'cmd': 'look', 'radius': float(a.get('radius', 64)), 'limit': int(a.get('limit', 40))}
    if a.get('type'):
        cmd['type'] = a['type']
    return body(cmd)

def t_move_to(a):
    return body({'cmd': 'move', 'x': float(a['x']), 'y': float(a['y']), 'speed': float(a.get('speed', 5))}, 100)

def t_say(a):
    return body({'cmd': 'say', 'text': str(a['text'])[:250]})

def t_command(a):
    cmd = {'cmd': 'command', 'name': str(a['name']).lstrip('/'), 'args': str(a.get('args', ''))}
    if a.get('target'):
        cmd['target'] = int(a['target'])
    result = body(cmd)
    time.sleep(1.0)  # give the server a moment so its response shows up in new_events
    return with_events(result)

def t_talk(a):
    result = body({'cmd': 'talk', 'target': int(a['target'])})
    time.sleep(1.0)
    return with_events(result)

def t_choose(a):
    result = body({'cmd': 'choose', 'index': int(a['index'])})
    time.sleep(1.0)
    return with_events(result)

def t_events(a):
    return daemon({'op': 'events', 'since': int(a.get('since', 0)), 'limit': int(a.get('limit', 50))})

def t_wait(a):
    time.sleep(max(0.0, min(float(a.get('seconds', 5)), 60.0)))
    return with_events({'ok': True})

def t_list_notes(a):
    NOTES.mkdir(parents=True, exist_ok=True)
    return {'ok': True, 'notes': sorted(p.stem for p in NOTES.glob('*.md'))}

def t_read_notes(a):
    path = NOTES/f'{safe_name(a["name"])}.md'
    return {'ok': True, 'name': path.stem, 'text': path.read_text(encoding='utf-8') if path.exists() else ''}

def t_write_notes(a):
    NOTES.mkdir(parents=True, exist_ok=True)
    path = NOTES/f'{safe_name(a["name"])}.md'
    path.write_text(str(a['text']), encoding='utf-8')
    return {'ok': True, 'saved': str(path.name)}

def t_report(a):
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS/f'{datetime.now():%Y-%m-%d}.md'
    with path.open('a', encoding='utf-8') as stream:
        stream.write(f'\n## {datetime.now():%H:%M} [{a.get("kind", "note")}] {a["title"]}\n\n{a["text"]}\n')
    return {'ok': True, 'file': path.name}


def schema(properties=None, required=()):
    return {'type': 'object', 'properties': properties or {}, 'required': list(required),
            'additionalProperties': False}

NUM, STR, INT = {'type': 'number'}, {'type': 'string'}, {'type': 'integer'}
TOOLS = {
    'connect': (t_connect, 'Log the agent character (Kael) into the local galaxy and enter the world. Call first. '
                'Takes up to a minute.', schema()),
    'disconnect': (t_disconnect, 'Log the character out (end of a play session).', schema()),
    'status': (t_status, 'Own position (x, y, z height), planet, cell (0 = outdoors), connection, and the '
               'current NPC conversation options.', schema()),
    'look': (t_look, 'Nearby objects sorted by distance: oid, name, type (CREO = creature/NPC/player, '
             'TANO = item/terminal, BUIO = building), x, y, distance. Outdoors only sees outdoor objects.',
             schema({'radius': NUM, 'limit': INT, 'type': STR})),
    'move_to': (t_move_to, 'Walk in a straight line to x, y on the current planet (outdoors only, about '
                '5 m/s, up to 90 s). Waits until arrival. No pathfinding: go around buildings yourself.',
                schema({'x': NUM, 'y': NUM, 'speed': NUM}, ['x', 'y'])),
    'say': (t_say, 'Speak in local (spatial) chat so nearby characters hear it.', schema({'text': STR}, ['text'])),
    'command': (t_command, 'Run any game slash command by name, without the slash. Examples: '
                'name="attack" target=<oid>; name="kneel"; name="sit"; name="stand"; name="peace"; '
                'name="tip" args="<amount>" target=<oid>. Server responses arrive in new_events.',
                schema({'name': STR, 'target': INT, 'args': STR}, ['name'])),
    'talk': (t_talk, 'Start a conversation with an NPC (target = its oid; stand within a few metres). '
             'Its words arrive as npc_says events and the choices as conversation_options.',
             schema({'target': INT}, ['target'])),
    'choose': (t_choose, 'Pick a conversation option by its 0-based index in conversation_options.',
               schema({'index': INT}, ['index'])),
    'events': (t_events, 'Game event history (chat, system messages, NPC speech, creatures leaving view). '
               'Every other tool already returns events that happened since the previous call.',
               schema({'since': INT, 'limit': INT})),
    'wait': (t_wait, 'Pause up to 60 s (e.g. let combat or a conversation play out), then return new events.',
             schema({'seconds': NUM})),
    'list_notes': (t_list_notes, 'List your persistent notebooks (your memory across sessions).', schema()),
    'read_notes': (t_read_notes, 'Read a notebook, e.g. "playbook", "mos-eisley", "the-beginning-quest".',
                   schema({'name': STR}, ['name'])),
    'write_notes': (t_write_notes, 'Replace a notebook with new text (keep it concise and current).',
                    schema({'name': STR, 'text': STR}, ['name', 'text'])),
    'report': (t_report, 'File a test report for the developers: kind = bug | balance | idea | progress.',
               schema({'kind': STR, 'title': STR, 'text': STR}, ['title', 'text'])),
}



def t_inventory(a):
    return body({'cmd': 'inventory'})

def t_radial_menu(a):
    result = body({'cmd': 'radial_menu', 'target': int(a['target'])})
    time.sleep(1)
    return with_events(result)

def t_select_radial(a):
    result = body({'cmd': 'select_radial', 'target': int(a['target']), 'radial_id': int(a['radial_id'])})
    time.sleep(1)
    return with_events(result)

def t_sui_pages(a):
    return body({'cmd': 'sui_pages'})

def t_sui_respond(a):
    result = body({'cmd': 'sui_respond', 'page_id': int(a['page_id']),
                   'event': int(a['event']), 'args': a.get('args', [])})
    time.sleep(1)
    return with_events(result)

def t_mission_list(a):
    result = body({'cmd': 'mission_list', 'target': int(a['target'])})
    time.sleep(1)
    return with_events(result)

TOOLS.update({
    'inventory': (t_inventory, 'Owned inventory/datapad objects from the client containment tree; may include containers.', schema()),
    'radial_menu': (t_radial_menu, 'Request server radial options for an object. Read radial_menu events before choosing.', schema({'target': INT}, ['target'])),
    'select_radial': (t_select_radial, 'Select a radial_id returned by the last menu for this object. Side effects depend on the chosen option.', schema({'target': INT, 'radial_id': INT}, ['target', 'radial_id'])),
    'sui_pages': (t_sui_pages, 'Inspect received pop-up pages and their raw widget commands/subscribed events.', schema()),
    'sui_respond': (t_sui_respond, 'Reply to a received pop-up with an event index and its subscribed string arguments. Inspect the page first.', schema({'page_id': INT, 'event': INT, 'args': {'type': 'array', 'items': STR}}, ['page_id', 'event'])),
    'mission_list': (t_mission_list, 'Request missions from a nearby mission terminal. Structured mission delta decoding is not implemented yet; do not blindly accept missions.', schema({'target': INT}, ['target'])),
})


def respond(message_id, result=None, error=None):
    reply = {'jsonrpc': '2.0', 'id': message_id}
    reply['error' if error else 'result'] = error or result
    sys.stdout.write(json.dumps(reply, ensure_ascii=False) + '\n')
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except ValueError:
            continue
        method, message_id = message.get('method'), message.get('id')
        if message_id is None:
            continue  # notifications (e.g. notifications/initialized)
        params = message.get('params') or {}
        if method == 'initialize':
            respond(message_id, {'protocolVersion': params.get('protocolVersion', '2025-06-18'),
                                 'capabilities': {'tools': {'listChanged': False}},
                                 'serverInfo': {'name': 'swg-agent', 'version': '0.1.0'},
                                 'instructions': 'Play the agent character on the local SWG galaxy. Read '
                                 'outputs/Agent/AGENT-GUIDE.md rules first; call connect, then look/status.'})
        elif method == 'ping':
            respond(message_id, {})
        elif method == 'tools/list':
            respond(message_id, {'tools': [{'name': n, 'description': d, 'inputSchema': s}
                                           for n, (_, d, s) in TOOLS.items()]})
        elif method == 'tools/call':
            name, arguments = params.get('name'), params.get('arguments') or {}
            if name not in TOOLS:
                respond(message_id, error={'code': -32602, 'message': f'unknown tool {name}'})
                continue
            try:
                result = TOOLS[name][0](arguments)
                is_error = not result.get('ok', True)
            except Exception as error:
                result, is_error = {'ok': False, 'error': f'{type(error).__name__}: {error}'}, True
            respond(message_id, {'content': [{'type': 'text', 'text': json.dumps(result, ensure_ascii=False)}],
                                 'isError': is_error})
        else:
            respond(message_id, error={'code': -32601, 'message': f'method not found: {method}'})


if __name__ == '__main__':
    main()
