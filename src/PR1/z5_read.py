"""PR1 Z5 for the three-source arm SbM3 (prereg.md section 6a, Z5; amendment 1 F13): storage evasion of morphs on the
MS1 FFHQ hold-out, formula and rule of C2P.4 (H-new-1), from the MS1 fits' own stored scores (scores_eval.npz of
MS1_SbM3_s<seed>.tar, scored at fit time on the fits' own L40S; no rescoring, no gate needed). The MS1 Sb fits are
printed beside (same formula, no rule). Read only after the MS1 owner's committed and reviewed read. C2P helpers
imported unchanged from src/PN1/c2p_read.py. Development data only.
  python3 -I z5_read.py --out z5_read.json"""
import argparse
import csv
import hashlib
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/PN1")
import c2p_read as C  # noqa: E402

RES = pathlib.Path("/mnt/t7/smad_next/MS1/results_rented")
MS1M_SHA = "d1fab6ad4b20f0ec9dd426374ccd56e96368bf7b658b48e3ef31867e1fe470c5"
SEEDS = (403, 404, 405, 406, 407)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    assert sha(C.MS1M) == MS1M_SHA, "MS1 manifest off its pin"
    M = list(csv.DictReader(open(C.MS1M)))
    natp, natm, pairs, mpairs = C.holdout(M)
    rng = np.random.default_rng(C.RNG_G)
    boot = {z: [rng.integers(0, len(pairs[z]), len(pairs[z])) for _ in range(C.B_BOOT)] for z in C.SIZES}
    out = dict(n=dict(photo=len(natp), u50=len(natm), pairs={z: len(pairs[z]) for z in C.SIZES},
                      mpairs={z: len(mpairs[z]) for z in C.SIZES}), nets={})
    for arm in ("SbM3", "Sb"):
        for s in SEEDS:
            t = RES / f"MS1_{arm}_s{s}.tar"
            ok = sha(t) == (RES / f"MS1_{arm}_s{s}.tar.sha256").read_text().split()[0]
            L = C.npz_from_tar(str(t), "scores_eval.npz") if ok else None
            need = set(natp) | set(natm) | {f"{i}_{z}" for z in C.SIZES for i in pairs[z]} | \
                {f"{i}_{z}" for z in C.SIZES for i in mpairs[z]}
            if L is None or not need <= set(L) or not all(np.isfinite(L[i]) for i in need):
                out["nets"][f"{arm}_s{s}"] = None
                continue
            out["nets"][f"{arm}_s{s}"] = C.net_stats(L, natp, natm, pairs, mpairs, boot)
    V = {}
    for arm in ("SbM3", "Sb"):
        vals = {z: [(out["nets"][f"{arm}_s{s}"] or {}).get(z, {}).get("d_mean_att_sd") for s in SEEDS] for z in C.SIZES}
        sup = any(sum(1 for v in vals[z] if v is not None and v <= -0.20) >= 4 for z in C.SIZES)
        fal = all(sum(1 for v in vals[z] if v is not None and v >= -0.10) >= 4 for z in C.SIZES)
        V[arm] = dict(d_mean_att_sd=vals, verdict=("supported" if sup else "falsified" if fal else "inconclusive"),
                      decides=(arm == "SbM3"))
    out["verdicts"] = V
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out["n"]))
    for arm, v in V.items():
        print(arm, v["verdict"], {z: [None if x is None else round(x, 3) for x in v["d_mean_att_sd"][z]] for z in C.SIZES})
    for k, r in out["nets"].items():
        if r:
            print(k, {z: dict(miss_nat=round(r[z]["miss_native_paired"], 3), miss_sto=round(r[z]["miss_stored"], 3)) for z in C.SIZES})


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
