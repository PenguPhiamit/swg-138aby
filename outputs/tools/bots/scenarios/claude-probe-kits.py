"""Claude, 15 Oct 2026: first live check of the new /agentgear kits (dev 60ed8971) and afflict (9b93665d) on two bots.

    squad.py run scenarios/claude-probe-kits.py --group Dorn --rounds 1 --round-minutes 6 --no-fallback

The leader takes two item kits and lists its abilities; then poisons, wounds and dizzies the second member through
afflict (target = that member) and once itself. Every answer must be '[agentgear] {json}' without an error.
"""
import json


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
    for kit in ('medicine2', 'instruments'):
        got = answer(lead, kit)
        g.check(f'kit {kit}: no failures', not got.get('error') and not got.get('failed'), got)
        g.note(f'{kit}: {len(got.get("inventory", []))} to inventory, {len(got.get("equipped", []))} equipped')
    listed = answer(lead, 'profession list')
    g.check('profession list has abilities', isinstance(listed.get('abilities'), list) and len(listed['abilities']) > 0,
            {'abilities': len(listed.get('abilities', [])), 'skills': len(listed.get('skills', []))})
    other.status()
    oid = other.oid
    for kind in ('poison', 'wounds', 'dizzy'):
        got = answer(lead, 'afflict ' + kind, target=oid)
        g.check(f'afflict {kind} on {other.name}', not got.get('error') and got.get('target') == oid, got)
    got = answer(lead, 'afflict damage')
    g.check('afflict damage on self', not got.get('error'), got)
    bad = answer(lead, 'afflict nonsense')
    g.check('unknown kind refused with usage', 'usage' in str(bad.get('error', '')), bad)
