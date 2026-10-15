"""Build a complete resource handoff from existing owner extracts. No game writes."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "outputs/Content-catalogue/owner-SWG-SW5E"
OUT = ROOT / "outputs/Documentation-support"


def load(name):
    return json.loads((SRC / name).read_text(encoding="utf-8"))


def clean(text):
    return str(text).replace("Je\ufffddaii", "Je'daii").replace("|", "/").replace("\n", " ")


def route(name, kind="", evidence=""):
    """Conservative editorial suggestions, never asserted game mappings."""
    n = name.lower()
    if kind == "Chemical" and ("ryll resin" in n or "lesai crystal" in n or "polstine dust" in n):
        return "Reagent", "Distinct processed ingredient; do not equate name with a raw mineral class"
    if "affide crystal" in n:
        return "Reagent", "Distinct poison ingredient, not a Jedi crystal; fictional effects need design"
    if evidence == "U":
        return "Hold", "Inactive in book; owner/lore decision before design"
    if evidence == "I" or "imported" in n:
        return "Trade", "Supply contract/vendor/crafted shipment; no local natural spawn"
    if any(t in n for t in ["holocron", "archive", "specimen", "ritual", "certificate", "habitat", "seed partners"]):
        return "Story", "Archaeology/research/quest item; provenance and finite acquisition"
    if kind == "Tech" or any(t in n for t in ["scrap", "salvage", "debris", "rubble", "old equipment", "abandoned", "damaged", "finite hull"]):
        return "Salvage", "Loot/recovery item -> crafted component; not surveyable ore"
    if any(t in n for t in ["component", "parts", "gear", "equipment", "machinery", "electronics", "electronic", "packaging", "firmware", "device", "module", "control nodes"]):
        return "Component", "Crafted input; Artisan/Droid Engineer or matching specialist"
    if any(t in n for t in ["water", "moisture"]) or re.search(r"\bice\b", n):
        return "Raw/processed", "Water family if suitable; filtered/sterile product needs recipe"
    if any(t in n for t in ["kyber", "crystal", "meditation stone"]):
        return "Crystal/reagent", "Generic mineral or distinct loot crystal; Jedi crystals need item semantics"
    if kind == "Mineral" or re.search(r"\bore\b", n) or any(t in n for t in ["mineral", "metal", "alloy", "durasteel", "aggregate", "rock", "stone", "doonium"]):
        return "Raw/processed", "Existing metal/ore family first; refined alloy needs recipe"
    if any(t in n for t in ["gland", "venom sac", "carapace", "bile", "stomach acid", "tree frog", "coral", "nutrient sap"]):
        return "Biological item", "Controlled creature/quest yield; BE/Toxicologist research, new acquisition hook"
    if any(t in n for t in ["precursor", "extract", "salve", "paste", "medium", "compound", "base", "reagent", "serum", "diluted", "kavam", "ambori", "residue", "ichor", "plague agent"]):
        return "Reagent", "Crafted intermediate; Medic/Doctor/Combat Medic/Smuggler or optional specialist"
    if any(t in n for t in ["hide", "tissue", "remains"]):
        return "Organic", "Existing harvest family where appropriate; distinct tissues need item hook"
    if any(t in n for t in ["fiber", "textile", "garment"]):
        return "Organic/processed", "Tailor input; biological fiber is not automatically fiberplast"
    if any(t in n for t in ["timber", "wood", "produce", "grain", "crop", "fruit", "food", "provision"]):
        return "Organic/food", "Existing flora/food families first; farming is a separate optional system"
    if kind in {"Botanical", "Organic"} or any(t in n for t in ["biomass", "plant", "resin", "peat", "soil", "botanical", "lichen", "spore", "root", "bark", "grass", "pollen"]):
        return "Botanical", "Proposed flora resource/cultivation input; Botanist pipeline not yet complete"
    if any(t in n for t in ["gas", "tibanna", "plasma", "sulfur", "chemical", "solvent", "coolant", "perfume", "polymer", "clay", "ceramic"]):
        return "Raw/processed", "Choose existing gas/chemical/ore parent; processed products need recipe"
    return "Review", "Assign raw resource, intermediate or story item before implementation"


def main():
    core, pharm, armory = (load(x) for x in ["swg-optional-content.json", "pharmacopoeia.json", "armory.json"])
    records = []
    for planet in core["planets"]:
        for i, r in enumerate(planet["resources"], 1):
            category, proposal = route(r["resource"], evidence=r["evidence"])
            records.append({"id": f'{planet["id"]}-mat-{i:02}', "book": "core", "source_record": planet["id"],
                            "page": planet["page"], "planet": planet["name"], "name": r["resource"],
                            "book_evidence": r["evidence"], "intended_use": r["crafting_role"],
                            "proposed_route": category, "adaptation_proposal": proposal,
                            "implementation_status": "proposal only; not enabled", "lore_review": "pending"})
    for r in pharm["resources"]:
        category, proposal = route(r["name"], r["type"])
        records.append({"id": r["id"], "book": "pharmacopoeia", "source_record": r["id"], "table": r["table"],
                        "name": r["name"], "book_type": r["type"], "book_location": r["source"],
                        "intended_use": r["primary_use"], "prior_token_matches": r["real_swg_class"] or [],
                        "proposed_route": category, "adaptation_proposal": proposal,
                        "implementation_status": "proposal only; not enabled", "lore_review": "pending"})
    assert len(core["planets"]) == 37 and len(records) == 265
    assert len({r["id"] for r in records}) == len(records)
    supplementary = {
        "creature_husbandry": [{"id": r["id"], "name": r["name"], "page": r["page"],
                                 "book_reference": r["husbandry"], "status": "acquisition design pending"} for r in core["creatures"]],
        "schematic_inputs": [{"id": r["id"], "name": r["name"], "page": r["page"],
                               "book_inputs": r["inputs"], "status": "portions are not SWG unit costs"} for r in core["schematics"]],
    }
    manifest = {n: {"sha256": hashlib.sha256((SRC/n).read_bytes()).hexdigest(), "source": load(n)["source"]}
                for n in ["swg-optional-content.json", "pharmacopoeia.json", "armory.json"]}
    result = {"schema_version": 1, "date": "2026-10-14", "scope": "All explicit resource rows in existing owner extracts, plus husbandry and recipe-input references",
              "sources": manifest, "counts": {"planet_rows": 185, "pharmacopoeia_rows": 80,
              "unique_exact_names": len({r["name"] for r in records}), "husbandry_references": len(supplementary["creature_husbandry"]),
              "schematic_input_groups": len(supplementary["schematic_inputs"])},
              "rules": ["Proposal only; no server/client edits", "No SW5E mechanics imported", "Prior matches are lexical leads, not identity or effects proof",
                        "Book quality ranges are not spawn gates or item stats", "Legends/era checks remain pending per asset"],
              "resources": records, "supplementary": supplementary}
    (OUT/"owner-ttrpg-resource-handoff.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    lines = ["# Owner TTRPG resources: clean handoff for Claude", "", "14 Oct 2026 — C29. Optional content reference; nothing enabled.", "",
             f'**185 planet entries + 80 pharmacopoeia entries = 265 source rows ({result["counts"]["unique_exact_names"]} exact distinct names).** Repeated names stay separate because location, evidence or use differs. Also included: 28 husbandry references and 16 schematic input groups. These are all explicit resource fields in the three existing structured book extracts; this is not a new word-by-word PDF audit.', "",
             "The armory contributes 247 finished items/modifications/relics, not a separate raw-resource table. Its resource/parts paragraph is a restoration concept, not adopted unit costs. The 85 pharmacopoeia substances are finished consumables, separate from its 80 resource rows; see the existing catalogues for both.", "",
             "## Read this first", "",
             "Names, locations and uses below come from the owner's books. **Route is our proposal**, not approved implementation or verified lore. H = proposed content; L = book's Legends claim; C-opt = optional Canon; AH = book's approved campaign departure; I = imported stock; U = inactive/unsupported entry. None of these labels replaces a fresh continuity/era check.", "",
             "Use real pre-CU mechanics. Do not transfer tabletop portions, DCs, alignment/session rules, instant Force-null effects, invulnerability or book quality ranges. Choose a SWG item category, acquisition route, consumer recipe and balance target first. Keep all optional and off by default until tested and approved.", "",
             "**Important match correction:** the earlier pharmacopoeia extractor uses word matching. Ryll resin is not automatically Ryll gemstone; Dioxis precursor is not automatically Dioxis gas; Iridonian iron is not an existing planet-specific resource. Existing Cortosis ore/Phrik aluminum are useful leads, but their names do not grant lightsaber immunity or unbreakable armor. Verify class and semantics separately.", "",
             "**Lowest-cost sequence:** reuse existing raw-material families → create a few intermediate reagents/salvage items → add consumer recipes → only then add new resource-tree leaves or farming acquisition. Existing species/planet art and biome availability remain separate dependencies.", "",
             "## Planet material list", ""]
    for planet in core["planets"]:
        lines += [f'### {planet["name"]} — core p. {planet["page"]}', "", "| Material | Book label | Intended use | Proposed SWG route |", "|---|---|---|---|"]
        for r in [r for r in records if r.get("source_record")==planet["id"]]:
            lines.append(f'| {clean(r["name"])} | {r["book_evidence"]} | {clean(r["intended_use"])} | {clean(r["proposed_route"])} |')
        lines.append("")
    lines += ["## Pharmacopoeia material list", "", "Original table and row IDs are retained in the JSON. Locations and uses are book claims; mechanical effects and lore are not validated by listing them.", ""]
    for table in dict.fromkeys(r["table"] for r in pharm["resources"]):
        lines += ["### "+table, "", "| Material | Book source/location | Intended use | Proposed SWG route |", "|---|---|---|---|"]
        for r in [r for r in records if r.get("table")==table]:
            lines.append(f'| {clean(r["name"])} | {clean(r["book_location"])} | {clean(r["intended_use"])} | {clean(r["proposed_route"])} |')
        lines.append("")
    lines += ["## Additional acquisition references", "", "These are husbandry ideas, not implemented corpse-loot guarantees or permission to carry special creature abilities into an extract.", "", "| Creature / core page | Resource or husbandry reference |", "|---|---|"]
    for r in supplementary["creature_husbandry"]:
        lines.append(f'| {clean(r["name"])} / {r["page"]} | {clean(r["book_reference"])} |')
    lines += ["", "## Recipe input vocabulary", "", "Retained to avoid losing resource references embedded in the 16 schematic records. Replace portions with actual SWG slot classes, component identities and balanced unit costs.", "", "| ID / recipe | Book inputs |", "|---|---|"]
    for r in supplementary["schematic_inputs"]:
        lines.append(f'| {r["id"]} / {clean(r["name"])} | {clean(r["book_inputs"])} |')
    lines += ["", "## Claude adaptation checklist", "", "For each chosen entry, record: raw resource/component/consumable/story item; exact parent class and client strings; acquisition and planet fallback; consumer schematic and profession; per-property weights/caps; quantity and lifecycle; art source; lore/era check; normal-player test receipts. New planet names in these books do not prove those planets are playable.", "",
             "Review in particular: Jedha/Drengir/kyber terminology and mixed continuity; Malachor V/Nathema/Ziost survival and dates; Vong coral identity; miraculous medical/Force effects. The core's cautious Ysalamir/Vornskr husbandry conflicts with some pharmacopoeia powers: flag for owner decision, do not silently choose the strongest version.", "",
             "## Sources and reproducibility", "", "One existing name contains an extraction replacement character: the tables display Je'daii, while the JSON retains the original extracted spelling. Original book text is not rewritten.", "", "- Existing owner catalogue: `../Content-catalogue/owner-SWG-SW5E/README.md`.",
             "- Core: `swg-optional-content.json`, 37 planet lists, 28 creature husbandry records, 16 schematics.",
             "- Pharmacopoeia: `pharmacopoeia.json`, four resource tables (20 + 25 + 15 + 20).",
             "- Armory: `armory.json` and `legacy_era_armory.md` section 5; no standalone resource rows.",
             "- Machine-readable handoff: `owner-ttrpg-resource-handoff.json` includes source hashes, stable IDs, proposed routes and prior token matches.",
             "- Rebuild: `python outputs/tools/owner_content/build_resource_handoff.py` (standard library only). All original extracts remain unchanged.", ""]
    (OUT/"owner-ttrpg-resource-handoff.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result["counts"]))


if __name__ == "__main__":
    main()
