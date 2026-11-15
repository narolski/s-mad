"""SM1 amendment A21 (registered before computing): H-A, H-B, H-C, H-D; zero GPU, development data only.

  python3 -I a21_read.py -> RES/a21_read.json
"""
import csv
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import sm1_stats as S  # noqa: E402
import hn2_incr as I  # noqa: E402
import a19_floor as AF  # noqa: E402

G = pathlib.Path("/mnt/t7/smad_next/DG1/gen")
BOX = (slice(70, 221), slice(64, 193))
B = 10000


def rank(x):
    r = np.empty(len(x))
    r[np.argsort(x, kind="stable")] = np.arange(len(x))
    return r


def partial(a, b, X, w=None):
    Xr = np.c_[np.ones(len(a)), np.apply_along_axis(rank, 0, X)] if X.shape[1] else np.ones((len(a), 1))
    res = lambda u: u - Xr @ np.linalg.lstsq(Xr, u, rcond=None)[0]  # noqa: E731
    ea, eb = res(rank(a)), res(rank(b))
    if w is None:
        return float(np.corrcoef(ea, eb)[0, 1])
    m = lambda v: (w * v).sum() / w.sum()  # noqa: E731
    ca, cb = ea - m(ea), eb - m(eb)
    return float(m(ca * cb) / np.sqrt(m(ca * ca) * m(cb * cb)))


def boot(a, b, X, units):
    uc = sorted(set(units))
    cp = {c: k for k, c in enumerate(uc)}
    Cb = np.random.default_rng(K.SEED).multinomial(len(uc), np.full(len(uc), 1 / len(uc)), size=B).astype(float)
    W = Cb[:, [cp[u] for u in units]]
    d = np.array([partial(a, b, X, w) for w in W])
    lo, hi = np.percentile(d[np.isfinite(d)], [2.5, 97.5])
    return dict(rho=round(partial(a, b, X), 4), ci=[round(float(lo), 4), round(float(hi), 4)], n=len(a))


def img(path):
    from PIL import Image
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float64)


def hf_energy(a):
    g = a.mean(2)[BOX]
    P = np.abs(np.fft.fftshift(np.fft.fft2(g - g.mean()))) ** 2
    h, w = P.shape
    yy, xx = np.mgrid[:h, :w]
    r = np.sqrt(((yy - h / 2) / (h / 2)) ** 2 + ((xx - w / 2) / (w / 2)) ** 2)
    return float(P[r > 0.5].sum() / P.sum())


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    items = list(csv.DictReader(open("/mnt/t7/smad_next/FZ2/read_addon_items.csv")))
    by = {(r["key"], r["host"]): r for r in items}
    out = {}
    # ---------------- H-A (A16 scores, all 536 hosts)
    rows16 = list(csv.DictReader(open(K.OUT / "dev_a16/sm1_dev16_eval.csv")))
    fam, host = {}, {}
    for r in rows16:
        fam.setdefault(r["family"], []).append(r["id"])
        host[r["id"]] = r["variant"]
    Fr, Re = fam["FRESH1_20"], fam["REC20"]
    key = lambda i: (i.split(":")[1], ":".join(i.split(":")[2:]))  # noqa: E731
    png = {i: float(by[key(i)]["png_bytes"]) for i in Fr + Re}
    hfe = {i: hf_energy(img(G / by[key(i)]["list"] / by[key(i)]["id"])) for i in Fr + Re}
    hosts = sorted(set(host.values()))
    hp = {h: k for k, h in enumerate(hosts)}
    Cb = np.random.default_rng(K.SEED).multinomial(len(hosts), np.full(len(hosts), 1 / len(hosts)), size=B).astype(float)
    Wh = lambda ids: Cb[:, [hp[host[i]] for i in ids]]  # noqa: E731
    ha = {}
    for arm in ("a", "e", "f"):
        ha[arm] = {}
        for nm, v in (("png", png), ("hf", hfe)):
            q = np.quantile([v[i] for i in Fr + Re], [0.2, 0.4, 0.6, 0.8])
            st = {i: int(np.searchsorted(q, v[i])) for i in Fr + Re}
            pts, drs = [], []
            for s in (401, 402):
                z = np.load(K.OUT / f"results_rented/dev16/SM1E_{arm}_s{s}/scores_audit.npz")
                p = np.clip(z["score_noTTA"].astype(float), 1e-7, 1 - 1e-7)
                zi = dict(zip([str(i) for i in z["id"]], np.log(p / (1 - p))))
                g = lambda ids: np.array([zi[i] for i in ids])  # noqa: E731
                pt, dr, wt = 0.0, 0.0, 0.0
                for k in range(5):
                    a_, b_ = [i for i in Fr if st[i] == k], [i for i in Re if st[i] == k]
                    if a_ and b_:
                        w = len(a_) * len(b_)
                        pt += w * float(S.wauc(g(a_), g(b_), np.ones((1, len(a_))), np.ones((1, len(b_))))[0])
                        dr = dr + w * S.wauc(g(a_), g(b_), Wh(a_), Wh(b_))
                        wt += w
                pts.append(pt / wt)
                drs.append(dr / wt)
            ha[arm][nm] = dict(auc=round(float(np.mean(pts)), 4), seeds=[round(x, 4) for x in pts],
                               ci=[round(x, 4) for x in S.ci(np.mean(drs, 0))])
    e = ha["e"]
    ha["verdict_e"] = ("supported" if max(e["png"]["auc"], e["hf"]["auc"]) >= 0.45 else
                       "falsified" if max(e["png"]["auc"], e["hf"]["auc"]) <= 0.40 else "undecided")
    out["H-A"] = ha
    # ---------------- H-B (stored rented A18 scores, test X20)
    pool = {p["pid"]: p for p in csv.DictReader(open("/home/narolski/smad-next/experiments/AR1/pool.csv"))}
    net = {}
    for s in (401, 402):
        z = np.load(K.OUT / f"results_rented/hn2/HN2_RS_s{s}/hn2test/scores_eval.npz")
        p = np.clip(z["score_noTTA"].astype(float), 1e-7, 1 - 1e-7)
        net[s] = dict(zip([str(i) for i in z["id"]], np.log(p / (1 - p))))
    rows = [r for r in I.test_rows() if r["y"] == 1]
    lg = np.array([np.mean([net[s][r["id"]] for s in (401, 402)]) for r in rows])
    dis = np.array([1 - float(pool[":".join(r["id"].split(":")[2:])]["cos_HB"]) for r in rows])
    F = np.array([r["f"] for r in rows])
    hb = dict(all_given_F=boot(lg, dis, F, [r["cycle"] for r in rows]), raw_spearman=round(partial(lg, dis, np.zeros((len(lg), 0))), 4))
    C = AF.codes()
    s6 = [k for k, r in enumerate(rows) if (r["id"].split(":")[1], ":".join(r["id"].split(":")[2:])) in C
          and by[("X20", ":".join(r["id"].split(":")[2:]))]["list"] == "addon_s6"]
    F6 = np.array([list(rows[k]["f"]) + [C[("X20", ":".join(rows[k]["id"].split(":")[2:]))][c] for c in ("c0", "c1", "c2", "c3")]
                   for k in s6])
    hb["shard6_given_F_c0c3"] = boot(lg[s6], dis[s6], F6, [rows[k]["cycle"] for k in s6])
    a = hb["all_given_F"]
    hb["verdict"] = ("falsified (no identity reading)" if a["rho"] <= 0.05 and a["ci"][1] < 0.20 else
                     "two-identity reading supported" if a["rho"] >= 0.20 else "undecided")
    hb["label"] = "confirmation test (raw ρ −0.10 known post hoc)"
    out["H-B"] = hb
    # ---------------- H-C and H-D (A19 CPU scores, ranks only)
    test_hosts = sorted({r["src_id"] for r in csv.DictReader(open(K.OUT / "hn2/sm1_hn2_test.csv"))})
    cpu = {}
    for s in (401, 402):
        z = np.load(K.OUT / f"a19/res/HN2_RS_s{s}/scores_audit.npz")
        p = np.clip(z["score_noTTA"].astype(float), 1e-7, 1 - 1e-7)
        cpu[s] = dict(zip([str(i) for i in z["id"]], np.log(p / (1 - p))))
    sc = lambda k, h: np.mean([cpu[s][f"a19:{k}:{h}"] for s in (401, 402)])  # noqa: E731
    hc = {}
    for k in ("SEMS20", "NOISES20"):
        hs = [h for h in test_hosts if (k, h) in by and ("REC20", h) in by]
        mse = np.array([float(((img(G / by[(k, h)]["list"] / by[(k, h)]["id"])[BOX] -
                                img(G / by[("REC20", h)]["list"] / by[("REC20", h)]["id"])[BOX]) ** 2).mean()) for h in hs])
        Xs = np.array([[np.log(float(by[(k, h)]["lapvar_box"])), np.log(float(by[(k, h)]["png_bytes"])),
                        float(by[(k, h)]["asym_box"]), float(by[(k, h)]["d"])] for h in hs])
        Xs = Xs[:, np.isfinite(Xs).all(0)]
        v = np.array([sc(k, h) for h in hs])
        hc[k] = boot(v, mse, Xs, hs)
    hc["verdict"] = ("supported" if all(hc[k]["rho"] >= 0.30 for k in ("SEMS20", "NOISES20")) else
                     "falsified" if all(hc[k]["rho"] <= 0.10 for k in ("SEMS20", "NOISES20")) else "undecided")
    hc["label"] = "A19 CPU scores: platform not equivalent, ranks only (rank agreement 0.99999)"
    out["H-C"] = hc
    # H-D
    dropped = set(json.load(open(K.OUT / "hn2/lists.json"))["dropped_crossing_X20"])
    tr = [r for r in items if r["key"] in ("X20", "SAME20") and r["list"] in {f"addon_s{k}" for k in range(6)}
          and r["id"] not in dropped and (r["key"], r["host"]) in C]

    def fv(r, pair_key):
        c = C[pair_key]
        return [c["theta"], np.log(float(r["lapvar_box"])), np.log(float(r["png_bytes"])), float(r["asym_box"]),
                float(r["d"])] + [c[x] for x in ("c0", "c1", "c2", "c3", "lp8", "zcos")]
    Xtr = np.array([fv(r, (r["key"], r["host"])) for r in tr])
    ytr = np.array([1 if r["key"] == "X20" else 0 for r in tr])
    fl = AF.lr_fit(Xtr, ytr)
    h6 = [h for h in test_hosts if by[("X20", h)]["list"] == "addon_s6" and ("X20", h) in C and ("SAME20", h) in C]
    hd = {}
    for kx, ks in (("NOISEX20", "NOISES20"), ("SEMX20", "SEMS20")):
        fx = fl(np.array([fv(by[(kx, h)], ("X20", h)) for h in h6]))
        fs = fl(np.array([fv(by[(ks, h)], ("SAME20", h)) for h in h6]))
        nx, ns = np.array([sc(kx, h) for h in h6]), np.array([sc(ks, h) for h in h6])
        A = lambda p_, n_: float(S.wauc(p_, n_, np.ones((1, len(p_))), np.ones((1, len(n_))))[0])  # noqa: E731
        hd[f"{kx}_over_{ks}"] = dict(floor=round(A(fx, fs), 4), network=round(A(nx, ns), 4),
                                     diff=round(A(fx, fs) - A(nx, ns), 4), n_hosts=len(h6))
    diffs = [abs(v["diff"]) for v in hd.values()]
    hd["verdict"] = "supported" if max(diffs) <= 0.05 else ("falsified" if max(diffs) > 0.10 else "undecided")
    hd["label"] = "network: A19 CPU scores (ranks only); shard 6"
    out["H-D"] = hd
    json.dump(out, open(K.RES / "a21_read.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
