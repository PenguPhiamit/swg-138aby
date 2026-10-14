
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
	void unstick(CreatureObject* follower, CreatureObject* leader) {
		Zone* zone = follower->getZone();

		if (zone == nullptr || leader->getZone() != zone)
			return;

		WorldCoordinates start(follower);
		WorldCoordinates goal(leader);
		Vector3 leaderPosition = leader->getWorldPosition();
		Vector3 followerPosition = follower->getWorldPosition();
		std::unique_ptr<Vector<WorldCoordinates>> path(PathFinderManager::instance()->findPath(start, goal, zone));

		if (path == nullptr || path->size() < 2) {
			warn(follower, "Leash: there's no walkable way to " + leader->getFirstName() + " from here.");
			return;
		}

		WorldCoordinates target = path->get(path->size() - 1); // the route's end: the closest reachable point

		if (target.getWorldPosition().distanceTo(leaderPosition) <= BEHIND) {
			// The route reaches the leader. Path points can be far apart, so walk back from the leader to the
			// first point at least BEHIND metres away and stop BEHIND metres short of the leader on that segment.
			for (int i = path->size() - 2; i >= 0; --i) {
				const WorldCoordinates& far = path->get(i);
				const WorldCoordinates& near = path->get(i + 1);

				if (far.getWorldPosition().distanceTo(leaderPosition) < BEHIND)
					continue;

				if (far.getCell() != near.getCell()) {
					target = near; // segment crosses a doorway: don't blend coordinates of two cells
					break;
				}

				Vector3 from = near.getPoint(), to = far.getPoint();
				float length = from.distanceTo(to);
				Vector3 point = length > BEHIND ? from + (to - from) * (BEHIND / length) : to;

				if (far.getCell() == nullptr)
					point.setZ(CollisionManager::getWorldFloorCollision(point.getX(), point.getY(), zone, false));

				target = WorldCoordinates(point, far.getCell());
				break;
			}
		}

		Vector3 targetPosition = target.getWorldPosition();

		// A route that stops short (raised ground, a spot off the mesh) can end where the follower already is:
		// moving them there again would only rubber-band.
		if (targetPosition.distanceTo(followerPosition) < 2.f ||
			targetPosition.distanceTo(leaderPosition) > followerPosition.distanceTo(leaderPosition) - 1.f) {
			warn(follower, "Leash: you're already as close to " + leader->getFirstName() + " as the ground allows; keep following.");
			return;
		}

		ManagedReference<CellObject*> cell = target.getCell(); // held until the move is done

		if (cell != nullptr) {
			ManagedReference<SceneObject*> parent = cell->getParent().get();
			BuildingObject* building = parent != nullptr && parent->isBuildingObject() ? cast<BuildingObject*>(parent.get()) : nullptr;

			if (building != nullptr && !building->isAllowedEntry(follower)) {
				warn(follower, "Leash: " + leader->getFirstName() + " is inside a building you can't enter.");
				return;
			}
		}

		follower->teleport(target.getX(), target.getZ(), target.getY(), cell != nullptr ? cell->getObjectID() : 0);
		follower->sendSystemMessage("Leash: you were stuck, so you've been moved closer to " + leader->getFirstName() + ".");
	}

	void warn(CreatureObject* follower, const String& text) {
		if (!warned)
			follower->sendSystemMessage(text);

		warned = true;
	}

};
int main(){
 Zone zone; CreatureObject follower{&zone,{0,0,0}},leader{&zone,{100,0,0}};
 // Exact current PathFinderManager failure fallback, starting from an empty route.
 WorldCoordinates pointA(&follower); Vector<WorldCoordinates> endPoints;endPoints.add(WorldCoordinates(&leader));
 auto finalpath=new Vector<WorldCoordinates>();
 	if (finalpath && finalpath->size() < 2) { // path could not be evaluated, just return the start/end position
		finalpath->removeAll();
		finalpath->add(pointA);
		finalpath->add(endPoints.get(0));
	}

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
