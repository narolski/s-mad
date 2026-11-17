"""verify12.py DIR: 12 npz present; ids vs score_v{1,2}.csv rows and vs athena_manifest M22_/G22_/E7aln22_ sets; finite values."""
import csv, sys, pathlib, collections, numpy as np
D = pathlib.Path(sys.argv[1]); P = pathlib.Path("/home/narolski/ad6_stage/h5race/pack/manifests")
sets = {r["id"]: r["set"] for r in csv.DictReader(open(P / "athena_manifest.csv"))}
want = {i for i, s in sets.items() if s.startswith(("M22_", "G22_", "E7aln22_"))}
nets = ["selfmad_hrnet_w18"] + [f"selfmad_S_s40{k}" for k in range(1, 6)]
bad = 0
for v in ("v1", "v2"):
    rows = [r["id"] for r in csv.DictReader(open(P / f"score_{v}.csv"))]
    wv = [i for i in rows if i in want]
    for n in nets:
        f = D / f"scores_rel_{n}__m22{v}.npz"
        if not f.exists():
            print("MISSING", f.name); bad += 1; continue
        z = np.load(f); ids = z["id"].tolist(); S = set(ids)
        miss_rows = len(set(rows) - S); miss_sets = len(want - S); extra = len(S - set(rows))
        fin = all(np.isfinite(z[k]).all() for k in ("score", "score_noTTA", "logit_noTTA"))
        order = ids == rows
        c = collections.Counter(sets[i].split("_")[0] for i in ids if i in want)
        ok = miss_rows == 0 and extra == 0 and fin and order and str(z["det"]) == "selfmad_hrnet_w18" and str(z["mode"]) == "rel"
        bad += not ok
        print(f.name, len(ids), f"missing_vs_csv={miss_rows} extra={extra} m22set_ids_in_csv={len(wv)} "
              f"m22set_ids_missing_vs_athena_manifest={miss_sets} same_order={order} finite={fin} {dict(c)} {'OK' if ok else 'BAD'}")
print("athena_manifest M22/G22/E7aln22 ids:", len(want), collections.Counter(sets[i].split("_")[0] for i in want))
print("VERIFY", "PASS" if bad == 0 else f"FAIL {bad}")
