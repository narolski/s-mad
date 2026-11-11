"""SM1 amendment A12 item 13 (post hoc): history copies at sizes not used in training, scored by the frozen heads.

Images: the protocol-network experiment's softened AR1 copies (AF0 `ar1soft.csv`, `ladsoft.csv`; target inter-eye
distance 112.7 px "amsl112" and 61.2 px "fm61"; aligned by prep_eval.align): R0 (camera photos, 200 hosts) and R2w
(both tools, 200 hosts), R3 / R4 (OpenCV, 536 hosts), R3m (OpenCV, 200 hosts); features from Athena job MODE a12
(feat_athena/test_af0soft.npz). Each softened image has its unsoftened counterpart in the SM1 AR1 test list (base id).
Per head (arm x seed from OUT/heads, the release-recipe heads from OUT/heads_fz1, the FE header): logit = feat @ W + b
(release recipe: normalised features, z0 - z1); thresholds = the head's camera threshold (95th percentile of its own
AR1 FRGC/colorFERET R0 logits) and its own rule (logit >= 0). Flag rate of each softened genuine-class set and of its
unsoftened counterparts (same hosts), the paired increment (softened - unsoftened, same hosts), miss rate of softened
R4 and of the same unsoftened R4. 5-seed means; AR1 person bootstrap (read_p3 draws). Note: the unsoftened R0 is the
raw camera photo, the softened copies are aligned frames, so the increment mixes alignment and softening.

  python3 -I a12_af0soft.py [--dirs heads,heads_fz1] -> RES/a12_af0soft.json
"""
import argparse
import csv
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import read_p3 as P  # noqa: E402

ARMS = ("a", "b", "d5", "d50", "bp", "c", "d", "e", "f")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dirs", default="heads,heads_fz1")
    ap.add_argument("--B", type=int, default=2000)
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    zf = np.load(K.OUT / "feat_athena/test_af0soft.npz")
    fid = [str(i) for i in zf["id"]]
    F = zf["feat"].astype(np.float64)
    soft = list(csv.DictReader(open(K.OUT / "flists/test_af0soft.csv")))
    assert [r["id"] for r in soft] == fid
    rows = P.meta()
    R = P.Reader(rows, a.B)
    pos = {r["id"]: i for i, r in enumerate(rows)}
    r0 = R.sel("ar1:frgcferet:none:R0", "0", "")
    sets = {}
    for r in soft:
        sets.setdefault(r["cell"], []).append(r)
    Wcache = {}
    res = {}
    for dname in a.dirs.split(","):
        hd = K.OUT / dname
        for arm in ARMS + ("feref",):
            files = [K.OUT / "heads/feref.npz"] if arm == "feref" else [hd / f"{arm}_s{s}.npz" for s in K.SEEDS]
            files = [f for f in files if f.exists()]
            if not files or (arm == "feref" and dname != "heads"):
                continue
            per = []
            for f in files:
                z = np.load(f)
                zt = dict(zip([str(i) for i in z["id"]], z["logit"].astype(np.float64)))
                zbase = np.array([zt[r["id"]] for r in rows])
                if arm == "feref":
                    from safetensors.torch import load_file
                    if "fe" not in Wcache:
                        sd = load_file("/mnt/t7/smad_heldout/mad22_production_cpu_stage_v1/payload/models/"
                                       "74dd7fbce8385ec4c080def2c63300243b04ca2abd8ddea6eb2a519296e054a9.safetensors",
                                       device="cpu")
                        Wcache["fe"] = (sd["head.weight"].float().numpy(), sd["head.bias"].float().numpy())
                    Wh, bh = Wcache["fe"]
                    zz = F @ Wh.T.astype(np.float64) + bh
                    zs = zz[:, 0] - zz[:, 1]
                elif dname == "heads_fz1":
                    Fn = F / np.maximum(np.linalg.norm(F, axis=1, keepdims=True), 1e-12)
                    zz = Fn @ z["W"].T.astype(np.float64) + z["b"]
                    zs = zz[:, 0] - zz[:, 1]
                else:
                    zs = F @ z["W"].astype(np.float64) + float(z["b"])
                zsoft = dict(zip(fid, zs))
                thr = {"cam": float(np.quantile(zbase[r0], 0.95)), "own": 0.0}
                m = {}
                for cell, rs in sets.items():
                    ib = np.array([pos[r["base"]] for r in rs])
                    s_soft = np.array([zsoft[r["id"]] for r in rs])
                    s_base = zbase[ib]
                    W = R.w(ib, True)
                    lab = rs[0]["label"]
                    for tn, t in thr.items():
                        fs = (s_soft >= t) if lab == "0" else (s_soft < t)
                        fb = (s_base >= t) if lab == "0" else (s_base < t)
                        kind = "flag" if lab == "0" else "miss"
                        for tag, v in (("soft", fs), ("unsoftened", fb), ("increment", fs.astype(float) - fb)):
                            v = v.astype(float)
                            m[f"{kind}:{tn}:{cell}:{tag}"] = (float(v.mean()), (W * v).sum(1) / W.sum(1))
                per.append(m)
            res[f"{dname}:{arm}"] = P.summarise(per)
            r_ = res[f"{dname}:{arm}"]
            print(dname, arm, " ".join(f"{k.split(':', 2)[2]}={v['mean']:.3f}" for k, v in r_.items()
                                       if k.startswith("flag:cam:af0soft:R0") or k.startswith("miss:cam:af0soft:R4")),
                  flush=True)
    res["note"] = ("post hoc (A12 item 13); our frames (aligned softened copies against raw unsoftened photos), "
                   "first-test data, arms fixed in advance; sizes 112.7 / 61.2 px target inter-eye distance, not the "
                   "80-px storage size of the arm (e) training copies")
    json.dump(res, open(K.RES / "a12_af0soft.json", "w"), indent=1)


if __name__ == "__main__":
    main()
