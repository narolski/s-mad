"""PN1: the 27 simple statistics of the alpha-field probe's floor (26 smadcvpr/cue_floor statistics on the 512 frame +
PNG bytes), computed by AF0's cues_all.one (imported unchanged; sha256 1ab50f30...) for PN1 lists that have none.
Output /mnt/t7/smad_next/PN1/cues/<name>.npz (ids, cues, names), the AF0 format.
  python3 -I cues27.py r2w4=/mnt/t7/smad_next/PN1/lists/r2w4.csv ar1soft=/mnt/t7/smad_next/AF0/lists/ar1soft.csv
"""
import csv
import hashlib
import importlib.util
import os
import pathlib
import sys

os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np  # noqa: E402

SRC = pathlib.Path("/home/narolski/smad-next/src/AF0/cues_all.py")
SRC_SHA = "1ab50f3098e9eac6fcdfeb7a08cb6b02613d728f87aa24a4a396509f41cdcc9f"
OUT = pathlib.Path("/mnt/t7/smad_next/PN1/cues")


def main():
    assert hashlib.sha256(SRC.read_bytes()).hexdigest() == SRC_SHA
    sys.path.insert(0, str(SRC.parent))
    spec = importlib.util.spec_from_file_location("af0_cues_all", SRC)
    M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)
    import cue_floor as CF
    OUT.mkdir(parents=True, exist_ok=True)
    for job in sys.argv[1:]:
        name, lst = job.split("=", 1)
        lim = int(os.environ.get("PN1_LIMIT", "0"))
        tag = name + (f"_limit{lim}" if lim else "")
        out = OUT / f"{tag}.npz"
        if out.exists():
            print("exists", out, flush=True)
            continue
        R = list(csv.DictReader(open(lst)))[: lim or None]
        C = []
        for k, r in enumerate(R):
            C.append(M.one(r["path"]))
            if (k + 1) % 200 == 0:
                print(name, k + 1, len(R), flush=True)
        np.savez(out, ids=np.array([r["id"] for r in R]), cues=np.stack(C), names=np.array(list(CF.NAMES) + ["png_bytes"]))
        print("DONE", name, len(R), flush=True)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
