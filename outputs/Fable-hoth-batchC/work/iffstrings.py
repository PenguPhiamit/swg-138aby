import re, sys
sys.path.insert(0, sys.argv[1])
from trn_iff import client_file
for path in sys.argv[2:]:
    seen = set(); chain = [path]
    while chain:
        p = chain.pop(0)
        if p in seen: break
        seen.add(p)
        data = client_file(p)
        if data is None:
            print(p, '-> not in client archives'); continue
        strings = sorted(set(m.group(0).decode('latin-1') for m in re.finditer(rb'[A-Za-z0-9_/\.]+\.(?:iff|sat|cdf|apt|msh|lmg|pob)', data)))
        print(p, len(data), 'bytes; strings:', strings)
        for s in strings:
            if s.startswith('object/') and s != p and s.endswith('.iff') and 'base' in s or s.startswith('object/mobile/base/'):
                chain.append(s)
