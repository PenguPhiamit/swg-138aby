"""Moved to outputs/tools/swgfmt/ws_read.py (Fable T1, 14 Oct 2026). This shim hands every import of the old path to the
package, so `import ws_read` here and `from swgfmt import ws_read` are the same module object."""
import importlib
import os
import runpy
import sys

_tools = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))
if _tools not in sys.path:
    sys.path.insert(0, _tools)
if __name__ == '__main__':
    runpy.run_module('swgfmt.ws_read', run_name='__main__', alter_sys=True)
else:
    sys.modules[__name__] = importlib.import_module('swgfmt.ws_read')
