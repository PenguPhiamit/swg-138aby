"""Seek fresh Varo kills for Pell; try one harvest type per corpse.

Three bounded patrol stops replace the old empty 40 m guard sweep. Verify death,
range and a new matching resource container, never a generic 'harvest' message.
Existing-stack quantity is not exposed by the current body and is BLOCKED.
"""
GROUP = 'Besh'
PATROL = ((3660, -4940), (3710, -4980), (3760, -5020))
PREY = ('rockmite', 'womprat', 'kreetle', 'rill')


def upright(status):
    return status.get('ok') and status.get('me', {}).get('posture') == 'upright'


def resources(reply, kind):
    return {i['oid']: i.get('name') for i in reply.get('items', [])
            if 'resource_container' in str(i.get('name', '')).lower()
            and kind in str(i.get('name', '')).lower()}


def run(g):
    pell, varo = g['Pell'], g['Varo']
    # Artisans stay in town while the guard and scout hunt, one driver per bot.
    g.note('Varo basic gear: ' + str(varo.gear('basic'))[:180])
    staging = g.parallel(lambda: g['Besh'].walk(3528, -4800, tries=1),
                         lambda: g['Dova'].walk(3531, -4800, tries=1))
    if not g.check('artisans reach town staging point',
                   all(isinstance(t, dict) and t.get('arrived') for t in staging),
                   [str(t)[:90] for t in staging]):
        return
    kills = 0
    for spot, kind in zip(PATROL, ('meat', 'hide', 'bone')):
        statuses = (pell.status(), varo.status())
        if not g.check(f'{kind} patrol pair upright on Tatooine',
                       all(upright(s) and s.get('planet') == 'tatooine' for s in statuses)):
            break
        trips = g.parallel(lambda: varo.walk(*spot, tries=1),
                           lambda: pell.walk(spot[0] + 3, spot[1], tries=1))
        if not g.check(f'{kind} patrol reached',
                       all(isinstance(t, dict) and t.get('arrived') for t in trips),
                       [str(t)[:90] for t in trips]):
            g.note('BLOCKED: short patrol unreachable; stop before further exposure.')
            break
        prey = varo.find('', radius=90, type='CREO', where=lambda o:
                         str(o.get('name', '')).split(':')[-1] in PREY
                         and str(o.get('name', '')).startswith('@mob/creature_names:')
                         and o.get('posture') == 'upright')
        if not g.check(f'{kind} ordinary wild prey found', bool(prey), prey):
            continue
        if prey.get('health_pct', 100) < 100:
            g.note('BLOCKED: prey already injured; fresh uncontested harvest rights not established.')
            continue
        guard = varo.status().get('me', {})
        ham, maximum = guard.get('ham', {}), guard.get('max_ham', {})
        if not all(isinstance(ham.get(k), (int, float)) and maximum.get(k, 0) > 0
                   and ham[k] / maximum[k] >= 0.8 for k in ('health', 'action', 'mind')):
            g.note('BLOCKED: guard below 80% HAM or missing HAM evidence; stop harvest hunt.')
            break
        creature = varo.inspect(prey['oid']).get('creature', {})
        if not isinstance(creature.get('level'), (int, float)) or creature['level'] > 5:
            g.note('BLOCKED: prey level unknown or above 5; need a mapped weak-animal spawn.')
            continue
        result = varo.fight(prey['oid'], 20)
        if result.get('result') != 'target dead':
            varo.slash('peace', wait=1)
            g.note('BLOCKED: bounded fight did not finish; stop rather than repeat a dangerous patrol.')
            break
        # 'target gone' or incapacitated is insufficient proof of a harvestable kill.
        corpse = varo.inspect(prey['oid'])
        dead = corpse.get('ok') and corpse.get('creature', {}).get('posture') == 'dead'
        if not g.check(f'Varo makes fresh {kind} corpse', dead,
                       {'fight': result.get('result'), 'corpse': corpse.get('creature')}):
            if not upright(varo.status()):
                break
            continue
        kills += 1
        # Inspect again after the fight: prey may have moved from its original location.
        trip = pell.go(corpse)
        here = pell.status()
        near = (here.get('cell') == 0 and corpse.get('parent', 0) == 0
                and all(isinstance(o.get(k), (int, float))
                        for o in (here, corpse) for k in ('x', 'y', 'z')))
        if near:
            near = sum((here[k] - corpse[k]) ** 2 for k in ('x', 'y', 'z')) <= 25
        if not g.check(f'Pell reaches fresh {kind} corpse',
                       trip.get('arrived') and upright(here) and near, trip):
            continue
        before_reply = pell.inventory()
        if not g.check(f'{kind} inventory baseline readable', before_reply.get('ok'), before_reply.get('error')):
            return
        before = resources(before_reply, kind)
        events = pell.slash('harvestcorpse', kind, target=prey['oid'], wait=6)
        texts = [e.get('text', '') or e.get('reason', '') for e in events
                 if e.get('event') in ('system', 'command_failed')]
        failures = [e for e in events if e.get('event') == 'command_failed']
        if any(e.get('error') == 2 for e in failures):
            g.note('BLOCKED: Pell lacks harvestCorpse; scout camp training grants forage, '
                   'not proof of harvesting ability. Claude should check the required skill.')
            return
        after_reply = pell.inventory()
        new = resources(after_reply, kind).keys() - before.keys()
        g.check(f'Pell receives new {kind} resource container',
                after_reply.get('ok') and bool(new) and not failures,
                {'new_oids': sorted(new), 'messages': texts, 'failures': failures})
        if not new and before and not failures:
            g.note(f'BLOCKED: {kind} may merge into an existing stack; body inventory/inspect '
                   'does not expose resource quantity. Receipt remains unverified.')
        elif not new and not failures:
            g.note(f'{kind}: no new matching resource container observed; inspect command messages '
                   'and inventory naming before attributing the failure to the server.')
        # A corpse is normally harvested once: never expect all three types from one kill.
    g.note(f'Fresh kills inspected: {kills}; one harvest type attempted per corpse.')
