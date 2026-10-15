"""Server-side population bots (/botpop, milestone 1 of Documentation-support/server-side-bots.md): how many can the
test galaxy carry? Uses load_fleet.py's sampler and its memory stops (WSL MemAvailable under 4 GB or Windows commit
headroom under 6 GB: every population bot is logged out at once).

Run inside Debian as swgemu, with the test galaxy started with --dev-server and --config 'BotPop=true':
  botpop_scale.py step N [WHERE] [WARMUP_S] [SAMPLE_S] [MODE]
                                                          bring the population to N bots (WHERE: split (default),
                                                          mos_eisley, coronet, here), let them run, sample, summarise.
                                                          MODE: throttled (default) or all; switching logs every
                                                          bot out first (the server only switches with none online)
  botpop_scale.py status                                 the server's /botpop status
  botpop_scale.py down                                   log every population bot out
The commands go through one squad bot with an AgentAccounts entry (VIA, default esk3; override with BOTPOP_VIA=<account>),
which also stands in Mos Eisley as the "real player" the active budget looks for and measures the chat round trip.
Summaries: /var/tmp/swg-bots/load/botpop-N-WHERE-MODE.json. The server's own once-a-minute "[BotPop]" lines are
copied in.
"""
import json, os, re, sys, threading, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import load_fleet as lf  # noqa: E402
from squad import BotDown, Group, load_spec  # noqa: E402

VIA = os.environ.get('BOTPOP_VIA', 'esk3')
STATS = re.compile(r'\[BotPop\] INFO - (.*)')


def via_bot():
    for name, spec in load_spec()['groups'].items():
        group = Group(name, spec)
        for bot in group.bots:
            if bot.account == VIA:
                return bot
    raise SystemExit(f'no squad bot with account {VIA}')


def botpop(bot, args, wait=8):
    """One /botpop command; the server's JSON answer, or an error dict."""
    bot.slash('botPop', args, wait=0)
    answer = bot.wait_for(lambda e: str(e.get('text', '')).startswith('[botpop]'), wait)
    try:
        return json.loads(answer['text'][len('[botpop] '):])
    except (TypeError, KeyError, ValueError):
        return {'ok': False, 'error': 'no answer (dev server? Core3.BotPop = true? account in AgentAccounts?)'}


def stats_lines(start):
    with open(lf.LOG, 'rb') as stream:
        stream.seek(start)
        text = stream.read().decode('utf-8', 'replace')
    return [m.group(1) for m in map(STATS.search, text.splitlines()) if m]


def use_mode(bot, mode):
    """Switch the server to `mode`, logging every bot out first when it runs the other one."""
    status = botpop(bot, 'status')
    if status.get('mode') == mode:
        return status
    if status.get('online') or status.get('queued_spawn'):
        print('switching to', mode, ': logging out', status.get('online'), 'bots', botpop(bot, 'despawn all'))
    deadline = time.time() + 300
    while time.time() < deadline:
        status = botpop(bot, 'status')
        if not (status.get('online') or status.get('leaving') or status.get('queued_logout')):
            break
        time.sleep(5)
    print('mode', botpop(bot, f'mode {mode}'))
    return botpop(bot, 'status')


def step(n, where, warmup, sample_s, mode='throttled'):
    lf.OUT.mkdir(parents=True, exist_ok=True)
    bot = via_bot()
    print('via', bot.first, lf.bring_up(bot, 'mos_eisley'))
    use_mode(bot, mode)
    sampler = lf.Sampler()
    sampler.start()
    log_begin = lf.LOG.stat().st_size
    began = time.time()

    before = botpop(bot, 'status')
    need = n - before.get('online', 0) - before.get('queued_spawn', 0)
    asked = botpop(bot, f'spawn {need} {where}') if need > 0 else {'ok': True, 'queued': 0}
    print('status before', before, '\nspawn', asked)

    polls, status = [], {}
    deadline = time.time() + 120 + n / 10
    while time.time() < deadline and not lf.TRIP.is_set():
        status = botpop(bot, 'status')
        polls.append(dict(status, t=round(time.time() - began)))
        if status.get('online', 0) >= n or (status.get('queued_spawn', 0) == 0 and status.get('ok')):
            break
        lf.TRIP.wait(5)
    up_seconds = round(time.time() - began)
    print('up after', up_seconds, 's:', status)

    rtts, sample_begin = [], None
    if not lf.TRIP.is_set():
        until = time.time() + warmup + sample_s
        prober = threading.Thread(target=lf.probe, args=(bot, until, rtts), daemon=True)
        if not lf.TRIP.wait(warmup):
            sampler.phase = 'sample'
            rtts.clear()
            sample_begin = lf.LOG.stat().st_size
            prober.start()
            end = time.time() + sample_s
            while time.time() < end and not lf.TRIP.is_set():
                lf.TRIP.wait(min(60, max(1, end - time.time())))
            prober.join(timeout=30)
    sampler.done.set()
    sampler.join(timeout=15)
    try:
        final = botpop(bot, 'status')
    except BotDown as exc:
        final = {'ok': False, 'error': f'via bot down: {exc}'}

    window = [r for r in sampler.rows if r['phase'] == 'sample']
    summary = {
        'population_asked': n, 'where': where, 'mode': mode, 'spawn_answer': asked, 'up_seconds': up_seconds,
        'status_at_end': final, 'sample_seconds': sample_s if window else 0, 'samples': len(window),
        'core3_cores': lf.stats([r.get('core3_cores') for r in window]),
        'core3_rss_mb': lf.stats([r.get('core3_rss_mb') for r in window]),
        'core3_rss_mb_before': sampler.rows[0].get('core3_rss_mb') if sampler.rows else None,
        'bodies': lf.stats([r['bodies'] for r in window]),
        'wsl_available_mb': lf.stats([r.get('wsl_available_mb') for r in window]),
        'commit_headroom_mb': lf.stats([r.get('commit_headroom_mb') for r in window]),
        'chat_rtt_ms': lf.stats(rtts), 'chat_rtt_missed': sum(r is None for r in rtts), 'chat_rtt_all': rtts,
        'server_log': lf.log_window(sample_begin) if sample_begin is not None else None,
        'botpop_lines': stats_lines(log_begin),
        'safety_stop': lf.TRIP_WHY[:1],
    }
    (lf.OUT / f'botpop-{n}-{where}-{mode}{os.environ.get("BOTPOP_TAG", "")}.json').write_text(json.dumps({'summary': summary, 'polls': polls,
                                                                 'rows': sampler.rows}, indent=1))
    print(json.dumps({k: v for k, v in summary.items() if k != 'chat_rtt_all'}, indent=1))
    if lf.TRIP.is_set():
        print('SAFETY STOP:', lf.TRIP_WHY[0], '- logging every population bot out')
        print(botpop(bot, 'despawn all'))


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    if args[0] == 'step':
        step(int(args[1]), args[2] if len(args) > 2 else 'split', int(args[3]) if len(args) > 3 else 120,
             int(args[4]) if len(args) > 4 else 300, args[5] if len(args) > 5 else 'throttled')
    elif args[0] in ('status', 'down'):
        bot = via_bot()
        print(json.dumps(botpop(bot, 'status' if args[0] == 'status' else 'despawn all'), indent=1))
    else:
        raise SystemExit(__doc__)
