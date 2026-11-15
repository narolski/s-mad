"""AD1 documentation check (CPU, re-read only): flag rates at fixed thresholds and the storage-alone comparison
the independent review (REVIEW_AD1_AG5_C_20261111.md) quotes; FE ViT-L/14 contrasts. Writes ad1_flagrates.json."""
import sys, json, csv, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/AD1")
import ad1_read as R
rows = list(csv.DictReader(open(R.MAN)))
ev = [r for r in csv.DictReader(open(R.EVAL)) if r["set"] == "mordiff" and r["family"] == "mordiff" and r["variant"] == "resmatch"]
G = {}
for i, r in enumerate(rows):
    k = r["arm"] if r["source"] == "a43" else {"mordiff_bona": "R0", "mordiff": "A_reg"}.get(r["family"], "frll_bona")
    G.setdefault(k, []).append(i)
out = {}
for lab, a43f, k43, evf, kev, role in R.DETS:
    s = np.load(R.A43 / "a43_out/a43" / a43f / "scores_a43.npz")[k43].astype(float)
    ze = np.load(R.MC / evf); em = dict(zip(ze["id"].tolist(), ze[kev].astype(float)))
    S = {k: s[np.array(v)] for k, v in G.items()}
    S["R1"] = np.array([em[r["id"]] for r in ev])
    eer, t = R.eer_thr(S["R0"], S["A_reg"])
    t1 = float(np.quantile(S["R0"], 0.99))          # threshold flagging 1% of the untouched photos (flag = score > t1)
    fr = lambda x, th, strict=False: float(((x > th) if strict else (x >= th)).mean())  # noqa: E731
    out[lab] = {"eer_pct": eer,
                "flag_at_eer_thr": {k: fr(S[k], t) for k in ("R0", "R1", "E", "D20", "C20", "B20", "A_reg")},
                "flag_at_1pct_thr": {k: fr(S[k], t1, True) for k in ("R0", "R1", "E", "D20", "C20", "B20", "A_reg")},
                "E_outranks_published_A": float(1 - R.wauc(S["A_reg"], S["E"], np.ones((1, len(S["A_reg"]))), np.ones((1, len(S["E"]))))[0])}
    print(lab, json.dumps({k: (round(v, 3) if isinstance(v, float) else {kk: round(vv, 3) for kk, vv in v.items()}) for k, v in out[lab].items()}))
json.dump(out, open("/home/narolski/smad-next/experiments/AD1/ad1_flagrates.json", "w"), indent=1)
