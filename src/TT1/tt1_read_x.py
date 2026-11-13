"""TT1-X printed reads (prereg_x_block.md): per network R1-R5 with the TT1 reader statistics unchanged (tt1_read.py:
load_pools, boot_weights with default_rng(20261122), read_net, family_ci), the TT1-FS printed reads (tt1_read_fs.py:
extra_reads), clipped family intervals with Clopper-Pearson beside zero-event families, and the TF32-split print.
No rule, no verdict. Part 1: Sp seeds 403-405 (pn1fs scores, gate passed per network). FS1 Sb 403-405 are printed as a
reference from tt1_read_fs.json (TT1-FS output), not recomputed.
  python -I tt1_read_x.py --scores DIR --nets DIR --gate gate_fs.json --names N1 N2 ... --out OUT.json [--mock]"""
import argparse
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tt1common as T  # noqa: E402
import tt1_read as TR  # noqa: E402
import tt1_read_fs as TF  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", required=True)
    ap.add_argument("--nets", required=True)
    ap.add_argument("--gate", required=True)
    ap.add_argument("--names", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    P, tt = TR.load_pools()
    W = TR.boot_weights(P, np.random.default_rng(TR.SEED))
    passed = set(a.names) if a.mock else set(json.load(open(a.gate))["passed"])
    out = dict(label="TT1-X printed reads; no rule", nets={}, not_available=[n for n in a.names if n not in passed])
    for n in a.names:
        if n not in passed:
            continue
        if a.mock:
            mr = np.random.default_rng(abs(hash(n)) % 2 ** 32)
            L = {i: float(np.clip(mr.normal(-3.0, 1.2), -3.87, 3.87)) for v in P.values() for i, _ in v}
            for i, _ in P["M_ffhq"]:
                L[i] = float(np.clip(mr.normal(3.0, 1.0), -3.87, 3.87))
            floor, tc = -3.87, -3.6
        else:
            L = {}
            for fam in ("gate", "tt1"):
                z = np.load(pathlib.Path(a.scores) / f"{n}__{fam}.npz")
                L.update(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
            floor = TR.head_floor(pathlib.Path(a.nets) / n)
            tc = TF.tau_cam_fs(pathlib.Path(a.nets) / n)
        r = TR.read_net(L, P, W, tt, floor, tc)
        TR.family_ci(r, P, W, L)
        r["printed"] = TF.extra_reads(L, P)
        corr = {}
        for f in T.FAMILIES:
            srcs = [f] if f != "lfw_calfw" else ["lfw", "calfw"]
            x = np.concatenate([np.array([L[i] for i, _ in P[f"U:{q}"]]) > 0 for q in srcs])
            lo, hi = r["fam_flag_ci"][f]
            corr[f] = dict(boot_ci_clipped=[max(0.0, lo), hi], cp=TR.cp(int(x.sum()), len(x)), zero_event=bool(x.sum() == 0))
        r["family_flag_corrected"] = corr
        if not a.mock:
            zs = np.load(pathlib.Path(a.nets) / n / "scores_eval.npz")
            ms = dict(zip(zs["id"].tolist(), zs["logit"].astype(float).tolist()))
            dd = np.array([L[i] - ms[i] for i, _ in P["R_cam"]])
            r["tf32_split_R_cam"] = dict(max_abs=float(np.abs(dd).max()), median_abs=float(np.median(np.abs(dd))),
                                         flips=int(sum((L[i] > 0) != (ms[i] > 0) for i, _ in P["R_cam"])))
        r["r5"].pop("_draws", None)
        out["nets"][n] = r
        print("read", n, flush=True)
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
