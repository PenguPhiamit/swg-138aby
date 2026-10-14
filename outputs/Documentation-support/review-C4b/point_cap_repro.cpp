
#include <array>
#include <cmath>
#include <iostream>
#include <vector>
namespace Math { float sqrt(float x) { return std::sqrt(x); } }
struct CellObject { unsigned long getObjectID() const { return 1; } };
struct WorldCoordinates {
 float x,y,z; CellObject* cell=nullptr;
 float getX() const{return x;} float getY() const{return y;} float getZ() const{return z;}
 CellObject* getCell() const{return cell;}
};
template<class T> struct Vector : std::vector<T> {
 using std::vector<T>::vector;
 const T& get(int i) const{return (*this)[i];}
};
struct Number { double v; template<class T> Number(T x):v(static_cast<double>(x)){} };
struct JSONSerializationType {
 std::vector<std::array<double,4>> values;
 static JSONSerializationType array(){return {};}
 std::size_t size() const{return values.size();}
 void push_back(std::initializer_list<Number> row){
  std::array<double,4> a{}; int i=0; for(auto n:row) a[i++]=n.v; values.push_back(a);
 }
};
struct CollisionManager {static float getWorldFloorCollision(float,float,int*,bool){return 0;}};

using uint64=unsigned long long;

struct Result { std::size_t count; bool partial; double x, y; };
Result flatten(Vector<WorldCoordinates>* path) {
 int* zone=nullptr;
 bool partial=false;
 static const int MAX_POINTS=256;
		JSONSerializationType points = JSONSerializationType::array();
		auto add = [&points](float px, float py, float pz, uint64 cellID) {
			if ((int) points.size() >= MAX_POINTS)
				return false;
			points.push_back({px, py, pz, cellID});
			return true;
		};
		const WorldCoordinates* previous = nullptr;

		for (int i = 0; i < path->size(); ++i) {
			const WorldCoordinates& point = path->get(i);
			CellObject* pointCell = point.getCell();
			bool full = false;

			if (pointCell == nullptr && previous != nullptr && previous->getCell() == nullptr) {
				float dx = point.getX() - previous->getX(), dy = point.getY() - previous->getY();
				int steps = (int) (Math::sqrt(dx * dx + dy * dy) / 8.f);

				for (int s = 1; s < steps && !full; ++s) {
					float px = previous->getX() + dx * s / steps, py = previous->getY() + dy * s / steps;
					full = !add(px, py, CollisionManager::getWorldFloorCollision(px, py, zone, false), 0);
				}
			}

			if (full || !add(point.getX(), point.getY(), point.getZ(), pointCell != nullptr ? pointCell->getObjectID() : 0)) {
				partial = true;
				break;
			}

			previous = &point;
		}

 auto last = points.values.back();
 return {points.size(), partial, last[0], last[1]};
}
int main() {
 Vector<WorldCoordinates> routes[] = {
   {{0,0,0},{2048,0,0}},
   {{0,0,0},{1600,0,0},{1600,1000,0}},
   {{0,0,0},{2032,0,0}},
   {{0,0,0},{2040,0,0}}
 };
 const char* names[] = {"straight_2048m", "corner", "below_cap", "exact_cap"};
 for (int i=0; i<4; ++i) {
   auto r=flatten(&routes[i]);
   std::cout << names[i] << " points=" << r.count << " partial=" << std::boolalpha << r.partial
             << " last=" << r.x << "," << r.y << "\n";
   if (r.count > 256 || r.partial != (i<2) || r.count != (i==2 ? 255 : 256)) return 1;
 }
}
