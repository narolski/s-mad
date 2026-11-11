"""PN1 tier 1 reader (prereg sections 6, 7 and amendments 1, 4). Reads the result tars of the eight fits (copied back to
/mnt/t7/smad_next/PN1/results/, sha256 checked), scores = logit without flip averaging.
  python3 -I tier1.py [--results /mnt/t7/smad_next/PN1/results]
Outputs experiments/PN1_.../tier1/<arm>_s<seed>.json (reads and marks), tier1/compare.json (P-g and A-B comparisons),
tier1_tables.md via report.py tier1.
"""
import argparse
import csv
import hashlib
import json
import os
import pathlib
import re
import sys
import tarfile

os.environ.setdefault("OMP_NUM_THREADS", "2")
import numpy as np  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pn1lib as K  # noqa: E402
import reads as RD  # noqa: E402

ARMS = ("A", "B", "Bn", "C")
SEEDS = (401, 402)


def eval_rows():
    cat = {r["id"]: r for r in K.catalog()}
    rows = []
    for r in csv.DictReader(open(K.PN1 / "manifests" / "pn1_eval.csv")):
        c = cat.get(r["id"])
        x = dict(r)
        x["neutral"] = r["neutral"] == "True"
        if c is not None:
            x.update(field=c.get("field", ""), persons=c["persons"], pool=c["pool"])
        else:                                    # AD4 benchmark rows: persons from the file name
            ids = re.findall(r"(\d{3})_\d{2}", pathlib.Path(r["path"]).name)
            x.update(field="", persons=tuple(sorted({"frll:" + i for i in ids})), pool=r["cell"])
            x["host"] = x["persons"][0] if x["persons"] else r["id"]
        rows.append(x)
    return rows


def load_result(tar):
    d = tar.parent / "unpacked"
    d.mkdir(parents=True, exist_ok=True)
    name = tar.name[:-4]
    if not (d / name).exists():
        with tarfile.open(tar) as t:
            t.extractall(d)
    z = np.load(d / name / "scores_eval.npz")
    zt = np.load(d / name / "scores_train.npz")
    info = json.load(open(d / name / "info.json"))
    return dict(zip([str(i) for i in z["id"]], z["logit"].astype(float))), zt, info


def gaps(zt, S, P):
    """amendment 4 item 3: mean training-row logit minus mean held-out logit of the same kind."""
    tr = {}
    for k, l in zip(zt["kind"], zt["logit"]):
        k = str(k)
        if "jpeg" in k:
            continue
        tr.setdefault(k, []).append(float(l))
    held = {"af0_photo": "V_photo", "af0_zero": "V_zero", "af0_half": "V_half", "af0_u50": "V_u50", "lad_R0": "D_R0",
            "lad_R2w": "D_R2w_opencv", "lad_R4": "D_R4_opencv", "af0_photo61": "V_photo_61", "lad_half": None,
            "af0_half61": None, "af0_u5061": "D_R4_opencv_61"}
    out = {}
    for k, v in tr.items():
        p = held.get(k)
        if p and P.get(p):
            h = RD.scores_of(S, P[p])
            out[k] = dict(train_mean=float(np.mean(v)), heldout=p, heldout_mean=float(h.mean()),
                          gap=float(np.mean(v) - h.mean()), n_train=len(v), n_held=len(h))
    return out


def wthr(s, w, alpha=0.05):
    o = np.argsort(s)
    s, w = s[o], w[o]
    tot = w.sum()
    above = tot - np.cumsum(w)           # weight strictly above s[i] (ties ignored: scores are continuous logits)
    ok = np.where(above / tot <= alpha)[0]
    return float(s[ok[0]])


def pg_bootstrap(SA, SX, P, B=2000, seed=20261111):
    """P-g: family-mean miss over the gating cells at τ_cam, network X minus network A, paired bootstrap; τ_cam refit
    per draw (development R0 by partner cycle, AF0 validation photos by person); attack cells by their units."""
    rng = np.random.default_rng(seed)
    cam = {p: P[p] for p in RD.CAMERA}
    cells = {c: P[c] for c in RD.GATING_ATTACK}

    def units(rows):
        return [RD.unit(r) if r["fam"] == "ladder" else (r["persons"][0] if r.get("persons") else r["id"]) for r in rows]
    U = {k: units(v) for k, v in list(cam.items()) + list(cells.items())}
    UI = {k: {u: i for i, u in enumerate(sorted(set(v)))} for k, v in U.items()}
    idx = {k: np.array([UI[k][u] for u in U[k]]) for k in U}

    def point(S, W):
        t = max(wthr(RD.scores_of(S, cam[p]), W[p]) for p in cam)
        ms = [float(np.sum(W[c] * (RD.scores_of(S, cells[c]) <= t)) / W[c].sum()) for c in cells]
        return float(np.mean(ms)), t

    W1 = {k: np.ones(len(U[k])) for k in U}
    a0, ta = point(SA, W1)
    x0, tx = point(SX, W1)
    d = []
    for _ in range(B):
        W = {}
        for k in U:
            n = len(UI[k])
            c = rng.multinomial(n, np.full(n, 1 / n))
            W[k] = c[idx[k]].astype(float)
            if W[k].sum() == 0:
                W[k] = np.ones(len(U[k]))
        d.append(point(SX, W)[0] - point(SA, W)[0])
    d = np.array(d)
    lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
    return dict(miss_A=a0, miss_X=x0, diff=x0 - a0, lo=lo, hi=hi, tau_cam_A=ta, tau_cam_X=tx,
                non_inferior_3pt=bool(hi <= 0.03), lowers_miss=bool(hi < 0))


def marks(R, RA):
    """tier-1 marks of section 7 as changed by amendment 4, for one network R (RA: the A network of the same seed)."""
    a = R["a"]
    m = {}
    m["P-a"] = all(isinstance(a[k].get("excess"), float) and a[k]["auc"] >= 0.95 and a[k]["excess"] >= 0.03
                   and a[k]["excess_lo"] > 0 for k in ("R2w_vs_R4_opencv", "R2w4_vs_R4_opencv"))
    b = [R["b"][k].get("auc") for k in ("R0_61_vs_R4_opencv", "R2w_61_vs_R4_opencv")]
    m["P-b_values"] = b
    m["P-b"] = all(x is not None and x >= 0.90 for x in b)
    m["P-b_middle"] = bool(all(x is not None for x in b) and min(b) >= 0.75 and min(b) < 0.90)
    st = RD.storage_marks(R)
    m["P-c"] = st["P-c"]["pass_"]
    m["P-c2"] = st["P-c2"]["pass_"] and st["P-c2_kernels"]["pass_"]
    m["storage"] = st
    m["P-d"] = R["d"].get("auc") is not None and R["d"]["auc"] >= 0.85
    if RA is not None:
        e = {f: (R["e"][f"{f}_e7"].get("eer_eer"), RA["e"][f"{f}_e7"].get("eer_eer")) for f in ("OpenCV", "Webmorph")}
        m["P-e_point_EERs_(X,A)"] = e
        m["P-e"] = all(x is not None and y is not None and x <= y + 3.0 for x, y in e.values())
    f61 = [R["fixed"][th].get("T_R4_opencv_61", {}).get("rate") for th in ("own", "cam")]
    m["P-f_miss_R4_61_(own,cam)"] = f61
    m["P-f"] = None if any(x is None for x in f61) else all(x <= 0.20 for x in f61)
    m["kill_parts"] = dict(R2w61_vs_R4_lt_075=bool(R["b"]["R2w_61_vs_R4_opencv"].get("auc", 1) < 0.75),
                           excess_lo_le0_R2w=bool(not (isinstance(a["R2w_vs_R4_opencv"].get("excess_lo"), float)
                                                       and a["R2w_vs_R4_opencv"]["excess_lo"] > 0)),
                           excess_lo_le0_R2w4=bool(not (isinstance(a["R2w4_vs_R4_opencv"].get("excess_lo"), float)
                                                        and a["R2w4_vs_R4_opencv"]["excess_lo"] > 0)))
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=str(K.PN1 / "results"))
    ap.add_argument("--out", default=str(K.RES / "tier1"))
    ap.add_argument("--boot", type=int, default=2000)
    a = ap.parse_args()
    rows = eval_rows()
    P = RD.pools(rows)
    import cert as CE
    z = np.load(K.AF0 / "cues" / "ar1.npz")
    cues = {str(i): c for i, c in zip(z["ids"], z["cues"])}
    z2 = np.load(K.PN1 / "cues" / "r2w4.npz")
    cues.update({str(i): c for i, c in zip(z2["ids"], z2["cues"])})
    c224 = CE.load_cues("c224")
    cues = {i: np.r_[v, c224[i]] for i, v in cues.items() if i in c224}
    names = [str(n) for n in z["names"]] + [n + "@224" for n in CE.PIX]
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    S, R, info = {}, {}, {}
    for arm in ARMS:
        for seed in SEEDS:
            t = pathlib.Path(a.results) / f"PN1_{arm}_s{seed}.tar"
            if not t.exists():
                continue
            h = hashlib.sha256(t.read_bytes()).hexdigest()
            assert h == (t.parent / (t.name + ".sha256")).read_text().split()[0], f"sha256 {t}"
            s, zt, inf = load_result(t)
            if not all(np.isfinite(v) for v in s.values()):
                info[(arm, seed)] = dict(refused="non-finite scores")
                continue
            S[(arm, seed)], info[(arm, seed)] = s, inf
            r = RD.all_reads(s, P, 0.0, (cues, names))
            r["gaps"] = gaps(zt, s, P)
            r["info"] = inf
            R[(arm, seed)] = r
    comp = {}
    for (arm, seed), r in R.items():
        r["marks"] = marks(r, R.get(("A", seed)) if arm != "A" else None)
        K.dump(r, out / f"{arm}_s{seed}.json")
        if arm != "A" and ("A", seed) in S:
            comp[f"{arm}_vs_A_s{seed}"] = pg_bootstrap(S[("A", seed)], S[(arm, seed)], P, B=a.boot)
    for seed in SEEDS:                     # amendment 4 item 4: C's gating miss against B's (JPEG mark)
        if ("B", seed) in S and ("C", seed) in S:
            comp[f"C_vs_B_s{seed}"] = pg_bootstrap(S[("B", seed)], S[("C", seed)], P, B=a.boot)
            st = RD.storage_marks(R[("C", seed)])
            comp[f"C_vs_B_s{seed}"]["C_jpeg50_le10_both_thresholds"] = st["jpeg50_le10_both"]
            comp[f"C_vs_B_s{seed}"]["C_jpeg_flags"] = st["jpeg_flags"]
    viol = {}
    for seed in SEEDS:
        if ("A", seed) in R:
            stA = RD.storage_marks(R[("A", seed)])
            cA = R[("A", seed)]["c"]["R0_to_R0_61"].get("shift_sd")
            viol[seed] = dict(storage_violation=bool(stA["A_violation_parts"]["R0_61_or_left_out_gt10_own"] or
                                                     stA["A_violation_parts"]["R0_61_or_left_out_gt10_cam"]),
                              jpeg50_violation=stA["jpeg50_gt10"], shift_sd=cA)
    comp["A_violation_by_seed"] = viol
    # amendment 5: reference row "standard recipe on released SMDD"
    rt = pathlib.Path(a.results) / "PN1_REF_smdd_m3.tar"
    if rt.exists():
        assert hashlib.sha256(rt.read_bytes()).hexdigest() == (rt.parent / (rt.name + ".sha256")).read_text().split()[0]
        d = rt.parent / "unpacked"
        if not (d / "PN1_REF_smdd_m3").exists():
            with tarfile.open(rt) as t:
                t.extractall(d)
        HIST = ["T_R0_61", "T_R0_112", "FRLL_amsl_e7", "FRLL_facemorpher_e7", "FRLL_opencv_e7", "FRLL_webmorph_e7",
                "MAD22_FaceMorpher_e7", "MAD22_OpenCV_e7", "MAD22_Webmorph_e7", "FRLL_bona_blur1", "FRLL_bona_resample50"]
        JPG = ["FRLL_bona_jpeg90", "FRLL_bona_jpeg70", "FRLL_bona_jpeg50"]
        ref = {}
        for nd in sorted((d / "PN1_REF_smdd_m3").glob("a12_*")):
            z = np.load(nd / "scores_eval.npz")
            s_ = dict(zip([str(i) for i in z["id"]], z["logit"].astype(float)))
            r = RD.all_reads(s_, P, 0.0, (cues, names))
            K.dump(r, out / f"ref_{nd.name}.json")
            q = {}
            for th in ("own", "cam"):
                fx = r["fixed"][th]
                q[th] = dict(flags_history={p: round(fx[p]["rate"], 4) for p in HIST if p in fx},
                             flags_jpeg={p: round(fx[p]["rate"], 4) for p in JPG if p in fx},
                             any_gt10=bool(any(fx[p]["rate"] > 0.10 for p in HIST + JPG if p in fx)),
                             miss_gating={c: round(fx[c]["rate"], 4) for c in RD.GATING_ATTACK if c in fx},
                             family_mean_miss=fx["_family_mean_miss_gating"]["mean"])
            ref[nd.name] = q
        comp["reference_standard_recipe_smdd"] = ref
    comp["networks_read"] = sorted(f"{a}_s{s}" for a, s in R)
    comp["networks_refused"] = {f"{a}_s{s}": v for (a, s), v in info.items() if "refused" in v}
    K.dump(comp, out / "compare.json")
    print(json.dumps({k: v for k, v in comp.items()}, indent=1, default=str)[:4000])


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
