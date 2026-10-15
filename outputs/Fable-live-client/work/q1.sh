C=/opt/swg/Core3-dev/MMOCoreORB/src/server/zone
echo "===== travel point list packet"; grep -n 'insert' $C/packets/player/PlanetTravelPointListResponse*.h | head -12
echo "===== ticket purchase: what the server sends the client"; grep -rn 'EnterTicketPurchaseModeMessage\|PlanetTravelPointListResponse' $C/objects/tangible/terminal/travel/TravelTerminalImplementation.cpp $C/managers/planet/PlanetManagerImplementation.cpp 2>/dev/null | head -6
echo "===== zone switch to client (scene name)"; grep -rn 'CmdStartScene' $C/packets/scene/CmdStartScene.h | head -3; grep -n 'insertAscii\|insertString\|terrain' $C/packets/scene/CmdStartScene.h | head -6
echo "===== waypoint planet crc"; grep -rn 'getPlanetCRC\|planetCRC' $C/packets/object/WaypointObjectMessage*.h $C/objects/waypoint/WaypointObjectImplementation.cpp 2>/dev/null | head -4
echo "===== config.lua keys"; grep -n 'ZonesEnabled\|TreFiles\|TrePath' /opt/swg/Core3-dev/MMOCoreORB/bin/conf/config.lua | head -8
