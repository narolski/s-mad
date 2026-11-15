import sys, csv, re, numpy as np, pathlib, collections, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lib import *
from scipy.stats import spearmanr, rankdata
R = rows_eval(); ids = [r["id"] for r in R]
z = np.load("/mnt/t7/smad_heldout/a46/feat/a46_feat.npz", allow_pickle=False)
E = z["emb"].astype(np.float64); E /= np.linalg.norm(E, axis=1, keepdims=True)
A = {str(k): e for k, e, f in zip(z["keys"], E, z["found"]) if f}
raw = {k.split("|",1)[1]: v for k, v in A.items() if k.startswith("raw|")}
MDR = pathlib.Path("/mnt/t7/Datasety/downloads/MorDIFF/MorDIFF_crop")
rx = re.compile(r"^morph_(\d{3})_(\d{2})_and_(\d{3})_(\d{2})"); rxab = re.compile(r"^(\d{3})_(\d{3})_")
gp = {}
for d in MDR.glob("*_front_*_aligned"):
    g = "F" if "_female_" in d.name else "M"
    for p in (d/"morphed").glob("*.png"):
        m = rx.match(p.name); gp[m.group(1)] = g; gp[m.group(3)] = g
print("persons with gender", len(gp), collections.Counter(gp.values()))
def items(f):
    out = []
    for i in sel(R, SETOF[f], f, "orig", "1"):
        n = R[i]["name"]; m = rx.match(n)
        if m: a, ea, b, eb = m.group(1), m.group(2), m.group(3), m.group(4)
        else:
            m = rxab.match(n); a, b, ea, eb = m.group(1), m.group(2), "03", "03"
        if a != b: out.append((i, a, b, ea+eb))
    return out
rng = np.random.default_rng(7)
pers = sorted(gp); pidx = {p: j for j, p in enumerate(pers)}
C = rng.multinomial(len(pers), np.full(len(pers), 1/len(pers)), size=1000)
def wsp(x, y, w):
    # weighted Spearman via replication-free weighted Pearson of full-sample ranks (approximation, adequate for a check)
    rx_, ry_ = rankdata(x), rankdata(y); sw = w.sum()
    mx, my = (w*rx_).sum()/sw, (w*ry_).sum()/sw
    return (w*(rx_-mx)*(ry_-my)).sum()/np.sqrt((w*(rx_-mx)**2).sum()*(w*(ry_-my)**2).sum())
dets = {"ViT-L/14": rel("madation_vitl14", ids), "ViT-B/16": rel("madation_vitb16", ids), "SelfMAD own": load(OWN, ids, "score")}
for f in ("facemorpher","opencv","webmorph","amsl","mordiff","greedy_dim_s","dim_c"):
    it = [q for q in items(f) if q[3] == "0303"]
    ix = np.array([q[0] for q in it]); a = [q[1] for q in it]; b = [q[2] for q in it]
    delta = np.array([1 - raw[x+"_03"] @ raw[y+"_03"] for x, y in zip(a, b)])
    g = np.array([gp[x]+gp[y] for x, y in zip(a, b)])
    W = C[:, [pidx[x] for x in a]] * C[:, [pidx[y] for y in b]]
    print(f"\n{f}: n={len(it)} gender pairs {dict(collections.Counter(g))}; delta median all {np.median(delta):.3f} FF {np.median(delta[g=='FF']):.3f} MM {np.median(delta[g=='MM']):.3f}; AUC(delta MM > FF) {auc(delta[g=='MM'], delta[g=='FF']):.2f}")
    for nm, s in dets.items():
        x = s[ix]
        r_all = spearmanr(x, delta).statistic
        rF = spearmanr(x[g=='FF'], delta[g=='FF']).statistic; rM = spearmanr(x[g=='MM'], delta[g=='MM']).statistic
        # pooled within-gender: ranks centred within gender
        def within(xx, dd, gg, w=None):
            rx_ = np.empty(len(xx)); rd_ = np.empty(len(xx))
            for k in ("FF","MM"):
                m_ = gg == k; rx_[m_] = rankdata(xx[m_])/m_.sum(); rd_[m_] = rankdata(dd[m_])/m_.sum()
                rx_[m_] -= rx_[m_].mean(); rd_[m_] -= rd_[m_].mean()
            if w is None: w = np.ones(len(xx))
            return (w*rx_*rd_).sum()/np.sqrt((w*rx_**2).sum()*(w*rd_**2).sum())
        rw = within(x, delta, g)
        bs_all = np.array([wsp(x, delta, W[k]) for k in range(300)]); bs_w = np.array([within(x, delta, g, W[k]) for k in range(300)])
        print(f"   {nm:12s} rho all {r_all:+.3f} [{np.percentile(bs_all,2.5):+.2f},{np.percentile(bs_all,97.5):+.2f}] | FF {rF:+.3f} MM {rM:+.3f} | pooled within-gender {rw:+.3f} [{np.percentile(bs_w,2.5):+.2f},{np.percentile(bs_w,97.5):+.2f}] | AUC(score MM > FF) {auc(x[g=='MM'], x[g=='FF']):.2f}")
