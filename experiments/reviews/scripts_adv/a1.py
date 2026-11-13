import sys, csv, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/adversary")
import contrasts as C, run_floors as RF, floor as FL
name = sys.argv[1]
rl = C.build(name)
X, nm = RF.X_of(rl)
y = np.array([l for _, _, l, _ in rl])
# reproduce reported AUCs from heldout csv
H = list(csv.DictReader(open(f"/home/narolski/smad-next/experiments/ADV_shortcut-floors/floors/{name}_heldout.csv")))
assert [h["id"] for h in H] == [r[0] for r in rl]
for m in ("single","logreg","gbt","nu_single","nu_logreg","nu_gbt"):
    print(m, round(FL.auc([float(h[m]) for h in H], [int(h["label"]) for h in H]),4))
print("components", len(set(h["component"] for h in H)))
res=[]
for j,n in enumerate(nm):
    x=X[:,j]; ok=np.isfinite(x)
    a=FL.auc(x[ok],y[ok]) if ok.sum()>2 else np.nan
    res.append((max(a,1-a) if np.isfinite(a) else -1, n, a, np.nanmedian(x[y==1]), np.nanmedian(x[y==0]), len(np.unique(x[ok]))))
res.sort(reverse=True)
for r in res[:30]: print("%.3f %-28s dir=%.3f med_pos=%.4g med_neg=%.4g nuniq=%d"%r)
print("--- pngmeta / file")
for r in res:
    if r[1] in RF.FILE_SIZE or "png_" in r[1]: print("%.3f %-28s dir=%.3f med_pos=%.4g med_neg=%.4g nuniq=%d"%r)
