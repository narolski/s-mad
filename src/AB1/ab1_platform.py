"""AB1 smoke, platform measurement (descriptive, decides nothing): FS1 Sb seed 403 rescored on a WCSS H100 (smoke tar
AB1smoke_platform.tar) against its stored A100 PCIe logits (FS1 result tar), on the 6,339 FS1 gate rows (af0, ffhq), with
the C2P gate statistics (c2p_read.gate, unchanged); also checks that the smoke network's 1,480 hold-out scores are finite.
  python3 -I ab1_platform.py SMOKE_TAR OUT.json"""
import csv
import importlib.util
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("c2p_read", HERE.parent / "PN1" / "c2p_read.py")
C2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C2)

smoke, out = sys.argv[1], sys.argv[2]
F = list(csv.DictReader(open(C2.FS1M)))
gate_ids = [r["id"] for r in F if r["fam"] in ("af0", "ffhq")]
new = {}
for fam in ("af0", "ffhq"):
    new.update(C2.npz_from_tar(smoke, f"AB1plat_PN1_Sb_s403_{fam}.npz") or {})
stored = C2.npz_from_tar(f"{C2.FS1}/PN1_Sb_s403.tar", "scores_eval.npz")
R = dict(gate_stats=C2.gate(new, stored, gate_ids))
ho = C2.npz_from_tar(smoke, "AB1smoke_SbH_s408_ms1ffhq.npz") or {}
R["holdout_rows"] = len(ho)
R["holdout_finite"] = bool(ho) and all(math.isfinite(v) for v in ho.values())
json.dump(R, open(out, "w"), indent=1)
print(json.dumps(R))
