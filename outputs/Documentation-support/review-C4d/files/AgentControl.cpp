/*
 * AgentControl.cpp - see AgentControl.h
 */

#include "AgentControl.h"
#include "client/zone/Zone.h"
#include "client/zone/ZoneClient.h"
#include "server/zone/packets/object/ObjectControllerMessage.h"

#include <algorithm>
#include <cmath>
#include <iostream>
#include <thread>

static AgentControl* agentInstance = nullptr;

// Client-to-server object controller header without ObjectControllerMessage's trailing
// int: the server's DataTransform and TeleportAck parsers start right after the object ID
// (CommandQueueEnqueue does expect that int, so it keeps using ObjectControllerMessage).
class ClientObjectController : public BaseMessage {
public:
	ClientObjectController(uint64 objid, uint32 header1, uint32 type) {
		insertShort(0x05);
		insertInt(0x80CE5E46);
		insertInt(header1);
		insertInt(type);
		insertLong(objid);
		setCompression(true);
	}
};

void AgentControl::enable() {
	if (agentInstance == nullptr)
		agentInstance = new AgentControl();
}

AgentControl* AgentControl::get() {
	return agentInstance;
}

void AgentControl::emit(const JSONSerializationType& message) {
	// One write per line so log output from other threads cannot split it.
	std::string line = "@@AGENT " + message.dump(-1, ' ', false, nlohmann::json::error_handler_t::replace) + "\n";
	std::lock_guard<std::mutex> lock(outMutex);
	fwrite(line.data(), 1, line.size(), stdout);
	fflush(stdout);
}

static std::string str(const String& s) {
	return std::string(s.toCharArray());
}

static std::string typeName(uint32 code) {
	std::string out;
	for (int shift = 24; shift >= 0; shift -= 8) {
		char c = (char) ((code >> shift) & 0xFF);
		if (c >= 32 && c < 127)
			out += c;
	}
	return out;
}

// A DeltaVector baseline: int count, int update counter, then count elements.
static void skipList(Message* pack, int elementSize) {
	uint32 count = pack->parseInt();
	pack->parseInt();
	if (count > 1000)
		throw std::runtime_error("oversized list");
	pack->shiftOffset(count * elementSize);
}

static std::vector<int> parseIntList(Message* pack) {
	uint32 count = pack->parseInt();
	pack->parseInt();
	if (count > 1000)
		throw std::runtime_error("oversized list");
	std::vector<int> values;
	for (uint32 i = 0; i < count; ++i)
		values.push_back(pack->parseInt());
	return values;
}

// Radial menu option names, generated from server/zone/managers/radial/RadialOptions.h
static const char* radialNames[] = {
	"unknown", "combat_target", "combat_untarget", "combat_attack", "combat_peace", "combat_duel",
	"combat_death_blow", "examine", "trade_start", "trade_accept", "item_pickup", "item_equip",
	"item_unequip", "item_drop", "item_destroy", "item_token", "item_open", "item_open_new_window",
	"item_activate", "item_deactivate", "item_use", "item_use_self", "item_use_other", "item_sit",
	"item_mail", "converse_start", "converse_respond", "converse_response", "converse_stop", "craft_options",
	"craft_start", "craft_hopper_input", "craft_hopper_output", "mission_terminal_list", "mission_details", "loot",
	"loot_all", "group_invite", "group_join", "group_leave", "group_kick", "group_disband",
	"group_decline", "extract_object", "pet_call", "terminal_auction_use", "creature_follow", "creature_stop_follow",
	"split", "imagedesign", "set_name", "item_rotate", "item_rotate_right", "item_rotate_left",
	"item_move", "item_move_forward", "item_move_back", "item_move_up", "item_move_down", "pet_store",
	"vehicle_generate", "vehicle_store", "mission_abort", "mission_end_duty", "ship_manage_components", "waypoint_autopilot",
	"program_droid", "server_divider", "server_menu1", "server_menu2", "server_menu3", "server_menu4",
	"server_menu5", "server_menu6", "server_menu7", "server_menu8", "server_menu9", "server_menu10",
	"server_harvester_manage", "server_house_manage", "server_faction_hall_manage", "server_hue", "server_observe", "server_stop_observing",
	"server_travel_options", "server_bazaar_options", "server_shipping_options", "server_heal_wound", "server_heal_wound_health", "server_heal_wound_action",
	"server_heal_wound_strength", "server_heal_wound_constitution", "server_heal_wound_quickness", "server_heal_wound_stamina", "server_heal_damage", "server_heal_state",
	"server_heal_state_stunned", "server_heal_state_blinded", "server_heal_state_dizzy", "server_heal_state_intimidated", "server_heal_enhance", "server_heal_enhance_health",
	"server_heal_enhance_action", "server_heal_enhance_strength", "server_heal_enhance_constitution", "server_heal_enhance_quickness", "server_heal_enhance_stamina", "server_heal_firstaid",
	"server_heal_cure_poison", "server_heal_cure_disease", "server_heal_apply_poison", "server_heal_apply_disease", "server_harvest_corpse", "server_performance_listen",
	"server_performance_watch", "server_performance_listen_stop", "server_performance_watch_stop", "server_terminal_permissions", "server_terminal_management", "server_terminal_permissions_enter",
	"server_terminal_permissions_banned", "server_terminal_permissions_admin", "server_terminal_permissions_vendor", "server_terminal_permissions_hopper", "server_terminal_management_status", "server_terminal_management_privacy",
	"server_terminal_management_transfer", "server_terminal_management_residence", "server_terminal_management_destroy", "server_terminal_management_pay", "server_terminal_create_vendor", "server_give_vendor_maintenance",
	"server_item_options", "server_survey_tool_range", "server_survey_tool_resolution", "server_survey_tool_class", "server_probe_droid_track_target", "server_probe_droid_find_target",
	"server_probe_droid_activate", "server_probe_droid_buy", "server_teach", "pet_command", "pet_follow", "pet_stay",
	"pet_guard", "pet_friend", "pet_attack", "pet_patrol", "pet_get_patrol_point", "pet_clear_patrol_points",
	"pet_assume_formation_1", "pet_assume_formation_2", "pet_transfer", "pet_release", "pet_trick_1", "pet_trick_2",
	"pet_trick_3", "pet_trick_4", "pet_group", "pet_tame", "pet_feed", "pet_special_attack_one",
	"pet_special_attack_two", "pet_ranged_attack", "dice_roll", "dice_two_face", "dice_three_face", "dice_four_face",
	"dice_five_face", "dice_six_face", "dice_seven_face", "dice_eight_face", "dice_count_one", "dice_count_two",
	"dice_count_three", "dice_count_four", "create_ballot", "vote", "bombing_run", "self_destruct",
	"thirty_sec", "fifteen_sec", "server_camp_disband", "server_camp_assume_ownership", "server_probe_droid_program", "server_guild_create",
	"server_guild_info", "server_guild_members", "server_guild_sponsored", "server_guild_enemies", "server_guild_sponsor", "server_guild_disband",
	"server_guild_namechange", "server_guild_guild_management", "server_guild_member_management", "server_manf_hopper_input", "server_manf_hopper_output", "server_manf_station_schematic",
	"elevator_up", "elevator_down", "server_pet_open", "server_pet_dpad", "server_med_tool_diagnose", "server_med_tool_tendwound",
	"server_med_tool_tenddamage", "server_pet_mount", "server_pet_dismount", "server_pet_train_mount", "server_vehicle_enter", "server_vehicle_exit",
	"open_navicomp_dpad", "init_navicomp_dpad", "city_status", "city_citizens", "city_structures", "city_treasury",
	"city_management", "city_name", "city_militia", "city_taxes", "city_treasury_deposit", "city_treasury_withdraw",
	"city_register", "city_rank", "city_admin_1", "city_admin_2", "city_admin_3", "city_admin_4",
	"city_admin_5", "city_admin_6", "memory_chip_program", "memory_chip_transfer", "memory_chip_analyze", "equip_droid_on_ship",
};

void AgentControl::onStartScene(uint64 oid, const String& terrain, float x, float z, float y) {
	{
		std::lock_guard<std::recursive_mutex> lock(worldMutex);
		self = oid;
		// A new scene (login or zone change): the server resends every object, so drop the old
		// scene's objects, including our stale container (e.g. the tutorial room).
		world.clear();
		selfParent = 0;
		radialMenus.clear(); suiPages.clear(); conversationOptions.clear();
		missions.clear(); // mission objects are resent with the new scene
		conversationActive = false; conversationNpc = 0;
		planet = str(terrain);
		size_t slash = planet.rfind('/');
		if (slash != std::string::npos)
			planet = planet.substr(slash + 1);
		if (planet.size() > 4 && planet.substr(planet.size() - 4) == ".trn")
			planet = planet.substr(0, planet.size() - 4);
		selfX = x; selfZ = z; selfY = y;
	}
	emit({{"event", "scene_start"}, {"self", oid}, {"planet", planet}, {"x", x}, {"y", y}, {"z", z}});

	// A planet change (e.g. /teleport to another zone) leaves us flagged as teleporting
	// again; acknowledge once the new scene is up, or all movement is ignored.
	if (zone != nullptr) {
		std::thread([this]() {
			Thread::sleep(2000);
			sendTeleportAck(moveCount);
		}).detach();
	}
}

void AgentControl::onCreate(uint64 oid, uint32 crc, float x, float z, float y) {
	std::lock_guard<std::recursive_mutex> lock(worldMutex);
	WorldObject& object = world[oid];
	object.oid = oid;
	object.crc = crc;
	object.x = x; object.z = z; object.y = y;
}

void AgentControl::onTransform(uint64 oid, uint64 parent, float x, float z, float y) {
	std::lock_guard<std::recursive_mutex> lock(worldMutex);
	if (oid == self) {
		// The server moved us (teleport, correction): accept its position.
		selfX = x; selfZ = z; selfY = y; selfParent = parent;
	}
	WorldObject& object = world[oid];
	object.oid = oid;
	object.x = x; object.z = z; object.y = y;
	object.parent = parent;
}

void AgentControl::onDestroy(uint64 oid) {
	std::string name;
	{
		std::lock_guard<std::recursive_mutex> lock(worldMutex);
		auto it = world.find(oid);
		radialMenus.erase(oid);
		missions.erase(oid); // also when the object was already dropped with its scene
		if (it == world.end())
			return;
		bool creature = it->second.type == "CREO";
		name = it->second.name;
		world.erase(it);
		if (!creature)
			return;
	}
	emit({{"event", "gone"}, {"oid", oid}, {"name", name}});
}

void AgentControl::onContainment(uint64 oid, uint64 parent) {
	std::lock_guard<std::recursive_mutex> lock(worldMutex);
	world[oid].oid = oid;
	world[oid].parent = parent;
	// Logging in (or being moved) into a building cell arrives as containment, not as a
	// transform; without this look() filters by the wrong cell. A vehicle is not a cell.
	if (oid == self) {
		auto it = world.find(parent);
		if (parent == 0 || (it != world.end() && it->second.type == "SCLT"))
			selfParent = parent;
	}
}

void AgentControl::onBaseline3(uint64 oid, uint32 typeCode, Message* pack) {
	std::string type = typeName(typeCode);
	pack->parseFloat(); // complexity
	String file, key;
	pack->parseAscii(file);
	pack->parseInt();
	pack->parseAscii(key);
	UnicodeString custom;
	pack->parseUnicode(custom);

	{
		std::lock_guard<std::recursive_mutex> lock(worldMutex);
		WorldObject& object = world[oid];
		object.oid = oid;
		object.type = type;
		if (!custom.isEmpty())
			object.name = str(custom.toString());
		else if (!key.isEmpty())
			object.name = "@" + str(file) + ":" + str(key);
	}
	if (type == "MISO") { // MissionObjectMessage3: fields 3..16 follow the name
		std::lock_guard<std::recursive_mutex> lock(worldMutex);
		JSONSerializationType& mission = missions[oid];
		mission = JSONSerializationType::object(); // a full baseline replaces the record
		mission["oid"] = oid;
		for (uint16 index = 3; index <= 16; ++index)
			if (!parseMissionField(mission, index, pack))
				break;
		return;
	}
	if (type != "CREO")
		return;

	// Rest of TangibleObjectMessage3, then CreatureObjectMessage3
	pack->parseInt(); // volume
	String customization;
	pack->parseAscii(customization);
	skipList(pack, 4); // visible components
	pack->parseInt(); // options
	pack->parseInt(); // use count
	pack->parseInt(); // condition damage
	pack->parseInt(); // max condition
	pack->parseByte(); // visible
	int posture = pack->parseByte();
	pack->parseByte(); // faction rank
	pack->parseLong(); // creature link (mount)
	pack->parseFloat(); // height
	pack->parseInt(); // shock wounds
	uint64 states = pack->parseLong();
	setPosture(oid, posture);
	setStates(oid, states);
}

static std::string planetName(uint32 crc) {
	static const char* planets[] = {"tatooine", "naboo", "corellia", "rori", "talus", "dantooine", "lok", "yavin4",
									"endor", "dathomir", "tutorial", "dungeon1"};
	for (const char* planet : planets)
		if (String(planet).hashCode() == crc)
			return planet;
	return std::to_string(crc);
}

static std::string missionTypeName(uint32 crc) {
	static const char* types[] = {"destroy", "deliver", "bounty", "survey", "crafting", "musician", "dancer",
								  "hunting", "recon", "escort"};
	for (const char* type : types)
		if (String(type).hashCode() == crc)
			return type;
	return std::to_string(crc);
}

// One MissionObjectMessage3 field by its index (the baseline order and the delta indices are the same).
// Returns false for an index whose size is unknown, so the caller stops reading.
bool AgentControl::parseMissionField(JSONSerializationType& mission, uint16 index, Message* pack) {
	String a, b;
	UnicodeString text;
	auto location = [&](const char* key) {
		float x = pack->parseFloat(), z = pack->parseFloat(), y = pack->parseFloat();
		pack->parseLong();
		mission[key] = {{"x", x}, {"y", y}, {"z", z}, {"planet", planetName(pack->parseInt())}};
	};
	auto stringId = [&](const char* key) {
		pack->parseAscii(a);
		pack->parseInt();
		pack->parseAscii(b);
		mission[key] = "@" + str(a) + ":" + str(b);
	};
	switch (index) {
	case 0x00: pack->parseFloat(); break;
	case 0x01: stringId("name"); break;
	case 0x02: pack->parseUnicode(text); break;
	case 0x03: case 0x04: case 0x0D: pack->parseInt(); break;
	case 0x05: mission["difficulty"] = pack->parseInt(); break;
	case 0x06: location("end"); break;
	case 0x07: pack->parseUnicode(text); mission["creator"] = str(text.toString()); break;
	case 0x08: mission["reward"] = pack->parseInt(); break;
	case 0x09: location("start"); break;
	case 0x0A: mission["target_crc"] = pack->parseInt(); break;
	case 0x0B: stringId("description"); break;
	case 0x0C: stringId("title"); break;
	case 0x0E: { uint32 crc = pack->parseInt(); mission["type"] = missionTypeName(crc); break; }
	case 0x0F: pack->parseAscii(a); mission["target"] = str(a); break;
	case 0x10: { // waypoint
		pack->parseInt();
		float x = pack->parseFloat(), z = pack->parseFloat(), y = pack->parseFloat();
		pack->parseLong();
		std::string planet = planetName(pack->parseInt());
		pack->parseUnicode(text);
		uint64 waypointId = pack->parseLong();
		pack->parseByte();
		pack->parseByte();
		if (waypointId != 0 || x != 0 || y != 0)
			mission["waypoint"] = {{"x", x}, {"y", y}, {"z", z}, {"planet", planet}};
		else
			mission.erase("waypoint"); // cleared on a refresh: don't keep the previous mission's destination
		break;
	}
	default: return false;
	}
	return true;
}

void AgentControl::onBaseline6(uint64 oid, uint32 typeCode, Message* pack) {
	if (typeName(typeCode) != "CREO")
		return;
	pack->parseInt();
	skipList(pack, 8); // defenders
	uint16 level = pack->parseShort();
	String text;
	pack->parseAscii(text); // performance animation
	pack->parseAscii(text); // mood
	uint64 weapon = pack->parseLong();
	uint64 group = pack->parseLong();
	pack->parseLong(); // group inviter
	pack->parseLong(); // invite counter
	pack->parseInt(); // guild
	uint64 target = pack->parseLong();
	pack->parseByte(); // mood id
	pack->parseInt(); // performance start
	pack->parseInt(); // performance type
	std::vector<int> ham = parseIntList(pack), maxHam = parseIntList(pack);

	std::lock_guard<std::recursive_mutex> lock(worldMutex);
	WorldObject& object = world[oid];
	object.oid = oid;
	object.level = level;
	object.weapon = weapon;
	object.group = group;
	object.target = target;
	object.ham = ham;
	object.maxHam = maxHam;
}

// DeltaVector update ops: 0 remove(idx), 1 add(idx, value), 2 change(idx, value),
// 3 reset(count, values...), 4 clear. Applies int updates to `list` when given.
static bool applyListDelta(Message* pack, int elementSize, std::vector<int>* list) {
	uint32 count = pack->parseInt();
	pack->parseInt(); // update counter
	if (count > 1000)
		return false;
	for (uint32 i = 0; i < count; ++i) {
		uint8 op = pack->parseByte();
		if (op == 4) {
			if (list) list->clear();
			continue;
		}
		if (op == 3) {
			uint16 n = pack->parseShort();
			if (list) list->clear();
			for (int k = 0; k < n; ++k) {
				if (elementSize == 4) {
					int v = pack->parseInt();
					if (list) list->push_back(v);
				} else {
					pack->shiftOffset(elementSize);
				}
			}
			continue;
		}
		uint16 idx = pack->parseShort();
		if (op == 0) {
			if (list && idx < list->size()) list->erase(list->begin() + idx);
			continue;
		}
		if (op != 1 && op != 2)
			return false;
		if (elementSize == 4) {
			int v = pack->parseInt();
			if (list) {
				if (op == 2 && idx < list->size()) (*list)[idx] = v;
				else if (op == 1) list->insert(list->begin() + std::min((size_t) idx, list->size()), v);
			}
		} else {
			pack->shiftOffset(elementSize);
		}
	}
	return true;
}

void AgentControl::onDelta(uint64 oid, uint32 typeCode, uint8 type, Message* pack) {
	if (typeName(typeCode) == "MISO" && type == 3) { // a terminal refresh rewrites existing mission objects
		std::lock_guard<std::recursive_mutex> lock(worldMutex);
		JSONSerializationType& mission = missions[oid];
		mission["oid"] = oid;
		uint16 updates = pack->parseShort();
		for (int u = 0; u < updates; ++u)
			if (!parseMissionField(mission, pack->parseShort(), pack))
				return;
		return;
	}
	if (typeName(typeCode) != "CREO" || (type != 3 && type != 6))
		return;
	uint16 updates = pack->parseShort();
	for (int u = 0; u < updates; ++u) {
		uint16 index = pack->parseShort();
		String text;
		if (type == 3) {
			switch (index) {
			case 0x00: pack->parseFloat(); break;
			case 0x01: pack->parseAscii(text); pack->parseInt(); pack->parseAscii(text); break;
			case 0x02: { UnicodeString name; pack->parseUnicode(name); break; }
			case 0x04: pack->parseAscii(text); break;
			case 0x05: if (!applyListDelta(pack, 4, nullptr)) return; break;
			case 0x03: case 0x06: case 0x07: case 0x08: case 0x09: case 0x0F: pack->parseInt(); break;
			case 0x0A: case 0x0C: pack->parseByte(); break;
			case 0x0B: setPosture(oid, pack->parseByte()); break;
			case 0x0D: pack->parseLong(); break;
			case 0x0E: pack->parseFloat(); break;
			case 0x10: setStates(oid, pack->parseLong()); break;
			case 0x11: if (!applyListDelta(pack, 4, nullptr)) return; break; // wounds
			default: return; // unknown size: stop parsing this message
			}
		} else {
			std::lock_guard<std::recursive_mutex> lock(worldMutex);
			WorldObject& object = world[oid];
			switch (index) {
			case 0x00: case 0x08: case 0x0B: case 0x0C: pack->parseInt(); break;
			case 0x01: if (!applyListDelta(pack, 8, nullptr)) return; break; // defenders
			case 0x02: object.level = pack->parseShort(); break;
			case 0x03: case 0x04: case 0x10: pack->parseAscii(text); break;
			case 0x05: object.weapon = pack->parseLong(); break;
			case 0x06: {
				uint64 group = pack->parseLong();
				if (oid == self && group != object.group)
					emit({{"event", group ? "group_joined" : "group_left"}, {"group", group}});
				object.group = group;
				break;
			}
			case 0x07: pack->parseLong(); pack->parseLong(); break;
			case 0x09: object.target = pack->parseLong(); break;
			case 0x0A: case 0x11: pack->parseByte(); break;
			case 0x0D: if (!applyListDelta(pack, 4, &object.ham)) return; break;
			case 0x0E: if (!applyListDelta(pack, 4, &object.maxHam)) return; break;
			default: return;
			}
		}
	}
}

static const char* postureName(int posture) {
	static const char* names[] = {"upright", "crouched", "prone", "sneaking", "blocking", "climbing", "flying",
		"lying down", "sitting", "skill animating", "driving vehicle", "riding creature", "knocked down",
		"incapacitated", "dead"};
	return posture >= 0 && posture <= 14 ? names[posture] : "unknown";
}

static JSONSerializationType stateNames(uint64 states) {
	static const std::pair<uint64, const char*> known[] = {{0x02, "combat"}, {0x04, "peace"}, {0x1000, "stunned"},
		{0x2000, "blinded"}, {0x4000, "dizzy"}, {0x8000, "intimidated"}, {0x10000, "immobilized"},
		{0x40000, "swimming"}, {0x100000, "crafting"}, {0x800000, "poisoned"}, {0x1000000, "bleeding"},
		{0x2000000, "diseased"}, {0x4000000, "on fire"}, {0x8000000, "riding mount"}, {0x20000000, "piloting ship"}};
	JSONSerializationType out = JSONSerializationType::array();
	for (const auto& state : known)
		if (states & state.first)
			out.push_back(state.second);
	return out;
}

void AgentControl::setPosture(uint64 oid, int posture) {
	std::string name;
	int previous;
	{
		std::lock_guard<std::recursive_mutex> lock(worldMutex);
		WorldObject& object = world[oid];
		previous = object.posture;
		object.posture = posture;
		name = object.name;
	}
	if (previous == posture || previous == -1)
		return;
	// Our own posture changes, and anyone else being incapacitated or killed.
	if (oid == self || posture == 13 || posture == 14)
		emit({{"event", "posture"}, {"oid", oid}, {"name", oid == self ? "me" : name},
			  {"posture", postureName(posture)}});
}

void AgentControl::setStates(uint64 oid, uint64 states) {
	uint64 previous;
	{
		std::lock_guard<std::recursive_mutex> lock(worldMutex);
		WorldObject& object = world[oid];
		previous = object.states;
		object.states = states;
	}
	if (oid == self && (previous & 0x02) != (states & 0x02))
		emit({{"event", (states & 0x02) ? "combat_started" : "combat_ended"}});
}

JSONSerializationType AgentControl::creatureState(const WorldObject& object) {
	JSONSerializationType state = {{"posture", postureName(object.posture)}, {"states", stateNames(object.states)}};
	if (object.ham.size() >= 9 && object.maxHam.size() >= 9) {
		// Pools are health/action/mind at indices 0, 3, 6 (the others are strength, constitution, ...).
		state["ham"] = {{"health", object.ham[0]}, {"action", object.ham[3]}, {"mind", object.ham[6]}};
		state["max_ham"] = {{"health", object.maxHam[0]}, {"action", object.maxHam[3]}, {"mind", object.maxHam[6]}};
	}
	if (object.level) state["level"] = object.level;
	if (object.group) state["group"] = object.group;
	if (object.target) state["target"] = object.target;
	return state;
}

void AgentControl::onSystemMessage(const String& text) {
	if (text.beginsWith("[agentpath] ")) {
		std::lock_guard<std::recursive_mutex> lock(worldMutex);
		helperReply = str(text.subString(12));
		++helperReplies;
		return;
	}
	emit({{"event", "system"}, {"text", str(text)}});
}

void AgentControl::onStringIdSystemMessage(Message* pack) {
	// String-table messages carry "file" and "key" inside an out-of-band blob; pull out the
	// identifier-like ASCII runs so the agent sees e.g. "@error_message:target_out_of_range".
	std::vector<std::string> words;
	std::string current;
	while (pack->getOffset() < pack->size()) {
		char c = (char) pack->parseByte();
		if ((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '_') {
			current += c;
		} else if (c != 0) {
			if (current.size() >= 3)
				words.push_back(current);
			current.clear();
		}
	}
	if (current.size() >= 3)
		words.push_back(current);
	if (words.size() >= 2)
		emit({{"event", "system"}, {"text", "@" + words[0] + ":" + words[1]}});
	else if (!words.empty())
		emit({{"event", "system"}, {"text", "@" + words[0]}});
}

void AgentControl::onInstantMessage(const String& from, const String& text) {
	emit({{"event", "tell"}, {"from", str(from)}, {"text", str(text)}});
}

std::string AgentControl::nameOf(uint64 oid) {
	std::lock_guard<std::recursive_mutex> lock(worldMutex);
	auto it = world.find(oid);
	return it == world.end() ? std::string() : it->second.name;
}

void AgentControl::onObjController(uint32 type, uint64 oid, Message* pack) {
	if (oid != self)
		return;

	switch (type) {
	case 0x147: { // ObjectMenuResponse (header's trailing int already consumed)
		uint64 target = pack->parseLong();
		pack->parseLong();
		uint32 count = pack->parseInt();
		if (count > 256) throw std::runtime_error("oversized radial menu");
		JSONSerializationType items = JSONSerializationType::array();
		for (uint32 i = 0; i < count; ++i) {
			uint8 index = pack->parseByte(), parent = pack->parseByte();
			uint8 radial = pack->parseByte(), callback = pack->parseByte();
			UnicodeString label; pack->parseUnicode(label);
			int known = sizeof(radialNames) / sizeof(radialNames[0]);
			items.push_back({{"index", index}, {"parent", parent}, {"radial_id", radial},
				{"name", radial < known ? radialNames[radial] : "unknown"},
				{"callback", callback}, {"label", str(label.toString())}});
		}
		uint8 counter = pack->parseByte();
		{ std::lock_guard<std::recursive_mutex> lock(worldMutex); radialMenus[target] = items; }
		emit({{"event", "radial_menu"}, {"target", target}, {"counter", counter}, {"items", items}});
		break;
	}
	case 0x134: { // CombatSpam: "%TU hits %TT for %DI points" etc., also for nearby fights
		uint64 attacker = pack->parseLong(), defender = pack->parseLong(), item = pack->parseLong();
		uint32 amount = pack->parseInt();
		String file, key;
		pack->parseAscii(file);
		pack->parseInt();
		pack->parseAscii(key);
		pack->parseByte(); // colour
		UnicodeString text;
		pack->parseUnicode(text);
		JSONSerializationType event = {{"event", "combat"}, {"attacker", attacker},
			{"attacker_name", attacker == self ? "me" : nameOf(attacker)}, {"defender", defender},
			{"defender_name", defender == self ? "me" : nameOf(defender)}, {"amount", amount}};
		if (!key.isEmpty())
			event["what"] = "@" + str(file) + ":" + str(key);
		if (!text.isEmpty())
			event["text"] = str(text.toString());
		if (item)
			event["weapon"] = item;
		emit(event);
		break;
	}
	case 0xF4: { // SpatialChat
		uint64 sender = pack->parseLong();
		pack->parseLong();
		UnicodeString message;
		pack->parseUnicode(message);
		emit({{"event", "chat"}, {"from_oid", sender}, {"from", sender == self ? "me" : nameOf(sender)},
			  {"text", str(message.toString())}});
		break;
	}
	case 0x71:   // DataTransform from the server = we were teleported/corrected
	case 0xF1: { // DataTransformWithParent (into a building cell)
		uint32 counter = pack->parseInt();
		uint64 parent = type == 0xF1 ? pack->parseLong() : 0;
		for (int i = 0; i < 4; ++i)
			pack->parseFloat(); // direction
		float x = pack->parseFloat(), z = pack->parseFloat(), y = pack->parseFloat();
		{
			std::lock_guard<std::recursive_mutex> lock(worldMutex);
			selfX = x; selfZ = z; selfY = y; selfParent = parent;
			moveCount = counter;
			++serverCorrections;
		}
		// The server ignores our movement until we acknowledge its teleport.
		if (zone != nullptr)
			sendTeleportAck(counter);
		emit({{"event", "position_set_by_server"}, {"x", x}, {"y", y}, {"z", z}, {"cell", parent}});
		break;
	}
	case 0x117: { // CommandQueueRemove: a queued command finished; report failures
		uint32 action = pack->parseInt();
		pack->parseFloat();
		uint32 error = pack->parseInt();
		uint32 detail = pack->parseInt();
		if (error != 0) {
			// Codes as the server sends them (QueueCommand.cpp, ObjectControllerImplementation.cpp): 1 locomotion
			// (detail = locomotion), 2 ability missing / not allowed, 3 invalid target, 5 state (detail = state bit).
			static const char* reasons[] = {"ok", "wrong locomotion", "missing ability or not allowed", "invalid target",
				"unknown", "invalid state", "too far", "unknown", "invalid parameters", "unknown", "unknown",
				"insufficient permission", "not allowed in jedi armor"};
			std::string name;
			{
				std::lock_guard<std::recursive_mutex> lock(worldMutex);
				auto it = commandNames.find(action);
				if (it != commandNames.end())
					name = it->second;
			}
			emit({{"event", "command_failed"}, {"command", name}, {"error", error},
				  {"reason", error < 13 ? reasons[error] : "unknown"}, {"detail", detail}});
		}
		break;
	}
	case 0xDD: { // NPC conversation started
		uint64 npc = pack->parseLong();
		{
			std::lock_guard<std::recursive_mutex> lock(worldMutex);
			conversationNpc = npc;
			conversationActive = true;
		}
		emit({{"event", "conversation_start"}, {"npc_oid", npc}});
		break;
	}
	case 0xDE: // NPC conversation ended
		{
			std::lock_guard<std::recursive_mutex> lock(worldMutex);
			conversationOptions.clear();
			conversationActive = false;
			conversationNpc = 0;
		}
		emit({{"event", "conversation_end"}});
		break;
	case 0xDF: { // NpcConversationMessage
		// Either plain Unicode text, or (string-table lines, e.g. city greeters) a Unicode-sized
		// wrapper around: short 0, then a StringIdChatParameter: short pad flag, byte type,
		// int, ascii file, int 0, ascii key, then the TU/TT/TO parameters.
		int offset = pack->getOffset();
		uint32 length = pack->parseInt();
		uint16 first = length > 0 ? pack->parseShort() : 0xFFFF;
		std::string text;
		if (first == 0 && length >= 6) {
			pack->parseShort(); // pad flag
			pack->parseByte();  // parameter type (1 = string id)
			pack->parseInt();
			String file, key;
			pack->parseAscii(file);
			pack->parseInt();
			pack->parseAscii(key);
			if (!key.isEmpty())
				text = "@" + str(file) + ":" + str(key);
		} else {
			pack->setOffset(offset);
			UnicodeString message;
			pack->parseUnicode(message);
			text = str(message.toString());
		}
		emit({{"event", "npc_says"}, {"text", text}});
		break;
	}
	case 0xE0: { // StringList: conversation options
		uint8 count = pack->parseByte();
		std::vector<std::string> options;
		for (int i = 0; i < count; ++i) {
			UnicodeString option;
			pack->parseUnicode(option);
			options.push_back(str(option.toString()));
		}
		{
			std::lock_guard<std::recursive_mutex> lock(worldMutex);
			conversationOptions = options;
		}
		emit({{"event", "conversation_options"}, {"options", options}});
		break;
	}
	default:
		break;
	}
}


bool AgentControl::onStandalonePacket(uint32 opcode, Message* pack) {
	if (opcode == 0x8A64B1D5) { // ResourceListForSurveyMessage: what the active survey tool can find
		try {
			uint32 count = pack->parseInt();
			if (count > 1000) throw std::runtime_error("oversized resource list");
			JSONSerializationType resources = JSONSerializationType::array();
			for (uint32 i = 0; i < count; ++i) {
				String name, type;
				pack->parseAscii(name);
				pack->parseLong();
				pack->parseAscii(type);
				resources.push_back({{"name", str(name)}, {"type", str(type)}});
			}
			String toolType;
			pack->parseAscii(toolType);
			emit({{"event", "survey_resources"}, {"tool_type", str(toolType)}, {"resources", resources}});
		} catch (...) { emit({{"event", "packet_parse_error"}, {"packet", "ResourceListForSurveyMessage"}}); }
		return true;
	}
	if (opcode == 0x877F79AC) { // SurveyMessage: concentration grid around us
		try {
			uint32 count = pack->parseInt();
			if (count > 1000) throw std::runtime_error("oversized survey");
			JSONSerializationType points = JSONSerializationType::array();
			float bestX = 0, bestY = 0, best = -1;
			for (uint32 i = 0; i < count; ++i) {
				float x = pack->parseFloat();
				pack->parseFloat();
				float y = pack->parseFloat(), percent = pack->parseFloat();
				points.push_back({x, y, percent});
				if (percent > best) { best = percent; bestX = x; bestY = y; }
			}
			emit({{"event", "survey_results"}, {"points", points},
				  {"best", {{"x", bestX}, {"y", bestY}, {"percent", best}}}});
		} catch (...) { emit({{"event", "packet_parse_error"}, {"packet", "SurveyMessage"}}); }
		return true;
	}
	if (opcode != 0xD44B7259) return false; // SuiCreatePageMessage
	try {
		uint32 page = pack->parseInt(); String script; pack->parseAscii(script);
		uint32 count = pack->parseInt();
		if (count > 4096) throw std::runtime_error("oversized SUI command list");
		JSONSerializationType commands = JSONSerializationType::array();
		for (uint32 i = 0; i < count; ++i) {
			uint8 kind = pack->parseByte();
			uint32 wideCount = pack->parseInt();
			if (wideCount > 256) throw std::runtime_error("oversized SUI wide list");
			JSONSerializationType wide = JSONSerializationType::array(), narrow = JSONSerializationType::array();
			for (uint32 n = 0; n < wideCount; ++n) { UnicodeString v; pack->parseUnicode(v); wide.push_back(str(v.toString())); }
			uint32 narrowCount = pack->parseInt();
			if (narrowCount > 256) throw std::runtime_error("oversized SUI narrow list");
			for (uint32 n = 0; n < narrowCount; ++n) { String v; pack->parseAscii(v); narrow.push_back(str(v)); }
			commands.push_back({{"kind", kind}, {"wide", wide}, {"narrow", narrow}});
		}
		uint64 target = pack->parseLong(); float distance = pack->parseFloat(); pack->parseLong();
		JSONSerializationType data = {{"page_id", page}, {"script", str(script)},
			{"target", target}, {"close_distance", distance}, {"commands", commands}};
		{ std::lock_guard<std::recursive_mutex> lock(worldMutex); suiPages[page] = data; }
		emit({{"event", "sui_page"}, {"page", data}});
	} catch (...) { emit({{"event", "packet_parse_error"}, {"packet", "SuiCreatePageMessage"}}); }
	return true;
}

JSONSerializationType AgentControl::inventorySnapshot() {
	std::lock_guard<std::recursive_mutex> lock(worldMutex);
	JSONSerializationType items = JSONSerializationType::array();
	for (const auto& entry : world) {
		const WorldObject& object = entry.second;
		if (object.oid == self || object.type == "PLAY") continue;
		uint64 parent = object.parent;
		bool owned = false;
		for (int depth = 0; parent && depth < 32; ++depth) {
			if (parent == self) { owned = true; break; }
			auto it = world.find(parent);
			if (it == world.end() || it->second.parent == parent) break;
			parent = it->second.parent;
		}
		if (owned) items.push_back({{"oid", object.oid}, {"parent", object.parent},
			{"type", object.type}, {"name", object.name}, {"crc", object.crc}});
	}
	return {{"ok", true}, {"self", self}, {"items", items}};
}

JSONSerializationType AgentControl::status() {
	std::lock_guard<std::recursive_mutex> lock(worldMutex);
	JSONSerializationType me = world.count(self) ? creatureState(world[self]) : JSONSerializationType::object();
	return {{"ok", true}, {"self", self}, {"planet", planet}, {"x", selfX}, {"y", selfY}, {"z", selfZ},
			{"me", me},
			{"cell", selfParent}, {"known_objects", world.size()},
			// Our container: non-zero while mounted (the vehicle) or inside a cell
			{"container", world.count(self) ? world[self].parent : 0},
			{"connected", zone != nullptr && zone->isConnected()},
			{"conversation_options", conversationOptions}};
}

JSONSerializationType AgentControl::look(float radius, const std::string& typeFilter, int limit) {
	std::vector<std::pair<float, const WorldObject*>> found;
	std::lock_guard<std::recursive_mutex> lock(worldMutex);
	uint64 here = selfParent;
	if (here == 0 && world.count(self) && world[self].parent != 0) {
		auto container = world.find(world[self].parent);
		if (container == world.end() || container->second.type != "CREO") // a vehicle is CREO, a cell is not
			here = world[self].parent;
	}
	for (const auto& entry : world) {
		const WorldObject& object = entry.second;
		if (object.oid == self || object.type.empty() || object.type == "PLAY" || object.type == "SCLT")
			continue;
		if (!typeFilter.empty() && object.type != typeFilter)
			continue;
		// Outdoors only see outdoor objects; inside a cell only that cell's contents.
		if (object.parent != here)
			continue;
		float dx = object.x - selfX, dy = object.y - selfY;
		float distance = std::sqrt(dx * dx + dy * dy);
		if (distance <= radius)
			found.push_back({distance, &object});
	}
	std::sort(found.begin(), found.end(), [](const auto& a, const auto& b) { return a.first < b.first; });
	JSONSerializationType objects = JSONSerializationType::array();
	for (int i = 0; i < (int) found.size() && i < limit; ++i) {
		const WorldObject* object = found[i].second;
		JSONSerializationType entry = {{"oid", object->oid}, {"type", object->type}, {"name", object->name},
						   {"x", std::round(object->x * 10) / 10}, {"y", std::round(object->y * 10) / 10},
						   {"z", std::round(object->z * 10) / 10}, {"distance", std::round(found[i].first * 10) / 10}};
		if (object->type == "CREO" && object->posture >= 0) {
			entry["posture"] = postureName(object->posture);
			if (object->ham.size() >= 1 && object->maxHam.size() >= 1 && object->maxHam[0] > 0)
				entry["health_pct"] = (int) std::round(100.0 * object->ham[0] / object->maxHam[0]);
		}
		objects.push_back(entry);
	}
	return {{"ok", true}, {"x", selfX}, {"y", selfY}, {"count", objects.size()}, {"objects", objects}};
}

void AgentControl::sendTransform(float heading, float speed) {
	clientTime += 450;
	ClientObjectController* msg = new ClientObjectController(self, 0x21, 0x71);
	msg->insertInt(clientTime);
	msg->insertInt(++moveCount);
	msg->insertFloat(0.f);
	msg->insertFloat(std::sin(heading / 2.f));
	msg->insertFloat(0.f);
	msg->insertFloat(std::cos(heading / 2.f));
	msg->insertFloat(selfX);
	msg->insertFloat(selfZ);
	msg->insertFloat(selfY);
	msg->insertFloat(speed);
	zone->getZoneClient()->sendMessage(msg);
}

bool AgentControl::groundNear(float x, float y, float& z) {
	// The client has no terrain, so take the height of the nearest outdoor creature: NPCs
	// stand on the ground. Without this our height drifts and the server's line-of-sight
	// checks (conversations, combat) fail silently.
	// Blend every outdoor creature within 64 m, weighted by 1/(d+1)^2, so the height follows
	// slopes and plateaus (Mos Eisley sits at about 5, the hills north-east at about 180).
	std::lock_guard<std::recursive_mutex> lock(worldMutex);
	double weights = 0, sum = 0;
	for (const auto& entry : world) {
		const WorldObject& object = entry.second;
		if (object.oid == self || object.parent != 0 || object.type != "CREO" || object.posture < 0)
			continue;
		float dx = object.x - x, dy = object.y - y;
		float distance = std::sqrt(dx * dx + dy * dy);
		if (distance > 64.f)
			continue;
		double weight = 1.0 / ((distance + 1.0) * (distance + 1.0));
		weights += weight;
		sum += weight * object.z;
	}
	if (weights <= 0)
		return false;
	z = (float) (sum / weights);
	return true;
}

// Empty when we may move; otherwise why not. Checked before and during every walk.
std::string AgentControl::immobileReason() {
	std::lock_guard<std::recursive_mutex> lock(worldMutex);
	int posture = world.count(self) ? world[self].posture : -1;
	if (posture == 13 || posture == 14)
		return std::string("cannot move while ") + postureName(posture);
	return "";
}

JSONSerializationType AgentControl::moveTo(float x, float y, float speed, float timeoutSeconds, float z) {
	if (selfParent != 0)
		return {{"ok", false}, {"error", "moving inside buildings needs the /agentpath helper"}};
	std::string blocked = immobileReason();
	if (!blocked.empty())
		return {{"ok", false}, {"error", blocked}};
	speed = std::max(0.5f, std::min(speed, 5.0f));
	Time started;
	uint32 correctionsAtStart = serverCorrections;
	float heading = 0;
	while (true) {
		blocked = immobileReason();
		if (!blocked.empty())
			return {{"ok", false}, {"error", blocked}, {"x", selfX}, {"y", selfY}};
		float dx, dy, distance;
		{
			std::lock_guard<std::recursive_mutex> lock(worldMutex);
			dx = x - selfX; dy = y - selfY;
			distance = std::sqrt(dx * dx + dy * dy);
			if (distance < 0.6f)
				break;
			if (started.miliDifference() > timeoutSeconds * 1000)
				return {{"ok", false}, {"error", "timeout"}, {"x", selfX}, {"y", selfY}, {"remaining", distance}};
			if (serverCorrections - correctionsAtStart >= 3)
				return {{"ok", false}, {"error", "the server keeps putting us back (blocked, rooted or dead)"},
						{"x", selfX}, {"y", selfY}, {"remaining", distance}};
			heading = std::atan2(dx, dy);
			float step = std::min(distance, speed * 0.45f);
			selfX += dx / distance * step;
			selfY += dy / distance * step;
			float ground;
			if (!std::isnan(z))
				selfZ = z;
			else if (groundNear(selfX, selfY, ground))
				selfZ = ground;
		}
		sendTransform(heading, speed);
		Thread::sleep(450);
	}
	sendTransform(heading, 0.f);
	return {{"ok", true}, {"arrived", true}, {"x", selfX}, {"y", selfY}, {"z", selfZ},
			{"seconds", started.miliDifference() / 1000.0}};
}

JSONSerializationType AgentControl::askHelper(const std::string& args, float timeoutSeconds) {
	uint32 before;
	std::string id;
	{
		std::lock_guard<std::recursive_mutex> lock(worldMutex);
		before = helperReplies;
		id = std::to_string(++helperSequence);
	}
	sendCommand("agentpath", 0, UnicodeString(("id:" + id + " " + args).c_str()));
	int polls = (int) (std::max(0.5f, std::min(timeoutSeconds, 4.f)) * 20);
	for (int i = 0; i < polls; ++i) {
		Thread::sleep(50);
		std::lock_guard<std::recursive_mutex> lock(worldMutex);
		if (helperReplies == before)
			continue;
		before = helperReplies;
		JSONSerializationType reply;
		try {
			reply = JSONSerializationType::parse(helperReply);
		} catch (...) {
			return {{"ok", false}, {"error", "unreadable helper reply"}};
		}
		// The server echoes our request id; a late answer to any earlier request (even one with the same
		// destination) is ignored.
		if (reply.value("id", std::string()) == id)
			return reply;
	}
	if (timeoutSeconds >= 4.f) // a full wait, not one cut short by a move's deadline
		helperMissing = true;
	return {{"ok", false}, {"error", "no answer from the server's /agentpath helper (not installed, or this account is not in Core3.AgentAccounts)"}};
}

void AgentControl::sendTransformWithParent(uint64 cell, float heading, float speed) {
	clientTime += 450;
	ClientObjectController* msg = new ClientObjectController(self, 0x21, 0xF1);
	msg->insertInt(clientTime);
	msg->insertInt(++moveCount);
	msg->insertLong(cell);
	msg->insertFloat(0.f);
	msg->insertFloat(std::sin(heading / 2.f));
	msg->insertFloat(0.f);
	msg->insertFloat(std::cos(heading / 2.f));
	msg->insertFloat(selfX);
	msg->insertFloat(selfZ);
	msg->insertFloat(selfY);
	msg->insertFloat(speed);
	zone->getZoneClient()->sendMessage(msg);
}

// Follow /agentpath points [x, y, z, cell]. Inside a cell the coordinates are cell-local and
// sent as DataTransformWithParent; outside they are world coordinates. Crossing between cells
// (through a door) is a single step to the next point.
JSONSerializationType AgentControl::walkPath(const JSONSerializationType& points, float speed, float timeoutSeconds) {
	speed = std::max(0.5f, std::min(speed, 5.0f));
	Time started;
	uint32 correctionsAtStart = serverCorrections;
	float heading = 0;
	for (size_t i = 0; i < points.size(); ++i) {
		std::string blocked = immobileReason();
		if (!blocked.empty())
			return {{"ok", false}, {"error", blocked}, {"cell", selfParent}, {"x", selfX}, {"y", selfY}};
		if (started.miliDifference() > timeoutSeconds * 1000)
			return {{"ok", false}, {"error", "timeout"}, {"cell", selfParent}, {"x", selfX}, {"y", selfY}};
		const auto& point = points[i];
		float px = point[0].get<float>(), py = point[1].get<float>(), pz = point[2].get<float>();
		uint64 cell = point[3].get<uint64>();
		bool newFrame;
		{
			std::lock_guard<std::recursive_mutex> lock(worldMutex);
			newFrame = i == 0 || cell != selfParent;
			if (newFrame) {
				// The first point is where the server thinks we are; a cell change is a doorway.
				selfX = px; selfY = py; selfZ = pz; selfParent = cell;
			}
		}
		if (newFrame) {
			if (cell != 0) sendTransformWithParent(cell, heading, speed); else sendTransform(heading, speed);
			Thread::sleep(450);
			continue;
		}
		while (true) {
			blocked = immobileReason();
			if (!blocked.empty())
				return {{"ok", false}, {"error", blocked}, {"cell", selfParent}, {"x", selfX}, {"y", selfY}};
			float dx, dy, distance;
			{
				std::lock_guard<std::recursive_mutex> lock(worldMutex);
				dx = px - selfX; dy = py - selfY;
				distance = std::sqrt(dx * dx + dy * dy);
				if (distance < 0.3f)
					break;
				if (started.miliDifference() > timeoutSeconds * 1000)
					return {{"ok", false}, {"error", "timeout"}, {"cell", selfParent}, {"x", selfX}, {"y", selfY}};
				if (serverCorrections - correctionsAtStart >= 3)
					return {{"ok", false}, {"error", "the server keeps putting us back (blocked, rooted or dead)"},
							{"cell", selfParent}, {"x", selfX}, {"y", selfY}};
				heading = std::atan2(dx, dy);
				float step = std::min(distance, speed * 0.45f);
				selfZ += (pz - selfZ) * step / distance;
				selfX += dx / distance * step;
				selfY += dy / distance * step;
			}
			if (cell != 0) sendTransformWithParent(cell, heading, speed); else sendTransform(heading, speed);
			Thread::sleep(450);
		}
	}
	if (selfParent != 0) sendTransformWithParent(selfParent, heading, 0.f); else sendTransform(heading, 0.f);
	std::lock_guard<std::recursive_mutex> lock(worldMutex);
	return {{"ok", true}, {"arrived", true}, {"cell", selfParent}, {"x", selfX}, {"y", selfY}, {"z", selfZ},
			{"points", points.size()}, {"seconds", started.miliDifference() / 1000.0}};
}

// Reflex: stay next to the target and keep attacking (the real client auto-attacks) until one
// side is incapacitated or dead, the target disappears, or the timeout passes.
JSONSerializationType AgentControl::fight(uint64 target, float timeoutSeconds) {
	Time started;
	int attacks = 0;
	std::string result = "timeout";
	while (started.miliDifference() < timeoutSeconds * 1000) {
		float tx, ty, distance;
		int targetPosture, myPosture;
		{
			std::lock_guard<std::recursive_mutex> lock(worldMutex);
			auto it = world.find(target);
			if (it == world.end()) {
				result = "target gone";
				break;
			}
			tx = it->second.x; ty = it->second.y;
			targetPosture = it->second.posture;
			myPosture = world.count(self) ? world[self].posture : -1;
			distance = std::sqrt((tx - selfX) * (tx - selfX) + (ty - selfY) * (ty - selfY));
		}
		if (targetPosture == 13 || targetPosture == 14) {
			result = std::string("target ") + postureName(targetPosture);
			break;
		}
		if (myPosture == 13 || myPosture == 14) {
			result = std::string("we are ") + postureName(myPosture);
			break;
		}
		if (distance > 3.5f) {
			// Stop 1.5 m short of the target.
			float approach = (distance - 1.5f) / distance;
			moveTo(selfX + (tx - selfX) * approach, selfY + (ty - selfY) * approach, 5.f, 15.f, std::nanf(""));
		}
		sendCommand("attack", target, UnicodeString(""));
		++attacks;
		Thread::sleep(2000);
	}
	std::lock_guard<std::recursive_mutex> lock(worldMutex);
	JSONSerializationType reply = {{"ok", true}, {"result", result}, {"attacks", attacks},
		{"seconds", started.miliDifference() / 1000.0}};
	if (world.count(self))
		reply["me"] = creatureState(world[self]);
	if (world.count(target))
		reply["target"] = creatureState(world[target]);
	return reply;
}

void AgentControl::sendTeleportAck(uint32 counter) {
	ClientObjectController* msg = new ClientObjectController(self, 0x23, 0x13F);
	msg->insertInt(counter);
	zone->getZoneClient()->sendMessage(msg);
}

void AgentControl::sendCommand(const String& name, uint64 target, const UnicodeString& args) {
	ObjectControllerMessage* msg = new ObjectControllerMessage(self, 0x23, 0x116);
	{
		std::lock_guard<std::recursive_mutex> lock(worldMutex);
		commandNames[++actionCount] = str(name);
		if (commandNames.size() > 200)
			commandNames.erase(commandNames.begin());
	}
	msg->insertInt(actionCount);
	msg->insertInt(name.toLowerCase().hashCode());
	msg->insertLong(target);
	msg->insertUnicode(args);
	zone->getZoneClient()->sendMessage(msg);
}

JSONSerializationType AgentControl::handle(const JSONSerializationType& request) {
	std::string cmd = request.value("cmd", "");

	if (cmd == "inventory") return inventorySnapshot();
	if (cmd == "fight") {
		uint64 target = request.value("target", (uint64) 0);
		if (!target)
			return {{"ok", false}, {"error", "target required"}};
		return fight(target, std::min(request.value("timeout", 60.0f), 170.0f));
	}
	if (cmd == "inspect") {
		uint64 target = request.value("target", (uint64) 0);
		std::lock_guard<std::recursive_mutex> lock(worldMutex);
		auto it = world.find(target);
		if (it == world.end())
			return {{"ok", false}, {"error", "unknown object"}};
		const WorldObject& object = it->second;
		JSONSerializationType reply = {{"ok", true}, {"oid", object.oid}, {"type", object.type}, {"name", object.name},
			{"x", object.x}, {"y", object.y}, {"z", object.z}, {"parent", object.parent}, {"crc", object.crc}};
		if (object.type == "CREO")
			reply["creature"] = creatureState(object);
		return reply;
	}
	if (cmd == "sui_pages") {
		std::lock_guard<std::recursive_mutex> lock(worldMutex);
		JSONSerializationType pages = JSONSerializationType::array();
		for (const auto& entry : suiPages) pages.push_back(entry.second);
		return {{"ok", true}, {"pages", pages}};
	}
	if (cmd == "radial_menu") {
		uint64 target = request.value("target", (uint64)0);
		if (!target) return {{"ok", false}, {"error", "target required"}};
		ObjectControllerMessage* msg = new ObjectControllerMessage(self, 0x23, 0x146);
		msg->insertLong(target); msg->insertLong(self); msg->insertInt(1);
		msg->insertByte(1); msg->insertByte(0); msg->insertByte(20); msg->insertByte(3);
		msg->insertUnicode(UnicodeString("")); msg->insertByte(++radialCounter);
		zone->getZoneClient()->sendMessage(msg);
		return {{"ok", true}, {"requested", target}};
	}
	if (cmd == "select_radial") {
		uint64 target = request.value("target", (uint64)0);
		int radial = request.value("radial_id", -1); bool offered = false;
		{ std::lock_guard<std::recursive_mutex> lock(worldMutex);
		  auto it = radialMenus.find(target);
		  if (it != radialMenus.end()) for (const auto& item : it->second)
			  if (item.value("radial_id", -1) == radial) offered = true; }
		if (!offered) return {{"ok", false}, {"error", "request menu first and select a returned radial_id"}};
		BaseMessage* msg = new BaseMessage(); msg->insertShort(3); msg->insertInt(0x7CA18726);
		msg->insertLong(target); msg->insertByte((uint8)radial);
		zone->getZoneClient()->sendMessage(msg);
		return {{"ok", true}, {"selected", radial}, {"target", target}};
	}
	if (cmd == "missions") { // every mission object we know: the terminal list (mission bag) and accepted ones
		std::lock_guard<std::recursive_mutex> lock(worldMutex);
		JSONSerializationType list = JSONSerializationType::array();
		for (const auto& entry : missions) {
			JSONSerializationType mission = entry.second;
			auto it = world.find(entry.first);
			uint64 parent = it != world.end() ? it->second.parent : 0;
			mission["container"] = parent;
			mission["container_name"] = parent && world.count(parent) ? world[parent].name : "";
			list.push_back(mission);
		}
		return {{"ok", true}, {"missions", list}};
	}
	if (cmd == "mission_accept") {
		uint64 mission = request.value("target", (uint64) 0), terminal = request.value("terminal", (uint64) 0);
		if (!mission || !terminal)
			return {{"ok", false}, {"error", "target (mission oid) and terminal required"}};
		ObjectControllerMessage* msg = new ObjectControllerMessage(self, 0x23, 0xF9);
		msg->insertLong(mission);
		msg->insertLong(terminal);
		msg->insertByte(++radialCounter);
		zone->getZoneClient()->sendMessage(msg);
		return {{"ok", true}, {"requested", mission}};
	}
	if (cmd == "mission_list") {
		uint64 target = request.value("target", (uint64)0);
		if (!target) return {{"ok", false}, {"error", "mission terminal target required"}};
		ObjectControllerMessage* msg = new ObjectControllerMessage(self, 0x23, 0xF5);
		msg->insertByte(0); msg->insertByte(++radialCounter); msg->insertLong(target);
		zone->getZoneClient()->sendMessage(msg);
		return {{"ok", true}, {"requested", target}, {"note", "mission deltas still need structured decoding"}};
	}
	if (cmd == "sui_respond") {
		uint32 page = request.value("page_id", (uint32)0);
		uint32 event = request.value("event", (uint32)0);
		JSONSerializationType args = request.value("args", JSONSerializationType::array());
		{ std::lock_guard<std::recursive_mutex> lock(worldMutex);
		  if (!suiPages.count(page)) return {{"ok", false}, {"error", "unknown SUI page"}}; }
		if (!args.is_array() || args.size() > 64) return {{"ok", false}, {"error", "invalid SUI arguments"}};
		for (const auto& arg : args) if (!arg.is_string()) return {{"ok", false}, {"error", "SUI arguments must be strings"}};
		BaseMessage* msg = new BaseMessage(); msg->insertShort(5); msg->insertInt(0x092D3564);
		msg->insertInt(page); msg->insertInt(event); msg->insertInt(args.size()); msg->insertInt(0);
		for (const auto& arg : args) msg->insertUnicode(UnicodeString(arg.get<std::string>().c_str()));
		// Forget the page before sending: the server may answer with a new page reusing its ID.
		{ std::lock_guard<std::recursive_mutex> lock(worldMutex); suiPages.erase(page); }
		zone->getZoneClient()->sendMessage(msg);
		return {{"ok", true}, {"responded", page}};
	}
	if (cmd == "ping")
		return {{"ok", true}};
	if (cmd == "status")
		return status();
	if (cmd == "look")
		return look(request.value("radius", 64.0f), request.value("type", ""), request.value("limit", 40));
	if (cmd == "move" || cmd == "path") {
		float x = request.value("x", selfX), y = request.value("y", selfY);
		float speed = request.value("speed", 5.0f);
		// One deadline for the whole move: planning, every leg and every re-plan. Keep it below
		// the MCP wrapper's 100 s wait so the caller never times out while we are still walking.
		float timeout = std::min(request.value("timeout", 90.0f), 95.0f);
		Time started;
		auto remainingTime = [&]() { return timeout - started.miliDifference() / 1000.f; };
		uint64 cell = request.value("cell", (uint64) 0);
		bool indoors = selfParent != 0 || cell != 0;
		bool usePath = cmd == "path" || indoors || (request.value("path", true) && !helperMissing);
		if (cmd == "move") {
			std::string blocked = immobileReason();
			if (!blocked.empty())
				return {{"ok", false}, {"error", blocked}};
		}
		if (!usePath)
			return moveTo(x, y, speed, timeout, request.value("z", std::nanf("")));
		std::string args = "path " + std::to_string(x) + " " + std::to_string(y);
		if (cell != 0)
			args += " " + std::to_string(request.value("z", 0.0f)) + " " + std::to_string(cell);
		JSONSerializationType plan = askHelper(args, remainingTime());
		if (cmd == "path")
			return plan;
		if (plan.value("ok", false)) {
			// The pathfinder can return part of the way (to a ledge, out of a building towards
			// a far target, or a capped long route); re-plan from there while each leg gets closer.
			JSONSerializationType result;
			float lastRemaining = 1e9f;
			int stalled = 0;
			for (int leg = 1; leg <= 25; ++leg) {
				if (remainingTime() <= 0)
					return {{"ok", false}, {"error", "timeout"}, {"legs", leg - 1}, {"cell", selfParent}, {"x", selfX}, {"y", selfY}};
				result = walkPath(plan["points"], speed, remainingTime());
				if (!result.value("ok", false))
					return result;
				float remaining;
				{
					std::lock_guard<std::recursive_mutex> lock(worldMutex);
					remaining = selfParent == cell ? std::sqrt((x - selfX) * (x - selfX) + (y - selfY) * (y - selfY)) : 1e9f;
				}
				result["legs"] = leg;
				if (remaining < 1.5f)
					return result;
				stalled = remaining > lastRemaining - 1.f ? stalled + 1 : 0;
				if (stalled >= 2)
					break;
				lastRemaining = std::min(lastRemaining, remaining);
				if (remainingTime() <= 0)
					break;
				plan = askHelper(args, remainingTime());
				if (!plan.value("ok", false))
					break;
			}
			result["ok"] = false;
			result["error"] = remainingTime() <= 0 ? "timeout" : "could not reach the destination; stopped at the end of the last path";
			return result;
		}
		if (indoors)
			return plan;
		JSONSerializationType result = moveTo(x, y, speed, std::max(0.f, remainingTime()), request.value("z", std::nanf("")));
		result["note"] = "walked a straight line: " + plan.value("error", std::string("no path"));
		return result;
	}
	if (cmd == "height") {
		return askHelper("height " + std::to_string(request.value("x", selfX)) + " " +
						 std::to_string(request.value("y", selfY)));
	}
	if (cmd == "say") {
		String text(request.value("text", "").c_str());
		sendCommand("spatialchatinternal", 0, UnicodeString("0 0 0 0 1 " + text));
		return {{"ok", true}};
	}
	if (cmd == "command") {
		String name(request.value("name", "").c_str());
		if (name.isEmpty())
			return {{"ok", false}, {"error", "name required"}};
		uint64 target = request.value("target", (uint64) 0);
		sendCommand(name, target, UnicodeString(request.value("args", "").c_str()));
		return {{"ok", true}, {"sent", str(name)}};
	}
	if (cmd == "talk") {
		sendCommand("npcconversationstart", request.value("target", (uint64) 0), UnicodeString(""));
		return {{"ok", true}};
	}
	if (cmd == "choose") {
		int index = request.value("index", 0);
		{
			std::lock_guard<std::recursive_mutex> lock(worldMutex);
			if (!conversationActive || index < 0 || index >= (int) conversationOptions.size())
				return {{"ok", false}, {"error", "no active conversation option at that index"}};
		}
		sendCommand("npcconversationselect", 0, UnicodeString(String::valueOf(index)));
		return {{"ok", true}};
	}
	return {{"ok", false}, {"error", "unknown cmd: " + cmd}};
}

void AgentControl::run(Zone* activeZone) {
	zone = activeZone;
	// Zoning in leaves us flagged as "teleporting" until acknowledged.
	sendTeleportAck(moveCount);
	emit({{"event", "ready"}, {"self", self}, {"planet", planet}});
	std::string line;
	while (std::getline(std::cin, line)) {
		if (line.empty())
			continue;
		JSONSerializationType request, reply;
		try {
			request = JSONSerializationType::parse(line);
		} catch (...) {
			emit({{"reply", "error"}, {"ok", false}, {"error", "invalid JSON"}});
			continue;
		}
		std::string cmd = request.value("cmd", "");
		if (cmd == "quit" || cmd == "logout") {
			emit({{"reply", cmd}, {"ok", true}, {"id", request.value("id", JSONSerializationType())}});
			break;
		}
		try {
			reply = handle(request);
		} catch (const std::exception& e) {
			reply = {{"ok", false}, {"error", e.what()}};
		} catch (...) {
			reply = {{"ok", false}, {"error", "exception"}};
		}
		reply["reply"] = cmd;
		if (request.contains("id"))
			reply["id"] = request["id"];
		emit(reply);
	}
	emit({{"event", "logging_out"}});
}
