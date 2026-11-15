"""CB1: BPCER at APCER 1/5/10/20% for the released detectors from the own-crop re-score (RS1) score files (missing in
RS1's tables). Reads RS1's pools through RS1's own analyse.py (import only); native genuine = raw photos (RS1 cell_sets),
history-matched = aligned E7 against aligned native (both through the release crop). No new scoring.
  python3 -I rs1_bpcer.py OUT.csv"""
import csv, sys
import numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/RS1"); sys.path.insert(0, "/home/narolski/smad-next/src/CB1")
import analyse as A
from analyse_cnn import w_eer, bpcer_at
A.ATH_RUNS.update(v1="/mnt/t7/smad_next/RS1/results_rented/prod_v1_rented", v2="/mnt/t7/smad_next/RS1/results_rented/prod_v2_rented")
CELLS = ["amsl", "facemorpher", "opencv", "stylegan", "webmorph"] + [f"mad22_{f}" for f in A.FAM22]
out = []
for det in ("madation_vitb16", "madation_vitl14", "mixfacenet_mad_smdd"):
    for v in ("v1", "v2"):
        P = A.athena_pools(det, variant=v)
        if P is None:
            print("no pools", det, v); continue
        for c in CELLS:
            g, m, _, e7a, ga = A.cell_sets(c)
            for pool, G in (("native_raw", g), ("aligned_native", ga), ("e7_aligned", e7a)):
                if G not in P or m not in P:
                    continue
                s = np.r_[P[G].s, P[m].s]; y = np.r_[np.zeros(len(P[G].s)), np.ones(len(P[m].s))]
                r = dict(detector=det, crop=v, cell=c, genuine_pool=pool, n_gen=len(P[G].s), n_morph=len(P[m].s),
                         eer=round(100 * w_eer(s, y), 2), published=A.PUB.get(det, {}).get(c),
                         crop_script_fail_share=A.FAILS.get(m))
                for a in (0.01, 0.05, 0.10, 0.20):
                    r[f"bpcer_at_apcer{int(a * 100)}"] = round(100 * bpcer_at(s, y, a), 2)
                out.append(r)
with open(sys.argv[1], "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print(len(out), "rows")
