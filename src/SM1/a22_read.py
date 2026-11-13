"""SM1 amendment A22 (registered 73bf220 before computing): H-E (rung-matched floor), H-F (descriptive), H-G (arm a).

  python3 -I a22_read.py -> RES/a22_read.json
"""
import csv
import io
import json
import pathlib
import sys
import tarfile

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import sm1_stats as S  # noqa: E402
import a19_floor as AF  # noqa: E402

A = lambda p, n: float(S.wauc(np.asarray(p), np.asarray(n), np.ones((1, len(p))), np.ones((1, len(n))))[0])  # noqa: E731


def rank(x):
    x = np.asarray(x, float)
    o = np.argsort(x, kind="stable")
    r = np.empty(len(x))
    r[o] = np.arange(len(x))
    for v in np.unique(x):                                   # mid-ranks for ties
        m = x == v
        r[m] = r[m].mean()
    return r


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    items = list(csv.DictReader(open("/mnt/t7/smad_next/FZ2/read_addon_items.csv")))
    by = {(r["key"], r["host"]): r for r in items}
    C = AF.codes()
    out = {}
    # ---------- H-E
    dropped = set(json.load(open(K.OUT / "hn2/lists.json"))["dropped_crossing_X20"])
    tr = [r for r in items if r["key"] in ("X20", "SAME20") and r["list"] in {f"addon_s{k}" for k in range(6)}
          and r["id"] not in dropped and (r["key"], r["host"]) in C]

    def fv(r, noise_pair, sem_pair):
        n, z = C[noise_pair], C[sem_pair]
        return [n["theta"], np.log(float(r["lapvar_box"])), np.log(float(r["png_bytes"])), float(r["asym_box"]),
                float(r["d"])] + [n[x] for x in ("c0", "c1", "c2", "c3", "lp8")] + [z["zcos"]]
    Xtr = np.array([fv(r, (r["key"], r["host"]), (r["key"], r["host"])) for r in tr])
    ytr = np.array([1 if r["key"] == "X20" else 0 for r in tr])
    fl = AF.lr_fit(Xtr, ytr)
    test_hosts = sorted({r["src_id"] for r in csv.DictReader(open(K.OUT / "hn2/sm1_hn2_test.csv"))})
    h6 = [h for h in test_hosts if by[("X20", h)]["list"] == "addon_s6" and ("X20", h) in C and ("SAME20", h) in C]
    cpu = {}
    for s in (401, 402):
        z = np.load(K.OUT / f"a19/res/HN2_RS_s{s}/scores_audit.npz")
        p = np.clip(z["score_noTTA"].astype(float), 1e-7, 1 - 1e-7)
        cpu[s] = dict(zip([str(i) for i in z["id"]], np.log(p / (1 - p))))
    sc = lambda k, h: float(np.mean([cpu[s][f"a19:{k}:{h}"] for s in (401, 402)]))  # noqa: E731
    pairs = {"NOISEX20": ("X20", "SAME20"), "NOISES20": ("SAME20", "SAME20"),     # (noise-map pair, semantic pair)
             "SEMX20": ("SAME20", "X20"), "SEMS20": ("SAME20", "SAME20")}
    fs = {k: fl(np.array([fv(by[(k, h)], (pairs[k][0], h), (pairs[k][1], h)) for h in h6])) for k in pairs}
    he = {}
    for kx, ks in (("NOISEX20", "NOISES20"), ("SEMX20", "SEMS20")):
        f_auc = A(fs[kx], fs[ks])
        n_auc = A([sc(kx, h) for h in h6], [sc(ks, h) for h in h6])
        he[f"{kx}_over_{ks}"] = dict(floor_matched=round(f_auc, 4), network=round(n_auc, 4), diff=round(f_auc - n_auc, 4))
    d = [abs(v["diff"]) for v in he.values()]
    he["n_hosts"] = len(h6)
    he["verdict"] = "matches" if max(d) <= 0.05 else ("does not match" if max(d) > 0.10 else "undecided")
    out["H-E"] = he
    # ---------- H-F (descriptive)
    t = tarfile.open("/mnt/t7/smad_next/DG1/rented_results/DG1_addon_s6_codes.tar")
    zc = fr = None
    for m in t.getmembers():
        if m.name.endswith("codes.npz"):
            zc = np.load(io.BytesIO(t.extractfile(m).read()))
        if m.name.endswith("fresh.npz"):
            fr = np.load(io.BytesIO(t.extractfile(m).read()))
    ix = {n: i for i, n in enumerate(zc["names"])}
    fix = {k: i for i, k in enumerate(fr["keys"])}
    cosv = lambda u, v: float(u.ravel() @ v.ravel() / np.linalg.norm(u) / np.linalg.norm(v))  # noqa: E731
    dist = {k: [] for k in ("REC20", "NOISES20", "SEMS20", "FRESH1_20", "NOISEX20", "SEMX20")}
    for h in h6:
        hn = h.replace(":", "_") + "_H"
        xa = zc["xT"][ix[hn]].astype(np.float64)
        dist["REC20"].append(0.0)
        dist["SEMS20"].append(0.0)
        dist["SEMX20"].append(0.0)
        dist["NOISES20"].append(1 - np.cos(C[("SAME20", h)]["theta"] / 2))
        dist["NOISEX20"].append(1 - np.cos(C[("X20", h)]["theta"] / 2))
        dist["FRESH1_20"].append(1 - cosv(fr["eps"][fix[f"{h}|1"]].astype(np.float64), xa))
    rungs = list(dist)
    md = [float(np.mean(dist[k])) for k in rungs]
    ms = [float(np.mean([sc(k, h) for h in h6])) for k in rungs]
    rho = float(np.corrcoef(rank(md), rank(ms))[0, 1])
    out["H-F"] = dict(rungs=rungs, mean_noise_distance=[round(x, 4) for x in md], mean_network_logit=[round(x, 3) for x in ms],
                      spearman=round(rho, 4), label="descriptive (6 points)",
                      reading="≥ 0.8 as predicted" if rho >= 0.8 else ("≤ 0.4 (falsified)" if rho <= 0.4 else "between"))
    # ---------- H-G (arm a; arm e control)
    rows16 = list(csv.DictReader(open(K.OUT / "dev_a16/sm1_dev16_eval.csv")))
    fam = {}
    for r in rows16:
        fam.setdefault(r["family"], []).append(r["id"])
    key = lambda i: (i.split(":")[1], ":".join(i.split(":")[2:]))  # noqa: E731
    Fr, Re = fam["FRESH1_20"], fam["REC20"]
    png = {i: float(by[key(i)]["png_bytes"]) for i in Fr + Re}
    q = np.quantile([png[i] for i in Fr + Re], np.arange(0.1, 1.0, 0.1))
    dec = {i: int(np.searchsorted(q, png[i])) for i in Fr + Re}
    rp = np.array([png[i] for i in Re])
    nn = {i: Re[int(np.argmin(np.abs(rp - png[i])))] for i in Fr}
    hg = {}
    for arm in ("a", "e"):
        hg[arm] = {}
        for s in (401, 402):
            z = np.load(K.OUT / f"results_rented/dev16/SM1E_{arm}_s{s}/scores_audit.npz")
            p = np.clip(z["score_noTTA"].astype(float), 1e-7, 1 - 1e-7)
            zi = dict(zip([str(i) for i in z["id"]], np.log(p / (1 - p))))
            pt, wt = 0.0, 0.0
            for k in range(10):
                a_, b_ = [i for i in Fr if dec[i] == k], [i for i in Re if dec[i] == k]
                if a_ and b_:
                    w = len(a_) * len(b_)
                    pt += w * A([zi[i] for i in a_], [zi[i] for i in b_])
                    wt += w
            nn_auc = float(np.mean([1.0 if zi[i] > zi[nn[i]] else 0.5 if zi[i] == zi[nn[i]] else 0.0 for i in Fr]))
            hg[arm][str(s)] = dict(decile=round(pt / wt, 4), nearest_neighbour=round(nn_auc, 4))
    vals = [hg["a"][s][m] for s in ("401", "402") for m in ("decile", "nearest_neighbour")]
    hg["verdict_a"] = "supported" if min(vals) >= 0.50 else ("falsified" if max(vals) <= 0.45 else "undecided")
    hg["decile_counts_FRESH_REC"] = [[sum(dec[i] == k for i in Fr), sum(dec[i] == k for i in Re)] for k in range(10)]
    out["H-G"] = hg
    json.dump(out, open(K.RES / "a22_read.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
