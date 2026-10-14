/*
 * AgentControl.h
 *
 * "Remote control" mode for core3client (enabled with --agent-control).
 * After zoning in, reads one JSON command per line on stdin and answers with one
 * line per reply on stdout, prefixed "@@AGENT ". Game events (chat, system
 * messages, conversations) are pushed on the same channel as they arrive.
 * Used by the local agent daemon in /opt/swg/agent.
 */

#ifndef AGENTCONTROL_H_
#define AGENTCONTROL_H_

#include "engine/engine.h"
#include "engine/util/JSONSerializationType.h"

#include <map>
#include <mutex>
#include <string>
#include <vector>

class Zone;

class AgentControl {
public:
	struct WorldObject {
		uint64 oid = 0;
		uint32 crc = 0;
		std::string type;
		std::string name;
		float x = 0, z = 0, y = 0;
		uint64 parent = 0;
		// Creatures only (CREO baselines 3/6 and their deltas)
		int posture = -1;
		uint64 states = 0;
		uint16 level = 0;
		uint64 group = 0, target = 0, weapon = 0;
		std::vector<int> ham, maxHam;
	};

	static void enable();
	static AgentControl* get(); // nullptr unless --agent-control was given

	void emit(const JSONSerializationType& message);

	// Hooks called from ZonePacketHandler
	void onStartScene(uint64 self, const String& terrain, float x, float z, float y);
	void onCreate(uint64 oid, uint32 crc, float x, float z, float y);
	void onTransform(uint64 oid, uint64 parent, float x, float z, float y);
	void onDestroy(uint64 oid);
	void onContainment(uint64 oid, uint64 parent);
	void onBaseline3(uint64 oid, uint32 typeCode, Message* pack);
	void onBaseline6(uint64 oid, uint32 typeCode, Message* pack);
	void onDelta(uint64 oid, uint32 typeCode, uint8 type, Message* pack);
	void onSystemMessage(const String& text);
	void onStringIdSystemMessage(Message* pack);
	void onInstantMessage(const String& from, const String& text);
	void onObjController(uint32 type, uint64 oid, Message* pack);
	bool onStandalonePacket(uint32 opcode, Message* pack);

	// Blocking command loop; returns when stdin closes or "quit" is received.
	void run(Zone* zone);

private:
	AgentControl() = default;

	JSONSerializationType handle(const JSONSerializationType& request);
	JSONSerializationType status();
	JSONSerializationType look(float radius, const std::string& typeFilter, int limit);
	JSONSerializationType moveTo(float x, float y, float speed, float timeoutSeconds, float z);
	bool groundNear(float x, float y, float& z);
	void sendTransform(float headingRadians, float speed);
	void sendCommand(const String& name, uint64 target, const UnicodeString& args);
	void sendTeleportAck(uint32 counter);
	std::string nameOf(uint64 oid);
	JSONSerializationType creatureState(const WorldObject& object);
	void setPosture(uint64 oid, int posture);
	void setStates(uint64 oid, uint64 states);

	std::recursive_mutex worldMutex;
	std::mutex outMutex;
	std::map<uint64, WorldObject> world;

	Zone* zone = nullptr;
	uint64 self = 0;
	std::string planet;
	float selfX = 0, selfZ = 0, selfY = 0;
	uint64 selfParent = 0;
	uint32 moveCount = 0;
	uint32 actionCount = 0;
	uint32 clientTime = 0;
	uint32 serverCorrections = 0; // position_set_by_server count, to notice blocked movement
	JSONSerializationType fight(uint64 target, float timeoutSeconds);

	// Server helper /agentpath (sandbox, bot accounts only): navmesh paths and ground height.
	std::string helperReply;
	uint32 helperReplies = 0;
	bool helperMissing = false;
	JSONSerializationType askHelper(const std::string& args);
	JSONSerializationType walkPath(const JSONSerializationType& points, float speed, float timeoutSeconds);
	void sendTransformWithParent(uint64 cell, float heading, float speed);
	bool conversationActive = false;
	uint64 conversationNpc = 0;
	uint8 radialCounter = 0;
	std::map<uint64, JSONSerializationType> radialMenus;
	std::map<uint32, JSONSerializationType> suiPages;
	JSONSerializationType inventorySnapshot();
	std::vector<std::string> conversationOptions;
	std::map<uint32, std::string> commandNames;
};

#endif /* AGENTCONTROL_H_ */
