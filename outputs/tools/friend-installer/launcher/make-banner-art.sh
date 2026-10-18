#!/bin/bash
# Banner art for the launcher (round 5, 18 Oct): local ComfyUI + FLUX.2 klein 4B via um comfy, 1536x512, no text.
# Ships from the Legends descriptions (Koros-Strohna worldship, coralskippers, miid ro'ik, magma weapons).
# Usage: make-banner-art.sh <out folder>; then: python -I make-banner.py <art.png> banner.png (adds the title).
S=${1:?out folder}; W=$(dirname "$0")/../../comfy/flux2-klein-4b-t2i.json
VONG="alien organic invasion fleet grown from rough pale yorik coral and volcanic rock: a colossal disc-shaped living worldship with huge spiraling arms like a hurricane, covered in craggy protrusions, trailing vast translucent membrane sails; coral warships with lumpy hulls patched with glossy black armour plates; swarms of small triangular coral starfighters with dark canopies; they hurl glowing molten magma boulders and streams of lava slag, no lasers"
P1="$VONG, looming in a burning sky above a planet-wide city of endless skyscrapers, grey triangular wedge-shaped star destroyer capital ships and rounded bulbous cruisers breaking apart and exploding in huge fireballs, falling wreckage trailing smoke, X-wing starfighters firing red lasers, cinematic wide matte painting, epic space opera, dramatic lighting, highly detailed, no text, no letters, no logo"
P2="$VONG, in orbit above a burning city-covered planet, a defending fleet of grey triangular wedge-shaped star destroyers torn open by magma impacts and exploding, debris and escape pods everywhere, X-wing starfighters dogfighting the coral fighters, red laser bolts against molten rock, cinematic wide matte painting, epic space opera, dramatic lighting, highly detailed, no text, no letters, no logo"
curl -s -m 2 http://127.0.0.1:8188/system_stats >/dev/null || (cd /c/Users/Pengw/Tools/ComfyUI_windows_portable && (./python_embeded/python.exe -s ComfyUI/main.py --windows-standalone-build --offline --disable-auto-launch --disable-pinned-memory > "$S/comfy.log" 2>&1 &))
for i in $(seq 1 60); do curl -s -m 2 http://127.0.0.1:8188/system_stats >/dev/null && break; sleep 5; done

n=0
for p in "$P1" "$P2"; do n=$((n+1)); for seed in 11 23 47; do
  um comfy run "$W" --set "74.text=$p" --set "73.noise_seed:=$seed" --set "62.width:=1536" --set "62.height:=512" --set "66.width:=1536" --set "66.height:=512" --out "$S" --name "y${n}_s${seed}" --timeout 600 2>&1 | tail -1
done; done
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$(cygpath -w "$(dirname "$0")/stop-comfy.ps1")"
echo DONE
