"""Moved to outputs/tools/swgfmt/hoth_ui.py (Fable T1, 14 Oct 2026). This shim hands every import of the old path to the
package, so `import hoth_ui` here and `from swgfmt import hoth_ui` are the same module object."""
import importlib
import os
import runpy
import sys

_tools = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))
if _tools not in sys.path:
    sys.path.insert(0, _tools)
if __name__ == '__main__':
    runpy.run_module('swgfmt.hoth_ui', run_name='__main__', alter_sys=True)
else:
    sys.modules[__name__] = importlib.import_module('swgfmt.hoth_ui')
