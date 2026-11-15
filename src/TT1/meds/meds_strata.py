"""TT1-M post hoc follow-ups S1 and S2 (prereg_meds_block.md section 7, commit 104edc3). Zero GPU.
  python -I meds_strata.py -> experiments/TT1_.../meds_strata.json"""
import csv
import json
import pathlib
import sys

import numpy as np
from scipy.stats import beta, rankdata

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import tt1common as T  # noqa: E402

RES = pathlib.Path("/mnt/t7/smad_next/TT1/results")
SM = RES / "unpacked_m/TT1M_se1d/scores"
NB = 2000
NETS = [f"PN1_{a}_s{s}" for a in ("A", "B", "Sb") for s in (403, 404, 405, 406, 407)] + [f"PN1_Sp_s{s}" for s in (403, 404, 405)]
BINS = [1.2, 1.6, 2.0, 2.5, 3.0, 3.5, 4.0, 6.0]


def cp(k, n):
    return [0.0 if k == 0 else float(beta.ppf(.025, k, n - k + 1)), 1.0 if k == n else float(beta.ppf(.975, k + 1, n - k))]


def boot_w(groups, rng):
    ps = sorted(set(groups)); idx = {p: i for i, p in enumerate(ps)}
    m = rng.integers(0, len(ps), size=(NB, len(ps)))
    c = np.stack([np.bincount(m[b], minlength=len(ps)) for b in range(NB)])
    return c[:, [idx[g] for g in groups]].astype(float)


def spear(x, y):
    return float(np.corrcoef(rankdata(x), rankdata(y))[0, 1]) if len(x) >= 20 else None


def binof(e):
    for i in range(len(BINS) - 1):
        if BINS[i] <= e < BINS[i + 1] or (i == len(BINS) - 2 and e == BINS[-1]):
            return i
    return None


def main():
    meds = [r for r in csv.DictReader(open("/mnt/t7/smad_next/TT1/meds/meds_manifest.csv")) if r["aligned"] == "1"]
    for r in meds:
        r["size"] = "240" if (r["width"], r["height"]) == ("240", "240") else "other"
    tt = [r for r in T.tt1_rows() if r["primary"]]
    out = dict(label="post hoc (prereg_meds_block.md section 7)", S1={}, S2={})
    # S1
    rng = np.random.default_rng(20261126)
    strata = {}
    for sz in ("240", "other"):
        for part in ("MEDS-I", "MEDS-II", "all"):
            rs = [r for r in meds if r["size"] == sz and (part == "all" or r["part"] == part)]
            if rs:
                strata[f"{sz}|{part}"] = (rs, boot_w([r["person"] for r in rs], rng))
    L = {}
    for n in NETS:
        z = np.load(SM / f"{n}__meds.npz")
        L[n] = dict(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
        o = {}
        for k, (rs, W) in strata.items():
            x = np.array([L[n][r["id"]] for r in rs]); f = (x > 0).astype(float)
            bf = (W @ f) / W.sum(1)
            o[k] = dict(n=len(rs), persons=len({r["person"] for r in rs}), flag=float(f.mean()), k=int(f.sum()),
                        boot=[max(0.0, float(np.percentile(bf, 2.5))), float(np.percentile(bf, 97.5))], cp=cp(int(f.sum()), len(rs)),
                        rho_lap=spear(x, np.log([float(r["lap_var"]) for r in rs])),
                        rho_enlarge=spear(x, np.log([float(r["enlarge"]) for r in rs])))
        out["S1"][n] = o
    # S2
    rng2 = np.random.default_rng(20261127)
    m240 = [r for r in meds if r["size"] == "240"]
    mb = [binof(float(r["enlarge"])) for r in m240]
    tb = [binof(float(r["enlarge"])) for r in tt]
    keep_bins = sorted({b for b in mb if b is not None} & {b for b in tb if b is not None})
    m240k = [(r, b) for r, b in zip(m240, mb) if b in keep_bins]
    ttk = [(r, b) for r, b in zip(tt, tb) if b in keep_bins]
    dropped = len(m240) - len(m240k)
    wbin = np.array([sum(1 for _, b in m240k if b == kb) for kb in keep_bins], float); wbin /= wbin.sum()
    Wm = boot_w([r["person"] for r, _ in m240k], rng2)
    Wt = boot_w([r["person"] for r, _ in ttk], rng2)
    tbin = np.array([b for _, b in ttk])
    for n in NETS:
        sub = "sp" if "_Sp_" in n else "fs"
        d = RES / ("unpacked_sp/TT1_pn1fs_sp" if sub == "sp" else "unpacked_fs/TT1_A100_pn1fs_fs") / "scores" / f"{n}__tt1.npz"
        z = np.load(d); Lt = dict(zip(z["id"].tolist(), z["logit"].astype(float).tolist()))
        fm = np.array([L[n][r["id"]] > 0 for r, _ in m240k], float)
        ft = np.array([Lt[r["id"]] > 0 for r, _ in ttk], float)

        def rew(w):
            num = np.array([(w * ft)[tbin == kb].sum() for kb in keep_bins]); den = np.array([w[tbin == kb].sum() for kb in keep_bins])
            rates = np.where(den > 0, num / np.maximum(den, 1e-12), 0.0)
            return float((rates * wbin).sum()), rates
        tr, rates = rew(np.ones(len(ft)))
        diff = float(fm.mean() - tr)
        draws = []
        for b in range(NB):
            mm = float((Wm[b] * fm).sum() / Wm[b].sum()); tt_, _ = rew(Wt[b]); draws.append(mm - tt_)
        out["S2"][n] = dict(meds240_flag=float(fm.mean()), tt1_reweighted_flag=tr, diff=diff,
                            diff_ci=[float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))],
                            tt1_bin_rates={f"{BINS[kb]}-{BINS[kb + 1]}": float(r_) for kb, r_ in zip(keep_bins, rates)},
                            meds240_bin_rates={f"{BINS[kb]}-{BINS[kb + 1]}": float(fm[np.array([b for _, b in m240k]) == kb].mean()) for kb in keep_bins},
                            verdict="consistent with enlargement" if abs(diff) <= 0.05 else "differs")
    out["S2_info"] = dict(bins=BINS, kept_bins=[f"{BINS[kb]}-{BINS[kb + 1]}" for kb in keep_bins], meds240_weights=wbin.tolist(),
                          meds240_n=len(m240k), meds240_dropped=dropped, tt1_n=len(ttk),
                          tt1_n_per_bin=[int((tbin == kb).sum()) for kb in keep_bins],
                          meds240_n_per_bin=[sum(1 for _, b in m240k if b == kb) for kb in keep_bins])
    arm = {}
    for a in ("A", "B", "Sb"):
        vs = [out["S2"][f"PN1_{a}_s{s}"]["verdict"] for s in (403, 404, 405, 406, 407)]
        best = max(set(vs), key=vs.count)
        arm[a] = best if vs.count(best) >= 4 else f"mixed ({vs.count(best)} of 5 '{best}')"
    out["S2_arm"] = arm
    (T.RES / "meds_strata.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out["S2_info"], indent=0)); print(arm)
    for n in NETS:
        s1 = out["S1"][n]; s2 = out["S2"][n]
        print(n, "240", s1["240|all"]["k"], "/", s1["240|all"]["n"], "other", s1["other|all"]["k"], "/", s1["other|all"]["n"],
              "| S2 meds240 %.3f tt1rew %.3f diff %+.3f [%.3f, %.3f] %s" % (s2["meds240_flag"], s2["tt1_reweighted_flag"], s2["diff"], *s2["diff_ci"], s2["verdict"]))


if __name__ == "__main__":
    main()
