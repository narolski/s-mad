"""AB1 second-engine arm (SbFM): the single registered read (prereg_fm.md). Development data only.

Inputs: AB1FM_SbFM_s<seed>.tar (fit-job scores on ab1x_eval.csv) in --resfm (default /mnt/t7/smad_next/AB1/fm/results);
the AB1 tars of A, B, Sb (fit-job scores) in --res; for the printed border rows of Sb and B, AB1Xrescore.tar in --resx.
ab1_read.py and c2p_read.py functions unchanged.
  python3 -I ab1fm_read.py --out OUT.json
  python3 -I ab1fm_read.py --mock [--mock-fm-gain 0.5] --out MOCK.json"""
import argparse
import csv
import importlib.util
import io
import json
import math
import pathlib
import tarfile

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ab1_read", HERE / "ab1_read.py")
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)
C2 = A.C2
AB1_READ_SHA = "74ecdf7a2ecb35812dcf4e5d5b9f5c3b1f095fc6846ae6f4813bfb28404d035b"
FM_OVERLAY = "e554b84f74e5de8791fddc168b99a7c46376ee48ab7902baf358ecbe668d8e47"
X_EVAL = pathlib.Path("/mnt/t7/smad_next/AB1/x/manifests/ab1x_eval.csv")
X_EVAL_SHA = "5257fb63f321612c39f8da6613989976450a68cd97c0b55d51667b554995d35f"
FM_MANDIR = pathlib.Path("/mnt/t7/smad_next/AB1/fm/manifests")
SEEDS = A.SEEDS


def load_fm(tar):
    sv = (A.OVERLAY["AB1"], A.MANDIR, A.EVAL_SHA)
    A.OVERLAY["AB1"], A.MANDIR, A.EVAL_SHA = FM_OVERLAY, FM_MANDIR, X_EVAL_SHA
    try:
        return A.load(tar, "AB1", "SbFM")
    finally:
        A.OVERLAY["AB1"], A.MANDIR, A.EVAL_SHA = sv


def npz_member(tar, name):
    with tarfile.open(tar) as t:
        m = [x for x in t.getmembers() if x.name.endswith(name)]
        if not m:
            return None
        z = np.load(io.BytesIO(t.extractfile(m[0]).read()))
        return dict(zip([str(i) for i in z["id"]], z["logit"].astype(float)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", default="/mnt/t7/smad_next/AB1/results")
    ap.add_argument("--resfm", default="/mnt/t7/smad_next/AB1/fm/results")
    ap.add_argument("--resx", default="/mnt/t7/smad_next/AB1/x/results")
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--mock-fm-gain", type=float, default=0.0)   # mock only: shift of SbFM morph logits on landmark_combined
    ap.add_argument("--mock-fm-r4", type=float, default=0.0)     # mock only: shift of SbFM test-ladder FaceMorpher R4 logits
    a = ap.parse_args()
    assert A.sha(HERE / "ab1_read.py") == AB1_READ_SHA
    assert A.sha(HERE.parent / "PN1" / "c2p_read.py") == A.C2P_SHA
    assert A.sha(X_EVAL) == X_EVAL_SHA
    M = list(csv.DictReader(open(X_EVAL)))
    P = A.pools([r for r in M if r["fam"] != "border"])

    def ids(**kw):
        return [r["id"] for r in M if all(r[k] == v for k, v in kw.items())]
    L = {}
    for role, tag in (("test", "T"), ("dev", "D")):
        for tool, t in (("opencv", "oc"), ("facemorpher", "fm")):
            for rung in ("R4", "R2w", "R3"):
                L[f"{tag}_{rung}_{t}"] = ids(fam="ladder", role=role, rung=rung, tool=tool, strength="")
    assert all(len(L[f"T_{r}_{t}"]) == 191 for r in ("R4", "R2w", "R3") for t in ("oc", "fm"))
    assert all(len(L[f"D_{r}_{t}"]) == 100 for r in ("R4", "R2w", "R3") for t in ("oc", "fm"))
    bc = [r["id"] for r in M if r["fam"] == "border" and r["rung"] == "R_cam_border" and r["role"] == "dev"]
    natp, natm, pairs, mpairs = C2.holdout(M)
    rng = np.random.default_rng(C2.RNG_G)
    boot = {z: [rng.integers(0, len(pairs[z]), len(pairs[z])) for _ in range(C2.B_BOOT)] for z in A.SIZES}
    R = dict(mock=a.mock, status={}, networks={})
    rs_tar = pathlib.Path(a.resx) / "AB1Xrescore.tar"
    nets = {}
    lcm = set(P["lc_m"])
    for arm in ("A", "B", "Sb", "SbFM"):
        for s in SEEDS:
            key = f"{arm}_s{s}"
            if a.mock:
                r = np.random.default_rng(s * 100 + sum(map(ord, arm)) + 13)
                x = {rr["id"]: float(r.normal(1.0 if rr["label"] == "1" else -2.0, 1.5)) for rr in M}
                if arm == "SbFM":
                    for i in lcm:
                        x[i] += a.mock_fm_gain
                    for i in L["T_R4_fm"]:
                        x[i] += a.mock_fm_r4
                xb = x
            else:
                if arm == "SbFM":
                    x, _, why = load_fm(pathlib.Path(a.resfm) / f"AB1FM_SbFM_s{s}.tar")
                    xb = x
                else:
                    x, _, why = A.load(pathlib.Path(a.res) / f"AB1_{arm}_s{s}.tar", "AB1", arm)
                    xb = npz_member(rs_tar, f"X_AB1_{arm}_s{s}_border.npz") if (arm in ("Sb", "B") and rs_tar.exists()) else None
                if x is None:
                    R["status"][key] = why
                    continue
            need = P["lc_m"] + P["lc_g"] + P["S3"] + [i for v in L.values() for i in v]
            if not all(math.isfinite(x.get(i, float("nan"))) for i in need):
                R["status"][key] = "incomplete scores"
                continue
            R["status"][key] = "read"
            sc = lambda k: [x[i] for i in L[k]]
            st = dict(lcomb_auc=C2.fauc([x[i] for i in P["lc_m"]], [x[i] for i in P["lc_g"]]),
                      S3=A.share(x, P["S3"]), camera=A.share(x, P["camera"]), ffhq_native_photo_flag=A.share(x, natp),
                      c2p=C2.net_stats(x, natp, natm, pairs, mpairs, boot))
            for t in ("oc", "fm"):
                st[f"D_{t}_R2w_placed"] = float(np.mean(np.array(sc(f"D_R2w_{t}")) > 0))
                st[f"D_{t}_R2w4_placed"] = float(np.mean([x[i] > 0 for i in ids(fam="ladder", role="dev", rung="R2w4", tool={"oc": "opencv", "fm": "facemorpher"}[t], strength="")]))
            for tag in ("T", "D"):
                for t in ("oc", "fm"):
                    st[f"{tag}_{t}_R4_vs_R2w"] = C2.fauc(sc(f"{tag}_R4_{t}"), sc(f"{tag}_R2w_{t}"))
                    st[f"{tag}_{t}_R4_vs_R3"] = C2.fauc(sc(f"{tag}_R4_{t}"), sc(f"{tag}_R3_{t}"))
                    st[f"{tag}_{t}_R3_placed"] = float(np.mean(np.array(sc(f"{tag}_R3_{t}")) > 0))
                    st[f"{tag}_{t}_R4_missed"] = float(np.mean(np.array(sc(f"{tag}_R4_{t}")) <= 0))
            if xb is not None and all(i in xb for i in bc):
                st["border_cam_flag"] = float(np.mean([xb[i] > 0 for i in bc]))
                st["border_source"] = "fit job" if arm == "SbFM" else "rescoring job 6314812 (printed only; other job)"
            nets[(arm, s)] = st
            R["networks"][key] = st
    ok = lambda *k: all(x in nets for x in k)

    def rule(read, sup, fal, ceiling=None):
        rd = [s for s in SEEDS if ok(("SbFM", s), ("Sb", s))]
        unt = [s for s in rd if ceiling is not None and nets[("Sb", s)][read] >= ceiling]   # check F4: untestable seeds
        rd = [s for s in rd if s not in unt]
        d = {s: nets[("SbFM", s)][read] - nets[("Sb", s)][read] for s in rd}
        out = dict(read_seeds=rd, untestable_seeds=unt, Sb_level={s: nets[("Sb", s)][read] for s in rd + unt}, SbFM_minus_Sb=d,
                   verdict=A.verdict(sum(sup(v) for v in d.values()), sum(fal(v) for v in d.values()), len(rd)))
        if len(d) >= 2:                                   # check F7: seed mean with t interval, printed only
            v = np.array(list(d.values())); t = {5: 2.7764451051977987, 4: 3.182446305284263, 3: 4.302652729911275, 2: 12.706204736174698}[len(v)]
            out["printed_seed_mean"] = dict(mean=float(v.mean()), half_width=float(t * v.std(ddof=1) / math.sqrt(len(v))))
        return out
    V = {}
    V["H_fm1_lcomb"] = rule("lcomb_auc", lambda v: v >= 0.02, lambda v: v < 0.005)
    V["H_fm2_test_fm_R4_vs_R2w"] = rule("T_fm_R4_vs_R2w", lambda v: v >= 0.02, lambda v: v < 0.005, ceiling=0.98)
    V["H_fm3_guard_test_oc_R4_vs_R2w"] = rule("T_oc_R4_vs_R2w", lambda v: v >= -0.02, lambda v: v < -0.02, ceiling=0.98)
    # printed engine-prior diagnostic (check improvement 3): development FaceMorpher R2w flags, SbFM and Sb
    V["printed_engine_prior"] = {s: {k: (nets[("SbFM", s)][k], nets[("Sb", s)][k]) for k in ("D_fm_R2w_placed", "D_fm_R2w4_placed", "ffhq_native_photo_flag")}
                                 for s in SEEDS if ok(("SbFM", s), ("Sb", s))}

    def xpass(s, z):
        if not ok(("A", s), ("SbFM", s)):
            return None
        Aa, xx = nets[("A", s)]["c2p"][z], nets[("SbFM", s)]["c2p"][z]
        if not (Aa["d_flag"] >= 0.05 and Aa["d_mean_sd"] > 0):
            return None
        return bool(xx["d_flag"] <= Aa["d_flag"] / 3 and abs(xx["d_mean_sd"]) <= Aa["d_mean_sd"] / 3 and xx["d_flag"] <= 0.05
                    and xx["d_flag_upper95"] <= 0.08)
    V["printed_SbFM_c2p_pass"] = {z: {s: xpass(s, z) for s in SEEDS} for z in A.SIZES}
    R["verdicts"] = V
    json.dump(R, open(a.out, "w"), indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else str(o))
    print(json.dumps({k: v["verdict"] for k, v in V.items() if isinstance(v, dict) and "verdict" in v}, indent=1))
    print("not read:", {k: x for k, x in R["status"].items() if x != "read"})


if __name__ == "__main__":
    main()
