"""Read-only prerequisite closures and CH skill modifiers from local client data."""
import json
import contextlib
import io
from collections import Counter
import swg_client_data as data

with contextlib.redirect_stdout(io.StringIO()):
    rows = data.datatable(data.client_file('datatables/skill/skills.iff'))
skills = {r['NAME']: r for r in rows}

def closure(goals):
    seen = set()
    def visit(name):
        if name in seen:
            return
        if name not in skills:
            raise ValueError(name)
        seen.add(name)
        for prerequisite in skills[name].get('SKILLS_REQUIRED', '').split(','):
            if prerequisite:
                visit(prerequisite)
    for goal in goals:
        visit(goal)
    return sorted(seen)

def build(goals):
    names = closure(goals)
    points = sum(skills[n].get('POINTS_REQUIRED', 0) for n in names)
    return {'goals': goals, 'points': points, 'remaining_of_250': 250-points, 'skills': names}

ch = closure(['outdoors_creaturehandler_master'])
mods = Counter()
for n in ch:
    if n.startswith('outdoors_creaturehandler_'):
        for entry in skills[n].get('SKILL_MODS', '').split(','):
            if '=' in entry:
                key, value = entry.split('=')
                mods[key] += int(value)
result = {
    'scope': 'Resolved local client skills table, not verified server runtime; login config may be missing',
    'ch_mods': dict(mods),
    'builds': [build(g) for g in [
        ['outdoors_creaturehandler_master'],
        ['outdoors_creaturehandler_master', 'combat_rifleman_master', 'science_medic_novice'],
        ['outdoors_creaturehandler_master', 'combat_unarmed_master', 'science_medic_novice'],
        ['outdoors_creaturehandler_master', 'outdoors_bio_engineer_master'],
    ]],
    'ch_rows': [skills[n] for n in ch if n.startswith('outdoors_creaturehandler_')],
}
print(json.dumps(result, indent=2))
