"""Apply C25 only to ChatGPT's worktree, as swgemu; never build/deploy."""
from pathlib import Path
import subprocess

ROOT = Path('/opt/swg/Core3-gpt')
branch = subprocess.check_output(['git', '-C', str(ROOT), 'branch', '--show-current'], text=True).strip()
assert branch == 'gpt/work', branch
assert not subprocess.check_output(['git', '-C', str(ROOT), 'status', '--porcelain'], text=True).strip(), 'worktree must be clean'
path = ROOT / 'MMOCoreORB/src/server/zone/objects/creature/commands/PurchaseTicketCommand.h'
raw = path.read_bytes()
old = b'\t\tReference<PlanetTravelPoint*>  destPoint = pmArrival->getPlanetTravelPoint(arrivalPoint);'
new = b'''\t\tReference<PlanetTravelPoint*> departureTravelPoint = pmDeparture->getPlanetTravelPoint(departurePoint);

\t\tif (departureTravelPoint == nullptr || departureTravelPoint->getShuttle() == nullptr) {
\t\t\tcreature->sendSystemMessage("Travel from your departure point is temporarily unavailable. Please try again shortly.");
\t\t\treturn GENERALERROR;
\t\t}

''' + old
assert raw.count(old) == 1
raw = raw.replace(old, new)
old = b'\t\tif (arrivalShuttle == nullptr) {\n\t\t\treturn GENERALERROR;\n\t\t}'
new = b'''\t\tif (arrivalShuttle == nullptr) {
\t\t\tcreature->sendSystemMessage("Travel to your destination is temporarily unavailable. Please try again shortly.");
\t\t\treturn GENERALERROR;
\t\t}'''
assert raw.count(old) == 1
path.write_bytes(raw.replace(old, new))
print('C25: updated only PurchaseTicketCommand.h in gpt/work; unbuilt and untested')
