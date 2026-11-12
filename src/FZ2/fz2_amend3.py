"""FZ2 amendment 3 (registered in commit 3c7fbbd before this ran; post hoc in substance). Measurement only.
Identity check cos(a,b) = sum_k w_k c_k and band power shares; HN10 partial correlations within SAME. -> amend3.json"""
import csv, io, json, pathlib, sys, tarfile
import numpy as np
from scipy.stats import rankdata
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import fz2_amend2 as A2  # noqa: E402

OUT = pathlib.Path("/home/narolski/smad-next/experiments/FZ2_frozen-read-new-diffusion-ladder/amend3.json")


def bands(a, b):
    A = np.fft.fft2(a); Bf = np.fft.fft2(b); c, w, pa = [], [], []
    PA, PB = (abs(A) ** 2).sum(), (abs(Bf) ** 2).sum()
    for m in A2.MASKS:
        mm = np.broadcast_to(m, A.shape)
        a2, b2 = (abs(A[mm]) ** 2).sum(), (abs(Bf[mm]) ** 2).sum()
        c.append(float(np.real((A[mm] * np.conj(Bf[mm])).sum()) / np.sqrt(a2 * b2)))
        w.append(float(np.sqrt(a2 * b2 / (PA * PB)))); pa.append(float(a2 / PA))
    return np.array(c), np.array(w), np.array(pa)


def partial(y, x, Z):
    rk = lambda v: rankdata(v) / len(v)  # noqa: E731
    Zr = np.c_[np.ones(len(y)), np.column_stack([rk(z) for z in Z])]
    ry = rk(y) - Zr @ np.linalg.lstsq(Zr, rk(y), rcond=None)[0]
    rx = rk(x) - Zr @ np.linalg.lstsq(Zr, rk(x), rcond=None)[0]
    return float(np.corrcoef(ry, rx)[0, 1])


def main():
    L = {}
    for r in csv.DictReader(open("/mnt/t7/smad_next/FZ2/read_addon_items.csv")):
        if r["key"] == "SAME20":
            L[r["host"]] = float(r["lapvar_box"])
    rows = []
    for k in range(2, 7):
        t = A2.RR / f"DG1_addon_s{k}_codes.tar"
        with tarfile.open(t) as tf:
            m = [x for x in tf.getmembers() if x.name.endswith("codes.npz")][0]
            z = np.load(io.BytesIO(tf.extractfile(m).read()))
        names = list(z["names"]); X = z["xT"]; ix = {n: i for i, n in enumerate(names)}
        for j in csv.DictReader(open(f"/mnt/t7/smad_next/DG1/addon_jobs/addon_s{k}.csv")):
            if j["pool"] != "AO_SAME20":
                continue
            a = X[ix[j["src_a"]]].astype(np.float64); b = X[ix[j["src_b"]]].astype(np.float64)
            c, w, pa = bands(a, b)
            rows.append({"host": j["host"], "cos": A2.cos(a, b), "c": c, "w": w, "pa": pa, "L": L[j["host"]]})
    n = len(rows)
    cosv = np.array([r["cos"] for r in rows]); wsum = np.array([(r["w"] * r["c"]).sum() for r in rows])
    out = {"n_hosts": n, "registered_in": "3c7fbbd",
           "identity": {"pearson_cos_vs_weighted_band_mean": float(np.corrcoef(cosv, wsum)[0, 1]),
                        "max_abs_diff": float(np.abs(cosv - wsum).max()),
                        "band_power_share_median": [float(np.median([r["pa"][q] for r in rows])) for q in range(4)],
                        "weight_sum_median": float(np.median([r["w"].sum() for r in rows]))}}
    th = np.arccos(cosv); Ls = np.array([r["L"] for r in rows]); C = np.array([r["c"] for r in rows])
    p1 = partial(Ls, th, [C[:, 1], C[:, 2], C[:, 3]]); p2 = partial(Ls, C[:, 2], [th])
    rng = np.random.default_rng(20261112); r1, r2 = [], []
    for _ in range(2000):
        i = rng.integers(0, n, n)
        r1.append(partial(Ls[i], th[i], [C[i, 1], C[i, 2], C[i, 3]])); r2.append(partial(Ls[i], C[i, 2], [th[i]]))
    ci = lambda x: [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]  # noqa: E731
    out["partial_theta_L_given_c1c2c3"] = {"rho": p1, "ci": ci(r1)}
    out["partial_c2_L_given_theta"] = {"rho": p2, "ci": ci(r2)}
    a, b = out["partial_theta_L_given_c1c2c3"], out["partial_c2_L_given_theta"]
    sup = abs(a["rho"]) <= 0.10 and a["ci"][0] <= 0 <= a["ci"][1] and b["rho"] >= 0.20 and b["ci"][0] > 0
    fal = (not (a["ci"][0] <= 0 <= a["ci"][1]) and abs(a["rho"]) >= 0.10) or b["ci"][1] < 0.20
    out["reading_HN10"] = "supported" if sup else ("falsified" if fal else "not decided")
    print(json.dumps(out, indent=1)); json.dump(out, open(OUT, "w"), indent=1)


if __name__ == "__main__":
    main()
