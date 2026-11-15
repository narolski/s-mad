"""Sealed MAD22 read (FINAL): the missing released-detector rows, SelfMAD on corrected MAD22, scored on SelfMAD's RS1
platform (the DGX, RS1's score.py = AR1 score.py byte copy, --mode own: dlib 81 landmarks, 384 px, the release's own
preprocessing), AFTER the registration commit, once. The inputs are exactly the RS1 rows the other releases were
scored on (athena_manifest.csv sets G22_raw, G22_aln, E7aln22_<fam>, M22_<fam>; 5,911 files).
Output is SEALED: this script prints counts only, and the npz is opened only by final_read.py.
  python3 -I selfmad_mad22.py list     -> /mnt/t7/smad_next/FINAL/selfmad/selfmad_mad22_list.csv (+ meta csv)
  bash: score.py run (see README: exact command, nice, workers 2, beside the running GPU job)
  python3 -I selfmad_mad22.py pack     -> /mnt/t7/smad_next/FINAL/selfmad/selfmad_mad22_scores.npz (+ .sha256), reader format"""
import csv
import hashlib
import pathlib
import sys

import numpy as np

D = pathlib.Path("/mnt/t7/smad_next/FINAL/selfmad")
MAN = pathlib.Path("/mnt/t7/smad_next/RS1/athena/athena_manifest.csv")
FAM22 = ("FaceMorpher", "MIPGAN_I", "MIPGAN_II", "OpenCV", "Webmorph")
SETS = {"G22_raw", "G22_aln"} | {f"E7aln22_{f}" for f in FAM22} | {f"M22_{f}" for f in FAM22}
TAG = "own_selfmad_mad22__dgx"


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def main():
    step = sys.argv[1]
    D.mkdir(parents=True, exist_ok=True)
    if step == "list":
        rows = [r for r in csv.DictReader(open(MAN)) if r["set"] in SETS and r["origin"] == "crop"]
        assert len(rows) == 5911, len(rows)
        with open(D / "selfmad_mad22_list.csv", "w", newline="") as f:
            w = csv.writer(f); w.writerow(["id", "path"])
            for r in rows:
                assert pathlib.Path(r["src_path"]).exists()
                w.writerow([r["id"], r["src_path"]])
        with open(D / "selfmad_mad22_meta.csv", "w", newline="") as f:
            w = csv.writer(f); w.writerow(["id", "set", "persons", "expr", "src_sha256"])
            for r in rows:
                w.writerow([r["id"], r["set"], r["persons"], r["expr"], sha(r["src_path"])])
        print("SELFMAD_LIST", len(rows), sha(D / "selfmad_mad22_list.csv"))
    elif step == "pack":
        meta = {r["id"]: r for r in csv.DictReader(open(D / "selfmad_mad22_meta.csv"))}
        z = np.load(D / "scores" / f"scores_{TAG}.npz")
        assert str(z["det"]) == "selfmad_hrnet_w18" and str(z["mode"]) == "own"
        ids = z["id"].tolist()
        assert sorted(ids) == sorted(meta), "scored rows differ from the list"
        cols = dict(det=[], variant=[], pool=[], logit=[], pa=[], pb=[], expr=[])
        for i, l in zip(ids, z["logit_noTTA"]):
            r = meta[i]; pp = r["persons"].split("|")
            cols["det"].append("selfmad_hrnet_w18"); cols["variant"].append("own_dgx"); cols["pool"].append(r["set"])
            cols["logit"].append(float(l)); cols["pa"].append(pp[0]); cols["pb"].append(pp[-1]); cols["expr"].append(r["expr"])
        out = D / "selfmad_mad22_scores.npz"
        np.savez(out, **{k: np.array(v) for k, v in cols.items()})
        h = sha(out)
        (D / "selfmad_mad22_scores.npz.sha256").write_text(f"{h}  {out.name}\n")
        print("SELFMAD_PACKED", len(ids), "rows", h)
    else:
        sys.exit("list | pack")


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
