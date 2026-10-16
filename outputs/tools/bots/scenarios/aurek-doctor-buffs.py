"""Verify doctor enhancements by max-HAM gain or an exact server re-apply receipt.

Never count command acknowledgements or unrelated/refusal messages as buffs.
Medical-facility refusals identify the next prerequisite; no guessed cell IDs.

Server rules (Agent/local-research/doctor-enhance-wounds/report.md, 15 Oct): ANY cell of the hospital gives the doctor
its medical rating (no treatment room), so the bots walk to an object that is inside the building (in Mos Eisley the
trainers stand in cell 9655496). healEnhance range is 7 m, and one ~20 s cooldown covers enhance and wound healing.
Error 2 is either a missing ability or a refused posture/locomotion (INVALIDLOCOMOTION).
"""
import math

GROUP = 'Aurek'
SQUARE = (3528, -4800)


def enhancement_result(initial, after, events, patient, attribute):
    """A refresh has no max-HAM gain; match the recipient and attribute exactly.

    This proves the server accepted the refresh, not an independently measured duration.
    Acknowledgements, other patients' messages, silence and any refusal never suffice.
    """
    valid = all(type(n) in (int, float) and math.isfinite(n) for n in (initial, after))
    failed = any(e.get('event') == 'command_failed' for e in events)
    refreshed = any(e.get('event') == 'system' and e.get('text') ==
                    f"You re-apply {patient}'s {attribute.title()} enhancement." for e in events)
    if not valid or failed:
        return 'unverified'
    if after > initial:
        return 'increased'
    return 'reapplied' if refreshed and after == initial else 'unverified'


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
    # Any object inside the building gives a real cell and a local position to walk to.
    rooms = {}
    for text in ('object/mobile', 'object/tangible'):
        for r in doctor.locate(text, radius=40, x=hospital['x'], y=hospital['y']):
            if r.get('cell') and r.get('local') and r.get('building') == hospital.get('oid'):
                rooms[r['oid']] = r
    rooms = list(rooms.values())
    if not rooms:
        g.note('BLOCKED: hospital found but no object inside it to walk to (no cell known). No guessed cell.')
        return
    room = rooms[0]
    local = room['local']
    trips = g.parallel(*[lambda b=b, i=i: b.walk(local['x'] + 1.0 + i, local['y'] + 1.0, local['z'], room['cell'], tries=3)
                         for i, b in enumerate((doctor,) + fighters)])
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
                g.note('BLOCKED: healEnhance refused with error 2: Tamsin lacks the ability, or her posture or '
                       'locomotion was refused (stand still and retry); science_doctor_wound_02 is in her training')
                return
            after = fighter.status().get('me', {}).get('max_ham', {}).get(attribute)
            outcome = enhancement_result(initial, after, events, fighter.first, attribute)
            g.check(f'{fighter.first} receives {attribute} enhancement', outcome != 'unverified',
                    {'max_ham_before': initial, 'max_ham_after': after,
                     'outcome': outcome, 'messages': texts, 'failures': failures})
            if any('must_be_near_droid' in str(t) for t in texts):
                g.note('RULE: enhancement refused at town staging point; map a medical-centre '
                       'cell or provide a medical droid before retrying. No buff verified.')
                return
            if outcome == 'unverified' and not failures:
                g.note(f'{fighter.first} {attribute}: no max-HAM gain observed. Existing buff '
                       'refresh is unverified: body exposes no buff list/duration; do not infer success.')
            # One ~20 s cooldown covers enhance and wound healing; it ends with healing_response_59.
            if not doctor.wait_for(lambda e: 'healing_response_59' in str(e.get('text', '')), 25):
                doctor.idle(2)
