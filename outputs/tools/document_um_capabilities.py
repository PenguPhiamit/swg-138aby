"""Read installed UM parser definitions; export command help without executing commands."""
import argparse
import hashlib
import importlib
import sys
from pathlib import Path

ROOT = Path('C:/Users/Pengw/.codex/plugins/cache/universal-modder/universal-modder/0.2.0')
OUT = Path(__file__).resolve().parents[1] / 'Documentation-support'
sys.path.insert(0, str(ROOT))
from um.cli import GROUPS

parser = argparse.ArgumentParser(prog='um')
sub = parser.add_subparsers(dest='group')
for name in GROUPS:
    importlib.import_module('um.' + name).register(sub)

lines = ['# Universal Modder 0.2.0: complete CLI command and option reference', '',
         'Generated from the installed argparse definitions. No command actions executed.', '',
         'This is the installed version, not a promise about future releases.', '']
commands = []

def visit(current, path):
    commands.append(path)
    lines.extend(['## ' + path, '', '```text', current.format_help().rstrip(), '```', ''])
    for action in current._actions:
        if isinstance(action, argparse._SubParsersAction):
            for name, child in action.choices.items():
                visit(child, path + ' ' + name)

visit(parser, 'um')
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'universal-modder-CLI-reference.md').write_text('\n'.join(lines), encoding='utf-8')
evidence = ['# Installed UM source inventory', '', 'Version: 0.2.0. Read-only hashes, no credential files.', '',
            '| Relative path | SHA-256 |', '|---|---|']
paths = [ROOT / 'README.md', ROOT / 'pyproject.toml', ROOT / '.mcp.json', ROOT / 'hooks/hooks.json']
paths += sorted((ROOT / 'um').rglob('*.py'))
paths += sorted((ROOT / 'skills').rglob('*.md'))
for path in paths:
    if path.is_file():
        evidence.append(f'| `{path.relative_to(ROOT).as_posix()}` | `{hashlib.sha256(path.read_bytes()).hexdigest()}` |')
(OUT / 'universal-modder-source-inventory.md').write_text('\n'.join(evidence) + '\n', encoding='utf-8')
print(f'Exported {len(commands)} parser entries and {len(paths)} source paths.')
