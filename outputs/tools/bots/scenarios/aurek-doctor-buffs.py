"""Verify all four doctor enhancements by max-HAM changes, away from camp combat.

Never count command acknowledgements or unrelated/refusal messages as buffs.
Medical-facility refusals identify the next prerequisite; no guessed cell IDs.
"""
GROUP = 'Aurek'
SQUARE = (3528, -4800)


def ready(status):
    me = status.get('me', {})
    return (status.get('ok') and status.get('planet') == 'tatooine'
            and me.get('posture') == 'upright' and 'combat' not in me.get('states', []))


def run(g):
    doctor = g['Tamsin']
    fighters = (g['Aurek'], g['Jesh'])
    g.note('Tamsin support gear: ' + str(doctor.gear('support'))[:180])
    hospitals = doctor.locate('hospital', radius=2000)
    if not hospitals:
        g.note('BLOCKED: no hospital mapped within 2 km; no buff attempted.')
        return
    hospital = hospitals[0]
    # An outdoor building position cannot identify its treatment cell. Search interior occupants.
    rooms = doctor.locate('medical', radius=100, x=hospital['x'], y=hospital['y'])
    rooms += doctor.locate('healer', radius=100, x=hospital['x'], y=hospital['y'])
    rooms += doctor.locate('hospital', radius=100, x=hospital['x'], y=hospital['y'])
    rooms = [r for r in rooms if r.get('cell') and r.get('local')
             and (r.get('building') == hospital.get('oid') or r.get('oid') == hospital.get('oid'))]
    if not rooms:
        g.note('BLOCKED: hospital found but no interior treatment anchor; Claude should expose building cells/medical rating. No guessed cell.')
        return
    room = rooms[0]
    local = room['local']
    trips = g.parallel(*[lambda b=b: b.walk(local['x'], local['y'], local['z'], room['cell'], tries=3)
                         for b in (doctor,) + fighters])
    if not g.check('doctor and fighters enter mapped hospital cell',
                   all(isinstance(t, dict) and t.get('arrived') for t in trips), trips):
        return
    for bot in (doctor,) + fighters:
        bot.slash('stand', wait=1)
    packs = [i for i in doctor.inventory().get('items', [])
             if 'enhance' in str(i.get('name', '')).lower()]
    if not g.check('Tamsin carries enhancement packs', bool(packs), len(packs)):
        return
    for fighter in fighters:
        for attribute in ('health', 'action'):
            healer, before = doctor.status(), fighter.status()
            near = (healer.get('cell') == before.get('cell')
                    and all(isinstance(s.get(k), (int, float))
                            for s in (healer, before) for k in ('x', 'y', 'z')))
            if near:
                near = sum((healer[k] - before[k]) ** 2 for k in ('x', 'y', 'z')) <= 36
            if not g.check(f'{fighter.first} {attribute} buff prerequisites',
                           ready(healer) and ready(before) and near and before.get('self'),
                           {'doctor': healer.get('me'), 'fighter': before.get('me'), 'near': near}):
                return
            initial = before.get('me', {}).get('max_ham', {}).get(attribute)
            if not isinstance(initial, (int, float)):
                g.note('BLOCKED: body omitted max_ham; cannot verify doctor enhancement')
                return
            events = doctor.slash('healenhance', attribute, target=before['self'], wait=8)
            # Capture command events before status() resets the doctor's inbox.
            texts = [e.get('text', '') or e.get('reason', '') for e in events
                     if e.get('event') in ('system', 'command_failed')]
            failures = [e for e in events if e.get('event') == 'command_failed']
            if any(e.get('error') == 2 for e in failures):
                g.note('BLOCKED: Tamsin lacks healEnhance; Claude should re-run setup Aurek '
                       '(science_doctor_wound_02 is already listed in training)')
                return
            after = fighter.status().get('me', {}).get('max_ham', {}).get(attribute)
            gained = isinstance(after, (int, float)) and after > initial
            g.check(f'{fighter.first} receives {attribute} enhancement', gained and not failures,
                    {'max_ham_before': initial, 'max_ham_after': after,
                     'messages': texts, 'failures': failures})
            if any('must_be_near_droid' in str(t) for t in texts):
                g.note('RULE: enhancement refused at town staging point; map a medical-centre '
                       'cell or provide a medical droid before retrying. No buff verified.')
                return
            if not gained and not failures:
                g.note(f'{fighter.first} {attribute}: no max-HAM gain observed. Existing buff '
                       'refresh is unverified: body exposes no buff list/duration; do not infer success.')
            doctor.idle(5)  # avoid overlapping heal cooldowns
