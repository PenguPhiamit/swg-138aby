"""The address bots and the owner's test-galaxy client log in at: the one the test galaxy's row hands out.

Core3's zone server accepts a session only from the IP that logged in (ClientIdMessageCallback.h compares sessions.ip,
written at login, with the zone connection's IP). Under WSL mirrored networking a connection to one of this PC's own
addresses comes from that same address, so logging in at the LAN address and zoning in at the row's Tailscale address
is refused with "Unable to obtain a valid session key" (18 Oct). Same rule as tools/test_galaxy.py: the private
/opt/swg/agent/galaxy-address while WSL lists it, else the first `hostname -I` address.

  python3 login_host.py      prints it (Play SWG Test Galaxy.cmd)
"""
import subprocess
from pathlib import Path

GALAXY_ADDRESS = Path('/opt/swg/agent/galaxy-address')  # private, outside git (tools/test_galaxy.py)


def login_host():
    here = subprocess.check_output(['hostname', '-I'], text=True).split()
    try:
        wanted = GALAXY_ADDRESS.read_text().strip()
    except OSError:  # no override, or a user who can't read /opt/swg/agent
        return here[0]
    return wanted if wanted in here else here[0]


if __name__ == '__main__':
    print(login_host())
