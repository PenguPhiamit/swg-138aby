"""Run the creation sweep's own data checks against the staged archive instead of the installed one.

The staged local_planets-creation-fixes.tre takes the installed archive's place (first in the load order); everything
else is read as the sweep reads it (stock client archives). starting_item_check needs the test galaxy's server scripts,
so run this inside WSL (read-only; nothing under /opt/swg is written):
    wsl -d Debian -u swgemu -- python3 -I <this file>
"""
import importlib.util
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUTS = HERE.parent.parent
STAGED = HERE / 'local_planets-creation-fixes.tre'
spec = importlib.util.spec_from_file_location('creation_sweep', OUTPUTS / 'tools/bots/scenarios/creation-sweep.py')
cs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cs)


def read_staged(rel):
    data = cs.iff.open_tre_entry(str(STAGED), rel)
    if data is not None:
        return data, STAGED.name
    data = cs.iff.client_file(rel)
    return data, cs.iff.client_index().get(rel.lower()) if data is not None else None


def main():
    results = cs.data_checks(cs.load_tables(read_staged)) + [cs.starting_item_check(read_staged)]
    for label, ok, detail in results:
        print('%-5s %s: %s' % ({True: 'PASS', False: 'FAIL', None: 'SKIP'}[ok], label, detail))
    return 0 if all(ok for _, ok, _ in results) else 1


if __name__ == '__main__':
    sys.exit(main())
