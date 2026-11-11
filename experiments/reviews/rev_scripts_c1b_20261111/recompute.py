"""Independent recomputation of C1b key numbers (reviewer; own code, no import from src/C1b)."""
import csv, re, sys, hashlib
import numpy as np
MC = "/home/narolski/mambamorph-code/"
S = MC + "smadcvpr_runs/A12_scored/"
EVAL = MC + "smadcvpr_data/manifests/eval.csv"
print("eval.csv sha256", hashlib.sha256(open(EVAL, "rb").read()).hexdigest())
rows = [r for r in csv.DictReader(open(EVAL)) if r["variant"] == "orig"]
FR = ["amsl", "facemorpher", "opencv", "stylegan", "webmorph"]
DI = ["dim_a", "dim_c", "fast_dim", "fast_dim_ode", "greedy_dim", "greedy_dim_s"]

def gen(setname, fam):
    out = {}
    for r in rows:
        if r["set"] == setname and r["family"] == fam and r["label"] == "0":
            m = re.match(r"^(\d{3})_(\d{2})_", r["path"].rsplit("/", 1)[1])
            out[(m.group(1), m.group(2))] = r["id"]
    return out

def morphs(setname, fam):
    return [r["id"] for r in rows if r["set"] == setname and r["family"] == fam and r["label"] == "1"]

def eer_std(b, m):
    """EER by threshold sweep: flag if score >= t; point where |APCER-BPCER| minimal; mean of the two (%)."""
    t = np.unique(np.r_[b, m])
    bs, ms = np.sort(b), np.sort(m)
    bp = 1 - np.searchsorted(bs, t, "left") / len(bs)
    ap = np.searchsorted(ms, t, "left") / len(ms)
    i = np.argmin(np.abs(bp - ap))
    return 100 * (bp[i] + ap[i]) / 2

def bpcer_at(b, m, a):
    ms = np.sort(m)
    # largest threshold t (a morph score) with APCER(t)=share morphs < t <= a
    k = int(np.floor(a * len(ms) + 1e-9))
    # APCER at t=ms[k] is (#morphs < ms[k])/n <= k/n
    t = ms[min(k, len(ms) - 1)]
    return 100 * np.mean(b >= t)

def auc(pos, neg):
    from scipy.stats import rankdata
    r = rankdata(np.r_[pos, neg])
    return (r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))

DETS = [("ViT-L/14 release", "A12REL/madation_vitl14/scores_eval.npz", "score_noTTA"),
        ("FE ViT-B/16 release", "A12REL/madation_fe_vitb16/scores_eval.npz", "score_noTTA"),
        ("M3L s1 last", "A12BR/a12_clip_vitl14_madation_r224_d0_train90_none_lr3.33e-06_s1_r/scores_eval_last.npz", "score"),
        ("M3L s3 last", "A12BR/a12_clip_vitl14_madation_r224_d0_train90_none_lr3.33e-06_s3_r/scores_eval_last.npz", "score"),
        ("M3 s1 last", "A12BR/a12_clip_vitb16_madation_r224_d0_train90_none_lr3.33e-06_s1_r/scores_eval_last.npz", "score"),
        ("M3 s4 last", "A12BR/a12_clip_vitb16_madation_r224_d0_train90_none_lr3.33e-06_s4_r/scores_eval_last.npz", "score"),
        ("M3 s5 last", "A12BR/a12_clip_vitb16_madation_r224_d0_train90_none_lr3.33e-06_s5_r/scores_eval_last.npz", "score")]
if len(sys.argv) > 1 and sys.argv[1] == "alt":
    DETS = [(n + " [alt key]", f, "score" if k == "score_noTTA" else "score_noTTA") for n, f, k in DETS]
GF, GM = gen("frllm", "frll_bona"), gen("mordiff", "mordiff_bona")
GD = gen("dim", "dim_bona")
P = sorted({p for p, e in GF})
assert len(P) == 102 and len(GF) == 204
for name, f, key in DETS:
    z = np.load(S + f, allow_pickle=False)
    assert str(z["manifest_sha256"]).startswith("86d055d3")
    sc = dict(zip(z["id"].tolist(), z[key].astype(np.float64)))
    print(f"\n=== {name}  ({f}, key {key})")
    for lab, G in (("frll frames", GF), ("dim frames", GD), ("mordiff frames", GM)):
        n3 = np.array([sc[G[(p, "03")]] for p in P]); n8 = np.array([sc[G[(p, "08")]] for p in P])
        k = int((n3 > n8).sum()); ties = int((n3 == n8).sum())
        rng = np.random.default_rng(1)
        ind = (n3 > n8) + 0.5 * (n3 == n8)
        bs = [ind[rng.integers(0, 102, 102)].mean() for _ in range(5000)]
        print(f"  {lab}: neutral>smiling {k}/102 (ties {ties}) AUC_wp {ind.mean():.3f} [{np.percentile(bs,2.5):.3f},{np.percentile(bs,97.5):.3f}]  pooled AUC {auc(n3,n8):.3f}  median score neu {np.median(n3):.4f} smi {np.median(n8):.4f}  mean diff {np.mean(n3-n8):+.4f}")
    ch = []
    for st, fams, G in (("frllm", FR, GF), ("dim", DI, GD)):
        for fam in fams:
            m = np.array([sc[i] for i in morphs(st, fam)])
            ball = np.array([sc[v] for v in G.values()])
            bneu = np.array([sc[v] for (p, e), v in G.items() if e == "03"])
            bsmi = np.array([sc[v] for (p, e), v in G.items() if e == "08"])
            e = [eer_std(x, m) for x in (ball, bneu, bsmi)]
            b5 = [bpcer_at(x, m, 0.05) for x in (ball, bneu, bsmi)]
            ch.append(e[1] - e[0])
            print(f"  {st}/{fam:13s} n_m {len(m):4d} EER all/neu/smi {e[0]:5.1f} / {e[1]:5.1f} / {e[2]:5.1f}  d {e[1]-e[0]:+5.1f}   BPCER@5 {b5[0]:5.1f} -> {b5[1]:5.1f}")
    print(f"  mean EER change neutral-only minus all over 11 cells: {np.mean(ch):+.2f}")
    m = np.array([sc[i] for i in morphs("mordiff", "mordiff")])
    e = [eer_std(np.array([sc[v] for (p, ex), v in GM.items() if ex in sel]), m) for sel in (("03", "08"), ("03",), ("08",))]
    print(f"  mordiff EER all/neu/smi {e[0]:.1f} / {e[1]:.1f} / {e[2]:.1f}")
