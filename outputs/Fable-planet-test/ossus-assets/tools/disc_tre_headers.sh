#!/bin/sh
# List the disc-extracted SWG archives with their TRE header (magic + version). Read-only.
#   MSYS_NO_PATHCONV=1 wsl -d Debian -u swgemu -- sh /mnt/c/.../ossus-assets/tools/disc_tre_headers.sh
D=/opt/swg/disc-extracted/SWG-group/files/SWG
ls "$D" | wc -l
for f in "$D"/*.tre; do
  printf '%-32s %12s  ' "$(basename "$f")" "$(stat -c %s "$f")"
  head -c 8 "$f" | od -An -c | tr -s ' ' | tr -d '\n'
  echo
done
echo ---- other dirs
ls "$D/miles" "$D/forcefeedback" 2>/dev/null | head -20
echo ---- LP and Support dirs
ls /opt/swg/disc-extracted/LP /opt/swg/disc-extracted/SWG 2>/dev/null | head -20
