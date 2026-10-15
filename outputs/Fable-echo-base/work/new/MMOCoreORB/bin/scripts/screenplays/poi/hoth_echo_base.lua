-- Hoth: Echo Base, first look (Fable E0, 14 Oct 2026; outputs/Fable-echo-base/README.md).
-- The NGE heroic building (object/building/heroic/shared_echo_base.iff, from the MTG archives) placed where MTG's
-- hoth.trn cut the terrain for it: its hangar, main-door and tower openings fit MTG's three cut-outs within 2.3 m RMS
-- at origin -5112.8, 5096.6, heading 0, height 37.6 m (the three doors agree within 2.1 m). One building, no NPCs: the
-- go / no-go look for E1 (outputs/Fable-hoth-guide/echo-base-plan.md). Owner: /teleport -5051 5440 hoth (main door),
-- /teleport -5307 5750 hoth (hangar), /teleport -5036 5120 hoth (tower).
HothEchoBaseScreenPlay = ScreenPlay:new {
	numberOfActs = 1,
	screenplayName = "HothEchoBaseScreenPlay",
}

registerScreenPlay("HothEchoBaseScreenPlay", true)

function HothEchoBaseScreenPlay:start()
	if (isZoneEnabled("hoth")) then
		self:spawnSceneObjects()
	end
end

function HothEchoBaseScreenPlay:spawnSceneObjects()
	spawnSceneObject("hoth", "object/building/heroic/echo_base.iff", -5112.8, 37.6, 5096.6, 0, 0)
end
