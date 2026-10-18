from pathlib import Path
p=Path('outputs/Documentation-support/review-C44/check_f1_fix.py')
s=p.read_text()
s=s.replace("model.active.extend([None, Mission('A', 'delivery'), Mission('B')])", "model.active.extend([None, Mission('A', 'nonmission'), Mission('A', 'delivery'), Mission('B')])")
p.write_bytes(s.encode())
p=Path('work/c45-check.sh')
s=p.read_text().replace('set -eu\n','set -euo pipefail\n')
p.write_bytes(s.encode())
