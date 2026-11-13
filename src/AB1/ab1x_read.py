"""AB1 border-crossed arm (Sbx): the single registered read (prereg_x.md). Development data only.

Inputs: AB1X_Sbx_s<seed>.tar (fit-job scores on ab1x_eval.csv) in --resx (default /mnt/t7/smad_next/AB1/x/results);
AB1Xrescore.tar (Sb and B at 408-412 rescored on the border rows and, as a job-path check, on landmark_combined, H100,
TF32 on) in the same folder; the AB1 tars of A, Sb, B (fit-job scores) in --res. Uses ab1_read.py and c2p_read.py
functions unchanged.
  python3 -I ab1x_read.py --out OUT.json
  python3 -I ab1x_read.py --mock --out MOCK.json"""
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
X_OVERLAY = "e5886e72622b618cb260689820efea861b63b061749db561d256ad57116f819c"
X_EVAL = pathlib.Path("/mnt/t7/smad_next/AB1/x/manifests/ab1x_eval.csv")
X_EVAL_SHA = "5257fb63f321612c39f8da6613989976450a68cd97c0b55d51667b554995d35f"
X_MANDIR = pathlib.Path("/mnt/t7/smad_next/AB1/x/manifests")
SEEDS = A.SEEDS


def load_x(tar):
    sv = (A.OVERLAY["AB1"], A.MANDIR, A.EVAL_SHA)
    A.OVERLAY["AB1"], A.MANDIR, A.EVAL_SHA = X_OVERLAY, X_MANDIR, X_EVAL_SHA
    try:
        return A.load(tar, "AB1", "Sbx")
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
    ap.add_argument("--resx", default="/mnt/t7/smad_next/AB1/x/results")
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--mock-sbx-border", type=float, default=0.0)   # mock only: shift of Sbx border logits
    a = ap.parse_args()
    assert A.sha(HERE / "ab1_read.py") == AB1_READ_SHA
    assert A.sha(HERE.parent / "PN1" / "c2p_read.py") == A.C2P_SHA
    assert A.sha(X_EVAL) == X_EVAL_SHA
    M = list(csv.DictReader(open(X_EVAL)))
    P = A.pools([r for r in M if r["fam"] != "border"])
    bc = [r for r in M if r["fam"] == "border" and r["rung"] == "R_cam_border" and r["role"] == "dev"]
    bf = [r for r in M if r["fam"] == "border" and r["rung"] == "R_ffhq_border"]
    assert len(bc) == 1582 and len(bf) == 2000
    fams = sorted({r["strength"] for r in bc})
    natp, natm, pairs, mpairs = C2.holdout(M)
    rng = np.random.default_rng(C2.RNG_G)
    boot = {z: [rng.integers(0, len(pairs[z]), len(pairs[z])) for _ in range(C2.B_BOOT)] for z in A.SIZES}
    R = dict(mock=a.mock, status={}, networks={})
    resx = pathlib.Path(a.resx)
    rs_tar = resx / "AB1Xrescore.tar"
    if not a.mock:
        ok_rs = rs_tar.exists() and (resx / "AB1Xrescore.tar.sha256").exists() and \
            A.sha(rs_tar) == (resx / "AB1Xrescore.tar.sha256").read_text().split()[0]
        R["status"]["rescore_tar"] = "verified" if ok_rs else "missing or unverified"
    nets = {}
    for arm in ("A", "Sb", "B", "Sbx"):
        for s in SEEDS:
            key = f"{arm}_s{s}"
            if a.mock:
                r = np.random.default_rng(s * 100 + sum(map(ord, arm)) + 11)
                x = {rr["id"]: float(r.normal(1.0 if rr["label"] == "1" else -2.0, 1.5)) for rr in M}
                for rr in M:                                     # mock: Sb reacts to borders; Sbx by --mock-sbx-border
                    if rr["fam"] == "border":
                        x[rr["id"]] += 1.0 if arm == "Sb" else (a.mock_sbx_border if arm == "Sbx" else 0.0)
                xb = x
                if arm in ("Sb", "B"):
                    R.setdefault("jobpath_check", {})[key] = dict(n=3000, p99=0.0, max=0.0, flips=0)
            elif arm == "Sbx":
                x, _, why = load_x(resx / f"AB1X_Sbx_s{s}.tar")
                if x is None:
                    R["status"][key] = why
                    continue
                xb = x                                          # border rows from its own fit job
            else:
                x, _, why = A.load(pathlib.Path(a.res) / f"AB1_{arm}_s{s}.tar", "AB1", arm)
                if x is None:
                    R["status"][key] = why
                    continue
                xb = None
                if arm in ("Sb", "B") and R["status"].get("rescore_tar") == "verified":
                    xb = npz_member(rs_tar, f"X_AB1_{arm}_s{s}_border.npz")
                    lc = npz_member(rs_tar, f"X_AB1_{arm}_s{s}_ffhq_lcomb.npz")
                    if lc:                                      # job-path check (binding, check F3)
                        d = np.array([abs(lc[i] - x[i]) for i in lc])
                        fl = int(sum((lc[i] > 0) != (x[i] > 0) for i in lc))
                        R.setdefault("jobpath_check", {})[key] = dict(n=len(d), p99=float(np.percentile(d, 99)), max=float(d.max()), flips=fl)
            st = {}
            if not all(math.isfinite(x.get(i, float("nan"))) for i in P["lc_m"] + P["lc_g"] + P["S3"]):
                R["status"][key] = "incomplete scores"
                continue
            st["lcomb_auc"] = C2.fauc([x[i] for i in P["lc_m"]], [x[i] for i in P["lc_g"]])
            st["S3"] = A.share(x, P["S3"])
            st["camera"] = A.share(x, P["camera"])
            st["ffhq_native_photo_flag"] = A.share(x, natp)
            st["c2p"] = C2.net_stats(x, natp, natm, pairs, mpairs, boot)
            if xb is not None and all(r["id"] in xb and math.isfinite(xb[r["id"]]) for r in bc + bf):
                st["border_cam_flag"] = float(np.mean([xb[r["id"]] > 0 for r in bc]))
                st["border_cam_count"] = int(sum(xb[r["id"]] > 0 for r in bc))
                st["border_cam_by_family"] = {f: float(np.mean([xb[r["id"]] > 0 for r in bc if r["strength"] == f])) for f in fams}
                st["border_ffhq_flag"] = float(np.mean([xb[r["id"]] > 0 for r in bf]))
            R["status"][key] = "read"
            nets[(arm, s)] = st
            R["networks"][key] = st
    ok = lambda *k: all(x in nets for x in k)
    hb = lambda arm, s: "border_cam_flag" in nets.get((arm, s), {})
    rd = [s for s in SEEDS if ok(("Sbx", s), ("Sb", s)) and hb("Sbx", s) and hb("Sb", s)]
    # control: Sb itself must flag > 2% of the border references (else nothing to remove)
    ctrl = {s: nets[("Sb", s)]["border_cam_count"] * 50 > len(bc) for s in rd}     # > 2% exactly, integer form
    sup = {s: bool(nets[("Sbx", s)]["border_cam_count"] * 50 <= len(bc)
                   and nets[("Sbx", s)]["border_cam_count"] * 2 <= nets[("Sb", s)]["border_cam_count"]      # check F1
                   and nets[("Sbx", s)]["lcomb_auc"] - nets[("Sb", s)]["lcomb_auc"] >= -0.02) for s in rd}
    fal = {s: bool(nets[("Sbx", s)]["border_cam_count"] >= nets[("Sb", s)]["border_cam_count"]
                   or nets[("Sbx", s)]["lcomb_auc"] - nets[("Sb", s)]["lcomb_auc"] < -0.02) for s in rd}
    n = len(rd)
    jp = R.get("jobpath_check", {})
    jp_ok = all(f"Sb_s{s}" in jp and jp[f"Sb_s{s}"]["max"] <= 0.01 and jp[f"Sb_s{s}"]["flips"] == 0 for s in rd)
    if n > 3 and not jp_ok:
        v = "job path unverified, no claim"
    elif n <= 3:
        v = "not read (too few seeds)"
    elif sum(ctrl.values()) <= 3:
        v = "uninformative (Sb flags at most 2% of border references on 2 or more seeds)"
    else:
        v = A.verdict(sum(sup.values()), sum(fal.values()), n)
    R["verdict_Hx1"] = dict(jobpath_ok=jp_ok, read_seeds=rd, control=ctrl, supported_on=sup, falsified_on=fal, verdict=v,
                            values={s: dict(Sbx_border=nets[("Sbx", s)]["border_cam_flag"], Sb_border=nets[("Sb", s)]["border_cam_flag"],
                                            B_border=nets[("B", s)].get("border_cam_flag") if ok(("B", s)) else None,
                                            lcomb_Sbx_minus_Sb=nets[("Sbx", s)]["lcomb_auc"] - nets[("Sb", s)]["lcomb_auc"]) for s in rd})
    # printed: C2P X rule for Sbx against A
    def xpass(s, z):
        if not ok(("A", s), ("Sbx", s)):
            return None
        Aa, x = nets[("A", s)]["c2p"][z], nets[("Sbx", s)]["c2p"][z]
        if not (Aa["d_flag"] >= 0.05 and Aa["d_mean_sd"] > 0):
            return None
        return bool(x["d_flag"] <= Aa["d_flag"] / 3 and abs(x["d_mean_sd"]) <= Aa["d_mean_sd"] / 3 and x["d_flag"] <= 0.05
                    and x["d_flag_upper95"] <= 0.08)
    R["printed_Sbx_c2p_pass"] = {z: {s: xpass(s, z) for s in SEEDS} for z in A.SIZES}
    json.dump(R, open(a.out, "w"), indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else str(o))
    print("H-x1:", v)
    print("not read:", {k: x for k, x in R["status"].items() if x != "read" and k != "rescore_tar"})


if __name__ == "__main__":
    main()
