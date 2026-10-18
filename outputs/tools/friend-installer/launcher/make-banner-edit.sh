#!/bin/bash
# Edits over a chosen banner art (copy it to ComfyUIinputg11.png) with FLUX.2 klein 4B reference editing (round 7, 18 Oct).
S=${1:?out folder}
W=/c/Users/Pengw/Documents/Codex/2026-10-13/h/outputs/tools/comfy/flux2-klein-4b-edit.json
curl -s -m 2 http://127.0.0.1:8188/system_stats >/dev/null || (cd /c/Users/Pengw/Tools/ComfyUI_windows_portable && (./python_embeded/python.exe -s ComfyUI/main.py --windows-standalone-build --offline --disable-auto-launch --disable-pinned-memory > "$S/comfy.log" 2>&1 &))
for i in $(seq 1 60); do curl -s -m 2 http://127.0.0.1:8188/system_stats >/dev/null && break; sleep 5; done
BASE="Remove all the white translucent sails and the cables holding them; nothing should be stretched above the worldship. Keep the same composition, camera angle, the giant coral worldship in the centre and the burning city-covered planet below. Add many more alien living coral warships around the worldship: reddish-black coral gunships shaped like jagged spearheads, a flat oval coral carrier ringed with spindly branch-like arms with small coral fighters clinging to them, a carrier with broad dark red and green arms, glossy black pyramid-shaped coral corvettes, lumpy pale coral warships patched with glossy black armour plates, a disguised warship that looks like a craggy asteroid, and dense swarms of small rough triangular coral starfighters with dark canopies. They hurl glowing molten magma boulders; small black gravity voids swallow laser bolts. The grey wedge-shaped star destroyers are breaking in half and exploding in fireballs."
P1="$BASE"
P2="$BASE Etch glowing red scar-like ritual tattoo patterns across the coral hulls. In the background a moon is shattering into burning fragments, and silvery storm clouds spiral over the planet."
n=0
for p in "$P1" "$P2"; do n=$((n+1)); for seed in 89 7 314 777; do
  um comfy run "$W" --set "74.text=$p" --set "73.noise_seed:=$seed" --out "$S" --name "e${n}_s${seed}" --timeout 600 2>&1 | tail -1
done; done
echo DONE
