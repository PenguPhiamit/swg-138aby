S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
echo "schematic files: $(find $S/object/draft_schematic -name '*.lua' | wc -l)"
grep -rhoE 'resourceTypes = \{[^}]*\}' $S/object/draft_schematic --include=*.lua | tr -d ' \t' | sed 's/resourceTypes={//; s/}//' | tr ',' '\n' | tr -d '"' | grep -v '^$' | sort | uniq -c | sort -rn > /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-resources3/work/schematic_resource_types.txt
wc -l /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-resources3/work/schematic_resource_types.txt; head -25 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-resources3/work/schematic_resource_types.txt
echo "===== per-schematic lists (file: types)"; grep -rlE 'resourceTypes = \{' $S/object/draft_schematic --include=*.lua | wc -l
grep -rHoE 'resourceTypes = \{[^}]*\}' $S/object/draft_schematic --include=*.lua | sed "s#$S/object/draft_schematic/##" | tr -d ' \t"' | sed 's/resourceTypes={//; s/}$//' > /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-resources3/work/schematic_types_by_file.txt
head -3 /mnt/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/Fable-resources3/work/schematic_types_by_file.txt
