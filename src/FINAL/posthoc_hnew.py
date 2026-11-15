"""Sealed MAD22 read (FINAL): H-new-1 to H-new-4 of posthoc_prereg_mad22_informed.md, run once each on the EXISTING
score files only. Label: "MAD22-informed, post-read, descriptive; no method choice follows".
Interpretations fixed before computing (written here at the time of coding, before any output):
- H-new-1: the EER-point threshold of a seed and family = the observed score t minimising |BPCER(t) - APCER(t)|
  (flagged = score > t; ties broken by the lower t). Ratio = BPCER(_08) / BPCER(_03); if BPCER(_03) = 0 and
  BPCER(_08) > 0 the ratio is +inf; if both are 0 the ratio is undefined (counts as neither >= 2 nor < 1.5).
  Per family: supported if ratio >= 2 on >= 4 of 5 seeds; falsified if ratio < 1.5 on >= 3 seeds; else inconclusive.
  Overall: supported if both families are supported; falsified if both are falsified; else inconclusive.
- H-new-2: per seed, EER of (S-form FaceMorpher morphs vs border-equalised native genuine) minus S EER, divided by
  (BE_S EER - S EER). A seed with BE_S - S <= 0.5 points is "not read". Supported if share >= 0.70 on >= 4 of 5 seeds;
  falsified if share < 0.40 on >= 3 seeds; else inconclusive (counts over all 5 seeds).
- H-new-3: not read (no per-frame landmark files exist for these MAD22 frames; the AF0 canonical mean hull is not a
  landmark file of these frames, and using it would change the registered read).
- H-new-4: Spearman over seeds 401-407 between the development landmark_combined AUC (401/402: tier1_a14/a14.json
  HN7 lcomb_auc; 403-407: tier_fs/fs.json seeds/<s>/Sb/lcomb_auc) and MAD22 mean2 history-matched EER (401/402: mean of
  sb_read.json Sb mad22_e7_eer; 403-407: final_read.json H Webmorph/OpenCV per seed).
  supported if rho <= -0.7; falsified if rho >= 0; else inconclusive.
  python3 -I posthoc_hnew.py --out experiments/FINAL_sealed-benchmark-read/posthoc_hnew_mad22_informed.json"""
import argparse
import json
import pathlib
import sys

import numpy as np
from scipy.stats import spearmanr

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import final_read as FR  # noqa: E402
import final_metrics as FM  # noqa: E402

ROOT = pathlib.Path("/home/narolski/smad-next")
O = pathlib.Path("/mnt/t7/smad_next/FINAL")
LABEL = "MAD22-informed, post-read, descriptive; no method choice follows"


def eer_threshold(sm, sg):
    best = None
    for t in np.unique(np.r_[sm, sg]):
        ap, bp = (sm <= t).mean(), (sg > t).mean()
        k = (abs(bp - ap), t)
        if best is None or k < best:
            best = k
    return float(best[1])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    args = argparse.Namespace(result=str(O / "results/FINAL_mad22_final2.tar"), pack=str(O / "FINAL_mad22_pack.tar"),
                              release_existing=str(O / "release_scores_existing.npz"),
                              selfmad=str(O / "selfmad/selfmad_mad22_scores.npz"), beststat=str(O / "beststat/beststat_mad22.npz"),
                              thresholds=str(ROOT / "experiments/FINAL_sealed-benchmark-read/final_thresholds.json"),
                              pins=str(HERE / "final_pins.json"))
    rd = FR.Read(args); rd.load()
    names = [n["name"] for n in rd.cfg["networks"]]
    pools = {n: rd.our_pools(lambda r, m=rd.scores[n]: m[r["id"]]) for n in names}
    out = dict(label=LABEL)
    # H-new-1
    h1 = {}
    for fam in ("OpenCV", "Webmorph"):
        rows = {}
        for n in names:
            sm, _, sg, _, ex = pools[n]["H"][fam]
            t = eer_threshold(sm, sg)
            b8 = float((sg[ex == "08"] > t).mean()); b3 = float((sg[ex == "03"] > t).mean())
            ratio = (b8 / b3) if b3 > 0 else (float("inf") if b8 > 0 else None)
            rows[n] = dict(threshold=t, bpcer_08=b8, bpcer_03=b3, ratio=ratio, n08=int((ex == "08").sum()), n03=int((ex == "03").sum()),
                           apcer_at_t=float((sm <= t).mean()))
        ge2 = sum(1 for v in rows.values() if v["ratio"] is not None and v["ratio"] >= 2)
        lt15 = sum(1 for v in rows.values() if v["ratio"] is not None and v["ratio"] < 1.5)
        verdict = "supported" if ge2 >= 4 else ("falsified" if lt15 >= 3 else "inconclusive")
        h1[fam] = dict(per_seed=rows, n_ratio_ge2=ge2, n_ratio_lt1_5=lt15, verdict=verdict)
    vs = [h1[f]["verdict"] for f in h1]
    h1["overall"] = "supported" if all(v == "supported" for v in vs) else ("falsified" if all(v == "falsified" for v in vs) else "inconclusive")
    out["H_new_1_expression"] = h1
    # H-new-2
    h2 = {}
    for n in names:
        S = pools[n]["S"]["FaceMorpher"]; BE = pools[n]["BE_S"]["FaceMorpher"]
        y = lambda a_, b_: np.r_[np.ones(len(a_)), np.zeros(len(b_))]
        e_s = FM.eer(np.r_[S[0], S[2]], y(S[0], S[2]))
        e_be = FM.eer(np.r_[BE[0], BE[2]], y(BE[0], BE[2]))
        e_mix = FM.eer(np.r_[S[0], BE[2]], y(S[0], BE[2]))
        rise = e_be - e_s
        h2[n] = dict(eer_S=e_s, eer_BE_S=e_be, eer_Smorph_BEgenuine=e_mix, rise_points=100 * rise,
                     share=None if rise <= 0.005 else (e_mix - e_s) / rise, read=bool(rise > 0.005))
    read = [v for v in h2.values() if v["read"]]
    ge = sum(1 for v in read if v["share"] >= 0.70); lt = sum(1 for v in read if v["share"] < 0.40)
    out["H_new_2_border_genuine_side"] = dict(per_seed=h2, n_read=len(read), n_share_ge_0_70=ge, n_share_lt_0_40=lt,
                                              verdict="supported" if ge >= 4 else ("falsified" if lt >= 3 else "inconclusive"))
    # H-new-3
    out["H_new_3_blend_energy"] = dict(verdict="not read", why="no per-frame landmark files exist for the MAD22 canonical frames (registered condition); the AF0 canonical mean hull is not one")
    # H-new-4
    a14 = json.load(open(ROOT / "experiments/PN1_protocol-network-first-tests/tier1_a14/a14.json"))
    fs = json.load(open(ROOT / "experiments/PN1_protocol-network-first-tests/tier_fs/fs.json"))
    sb = json.load(open(ROOT / "experiments/PN1_protocol-network-first-tests/tier1_sb/sb_read.json"))
    fr = json.load(open(ROOT / "experiments/FINAL_sealed-benchmark-read/final_read.json"))
    auc, eer2 = {}, {}
    for s in (401, 402):
        auc[s] = a14["HN7"]["lcomb_auc"][f"Sb_s{s}"]
        eer2[s] = float(np.mean(sb[f"s{s}"]["Sb"]["mad22_e7_eer"]))
    for s in (403, 404, 405, 406, 407):
        auc[s] = fs["seeds"][str(s)]["Sb"]["lcomb_auc"]
        n = f"PN1_Sb_s{s}"
        eer2[s] = 100 * float(np.mean([fr["cells"]["H"][f]["ours"][n]["eer"] for f in ("OpenCV", "Webmorph")]))
    ss = sorted(auc)
    rho = float(spearmanr([auc[s] for s in ss], [eer2[s] for s in ss]).correlation)
    out["H_new_4_dev_auc_predicts_rank"] = dict(seeds=ss, lcomb_auc={str(s): auc[s] for s in ss},
                                                mad22_mean2_H_eer_pct={str(s): eer2[s] for s in ss}, spearman=rho,
                                                verdict="supported" if rho <= -0.7 else ("falsified" if rho >= 0 else "inconclusive"),
                                                caveat="n = 7, low power; 401/402 from another block")

    def conv(x):
        if isinstance(x, dict):
            return {str(k): conv(v) for k, v in x.items()}
        if isinstance(x, float) and np.isinf(x):
            return "inf"
        return x
    pathlib.Path(a.out).write_text(json.dumps(conv(out), indent=1))
    print("HNEW written", a.out)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
