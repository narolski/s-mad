"""SM1 A19 H-N2 (registered 71a08f6): identity in the output. glintr100 cosine of each test X20 render to its partner's
source photo and to its host's source photo (AR1 `fr.py` route), on CPU (GPU hidden). Within X20 on shard 6 (saved noise
maps), partial Spearman ρ of the A18 network logit (2-seed mean 401, 402) with the render-to-partner cosine given the
extended floor (F + c0-c3 + low-pass + semantic-code cosine; ranks residualised by least squares); partner-cycle
bootstrap B = 10,000 (rows resampled with their cycle counts). Falsified if ρ ≤ 0.10 with upper bound < 0.25;
supported if ρ ≥ 0.25 with lower bound > 0.10; else undecided. Descriptive: all 133 X20 rows given F.

  CUDA_VISIBLE_DEVICES= python3 -I a19_hn2id.py -> RES/a19_hn2id.json
"""
import csv
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, "/home/narolski/smad-next/src/AR1")
import sm1_common as K  # noqa: E402
import hn2_incr as I  # noqa: E402
import a19_floor as AF  # noqa: E402


def rank(x):
    r = np.empty(len(x))
    r[np.argsort(x, kind="stable")] = np.arange(len(x))
    return r


def resid(u, X):
    Xc = np.c_[np.ones(len(u)), X]
    return u - Xc @ np.linalg.lstsq(Xc, u, rcond=None)[0]


def partial(a, b, X, w=None):
    ra, rb = rank(a), rank(b)
    Xr = np.apply_along_axis(rank, 0, X)
    ea, eb = resid(ra, Xr), resid(rb, Xr)
    if w is None:
        return float(np.corrcoef(ea, eb)[0, 1])
    m = lambda v: (w * v).sum() / w.sum()  # noqa: E731
    ca, cb = ea - m(ea), eb - m(eb)
    return float(m(ca * cb) / np.sqrt(m(ca * ca) * m(cb * cb)))


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    sys.path.insert(0, "/home/narolski/mambamorph-code")
    import dmad.quads.gpuface as GF                       # deviation note (A19): run the onnx2torch nets on the CPU
    _init = GF.TorchSession.__init__
    GF.TorchSession.__init__ = lambda self, sess, path, device="cuda": _init(self, sess, path, "cpu")
    import fr
    pool = {p["pid"]: p for p in csv.DictReader(open("/home/narolski/smad-next/experiments/AR1/pool.csv"))}
    jobs = {}
    for k in (6, 7):
        for j in csv.DictReader(open(f"/mnt/t7/smad_next/DG1/addon_jobs/addon_s{k}.csv")):
            if j["pool"] == "AO_X20":
                jobs[j["host"]] = j
    rows = [r for r in I.test_rows() if r["y"] == 1]
    items = {r["id"]: r for r in csv.DictReader(open("/mnt/t7/smad_next/FZ2/read_addon_items.csv")) if r["key"] == "X20"}

    def photo(name):
        db, subj, kind = name.split("_")[0], name.split("_")[1], name.split("_")[2]
        return pool[f"{db}:{subj}"][kind]
    paths, meta = [], []
    for r in rows:
        a = items[r["item_id"]]
        j = jobs[a["host"]]
        rp = str(pathlib.Path("/mnt/t7/smad_next/DG1/gen") / a["list"] / a["id"])
        paths += [rp, photo(j["src_b"]), photo(j["src_a"])]
        meta.append((r, a))
    E, F = fr.embed_paths(paths)
    E = E.reshape(len(rows), 3, -1)
    found = F.reshape(len(rows), 3).all(1)
    cosP = (E[:, 0] * E[:, 1]).sum(1)
    cosH = (E[:, 0] * E[:, 2]).sum(1)
    net = {}
    for s in (401, 402):
        z = np.load(K.OUT / f"results_rented/hn2/HN2_RS_s{s}/hn2test/scores_eval.npz")
        p = np.clip(z["score_noTTA"].astype(float), 1e-7, 1 - 1e-7)
        net[s] = dict(zip([str(i) for i in z["id"]], np.log(p / (1 - p))))
    lg = np.array([np.mean([net[s][r["id"]] for s in (401, 402)]) for r, _ in meta])
    C = AF.codes()
    out = dict(n=len(rows), faces_found=int(found.sum()), cos_render_partner_median=round(float(np.median(cosP)), 4),
               cos_render_host_median=round(float(np.median(cosH)), 4))
    B = 10000
    for tag, sel, ext in (("shard6_extfloor", lambda a: a["list"] == "addon_s6" and (a["key"], a["host"]) in C, True),
                          ("all_given_F", lambda a: True, False)):
        ix = [i for i, (r, a) in enumerate(meta) if sel(a) and found[i]]
        X = np.array([AF_fvec(meta[i][0], meta[i][1], C, ext) for i in ix])
        a_, b_ = lg[ix], cosP[ix]
        pt = partial(a_, b_, X)
        cyc = [meta[i][0]["cycle"] for i in ix]
        uc = sorted(set(cyc))
        cp = {c: k for k, c in enumerate(uc)}
        Cb = np.random.default_rng(K.SEED).multinomial(len(uc), np.full(len(uc), 1 / len(uc)), size=B).astype(float)
        Wr = Cb[:, [cp[c] for c in cyc]]
        dr = np.array([partial(a_, b_, X, w) for w in Wr])
        lo, hi = np.percentile(dr[np.isfinite(dr)], [2.5, 97.5])
        out[tag] = dict(n=len(ix), partial_rho=round(pt, 4), ci=[round(float(lo), 4), round(float(hi), 4)])
    sh = out["shard6_extfloor"]
    out["verdict"] = ("falsified" if sh["partial_rho"] <= 0.10 and sh["ci"][1] < 0.25 else
                      "supported" if sh["partial_rho"] >= 0.25 and sh["ci"][0] > 0.10 else "undecided")
    json.dump(out, open(K.RES / "a19_hn2id.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


def AF_fvec(r, a, C, ext):
    f = list(r["f"])
    if ext:
        c = C[(a["key"], a["host"])]
        f += [c[k] for k in ("c0", "c1", "c2", "c3", "lp8", "zcos")]
    return f


if __name__ == "__main__":
    main()
