import sys, os
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-batchA/tools')
import hoth_survey as S, trn_iff as I
ev = S.evaluator()
print('height grid 250 m over the echo_base rectangle (x -7000..-3200 across, y 7000 down to 3200):')
xs = list(range(-6875, -3200, 250)); print('       ' + ''.join('%6d' % x for x in xs))
for y in range(6875, 3200, -250):
    print('%6d ' % y + ''.join('%6.0f' % ev.height(x, y) for x in xs))
idx = I.client_index()
print('\n== Echo Base / Hoth heroic client files (non-collision)')
for n in sorted(idx):
    if '/collision/' in n: continue
    if any(k in n for k in ('echo_base', 'hoth_generator', 'hoth_ion', 'hoth_rebel_transport', 'hoth_at_st', 'echo_base_door')):
        print('  ', n, '<-', idx[n])
