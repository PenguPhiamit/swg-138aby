"""Botanist feasibility test, server half (owner, 14 Oct). Does the test galaxy know the new box, grant it, show the
trainer, and keep the box across a relog? One bot (Pell, a Besh gatherer), test galaxy only. /agentskill is the bots'
training helper; it grants a box with its prerequisites and answers "[agentskill] {json}" (granted/failed/unknown).

    wsl -d Debian -u swgemu -- python3 .../tools/bots/squad.py run .../tools/owner_content/botanist_check.py --group Besh
Run it twice with a relog of Pell in between: the second run's first check then shows whether the box persisted.
"""
import json

GROUP = 'Besh'
BOX = 'outdoors_botanist_novice'


def skills_seen(bot):
    s = bot.status()
    for key in ('skills', 'skill_list', 'skillList'):
        if key in s:
            return s[key]
    return None


def ask(bot, boxes):
    bot.slash('agentSkill', boxes, wait=0)
    answer = bot.wait_for(lambda e: str(e.get('text', '')).startswith('[agentskill]'), 8)
    return json.loads(answer['text'][len('[agentskill] '):]) if answer else None


def run(g):
    pell = g['Pell']
    before = skills_seen(pell)
    g.note(f'status keys: {sorted(pell.status().keys())}')
    if before is not None:
        g.note(f'BOTANIST: Pell holds {BOX} before asking: {BOX in before}')
    reply = ask(pell, BOX)
    g.check(f'server knows {BOX} (not "unknown")', reply is not None and BOX not in reply.get('unknown', []), reply)
    g.check(f'{BOX} granted or already held', reply is not None and BOX in reply.get('granted', []), reply)
    reply = ask(pell, 'outdoors_botanist')
    g.note(f'profession root as a box: {reply}')

    found = pell.locate('Botanist', 60) or pell.locate('trainer_botanist', 60)
    g.check('a Botanist trainer stands in Mos Eisley', bool(found), found[:1] if found else pell.status().get('x'))
    if found:
        trainer = found[0]
        g.note(f'trainer: {trainer.get("name")} at {trainer.get("x")},{trainer.get("y")}')
        events = pell.talk(trainer['oid'], wait=4)
        texts = [str(e.get('text', '')) for e in events if e.get('text')]
        options = pell.status().get('conversation_options', [])
        g.check('the trainer talks (stock trainer conversation)', bool(texts or options), dict(texts=texts[:4], options=options))
