"""Aurek, the world-boss crew: support sets up a camp outside town and buffs the fighters before a fight.

  Oren (scout trained to Ranger) places a camp, Tamsin (trained to Doctor) applies enhancement buffs,
  Sela (entertainer) dances while the fighters watch, then Aurek and Jesh (boss gear, trained to certify it)
  fight a creature near camp and come back to recover. Training comes from groups.json "training" (setup).

This is the warm-up for real boss hunts: Rhea Tannor (cresh-travel.py) lists where bosses are. A boss trip is
the same pattern with a long walk or a shuttle first; extend it here as aurek-boss-<name>.py.
"""
GROUP = 'Aurek'
CAMP = (4150, -4350)  # open desert ~800 m from Mos Eisley: camps are refused inside city limits (@camp:error_muni_true)
TOUGH = ('greater', 'giant', 'ancient', 'enraged', 'matriarch', 'patriarch', 'king', 'queen', 'elder')


def text_of(events):
    return '; '.join(e.get('text', '') or e.get('reason', '') for e in events
                     if e.get('event') in ('system', 'command_failed') and 'World boss' not in str(e.get('text')))[:220]


def run(g):
    aurek, jesh, tamsin, sela, oren = g['Aurek'], g['Jesh'], g['Tamsin'], g['Sela'], g['Oren']
    fighters, support = (aurek, jesh), (tamsin, sela, oren)
    for bot in fighters:
        g.note(f'{bot.first} gear: ' + str(bot.gear('boss'))[:120])
    for bot in support:
        g.note(f'{bot.first} gear: ' + str(bot.gear('support'))[:120])
    g.parallel(*[lambda b=b, i=i: b.walk(CAMP[0] + 3 * i, CAMP[1]) for i, b in enumerate(g.bots)])

    kit = next((i for i in oren.inventory().get('items', []) if 'camp' in str(i.get('name')).lower()), None)
    if g.check('Oren has a camp kit', kit):
        camp, refusals = None, []
        for step in range(4):  # camps are refused in cities and next to buildings: move on and try again
            events = oren.select(kit['oid'], 20, wait=6)
            camp = oren.find('camp', radius=30, type='TANO', where=lambda o: o['oid'] != kit['oid'])
            if camp:
                break
            refusals.append(text_of(events))
            here = oren.status()
            g.parallel(*[lambda b=b, i=i: b.walk(here['x'] + 150 + 3 * i, here['y'] + 150) for i, b in enumerate(g.bots)])
        g.check('camp placed', camp, camp and camp['name'] or '; '.join(refusals))

    packs = [i for i in tamsin.inventory().get('items', []) if 'enhance' in str(i.get('name')).lower()]
    if g.check('Tamsin carries enhancement packs', packs, len(packs)):
        answers = []
        for bot in fighters:
            for attribute in ('health', 'action'):
                events = tamsin.slash('healenhance', attribute, target=bot.oid, wait=4)
                answers.append(text_of(events))
                g.note(f'Tamsin enhances {bot.first} {attribute}: {answers[-1]}')
        refused = ('missing ability', 'must_be_near_droid', 'not_enough', 'cannot', 'invalid', 'no_')
        if all('missing ability' in a for a in answers):
            g.note('BLOCKED: Tamsin lacks the healEnhance ability (it comes from science_doctor_wound_02, in groups.json training; '
                   're-run squad.py setup Aurek)')
        elif all('must_be_near_droid' in a for a in answers):
            g.note('RULE: Doctor buffs need a medical droid or a medical centre, not a camp. Next: buff the fighters inside '
                   "the Mos Eisley medical centre (find it with look(type='BUIO')) before they leave town")
        else:
            ok = [a for a in answers if a and not any(r in a for r in refused)]
            g.check('fighters receive doctor buffs', ok, (ok or answers)[:2])

    events = sela.slash('startdance', 'basic', wait=2)
    g.check('Sela dances in camp', any(e.get('event') == 'posture' or 'dance_start' in str(e.get('text')) for e in events),
            text_of(events))
    for bot in fighters:
        bot.slash('watch', target=sela.oid, wait=1)
    for bot in fighters:
        bot.idle(25)  # watching a while is what pays out entertainer effects
        g.note(f'{bot.first} watching Sela: {text_of(bot.inbox)}')
        bot.slash('stopwatching', wait=1)
    sela.slash('stopdance', wait=1)

    def wild(o):
        name = str(o.get('name', ''))
        return name.startswith('@mob/creature_names:') and o.get('posture') == 'upright' and not any(w in name for w in TOUGH)

    prey = next(iter([o for o in aurek.look(120, 'CREO', 400) if wild(o)]), None)
    if g.check('a creature near camp', prey, prey and prey['name']):
        results = g.parallel(*[lambda b=b: b.fight(prey['oid'], 90) for b in fighters])
        g.check('buffed fighters bring it down', any('target' in str(r.get('result')) for r in results if isinstance(r, dict)),
                [r.get('result') if isinstance(r, dict) else str(r) for r in results])
        g.parallel(*[lambda b=b, i=i: b.walk(CAMP[0] + 3 * i, CAMP[1] + 4) for i, b in enumerate(fighters)])
        for bot in fighters:
            me = bot.status().get('me', {})
            g.note(f"{bot.first} back at camp: {me.get('posture')} H{me.get('ham', {}).get('health')}/{me.get('max_ham', {}).get('health')}")
