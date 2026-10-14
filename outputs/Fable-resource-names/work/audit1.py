import sys, os, struct
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-ossus/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/hoth')
import swg_tables as T, trn_iff as I
import client_load_order as clo
trees, a, b = clo.load_order()
print('load order entries', len(trees), 'extra', type(a), type(b))
N = 'string/en/resource/resource_names.stf'
for pri, name in sorted(trees, key=lambda t: -t[0])[:60]:
    p = os.path.join(I.CLIENT, os.path.basename(name))
    if not os.path.exists(p): print('%3d %-28s MISSING on disk' % (pri, os.path.basename(name))); continue
    with open(p, 'rb') as f: hdr = f.read(12)
    try:
        ents = I.list_tre(p); has = N in ents
    except Exception as e:
        ents = None; has = 'ERR ' + str(e)[:40]
    print('%3d %-28s %s %s %s' % (pri, os.path.basename(name), hdr[:8], len(ents) if ents is not None else '-', 'HAS resource_names' if has is True else ('' if has is False else has)))
