// Read-only replay of BotPop's meshPath (BotPopLaunchBrain.h at 69f5c879) on navmeshes carved from a copy of navareas.db.
// Usage: replay <positions.json> <meshdir> [nodes]
#include "DetourNavMesh.h"
#include "DetourNavMeshQuery.h"
#include "DetourCommon.h"
#include "DetourNode.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <string>
#include <vector>
#include <map>
#include <dirent.h>
#include <random>
#include <algorithm>

struct SetHeader { int magic, version, numTiles; dtNavMeshParams params; };
struct TileHeader { dtTileRef tileRef; int dataSize; };

struct Mesh {
	std::string name, planet;
	dtNavMesh* nav = nullptr;
	dtNavMeshQuery* q = nullptr;   // MESH_NODES
	dtNavMeshQuery* big = nullptr; // 65535 nodes
	float cx, cy, r;               // world centre and radius (from the build bounds: centre +- radius)
	std::map<dtPolyRef, int> comp;
	std::vector<int> compSize;
};

static dtQueryFilter filter;
static int NODES = 8192;
static std::mt19937 rng(17);
static float frand() { return std::uniform_real_distribution<float>(0, 1)(rng); }

static bool load(const std::string& path, Mesh& m) {
	FILE* f = fopen(path.c_str(), "rb");
	if (!f) return false;
	SetHeader h;
	if (fread(&h, sizeof h, 1, f) != 1) return false;
	m.nav = dtAllocNavMesh();
	if (dtStatusFailed(m.nav->init(&h.params))) return false;
	float minx = 1e9, maxx = -1e9, minz = 1e9, maxz = -1e9;
	for (int i = 0; i < h.numTiles; ++i) {
		TileHeader th;
		if (fread(&th, sizeof th, 1, f) != 1) break;
		unsigned char* d = (unsigned char*)dtAlloc(th.dataSize, DT_ALLOC_PERM);
		if (th.dataSize <= (int)sizeof(dtMeshHeader) || th.dataSize > (64 << 20)) { fclose(f); return false; }
		if (fread(d, th.dataSize, 1, f) != 1) break;
		const dtMeshHeader* mh = (const dtMeshHeader*)d;
		if (mh->magic != DT_NAVMESH_MAGIC || mh->version != DT_NAVMESH_VERSION) { fprintf(stderr, "bad tile in %s\n", path.c_str()); fclose(f); return false; }
		// every polygon's vertices within the tile's own vertex array
		int need = dtAlign4(sizeof(dtMeshHeader)) + dtAlign4(sizeof(float) * 3 * mh->vertCount) + dtAlign4(sizeof(dtPoly) * mh->polyCount);
		if (need > th.dataSize || mh->vertCount <= 0) { fprintf(stderr, "short tile in %s\n", path.c_str()); fclose(f); return false; }
		const dtPoly* polys = (const dtPoly*)(d + dtAlign4(sizeof(dtMeshHeader)) + dtAlign4(sizeof(float) * 3 * mh->vertCount));
		for (int j = 0; j < mh->polyCount; ++j)
			for (int v = 0; v < polys[j].vertCount; ++v)
				if (polys[j].verts[v] >= mh->vertCount) { fprintf(stderr, "bad poly in %s\n", path.c_str()); fclose(f); return false; }
		m.nav->addTile(d, th.dataSize, DT_TILE_FREE_DATA, th.tileRef, 0);
	}
	fclose(f);
	// The build bounds: orig is the box's min corner; tiles are tileWidth wide, so the box's far side is unknown to a
	// tile; the radius from the tile grid's used extent (within one tile).
	const dtNavMeshParams* p = m.nav->getParams();
	int maxtx = 0, maxty = 0;
	for (int i = 0; i < m.nav->getMaxTiles(); ++i) {
		const dtMeshTile* t = ((const dtNavMesh*)m.nav)->getTile(i);
		if (!t || !t->header) continue;
		maxtx = std::max(maxtx, t->header->x); maxty = std::max(maxty, t->header->y);
	}
	float wx = (maxtx + 1) * p->tileWidth, wz = (maxty + 1) * p->tileHeight;
	m.r = std::min(wx, wz) * 0.5f;
	m.cx = p->orig[0] + m.r;
	m.cy = -(p->orig[2] + m.r);
	m.q = dtAllocNavMeshQuery(); m.q->init(m.nav, NODES);
	m.big = dtAllocNavMeshQuery(); m.big->init(m.nav, 65535);
	return true;
}

static void components(Mesh& m) {
	const dtNavMesh* nav = m.nav;
	for (int i = 0; i < nav->getMaxTiles(); ++i) {
		const dtMeshTile* t = nav->getTile(i);
		if (!t || !t->header) continue;
		dtPolyRef base = nav->getPolyRefBase(t);
		for (int j = 0; j < t->header->polyCount; ++j) {
			const dtPoly* poly = &t->polys[j];
			if (poly->getType() != DT_POLYTYPE_GROUND || !(poly->flags & filter.getIncludeFlags())) continue;
			dtPolyRef start = base | (dtPolyRef)j;
			if (m.comp.count(start)) continue;
			int id = (int)m.compSize.size(), size = 0;
			std::vector<dtPolyRef> stack{start};
			m.comp[start] = id;
			while (!stack.empty()) {
				dtPolyRef ref = stack.back(); stack.pop_back(); ++size;
				const dtMeshTile* tt; const dtPoly* pp;
				nav->getTileAndPolyByRefUnsafe(ref, &tt, &pp);
				for (unsigned int k = pp->firstLink; k != DT_NULL_LINK; k = tt->links[k].next) {
					dtPolyRef nb = tt->links[k].ref;
					if (!nb || m.comp.count(nb)) continue;
					const dtMeshTile* nt; const dtPoly* np;
					nav->getTileAndPolyByRefUnsafe(nb, &nt, &np);
					if (!(np->flags & filter.getIncludeFlags())) continue;
					m.comp[nb] = id; stack.push_back(nb);
				}
			}
			m.compSize.push_back(size);
		}
	}
}

// floorNear's stand-in (no terrain offline): the lowest mesh surface under (x, y) within 1 m, else NaN.
static float ground(Mesh& m, float x, float y) {
	float c[3] = {x, 0, -y}, ext[3] = {1, 3000, 1};
	dtPolyRef refs[256]; int n = 0;
	m.q->queryPolygons(c, ext, &filter, refs, &n, 256);
	float best = NAN;
	for (int i = 0; i < n; ++i) {
		float h;
		if (dtStatusSucceed(m.q->getPolyHeight(refs[i], c, &h)) && (std::isnan(best) || h < best)) best = h;
	}
	return best;
}

static bool nearest(Mesh& m, float x, float y, float z, float reach, float rise, dtPolyRef& ref, float* pt) {
	float c[3] = {x, z, -y}, ext[3] = {reach, rise, reach};
	ref = 0;
	return dtStatusSucceed(m.q->findNearestPoly(c, ext, &filter, &ref, pt)) && ref;
}

struct Tally { long n = 0, ok = 0, nostart = 0, noend = 0, partial = 0, oon = 0, island = 0, islandSmall = 0, near2 = 0, near15 = 0, bigOk = 0, snapped = 0, hopStart = 0, hopEnd = 0; double hopLen = 0; double len = 0, lenPartial = 0; };
static std::map<std::string, Tally> tallies;

static int FIX = 0, PROBE = 512; static float HOP = 15;
static dtNavMeshQuery* probeQuery = nullptr;
// true and (ref, pos) moved when a 512-node search from ref toward other runs out of mesh, not nodes: ref is on a
// piece of fewer than 512 polygons that doesn't hold other. The new place: the nearest polygon within 15 m across and
// 4 m up or down that the probe never reached.
static bool cutOff(dtPolyRef ref, const float* pos, dtPolyRef other, const float* otherPos) {
	static dtPolyRef polys[8192]; int count = 0;
	dtStatus st = probeQuery->findPath(ref, other, pos, otherPos, &filter, polys, &count, 8192);
	return dtStatusSucceed(st) && (st & DT_PARTIAL_RESULT) && !(st & DT_OUT_OF_NODES);
}
static bool pocket(Mesh& m, dtPolyRef& ref, float* pos, dtPolyRef other, const float* otherPos) {
	static dtNavMesh* inited = nullptr;
	if (!probeQuery) probeQuery = dtAllocNavMeshQuery();
	if (inited != m.nav) { probeQuery->init(m.nav, PROBE); inited = m.nav; }
	if (!cutOff(ref, pos, other, otherPos)) return false;
	float ext[3] = {HOP, 4, HOP};
	dtPolyRef near[256]; int n = 0;
	probeQuery->queryPolygons(pos, ext, &filter, near, &n, 256);
	struct C { float d; dtPolyRef r; float p[3]; };
	std::vector<C> cs;
	dtNodePool* pool = probeQuery->getNodePool();
	for (int i = 0; i < n; ++i) {
		if (pool->findNode(near[i], 0)) continue; // on the piece itself
		C c; c.r = near[i];
		if (!dtStatusSucceed(probeQuery->closestPointOnPoly(near[i], pos, c.p, nullptr))) continue;
		c.d = dtVdistSqr(c.p, pos); cs.push_back(c);
	}
	std::sort(cs.begin(), cs.end(), [](const C& x, const C& y) { return x.d < y.d; });
	std::vector<dtPolyRef> tried; // polygons of pockets already probed
	int probes = 0;
	for (const C& c : cs) {
		if (std::find(tried.begin(), tried.end(), c.r) != tried.end()) continue;
		if (++probes > 4) break;
		if (!cutOff(c.r, c.p, other, otherPos)) { ref = c.r; dtVcopy(pos, c.p); return true; }
		for (int i = 0; i < pool->getNodeCount(); ++i) tried.push_back(pool->getNodeAtIdx(i + 1)->id);
	}
	return false;
}

// meshPath at 69f5c879, with the reasons a partial is partial
static void leg(Mesh& m, const char* kind, float ax, float ay, float bx, float by, float az0 = NAN, float bz0 = NAN) {
	Tally& t = tallies[kind]; Tally& all = tallies["ALL"];
	float az = std::isnan(az0) ? ground(m, ax, ay) : az0, bz = std::isnan(bz0) ? ground(m, bx, by) : bz0;
	if (std::isnan(az) || std::isnan(bz)) return; // not over the mesh: unknown height offline, skip
	++t.n; ++all.n;
	dtPolyRef s, e; float sp[3], ep[3];
	if (!nearest(m, ax, ay, az, 10, 2.5f, s, sp)) { ++t.nostart; ++all.nostart; return; }
	if (!nearest(m, bx, by, bz, 10, 2.5f, e, ep) && !nearest(m, bx, by, bz, 40, 4, e, ep)) { ++t.noend; ++all.noend; return; }
	float ex = ep[0] - bx, ey = -ep[2] - by;
	if (ex * ex + ey * ey > 2.25f) { ++t.snapped; ++all.snapped; }
	if (FIX) { // the patch: an end on a small cut-off piece moves to the nearest polygon off it within 15 m
		float before[3]; dtVcopy(before, sp);
		if (pocket(m, s, sp, e, ep)) { ++t.hopStart; ++all.hopStart; t.hopLen += dtVdist2D(before, sp); all.hopLen += dtVdist2D(before, sp); }
		dtVcopy(before, ep);
		if (pocket(m, e, ep, s, sp)) { ++t.hopEnd; ++all.hopEnd; }
	}
	static dtPolyRef polys[2048]; int count = 0;
	dtStatus st = m.q->findPath(s, e, sp, ep, &filter, polys, &count, 2048);
	float L = std::sqrt((bx - ax) * (bx - ax) + (by - ay) * (by - ay));
	t.len += L; all.len += L;
	if (!dtStatusSucceed(st) || !count) return;
	bool partial = (st & DT_PARTIAL_RESULT) || polys[count - 1] != e;
	if (!partial) { ++t.ok; ++all.ok; return; }
	++t.partial; ++all.partial; t.lenPartial += L; all.lenPartial += L;
	if (st & DT_OUT_OF_NODES) { ++t.oon; ++all.oon; }
	bool other = m.comp.count(s) && m.comp.count(e) && m.comp[s] != m.comp[e];
	if (other) { ++t.island; ++all.island; if (m.compSize[m.comp[e]] < m.compSize[m.comp[s]]) { ++t.islandSmall; ++all.islandSmall; } }
	float end[3];
	m.q->closestPointOnPoly(polys[count - 1], ep, end, nullptr);
	float dx = end[0] - bx, dy = -end[2] - by, d = std::sqrt(dx * dx + dy * dy);
	if (d <= 2.5f) { ++t.near2; ++all.near2; }
	if (d <= 15.f) { ++t.near15; ++all.near15; }
	int c2 = 0;
	static dtPolyRef p2[8192];
	dtStatus st2 = m.big->findPath(s, e, sp, ep, &filter, p2, &c2, 8192);
	if (dtStatusSucceed(st2) && c2 && !(st2 & DT_PARTIAL_RESULT) && p2[c2 - 1] == e) { ++t.bigOk; ++all.bigOk; }
}

// planRoute's edge(): the last point of inside->outside still in the circle, 2 m back
static void edge(Mesh& m, float ix, float iy, float ox, float oy, float& x, float& y) {
	float lo = 0, hi = 1, dx = ox - ix, dy = oy - iy;
	for (int i = 0; i < 12; ++i) {
		float mid = (lo + hi) * 0.5f, px = ix + dx * mid - m.cx, py = iy + dy * mid - m.cy;
		if (px * px + py * py < m.r * m.r) lo = mid; else hi = mid;
	}
	float len = std::sqrt(dx * dx + dy * dy), tt = len > 0.01f ? std::max(0.f, lo - 2.f / len) : 0.f;
	x = ix + dx * tt; y = iy + dy * tt;
}

int main(int argc, char** argv) {
	if (argc > 3) NODES = atoi(argv[3]);
	filter.setIncludeFlags(0xffff ^ (0x10 | 0x02));
	filter.setExcludeFlags(0);
	std::vector<Mesh> meshes;
	DIR* d = opendir(argv[2]);
	while (dirent* e = readdir(d)) {
		std::string n = e->d_name;
		if (n.find(".mset") == std::string::npos || n.find("_city_") == std::string::npos) continue;
		Mesh m; m.name = n.substr(0, n.find(".")); m.planet = m.name.substr(0, m.name.find("_"));
		if (load(std::string(argv[2]) + "/" + n, m)) meshes.push_back(m);
	}
	closedir(d);
	// positions: [[id,"planet",x,y,s],...]
	FILE* f = fopen(argv[1], "rb"); std::string js; char buf[65536]; size_t k;
	while ((k = fread(buf, 1, sizeof buf, f)) > 0) js.append(buf, k);
	fclose(f);
	struct Bot { std::string planet; float x, y, z = NAN; };
	std::vector<Bot> bots;
	for (size_t p = js.find("[", js.find("bots")) + 1; (p = js.find("[", p)) != std::string::npos; ++p) {
		char planet[64]; unsigned long long id; int x, y, s;
		if (sscanf(js.c_str() + p, "[%llu,\"%63[^\"]\",%d,%d,%d]", &id, planet, &x, &y, &s) == 5) bots.push_back({planet, (float)x, (float)y});
	}
	if (std::string(argv[1]).find(".txt") != std::string::npos) { // snap rows: planet x y z
		bots.clear();
		FILE* bf = fopen(argv[1], "r"); char pl[64]; float x, y, z;
		while (fscanf(bf, "%63s %f %f %f", pl, &x, &y, &z) == 4) bots.push_back({pl, x, y, z});
		fclose(bf);
	}
	if (getenv("FIX")) FIX = 1;
	if (getenv("PROBE")) PROBE = atoi(getenv("PROBE"));
	if (getenv("HOP")) HOP = atof(getenv("HOP"));
	printf("nodes %d, %zu city meshes, %zu bots\n", NODES, meshes.size(), bots.size());
	for (auto& m : meshes) {
		std::vector<Bot*> here;
		for (auto& b : bots) {
			bool same = m.planet == b.planet || (m.planet == "hutta" && b.planet == "nal_hutta");
			if (!same) continue;
			float dx = b.x - m.cx, dy = b.y - m.cy;
			if (dx * dx + dy * dy < m.r * m.r) here.push_back(&b);
		}
		if (here.empty()) continue;
		float lx = m.cx, ly = m.cy; // BotPopLaunch.h's centre for this town, when there is one
		if (FILE* cf = fopen("cities.txt", "r")) { char nm[64]; float x, y; float bd = 1e9;
			while (fscanf(cf, "%63s %f %f", nm, &x, &y) == 3) if (m.planet == nm && std::hypot(x - m.cx, y - m.cy) < std::min(bd, m.r)) { bd = std::hypot(x - m.cx, y - m.cy); lx = x; ly = y; }
			fclose(cf); }
		components(m);
		int biggest = 0; for (int s : m.compSize) biggest = std::max(biggest, s);
		long before = tallies["ALL"].partial, nBefore = tallies["ALL"].n;
		int mainId = (int)(std::max_element(m.compSize.begin(), m.compSize.end()) - m.compSize.begin());
		int offMain = 0, printed = 0, offMesh = 0, smallPiece = 0;
		auto where = [&](float x, float y, int& size) {
			float z = ground(m, x, y); dtPolyRef r; float p[3]; size = 0;
			if (std::isnan(z) || !nearest(m, x, y, z, 10, 2.5f, r, p) || !m.comp.count(r)) return -1;
			size = m.compSize[m.comp[r]];
			return m.comp[r];
		};
		for (Bot* b : here) {
			int size, id = where(b->x, b->y, size);
			if (!std::isnan(b->z)) { dtPolyRef r; float p[3]; id = -1; size = 0;
				if (nearest(m, b->x, b->y, b->z, 10, 2.5f, r, p) && m.comp.count(r)) { id = m.comp[r]; size = m.compSize[id]; } else ++offMesh; }
			if (id >= 0 && id != mainId && size < 512) ++smallPiece;
			if (id >= 0 && id != mainId) {
				++offMain;
				if (printed++ < 3 && getenv("SAMPLES")) {
					float c[3] = {b->x, 0, -b->y}, ext[3] = {1, 3000, 1}; dtPolyRef refs[64]; int n = 0;
					m.q->queryPolygons(c, ext, &filter, refs, &n, 64);
					printf("   bot at %.0f %.0f on piece of %d polys; surfaces here:", b->x, b->y, size);
					for (int i = 0; i < n; ++i) { float h; if (dtStatusSucceed(m.q->getPolyHeight(refs[i], c, &h))) printf(" %.1f(%d)", h, m.comp.count(refs[i]) ? m.compSize[m.comp[refs[i]]] : -1); }
					printf("\n");
				}
			}
		}
		if (getenv("DIAG")) { // the nearest main-piece polygons around each town's launch centre, by height
			float c[3] = {lx, 0, -ly}, ext[3] = {60, 3000, 60}; static dtPolyRef refs[4096]; int n = 0;
			m.q->queryPolygons(c, ext, &filter, refs, &n, 4096);
			float gz = ground(m, lx, ly), best = 1e9, bz = 0;
			for (int i = 0; i < n; ++i) {
				if (!m.comp.count(refs[i]) || m.comp[refs[i]] != mainId) continue;
				float p[3], q[3] = {lx, std::isnan(gz) ? 0 : gz, -ly};
				m.q->closestPointOnPoly(refs[i], q, p, nullptr);
				float d = std::hypot(p[0] - lx, -p[2] - ly);
				if (d < best) { best = d; bz = p[1]; }
			}
			printf("   DIAG centre %.0f %.0f ground %.1f: nearest main piece %.1f m across at height %.1f\n", lx, ly, gz, best, bz);
		}
		if (getenv("PIECES")) for (Bot* b : here) {
			dtPolyRef r; float p[3]; int size = -1, main = 0;
			if (nearest(m, b->x, b->y, b->z, 10, 2.5f, r, p) && m.comp.count(r)) { size = m.compSize[m.comp[r]]; main = m.comp[r] == mainId; }
			printf("PIECE %s %.0f %.0f %.0f %d %d\n", m.name.c_str(), b->x, b->y, b->z, size, main);
		}
		if (getenv("LANDINGS")) { // each bot's piece and the nearest main-piece point within 200 m, 4 m up or down
			std::map<std::pair<int, int>, int> seen;
			for (Bot* b : here) {
				if (seen[{(int)b->x / 10, (int)b->y / 10}]++) continue;
				dtPolyRef r; float p[3];
				if (!nearest(m, b->x, b->y, b->z, 10, 2.5f, r, p) || !m.comp.count(r)) { printf("   LANDING %.0f %.0f %.0f: no polygon\n", b->x, b->y, b->z); continue; }
				int id = m.comp[r];
				float c[3] = {b->x, b->z, -b->y}, ext[3] = {200, 4, 200}; static dtPolyRef refs[16384]; int n = 0;
				m.q->queryPolygons(c, ext, &filter, refs, &n, 16384);
				float best = 1e9;
				for (int i = 0; i < n; ++i) {
					if (!m.comp.count(refs[i]) || m.comp[refs[i]] != mainId) continue;
					float q[3]; m.q->closestPointOnPoly(refs[i], c, q, nullptr);
					best = std::min(best, std::hypot(q[0] - b->x, -q[2] - b->y));
				}
				printf("   LANDING %.0f %.0f %.0f: piece %d polys (%s), main piece %.1f m away\n", b->x, b->y, b->z, m.compSize[id], id == mainId ? "main" : "cut off", best);
			}
		}
		int csize, cid = where(lx, ly, csize);
		printf("   bots with no polygon within 10 m / 2.5 m: %d; on a piece under 512 polygons: %d\n", offMesh, smallPiece);
		printf("   bots off the main piece %d of %zu; centre on %s (%d polys)\n", offMain, here.size(), cid == mainId ? "main" : cid < 0 ? "nothing" : "an island", csize);
		for (Bot* b : here) {
			for (int rep = 0; rep < 4; ++rep) {
				// out: a hunter's goal, city radius + 40 + up to 500 m from the centre (launchHunt); the leg to the edge
				float a = frand() * 6.2832f, reach = m.r + 40 + frand() * 500;
				float gx = m.cx + std::cos(a) * reach, gy = m.cy + std::sin(a) * reach, ex, ey;
				edge(m, b->x, b->y, gx, gy, ex, ey);
				leg(m, "out (bot -> edge)", b->x, b->y, ex, ey, b->z);
				// in: from the edge toward the bot's spot (a hunter coming back to its city)
				leg(m, "in (edge -> bot spot)", ex, ey, b->x, b->y, NAN, b->z);
				// centre: medics, entertainers, resting hunters (chaseToward L->center): the launch table's centre
				leg(m, "centre", b->x, b->y, lx, ly, b->z);
				// a random walkable point (terminals, trainers, shuttles)
				dtPolyRef rr; float rp[3];
				if (dtStatusSucceed(m.q->findRandomPoint(&filter, frand, &rr, rp))) leg(m, "random point", b->x, b->y, rp[0], -rp[2], b->z);
			}
		}
		printf("%-40s r %4.0f bots %3d components %5zu (largest %6d polys) legs %5ld partial %5ld\n", m.name.c_str(), m.r, (int)here.size(), m.compSize.size(), biggest,
			tallies["ALL"].n - nBefore, tallies["ALL"].partial - before);
	}
	printf("\n%-24s %6s %6s %5s %5s %7s %6s %6s %7s %7s %6s %8s %7s %9s\n", "leg", "n", "ok", "nost", "noend", "partial", "OOnod", "island", "isl<st", "end<2.5", "end<15", "full@64k", "snapped", "len all/p");
	for (auto& kv : tallies) {
		Tally& t = kv.second;
		printf("%-24s %6ld %6ld %5ld %5ld %7ld %6ld %6ld %7ld %7ld %6ld %8ld %7ld %5.0f/%3.0f\n", kv.first.c_str(), t.n, t.ok, t.nostart, t.noend, t.partial, t.oon, t.island, t.islandSmall, t.near2, t.near15, t.bigOk, t.snapped,
			t.n ? t.len / t.n : 0, t.partial ? t.lenPartial / t.partial : 0);
	}
}
