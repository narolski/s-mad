"""SM1 A19 H-N4 (registered 71a08f6): FRESH1_20 over REC20 for the A16 fits, stratified by face-box Laplacian quintiles
(pooled over FRESH1_20 + REC20; weights n_F x n_R per stratum); 2-seed means, host bootstrap (A16 draws).
Decision on arm e: supported if ≥ 0.45; falsified if ≤ 0.40; otherwise undecided. Arms a, f reported.

  python3 -I a19_hn4.py -> RES/a19_hn4.json
"""
import csv
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import sm1_stats as S  # noqa: E402

D = K.OUT / "results_rented/dev16"


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    rows = list(csv.DictReader(open(K.OUT / "dev_a16/sm1_dev16_eval.csv")))
    lap = {f"dev16:{r['key']}:{r['host']}": float(r["lapvar_box"]) for r in
           csv.DictReader(open("/mnt/t7/smad_next/FZ2/read_addon_items.csv")) if r["key"] in ("FRESH1_20", "REC20")}
    fam, host = {}, {}
    for r in rows:
        fam.setdefault(r["family"], []).append(r["id"])
        host[r["id"]] = r["variant"]
    hosts = sorted(set(host.values()))
    hp = {h: i for i, h in enumerate(hosts)}
    Cb = np.random.default_rng(K.SEED).multinomial(len(hosts), np.full(len(hosts), 1 / len(hosts)), size=10000).astype(float)
    W = lambda ids: Cb[:, [hp[host[i]] for i in ids]]  # noqa: E731
    Fr, Re = fam["FRESH1_20"], fam["REC20"]
    v = np.array([lap[i] for i in Fr + Re])
    q = np.quantile(v, [0.2, 0.4, 0.6, 0.8])
    st = {i: int(np.searchsorted(q, lap[i])) for i in Fr + Re}
    per = {}
    for d in sorted(D.glob("SM1E_*")):
        if not d.is_dir():
            continue
        z = np.load(d / "scores_audit.npz")
        p = np.clip(z["score_noTTA"].astype(float), 1e-7, 1 - 1e-7)
        zi = dict(zip([str(i) for i in z["id"]], np.log(p / (1 - p))))
        g = lambda ids: np.array([zi[i] for i in ids])  # noqa: E731
        pt, dr, wt, raw = 0.0, 0.0, 0.0, None
        for k in range(5):
            a, b = [i for i in Fr if st[i] == k], [i for i in Re if st[i] == k]
            if a and b:
                w = len(a) * len(b)
                pt += w * float(S.wauc(g(a), g(b), np.ones((1, len(a))), np.ones((1, len(b))))[0])
                dr = dr + w * S.wauc(g(a), g(b), W(a), W(b))
                wt += w
        raw = float(S.wauc(g(Fr), g(Re), np.ones((1, len(Fr))), np.ones((1, len(Re))))[0])
        per.setdefault(d.name.split("_")[1], []).append((pt / wt, dr / wt, raw))
    out = {}
    for arm, lst in per.items():
        out[arm] = dict(lapstrat=round(float(np.mean([x[0] for x in lst])), 4), seeds=[round(x[0], 4) for x in lst],
                        ci=[round(x, 4) for x in S.ci(np.mean([x[1] for x in lst], 0))],
                        raw=round(float(np.mean([x[2] for x in lst])), 4))
    e = out["e"]["lapstrat"]
    out["verdict_e"] = "supported" if e >= 0.45 else ("falsified" if e <= 0.40 else "undecided")
    out["stratum_counts"] = {k: [sum(st[i] == k for i in Fr), sum(st[i] == k for i in Re)] for k in range(5)}
    json.dump(out, open(K.RES / "a19_hn4.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
