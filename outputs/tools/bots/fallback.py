"""Pure per-group scenario chooser. No processes, credentials or game I/O."""
import hashlib
from pathlib import Path


def revision(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def problems(report):
    reasons = {'FAIL: ' + c['label'] for c in report.get('checks', []) if not c['ok']}
    reasons.update(n for n in report.get('notes', []) if n.startswith(('BLOCKED', 'ERROR')))
    if report.get('error'):
        reasons.add('ERROR: ' + report['error'])
    if not report.get('checks') and not reasons:
        reasons.add('BLOCKED: scenario produced no checks')
    return reasons


class Chooser:
    def __init__(self, state=None, return_after=3):
        self.state = state if state is not None else {}
        self.return_after = return_after

    def select(self, group, main, fallbacks):
        main = str(Path(main).resolve())
        digest = revision(main)
        row = self.state.setdefault(group, {})
        changed = row.get('main') != main or row.get('revision') != digest
        if changed:
            row.clear()
            row.update(main=main, revision=digest, active=main, passes=0,
                       reasons={}, fallback_rounds=0, cursor=0,
                       why='main scenario selected or changed')
        choices = [str(Path(p).resolve()) for p in fallbacks
                   if Path(p).is_file() and str(Path(p).resolve()) != main]
        if row.get('active') != main and row.get('active') not in choices:
            row.update(active=main, fallback_rounds=0, passes=0, reasons={},
                       why='fallback unavailable; return to main')
        row['choices'] = choices
        return Path(row['active']), dict(main=Path(main).name,
                    fallback=row['active'] != main, reason=row['why'])

    def observe(self, group, report):
        row = self.state[group]
        timed_out = report.get('state') == 'stopped' and 'run time budget reached' in str(report.get('error', ''))
        if report.get('state') == 'stopped' and not timed_out:
            return None  # a halt/deadline is never a failure or a reason to start more work
        issues = problems(report)
        if timed_out:
            issues = {'BLOCKED: round time budget reached'}
        row['passes'] = row.get('passes', 0) + 1 if not issues and report.get('checks') else 0
        previous = row.get('reasons', {})
        row['reasons'] = {r: previous.get(r, 0) + 1 for r in issues}
        if row['active'] != row['main']:
            row['fallback_rounds'] += 1
            if row['fallback_rounds'] >= self.return_after:
                return self._change(row, row['main'], 'scheduled main retry after fallback rounds')
        repeated = sorted(r for r, count in row['reasons'].items() if count >= 2)
        reason = ('all checks passed for two consecutive rounds' if row['passes'] >= 2 else
                  'same problem twice: ' + repeated[0] if repeated else None)
        if reason and row['choices']:
            for _ in row['choices']:
                target = row['choices'][row['cursor'] % len(row['choices'])]
                row['cursor'] += 1
                if target != row['active']:
                    return self._change(row, target, reason)
        return None

    @staticmethod
    def _change(row, target, reason):
        old = row['active']
        # Preserve the total fallback lease across rotations so the main is retried.
        if old == row['main'] or target == row['main']:
            row['fallback_rounds'] = 0
        row.update(active=target, passes=0, reasons={}, why=reason)
        return dict(previous=Path(old).name, next=Path(target).name, reason=reason)
