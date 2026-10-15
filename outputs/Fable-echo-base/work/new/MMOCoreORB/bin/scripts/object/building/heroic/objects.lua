-- Sandbox: Hoth Echo Base (Fable E0, 14 Oct 2026; outputs/Fable-echo-base/README.md). The shared template is the NGE
-- heroic building MTG ships (mtg_patch_019.tre); the server reads its portal layout (appearance/echo_base_pob.pob,
-- mtg_patch_016.tre, 41 cells) and the rest from the client file through clientTemplateFileName, as the other
-- building templates do.
object_building_heroic_shared_echo_base = SharedBuildingObjectTemplate:new {
	clientTemplateFileName = "object/building/heroic/shared_echo_base.iff"
}

ObjectTemplates:addClientTemplate(object_building_heroic_shared_echo_base, "object/building/heroic/shared_echo_base.iff")
