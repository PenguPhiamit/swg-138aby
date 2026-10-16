"""Summarize saved bot reports without interpreting teleport packets as rejection reasons.

python outputs/tools/bots/movement_evidence.py REPORT.json [...] --output RESULT.json
No bot/server/network access. Output contains numeric movement evidence, not raw chat.
"""
import argparse
import hashlib
import json
from pathlib import Path


def summarize(path):
    raw = path.read_bytes()
    report = json.loads(raw)
    result = {'report': path.name, 'sha256': hashlib.sha256(raw).hexdigest(),
              'correction_events': {}, 'posture_event_count': 0, 'moves': [],
              'reason': 'undetermined: position_set_by_server carries no rejection reason'}
    for bot, events in report.get('events', {}).items():
        corrections = [e for e in events if e.get('event') == 'position_set_by_server']
        result['correction_events'][bot] = len(corrections)
        result['posture_event_count'] += sum(e.get('event') == 'posture' for e in events)
    for step in report.get('steps', []):
        try:
            request = json.loads(step.get('request', ''))
        except (ValueError, TypeError):
            continue
        if request.get('cmd') != 'move':
            continue
        try:
            reply = json.loads(step.get('reply', ''))
        except (ValueError, TypeError):
            reply = {}  # Reports truncate replies; never invent the omitted fields.
        error = reply.get('error', '')
        if 'keeps putting us back' in error:
            outcome = 'generic correction failure'
        elif error == 'timeout':
            outcome = 'timeout'
        elif reply.get('arrived') is True:
            outcome = 'arrived'
        else:
            outcome = 'unavailable/truncated reply'
        result['moves'].append({'bot': step.get('bot'), 'completion_t': step.get('t'),
                                'cell': request.get('cell', 0), 'explicit_z': 'z' in request,
                                'destination': {k: request[k] for k in ('x', 'y', 'z') if k in request},
                                'outcome': outcome, 'final_position': {k: reply[k] for k in ('x', 'y', 'z') if k in reply}})
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('reports', nargs='+', type=Path)
    p.add_argument('--output', required=True, type=Path)
    args = p.parse_args()
    data = [summarize(path) for path in args.reports]
    args.output.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
    print(f'{len(data)} saved reports summarized; no cause inferred from generic position events.')


if __name__ == '__main__':
    main()
