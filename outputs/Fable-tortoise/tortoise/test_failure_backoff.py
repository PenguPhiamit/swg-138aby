"""Regression tests for failure_backoff.py. Cases 1-15 are ported from TortoiseBots
`tools/test_engine_failure_backoff.cpp` (TortoiseBots by Sagiroth, https://github.com/Sagiroth/TortoiseBots,
AGPL-3.0 with the attribution term; the original test file carries no per-file notice). Cases 16-20 are ours.
Run: python test_failure_backoff.py   (prints PASS <n> checks or the first FAIL and exits 1)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from failure_backoff import (ActionFailureBackoff, TransitionTracker, Retry, Impossible, decide,
                             RESULT_FAILED, RESULT_IMPOSSIBLE)

checks = 0


def check(cond, what):
    global checks
    checks += 1
    if not cond:
        print(f'FAIL {checks}: {what}')
        sys.exit(1)


FAILED, IMPOSSIBLE = 4, 2  # the original Engine result codes used by the ported cases
T = TransitionTracker


def main():
    # 1. Unknown keys never back off.
    b = ActionFailureBackoff()
    check(not b.is_backed_off('nothing|here|0|0|4', 1000), '1 unknown key')
    check(b.size() == 0, '1 size')

    # 2. Exponential growth then cap: base 250, max 2000.
    b = ActionFailureBackoff()
    k = ActionFailureBackoff.key('gather', 'node', 7, 0, FAILED)
    b.record(k, 10000, 250, 2000, 64, 30000)
    check(b.is_backed_off(k, 10249) and not b.is_backed_off(k, 10250), '2 base 250')
    b.record(k, 10250, 250, 2000, 64, 30000)
    check(b.is_backed_off(k, 10749) and not b.is_backed_off(k, 10750), '2 +500')
    b.record(k, 10750, 250, 2000, 64, 30000)
    check(not b.is_backed_off(k, 11750), '2 +1000')
    b.record(k, 11750, 250, 2000, 64, 30000)
    check(not b.is_backed_off(k, 13750), '2 +2000 (shift 3)')
    b.record(k, 13750, 250, 2000, 64, 30000)
    check(b.is_backed_off(k, 15749) and not b.is_backed_off(k, 15750), '2 shift 4 capped to 2000')
    for i in range(20):
        b.record(k, 15750 + i, 250, 2000, 64, 30000)
    check(not b.is_backed_off(k, 15750 + 19 + 2000), '2 saturation never passes the cap')
    check(b.size() == 1, '2 one entry')

    # 3. Success clears both result variants.
    b = ActionFailureBackoff()
    kf = ActionFailureBackoff.key('gather', 'node', 7, 0, FAILED)
    ki = ActionFailureBackoff.key('gather', 'node', 7, 0, IMPOSSIBLE)
    b.record(kf, 1000, 250, 2000, 64, 30000)
    b.record(ki, 1000, 250, 2000, 64, 30000)
    check(b.size() == 2, '3 two variants')
    b.clear(kf, ki)
    check(b.size() == 0 and not b.is_backed_off(kf, 1001), '3 cleared')

    # 4. TTL expiry prunes stale entries, keeps fresh ones.
    b = ActionFailureBackoff()
    b.record('old', 0, 250, 2000, 64, 30000)
    b.record('new', 30900, 250, 2000, 64, 30000)
    b.prune(31000, 30000, True)
    check(b.size() == 1 and not b.is_backed_off('old', 31000) and b.is_backed_off('new', 31000), '4 ttl prune')

    # 5. Overflow evicts the stalest entry first; size stays bounded.
    b = ActionFailureBackoff()
    b.record('a', 0, 5000, 20000, 2, 30000)
    b.record('b', 100, 5000, 20000, 2, 30000)
    b.record('c', 200, 5000, 20000, 2, 30000)
    check(b.size() == 2, '5 bounded')
    check(not b.is_backed_off('a', 1000) and b.is_backed_off('b', 1000) and b.is_backed_off('c', 1000), '5 stalest evicted')

    # 6. Zero base/max disables and empties the cache.
    b = ActionFailureBackoff()
    b.record('x', 0, 250, 2000, 64, 30000)
    check(b.size() == 1, '6 one')
    b.record('y', 0, 0, 2000, 64, 30000)
    check(b.size() == 0, '6 disabled empties')

    # 7. Key separates target, destination and result.
    a = ActionFailureBackoff.key('go', 's', 1, 2, FAILED)
    check(a != ActionFailureBackoff.key('go', 's', 1, 3, FAILED), '7 dest')
    check(a != ActionFailureBackoff.key('go', 's', 1, 2, IMPOSSIBLE), '7 result')

    # 8. Steady presence never drains, including zone-line walking.
    t = T()
    check(t.update(True, False, 0, 0.0, 0.0, 0.0, 0) == T.NONE, '8 init')
    check(t.update(True, False, 0, 5.0, 0.0, 0.0, 0) == T.NONE, '8 walk')
    check(t.update(True, False, 0, 40.0, 30.0, 5.0, 0) == T.NONE and t.last_scene == 0, '8 walk 2')

    # 9. Teleport away and back on the same scene drains on arrival.
    t = T()
    check(t.update(True, False, 1, 0.0, 0.0, 0.0, 0) == T.NONE, '9 init')
    check(t.update(True, True, 1, 0.0, 0.0, 0.0, 0) == T.AWAY, '9 away')
    check(t.update(True, True, 1, 0.0, 0.0, 0.0, 0) == T.AWAY, '9 still away')
    check(t.update(True, False, 1, 500.0, 500.0, 0.0, 1) == T.TRANSITION, '9 transition')
    check(t.update(True, False, 1, 501.0, 500.0, 0.0, 1) == T.NONE, '9 settled')

    # 10. Leaving the world and returning drains even without teleport flags.
    t = T()
    check(t.update(True, False, 1, 0.0, 0.0, 0.0, 0) == T.NONE, '10 init')
    check(t.update(False, False, 1, 0.0, 0.0, 0.0, 0) == T.AWAY, '10 out of world')
    check(t.update(True, False, 1, 10.0, 0.0, 0.0, 0) == T.ARRIVED, '10 arrived')

    # 11. Scene change drains and re-baselines.
    t = T()
    check(t.update(True, False, 0, 0.0, 0.0, 0.0, 0) == T.NONE, '11 init')
    check(t.update(True, False, 1, 0.0, 0.0, 0.0, 0) == T.SCENE_CHANGED and t.last_scene == 1, '11 scene')
    check(t.update(True, False, 1, 1.0, 0.0, 0.0, 0) == T.NONE, '11 settled')

    # 12. Impossible jump on the same scene drains; sub-threshold never does.
    t = T()
    check(t.update(True, False, 0, 0.0, 0.0, 0.0, 0) == T.NONE, '12 init')
    check(t.update(True, False, 0, 99.0, 0.0, 0.0, 0) == T.NONE, '12 under threshold')
    check(t.update(True, False, 0, 500.0, 0.0, 0.0, 0) == T.JUMPED, '12 jumped')
    check(t.update(True, False, 0, 501.0, 0.0, 0.0, 0) == T.NONE, '12 settled')

    # 13. Short same-scene teleport with no AWAY seen: the generation bump still drains.
    t = T()
    check(t.update(True, False, 0, 0.0, 0.0, 0.0, 0) == T.NONE, '13 init')
    check(t.update(True, False, 0, 30.0, 0.0, 0.0, 1) == T.TRANSITION, '13 generation bump')
    check(t.update(True, False, 0, 31.0, 0.0, 0.0, 1) == T.NONE, '13 settled')

    # 14. Vertical displacement counts.
    t = T()
    check(t.update(True, False, 0, 0.0, 0.0, 100.0, 0) == T.NONE, '14 init')
    check(t.update(True, False, 0, 0.0, 0.0, 60.0, 0) == T.NONE, '14 drop 40')
    check(t.update(True, False, 0, 0.0, 0.0, -100.0, 0) == T.JUMPED, '14 drop 160')

    # 15. Mid-walk note_away marks arrival even with no other signal.
    t = T()
    check(t.update(True, False, 0, 0.0, 0.0, 0.0, 0) == T.NONE, '15 init')
    t.note_away()
    check(t.update(True, False, 0, 1.0, 0.0, 0.0, 0) == T.ARRIVED, '15 arrived')
    check(t.update(True, False, 0, 2.0, 0.0, 0.0, 0) == T.NONE, '15 settled')

    # ---- ours -------------------------------------------------------------------------------------------------
    # 16. decide(): deadline beats backoff; wait reports the remaining time; free keys go.
    b = ActionFailureBackoff()
    k = ActionFailureBackoff.key('walk', 'Kor', 0, '3475,-4622', RESULT_FAILED)
    check(decide(b, k, 1000) == (True, 'go', 0), '16 free key goes')
    b.record(k, 1000, 250, 2000, 64, 30000)
    check(decide(b, k, 1100) == (False, 'backed off', 150), '16 waits 150 ms')
    check(decide(b, k, 1100, deadline_ms=1050) == (False, 'deadline', 0), '16 deadline first')
    check(decide(b, k, 1250) == (True, 'go', 0), '16 free again')

    # 17. Retry with an injected clock: failures back off 250/500/1000 ms, success clears both variants.
    clock = {'now': 0}
    slept = []

    def tick():
        return clock['now']

    def sleep(s):
        slept.append(round(s * 1000))
        clock['now'] += round(s * 1000)

    calls = {'n': 0}

    def attempt():
        calls['n'] += 1
        return 'arrived' if calls['n'] == 4 else None

    r = Retry(clock=tick, sleep=sleep)
    result, attempts, reason = r.run('walk', 'Kor', attempt, dest='3475,-4622', tries=5)
    check((result, attempts, reason) == ('arrived', 4, 'ok'), f'17 success on 4th: {(result, attempts, reason)}')
    check(slept == [250, 500, 1000], f'17 waits {slept}')
    check(r.backoff.size() == 0, '17 success cleared the table')

    # 18. Retry: tries exhausted leaves the entry (next call still waits); Impossible is its own variant.
    clock['now'], slept[:] = 0, []
    r = Retry(clock=tick, sleep=sleep)

    def never():
        return None

    check(r.run('buy', 'Ilsa', never, target=42, tries=2)[1:] == (2, 'tries exhausted'), '18 exhausted')
    check(r.backoff.size() == 1, '18 entry kept')

    def impossible():
        raise Impossible('no terminal')

    r.run('buy', 'Ilsa', impossible, target=42, tries=1)
    check(r.backoff.size() == 2, '18 impossible variant separate')
    k_f = ActionFailureBackoff.key('buy', 'Ilsa', 42, 0, RESULT_FAILED)
    k_i = ActionFailureBackoff.key('buy', 'Ilsa', 42, 0, RESULT_IMPOSSIBLE)
    # the run waited out the failed variant (free exactly at 750 ms) before trying; the impossible one is fresh
    check(clock['now'] == 750 and not r.backoff.is_backed_off(k_f, 750) and r.backoff.is_backed_off(k_i, 750), '18 impossible active, failed waited out')
    check(k_f in r.backoff.failures and k_i in r.backoff.failures, '18 both entries kept')

    # 19. Retry: deadline stops before a wait that would pass it; scene change clears the table.
    clock['now'], slept[:] = 0, []
    r = Retry(clock=tick, sleep=sleep)
    r.run('buy', 'Ilsa', never, target=42, tries=1)          # entry: retry after 250
    result = r.run('buy', 'Ilsa', never, target=42, tries=1, deadline_ms=100)
    check(result == (None, 0, 'backed off') and slept == [], f'19 would pass deadline: {result} {slept}')
    clock['now'] = 100
    check(r.run('buy', 'Ilsa', never, target=42, tries=1, deadline_ms=100) == (None, 0, 'deadline'), '19 deadline')
    check(r.observe(T.SCENE_CHANGED) == T.SCENE_CHANGED and r.backoff.size() == 0, '19 scene change clears')
    r.run('buy', 'Ilsa', never, target=42, tries=1)
    check(r.observe(T.NONE) == T.NONE and r.backoff.size() == 1, '19 NONE keeps')

    # 20. Keys are plain strings with a stable layout, so logs and tests can read them.
    check(ActionFailureBackoff.key('walk', 'Kor', 6076175, 'tatooine', 'failed') == 'walk|Kor|6076175|tatooine|failed', '20 key text')

    print(f'PASS test_failure_backoff ({checks} checks)')


if __name__ == '__main__':
    main()
