"""Stage capability wrappers; does not replace or restart the running MCP server."""
from pathlib import Path
import difflib

ROOT = Path(__file__).resolve().parent
source = (ROOT.parent/'mcp_server.py').read_text(encoding='utf-8-sig')
addition = '''
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

'''
needle = '\ndef respond(message_id, result=None, error=None):'
assert source.count(needle) == 1
staged = source.replace(needle, '\n'+addition+needle, 1)
compile(staged, 'mcp_server.py', 'exec')
(ROOT/'mcp_server.py').write_text(staged, encoding='utf-8')
(ROOT/'mcp-capabilities.patch').write_text(''.join(difflib.unified_diff(source.splitlines(True), staged.splitlines(True),
    fromfile='a/outputs/tools/agent/mcp_server.py', tofile='b/outputs/tools/agent/mcp_server.py')), encoding='utf-8')
scope = {'__name__': 'staged_validation', '__file__': str(ROOT/'mcp_server.py')}
exec(compile(staged, 'staged_mcp_server', 'exec'), scope)
required = {'inventory', 'radial_menu', 'select_radial', 'sui_pages', 'sui_respond', 'mission_list'}
assert required <= scope['TOOLS'].keys()
assert len(scope['TOOLS']) == 21
print('Staged MCP adapter compiles/imports; 21 tools (15 original + 6 new). No connection or deployment performed.')
