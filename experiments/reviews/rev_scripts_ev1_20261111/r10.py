import sys, csv, re, numpy as np, pathlib, collections, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lib import *
R = rows_eval(); ids = [r["id"] for r in R]; dev = sel(R, "devbona","devbona","orig","0")
orig = sel(R,"frllm","frll_bona","orig","0")
G = {"orig": orig, "MorDIFF align": sel(R,"mordiff","mordiff_bona","orig","0")}
for v in ("jpeg90","jpeg70","resample50"): G[v] = sel(R,"frllm","frll_bona",v,"0")
for f in FAMS: G["E7 "+f] = sel(R, SETOF[f], f, "resmatch", "0")
ICAO_OK = ["orig","jpeg90","jpeg70","resample50","E7 amsl","E7 facemorpher","E7 opencv","E7 stylegan","E7 webmorph"]   # effective inter-eye distance >= 100 px, full frame
M = {f: sel(R, SETOF[f], f, "orig", "1") for f in FAMS}
rxab = re.compile(r"^(\d{3})_(\d{3})_"); rxm = re.compile(r"^morph_(\d{3})_\d{2}_and_(\d{3})_")
def pers(i):
    n = R[i]["name"]
    if R[i]["label"] == "0": return (n[:3], n[:3])
    m = rxm.match(n) or rxab.match(n); return (m.group(1), m.group(2))
allp = sorted({p for f in FAMS for i in M[f] for p in pers(i)} | {pers(i)[0] for i in orig}); pidx = {p: j for j, p in enumerate(allp)}
rng = np.random.default_rng(11); C = rng.multinomial(len(allp), np.full(len(allp), 1/len(allp)), size=400).astype(float)
def wthr(x, w, a):
    o = np.argsort(x); xs, ws = x[o], w[o]; tot = ws.sum(); above = tot - np.cumsum(ws)
    j = np.argmax(above <= a*tot + 1e-12); return xs[j]
def run(nm, s, dev_thr=True):
    t = thr(s[dev], .05) if dev_thr else thr(s[orig], .05)
    avail = [k for k in G if np.isfinite(s[G[k]]).all()]
    tp = {k: thr(s[G[k]], .05) for k in avail}
    t_all = max([t] + list(tp.values())); t_icao = max([t] + [tp[k] for k in ICAO_OK if k in tp]); t_orig = thr(s[orig], .05)
    fm = lambda tt: np.mean([100*(s[M[f]] <= tt).mean() for f in FAMS])
    lm = lambda tt: np.mean([100*(s[M[f]] <= tt).mean() for f in ("amsl","facemorpher","opencv","webmorph")])
    # bootstrap of the FRLL-orig-fitted family-mean miss (threshold refit per replicate)
    po = np.array([pidx[pers(i)[0]] for i in orig]); reps = []
    mp = {f: (np.array([pidx[pers(i)[0]] for i in M[f]]), np.array([pidx[pers(i)[1]] for i in M[f]])) for f in FAMS}
    for b in range(C.shape[0]):
        tb = wthr(s[orig], C[b, po], .05); v = []
        for f in FAMS:
            w = C[b, mp[f][0]] * C[b, mp[f][1]]; v.append(100*(w*(s[M[f]] <= tb)).sum()/max(w.sum(), 1e-12))
        reps.append(np.mean(v))
    print(f"{nm:14s} family-mean miss %: dev thr {fm(t):5.1f} | FRLL-orig-fitted {fm(t_orig):5.1f} [{np.percentile(reps,2.5):.1f}, {np.percentile(reps,97.5):.1f}] | worst-pool, all 18 pools {fm(t_all):5.1f} | worst-pool, full-frame pools with inter-eye distance >= 100 px {fm(t_icao):5.1f} (binding: {max((k for k in ICAO_OK if k in tp), key=lambda k: tp[k])}) | landmark-only: dev {lm(t):.1f} orig-fit {lm(t_orig):.1f} wp-all {lm(t_all):.1f} wp-compliant {lm(t_icao):.1f}")
run("ViT-L/14", rel("madation_vitl14", ids)); run("ViT-B/16", rel("madation_vitb16", ids)); run("FE ViT-L/14", rel("madation_fe_vitl14", ids))
run("SelfMAD own", load(OWN, ids, "score"), dev_thr=False)
nets = []
for ln in open(MC/"experiments/A36_published-detector-shortcuts/raw/A36_networks.tsv"):
    if ln.startswith("#"): continue
    f = ln.rstrip("\n").split("\t")
    if len(f) >= 7 and f[3] == "primary" and f[4].split()[0] in ("M3","M3L"): nets.append((f[4].split()[0], int(f[6]), pathlib.PurePath(f[0]).name))
for meth, seed, run_ in sorted(nets)[:3] + sorted(nets)[8:10]:
    run(f"{meth} s{seed}", load(A12BR/run_/"scores_eval_last.npz", ids, "score"))
