#include "Zone.h"
#include "ZonePacketHandler.h"
#include "ClientCore.h"
#include "client/zone/objects/scene/SceneObject.h"
#include "server/zone/packets/zone/SelectCharacter.h"
#include "server/zone/packets/zone/CmdSceneReady.h"
#include "client/zone/managers/object/ObjectManager.h"
#include "client/zone/managers/objectcontroller/ObjectController.h"
#include "server/zone/packets/charcreation/ClientCreateCharacter.h"
#include "client/agent/AgentControl.h"

ZonePacketHandler::ZonePacketHandler(const String& s, Zone* z, ClientCore* clientCore) : Logger(s) {
	zone = z;
	core = clientCore;

	setLogging(true);
	setGlobalLogging(true);
	setLogLevel(static_cast<Logger::LogLevel>(ClientCore::getLogLevel()));
}

#define CASE_OPCODE(str) case STRING_HASHCODE(str): what = str

void ZonePacketHandler::handleMessage(Message* pack) {
	Locker lock(this);

	sys::uint16 opcount = pack->parseShort();
	sys::uint32 opcode = pack->parseInt();
	if (AgentControl::get() != nullptr && AgentControl::get()->onStandalonePacket(opcode, pack)) {
		zone->signal(opcode);
		return;
	}

	String what;

	switch (opcount) {
	case 1:
		switch (opcode) {
		CASE_OPCODE("CmdSceneReady");
			handleCmdSceneReady(pack);
			break;
		}
	case 2:
		switch (opcode) {
		CASE_OPCODE("ClientCreateCharacterSuccess");
			handleClientCreateCharacterSuccess(pack);
			break;
		CASE_OPCODE("SceneEndBaselines");
			break;
		CASE_OPCODE("ChatPersistentMessageToClient");
			break;
		CASE_OPCODE("ChatServerStatus");
			break;
		CASE_OPCODE("ParametersMessage");
			break;
		CASE_OPCODE("ServerTimeMessage");
			break;
		CASE_OPCODE("ChatRoomList");
			break;
		}
		break;
	case 3:
		switch (opcode) {
		CASE_OPCODE("ErrorMessage");
			handleErrorMessage(pack);
			break;
		CASE_OPCODE("ClientCreateCharacterFailed");
			handleClientCreateCharacterFailed(pack);
			break;
		CASE_OPCODE("UpdateCellPermissionMessage");
			break;
		CASE_OPCODE("ServerWeatherMessage");
			break;
		CASE_OPCODE("ChatOnGetFriendsList");
			break;
		CASE_OPCODE("ChatOnGetIgnoreList");
			break;
		CASE_OPCODE("ChatOnLeaveRoom");
			break;
		CASE_OPCODE("SceneDestroyObject");
			if (AgentControl::get() != nullptr)
				AgentControl::get()->onDestroy(pack->parseLong());
			break;
		}
		break;

	case 4:
		switch (opcode) {
		CASE_OPCODE("ClientPermissionsMessage");
			handleClientPermissionsMessage(pack);
			break;

		CASE_OPCODE("ClientRandomNameResponse");
			handleClientRandomNameResponse(pack);
			break;

		CASE_OPCODE("UpdateContainmentMessage");
			handleUpdateContainmentMessage(pack);
			break;

		CASE_OPCODE("ChatSystemMessage");
			handleChatSystemMessage(pack);
			break;

		CASE_OPCODE("UpdatePvpStatusMessage");
			break;
		}
		break;
	case 5:
		switch (opcode) {
		CASE_OPCODE("SceneCreateObjectByCrc");
			handleSceneObjectCreateMessage(pack);
			break;

		CASE_OPCODE("BaselinesMessage");
			handleBaselineMessage(pack);
			break;

		CASE_OPCODE("ChatInstantMessageToClient");
			handleChatInstantMessageToClient(pack);
			break;

		CASE_OPCODE("ObjControllerMessage");
			handleObjectControllerMessage(pack);
			break;

		CASE_OPCODE("DeltasMessage");
			break;

		CASE_OPCODE("ChatOnDestroyRoom");
			break;

		CASE_OPCODE("ChatOnEnteredRoom");
			break;
		}
		break;
	case 8:
		switch (opcode) {
		case 0x1B24F808: { // UpdateTransformMessage
			what = "UpdateTransformMessage";
			if (AgentControl::get() != nullptr) {
				uint64 oid = pack->parseLong();
				float x = pack->parseSignedShort() / 4.f;
				float z = pack->parseSignedShort() / 4.f;
				float y = pack->parseSignedShort() / 4.f;
				AgentControl::get()->onTransform(oid, 0, x, z, y);
			}
			break;
		}
		case 0xC867AB5A: { // UpdateTransformWithParentMessage
			what = "UpdateTransformWithParentMessage";
			if (AgentControl::get() != nullptr) {
				uint64 parent = pack->parseLong();
				uint64 oid = pack->parseLong();
				float x = pack->parseSignedShort() / 8.f;
				float z = pack->parseSignedShort() / 8.f;
				float y = pack->parseSignedShort() / 8.f;
				AgentControl::get()->onTransform(oid, parent, x, z, y);
			}
			break;
		}
		}
		break;
	case 9:
		switch (opcode) {
		CASE_OPCODE("CmdStartScene");
			handleCmdStartScene(pack);
			break;
		}
		break;
	}

	if (what.isEmpty()) {
		uint32 count = unknownOpcodes.contains(opcode) ? unknownOpcodes.get(opcode) : 0;
		unknownOpcodes.put(opcode, count + 1);
		what = "unknown";
	}

	debug() << __FUNCTION__ << ": " << what << "(opcount=" << opcount << ", opcode=0x" << uppercase << hex << opcode << ")";

	// Auto-signal for all recognized packets (signal() ignores if no waiter)
	if (!what.isEmpty() && what != "unknown") {
		zone->signal(opcode);
	}
}

void ZonePacketHandler::handleClientPermissionsMessage(Message* pack) {
	info(true) << __FUNCTION__;

	bool canLogin = pack->parseByte();
	bool canCreateRegularCharacter = pack->parseByte();
	bool canCreateJediCharacter = pack->parseByte();
	bool canSkipTutorial = pack->parseByte();

	// Store permissions on zone for actions to check
	zone->setPermissions(canLogin, canCreateRegularCharacter, canCreateJediCharacter, canSkipTutorial);

	info(true) << "Client permissions received:";
	info(true) << "    canLogin = " << canLogin;
	info(true) << "    canCreateCharacter = " << canCreateRegularCharacter;
	info(true) << "    canCreateJedi = " << canCreateJediCharacter;
	info(true) << "    canSkipTutorial = " << canSkipTutorial;
}

void ZonePacketHandler::handleCmdStartScene(Message* pack) {
	info(true) << __FUNCTION__;

	BaseClient* client = (BaseClient*) pack->getClient();

	uint8 unknown = pack->parseByte();
	uint64 selfPlayerObjectID = pack->parseLong();
	String terrain;
	pack->parseAscii(terrain);

	float x = pack->parseFloat();
	float z = pack->parseFloat();
	float y = pack->parseFloat();

	String race;
	pack->parseAscii(race);

	uint64 galacticTime = pack->parseLong();

	if (AgentControl::get() != nullptr)
		AgentControl::get()->onStartScene(selfPlayerObjectID, terrain, x, z, y);

	// Server confirms our character OID
	if (core->selectedCharacterOid != selfPlayerObjectID) {
		error() << "Scene starting for wrong OID: " << selfPlayerObjectID
			<< "; expected OID: " << core->selectedCharacterOid
			<< "; aborting Scene.";
		return;
	}

	info(true) << "Scene Starting for character OID: " << selfPlayerObjectID;

	BaseMessage* msg = new CmdSceneReady();
	client->sendPacket(msg);

	zone->setSceneStarted();
}

void ZonePacketHandler::handleSceneObjectCreateMessage(Message* pack) {
	BaseClient* client = (BaseClient*) pack->getClient();
	uint64 objectID = pack->parseLong();
	pack->shiftOffset(16);

	float x = pack->parseFloat();
	float z = pack->parseFloat();
	float y = pack->parseFloat();

	uint32 crc = pack->parseInt();

	if (AgentControl::get() != nullptr)
		AgentControl::get()->onCreate(objectID, crc, x, z, y);

	ObjectManager* objectManager = zone->getObjectManager();
	if (objectManager == nullptr) {
		error("object manager was nullptr");
		return;
	}

	SceneObject* object = objectManager->createObject(crc, objectID);

	if (object == nullptr) {
		client->debug() << "unknown crc 0x" << hex << crc << " received in SceneObjectCreateMessage";
		return;
	}

	object->setClient(zone->getZoneClient());
}

void ZonePacketHandler::handleBaselineMessage(Message* pack) {
	BaseClient* client = (BaseClient*) pack->getClient();

	uint64 oid = pack->parseLong();
	uint32 nametype = pack->parseInt();
	uint8 type = pack->parseByte();

	uint32 size = pack->parseInt();

	uint16 opcount = pack->parseShort();

	if (type == 3 && AgentControl::get() != nullptr) {
		int offset = pack->getOffset();
		try {
			AgentControl::get()->onBaseline3(oid, nametype, pack);
		} catch (...) {
		}
		pack->setOffset(offset);
	}

	SceneObject* object = zone->getObject(oid);

	if (object == nullptr) {
		client->debug("received baseline for null object");
		return;
	}

	Locker objectLocker(object);

	switch (type) {
	case 3:
		object->parseBaseline3(pack);
		break;
	case 6:
		object->parseBaseline6(pack);
		break;
	default:
		break;
	}
}

void ZonePacketHandler::handleChatInstantMessageToClient(Message* pack) {
	BaseClient* client = (BaseClient*) pack->getClient();

	String game, galaxy, name;
	UnicodeString message;

	pack->parseAscii(game);
	pack->parseAscii(galaxy);
	pack->parseAscii(name);
	pack->parseUnicode(message);

	if (AgentControl::get() != nullptr)
		AgentControl::get()->onInstantMessage(name, message.toString());

	StringBuffer infoMsg;
	infoMsg << "instant message from [" << name << "] : " << message.toString();
	client->info(infoMsg.toString());
}

void ZonePacketHandler::handleChatSystemMessage(Message* pack) {
	info(true) << __FUNCTION__;

	BaseClient* client = (BaseClient*) pack->getClient();

	uint8 type = pack->parseByte();

	UnicodeString message;
	pack->parseUnicode(message);

	if (AgentControl::get() != nullptr) {
		if (message.isEmpty())
			AgentControl::get()->onStringIdSystemMessage(pack);
		else
			AgentControl::get()->onSystemMessage(message.toString());
	}

	info(true) << "type=" << type << "; len=" << message.length();

	StringTokenizer lines(message.toString());
	lines.setDelimeter("\n");

	while (lines.hasMoreTokens()) {
		String line;
		lines.getStringToken(line);
		info(true) << "> " << line;
	}
}

void ZonePacketHandler::handleObjectControllerMessage(Message* pack) {
	uint32 header1 = pack->parseInt();
	uint32 header2 = pack->parseInt();

	uint64 objectID = pack->parseLong();

	pack->parseInt();

	if (AgentControl::get() != nullptr) {
		try {
			AgentControl::get()->onObjController(header2, objectID, pack);
		} catch (...) {
		}
	}

	SceneObject* object = zone->getObject(objectID);

	if (object != nullptr) {
		// No object controller handling needed
	}
}

void ZonePacketHandler::handleUpdateContainmentMessage(Message* pack) {
	uint64 obj = pack->parseLong();
	uint64 par = pack->parseLong();

	if (AgentControl::get() != nullptr)
		AgentControl::get()->onContainment(obj, par);

	int type = pack->parseInt();

	SceneObject* object = zone->getObject(obj);
	SceneObject* parent = zone->getObject(par);

	if (object == nullptr)
		return;

	if (par == 0) {
		// remove object from parent
		parent = object->getParent();

		if (parent != nullptr) {
			// No container removal needed
		} else {
			object->setParent(nullptr);
		}

		return;
	} else if (parent == nullptr) {
		return;
	}

	// No container transfer needed
}

void ZonePacketHandler::handleCmdSceneReady(Message* pack) {
	info(true) << __FUNCTION__;

	zone->setSceneReady();
}

void ZonePacketHandler::handleClientCreateCharacterSuccess(Message* pack) {
	info(true) << __FUNCTION__;

	uint64 newCharacterOID = pack->parseLong();

	info(true) << "Character creation SUCCESS - OID: " << newCharacterOID;

	// Store in vars
	core->setVar("ClientCreateCharacterSuccess/oid", newCharacterOID);

	// Now send SelectCharacter with the new OID
	BaseClient* client = (BaseClient*) pack->getClient();
	info(true) << "Sending SelectCharacter(" << newCharacterOID << ")";

	BaseMessage* selectChar = new SelectCharacter(newCharacterOID);
	client->sendPacket(selectChar);
}

void ZonePacketHandler::handleClientCreateCharacterFailed(Message* pack) {
	info(true) << __FUNCTION__;

	uint32 unicodeLength = pack->parseInt();
	String uiFile;
	pack->parseAscii(uiFile);
	uint32 spacer = pack->parseInt();
	String errorCode;
	pack->parseAscii(errorCode);

	error() << "Character creation FAILED";
	error() << "  Error code: " << errorCode;
	error() << "  UI file: " << uiFile;

	// Store in vars
	core->setVar("ClientCreateCharacterFailed/errorCode", errorCode);
	core->setVar("ClientCreateCharacterFailed/uiFile", uiFile);
}

void ZonePacketHandler::handleErrorMessage(Message* pack) {
	info(true) << __FUNCTION__;

	String errorType, errorMessage;
	pack->parseAscii(errorType);
	pack->parseAscii(errorMessage);

	error() << "Zone ERROR: " << errorType << " - " << errorMessage;

	// Store in vars
	core->setVar("ErrorMessage/type", errorType);
	core->setVar("ErrorMessage/message", errorMessage);
	core->setVar("ErrorMessage/source", "ZonePacketHandler");

	zone->setError(errorMessage, 1);
}

void ZonePacketHandler::handleClientRandomNameResponse(Message* pack) {
	info(true) << __FUNCTION__;

	String templatePath;
	pack->parseAscii(templatePath);

	UnicodeString suggestedName;
	pack->parseUnicode(suggestedName);

	uint32 unused1 = pack->parseInt();
	uint32 unused2 = pack->parseInt();

	String approvalStatus;
	pack->parseAscii(approvalStatus);

	info(true) << "Random name response:";
	info(true) << "  Template: " << templatePath;
	info(true) << "  Suggested name: " << suggestedName.toString();
	info(true) << "  Approval: " << approvalStatus;

	// Store in vars
	core->setVar("ClientRandomNameResponse/name", suggestedName.toString());
	core->setVar("ClientRandomNameResponse/template", templatePath);
	core->setVar("ClientRandomNameResponse/approval", approvalStatus);
}
