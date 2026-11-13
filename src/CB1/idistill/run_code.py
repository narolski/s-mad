"""CB1: run an authors' script under python -I with its own folder and the stub folder on sys.path.
  python3 -I run_code.py CODE_DIR STUB_DIR SCRIPT.py [args...]"""
import os, runpy, sys
code, stubs, script = sys.argv[1:4]
sys.path[:0] = [code, stubs] + [p for p in os.environ.get("CB1_EXTRA_SITE", "").split(":") if p]   # DGX variant: extra packages
sys.argv = [script] + sys.argv[4:]
runpy.run_path(script, run_name="__main__")
