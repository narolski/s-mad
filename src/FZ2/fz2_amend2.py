"""FZ2 amendment 2 (registered in commit c258935 before this ran; post hoc in substance). Measurement only.
Band-wise and 8x8 low-pass cosines of the inverted noise maps (host vs same-person / other-person partner) from the
saved codes of add-on shards 2-6, related to FZ2's Laplacian and P_XS within SAME and within X; separation of X vs SAME
by c0, low-pass cosine and theta. -> experiments/FZ2_.../amend2.json"""
import csv, hashlib, io, json, pathlib, sys, tarfile
import numpy as np
from scipy.stats import spearmanr, rankdata
sys.path.insert(0, "/home/narolski/smad-next/src/FZ1")
import fz1_common as K1  # noqa: E402

RR = pathlib.Path("/mnt/t7/smad_next/DG1/rented_results")
OUT = pathlib.Path("/home/narolski/smad-next/experiments/FZ2_frozen-read-new-diffusion-ladder/amend2.json")
fy = np.fft.fftfreq(256)[:, None]; fx = np.fft.fftfreq(256)[None, :]; RAD = np.sqrt(fx ** 2 + fy ** 2)
BANDS = [(0, 1 / 32), (1 / 32, 1 / 8), (1 / 8, 1 / 4), (1 / 4, 0.75)]
MASKS = [(RAD >= lo) & (RAD < hi) for lo, hi in BANDS]


def cos(u, v):
    return float(u.ravel() @ v.ravel() / np.linalg.norm(u) / np.linalg.norm(v))


def feats(a, b):
    A = np.fft.fft2(a); Bf = np.fft.fft2(b)
    bc = []
    for m in MASKS:
        mm = np.broadcast_to(m, A.shape)
        bc.append(float(np.real((A[mm] * np.conj(Bf[mm])).sum()) / np.sqrt((abs(A[mm]) ** 2).sum() * (abs(Bf[mm]) ** 2).sum())))
    lp = lambda u: u.reshape(3, 32, 8, 32, 8).mean((2, 4))  # noqa: E731
    c = cos(a, b)
    return {"theta": float(np.arccos(np.clip(c, -1, 1))), "c0": bc[0], "c1": bc[1], "c2": bc[2], "c3": bc[3], "lp8": cos(lp(a), lp(b))}


def ci(x):
    x = np.asarray(x); x = x[np.isfinite(x)]
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


def wspear(x, y, w):
    k = np.round(w).astype(int)
    if k.sum() < 5:
        return np.nan
    return float(np.corrcoef(rankdata(np.repeat(x, k)), rankdata(np.repeat(y, k)))[0, 1])


def main():
    items = {}
    for r in csv.DictReader(open("/mnt/t7/smad_next/FZ2/read_addon_items.csv")):
        if r["key"] in ("SAME20", "X20"):
            items[(r["key"], r["host"])] = r
    rows = []
    for k in range(2, 7):
        t = RR / f"DG1_addon_s{k}_codes.tar"
        exp = open(f"{t}.sha256").read().split()[0]
        h = hashlib.sha256()
        with open(t, "rb") as f:
            for blk in iter(lambda: f.read(1 << 22), b""):
                h.update(blk)
        assert h.hexdigest() == exp, t
        with tarfile.open(t) as tf:
            m = [x for x in tf.getmembers() if x.name.endswith("codes.npz")][0]
            z = np.load(io.BytesIO(tf.extractfile(m).read()))
        names = list(z["names"]); X = z["xT"]; ix = {n: i for i, n in enumerate(names)}
        jobs = list(csv.DictReader(open(f"/mnt/t7/smad_next/DG1/addon_jobs/addon_s{k}.csv")))
        same = {j["host"]: (j["src_a"], j["src_b"]) for j in jobs if j["pool"] == "AO_SAME20"}
        xx = {j["host"]: (j["src_b"], j["partner"]) for j in jobs if j["pool"] == "AO_X20"}
        for host, (sa, sb) in same.items():
            a = X[ix[sa]].astype(np.float64); b = X[ix[sb]].astype(np.float64)
            ps, partner = xx[host]; p = X[ix[ps]].astype(np.float64)
            rs, rx = items[("SAME20", host)], items[("X20", host)]
            rows.append({"host": host, "partner": partner, "shard": k, "same": feats(a, b), "x": feats(a, p),
                         "L_same": float(rs["lapvar_box"]), "L_x": float(rx["lapvar_box"]),
                         "P_same": float(rs["clip_mad|P_XS"]), "P_x": float(rx["clip_mad|P_XS"])})
        print(f"shard {k}: {len(same)} hosts", flush=True)
    n = len(rows)
    allp = sorted({r["pid"] for r in csv.DictReader(open("/home/narolski/smad-next/experiments/AR1/pool.csv"))})
    D = K1.Draw(allp, 10000, [20261112, 2, 1])
    ws = D.w([(r["host"],) for r in rows]); wx = D.w([(r["host"], r["partner"]) for r in rows])
    out = {"n_hosts": n, "registered_in": "c258935", "shards": [2, 3, 4, 5, 6]}
    keys = ("theta", "c0", "c1", "c2", "c3", "lp8")
    out["medians"] = {f"{g}_{k}": float(np.median([r[g][k] for r in rows])) for g in ("same", "x") for k in keys}
    # within-condition Spearman
    corr = {}
    for g, L, P, w in (("same", "L_same", "P_same", ws), ("x", "L_x", "P_x", wx)):
        for k in keys:
            v = np.array([r[g][k] for r in rows])
            for oname, oc in (("L", L), ("P_XS", P)):
                o = np.array([r[oc] for r in rows])
                pt = float(spearmanr(v, o)[0])
                rep = [wspear(v, o, w[bb]) for bb in range(2000)]
                corr[f"{g}: {k} vs {oname}"] = {"rho": pt, "ci": ci(rep)}
    out["within_spearman"] = corr
    # separation X vs SAME (x pair should have lower cosine / larger theta)
    sep = {}
    for k in keys:
        vx = np.array([r["x"][k] for r in rows]); vs = np.array([r["same"][k] for r in rows])
        sx, ss = (vx, vs) if k == "theta" else (-vx, -vs)
        rep = K1.wauc(sx, ss, wx, ws)
        sep[k] = {"auc_X_vs_SAME": K1.auc(sx, ss), "ci": ci(rep)}
    out["separation"] = sep
    # joint model within SAME
    L = np.array([r["L_same"] for r in rows]); c0 = np.array([r["same"]["c0"] for r in rows]); th = np.array([r["same"]["theta"] for r in rows])
    rk = lambda v: (rankdata(v) - 1) / (len(v) - 1)  # noqa: E731

    def dr2(idx):
        y, a1, a2 = rk(L[idx]), rk(c0[idx]), rk(th[idx])
        X1 = np.c_[np.ones(len(idx)), a1]; X2 = np.c_[X1, a2]
        r1 = y - X1 @ np.linalg.lstsq(X1, y, rcond=None)[0]; r2 = y - X2 @ np.linalg.lstsq(X2, y, rcond=None)[0]
        tss = ((y - y.mean()) ** 2).sum()
        return 1 - (r1 ** 2).sum() / tss, 1 - (r2 ** 2).sum() / tss
    a, b = dr2(np.arange(n))
    rng = np.random.default_rng(20261112)
    reps = [dr2(rng.integers(0, n, n)) for _ in range(2000)]
    d = np.array([y - x for x, y in reps])
    out["joint_SAME_L"] = {"R2_c0": a, "R2_c0_theta": b, "dR2_theta": b - a, "dR2_ci": ci(d)}
    r = corr["same: c0 vs L"]
    sup = r["rho"] >= 0.30 and r["ci"][0] > 0.10 and (ci(d)[0] <= 0 or (b - a) < 0.02)
    fal = r["ci"][1] < 0.10 or ((b - a) >= 0.02 and ci(d)[0] > 0)
    out["reading_HA_shared"] = "supported" if sup else ("falsified" if fal else "not decided")
    print(json.dumps({k: out[k] for k in ("medians", "separation", "joint_SAME_L", "reading_HA_shared")}, indent=1))
    print({k: (round(v["rho"], 3), [round(x, 3) for x in v["ci"]]) for k, v in corr.items()})
    json.dump(out, open(OUT, "w"), indent=1)


if __name__ == "__main__":
    main()
