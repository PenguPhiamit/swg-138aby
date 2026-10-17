"""ASCII map of Bilbousa's free ground (diagnostic): '#' occupied, '.' free; 6 m cells; x -1080..-420, y 1230..1950."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from life_common import occupied, blocked  # noqa: E402
polys = occupied(pad=1.0)
C = 6
print('      ' + ''.join(str(abs(x) // 100 % 10) if x % 60 == 0 else ' ' for x in range(-1080, -420, C)))
for y in range(1950, 1230, -C):
    row = ''.join('#' if blocked(polys, x + C / 2, y - C / 2, r=C / 2 - 0.5) else '.' for x in range(-1080, -420, C))
    print('%5d ' % y + row)
