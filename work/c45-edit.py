from pathlib import Path
root=Path('/opt/swg/Core3-gpt/MMOCoreORB/src/server/zone/objects/mission')
p=root/'CraftingMissionObjectiveImplementation.cpp'
s=p.read_text()
anchor='#include "server/zone/objects/mission/MissionObject.h"\n'
helper='''
// Mission recipes can be shared when more than two crafting missions are active.
// Keep the pooled grant until the last mission using it ends, including missions
// whose pickup has not happened yet. The caller's mission is still in the datapad.
static void removeUnusedMissionSchematic(MissionObject* mission, CreatureObject* player) {
	if (mission == nullptr || player == nullptr) {
		return;
	}

	Locker playerLock(player);
	SceneObject* datapad = player->getSlottedObject("datapad");

	if (datapad == nullptr) {
		return;
	}

	for (int i = 0; i < datapad->getContainerObjectsSize(); ++i) {
		ManagedReference<SceneObject*> object = datapad->getContainerObject(i);

		if (object == nullptr || !object->isMissionObject()) {
			continue;
		}

		MissionObject* otherMission = cast<MissionObject*>(object.get());

		if (otherMission != mission && otherMission->getTypeCRC() == MissionTypes::CRAFTING &&
				otherMission->getTemplateString1() == mission->getTemplateString1()) {
			return;
		}
	}

	ManagedReference<PlayerObject*> ghost = player->getPlayerObject();
	DraftSchematic* schematic = SchematicMap::instance()->get(mission->getTemplateString1().hashCode());

	if (ghost != nullptr && schematic != nullptr) {
		ghost->removeRewardedSchematic(schematic, true);
	}
}
'''
assert s.count(anchor)==1
s=s.replace(anchor,anchor+helper)
start=s.index('void CraftingMissionObjectiveImplementation::abort() {')
s=s[:start]+'''void CraftingMissionObjectiveImplementation::abort() {
	ManagedReference<MissionObject*> mission = this->mission.get();
	ManagedReference<CreatureObject*> player = getPlayerOwner();

	removeUnusedMissionSchematic(mission, player);

	//Run normal abort for deliver missions.
	DeliverMissionObjectiveImplementation::abort();
}

void CraftingMissionObjectiveImplementation::complete() {
	ManagedReference<MissionObject*> mission = this->mission.get();
	ManagedReference<CreatureObject*> player = getPlayerOwner();

	removeUnusedMissionSchematic(mission, player);

	DeliverMissionObjectiveImplementation::complete();
}
'''
p.write_text(s)
p=root/'CraftingMissionObjective.idl'
s=p.read_text()
anchor='\tpublic abstract native void abort();\n'
assert s.count(anchor)==1
p.write_text(s.replace(anchor,anchor+'\tpublic abstract native void complete();\n'))
print('Changed only crafting objective cpp + idl')
