
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
std::size_t flatten(Vector<WorldCoordinates>* path) {
 int* zone=nullptr;
		JSONSerializationType points = JSONSerializationType::array();
		const WorldCoordinates* previous = nullptr;

		for (int i = 0; i < path->size() && points.size() < 256; ++i) {
			const WorldCoordinates& point = path->get(i);
			CellObject* pointCell = point.getCell();

			if (pointCell == nullptr && previous != nullptr && previous->getCell() == nullptr) {
				float dx = point.getX() - previous->getX(), dy = point.getY() - previous->getY();
				int steps = (int) (Math::sqrt(dx * dx + dy * dy) / 8.f);

				for (int s = 1; s < steps; ++s) {
					float px = previous->getX() + dx * s / steps, py = previous->getY() + dy * s / steps;
					points.push_back({px, py, CollisionManager::getWorldFloorCollision(px, py, zone, false), 0});
				}
			}

			points.push_back({point.getX(), point.getY(), point.getZ(), pointCell != nullptr ? pointCell->getObjectID() : 0});
			previous = &point;
		}

 return points.size();
}
int main(){
 Vector<WorldCoordinates> straight{{0,0,0},{2048,0,0}};
 Vector<WorldCoordinates> corner{{0,0,0},{1600,0,0},{1600,1000,0}};
 std::cout << "{\"straight_2048m_points\":" << flatten(&straight)
           << ",\"corner_points\":" << flatten(&corner) << "}\n";
}
