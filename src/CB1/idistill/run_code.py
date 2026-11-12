"""CB1: run an authors' script under python -I with its own folder and the stub folder on sys.path.
  python3 -I run_code.py CODE_DIR STUB_DIR SCRIPT.py [args...]"""
import runpy, sys
code, stubs, script = sys.argv[1:4]
sys.path[:0] = [code, stubs]
sys.argv = [script] + sys.argv[4:]
runpy.run_path(script, run_name="__main__")
