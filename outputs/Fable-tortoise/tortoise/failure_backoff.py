"""Bounded failure backoff and scene-transition tracking for bot actions. Pure policy: no bot, server or file I/O.

TortoiseBots by Sagiroth (https://github.com/Sagiroth/TortoiseBots).
Ported to Python from TortoiseBots `ai/playerbot/strategy/ActionFailureBackoff.h` (classes ActionFailureBackoff
and TransitionTracker, "issue #84"), under the owner's full-use authorisation from the author and the file's
licence: GNU AGPL-3.0 with the TortoiseBots attribution term (LICENCE.md: modified versions, forks, repacks and
bundles must keep the author attribution and the source link; you may add your own credit alongside). The
original file carries no per-file notice of its own; this header is the retained notice.
Lineage flag: the original header says its semantics were "ported from the Shyalya runtime reference"
(Shyalya/tortoise-wow, AGPL-3.0 per TortoiseBots docs/LICENSE_AUDIT.md), so the idea predates TortoiseBots;
the code ported here is Sagiroth's file. Python port and the SWG additions (`decide`, `Retry`, `Impossible`)
by Fable, 14 October 2026, also AGPL-3.0.

Semantics kept from the original:
- One entry per key = (action, source, target, destination, result). Repeated failures back off exponentially:
  base, 2x, 4x, 8x, 16x, capped at max.
- The table is bounded twice: entries expire after a TTL, and overflow evicts the stalest entry first.
- Success clears the entry; scene changes and explicit commands clear everything.
- Times are caller milliseconds (ints). The original compares uint32 times with wrap-around; Python ints do not
  wrap, so callers pass a monotonic clock (now_ms()) and never wall-clock seconds.
"""
import time
from collections import namedtuple


def now_ms():
    """Monotonic milliseconds, the clock every method here expects."""
    return int(time.monotonic() * 1000)


class ActionFailureState:
    __slots__ = ('failures', 'retry_after_ms', 'last_failure_ms')

    def __init__(self):
        self.failures = 0
        self.retry_after_ms = 0
        self.last_failure_ms = 0


class ActionFailureBackoff:
    """One bounded table of failing (action, source, target, destination, result) keys and when to retry each."""

    def __init__(self):
        self.failures = {}
        self.last_prune_ms = 0

    @staticmethod
    def key(action, source, target=0, dest=0, result=0):
        """Original: action|source|targetGuid|destGuid|result. Here target/dest/result may be any value with a
        stable str(); SWG callers pass object ids, 'x,y' strings or planet names."""
        return '|'.join(str(part) for part in (action, source, target, dest, result))

    def is_backed_off(self, key, now):
        state = self.failures.get(key)
        return state is not None and state.retry_after_ms - now > 0

    def retry_after(self, key, now):
        """Milliseconds still to wait for key (0 when free). Our addition for the decision helpers below."""
        state = self.failures.get(key)
        return max(0, state.retry_after_ms - now) if state else 0

    def record(self, key, now, base_ms, max_ms, max_entries, ttl_ms):
        """Record one failure. Zero base/max disables (and empties) the table."""
        if not base_ms or not max_ms:
            self.clear_all()
            return
        max_entries = max(1, max_entries)
        self.prune(now, ttl_ms, len(self.failures) >= max_entries)
        state = self.failures.get(key)
        if state is None:
            if len(self.failures) >= max_entries:
                self._evict_oldest(now)
            state = self.failures[key] = ActionFailureState()
        state.failures = min(16, state.failures + 1)
        shift = min(4, state.failures - 1)
        delay = base_ms << shift
        state.retry_after_ms = now + min(delay, max_ms)
        state.last_failure_ms = now

    def clear(self, first, second=None):
        """Drop the entries for both result variants of one action event."""
        self.failures.pop(first, None)
        if second is not None:
            self.failures.pop(second, None)

    def clear_all(self):
        self.failures.clear()
        self.last_prune_ms = 0

    def size(self):
        return len(self.failures)

    __len__ = size

    def prune(self, now, ttl_ms, enforce_limit=False):
        if not self.failures:
            return
        interval = min(ttl_ms, 5000)
        if not enforce_limit and self.last_prune_ms and now - self.last_prune_ms < interval:
            return
        self.last_prune_ms = now
        for key in [k for k, s in self.failures.items() if now - s.last_failure_ms >= ttl_ms]:
            del self.failures[key]

    def _evict_oldest(self, now):
        oldest, oldest_age = None, -1
        for key, state in self.failures.items():
            age = now - state.last_failure_ms
            if oldest is None or age > oldest_age:
                oldest, oldest_age = key, age
        if oldest is not None:
            del self.failures[oldest]


class TransitionTracker:
    """Tells a caller when the bot's scene changed so backoff state can be dropped. Original: map id, 3D position
    and a teleport-ack generation counter. Here `scene` is any hashable (we pass the planet name or
    (planet, cell)); `generation` is a counter the caller bumps when it knows a transition happened, 0 if none.
    Positions are metres; the jump threshold defaults to the original 100 units, which fits our 2 s status polls
    (a walking bot covers well under 100 m between polls)."""
    NONE, AWAY, ARRIVED, SCENE_CHANGED, JUMPED, TRANSITION = 'none', 'away', 'arrived', 'scene_changed', 'jumped', 'transition'

    def __init__(self, jump_threshold=100.0):
        self.jump_threshold = float(jump_threshold)
        self.initialized = False
        self.was_away = False
        self.last_scene = None
        self.last_x = self.last_y = self.last_z = 0.0
        self.last_gen = 0

    def update(self, in_world, teleporting, scene, x, y, z=0.0, generation=0):
        if not in_world or teleporting:
            self.was_away = True
            return self.AWAY
        if not self.initialized:
            self._snapshot(scene, x, y, z, generation)
            self.initialized = True
            self.was_away = False
            return self.NONE
        if generation != self.last_gen:  # explicit signal first: covers short same-scene hops
            self._snapshot(scene, x, y, z, generation)
            self.was_away = False
            return self.TRANSITION
        if self.was_away:
            self._snapshot(scene, x, y, z, generation)
            self.was_away = False
            return self.ARRIVED
        if scene != self.last_scene:
            self._snapshot(scene, x, y, z, generation)
            return self.SCENE_CHANGED
        dx, dy, dz = x - self.last_x, y - self.last_y, z - self.last_z
        if dx * dx + dy * dy + dz * dz > self.jump_threshold * self.jump_threshold:
            self._snapshot(scene, x, y, z, generation)
            return self.JUMPED
        self._snapshot(scene, x, y, z, generation)
        return self.NONE

    def note_away(self):
        """Mark the tracker away when a walk observes a transition mid-stride, so arrival drains anyway."""
        self.was_away = True

    def _snapshot(self, scene, x, y, z, generation):
        self.last_scene, self.last_x, self.last_y, self.last_z, self.last_gen = scene, x, y, z, generation


# ---- SWG additions (ours): pure decisions a scenario can call before each retry --------------------------------

Decision = namedtuple('Decision', 'go reason wait_ms')

RESULT_FAILED, RESULT_IMPOSSIBLE = 'failed', 'impossible'


class Impossible(Exception):
    """Raise from an attempt when the action cannot work at all here (no such terminal, no route): it is recorded
    under the 'impossible' result so the two variants stay separate, as in the original Engine."""


def decide(backoff, key, now, deadline_ms=None):
    """Go, wait (how long) or stop: the only three answers. Deadline first, then the backoff table."""
    if deadline_ms is not None and now >= deadline_ms:
        return Decision(False, 'deadline', 0)
    if backoff.is_backed_off(key, now):
        return Decision(False, 'backed off', backoff.retry_after(key, now))
    return Decision(True, 'go', 0)


class Retry:
    """Run an attempt until it succeeds, backing off between failures. Clock and sleep are injected so tests and
    scenario dry runs never wait. Scene changes (TransitionTracker events other than NONE) clear the table, as
    the original Engine does on map change."""

    def __init__(self, base_ms=250, max_ms=2000, max_entries=64, ttl_ms=30000, clock=now_ms, sleep=time.sleep):
        self.backoff = ActionFailureBackoff()
        self.base_ms, self.max_ms, self.max_entries, self.ttl_ms = base_ms, max_ms, max_entries, ttl_ms
        self.clock, self.sleep = clock, sleep

    def observe(self, event):
        if event != TransitionTracker.NONE:
            self.backoff.clear_all()
        return event

    def run(self, action, source, attempt, target=0, dest=0, tries=3, deadline_ms=None):
        """attempt() returns a truthy value on success, falsy on failure, or raises Impossible.
        Returns (result or None, attempts made, reason) where reason is 'ok', 'deadline', 'backed off' (waiting
        would pass the deadline) or 'tries exhausted'."""
        failed = ActionFailureBackoff.key(action, source, target, dest, RESULT_FAILED)
        impossible = ActionFailureBackoff.key(action, source, target, dest, RESULT_IMPOSSIBLE)
        attempts = 0
        for _ in range(max(1, tries)):
            now = self.clock()
            waits = max(self.backoff.retry_after(failed, now), self.backoff.retry_after(impossible, now))
            if deadline_ms is not None and now >= deadline_ms:
                return None, attempts, 'deadline'
            if waits:
                if deadline_ms is not None and now + waits >= deadline_ms:
                    return None, attempts, 'backed off'
                self.sleep(waits / 1000.0)
                now = self.clock()
            attempts += 1
            try:
                result = attempt()
            except Impossible:
                self.backoff.record(impossible, now, self.base_ms, self.max_ms, self.max_entries, self.ttl_ms)
                continue
            if result:
                self.backoff.clear(failed, impossible)
                return result, attempts, 'ok'
            self.backoff.record(failed, now, self.base_ms, self.max_ms, self.max_entries, self.ttl_ms)
        return None, attempts, 'tries exhausted'
