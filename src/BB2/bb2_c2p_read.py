"""Second backbone (BB2), amendment 1 reader: contrast 2-prime and H-new-1 (registration C2P, PN1 prereg.md, 2715e48)
and the platform gate on the nine BB2 networks, with BB2's three-seed counting; plus the printed same-person splice
reads (S3) from the fit scores. The per-network statistics are C2P's own functions (src/PN1/c2p_read.py, imported
unchanged; sha256 asserted): same hold-out rows, pairs, bootstrap draws (rng 20261131), gate thresholds.
Inputs: BB2C2P.tar (out/C2P_BB2_<arm>_s<seed>_<fam>.npz; fam af0, ffhq, ms1ffhq; rescored on WCSS), the BB2 fit tars
(/mnt/t7/smad_next/BB2/results, stored logits for the gate and the S3 reads), the MS1 and FS1 manifests (pinned in
c2p_read.py), the hold-out sharpness file.
  python3 -I bb2_c2p_read.py --c2p BB2C2P.tar --out OUT.json
  python3 -I bb2_c2p_read.py --mock      (random scores; code path only; output bb2_c2p_mock.json)"""
import argparse
import csv
import hashlib
import json
import math
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "PN1"))
import c2p_read as P  # noqa: E402  (registration C2P reader, unchanged)

C2P_READ_SHA = "45e72914d960214131a5b4a11aefd2e301a2236e908d77d20d94136c1d7d5840"
BB2R = "/mnt/t7/smad_next/BB2/results"
RES = HERE.parents[1] / "experiments" / "BB2_second-backbone"
CLIP_C2P = HERE.parents[1] / "experiments" / "PN1_protocol-network-first-tests" / "c2p_read.json"
ARMS, SEEDS, SIZES = ("A", "B", "Sb"), (403, 404, 405), P.SIZES


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def s3_reads(L, F):
    """Printed only (amendment 1): own-rule flag share of same-person splices (S3), AUC S3 vs S0 and S4 vs S3,
    development (100) and test (191) ladder."""
    out = {}
    for role, tag in (("dev", "D"), ("test", "T")):
        g = {k: [L[r["id"]] for r in F if r["fam"] == "splice" and r["role"] == role and r["rung"] == k] for k in ("S0", "S3", "S4")}
        out[tag] = dict(n=len(g["S3"]), S3_flag=float(np.mean(np.array(g["S3"]) > 0)), S0_flag=float(np.mean(np.array(g["S0"]) > 0)),
                        S4_miss=float(np.mean(np.array(g["S4"]) <= 0)), auc_S3_vs_S0=P.fauc(g["S3"], g["S0"]),
                        auc_S4_vs_S3=P.fauc(g["S4"], g["S3"]))
    return out


def count_c2(res_z_pass, res_z_ctrl):
    """BB2 counting for contrast 2-prime (amendment 1): passes = pass on >= 2 of 3 seeds at both sizes; fails = pass on
    0 seeds at a size where A's control is met on >= 2; uninformative = A's control met on <= 1 seed at either size;
    otherwise inconclusive."""
    if any(res_z_ctrl[z] <= 1 for z in SIZES):
        return "uninformative"
    if all(res_z_pass[z] >= 2 for z in SIZES):
        return "passes"
    if any(res_z_pass[z] == 0 and res_z_ctrl[z] >= 2 for z in SIZES):
        return "fails"
    return "inconclusive, no claim"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--c2p", action="append", default=[])
    ap.add_argument("--out")
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    assert sha(HERE.parent / "PN1" / "c2p_read.py") == C2P_READ_SHA, "c2p_read.py changed"
    M = list(csv.DictReader(open(P.MS1M)))
    F = list(csv.DictReader(open(P.FS1M)))
    assert {r["fam"] for r in F} <= {"af0", "ladder", "splice", "ffhq", "ffhq_lcomb"}
    assert {r["fam"] for r in M if r["fam"] == "ms1ffhq"} == {"ms1ffhq"}
    gate_ids = [r["id"] for r in F if r["fam"] in ("af0", "ffhq")]
    natp, natm, pairs, mpairs = P.holdout(M)
    rng = np.random.default_rng(P.RNG_G)
    boot = {z: [rng.integers(0, len(pairs[z]), len(pairs[z])) for _ in range(P.B_BOOT)] for z in SIZES}
    nets, gates, s3 = {}, {}, {}
    for arm in ARMS:
        for s in SEEDS:
            T = f"BB2_{arm}_s{s}"
            if a.mock:
                r = np.random.default_rng(s * 10 + len(arm))
                L = {}
                for row in M:
                    if row["fam"] == "ms1ffhq":
                        base = -3.0 if row["label"] == "0" else 1.0
                        shift = (1.0 if arm == "A" else 0.05) if row["strength"] else 0.0
                        L[row["id"]] = float(r.normal(base + shift * (row["label"] == "0"), 1.5))
                stored = {row["id"]: float(r.normal(0, 1)) for row in F}
                gates[T] = dict(passed=True, mock=True)
            else:
                L, new_g = {}, {}
                for c in a.c2p:
                    for fam in ("af0", "ffhq", "ms1ffhq"):
                        d = P.npz_from_tar(c, f"C2P_{T}_{fam}.npz")
                        if d is not None:
                            (L if fam == "ms1ffhq" else new_g).update(d)
                stored = P.npz_from_tar(f"{BB2R}/{T}.tar", "scores_eval.npz") or {}
                gates[T] = P.gate(new_g, stored, gate_ids)
            if stored:
                s3[T] = s3_reads(stored, F)
            need = set(natp) | set(natm) | {f"{i}_{z}" for z in SIZES for i in pairs[z]} | {f"{i}_{z}" for z in SIZES for i in mpairs[z]}
            if not need <= set(L) or not all(math.isfinite(L[i]) for i in need):
                gates[T]["holdout_complete"] = False
                continue
            if not gates[T]["passed"]:
                continue
            nets[(arm, s)] = P.net_stats(L, natp, natm, pairs, mpairs, boot)
    R = dict(mock=a.mock, gates=gates, per_network={f"{k[0]}_s{k[1]}": v for k, v in nets.items()}, printed_S3=s3)
    ctrl = {z: {s: bool(("A", s) in nets and nets[("A", s)][z]["d_flag"] >= 0.05 and nets[("A", s)][z]["d_mean_sd"] > 0)
                for s in SEEDS} for z in SIZES}
    R["A_control"] = ctrl
    c2 = {}
    for X in ("B", "Sb"):
        res = {}
        for z in SIZES:
            per = {}
            for s in SEEDS:
                if not ctrl[z][s] or (X, s) not in nets:
                    per[s] = False
                    continue
                x, A = nets[(X, s)][z], nets[("A", s)][z]
                per[s] = bool(x["d_flag"] <= A["d_flag"] / 3 and abs(x["d_mean_sd"]) <= A["d_mean_sd"] / 3
                              and x["d_flag"] <= 0.05 and x["d_flag_upper95"] <= 0.08)
            res[z] = dict(per_seed=per, n_pass=sum(per.values()), n_control=sum(ctrl[z].values()))
        res["verdict"] = count_c2({z: res[z]["n_pass"] for z in SIZES}, {z: res[z]["n_control"] for z in SIZES})
        c2[X] = res
    R["contrast2prime"] = c2
    h1 = {}
    for X in ("B", "Sb"):
        vals = {z: {s: nets[(X, s)][z]["d_mean_att_sd"] for s in SEEDS if (X, s) in nets} for z in SIZES}
        n_read = min(len(vals[z]) for z in SIZES)
        sup = any(sum(1 for v in vals[z].values() if v <= -0.20) >= 2 for z in SIZES)
        fal = all(sum(1 for v in vals[z].values() if v >= -0.10) >= 2 for z in SIZES)
        h1[X] = dict(values=vals, verdict="not read (too few seeds)" if n_read < 2 else
                     ("supported" if sup else ("falsified" if fal else "inconclusive")))
    R["H_new_1"] = h1
    clip = json.load(open(CLIP_C2P)) if CLIP_C2P.exists() and not a.mock else None
    R["clip_c2p"] = None if clip is None else dict(contrast2prime={X: clip["contrast2prime"][X]["verdict"] for X in ("B", "Sb")},
                                                    H_new_1={X: clip["H_new_1"][X]["verdict"] for X in ("B", "Sb")})
    sent = {}
    for X in ("B", "Sb"):
        cv = None if clip is None else clip["contrast2prime"][X]["verdict"]
        w = c2[X]["verdict"]
        if clip is None:
            sent[f"c2p_{X}"] = "CLIP C2P reading not available: BB2 counts printed only."
        elif cv != "passes":
            sent[f"c2p_{X}"] = f"No CLIP effect to repeat for {X} (CLIP contrast 2-prime: {cv}); second backbone printed only."
        elif w == "passes":
            sent[f"c2p_{X}"] = (f"The reduction of the storage reaction ({X}, at most a third of the plain recipe's and at most 5 "
                                f"points, at 61.2 px and at 112.7 px, on 300 unseen FFHQ persons) repeats on a second backbone "
                                f"(DINOv3 ViT-L/16, 2 of 3 seeds or more).")
        elif w == "uninformative":
            sent[f"c2p_{X}"] = f"Second backbone, {X}: contrast 2-prime uninformative (the plain arm's control is not met on DINOv3)."
        else:
            sent[f"c2p_{X}"] = (f"The reduction of the storage reaction ({X}) did not repeat on a second backbone ({w}): it is not "
                                f"shown to be independent of the CLIP backbone.")
        sent[f"H_new_1_{X}"] = f"Second backbone, {X}: H-new-1 (storage evasion) {h1[X]['verdict']} (printed beside CLIP's)."
    R["sentences"] = sent
    out = a.out or str(RES / "bb2_c2p_mock.json")
    json.dump(R, open(out, "w"), indent=1, default=lambda o: o if not isinstance(o, np.generic) else o.item())
    print(json.dumps(dict(contrast2prime={X: c2[X]["verdict"] for X in c2}, H_new_1={X: h1[X]["verdict"] for X in h1},
                          gates_failed=[k for k, v in gates.items() if not v.get("passed")], sentences=sent)))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
