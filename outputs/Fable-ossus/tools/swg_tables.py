"""Moved to outputs/tools/swgfmt/swg_tables.py (Fable T1, 14 Oct 2026). This shim hands every import of the old path to the
package, so `import swg_tables` here and `from swgfmt import swg_tables` are the same module object."""
import importlib
import os
import runpy
import sys

_tools = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))
if _tools not in sys.path:
    sys.path.insert(0, _tools)
if __name__ == '__main__':
    runpy.run_module('swgfmt.swg_tables', run_name='__main__', alter_sys=True)
else:
    sys.modules[__name__] = importlib.import_module('swgfmt.swg_tables')
