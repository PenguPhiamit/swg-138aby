"""Cooperative scenario cancellation and observational activity records; no bot I/O."""
import json
import os
import time
import threading
from pathlib import Path


class RunStopped(Exception):
    pass


class RunControl:
    def __init__(self, folder, group, scenario, deadline=None):
        self.folder = Path(folder)
        self.group, self.scenario, self.deadline = group, scenario, deadline
        self.path = self.folder / (group + '-activity.json')
        self.lock = threading.Lock()

    def reason(self):
        if (self.folder / 'STOP').exists():
            return 'owner requested halt'
        if self.deadline is not None and time.monotonic() >= self.deadline:
            return 'run time budget reached'
        return None

    def publish(self, state, detail=''):
        self.folder.mkdir(parents=True, exist_ok=True)
        data = dict(group=self.group, scenario=self.scenario, state=state,
                    detail=detail, updated=time.time(), pid=os.getpid(),
                    stop_requested=self.reason())
        temporary = self.path.with_suffix('.tmp')
        with self.lock:
            temporary.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
            temporary.replace(self.path)

    def checkpoint(self):
        reason = self.reason()
        if reason:
            self.publish('stopped', reason)
            raise RunStopped(reason)

    def sleep(self, seconds):
        until = time.monotonic() + max(0, seconds)
        while True:
            self.checkpoint()
            remaining = until - time.monotonic()
            if remaining <= 0:
                return
            time.sleep(min(.2, remaining))


def read_activity(folder, stale_after=120):
    """Read saved observations, never infer that an old record is current."""
    rows = []
    for path in sorted(Path(folder).glob('*-activity.json')):
        try:
            row = json.loads(path.read_text(encoding='utf-8'))
            row['age_seconds'] = max(0, round(time.time() - row['updated']))
            row['stale'] = row['age_seconds'] > stale_after
            rows.append(row)
        except (OSError, ValueError, TypeError, KeyError):
            rows.append(dict(group=path.stem, state='unreadable', stale=True))
    return rows
