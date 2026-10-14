#!/bin/bash
# Fetch section A of Documentation-support/archive-download-plan.md (owner's go, 13 Oct 22:35) into work/research/.
# Partial, pinned checkouts; nothing is built, run or installed. Prints one JSON line per item for the record
# (Content-catalogue/archive-downloads.json, written by archive_record.py).   Usage: archive_fetch.sh [ITEM...]
R=/c/Users/Pengw/Documents/Codex/2026-10-13/h/work/research
CAP_MB=3072
set -u

used_mb() { du -sm "$R"/Miphstoe_BellumGero-Live "$R"/Thrax989_SWGFlurry "$R"/swgemu_Tools "$R"/XanderOlson_swgemu_single_player \
                   "$R"/[name removed]_swgmtv "$R"/nostyleguy_io_scene_swg_msh 2>/dev/null | awk '{t+=$1} END {print t+0}'; }

sparse() {  # id url dir folders...
  local id=$1 url=$2 dir=$3; shift 3
  if [ "$(used_mb)" -ge "$CAP_MB" ]; then echo "{\"id\":\"$id\",\"status\":\"skipped_cap\"}"; return; fi
  if [ ! -d "$R/$dir/.git" ]; then
    git clone -q --depth 1 --filter=blob:none --no-checkout "$url" "$R/$dir" || { echo "{\"id\":\"$id\",\"status\":\"clone_failed\"}"; return; }
  fi
  if [ $# -gt 0 ]; then git -C "$R/$dir" sparse-checkout set "$@"; else git -C "$R/$dir" sparse-checkout disable; fi
  git -C "$R/$dir" checkout -q 2>/dev/null || git -C "$R/$dir" checkout -q HEAD
  local rev mb lic
  rev=$(git -C "$R/$dir" rev-parse HEAD)
  mb=$(du -sm "$R/$dir" | cut -f1)
  lic=$(ls "$R/$dir" | grep -i -m1 "^licen\|^copying" || true)
  echo "{\"id\":\"$id\",\"status\":\"downloaded\",\"url\":\"$url\",\"path\":\"work/research/$dir\",\"revision\":\"$rev\",\"mb\":$mb,\"license_file\":\"$lic\",\"folders\":\"${*:-whole repo}\"}"
}

release_zip() {  # id owner/repo dir
  local id=$1 repo=$2 dir=$3 url tag
  mkdir -p "$R/$dir"
  read -r tag url < <(curl -s -m 30 "https://api.github.com/repos/$repo/releases/latest" |
                        python -c "import sys,json; d=json.load(sys.stdin); print(d.get('tag_name','none'), d.get('zipball_url',''))")
  [ -z "$url" ] && url="https://github.com/$repo/archive/refs/heads/main.zip" && tag=main
  curl -s -L -m 120 -o "$R/$dir/$dir-$tag.zip" "$url" || { echo "{\"id\":\"$id\",\"status\":\"download_failed\"}"; return; }
  echo "{\"id\":\"$id\",\"status\":\"downloaded\",\"url\":\"$url\",\"path\":\"work/research/$dir/$dir-$tag.zip\",\"revision\":\"$tag\",\"bytes\":$(stat -c %s "$R/$dir/$dir-$tag.zip"),\"sha256\":\"$(sha256sum "$R/$dir/$dir-$tag.zip" | cut -d' ' -f1)\",\"folders\":\"release zip\"}"
}

ALL=" ${*:-A1 A2 A3 A4 A5 A6} "
for id in A1 A2 A3 A4 A5 A6; do
  [[ "$ALL" == *" $id "* ]] || continue
  case $id in
    A1) sparse A1 https://github.com/Miphstoe/BellumGero-Live Miphstoe_BellumGero-Live MMOCoreORB/bin/scripts MMOCoreORB/bin/conf MMOCoreORB/tools ;;
    A2) sparse A2 https://github.com/Thrax989/SWGFlurry Thrax989_SWGFlurry MMOCoreORB/bin/scripts ;;
    A3) sparse A3 https://github.com/nostyleguy/io_scene_swg_msh nostyleguy_io_scene_swg_msh ;;  # no releases or tags: pinned clone of main
    A4) sparse A4 https://github.com/swgemu/Tools swgemu_Tools ;;
    A5) sparse A5 https://github.com/XanderOlson/swgemu_single_player XanderOlson_swgemu_single_player .github spec MMOCoreORB/src/tests MMOCoreORB/bin/scripts/screenplays/tests ;;
    A6) sparse A6 https://github.com/[name removed]/swgmtv [name removed]_swgmtv ;;
  esac
done
echo "{\"total_mb\":$(used_mb)}"
