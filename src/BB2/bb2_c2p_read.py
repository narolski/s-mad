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
sys.path.insert(0, str(HERE))
import c2p_read as P  # noqa: E402  (registration C2P reader, unchanged)
import bb2_read as BR  # noqa: E402  (BB2 read-seed rule, seed mode, training accuracy)
import tarfile  # noqa: E402

C2P_READ_SHA = "45e72914d960214131a5b4a11aefd2e301a2236e908d77d20d94136c1d7d5840"
BB2R = "/mnt/t7/smad_next/BB2/results"
RES = HERE.parents[1] / "experiments" / "BB2_second-backbone"
CLIP_C2P = HERE.parents[1] / "experiments" / "PN1_protocol-network-first-tests" / "c2p_read.json"
ARMS, SIZES = ("A", "B", "Sb"), P.SIZES
ADEQ = BR.ADEQ


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


def count_c2_five(res_z_pass, res_z_ctrl):
    """Amendment 2, five seeds: C2P.3's own rule (passes >= 4 of 5 at both sizes; fails <= 1 at a size with A's control
    met on >= 4; uninformative if A's control is met on <= 3 at either size; otherwise inconclusive)."""
    if any(res_z_ctrl[z] <= 3 for z in SIZES):
        return "uninformative"
    if all(res_z_pass[z] >= 4 for z in SIZES):
        return "passes"
    if any(res_z_pass[z] <= 1 and res_z_ctrl[z] >= 4 for z in SIZES):
        return "fails"
    return "inconclusive, no claim"


def check_c2p_tar(tar, fit_gpu):
    """Review F6: the tar holds only the expected score files and logs, TF32 is on, and the GPU model equals the fits'."""
    with tarfile.open(tar) as t:
        names = [m.name for m in t.getmembers() if m.isfile()]
        base = [n.split("/")[-1] for n in names]
        bad = [b for b in base if not ((b.startswith("C2P_BB2_") and b.endswith(("_af0.npz", "_ffhq.npz", "_ms1ffhq.npz")))
                                       or b in ("env.txt", "gpu.txt", "rescore.log", "tasks.txt", "precision.txt"))]
        pm = [m for m in t.getmembers() if m.name.endswith("precision.txt")]
        prec = None
        if pm:
            line = [x for x in t.extractfile(pm[0]).read().decode().splitlines() if x.startswith("BB2_PRECISION")]
            prec = json.loads(line[-1].split(" ", 1)[1]) if line else None
        env = t.extractfile([m for m in t.getmembers() if m.name.endswith("env.txt")][0]).read().decode()
        gpu = t.extractfile([m for m in t.getmembers() if m.name.endswith("gpu.txt")][0]).read().decode()
    return dict(unexpected_members=bad, precision=prec,
                gpu_asserted=bool(prec and prec.get("gpu_ok") and prec.get("gpu") == "NVIDIA H100"),
                tf32_effective=bool(prec and prec.get("matmul_rel_err_vs_fp64", 0) > 1e-5), wrapper_pinned=("0d0b6b6fb5ebc4d5bdbe15384fcd00e13c0756785ed22743893186e68245d8d5" in env
                                                        and "6f6eede71c6d9a895199dabc8bc90b882adb25f5f91cd2fcc676ebe7a380b51e" in env),
                gpu=gpu.strip(), fit_gpu=sorted(fit_gpu), same_gpu_model=all(g in gpu for g in fit_gpu) if fit_gpu else None)


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
    ap.add_argument("--five", action="store_true", help="mock only: five seeds")
    ap.add_argument("--clip-json", default=None, help="amendment 3: the CLIP C2P-R reading file, if C2P-R was "
                    "registered and read before this BB2 read; otherwise the first C2P reading (uninformative) is used")
    a = ap.parse_args()
    assert sha(HERE.parent / "PN1" / "c2p_read.py") == C2P_READ_SHA, "c2p_read.py changed"
    M = list(csv.DictReader(open(P.MS1M)))
    F = list(csv.DictReader(open(P.FS1M)))
    assert {r["fam"] for r in F} <= {"af0", "ladder", "splice", "ffhq", "ffhq_lcomb"}
    assert sum(r["fam"] == "ms1ffhq" for r in M) == 1480, "hold-out row count"
    gate_ids = [r["id"] for r in F if r["fam"] in ("af0", "ffhq")]
    five = a.five
    SEEDS, MODE = ((BR.SEEDS5, "five") if five else (BR.SEEDS3, "three")) if a.mock else BR.frozen_mode(pathlib.Path(BB2R))
    if not a.mock:      # amendment 2 fix 3: the C2P tar must have scored exactly the frozen read set
        want = {f"BB2_{arm}_s{s}" for arm in ARMS for s in SEEDS}
        for c in a.c2p:
            with tarfile.open(c) as t:
                got = set(t.extractfile([m for m in t.getmembers() if m.name.endswith("tasks.txt")][0]).read().decode().split())
            if got != want:
                sys.exit(f"refused: {c} scored {sorted(got)}, the frozen read set is {sorted(want)}")
    NMIN = 2 if MODE == "three" else 4
    natp, natm, pairs, mpairs = P.holdout(M)
    rng = np.random.default_rng(P.RNG_G)
    boot = {z: [rng.integers(0, len(pairs[z]), len(pairs[z])) for _ in range(P.B_BOOT)] for z in SIZES}
    nets, gates, s3, acc, readseed, fit_gpu = {}, {}, {}, {}, {}, set()
    for s in SEEDS:      # BB2 read-seed rule (prereg section 6): verified tars, finite logits, no non-finite train loss
        if a.mock:
            readseed[s] = True
            for arm in ARMS:
                acc[(arm, s)] = 0.9
            continue
        S = {arm: BR.F.load(pathlib.Path(BB2R) / f"BB2_{arm}_s{s}.tar") for arm in ARMS}
        INF = {arm: BR.info_of(pathlib.Path(BB2R) / f"BB2_{arm}_s{s}.tar") for arm in ARMS if S[arm] is not None}
        readseed[s] = all(v is not None for v in S.values()) and not any(i["train_log_nonfinite"] for i in INF.values())
        for arm in INF:
            acc[(arm, s)] = INF[arm]["train_acc_rule0"] or 0.0
            gp = pathlib.Path(BB2R) / "unpacked" / f"BB2_{arm}_s{s}" / "gpu.txt"
            g = gp.read_text().strip().splitlines()[-1].split(",")[2].strip() if gp.exists() else None
            fit_gpu.add(g)
            if g != "NVIDIA H100":      # amendment 3: fits must have run on the registered GPU model
                readseed[s] = False
    for arm in ARMS:
        for s in SEEDS:
            T = f"BB2_{arm}_s{s}"
            if not readseed[s]:
                gates[T] = dict(passed=False, reason="seed not read (section 6)")
                continue
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
    R = dict(mock=a.mock, seed_mode=MODE, seeds=list(SEEDS), read_seeds=[s for s in SEEDS if readseed[s]],
             train_acc_rule0={f"{k[0]}_s{k[1]}": v for k, v in acc.items()}, gates=gates, per_network={f"{k[0]}_s{k[1]}": v for k, v in nets.items()}, printed_S3=s3)
    ctrl = {z: {s: bool(("A", s) in nets and nets[("A", s)][z]["d_flag"] >= 0.05 and nets[("A", s)][z]["d_mean_sd"] > 0)
                for s in SEEDS} for z in SIZES}
    R["A_control"] = ctrl
    c2 = {}
    for X in ("B", "Sb"):
        res = {}
        for z in SIZES:
            per = {}
            for s in SEEDS:
                if not ctrl[z][s] or (X, s) not in nets or acc.get((X, s), 0) < ADEQ or acc.get(("A", s), 0) < ADEQ:
                    per[s] = False      # review F2: X and A must both meet the training-adequacy rule on that seed
                    continue
                x, A = nets[(X, s)][z], nets[("A", s)][z]
                per[s] = bool(x["d_flag"] <= A["d_flag"] / 3 and abs(x["d_mean_sd"]) <= A["d_mean_sd"] / 3
                              and x["d_flag"] <= 0.05 and x["d_flag_upper95"] <= 0.08)
            res[z] = dict(per_seed=per, n_pass=sum(per.values()), n_control=sum(ctrl[z].values()),
                          miss_native={s: nets[(X, s)]["miss_native"] for s in SEEDS if (X, s) in nets})
        cf = count_c2 if MODE == "three" else count_c2_five
        res["verdict"] = cf({z: res[z]["n_pass"] for z in SIZES}, {z: res[z]["n_control"] for z in SIZES})
        c2[X] = res
    R["contrast2prime"] = c2
    h1 = {}
    for X in ("B", "Sb"):
        vals = {z: {s: nets[(X, s)][z]["d_mean_att_sd"] for s in SEEDS if (X, s) in nets} for z in SIZES}
        n_read = min(len(vals[z]) for z in SIZES)
        sup = any(sum(1 for v in vals[z].values() if v <= -0.20) >= NMIN for z in SIZES)
        fal = all(sum(1 for v in vals[z].values() if v >= -0.10) >= NMIN for z in SIZES)
        h1[X] = dict(values=vals, verdict="not read (too few seeds)" if n_read < NMIN else
                     ("supported" if sup else ("falsified" if fal else "inconclusive")))
    R["H_new_1"] = h1
    cj = pathlib.Path(a.clip_json) if a.clip_json else CLIP_C2P
    clip = json.load(open(cj)) if cj.exists() and not a.mock else None
    R["clip_c2p_json"] = str(cj) if clip is not None else None
    R["clip_c2p_json_sha256"] = sha(cj) if clip is not None else None
    if not a.mock:
        R["c2p_tar_checks"] = {c: check_c2p_tar(c, fit_gpu) for c in a.c2p}
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
                                f"(DINOv3 ViT-L/16, {'2 of 3 seeds, a lower bar than CLIP' + chr(39) + 's 4 of 5' if MODE == 'three' else '4 of 5 seeds'}).")
        elif w == "uninformative":
            sent[f"c2p_{X}"] = f"Second backbone, {X}: contrast 2-prime uninformative (the plain arm's control is not met on DINOv3)."
        else:
            sent[f"c2p_{X}"] = (f"The reduction of the storage reaction ({X}) did not repeat on a second backbone ({w}): it is not "
                                f"shown to be independent of the CLIP backbone.")
        sent[f"H_new_1_{X}"] = f"Second backbone, {X}: H-new-1 (storage evasion) {h1[X]['verdict']} (printed beside CLIP's)."
    R["sentences"] = sent
    out = a.out or str(RES / f"bb2_c2p_mock_{MODE}.json")
    json.dump(R, open(out, "w"), indent=1, default=lambda o: o if not isinstance(o, np.generic) else o.item())
    print(json.dumps(dict(contrast2prime={X: c2[X]["verdict"] for X in c2}, H_new_1={X: h1[X]["verdict"] for X in h1},
                          gates_failed=[k for k, v in gates.items() if not v.get("passed")], sentences=sent)))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
