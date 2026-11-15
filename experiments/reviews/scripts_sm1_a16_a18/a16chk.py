import sys, csv, io, tarfile, hashlib, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/SM1")
import sm1_common as K, sm1_stats as S
from scipy.stats import spearmanr
D = K.OUT / "results_rented/dev16"
rows = list(csv.DictReader(open(K.OUT / "dev_a16/sm1_dev16_eval.csv")))
it = {}
for r in csv.DictReader(open("/mnt/t7/smad_next/FZ2/read_addon_items.csv")):
    it[(r["key"], r["host"])] = r
def auc(p, n): return float(S.wauc(np.array(p), np.array(n), np.ones((1,len(p))), np.ones((1,len(n))))[0])
sc = {}
for arm in "aef":
    for s in (401, 402):
        f = D / f"SM1E_{arm}_s{s}.tar"
        assert hashlib.sha256(open(f,"rb").read()).hexdigest() == open(str(f)+".sha256").read().split()[0]
        with tarfile.open(f) as t:
            m = [x for x in t.getmembers() if x.name.endswith("scores_audit.npz")][0]
            z = np.load(io.BytesIO(t.extractfile(m).read()))
        p = np.clip(z["score_noTTA"].astype(float), 1e-7, 1-1e-7)
        sc[(arm,s)] = dict(zip([str(i) for i in z["id"]], np.log(p/(1-p))))
fam = {}
for r in rows: fam.setdefault(r["family"], {})[r["variant"]] = r["id"]
print({k: len(v) for k, v in fam.items()})
for arm in "aef":
    for a, b in (("FRESH1_20","REC20"),("NOISES20","REC20"),("NOISEX20","NOISES20"),("SEMX20","SEMS20"),("MIR20","REC20"),("SEMS20","REC20")):
        hs = sorted(set(fam[a]) & set(fam[b]))
        v = [auc([sc[(arm,s)][fam[a][h]] for h in fam[a]], [sc[(arm,s)][fam[b][h]] for h in fam[b]]) for s in (401,402)]
        # paired: share of hosts where a > b, and Laplacian
        m = np.mean([[sc[(arm,s)][fam[a][h]] - sc[(arm,s)][fam[b][h]] for h in hs] for s in (401,402)], 0)
        ka, kb = a, b
        dl = np.array([np.log(float(it[(ka,h)]["lapvar_box"])) - np.log(float(it[(kb,h)]["lapvar_box"])) for h in hs])
        db = np.array([np.log(float(it[(ka,h)]["png_bytes"])) - np.log(float(it[(kb,h)]["png_bytes"])) for h in hs])
        print(arm, f"{a}/{b}", [round(x,4) for x in v], "mean", round(np.mean(v),4), "paired share>", round((m>0).mean(),3),
              "| share dLap>0", round((dl>0).mean(),3), "spearman dscore~dLap", round(spearmanr(m, dl)[0],3), "~dbytes", round(spearmanr(m, db)[0],3))
# score vs Laplacian across all rungs, arm e and a
for arm in "ae":
    allv = [(np.mean([sc[(arm,s)][r["id"]] for s in (401,402)]), np.log(float(it[(r["family"], r["variant"])]["lapvar_box"]))) for r in rows]
    a_ = np.array(allv); print(arm, "spearman score~log Lap over all rung rows", round(spearmanr(a_[:,0], a_[:,1])[0],3))
    for f in fam:
        print("   ", f, "median logit", round(np.median([np.mean([sc[(arm,s)][fam[f][h]] for s in (401,402)]) for h in fam[f]]),2), "median Lap", round(np.median([float(it[(f,h)]["lapvar_box"]) for h in fam[f]]),1))
