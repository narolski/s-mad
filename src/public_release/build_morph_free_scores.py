"""PRIVATE helper: score file of the morph-free networks (AD4; ViT-B/16 registered arm results_wcss_m3, ViT-L/14
registered arm results_m3l_registered; label-permuted controls; untrained networks from zero_step) with pool labels
only. Fields: method, seed, pool, score (flip-averaged sigmoid, the registered AD4 score) and score_noTTA.
  python3 -I build_morph_free_scores.py <release-repo>/results/morph_free/scores_morph_free.npz"""
import csv, io, sys, tarfile, collections
import numpy as np
T = "/mnt/t7/smad_next/AD4"
EV = f"{T}/test/work/task_AD4_m3mf_s401/ad4/data/manifests/ad4_eval.csv"
rows = list(csv.DictReader(open(EV)))
def pool(r):
    if r["label"] == "1": return f"{r['set']}:{r['family']}:morph"
    if r["variant"] == "orig": return f"{r['set']}:genuine_raw"
    return f"{r['set']}:{r['family']}:genuine_history"
P = [pool(r) for r in rows]; ids = [r["id"] for r in rows]
out = []
def add(method, seed, z):
    assert list(z["id"]) == ids
    out.append((method, seed, z["score"], z["score_noTTA"]))
for rec, d, name in (("m3", "results_wcss_m3", "vitb16"), ("m3l", "results_m3l_registered", "vitl14")):
    for arm, lab in (("mf", "morph-free"), ("perm", "label-permuted")):
        for s in range(401, 406):
            t = f"AD4_{rec}{arm}_s{s}"
            with tarfile.open(f"{T}/{d}/{t}.tar") as tf:
                add(f"{lab}-{name}", s, np.load(io.BytesIO(tf.extractfile(f"{t}/scores_eval.npz").read())))
    add(f"untrained-{name}", 0, np.load(f"{T}/zero_step/{rec}/scores_eval.npz"))
n = len(ids)
pools = np.array(sorted(set(P))); pc = np.searchsorted(pools, np.array(P)).astype(np.int16)
methods = np.array(sorted({o[0] for o in out}))
np.savez_compressed(sys.argv[1], method_names=methods, pool_names=pools,
                    method=np.concatenate([np.full(n, list(methods).index(o[0]), np.int16) for o in out]),
                    seed=np.concatenate([np.full(n, o[1], np.int16) for o in out]), pool=np.tile(pc, len(out)),
                    score=np.concatenate([o[2] for o in out]).astype(np.float32),
                    score_noTTA=np.concatenate([o[3] for o in out]).astype(np.float32))
print(len(out), "networks x", n, "images;", collections.Counter(P).most_common(3))
