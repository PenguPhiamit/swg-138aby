# PIECE rows (replay) -> bots by where they stand: main mesh, a starport landing piece, a launch centre pocket, other
import sys, math, collections
land = [(l.split()[0],) + tuple(map(float, l.split()[1:3])) for l in open('/root/pr/arrivals.txt')]
cent = [(l.split()[0],) + tuple(map(float, l.split()[1:3])) for l in open('/root/pr/cities.txt') if len(l.split()) == 3]
near = lambda p, pts, d: any(q[0] == p[0] and math.hypot(p[1] - q[1], p[2] - q[2]) < d for q in pts)
c = collections.Counter(); town = collections.Counter()
for l in open(sys.argv[1]):
    if not l.startswith('PIECE'): continue
    _, mesh, x, y, z, size, main = l.split()
    p = (mesh.split('_')[0], float(x), float(y)); size = int(size); main = int(main)
    if main: k = 'main mesh'
    elif size < 0: k = 'no polygon within 10 m / 2.5 m'
    elif near(p, land, 45): k = 'starport landing piece'
    elif near(p, cent, 45): k = 'launch centre pocket'
    elif size < 512: k = 'other small piece'
    else: k = 'other large piece'
    c[k] += 1
    if k != 'main mesh': town[(mesh, k)] += 1
tot = sum(c.values())
print('bots in a town mesh:', tot)
for k, v in c.most_common(): print('  %-34s %4d (%d%%)' % (k, v, round(100 * v / tot)))
print('by town (not on the main mesh):')
for (mesh, k), v in sorted(town.items(), key=lambda kv: -kv[1])[:20]: print('  %4d %-36s %s' % (v, mesh, k))
