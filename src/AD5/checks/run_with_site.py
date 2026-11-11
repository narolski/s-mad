"""Retrains of released methods (AD5): run a third-party script under python3 -I with one extra site directory.

  python3 -I run_with_site.py SITE_DIR SCRIPT.py [args...]
Inserts SITE_DIR at the front of sys.path (python -I ignores PYTHONPATH and does not add the script's directory),
then runs SCRIPT.py as __main__ with the remaining arguments. Used for the 8-image checks on the DGX only.
"""
import runpy
import sys

site, script = sys.argv[1], sys.argv[2]
sys.path.insert(0, site)
sys.argv = [script] + sys.argv[3:]
runpy.run_path(script, run_name="__main__")
