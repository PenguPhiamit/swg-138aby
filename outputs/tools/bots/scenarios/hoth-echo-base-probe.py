"""H1 probe (Claude, 18 Oct 2026; board row H1, owner 7:55 AM: Echo Base's building doesn't draw): does the server send
the Echo Base building to a client standing at it? One Esk bot jumps (/agentgear goto) to the building's origin and to
the main door, and lists every object whose name mentions Echo Base. Changes nothing in the world.

Read the result by name, not by type: Core3 sends every building's baseline 3 as TangibleObjectMessage3 with the TANO
tag (BuildingObjectImplementation::sendBaselinesTo), so the agent client labels buildings TANO, never BUIO.
Run 31b (9:07 AM): the building ('@building_name:echo_base_n') is sent at the origin and not from the main door, 344 m
away, where only the NPCs near the door are."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import escort  # noqa: E402

GROUP = 'Esk'
FOCUS = 'H1: is the Echo Base building sent to a client at its origin and at the main door'

SPOTS = [('origin', -5113, 5097), ('main door', -5051, 5440)]
BUILDING_NAME = '@building_name:echo_base_n'


def short(o):
    keep = {k: o[k] for k in ('oid', 'name', 'type', 'template', 'crc', 'x', 'y', 'z', 'cell', 'parent') if k in o}
    return str(keep)


def run(g):
    bot = g.bots[0]
    for label, x, y in SPOTS:
        answer = escort.goto(bot, 'hoth', x, y)
        st = bot.status()
        g.note(f'{label}: goto {answer and answer.get("text")}; at {st.get("x")}, {st.get("y")}')
        echo = [o for o in bot.look(512, '', 400) if 'echo' in str(o).lower()]
        g.note(f'{label}: objects mentioning echo: ' + '; '.join(short(o) for o in echo[:15]))
        g.check(f'{label}: the Echo Base building is sent to the client',
                any(o.get('name') == BUILDING_NAME for o in echo), f'{len(echo)} matches')
