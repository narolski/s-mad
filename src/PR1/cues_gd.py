"""PR1: run src/PN1/cues27.py UNCHANGED (sha256 printed, imported) with its output folder set to
/mnt/t7/smad_next/PR1/cues (nothing is written into the PN1 folders).
  python3 -I cues_gd.py gd0=/mnt/t7/smad_next/PR1/lists/gd0.csv
Amendment 4: a job prefixed "loader:" computes the same 26 statistics through smadcvpr/cue_floor._cue_one (unchanged;
the networks' own loader view at 512 px) plus the PNG file size, for frames that are not 512 px (GD1).
  python3 -I cues_gd.py loader:gd1=/mnt/t7/smad_next/PR1/lists/gd1.csv"""
import csv
import hashlib
import importlib.util
import os
import pathlib
import sys

import numpy as np

SRC = pathlib.Path("/home/narolski/smad-next/src/PN1/cues27.py")
CF_SRC = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr/cue_floor.py")
CF_SHA = "556e7aba7c52d9ffaeab315884ce834fbb2413548bd335aac2442828f5dd40ca"
OUT = pathlib.Path("/mnt/t7/smad_next/PR1/cues")


def loader_job(name, lst):
    assert hashlib.sha256(CF_SRC.read_bytes()).hexdigest() == CF_SHA
    sys.path.insert(0, str(CF_SRC.parent))
    import cue_floor as CF
    out = OUT / f"{name}.npz"
    if out.exists():
        print("exists", out)
        return
    R = list(csv.DictReader(open(lst)))
    C = []
    for k, r in enumerate(R):
        C.append(np.r_[CF._cue_one(r["path"]), os.path.getsize(r["path"])])
        if (k + 1) % 200 == 0:
            print(name, k + 1, len(R), flush=True)
    np.savez(out, ids=np.array([r["id"] for r in R]), cues=np.stack(C), names=np.array(list(CF.NAMES) + ["png_bytes"]),
             path_label=np.array("loader view (common.ImageItems at 512)"))
    print("DONE", name, len(R), flush=True)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    jobs = sys.argv[1:]
    for j in [j for j in jobs if j.startswith("loader:")]:
        n, l = j[len("loader:"):].split("=", 1)
        loader_job(n, l)
    rest = [j for j in jobs if not j.startswith("loader:")]
    if rest:
        spec = importlib.util.spec_from_file_location("cues27", SRC)
        M = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(M)
        M.OUT = OUT
        print("cues27.py sha256", hashlib.sha256(SRC.read_bytes()).hexdigest(), flush=True)
        sys.argv = [sys.argv[0]] + rest
        M.main()
