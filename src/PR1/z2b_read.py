"""PR1 Z2b and Z2b-tau5 (prereg.md section 4 and amendment 1 F3). Read only after the TT1 owner has committed its
TT1-FS read (tt1_read_fs.json). Inputs: that json (F-bar per network, gate list) and the TT1-FS result tar's per-row
TT1 logits (scores/<net>__tt1.npz, TF32 off); PR1's tau5 and y from z_read.json. Families and pools from the TT1
reader's own load_pools() (unchanged, imported). Development data only.
  python -I z2b_read.py --tt1json .../tt1_read_fs.json --tt1tar .../TT1_A100_pn1fs_fs.tar --out z2b_read.json [--mock]"""
import argparse
import io
import json
import pathlib
import sys
import tarfile

import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/TT1")
import tt1common as T  # noqa: E402
import tt1_read as TR  # noqa: E402

ZREAD = pathlib.Path("/home/narolski/smad-next/experiments/PR1_protocol-reads-existing-networks/z_read.json")
ARMS, SEEDS = ("A", "B", "Sb"), (403, 404, 405, 406, 407)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tt1json")
    ap.add_argument("--tt1tar")
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    from scipy.stats import spearmanr
    Z = json.load(open(ZREAD))["per_net"]
    P, _ = TR.load_pools()
    fam_src = {f: ([f] if f != "lfw_calfw" else ["lfw", "calfw"]) for f in T.FAMILIES}
    if a.mock:
        passed = {f"PN1_{x}_s{s}" for x in ARMS for s in SEEDS} - {"PN1_A_s404"}
        fbar = {n: 0.01 * (k + 1) for k, n in enumerate(sorted(passed))}
        tf = None
    else:
        J = json.load(open(a.tt1json))
        assert not J.get("mock")
        passed = set(J["gate_passed"])
        fbar = {n: J["nets"][n]["r5"]["Fbar"] for n in J["nets"]}
        tf = tarfile.open(a.tt1tar)
        root = tf.getnames()[0].split("/")[0]
    out = dict(per_net={}, mock=a.mock)
    for x in ARMS:
        for s in SEEDS:
            n = f"PN1_{x}_s{s}"
            if n not in passed:
                out["per_net"][n] = None
                continue
            if a.mock:
                rng = np.random.default_rng(s)
                L = {i: float(rng.normal(-2, 1.5)) for v in P.values() for i, _ in v}
            else:
                z = np.load(io.BytesIO(tf.extractfile(f"{root}/scores/{n}__tt1.npz").read()))
                L = dict(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
            t5 = Z[f"{x}_s{s}"]["tau5"]
            fl = {f: float(np.mean(np.concatenate([np.array([L[i] for i, _ in P[f"U:{q}"]]) for q in fam_src[f]]) > t5))
                  for f in T.FAMILIES}
            fl_own = {f: float(np.mean(np.concatenate([np.array([L[i] for i, _ in P[f"U:{q}"]]) for q in fam_src[f]]) > 0))
                      for f in T.FAMILIES}
            g = max(fl.values())
            out["per_net"][n] = dict(tau5=t5, flags_t5=fl, flags_own=fl_own, G_unseen=g, G_unseen_family=max(fl, key=fl.get),
                                     Fbar=fbar.get(n), y_own=Z[f"{x}_s{s}"]["z2rho"]["y_own"])
    V = {}
    for x in ARMS:
        gs = [out["per_net"][f"PN1_{x}_s{s}"]["G_unseen"] if out["per_net"][f"PN1_{x}_s{s}"] else None for s in SEEDS]
        nu = sum(1 for v in gs if v is not None and v <= 0.10)
        nn = sum(1 for v in gs if v is not None and v > 0.15)
        V[f"Z2b_tau5_{x}"] = dict(G_unseen=gs, verdict="usable on unseen sources" if nu >= 4 else ("not usable" if nn >= 4 else "inconclusive"),
                                  limit="tau5 from stored TF32-on scores; TT1 rows scored TF32 off (TT1: up to 0.035 logit)")
    keys = [n for n, r in out["per_net"].items() if r is not None]
    xs = np.array([out["per_net"][n]["Fbar"] for n in keys])
    ys = np.array([out["per_net"][n]["y_own"] for n in keys])
    rho = float(spearmanr(xs, ys).correlation)
    rng = np.random.default_rng(20261142)
    nperm = 2000 if a.mock else 200000
    perm = np.array([spearmanr(xs, rng.permutation(ys)).correlation for _ in range(nperm)])
    arm = np.array([k.split("_")[1] for k in keys])
    rng2 = np.random.default_rng(20261142)
    pw = []
    for _ in range(nperm):
        yy = ys.copy()
        for ar in ARMS:
            m = arm == ar
            yy[m] = rng2.permutation(ys[m])
        pw.append(spearmanr(xs, yy).correlation)
    xm = [float(xs[arm == ar].mean()) for ar in ARMS if (arm == ar).any()]
    ym = [float(ys[arm == ar].mean()) for ar in ARMS if (arm == ar).any()]
    V["Z2b_rho"] = dict(n=len(keys), rho=rho, p_perm=float((np.abs(perm) >= abs(rho) - 1e-12).mean()),
                        p_perm_within_arm=float((np.abs(np.array(pw)) >= abs(rho) - 1e-12).mean()),
                        rho_arm_means=float(spearmanr(xm, ym).correlation) if len(xm) == 3 else None,
                        label="across recipes (3 arms; effective n about 3)",
                        verdict="falsified" if rho >= 0 else ("supported" if rho <= -0.6 else "weak (not decided)"))
    out["verdicts"] = V
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1, default=float))
    for k, v in V.items():
        print(k, json.dumps(v, default=float))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python -I")
    main()
