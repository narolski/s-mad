import sys, csv, io, tarfile, hashlib, json, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/SM1"); sys.path.insert(0, "/home/narolski/smad-next/src/FZ2")
import hn2_incr as I, sm1_common as K, sm1_stats as S
from fz2_amend2 import feats, cos
from scipy.stats import spearmanr
RR = "/mnt/t7/smad_next/DG1/rented_results"
pool = {p["pid"]: p for p in csv.DictReader(open("/home/narolski/smad-next/experiments/AR1/pool.csv"))}
items = {r["id"]: r for r in csv.DictReader(open("/mnt/t7/smad_next/FZ2/read_addon_items.csv")) if r["key"] in ("X20","SAME20")}
code = {}  # (key, host) -> dict
for k in range(2, 7):
    t = f"{RR}/DG1_addon_s{k}_codes.tar"
    h = hashlib.sha256(open(t, "rb").read()).hexdigest(); assert h == open(t + ".sha256").read().split()[0]
    with tarfile.open(t) as tf:
        m = [x for x in tf.getmembers() if x.name.endswith("codes.npz")][0]
        z = np.load(io.BytesIO(tf.extractfile(m).read()))
    ix = {n: i for i, n in enumerate(z["names"])}
    for j in csv.DictReader(open(f"/mnt/t7/smad_next/DG1/addon_jobs/addon_s{k}.csv")):
        if j["pool"] not in ("AO_X20", "AO_SAME20"): continue
        if j["src_b"] not in ix or j["src_a"] not in ix: continue
        a = z["xT"][ix[j["src_a"]]].astype(np.float64); b = z["xT"][ix[j["src_b"]]].astype(np.float64)
        f = feats(a, b); f["zcos"] = cos(z["z"][ix[j["src_a"]]].astype(np.float64), z["z"][ix[j["src_b"]]].astype(np.float64))
        f["shard"] = k
        code[(j["pool"][3:], j["host"])] = f
print("codes", len(code))
# glint identity cos
def idcos(key, host):
    p = pool[host]; return float(p["cos_HB"] if key == "X20" else p["cos_HS"])
# network logits
D = K.OUT / "results_rented/hn2"
net = {}
for s in (401, 402, 403):
    z = np.load(D / f"HN2_RS_s{s}/hn2test/scores_eval.npz"); p = np.clip(z["score_noTTA"].astype(float), 1e-7, 1-1e-7)
    net[s] = dict(zip([str(i) for i in z["id"]], np.log(p/(1-p))))
rows = I.test_rows()
for r in rows:
    key, host = r["id"].split(":")[1], ":".join(r["id"].split(":")[2:])
    r["key"], r["host"] = key, host
    r["code"] = code.get((key, host)); r["idcos"] = idcos(key, host)
    r["shard"] = items[r["item_id"]]["list"]
    r["net"] = np.mean([net[s][r["id"]] for s in (401, 402)])
# check theta recompute
d = [abs(r["code"]["theta"] - r["f"][0]) for r in rows if r["code"]]
print("theta recompute max diff", max(d), "n with codes", len(d), "shards", set(r["shard"] for r in rows if r["code"]))
s6 = [r for r in rows if r["code"]]
y6 = np.array([r["y"] for r in s6])
def auc(v, y): 
    return float(S.wauc(v[y==1], v[y==0], np.ones((1,(y==1).sum())), np.ones((1,(y==0).sum())))[0])
print("n s6 X/SAME", (y6==1).sum(), (y6==0).sum(), "cycles", len({r['cycle'] for r in s6}))
for nm in ("theta","c0","c1","c2","c3","lp8","zcos"):
    v = np.array([r["code"][nm] for r in s6]); a = auc(v, y6); print("single", nm, round(max(a,1-a),4))
v = np.array([r["idcos"] for r in s6]); print("single glint idcos", round(1-auc(v,y6),4))
for s in (401,402,403):
    v=np.array([net[s][r["id"]] for r in s6]); print("net raw s6", s, round(auc(v,y6),4))
# incremental over extended floors on shard 6 (cross-fit on s6 cycles)
def mk(r, ext):
    f = list(r["f"])
    if ext >= 1: f += [r["code"][k] for k in ("c0","c1","c2","c3","lp8")]
    if ext >= 2: f += [r["code"]["zcos"]]
    return f
out = {}
for ext in (0, 1, 2):
    rr = [dict(r, f=mk(r, ext)) for r in s6]
    res = [I.incremental(rr, net[s]) for s in (401, 402, 403)]
    sm = I.summarise(res[:2]); sm3 = I.summarise(res)
    print("ext", ext, "F", sm["F"]["mean"], "F+net", sm["F_plus"]["mean"], "dAUC 2seed", sm["dAUC_over_F"], "3seed", sm3["dAUC_over_F"]["mean"], sm3["dAUC_over_F"]["seeds"])
    out[ext] = sm
json.dump({str(k): v for k, v in out.items()}, open("ext_out.json", "w"), indent=1)
# identity: within X20 and SAME20, all test rows
for key in ("X20", "SAME20"):
    g = [r for r in rows if r["key"] == key]
    a = np.array([r["net"] for r in g]); b = np.array([r["idcos"] for r in g]); th = np.array([r["f"][0] for r in g])
    print(key, "n", len(g), "spearman net vs glint cos", spearmanr(a, b), "net vs theta", spearmanr(a, th)[0], "glint vs theta", spearmanr(b, th)[0])
    from numpy.linalg import lstsq
    def res_(u, Xc): Xc = np.c_[np.ones(len(u)), Xc]; return u - Xc @ lstsq(Xc, u, rcond=None)[0]
    from scipy.stats import rankdata
    Fm = np.array([r["f"] for r in g])
    print("  partial (ranks) net~glint | F", spearmanr(res_(rankdata(a), np.apply_along_axis(rankdata,0,Fm)), res_(rankdata(b), np.apply_along_axis(rankdata,0,Fm))))
    g6 = [r for r in g if r["code"]]
    a6 = np.array([r["net"] for r in g6]); b6 = np.array([r["idcos"] for r in g6]); Fm6 = np.array([mk(r, 2) for r in g6])
    print("  s6 n", len(g6), "partial net~glint | Fext+zcos", spearmanr(res_(rankdata(a6), np.apply_along_axis(rankdata,0,Fm6)), res_(rankdata(b6), np.apply_along_axis(rankdata,0,Fm6))))
    for nm in ("c0","c2","lp8","zcos"):
        print("  s6 spearman net vs", nm, round(spearmanr(a6, [r["code"][nm] for r in g6])[0],3))
