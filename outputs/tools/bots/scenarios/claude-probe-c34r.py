"""Claude, 15 Oct 2026: game check of ChatGPT's C34r fix (dev 90044b8e, from gpt/work 19cfb3a5).

    squad.py run scenarios/claude-probe-c34r.py --group Aurek --rounds 1 --round-minutes 6 --no-fallback

Before the fix, /agentgear afflict poison|disease|fire|bleeding rolled the engine's DOT resistance (potency 100 against
defense 0: about one in five missed) and still answered without an error. Now every application lands, or the answer
carries an error. The leader afflicts the second member ten times per kind: all 40 must report a DOT, and none may
answer with an error. With the old roll, 40 out of 40 had a chance of about 0.8^40 (1 in 7,500).
"""
import json

KINDS = ('poison', 'disease', 'fire', 'bleeding')
TRIES = 10


def answer(bot, args, target=0):
    bot.slash('agentGear', args, target=target, wait=0)
    event = bot.wait_for(lambda e: str(e.get('text', '')).startswith('[agentgear] '), 8)
    if not event:
        return {'error': 'no answer'}
    try:
        return json.loads(event['text'][len('[agentgear] '):])
    except ValueError:
        return {'error': 'bad json: ' + event['text'][:120]}


def run(g):
    lead, other = g.bots[0], g.bots[1]
    other.status()
    oid = other.oid
    for kind in KINDS:
        landed, errors, sample = 0, [], None
        for _ in range(TRIES):
            got = answer(lead, 'afflict ' + kind, target=oid)
            sample = got
            if got.get('error'):
                errors.append(got['error'])
            elif got.get('dot'):
                landed += 1
        g.check(f'afflict {kind}: {TRIES}/{TRIES} DOTs land, no errors', landed == TRIES and not errors,
                {'landed': landed, 'errors': errors[:3], 'last': sample})
    # Leave the patient clean for the next scenario: the afflictions wear off (60-120 s), and a self-test answer shows
    # the command still works on the caller.
    got = answer(lead, 'afflict bleeding')
    g.check('afflict bleeding on self lands', not got.get('error') and bool(got.get('dot')), got)
