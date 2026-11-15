"""Sealed MAD22 read (FINAL): copy the EXISTING released-detector score rows needed by the reader into one pinned file.
No score is computed. Reads the RS1 production score files (rented RTX 3090, own crop, variant 1 = SMDD crop script
unchanged, primary; variant 2 printed) through RS1's analyse.py (import only, as src/CB1/rs1_bpcer.py does), and the
SelfMAD own-preprocessing FFHQ rows of RS1's DGX run (for SelfMAD's development threshold only).

Pools kept (RS1 set names): G22_raw (raw FRLL photos), G22_aln (our aligned native frames), E7aln22_<fam> (our aligned
E7 frames), M22_<fam> (raw corrected-MAD22 morphs), FF_orig (FFHQ genuine development photos, threshold only).
Out: /mnt/t7/smad_next/FINAL/release_scores_existing.npz (+ .sha256).
  python3 -I extract_release_scores.py"""
import hashlib
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, "/home/narolski/smad-next/src/RS1")
import analyse as A  # noqa: E402

A.ATH_RUNS.update(v1="/mnt/t7/smad_next/RS1/results_rented/prod_v1_rented",
                  v2="/mnt/t7/smad_next/RS1/results_rented/prod_v2_rented")
OUT = pathlib.Path("/mnt/t7/smad_next/FINAL/release_scores_existing.npz")
DETS = ("madation_vitb16", "madation_vitl14", "mixfacenet_mad_smdd")
FAM22 = ("FaceMorpher", "MIPGAN_I", "MIPGAN_II", "OpenCV", "Webmorph")
KEEP = ["G22_raw", "G22_aln", "FF_orig"] + [f"E7aln22_{f}" for f in FAM22] + [f"M22_{f}" for f in FAM22]


def main():
    cols = dict(det=[], variant=[], pool=[], logit=[], pa=[], pb=[], expr=[])
    counts = {}
    for det in DETS:
        for v in ("v1", "v2"):
            P = A.athena_pools(det, variant=v)
            if P is None:
                sys.exit(f"no RS1 pools for {det} {v}")
            for pool in KEEP:
                if pool not in P:
                    sys.exit(f"{det} {v}: pool {pool} missing")
                p = P[pool]
                for s, pp, ex in zip(p.s, p.pp, p.ex):
                    cols["det"].append(det); cols["variant"].append(v); cols["pool"].append(pool)
                    cols["logit"].append(float(s)); cols["pa"].append(pp[0]); cols["pb"].append(pp[-1])
                    cols["expr"].append(str(ex))
                counts[f"{det}/{v}/{pool}"] = len(p.s)
    # SelfMAD: its MAD22 rows do not exist (RS1 scored FRLL only); its FFHQ rows (development threshold) from RS1's DGX run
    man = A.manifest()
    S = A.selfmad_dgx(man)
    if "FF_orig" not in S:
        sys.exit("SelfMAD FF_orig missing")
    p = S["FF_orig"]
    for s, pp, ex in zip(p.s, p.pp, p.ex):
        cols["det"].append("selfmad_hrnet_w18"); cols["variant"].append("own_dgx"); cols["pool"].append("FF_orig")
        cols["logit"].append(float(s)); cols["pa"].append(pp[0]); cols["pb"].append(pp[-1]); cols["expr"].append(str(ex))
    counts["selfmad_hrnet_w18/own_dgx/FF_orig"] = len(p.s)
    np.savez(OUT, **{k: np.array(v) for k, v in cols.items()})
    h = hashlib.sha256(OUT.read_bytes()).hexdigest()
    (OUT.parent / (OUT.name + ".sha256")).write_text(f"{h}  {OUT.name}\n")
    json.dump(dict(counts=counts, sha256=h, key=p.key), open(OUT.with_suffix(".json"), "w"), indent=1)
    print("RELEASE_EXISTING", h, len(cols["logit"]), "rows")


if __name__ == "__main__":
    main()
