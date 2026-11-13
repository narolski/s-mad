"""Convert an Athena audit tar's scores_audit.npz to lora_audit_vitl/a_s<seed>.npz for a12_rank.py.
logit = log(p / (1 - p)) of score_noTTA (the registered convention; reproduces a_s401..403 exactly).
  python -I audit_conv.py SEED [SEED ...]
"""
import sys
import numpy as np
A = "/mnt/t7/smad_next/SM1/athena/lora_audit/SM1A_SM1L_a_s%d/scores_audit.npz"
O = "/mnt/t7/smad_next/SM1/lora_audit_vitl/a_s%d.npz"
for s in map(int, sys.argv[1:]):
    e = np.load(A % s)
    p = e["score_noTTA"].astype(np.float64)
    np.savez(O % s, id=e["id"], logit=np.log(p / (1 - p)).astype(np.float32))
    print(s, len(p))
