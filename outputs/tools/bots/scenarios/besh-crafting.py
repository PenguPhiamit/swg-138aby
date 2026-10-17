"""Besh crafts: the crafting check of functional-test-plan.md section 15 (Claude, 17 Oct 2026).

Two routines other scenarios can reuse:
  resources(g, bot)                                      test-galaxy raw materials (/agentgear resources)
  craft(g, bot, tool, schematic, label, experiment=None) one session from tool to finished item; returns the new item

Part 1: Besh, a novice Artisan, makes a Mineral Survey Device with the generic crafting tool. There is no station,
so there is no experimentation. Checks: the schematic list, every slot filled, assembly, the prototype arriving in the
inventory, and the XP message.
Part 2: the same item with the weapon tool at a weapon crafting station, with one experimentation point. The server
offers experimentation only with a station of the tool's type within 7 m (PlayerManager getNearbyCraftingStation).
No station has the generic tool's type, so the weapon tool is the only way to test it (its tabs include the
Artisan's). Without a station in reach, Part 2 is a BLOCKED note, not a failure.

Body protocol (AgentControl.cpp, 17 Oct): craft_schematics, craft_slots and craft_result events; craft_add and
craft_experiment commands; the rest are queue commands (requestcraftingsession, selectdraftschematic,
nextcraftingstage, createprototype, cancelcraftingsession).
"""
import json

GROUP = 'Besh'
SURVEY_DEVICE = 'object/draft_schematic/item/shared_item_survey_tool_mineral.iff'
CRITICAL_FAILURE = 8  # assembly and experiment results 0-7 are degrees of success (CraftingManager)


def template_crc(path):
    """The client's object-template CRC (CRC-32, polynomial 0x04C11DB7, not reflected)."""
    crc = 0xFFFFFFFF
    for byte in path.encode():
        crc ^= byte << 24
        for _ in range(8):
            crc = ((crc << 1) ^ 0x04C11DB7) & 0xFFFFFFFF if crc & 0x80000000 else (crc << 1) & 0xFFFFFFFF
    return crc ^ 0xFFFFFFFF


def agentgear(bot, kit):
    """/agentgear KIT without gear()'s armor shortcut; the server's JSON answer, or {} when none came."""
    bot.slash('agentGear', kit, wait=0)
    answer = bot.wait_for(lambda e: str(e.get('text', '')).startswith('[agentgear]'), 10)
    try:
        return json.loads(answer['text'][len('[agentgear] '):])
    except (TypeError, KeyError, ValueError):
        return {}


def items(bot, kind=None):
    return [i for i in bot.inventory().get('items', []) if kind is None or kind in str(i.get('name')) or i.get('type') == kind]


def resources(g, bot):
    answer = agentgear(bot, 'resources')
    g.check(f'{bot.first} gets test resources', answer.get('given'), answer)
    bot.idle(2)
    return [i['oid'] for i in items(bot, 'RCNO') if (i.get('units') or 0) > 0]


def result(bot, step, timeout=8):
    return bot.wait_for(lambda e: e.get('event') == 'craft_result' and e.get('step') == step, timeout)


def craft(g, bot, tool, schematic, label, experiment=None):
    """One crafting session. experiment = [[row, points], ...] to experiment after assembly (needs a station)."""
    bot.slash('cancelcraftingsession', wait=1)  # a session left open by an earlier run
    before = {i['oid'] for i in items(bot)}
    bot.slash('requestcraftingsession', target=tool['oid'], wait=0)
    listed = bot.wait_for('"craft_schematics"', 10)
    if not g.check(f'{label}: the tool lists schematics', listed and listed.get('schematics'),
                   listed and f"{len(listed['schematics'])} schematics, station {listed.get('station')}"):
        return None
    want = template_crc(schematic)
    index = next((s['index'] for s in listed['schematics'] if s['crc'] == want), None)
    if not g.check(f'{label}: the Mineral Survey Device is on the list', index is not None,
                   f'crc {want}; tabs {sorted({s["tab"] for s in listed["schematics"]})}'):
        bot.slash('cancelcraftingsession', wait=1)
        return None

    schematics_before = {i['oid'] for i in items(bot, 'MSCO')}
    bot.slash('selectdraftschematic', str(index), wait=2)
    # The server makes a manufacture schematic and waits: the slots come after the client's synchronizeduilisten on
    # it (ManufactureSchematicImplementation::synchronizedUIListen), as the real client does when the window opens.
    made = [i for i in items(bot, 'MSCO') if i['oid'] not in schematics_before] or items(bot, 'MSCO')
    if not g.check(f'{label}: a manufacture schematic is made', made, made[-1:]):
        bot.slash('cancelcraftingsession', wait=1)
        return None
    bot.slash('synchronizeduilisten', '0', target=made[-1]['oid'], wait=0)
    slots = bot.wait_for('"craft_slots"', 10)
    if not g.check(f'{label}: the schematic opens with its slots', slots and slots.get('slot_count'),
                   slots and [(s['name'], s['resource'], s['quantity']) for s in slots.get('slots', [])]):
        bot.slash('cancelcraftingsession', wait=1)
        return None

    containers = [i['oid'] for i in items(bot, 'RCNO') if (i.get('units') or 0) > 0]
    filled = 0
    for slot in range(slots['slot_count']):
        for oid in containers:  # the server says which container fits: code 0 is IngredientSlot::OK
            bot.request('craft_add', 5, target=oid, slot=slot)
            answer = result(bot, 'ingredient', 5)
            if answer and answer.get('code') == 0:
                filled += 1
                break
    if not g.check(f'{label}: every slot filled', filled == slots['slot_count'], f'{filled} of {slots["slot_count"]}'):
        bot.slash('cancelcraftingsession', wait=1)
        return None

    stage = 0
    bot.slash('nextcraftingstage', str(stage := stage + 1), wait=0)
    assembly = result(bot, 'assembly', 10)
    g.check(f'{label}: assembly succeeds', assembly and assembly.get('code') != CRITICAL_FAILURE, assembly)

    if experiment:
        bot.request('craft_experiment', 5, rows=experiment)
        tried = result(bot, 'experiment', 10)
        g.check(f'{label}: an experiment result comes back', tried and tried.get('code') != CRITICAL_FAILURE, tried)
        bot.slash('nextcraftingstage', str(stage := stage + 1), wait=2)  # leave experimentation
    bot.slash('nextcraftingstage', str(stage := stage + 1), wait=2)      # customization, then the finish stage

    bot.slash('createprototype', f'{stage + 1} 1', wait=0)
    made = bot.wait_for(lambda e: 'prototype_transferred' in str(e.get('text', '')), 40)
    xp = [e.get('text') for e in bot.idle(2) if e.get('event') == 'system' and 'xp' in str(e.get('text', '')).lower()]
    g.check(f'{label}: the prototype arrives', made, made and made.get('text'))
    new = [i for i in items(bot) if i['oid'] not in before and 'survey_tool_mineral' in str(i.get('name'))]
    g.check(f'{label}: a new survey device is in the inventory', new, new[:1])
    g.check(f'{label}: crafting XP is granted', xp, xp[:2])
    return new[0] if new else None


def weapon_station(bot):
    for text in ('weapon_station', 'weapon station'):
        found = [o for o in bot.locate(text, 1500) if 'weapon' in (str(o.get('template')) + str(o.get('name'))).lower()]
        if found:
            return found[0]
    return None


def run(g):
    # Dova crafts: on 17 Oct every /agentgear item for Besh failed (his inventory is full on the server, though his
    # client lists about ten items), while Dova, Pell and Varo took a whole kit.
    besh = g['Dova']
    besh.recover()
    if not any('crafting_artisan_novice' in str(s) for s in besh.profession('list').get('skills', [])):
        g.note(f'{besh.first} profession: ' + str(besh.profession('crafting_artisan'))[:160])
    if not items(besh, 'generic_tool'):
        g.note('crafting kit: ' + str(agentgear(besh, 'crafting').get('inventory'))[:160])
    if not resources(g, besh):
        g.note('BLOCKED: no resource containers with units in the inventory')
        return

    tool = (items(besh, 'generic_tool') or [None])[0]
    if g.check(f'{besh.first} has a generic crafting tool', tool, tool):
        craft(g, besh, tool, SURVEY_DEVICE, 'generic tool')

    weapon_tool = (items(besh, 'weapon_tool') or [None])[0]
    station = weapon_station(besh)
    if weapon_tool is None or station is None:
        g.note(f'BLOCKED: experimentation needs a weapon tool and a weapon station in reach '
               f'(tool {bool(weapon_tool)}, station {station and station.get("template")})')
        return
    g.note(f"weapon station: {station.get('template')} at {station.get('x'):.0f}, {station.get('y'):.0f}, "
           f"{station.get('distance', 0):.0f} m away{' in a building' if station.get('cell') else ''}")
    if station.get('cell'):
        reached = besh.walk(station['x'], station['y'], station.get('z'), station['cell'])
    else:
        reached = besh.walk(station['x'] + 2, station['y'])
    if not reached.get('arrived'):
        g.note(f'BLOCKED: could not reach the weapon station ({reached.get("error") or "did not arrive"})')
        return
    craft(g, besh, weapon_tool, SURVEY_DEVICE, 'weapon tool at a station', experiment=[[0, 1]])
