"""Sealed MAD22 read (FINAL): the printed reference detector = the best single development statistic,
noise_std_face (smadcvpr/cue_floor.stats, through AF0's cues_all.one, imported unchanged, sha256 pinned), on the same
512-px frames our networks read (every row of the pack's final_bench.csv: standard, E7 and border-equalised copies).
Direction fixed on development data (FFHQ landmark_combined, PN1 amendment 14 read: morphs LOWER in noise, AUC
0.886): the reader scores -noise_std_face. Run on the DGX CPU AFTER the registration commit, once. Output SEALED:
prints counts only; the npz is opened only by final_read.py.
  python3 -I beststat_mad22.py --tree /mnt/t7/smad_next/FINAL/tree_FINAL_mad22/final"""
import argparse
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
OUT = pathlib.Path("/mnt/t7/smad_next/FINAL/beststat/beststat_mad22.npz")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tree", required=True); ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    assert hashlib.sha256(SRC.read_bytes()).hexdigest() == SRC_SHA
    sys.path.insert(0, str(SRC.parent))
    spec = importlib.util.spec_from_file_location("af0_cues_all", SRC)
    M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
    import cue_floor as CF
    j = list(CF.NAMES).index("noise_std_face")
    tree = pathlib.Path(a.tree)
    rows = list(csv.DictReader(open(tree / "data/manifests/final_bench.csv")))[: a.limit or None]
    v = np.array([M.one(str(tree / "data" / r["path"]))[j] for r in rows], np.float64)
    out = OUT if not a.limit else OUT.with_name(f"beststat_limit{a.limit}.npz")
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, id=np.array([r["id"] for r in rows]), noise_std_face=v)
    h = hashlib.sha256(out.read_bytes()).hexdigest()
    (out.parent / (out.name + ".sha256")).write_text(f"{h}  {out.name}\n")
    print("BESTSTAT", len(rows), "rows", h)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
