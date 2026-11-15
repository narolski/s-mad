"""CB1: additions requested by the results review (13 Nov, about 04:00). Existing score files only.
(1) per arm: A12-BR-style EER (E7 genuine pool, flip-averaged probability, old MAD22 subset rows = the A12 ledger's
    definition) beside the CB1 registered EER (native pool, logit, corrected MAD22); also A12-style on corrected MAD22;
(2) PW-MAD M5 with all 8 seeds and M4 with all 5 seeds (C1 exclusions undone), registered rule;
(3) AUC per arm and family (native pool, logit; mean over seeds), marking inverted rankings (AUC < 0.5);
(4) C2 maximum and minimum Kendall over all networks.
  python3 -I review_addons.py OUT_DIR"""
import csv, json, math, pathlib, re, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from analyse_cnn import w_eer, FAM, GATEFAM, PUB
from scipy.stats import t as tdist, rankdata

out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
rows = list(csv.DictReader(open("/mnt/t7/smad_next/CB1/manifests/cb1_cnn_images_v2.csv")))
idx = {}
for i, r in enumerate(rows):
    idx.setdefault((r["bench"], r["pool"], r["family"], int(r["label"])), []).append(i)
S = pathlib.Path("/mnt/t7/smad_next/CB1/scores_cnn")
ARMS = {"A12BR_M1": ("Inception-MAD", "es"), "A12BR_M2": ("MorphHRNet", "es"), "A12BR_M5": ("PW-MAD", "es"),
        "A12BR_M6": ("OrthoMAD", "es"), "A12BR_M8": ("MixFaceNet-MAD", "es"), "A12BR_M8O": ("MixFaceNet-MAD", "es"),
        "A12BR_M4": ("SelfMAD", "es"), "A45_incepofc": ("Inception-MAD", "last"), "A45_hrnetw18": ("MorphHRNet", "last")}


def cell(bench, fam, pool):
    g = idx[(bench, "native", "bona", 0)] if pool == "native" else idx[(bench, "e7", fam, 0)]
    return np.array(g), np.array(idx[(bench, "native", fam, 1)])


def auc(s, y):
    r = rankdata(s); n1 = (y == 1).sum(); n0 = (y == 0).sum()
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


res_style, res_auc, res_all = [], [], []
for arm, (method, ck) in ARMS.items():
    nets = sorted(p.stem for p in S.glob(f"{arm}_s*_{ck}.npz"))
    Z = {n: np.load(S / f"{n}.npz") for n in nets}
    def mean5(bench, pool, key, fams):
        per = []
        for n in nets:
            v = []
            for fam in fams:
                g, m = cell(bench, fam, pool)
                s = Z[n][key].astype(float); sel = np.r_[g, m]
                v.append(100 * w_eer(s[sel], np.r_[np.zeros(len(g)), np.ones(len(m))]))
            per.append(np.mean(v))
        return np.array(per)
    a12_old = mean5("gate", "e7", "score", GATEFAM)
    a12_new = mean5("mad22c", "e7", "score", FAM["mad22c"])
    cb1_new = mean5("mad22c", "native", "logit_noTTA", FAM["mad22c"])
    fr_a12 = mean5("frllm", "e7", "score", FAM["frllm"])
    fr_cb1 = mean5("frllm", "native", "logit_noTTA", FAM["frllm"])
    res_style.append(dict(arm=arm, ckpt=ck, n=len(nets),
                          mad22_A12style_oldsubset_e7_flip=round(a12_old.mean(), 2),
                          mad22_A12style_corrected_e7_flip=round(a12_new.mean(), 2),
                          mad22_CB1_corrected_native_logit=round(cb1_new.mean(), 2),
                          frll_A12style_e7_flip=round(fr_a12.mean(), 2), frll_CB1_native_logit=round(fr_cb1.mean(), 2)))
    # all-seed registered rule (no C1 exclusion)
    for bench, per in (("mad22c", cb1_new), ("frllm", fr_cb1)):
        pub = PUB[method][bench] if method != "SelfMAD" else None
        rec = dict(arm=arm, ckpt=ck, bench=bench, n=len(nets), mean=round(per.mean(), 2))
        if pub is not None:
            pm = float(np.mean(pub)); M = max(0.3 * pm, 1.5); d = per - pm
            h = tdist.ppf(0.95, len(d) - 1) * d.std(ddof=1) / math.sqrt(len(d))
            lo, hi = d.mean() - h, d.mean() + h
            rd = ("reproduces" if (lo > -M and hi < M) else "does not reproduce (worse)" if lo > M else
                  "does not reproduce (better)" if hi < -M else "inconclusive")
            rec.update(published=round(pm, 2), delta=round(d.mean(), 2), lo=round(lo, 2), hi=round(hi, 2), M=round(M, 2), reading=rd)
        res_all.append(rec)
    for bench in ("mad22c", "frllm"):
        for fam in FAM[bench]:
            g, m = cell(bench, fam, "native"); sel = np.r_[g, m]; y = np.r_[np.zeros(len(g)), np.ones(len(m))]
            a = np.mean([auc(Z[n]["logit_noTTA"].astype(float)[sel], y) for n in nets])
            res_auc.append(dict(arm=arm, ckpt=ck, bench=bench, family=fam, auc_seed_mean=round(float(a), 3),
                                inverted=bool(a < 0.5)))
for name, data in (("a12style_vs_cb1.csv", res_style), ("all_seed_readings.csv", res_all), ("auc_native.csv", res_auc)):
    with open(out / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list({k: 0 for d in data for k in d})); w.writeheader(); w.writerows(data)
c2 = []
for p in ("es", "last", "a45"):
    c2 += list(csv.DictReader(open(f"/mnt/t7/smad_next/CB1/analysis_cnn/{p}/c2_pipeline_shift.csv")))
json.dump(dict(n=len(c2), max_median_abs_logit=max(float(r["median_abs_logit_diff"]) for r in c2),
               min_kendall=min(float(r["kendall"]) for r in c2)), open(out / "c2_summary.json", "w"), indent=1)
print(open(out / "c2_summary.json").read())
for r in res_style: print(r)
for r in res_all: print(r)
