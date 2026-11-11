"""Reviewer: the descriptive FE/FS rows of AD1 - is there a morph-vs-reconstruction separation that result.md skipped?"""
import csv, re, pathlib, numpy as np
A43 = pathlib.Path("/mnt/t7/smad_heldout/a43")
rows = list(csv.DictReader(open(A43/"data/manifests/a43.csv")))
def pers(r):
    if r["source"]=="a43": return (r["src_a"][:3], r["src_b"][:3]) if r["src_b"] else (r["src_a"][:3],)
    n = pathlib.PurePath(r["path"]).name; m = re.match(r"^morph_(\d{3})_\d{2}_and_(\d{3})_\d{2}", n)
    return (m.group(1), m.group(2)) if m else (n[:3],)
allp = sorted({p for r in rows for p in pers(r)}); pidx = {p:i for i,p in enumerate(allp)}
rng = np.random.default_rng(31337); NB = 4000
CNT = rng.multinomial(len(allp), np.full(len(allp),1/len(allp)), size=NB).astype(float)
def W(ii):
    pp = [pers(rows[i]) for i in ii]; a = np.array([pidx[p[0]] for p in pp]); b = np.array([pidx[p[-1]] for p in pp]); w = CNT[:,a]*CNT[:,b]; s = a==b; w[:,s] = CNT[:,a[s]]; return w
def wauc(pos, neg, wp, wn):
    ob = np.argsort(neg, kind="stable"); ns = neg[ob]; lo, hi = np.searchsorted(ns,pos,"left"), np.searchsorted(ns,pos,"right")
    C = np.concatenate([np.zeros((wn.shape[0],1)), np.cumsum(wn[:,ob],1)],1)
    return (wp*(C[:,lo]+0.5*(C[:,hi]-C[:,lo]))).sum(1)/np.maximum(wp.sum(1)*C[:,-1],1e-12)
def grp(arm, ex=None):
    if arm=="R0": return [i for i,r in enumerate(rows) if r["source"]!="a43" and r["family"]=="mordiff_bona"]
    return [i for i,r in enumerate(rows) if r["source"]=="a43" and r["arm"]==arm and (ex is None or r["expr"]==ex)]
for lab, f in (("FE ViT-L/14","madation_fe_vitl14/rel"),("FE ViT-B/16","madation_fe_vitb16/rel"),("FS ViT-L/14","madation_fs_vitl14/rel"),("full ViT-L/14","madation_vitl14/rel"),("full ViT-B/16","madation_vitb16/rel")):
    s = np.load(A43/"a43_out/a43"/f/"scores_a43.npz")["score_noTTA"].astype(float)
    def c(a, b, ea=None, eb=None):
        ia, ib = grp(a, ea), grp(b, eb); pt = float(wauc(s[ia], s[ib], np.ones((1,len(ia))), np.ones((1,len(ib))))[0]); rep = wauc(s[ia], s[ib], W(ia), W(ib))
        return f"{pt:.3f} [{np.percentile(rep,2.5):.3f}, {np.percentile(rep,97.5):.3f}]"
    print(f"== {lab}")
    print("   20 steps : B20 vs D20", c("B20","D20"), "| neutral", c("B20","D20","03","03"), "| smiling", c("B20","D20","08","08"), "| C20 vs D20", c("C20","D20"), "| B20 vs C20", c("B20","C20"))
    print("   100 steps: B vs D    ", c("B","D"), "| neutral", c("B","D","03","03"), "| smiling", c("B","D","08","08"), "| C vs D", c("C","D"), "| B vs C", c("B","C"))
    print("   vs camera: E vs R0", c("E","R0"), "| D vs R0", c("D","R0"), "| D20 vs R0", c("D20","R0"), "| B vs R0", c("B","R0"), "| B20 vs R0", c("B20","R0"), "| A vs R0", c("A","R0"), "| D vs E", c("D","E"), "| B vs E", c("B","E"))
