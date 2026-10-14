S=/opt/swg/Core3-dev/MMOCoreORB/bin/scripts
sed -n '61,100p' $S/screenplays/poi/hoth_camps.lua | grep -n '^\s*--\|junk_dealer\|recruiter\|salvage_tech' 
