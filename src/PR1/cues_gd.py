"""PR1: run src/PN1/cues27.py UNCHANGED (sha256 asserted, imported) with its output folder set to
/mnt/t7/smad_next/PR1/cues (so nothing is written into the PN1 folders).  python3 -I cues_gd.py gd0=/mnt/t7/smad_next/PR1/lists/gd0.csv"""
import hashlib
import importlib.util
import pathlib
import sys

SRC = pathlib.Path("/home/narolski/smad-next/src/PN1/cues27.py")
SRC_SHA = hashlib.sha256(SRC.read_bytes()).hexdigest()
spec = importlib.util.spec_from_file_location("cues27", SRC)
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
M.OUT = pathlib.Path("/mnt/t7/smad_next/PR1/cues")
print("cues27.py sha256", SRC_SHA, flush=True)
if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    M.main()
