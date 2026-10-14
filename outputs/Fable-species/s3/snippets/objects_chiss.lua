
-- Sandbox: Chiss shared client templates (Fable species S3, 14 Oct 2026). Minimal declarations as the Halyn/Phoenix
-- species package made them; Core3 reads object/creature/player/shared_chiss_*.iff from the tre (MTG patch 023) first.
object_creature_player_shared_chiss_female = SharedCreatureObjectTemplate:new {
	clientTemplateFileName = "object/creature/player/shared_chiss_female.iff"
}
ObjectTemplates:addClientTemplate(object_creature_player_shared_chiss_female, "object/creature/player/shared_chiss_female.iff")

object_creature_player_shared_chiss_male = SharedCreatureObjectTemplate:new {
	clientTemplateFileName = "object/creature/player/shared_chiss_male.iff"
}
ObjectTemplates:addClientTemplate(object_creature_player_shared_chiss_male, "object/creature/player/shared_chiss_male.iff")
