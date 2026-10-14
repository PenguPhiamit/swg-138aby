"""C23 test-galaxy acceptance; no provisioning/staff commands. Run only after restart-ready + driver claim.

Use squad.py run <this file> --group Esk --no-fallback --rounds 1 --round-minutes 30.
Existing crew needs ordinary survey tools and harvesting skills. Unsupported quantity/credit/waypoint
telemetry is BLOCKED, never inferred from a success message. Actual run is pending.
"""
import importlib.util
import math
from pathlib import Path
import sys

GROUP = 'Esk'
TOOLS = {'mineral': ('mineral',), 'chemical': ('chemical',), 'gas': ('gas',),
         'water': ('moisture',), 'flora': ('flora',), 'energy': ('liquid', 'wind', 'solar')}
HOTH_TYPES = {'steel_hoth', 'iron_hoth', 'aluminum_hoth', 'copper_hoth', 'ore_extrusive_hoth',
              'ore_intrusive_hoth', 'radioactive_hoth', 'gas_reactive_hoth',
              'petrochem_fuel_liquid_hoth', 'petrochem_fuel_solid_hoth'}
ROOT = Path(__file__).resolve().parents[3]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def named(value):
    return isinstance(value, str) and bool(value.strip()) and not value.startswith('@')


def quantities(reply):
    """No made-up default of one unit; body v0.2 may expose only names/IDs."""
    out = {}
    for item in reply.get('items', []):
        amount = next((item[k] for k in ('units', 'quantity', 'stack_count')
                       if isinstance(item.get(k), (int, float)) and not isinstance(item[k], bool)), None)
        if amount is not None and item.get('oid') is not None:
            out[str(item['oid'])] = (item.get('name'), amount)
    return out


def unit_gain(before, after):
    a, b = quantities(before), quantities(after)
    if not b:
        return None
    return [(name, amount - a.get(oid, ('', 0))[1]) for oid, (name, amount) in b.items()
            if amount > a.get(oid, ('', 0))[1]]


def receipt(g, label, before, after):
    gains = unit_gain(before, after)
    if gains is None:
        g.note(f'BLOCKED: {label}: inventory units unavailable; new item or success text is insufficient')
        return
    g.check(label + ': units received', bool(gains), gains)


def healthy(bot):
    s = bot.status()
    me = s.get('me', {})
    ham, cap = me.get('ham', {}), me.get('max_ham', {})
    return s.get('planet') == 'hoth' and me.get('posture') == 'upright' and all(
        isinstance(ham.get(k), (int, float)) and cap.get(k, 0) > 0 and ham[k] / cap[k] >= .8
        for k in ('health', 'action', 'mind'))


def choose_job(options):
    return next((i for i, value in enumerate(options)
                 if 'find her' in str(value).lower() or 'player_1_1' in str(value)), None)


def quest_waypoint(before, after, target):
    """None means telemetry unavailable; [] means observed but no matching new marker."""
    if not isinstance(before.get('waypoints'), list) or not isinstance(after.get('waypoints'), list):
        return None
    old = {str(p.get('oid')): p for p in before['waypoints']}
    return [p for p in after['waypoints'] if p != old.get(str(p.get('oid')))
            and p.get('planet') == 'hoth' and p.get('active') is True
            and all(isinstance(p.get(k), (int, float)) and not isinstance(p[k], bool)
                    for k in ('x', 'y'))
            and math.hypot(p['x'] - target['x'], p['y'] - target['y']) <= 5]


def preflight(g):
    inventories = [(member, member.inventory().get('items', [])) for member in g.bots]
    missing = [kind for kind in ('mineral', 'chemical', 'gas', 'moisture', 'flora', 'liquid')
               if not any('survey_tool_' + kind in str(item.get('name'))
                          for _, items in inventories for item in items)]
    fighter_ready = any('armor_composite' in str(item.get('name')) for item in inventories[0][1])
    if missing:
        g.note('BLOCKED: crew preparation lacks survey tools: ' + ', '.join(missing))
    if not fighter_ready:
        g.note('BLOCKED: leader has no observable approved boss-kit armor; do not leave the outpost for Hoth testing')
    return not missing and fighter_ready


def run(g):
    if not preflight(g):
        return  # remain in the starting safe location; do not travel merely to discover missing prerequisites
    travel = load('c23_travel', 'outputs/tools/bots/scenarios/esk-hoth.py')
    gather = load('c23_gather', 'outputs/tools/bots/scenarios/besh-gather.py')
    from fallback_scenarios import recover_home
    bot = g.leader
    kills, loot = 0, []
    try:
        for member in g.bots:
            planet = member.status().get('planet')
            if planet == 'tatooine' and not travel.ride(g, member, travel.MOS_EISLEY, travel.CORONET):
                return
            if member.status().get('planet') == 'corellia' and not travel.ride(g, member, travel.CORONET, travel.HOTH):
                return
            if not g.check(member.first + ': on Hoth', member.status().get('planet') == 'hoth'):
                return
        if not bot.walk(20, -2235, tries=2).get('arrived'):
            g.note('BLOCKED: cannot reach survey field south of outpost')
            return
        if not healthy(bot):
            g.note('BLOCKED: survey-field traversal compromised the leader; stop rather than test services while down')
            return
        sys.path.insert(0, str(ROOT / 'outputs/tools/owner_content'))
        import swg_client_data
        raw = swg_client_data.client_file('string/en/resource_names.stf')
        labels = swg_client_data.string_file(raw) if raw else {}
        seen = set()
        tool_inventory = [item for member in g.bots for item in member.inventory().get('items', [])]
        for category, kinds in TOOLS.items():
            observed, available = [], False
            for kind in kinds:
                surveyor, tool = next(((member, item) for member in g.bots for item in member.inventory().get('items', [])
                                      if 'survey_tool_' + kind in str(item.get('name'))), (None, None))
                if tool is None:
                    continue
                if surveyor is not bot and not surveyor.walk(20, -2235, tries=1).get('arrived'):
                    g.note('BLOCKED: tool owner cannot safely reach the survey field')
                    continue
                available = True
                surveyor.status()  # consume old inbox before opening a fresh survey
                surveyor.select(tool['oid'], 20, wait=0)
                event = surveyor.wait_for('"survey_resources"', 5)
                if not event:
                    g.note(f'BLOCKED: {kind} survey list unavailable; range dialog/tool setup may be required')
                    continue
                for resource in event.get('resources', []):
                    typ, name = resource.get('type'), resource.get('name')
                    seen.add(typ)
                    display = labels.get(typ)
                    g.check(f'{kind}: resolved resource names', named(name) and named(display),
                            dict(name=name, type=typ, display=display))
                    surveyor.slash('requestSurvey', name, wait=0)
                    result = surveyor.wait_for('"survey_results"', 15)
                    g.note('SURVEY: ' + str(dict(category=category, resource=resource, display=display,
                                                best=(result or {}).get('best'), reply_received=bool(result))))
                    observed.append(resource)
                    g.sleep(4)
            if available:
                g.check(category + ': at least one survey type', bool(observed), observed)
            else:
                g.note(f'BLOCKED: {category}: no ordinary survey tool in inventory')
        missing = sorted(HOTH_TYPES - seen)
        if any('survey_tool_mineral' in str(i.get('name')) for i in tool_inventory) and any(
                'survey_tool_gas' in str(i.get('name')) for i in tool_inventory):
            # Liquid fuel requires the liquid survey tool too; do not call a missing tool a server regression.
            if any('survey_tool_liquid' in str(i.get('name')) for i in tool_inventory):
                g.check('all ten Hoth inorganic types listed', not missing, missing)
            else:
                g.note('BLOCKED: full ten-type census needs liquid survey tool; missing observed types=' + str(missing))
        sampler = next((member for member in g.bots if any('survey_tool_mineral' in str(i.get('name'))
                        for i in member.inventory().get('items', []))), bot)
        before = sampler.inventory()
        gather.survey_and_sample(g, sampler, 'mineral')
        receipt(g, 'mineral sample', before, sampler.inventory())

        # One harvest category per fresh corpse avoids the pre-CU one-harvest-per-corpse rule.
        for kind in ('meat', 'hide', 'bone'):
            g.checkpoint()
            if not healthy(bot):
                g.note('BLOCKED: tauntaun combat requires upright crew leader with >=80% known HAM')
                break
            prey = bot.find('tauntaun', radius=120, type='CREO', where=lambda o:
                            o.get('posture') == 'upright' and o.get('health_pct') == 100)
            if not g.check(kind + ': fresh tauntaun south of pad', bool(prey), prey):
                continue
            result = bot.fight(prey['oid'], 60)
            if result.get('result') != 'target dead':
                bot.slash('peace', wait=1)
                g.note('BLOCKED: tauntaun fight not won within 60 s; ' + str(result))
                break
            kills += 1
            corpse = bot.inspect(prey['oid'])
            if corpse.get('creature', {}).get('posture') != 'dead':
                g.note('BLOCKED: dead corpse not observable for harvest/loot')
                continue
            bot.go(prey)
            before = bot.inventory()
            events = bot.slash('harvestcorpse', kind, target=prey['oid'], wait=4)
            if gather.missing_ability(events):
                g.note('BLOCKED: ordinary scout harvest skill missing: ' + kind)
            else:
                receipt(g, kind + ' harvest', before, bot.inventory())
            # Observe actual loot changes; zero drops is valid, never a probability test.
            before = bot.inventory()
            bot.slash('loot', target=prey['oid'], wait=3)
            old = {str(i.get('oid')) for i in before.get('items', [])}
            loot.extend(i for i in bot.inventory().get('items', []) if str(i.get('oid')) not in old)

        accepted = False
        for y in (-1996, -2002):
            terminals = bot.locate('terminal_mission', 5, x=48, y=y)
            if not g.check(f'mission terminal {y} exists', bool(terminals), terminals):
                continue
            terminal = terminals[0]
            if not bot.go(terminal).get('arrived'):
                g.note('BLOCKED: cannot reach mission terminal')
                continue
            offered = [m for m in bot.mission_list(terminal['oid']) if 'mission_bag' in str(m.get('container_name'))]
            hoth = [m for m in offered if (m.get('waypoint') or m.get('start') or {}).get('planet') == 'hoth']
            g.check(f'terminal {y} lists Hoth missions', bool(hoth), offered)
            mission = next((m for m in hoth if m.get('type') == 'destroy'), None)
            if mission and not accepted:
                bot.accept_mission(mission['oid'], terminal['oid'])
                mine = next((m for m in bot.missions() if m.get('oid') == mission['oid'] and 'datapad' in str(m.get('container_name'))), {})
                g.check('accepted destroy target is Hoth',
                        (mine.get('waypoint') or mine.get('start') or {}).get('planet') == 'hoth', mine)
                accepted = True  # do not accept a second mission; retained for inspection
            elif not mission:
                g.note('BLOCKED: no observable Hoth destroy offer')
        vell = bot.locate('quartermaster', 30, x=44, y=-2010)
        if g.check('Vell found', bool(vell), vell):
            bot.go(vell[0])
            bot.talk(vell[0]['oid'], wait=3)
            index = choose_job(bot.status().get('conversation_options', []))
            if index is None:
                g.note('BLOCKED: Vell first-job option unavailable; quest state retained, no reset')
            else:
                previous_ria = {o['oid'] for o in bot.locate('Ria', 1000, x=44, y=-2010)}
                before_waypoints = bot.status()
                bot.choose(index, wait=4)
                ria = [o for o in bot.locate('Ria', 1000, x=44, y=-2010) if o['oid'] not in previous_ria]
                g.check('Ria spawned 600–900 m from Vell', bool(ria) and 600 <= math.hypot(ria[0]['x'] - 44, ria[0]['y'] + 2010) <= 900, ria)
                if len(ria) == 1:
                    markers = quest_waypoint(before_waypoints, bot.status(), ria[0])
                    if markers is None:
                        g.note('BLOCKED: quest waypoint telemetry unavailable; spawned-NPC position is not waypoint proof')
                    else:
                        g.check('new active Hoth quest waypoint matches Ria', bool(markers), markers)
                if len(ria) != 1:
                    g.note('BLOCKED: cannot identify exactly one newly spawned quest target; no unrelated target touched')
                else:
                    target = ria[0]
                    guards = bot.locate('ice_mynock', 40, x=target['x'], y=target['y'])
                    levels = [bot.inspect(o['oid']).get('creature', {}).get('level') for o in guards]
                    g.check('Ria guarded by two level-67 ice mynocks', len(guards) == 2 and levels == [67, 67], levels)
                    won = len(guards) == 2
                    for guard in guards[:2]:
                        if not healthy(bot):
                            won = False
                            g.note('BLOCKED: crew cannot safely attempt level-67 guard fight with current HAM/kit')
                            break
                        result = bot.fight(guard['oid'], 60)
                        if result.get('result') != 'target dead':
                            bot.slash('peace', wait=1)
                            won = False
                            g.note('BLOCKED: level-67 guard fight not won within budget: ' + str(result))
                            break
                        kills += 1
                        bot.go(guard)
                        old = {str(i.get('oid')) for i in bot.inventory().get('items', [])}
                        bot.slash('loot', target=guard['oid'], wait=3)
                        loot.extend(i for i in bot.inventory().get('items', []) if str(i.get('oid')) not in old)
                    if won and bot.go(target).get('arrived'):
                        before_items = {str(i.get('oid')) for i in bot.inventory().get('items', [])}
                        bot.talk(target['oid'], wait=4)
                        regulator = [i for i in bot.inventory().get('items', [])
                                     if str(i.get('oid')) not in before_items and 'Salvaged Power Regulator' in str(i.get('name'))]
                        if g.check('Ria hands over Salvaged Power Regulator', bool(regulator), regulator):
                            if bot.go(vell[0]).get('arrived'):
                                before = bot.status()
                                events = bot.talk(vell[0]['oid'], wait=4)
                                after = bot.status()
                                consumed = not any(str(i.get('oid')) == str(regulator[0]['oid']) for i in bot.inventory().get('items', []))
                                g.check('Vell takes the regulator', consumed, events)
                                if all(isinstance(s.get('cash_credits'), (int, float)) and isinstance(s.get('bank_credits'), (int, float)) for s in (before, after)):
                                    delta = after['cash_credits'] + after['bank_credits'] - before['cash_credits'] - before['bank_credits']
                                    g.check('Vell reward exactly 1500 credits', delta == 1500, delta)
                                else:
                                    g.note('BLOCKED: exact 1500-credit reward delta unavailable in current body')
    finally:
        g.note(f'LOOT OBSERVATION: confirmed kills={kills}; new loot item records={len(loot)}; {loot}')
        # Cleanup has the same run deadline; budget stops are reported, never silently called home.
        g.parallel(*[lambda member=member: member.recover() for member in g.bots])
        g.check('crew returns to Tatooine', recover_home(g))
