import sys, csv, json, pathlib, zlib, collections
sys.path.insert(0, "/home/narolski/smad-next/src/AG1")
import numpy as np
import ag1_read as A
DATA = pathlib.Path("/mnt/t7/smad_next/AG1/data")
rows = list(csv.DictReader(open(DATA / "manifests/ag1.csv")))
lg = {}
for f in pathlib.Path("/mnt/t7/smad_next/AG1/results").glob("AG1_*.log.csv"):
    if "smoke" in f.name: continue
    for r in csv.DictReader(open(f)): lg[r["stem"]] = r
for r in rows:
    if r["id"] in lg:
        for k in ("latdist", "loss", "msssim"):
            if lg[r["id"]].get(k) not in (None, ""): r[k] = float(lg[r["id"]][k])
z = dict(np.load(DATA / "baselines.npz"))
A.BASE = {i: {k: z[k][j] for k in ("bytes", "lapvar", "hfband", "sym", "thumb")} for j, i in enumerate(z["id"].tolist())}
S = A.load_scores(rows, "/mnt/t7/smad_next/AG1/scoring/a41g_out/ag1", False)
REL = list(S)
pool = "primary"
sub = [r for r in rows if A.in_pool(r, pool) and r["gen"] in ("mip1", "camera")]
pers = sorted({r["pa"] for r in sub} | {r["pb"] for r in sub})
D = A.Draw(pers, 10000, A.SEED + zlib.crc32(pool.encode()) % 100000)
plat = {r["pa"]: r["platform"] for r in sub if r["rung"] in ("R2", "R3", "R4") and r["source"] == "ours"}
def grp(hosts=None):
    g = collections.defaultdict(list)
    for r in sub:
        if hosts is None or r["pa"] in hosts: g[r["rung"]].append(r)
    return g
def q(x): return [round(float(v), 3) for v in x]
def excess_retake(c, pos, neg):
    b = A.baseline_block(pos, neg, D)
    # recompute reps of every baseline
    wp = D.w([r["pa"] for r in pos if r["id"] in A.BASE], [r["pb"] for r in pos if r["id"] in A.BASE])
    wn = D.w([r["pa"] for r in neg if r["id"] in A.BASE], [r["pb"] for r in neg if r["id"] in A.BASE])
    P = [r for r in pos if r["id"] in A.BASE]; N = [r for r in neg if r["id"] in A.BASE]
    reps = []
    for k in A.SCALAR_BASELINES:
        sp = np.array([A.BASE[r["id"]][k] for r in P]); sn = np.array([A.BASE[r["id"]][k] for r in N])
        sg = 1 if A.auc(sp, sn) >= .5 else -1
        reps.append(A.wauc(sg*sp, sg*sn, wp, wn))
    reps.append(b["best_rep"] if b["best"] == "thumb" else None)
    # thumb rep: recompute from oof via baseline_block internals -> reuse by calling again with best forced
    return b, reps
def contrast_row(sc, g, a, bkey):
    pos, neg = g[bkey], g[a]
    c = A.contrast_fn(sc, D)(pos, neg)
    b = A.baseline_block(pos, neg, D)
    ex = c["auc"] - b["best_auc"]; exci = A.ci(c["rep"] - b["best_rep"])
    return c, b, ex, exci
out = {}
for rel in REL:
    sc = S[rel]
    for name, hosts in (("all", None), ("athena", {h for h, p in plat.items() if p.startswith("athena")}),
                        ("rented", {h for h, p in plat.items() if p.startswith("rented")})):
        g = grp(hosts)
        res = {"nhosts": len({r["pa"] for r in g["R4"]})}
        C = {}
        for a, bk in (("R0", "R2"), ("R2", "R4"), ("R3", "R4"), ("R2s", "R4"), ("R0", "R4"), ("R2", "R3"), ("R2s","R2")):
            c, b, ex, exci = contrast_row(sc, g, a, bk)
            C[a+">"+bk] = c
            res[a+">"+bk] = {"auc": round(c["auc"], 3), "ci": q(c["ci"]), "best": b["best"], "best_auc": round(b["best_auc"], 3),
                             "excess": round(ex, 3), "excess_ci": q(exci), "bl": {k: round(v, 3) for k, v in b["aucs"].items()}}
        d04 = A.dprime(C["R0>R4"]["auc"])
        rep = np.array([A.dprime(x) for x in C["R0>R2"]["rep"]]) / np.array([max(A.dprime(x), 1e-9) for x in C["R0>R4"]["rep"]])
        sh = A.dprime(C["R0>R2"]["auc"]) / d04; shci = A.ci(rep)
        m = C["R2>R4"]
        res["share02"] = [round(sh, 3)] + q(shci)
        res["A"] = A.verdict_A(m["auc"], *m["ci"], sh, shci[0]); res["B"] = A.verdict_B(m["auc"], *m["ci"])
        res["side_R3R4"] = A.side_verdict(C["R3>R4"]["auc"], *C["R3>R4"]["ci"])
        # share without clip
        from scipy.stats import norm
        def dp(a, clip): return np.sqrt(2) * norm.ppf(np.clip(a, 1-clip, clip))
        for clip in (0.999, 0.9999):
            r2 = dp(C["R0>R2"]["rep"], clip) / dp(C["R0>R4"]["rep"], clip)
            res[f"share02_clip{clip}"] = [round(float(dp(C['R0>R2']['auc'], clip) / dp(C['R0>R4']['auc'], clip)), 3)] + q(A.ci(r2))
        out[f"{rel}/{name}"] = res
json.dump(out, open(sys.argv[1], "w"), indent=1)
for k, v in out.items():
    print(k, v["nhosts"], "A:", v["A"], "| B:", v["B"], "| share", v["share02"], v["share02_clip0.999"], "| side", v["side_R3R4"])
    for c in ("R0>R2", "R2>R4", "R3>R4", "R2s>R4", "R2>R3", "R2s>R2", "R0>R4"):
        x = v[c]; print("   ", c, x["auc"], x["ci"], x["best"], x["best_auc"], "ex", x["excess"], x["excess_ci"])
