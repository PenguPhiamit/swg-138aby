"""Isolated C4f-F2 lookup/build-input check, never calls main or publishes."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
H = HERE.parents[2]
spec = importlib.util.spec_from_file_location('review_fixed_build', H / 'outputs/tools/hoth/hoth_client_build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)
order = build.swg_client_data.clo.load_order
trees, second, third = order()
build.swg_client_data.clo.load_order = lambda: ([(0, 'local_planets.tre'), *trees], second, third)
build._stock_index = None
selected = build.winning('datatables/skill/skills.iff')[0]
assert selected.lower() != 'local_planets.tre'
stage = Path(build.STAGE)
paths = ['datatables/skill/skills.iff', *build.BOTANIST_STRINGS]
before = {p: hashlib.sha256((stage / p).read_bytes()).hexdigest() for p in paths}
original_src = build.src
with tempfile.TemporaryDirectory(dir=HERE) as scratch:
    def dst(path):
        out = Path(scratch) / path
        out.parent.mkdir(parents=True, exist_ok=True)
        return str(out)
    build.dst = dst
    build.src = lambda p: original_src(p) if Path(original_src(p)).exists() else dst('base/' + p)
    first = build.botanist()
    a = {p: hashlib.sha256(Path(dst(p)).read_bytes()).hexdigest() for p in paths}
    second_report = build.botanist()
    b = {p: hashlib.sha256(Path(dst(p)).read_bytes()).hexdigest() for p in paths}
    assert a == b == before
assert before == {p: hashlib.sha256((stage / p).read_bytes()).hexdigest() for p in paths}
result = dict(skill_source_with_own_archive_first=selected, two_isolated_botanist_builds_identical=True,
              matches_installed_stage=True, protected_stage_unchanged=True,
              note='main/publish not executed; full archive repeat-build evidence belongs to Claude')
(HERE / 'fixed-results.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
