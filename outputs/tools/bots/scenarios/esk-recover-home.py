"""Return Esk's stranded crew via the verified Hoth -> Coronet -> Mos Eisley route."""
from fallback_scenarios import recover_home

GROUP = 'Esk'


def run(g):
    recover_home(g)
