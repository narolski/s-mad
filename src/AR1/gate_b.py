"""AR1 gate G-b (twin validity, P1) with the glintr100 FR oracle (fr.py, registered X3 route). No detector score is read.

Primary pool: reference = the host's independent photo R (not used in any build); tau = the 99.9th percentile of the
impostor scores cos(H_p, R_q), p != q, same database (FMR 1/1,000). FRLL: no independent photo exists; reference = H
(source-photo reference, labelled), impostors cos(H_p, S_q), p != q.
  oracle AUC  : score 1 - cos(image, ref_host), R4 (positive) vs R3, person bootstrap (a41_read.Draw), >= 0.90 passes
  verification: morphs verify against both (cos(R4, ref_host) >= tau and cos(R4, ref_B) >= tau) >= 70%; twins vs host
  negative ctrl: oracle AUC NC vs R3 in [0.40, 0.60]
Writes experiments/AR1/gate_b.json and OUT/fr_emb_built.npz.
"""
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ar1_common as K  # noqa: E402
import stats  # noqa: E402


def cp(k, n, alpha=0.05):
    from scipy.stats import beta
    lo = beta.ppf(alpha / 2, k, n - k + 1) if k > 0 else 0.0
    hi = beta.ppf(1 - alpha / 2, k + 1, n - k) if k < n else 1.0
    return [float(lo), float(hi)]


def main():
    man = list(csv.DictReader(open(K.OUT / "manifest.csv")))
    need = [r for r in man if r["pool"] in ("frgcferet", "frll") and r["rung"] in ("R3", "R4", "NC")]
    cache = K.OUT / "fr_emb_built.npz"
    if cache.exists():
        z = np.load(cache)
        E = dict(zip(z["path"].tolist(), z["emb"]))
        Fd = dict(zip(z["path"].tolist(), z["found"]))
    else:
        import fr
        paths = sorted({r["path"] for r in need})
        emb, found = fr.embed_paths(paths, log=lambda s: print(s, flush=True))
        np.savez(cache, path=np.array(paths), emb=emb, found=found)
        E, Fd = dict(zip(paths, emb)), dict(zip(paths, found))
    for f in ("pool_src_emb.npz",):
        z = np.load(K.OUT / f)
        E.update(zip(z["path"].tolist(), z["emb"]))
        Fd.update(zip(z["path"].tolist(), z["found"]))
    z = np.load(K.OUT / "frll_src_emb.npz")
    for s, e, f in zip(z["stem"].tolist(), z["emb"], z["found"]):
        p = str(K.OUT / "frll_src" / f"{s}.png")
        E[p], Fd[p] = e, f
    out = {}
    for pool, pcsv in (("frgcferet", K.OUT / "pool.csv"), ("frll", K.OUT / "pool_frll.csv")):
        P = {r["pid"]: r for r in csv.DictReader(open(pcsv))}
        ref = {pid: (r["R"] if pool == "frgcferet" else r["H"]) for pid, r in P.items()}
        ok = {pid for pid, p in ref.items() if p and Fd.get(p)}
        # impostors
        imp = []
        for db in sorted({r["db"] for r in P.values()}):
            ids = [pid for pid in sorted(ok) if P[pid]["db"] == db]
            Hm = np.stack([E[P[pid]["H"]] for pid in ids])
            Rm = np.stack([E[ref[pid]] if pool == "frgcferet" else E[P[pid]["S"]] for pid in ids])
            c = Hm @ Rm.T
            imp.append(c[~np.eye(len(ids), dtype=bool)])
        imp = np.concatenate(imp)
        tau = float(np.quantile(imp, 0.999))
        res = dict(reference="independent photo R" if pool == "frgcferet" else "source photo H (no independent photo)",
                   tau_fmr1e3=tau, n_impostor=int(len(imp)), hosts_with_reference=len(ok))
        for tool in ("opencv", "facemorpher"):
            rows = {g: [r for r in need if r["pool"] == pool and r["tool"] == tool and r["rung"] == g
                        and r["p1"] in ok and Fd[r["path"]]] for g in ("R3", "R4", "NC")}
            rows["R4"] = [r for r in rows["R4"] if r["p2"] in ok]
            nf = {g: sum(1 for r in need if r["pool"] == pool and r["tool"] == tool and r["rung"] == g
                         and not Fd[r["path"]]) for g in ("R3", "R4", "NC")}
            orc = {g: np.array([1 - float(E[r["path"]] @ E[ref[r["p1"]]]) for r in rows[g]]) for g in rows}
            pers = sorted(ok)
            D = stats.Draw(pers, 2000, [20261111, 2])
            a_mt, ci_mt = stats.wauc_ci(D, orc["R4"], [(r["p1"], r["p2"]) for r in rows["R4"]],
                                        orc["R3"], [(r["p1"],) for r in rows["R3"]])
            a_nc, ci_nc = stats.wauc_ci(D, orc["NC"], [(r["p1"],) for r in rows["NC"]],
                                        orc["R3"], [(r["p1"],) for r in rows["R3"]])
            vb = [(float(E[r["path"]] @ E[ref[r["p1"]]]) >= tau) and (float(E[r["path"]] @ E[ref[r["p2"]]]) >= tau)
                  for r in rows["R4"]]
            vh = [float(E[r["path"]] @ E[ref[r["p1"]]]) >= tau for r in rows["R3"]]
            vb_src = []
            for r in rows["R4"]:
                h, b = P[r["p1"]]["H"], P[r["p1"]]["B"]
                vb_src.append(float(E[r["path"]] @ E[h]) >= tau and float(E[r["path"]] @ E[b]) >= tau)
            k, n = int(sum(vb)), len(vb)
            res[tool] = dict(
                n=dict((g, len(v)) for g, v in rows.items()), no_face=nf,
                oracle_auc_morph_vs_twin=a_mt, ci95=ci_mt, pass_oracle=bool(a_mt >= 0.90),
                morph_verifies_both=k / n, morph_verifies_both_ci=cp(k, n), pass_verification=bool(k / n >= 0.70),
                morph_verifies_both_source_photos=float(np.mean(vb_src)),
                twin_verifies_host=float(np.mean(vh)), twin_verifies_host_ci=cp(int(sum(vh)), len(vh)),
                negative_control_auc_NC_vs_R3=a_nc, negative_control_ci95=ci_nc,
                pass_negative_control=bool(0.40 <= a_nc <= 0.60),
                G_b=bool(a_mt >= 0.90 and k / n >= 0.70 and 0.40 <= a_nc <= 0.60))
            print(pool, tool, json.dumps(res[tool]), flush=True)
        out[pool] = res
    json.dump(out, open(K.RES / "gate_b.json", "w"), indent=1)


if __name__ == "__main__":
    main()
