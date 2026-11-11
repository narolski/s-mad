"""V1: leakage checks + independent recomputation of the Q3 headline (own folds, own head code).
Run: OMP_NUM_THREADS=2 nice -n 10 <spark python> -I v1_recompute.py"""
import json, sys, collections
import numpy as np
sys.path.insert(0, __import__("os").path.dirname(__file__))
import vlib as V

items = V.rows("items.csv"); IT = {r["id"]: r for r in items}
hosts = V.rows("hosts.csv")
HG = [h for h in hosts if h["set"] == "G"]
HH = [h for h in hosts if h["set"] == "Hr"]
out = {}

# ---------------- leakage ----------------
lk = {}
g = [r for r in items if r["set"] == "G"]
subj_blocks = collections.defaultdict(set)
for r in g:
    if r["role"] == "x0":
        subj_blocks[(r["db"], r["subject"])].add(r["cluster"])
lk["subjects_in_more_than_one_block"] = sum(len(v) > 1 for v in subj_blocks.values())
lk["n_subjects"] = len(subj_blocks)
# every source capture of x1/x2/x3 belongs to its own block
bad = [r["id"] for r in g if r["role"] != "x0" and any(not s.startswith(r["cluster"] + "__") for s in r["src"].split(";"))]
lk["renders_with_source_outside_block"] = len(bad)
# persons per block: A and B different subjects, each with two captures
per = collections.defaultdict(set)
for r in g:
    if r["role"] == "x0":
        per[r["cluster"]].add(r["subject"])
lk["blocks_with_not_2_subjects"] = sum(len(v) != 2 for v in per.values())
# FR templates: cross-block near-duplicates of persons
tz = np.load(V.BIG / "templates.npz"); T = tz["t"] / np.linalg.norm(tz["t"], axis=1, keepdims=True); keys = tz["key"].tolist()
blk = [k.split("__")[0] for k in keys]
S = T @ T.T
cross = np.array([[blk[i] != blk[j] for j in range(len(keys))] for i in range(len(keys))])
same = np.array([[blk[i] == blk[j] and keys[i].split("__")[1][0] == keys[j].split("__")[1][0] and i != j for j in range(len(keys))] for i in range(len(keys))])
lk["FR_cos_cross_block_max"] = float(S[cross].max())
lk["FR_cos_cross_block_n_above_0.4"] = int((S[cross] > 0.4).sum() // 2)
lk["FR_cos_same_person_median"] = float(np.median(S[same]))
lk["image_ids_shared_between_hosts_of_different_blocks"] = 0
idblk = collections.defaultdict(set)
for h in HG:
    for r in ("x0", "x1", "x2", "x3"):
        idblk[h[r]].add(h["cluster"])
lk["image_ids_shared_between_hosts_of_different_blocks"] = sum(len(v) > 1 for v in idblk.values())
lk["H_pairs"] = len(HH)
out["leakage"] = lk
print(json.dumps(lk, indent=1), flush=True)


def contrasts(sc, tag):
    r = {}
    for p, n in (("x3", "x1"), ("x3", "x2"), ("x2", "x1"), ("x3", "x0"), ("x1", "x0"), ("x2", "x0")):
        ip, inn = sorted({h[p] for h in HG}), sorted({h[n] for h in HG})
        sp, sn = [sc[i] for i in ip], [sc[i] for i in inn]
        r[f"{p} vs {n}"] = dict(auc=V.auc(sp, sn), ci=V.boot_auc(sp, [IT[i]["cluster"] for i in ip], sn, [IT[i]["cluster"] for i in inn]))
    # paired win x3 > x1 over hosts
    r["paired_win_x3_gt_x1"] = float(np.mean([sc[h["x3"]] > sc[h["x1"]] for h in HG]))
    return r


def oof(F, kind, pos, seed):
    fo = V.block_folds([h["cluster"] for h in HG], 5, seed)
    sc, Cs, thr = {}, [], {}
    flags = {"x2": [], "x3": [], "x0": []}
    for k in range(5):
        tr = [h for h in HG if fo[h["cluster"]] != k]; te = [h for h in HG if fo[h["cluster"]] == k]
        assert not ({h["cluster"] for h in tr} & {h["cluster"] for h in te})
        trimg = {h[r] for h in tr for r in ("x0", "x1", "x2", "x3")}; teimg = {h[r] for h in te for r in ("x0", "x1", "x2", "x3")}
        assert not (trimg & teimg)
        hd, C = V.fit_head(kind, F, [(h[pos], h["x1"]) for h in tr], [h["cluster"] for h in tr], seed * 10 + k)
        Cs.append(C)
        ids = sorted(teimg)
        s = hd(np.array([F[i] for i in ids]))
        sc.update(zip(ids, s.tolist()))
    return sc, Cs


def flagx(sc):
    """threshold at the 95% quantile of x1 (reconstructions) OOF scores; share of x2 / x3 above (descriptive)."""
    x1 = np.array([sc[i] for i in sorted({h["x1"] for h in HG})])
    t = np.quantile(x1, .95, method="higher")
    r = {}
    for role in ("x2", "x3"):
        v = np.array([sc[i] for i in sorted({h[role] for h in HG})])
        r[f"{role}_flagged_at_x1_5pct"] = float(np.mean(v > t))
    x0 = np.array([sc[i] for i in sorted({h["x0"] for h in HG})])
    t0 = np.quantile(x0, .95, method="higher")
    for role in ("x1", "x2", "x3"):
        v = np.array([sc[i] for i in sorted({h[role] for h in HG})])
        r[f"{role}_flagged_at_camera_photo_5pct"] = float(np.mean(v > t0))
    return r


res = {}
saved = {}
for bb, kind in (("clip", "pool"), ("clip", "patch"), ("dinov3", "pool")):
    F = V.feats(bb, kind, ["G"])
    fr = {}
    for hk, pos, typ in (("O_paired", "x2", "paired"), ("T_paired", "x3", "paired"), ("O_unpaired", "x2", "unpaired"), ("T_unpaired", "x3", "unpaired")):
        per_seed = {}
        for seed in (7, 8, 9):
            sc, Cs = oof(F, typ, pos, seed)
            c = contrasts(sc, hk)
            c["C"] = Cs
            c.update(flagx(sc))
            per_seed[seed] = c
            if seed == 7:
                saved[f"{bb}_{kind}_{hk}"] = sc
            print(bb, kind, hk, seed, "x3vx1 %.3f %s  x3vx2 %.3f x2vx1 %.3f C %s" % (c["x3 vs x1"]["auc"], np.round(c["x3 vs x1"]["ci"], 3),
                  c["x3 vs x2"]["auc"], c["x2 vs x1"]["auc"], Cs), flush=True)
        fr[hk] = per_seed
    # owner's saved OOF
    z = np.load(V.BIG / f"oof_{bb}_{kind}.npz")
    so = dict(zip(z["O_id"].tolist(), z["O_score"]))
    fr["owner_saved_O_oof"] = {k: v["auc"] for k, v in contrasts(so, "own").items() if isinstance(v, dict)}
    res[f"{bb}_{kind}"] = fr
out["heads"] = res
np.savez(V.OUT / "v1_oof.npz", **{k: np.array([[i, str(s)] for i, s in v.items()]) for k, v in saved.items()})
json.dump(out, open(V.OUT / "v1_recompute.json", "w"), indent=1)
print("done")
