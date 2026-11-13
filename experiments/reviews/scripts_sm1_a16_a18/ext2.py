import sys, csv, io, tarfile, json, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/SM1"); sys.path.insert(0, "/home/narolski/smad-next/src/FZ2")
import hn2_incr as I, sm1_common as K, sm1_stats as S
from fz2_amend2 import feats, cos
from sklearn.linear_model import LogisticRegression
RR = "/mnt/t7/smad_next/DG1/rented_results"
items = {r["id"]: r for r in csv.DictReader(open("/mnt/t7/smad_next/FZ2/read_addon_items.csv")) if r["key"] in ("X20","SAME20")}
th = {}
for k in range(8):
    for r in csv.DictReader(open(f"/mnt/t7/smad_next/DG1/gen/addon_s{k}/out_addon_s{k}/addon_s{k}/gen_rows.csv")):
        if r["theta_xT"] not in ("", "nan"): th[(f"addon_s{k}", r["pool"], r["name"])] = float(r["theta_xT"])
code = {}
for k in range(2, 7):
    with tarfile.open(f"{RR}/DG1_addon_s{k}_codes.tar") as tf:
        m = [x for x in tf.getmembers() if x.name.endswith("codes.npz")][0]; z = np.load(io.BytesIO(tf.extractfile(m).read()))
    ix = {n: i for i, n in enumerate(z["names"])}
    for j in csv.DictReader(open(f"/mnt/t7/smad_next/DG1/addon_jobs/addon_s{k}.csv")):
        if j["pool"] in ("AO_X20","AO_SAME20") and j["src_a"] in ix and j["src_b"] in ix:
            f = feats(z["xT"][ix[j["src_a"]]].astype(np.float64), z["xT"][ix[j["src_b"]]].astype(np.float64))
            code[(j["pool"][3:], j["host"])] = [f[q] for q in ("c0","c1","c2","c3","lp8")]
dropped = set(json.load(open(K.OUT / "hn2/lists.json"))["dropped_crossing_X20"])
def base(a):
    p = a["id"].split("/")
    return [th[(a["list"], p[-2], p[-1])], np.log(float(a["lapvar_box"])), np.log(float(a["png_bytes"])), float(a["asym_box"]), float(a["d"])]
tr = [a for a in items.values() if a["list"] in ("addon_s2","addon_s3","addon_s4","addon_s5") and a["id"] not in dropped and (a["key"], a["host"]) in code]
Xtr = np.array([base(a) + code[(a["key"], a["host"])] for a in tr]); ytr = np.array([a["key"] == "X20" for a in tr]).astype(int)
print("floor train rows (s2-5)", len(tr), ytr.sum())
mu, sd = Xtr.mean(0), Xtr.std(0)
fl = LogisticRegression(max_iter=5000).fit((Xtr-mu)/sd, ytr)
fl5 = LogisticRegression(max_iter=5000).fit(((Xtr-mu)/sd)[:, :5], ytr)
rows = [r for r in I.test_rows() if (r["id"].split(":")[1], ":".join(r["id"].split(":")[2:])) in code]
y = np.array([r["y"] for r in rows])
ext = np.array([r["f"] + code[(r["id"].split(":")[1], ":".join(r["id"].split(":")[2:]))] for r in rows])
fs = fl.decision_function((ext-mu)/sd); fs5 = fl5.decision_function(((ext-mu)/sd)[:, :5])
def auc(v): return float(S.wauc(v[y==1], v[y==0], np.ones((1,(y==1).sum())), np.ones((1,(y==0).sum())))[0])
print("out-of-sample floor (fit s2-5) on s6: F_ext", round(auc(fs),4), "F5", round(auc(fs5),4))
net = {}
for s in (401,402,403):
    z = np.load(K.OUT / f"results_rented/hn2/HN2_RS_s{s}/hn2test/scores_eval.npz"); p = np.clip(z["score_noTTA"].astype(float),1e-7,1-1e-7)
    net[s] = dict(zip([str(i) for i in z["id"]], np.log(p/(1-p))))
# combine pre-fit floor score + net (cross-fit on s6 cycles) -> use incremental with f=[floor score]
for nm, f in (("Fext_pre", fs), ("F5_pre", fs5)):
    rr = [dict(r, f=[f[i], f[i]]) for i, r in enumerate(rows)]  # hn2_incr drops f[0] for Fimg; keep 2 copies
    res = I.summarise([I.incremental(rr, net[s]) for s in (401,402)])
    print(nm, "F", res["F"]["mean"], "F+net", res["F_plus"]["mean"], "dAUC", res["dAUC_over_F"])
# stratified: net AUC within terciles of the pre-fit extended floor score
q = np.quantile(fs, [1/3, 2/3]); st = np.searchsorted(q, fs)
for s in (401,402):
    v = np.array([net[s][r["id"]] for r in rows]); pt = wt = 0
    for k in range(3):
        m = st == k; nx, ns = (y[m]==1).sum(), (y[m]==0).sum()
        if nx and ns:
            a = float(S.wauc(v[m&(y==1)], v[m&(y==0)], np.ones((1,nx)), np.ones((1,ns)))[0]); pt += nx*ns*a; wt += nx*ns
            print(s, "tercile", k, "X/SAME", nx, ns, "net AUC", round(a,3), "floor AUC", round(float(S.wauc(fs[m&(y==1)], fs[m&(y==0)], np.ones((1,nx)), np.ones((1,ns)))[0]),3))
    print(s, "floor-tercile-stratified net AUC", round(pt/wt,4))
# frozen probes over the extended floor (cross-fit within s6)
FD = "/mnt/t7/smad_next/FZ2/results/dgx/out"
alli = [r for r in csv.DictReader(open("/mnt/t7/smad_next/FZ2/read_addon_items.csv")) if r["key"] in ("X20","SAME20")]
trp = [r for r in alli if r["list"] in {f"addon_s{k}" for k in range(6)} and r["id"] not in dropped]
tm = {f"hn2:{r['key']}:{r['host']}": r["id"] for r in alli}
for feat in ("clip_mad","dinov2"):
    F = {}
    for k in range(8):
        z = np.load(f"{FD}/{feat}_addon_s{k}.npz"); F.update(zip([str(i) for i in z["id"]], z["feat"].astype(np.float64)))
    A = np.stack([F[r["id"]] for r in trp]); ya = np.array([r["key"]=="X20" for r in trp]).astype(int)
    m_, s_ = A.mean(0), A.std(0)+1e-12; pr = LogisticRegression(max_iter=5000).fit((A-m_)/s_, ya)
    sc = {r["id"]: float(pr.decision_function(((F[tm[r["id"]]]-m_)/s_)[None])[0]) for r in rows}
    for nm, ex in (("F5", False), ("Fext", True)):
        rr = [dict(r, f=list(ext[i]) if ex else list(r["f"])) for i, r in enumerate(rows)]
        o = I.summarise([I.incremental(rr, sc)])
        print(feat, nm, "probe raw", o["score_raw_auc"]["mean"], "F", o["F"]["mean"], "dAUC", o["dAUC_over_F"])
