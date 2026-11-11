"""Comparison numbers for the released MADation ViT-L/14 from scores the record already has (no rescoring):
smadcvpr_runs/A12_scored/A12REL/madation_vitl14/scores_eval.npz (registered A12REL eval pass on our 512 frames,
key score_noTTA, morph = higher), on the same FRLL-Morphs rows as bench_s: EER native / E7 per family (person
bootstrap) and the FRLL genuine native -> E7 shift in native standard deviations. Corrected MAD22: no score exists.
  python3 -I madation_ref.py
"""
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import af0lib as L  # noqa: E402
import metrics as M  # noqa: E402

Z = "/home/narolski/mambamorph-code/smadcvpr_runs/A12_scored/A12REL/madation_vitl14/scores_eval.npz"


def main():
    z = np.load(Z)
    s = dict(zip(z["id"], z["score_noTTA"]))
    S = {}
    for r in L.rows("bench_s"):
        if r["id"].startswith("frllm_"):
            e = r["id"][len("frllm_"):]
            if e in s:
                S[r["id"]] = float(s[e])
    out = dict(source=Z, ckpt_sha256=str(z["ckpt_sha256"]), manifest_sha256=str(z["manifest_sha256"]), n=len(S))
    for fam in ("amsl", "facemorpher", "opencv", "webmorph"):
        out[f"FRLL_native_to_E7_{fam}"] = M.shift(S, "bench_s", lambda r: r["cell"] == "frllm_frll_bona",
                                                  lambda r, f=fam: r["cell"] == f"frllm_{f}" and r["rung"] == "e7")
        for gen in ("native", "e7"):
            bf = (lambda r: r["cell"] == "frllm_frll_bona") if gen == "native" else \
                (lambda r, f=fam: r["cell"] == f"frllm_{f}" and r["rung"] == "e7")
            out[f"EER_frllm_{fam}_{gen}"] = M.eer(S, "bench_s", bf, lambda r, f=fam: r["cell"] == f"frllm_{f}" and r["rung"] == "morph")
    json.dump(out, open(L.RES / "madation_vitl14_ref.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
