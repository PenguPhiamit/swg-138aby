"""Compile the exported unstick method verbatim against minimal engine stubs.

Algorithm reproduction only: not a Core3 build, navmesh test, or game action.
Run with Python and g++ on WSL; writes artifacts beside this file.
"""
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parent
leash = (root / "files/LeashCommand.h").read_text()
method = leash[leash.index("\tvoid unstick("):leash.index("\n\tvoid stop(")]
finder = (root / "context/PathFinderManager.cpp").read_text()
fallback = finder[finder.index("\tif (finalpath && finalpath->size() < 2)"):finder.index("\n#ifdef PROFILE_PATHING", finder.index("\tif (finalpath && finalpath->size() < 2)"))]
prefix = r'''
#include <vector>
#include <string>
#include <memory>
#include <cmath>
#include <iostream>
#include <cassert>
using String = std::string;
template<class T> struct ManagedReference {
 T value{}; ManagedReference(T v=nullptr):value(v){} operator T() const{return value;}
 T get()const{return value;} T operator->()const{return value;}
 bool operator!=(std::nullptr_t)const{return value!=nullptr;}
};
struct Vector3 {
 float x{},y{},z{}; Vector3(float a=0,float b=0,float c=0):x(a),y(b),z(c){}
 float getX()const{return x;} float getY()const{return y;} float getZ()const{return z;}
 void setZ(float a){z=a;}
 float distanceTo(const Vector3& b)const{return std::sqrt((x-b.x)*(x-b.x)+(y-b.y)*(y-b.y)+(z-b.z)*(z-b.z));}
 Vector3 operator+(const Vector3& b)const{return {x+b.x,y+b.y,z+b.z};}
 Vector3 operator-(const Vector3& b)const{return {x-b.x,y-b.y,z-b.z};}
 Vector3 operator*(float a)const{return {x*a,y*a,z*a};}
};
struct Zone {};
struct SceneObject {bool isBuildingObject()const{return false;}};
struct CreatureObject;
struct BuildingObject:SceneObject {bool isAllowedEntry(CreatureObject*)const{return true;}};
struct CellObject {ManagedReference<SceneObject*> getParent(){return {};}
 unsigned long long getObjectID()const{return 1;}};
template<class T> T cast(SceneObject* p){return static_cast<T>(p);}
struct CreatureObject {
 Zone* zone; Vector3 position; int moves=0; std::vector<String> messages;
 Zone* getZone(){return zone;} Vector3 getWorldPosition(){return position;}
 String getFirstName(){return "leader";}
 void teleport(float x,float z,float y,unsigned long long){position={x,y,z};++moves;}
 void sendSystemMessage(String s){messages.push_back(s);}
};
struct WorldCoordinates {
 Vector3 p; CellObject* c=nullptr;
 WorldCoordinates(CreatureObject* a):p(a->position){}
 WorldCoordinates(Vector3 a,CellObject* b=nullptr):p(a),c(b){}
 Vector3 getWorldPosition()const{return p;} Vector3 getPoint()const{return p;}
 CellObject* getCell()const{return c;}
 float getX()const{return p.x;}float getY()const{return p.y;}float getZ()const{return p.z;}
};
template<class T>struct Vector:std::vector<T> {
 T& get(int i){return this->at(i);} const T& get(int i)const{return this->at(i);}
 void add(T a){this->push_back(a);}void removeAll(){this->clear();}
};
struct CollisionManager {static float getWorldFloorCollision(float,float,Zone*,bool){return 0;}};
struct PathFinderManager {
 Vector<WorldCoordinates>* route=nullptr;
 static PathFinderManager* instance(){static PathFinderManager a;return &a;}
 Vector<WorldCoordinates>* findPath(WorldCoordinates,WorldCoordinates,Zone*){auto p=route;route=nullptr;return p;}
};
struct Probe {
 static constexpr float BEHIND=3;
 bool warned=false;
'''
suffix = r'''
};
int main(){
 Zone zone; CreatureObject follower{&zone,{0,0,0}},leader{&zone,{100,0,0}};
 // Exact current PathFinderManager failure fallback, starting from an empty route.
 WorldCoordinates pointA(&follower); Vector<WorldCoordinates> endPoints;endPoints.add(WorldCoordinates(&leader));
 auto finalpath=new Vector<WorldCoordinates>();
 FALLBACK
 PathFinderManager::instance()->route=finalpath;
 Probe probe;probe.unstick(&follower,&leader);
 std::cout<<"failed-route fallback: moves="<<follower.moves<<" destination="<<follower.position.x<<","<<follower.position.y<<"\n";
 assert(follower.moves==1 && std::fabs(follower.position.x-97)<0.01);
 follower.position={0,0,0};follower.moves=0;
 PathFinderManager::instance()->route=nullptr;probe.unstick(&follower,&leader);
 std::cout<<"null route: moves="<<follower.moves<<"\n";assert(follower.moves==0);
 auto partial=new Vector<WorldCoordinates>();partial->add(WorldCoordinates(&follower));partial->add(WorldCoordinates(Vector3(20,0,0)));
 PathFinderManager::instance()->route=partial;probe.unstick(&follower,&leader);
 std::cout<<"reachable prefix: moves="<<follower.moves<<" destination="<<follower.position.x<<"\n";
 assert(follower.moves==1 && follower.position.x==20);
 follower.moves=0;auto same=new Vector<WorldCoordinates>();same->add(WorldCoordinates(&follower));same->add(WorldCoordinates(&follower));
 PathFinderManager::instance()->route=same;probe.unstick(&follower,&leader);
 std::cout<<"no progress: moves="<<follower.moves<<"\n";assert(follower.moves==0);
}
'''.replace("FALLBACK", fallback)
source = root / "route_fallback_repro.cpp"
source.write_text(prefix + method + suffix)
binary = root / "route_fallback_repro"
subprocess.run(["g++", "-std=c++17", "-O0", str(source), "-o", str(binary)], check=True)
result = subprocess.run([str(binary)], capture_output=True, text=True, check=True)
(root / "route_fallback_results.txt").write_text(result.stdout)
print(result.stdout, end="")
