"""Read-only inventory of active-client saber appearance dependencies; no extraction."""
import json
import re
import swg_client_data as data

data._build_index()
names = sorted(data._index)
matches = [n for n in names if any(x in n for x in ('darksaber', 'ghostfire', 'lightsaberblade', 'wp_lightsaber')) or n.endswith('.lsb')]
print(json.dumps({'matching_count': len(matches), 'paths': matches}, indent=2))
for name in [n for n in matches if n.endswith('.lsb')][:2] + [n for n in matches if n.endswith('.sht')][:3]:
    blob = data.client_file(name)
    strings = [s.decode('ascii') for s in re.findall(rb'[ -~]{5,}', blob)]
    print(json.dumps({'path': name, 'size': len(blob), 'ascii': strings}, indent=2))
