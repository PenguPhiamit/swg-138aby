"""Botanist feasibility test, server half (owner, 14 Oct). Does the test galaxy know the new box, grant it, show the
trainer, and keep the box across a relog? One bot (Pell, a Besh gatherer), test galaxy only. /agentskill is the bots'
training helper; it grants a box with its prerequisites and answers "[agentskill] {json}" (granted/failed/unknown).

    wsl -d Debian -u swgemu -- python3 .../tools/bots/squad.py run .../tools/owner_content/botanist_check.py --group Besh
Run it twice with a relog of Pell in between: the second run's first check then shows whether the box persisted.
"""
import json

GROUP = 'Besh'
BOX = 'outdoors_botanist_novice'
TRAINER_SPOT = (3516.0, -4783.0)  # the trainer's spawn line in Mos Eisley (dev 578861d9)


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


def trainer_says(pell, trainer):
    events = pell.talk(trainer['oid'], wait=4)
    texts = [str(e.get('text', '')) for e in events if e.get('text')]
    return texts, pell.status().get('conversation_options', [])


def run(g):
    pell = g['Pell']
    # The trainer first, before any /agentSkill: the bot's status has no skill list, so the trainer's answer is the
    # evidence of what Pell already holds ("@skill_teacher:topped_out" = Novice held, e.g. after a relog). /agentSkill
    # reports a box it re-grants as "granted", so asking first would hide a lost box (08:37 run).
    # Search around the trainer's spawn spot, not around Pell (06:29: Pell stood in the gather field, 250 m away).
    tx, ty = TRAINER_SPOT
    found = pell.locate('Botanist', 40, x=tx, y=ty) or pell.locate('trainer_botanist', 40, x=tx, y=ty)
    g.check('a Botanist trainer stands in Mos Eisley', bool(found), found[:1] if found else pell.status().get('x'))
    trainer = found[0] if found else None
    if trainer:
        g.note(f'trainer: {trainer.get("name")} at {trainer.get("x")},{trainer.get("y")}')
        walked = pell.walk(trainer['x'] + 2, trainer['y'])  # conversations need the NPC within a few metres
        g.note(f'walked to the trainer: {walked.get("arrived")}, {walked.get("seconds")} s')
        texts, options = trainer_says(pell, trainer)
        g.check('the trainer talks (stock trainer conversation)', bool(texts or options), dict(texts=texts[:4], options=options))
        g.note(f'BOTANIST before asking: Pell holds {BOX}: {any("topped_out" in t for t in texts)} (trainer: {texts[:2]})')

    reply = ask(pell, BOX)
    g.check(f'server knows {BOX} (not "unknown")', reply is not None and BOX not in reply.get('unknown', []), reply)
    g.check(f'{BOX} granted or already held', reply is not None and BOX in reply.get('granted', []), reply)
    reply = ask(pell, 'outdoors_botanist')
    g.note(f'profession root as a box: {reply}')
    if trainer:
        texts, options = trainer_says(pell, trainer)
        g.check('after the grant the trainer has nothing more to teach', any('topped_out' in t for t in texts),
                dict(texts=texts[:4], options=options))
