import sys, os
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-planet-test/tools')
sys.path.insert(0, 'C:/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-hoth-batchA/tools')
import hoth_survey as S
ev = S.evaluator()
h = (lambda x, y: ev.height(x, y)) if hasattr(ev, 'height') else ev
pts = {'Flurry centre': (-5100, 5100), 'MTG main door': (-5050, 5410), 'MTG hangar door': (-5300, 5690), 'MTG tower': (-5036, 5106),
       '300 m S of main': (-5050, 5110), '600 m S': (-5050, 4810), '1 km S': (-5050, 4410), '1 km E': (-4050, 5410), '1 km W': (-6050, 5410), '400 m N of hangar': (-5300, 6090)}
for k, (x, y) in pts.items():
    print('%-18s %6d %6d  h=%7.1f' % (k, x, y, h(x, y)))
print('profile south from the main door, 100 m steps:')
print(' '.join('%.0f' % h(-5050, 5410 - i * 100) for i in range(0, 16)))
print('profile west->east through 5300, 200 m steps from -7000:')
print(' '.join('%.0f' % h(-7000 + i * 200, 5300) for i in range(0, 20)))
