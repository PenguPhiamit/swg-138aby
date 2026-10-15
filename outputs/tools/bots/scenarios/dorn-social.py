"""Dorn, starter: group chat and tells, the /leash follow assist, an entertainer dance, and a conversation
with the mercenary broker Dax Venn."""
import time

GROUP = 'Dorn'
SQUARE = (3528, -4790)


def run(g):
    dorn, nima, rusk = g['Dorn'], g['Nima'], g['Rusk']
    g.note('Rusk gear: ' + str(rusk.gear('basic'))[:160])
    g.parallel(*[lambda b=b, i=i: b.walk(SQUARE[0] + 2 * i, SQUARE[1]) for i, b in enumerate(g.bots)])

    for bot in (nima, rusk):
        bot.status()  # start a fresh inbox
    dorn.say('Dorn group checking in')
    heard = [b.wait_for(lambda e: e.get('event') == 'chat' and 'Dorn' in str(e.get('from')), 6) for b in (nima, rusk)]
    g.check('spatial chat heard by both', all(heard), [h and h.get('text') for h in heard])

    nima.status()
    sent = dorn.tell('Nima', 'Nima, are you with me?')
    tell = nima.wait_for('"tell"', 6)
    g.check('tell arrives', tell and 'with me' in str(tell.get('text')), tell or sent)

    nima.slash('leash', 'off', wait=1)  # a run that stopped early can leave it on
    events = nima.slash('leash', 'Dorn', wait=1)
    g.check('leash starts', any('Leashed to' in str(e.get('text')) for e in events), [e.get('text') for e in events if e.get('text')])
    start = dorn.status()
    if not all(isinstance(start.get(k), (int, float)) for k in ('x', 'y')):
        g.check('leader position available before leash walk', False, start)
        nima.slash('leash', 'off', wait=1)
        return
    walk_started = time.time() - nima.started
    end = dorn.walk(start['x'], start['y'] + 30)  # Nima stands still; the leash should hop her after him
    # A failed walk returns an error dict, not a position. Do not dereference it or keep the leash active.
    if not isinstance(end, dict) or not end.get('ok', True) or not end.get('arrived') or not all(
            isinstance(end.get(k), (int, float)) for k in ('x', 'y')):
        g.check('leader leash test walk arrived', False, end)
        nima.slash('leash', 'off', wait=1)
        return
    gap, deadline = 99.0, time.time() + 20
    while time.time() < deadline:
        spot = nima.status()
        if not all(isinstance(spot.get(k), (int, float)) for k in ('x', 'y')):
            g.check('follower position available during leash test', False, spot)
            nima.slash('leash', 'off', wait=1)
            return
        gap = ((spot['x'] - end['x']) ** 2 + (spot['y'] - end['y']) ** 2) ** 0.5
        if gap < 10:
            break
        time.sleep(2)
    # The leash only moves along a real route. Where the navmesh stops short of the leader (raised ground) it
    # stops at the closest walkable spot and says so once, instead of rubber-banding.
    def said(text, since):  # Nima's system messages since a point in the run (status() clears the inbox)
        return [e for e in nima.history if e.get('t', 0) >= since and text in str(e.get('text', ''))]

    capped = said('as close to', walk_started)
    g.check('leash brings Nima to Dorn after he stops', gap < 10 or (capped and gap < 20),
            f'{gap:.1f} m from Dorn' + (' (closest walkable spot)' if capped else ''))
    stopped = time.time() - nima.started
    nima.idle(10)
    hops = len(said('you were stuck', stopped))
    g.check('no repeated hops once Dorn has stopped', hops <= 1, f'{hops} hops in 10 s')

    # Menu labels in a three-person group: "Stop leash" only on the current leader (ChatGPT C4b finding 5).
    def label(menu):
        return next((i.get('label') for i in menu.get('items', []) if i.get('radial_id') == 77), None)

    on_dorn, on_rusk = label(nima.radial(dorn.oid)), label(nima.radial(rusk.oid))
    g.check('menu: "Stop leash" on the leader', on_dorn == 'Stop leash', on_dorn)
    g.check('menu: another member offers to switch', on_rusk == 'Leash to this member instead', on_rusk)
    events = nima.slash('leash', 'off', wait=1)
    g.check('leash off', any('Leash off' in str(e.get('text')) for e in events), [e.get('text') for e in events if e.get('text')])

    # Entertainer buff (Agent/local-research/entertainer-buffs/report.md, 15 Oct): a patron grouped with the performer
    # who watches for at least 60 s gets the dance buff when the watching ends, here when Dorn stops dancing.
    events = dorn.slash('startdance', 'basic', wait=4)
    g.note('Dorn /startdance basic: ' + '; '.join(e.get('text', e.get('event', '')) for e in events
                                                    if e.get('event') in ('system', 'posture', 'command_failed'))[:300])
    dancing = any('dance_start_self' in str(e.get('text')) or 'start dancing' in str(e.get('text')).lower()
                  for e in events)
    if dancing:
        watch = nima.slash('watch', target=dorn.oid, wait=3)
        g.check('Nima watches Dorn dance', any('dance_watch_self' in str(e.get('text')) or 'watch' in str(e.get('text')).lower()
                                               for e in watch if e.get('event') == 'system'),
                [e.get('text') for e in watch if e.get('text')][:3])
        nima.idle(70)
        dorn.slash('stopdance', wait=3)
        buff = nima.wait_for(lambda e: 'performance_enhance_dance_mind' in str(e.get('text', '')), 8)
        g.check('Nima gets the dance buff after 70 s of watching', buff,
                (buff or {}).get('text') or 'no performance_enhance message: does Dorn have private_buff_mind and '
                'healing_dance_mind (novice entertainer only)?')
    else:
        g.note('BLOCKED: Dorn did not start dancing, so the entertainer buff was not tried')
        dorn.slash('stopdance', wait=2)

    dax = rusk.find('Dax Venn', radius=96, type='CREO')
    if g.check('Dax Venn the mercenary broker is nearby', dax, dax and f"{dax['distance']} m"):
        rusk.go(dax)
        rusk.talk(dax['oid'], wait=3)
        options = rusk.wait_for('"conversation_options"', 5)
        g.check('Dax offers options', options and options.get('options'), (options or {}).get('options'))
