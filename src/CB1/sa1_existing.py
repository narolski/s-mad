"""CB1 amendment 5: SA1 cells from existing RS1 score files (read only, through RS1's analyse.py):
5-* own-crop frame-alone shift (Galn_mordiff - Galn_frll, paired by photo; median, person bootstrap 95%);
4-ViTL own-rule (logit > 0) flag rate on FFHQ (FF_orig); RS1 pool rates for MixFaceNet are read from rs1_pool_rates.csv.
  python3 -I sa1_existing.py OUT.json"""
import json, sys
import numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/RS1")
import analyse as A
A.ATH_RUNS.update(v1="/mnt/t7/smad_next/RS1/results_rented/prod_v1_rented", v2="/mnt/t7/smad_next/RS1/results_rented/prod_v2_rented")
rng = np.random.default_rng(20261111); out = {}   # amendment 6: EV1 seed
for det in ("madation_vitb16", "madation_vitl14", "mixfacenet_mad_smdd"):
    for v in ("v1", "v2"):
        P = A.athena_pools(det, variant=v)
        if P is None or "Galn_frll" not in P or "Galn_mordiff" not in P:
            out[f"{det}_{v}"] = "pools missing"; continue
        a = {ph: s for ph, s in zip(P["Galn_frll"].ph, P["Galn_frll"].s)}
        b = {ph: s for ph, s in zip(P["Galn_mordiff"].ph, P["Galn_mordiff"].s)}
        ks = sorted(set(a) & set(b)); d = np.array([b[k] - a[k] for k in ks])
        pers = np.array([k.split("_")[0] for k in ks]); up = np.unique(pers)
        idx = {p: np.where(pers == p)[0] for p in up}
        bs = [np.median(np.concatenate([d[idx[p]] for p in rng.choice(up, len(up))])) for _ in range(2000)]
        r = dict(n=len(ks), median_shift=float(np.median(d)), lo95=float(np.percentile(bs, 2.5)), hi95=float(np.percentile(bs, 97.5)),
                 share_up=float((d > 0).mean()))
        if "FF_orig" in P:
            r["ffhq_own_rule_flag_rate"] = float((P["FF_orig"].s > 0).mean()); r["ffhq_n"] = int(len(P["FF_orig"].s))
        out[f"{det}_{v}"] = r
json.dump(out, open(sys.argv[1], "w"), indent=1); print(json.dumps(out, indent=1))
