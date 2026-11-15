"""RZ1: run the unchanged pack train.py with the RZ1 input transform (rz1_patch). Usage: rz1_train.py CODE_DIR <train.py args>.
Writes rz1_transform.json beside meta.json in --out (spec, res, RZ1_RES512, kernel list)."""
import json
import os
import pathlib
import runpy
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import rz1_patch  # noqa: E402

code = sys.argv[1]
spec = rz1_patch.apply(code)
import rz1_kernels as K  # noqa: E402
args = sys.argv[2:]
out = args[args.index("--out") + 1]
res = int(args[args.index("--res") + 1])
print(f"RZ1 transform {spec} res {res} RZ1_RES512 {os.environ.get('RZ1_RES512', '0')}", flush=True)
sys.argv = [str(pathlib.Path(code) / "smadcvpr" / "train.py")] + args
try:
    runpy.run_path(sys.argv[0], run_name="__main__")
finally:
    pathlib.Path(out).mkdir(parents=True, exist_ok=True)
    json.dump(dict(spec=spec, res=res, res512=os.environ.get("RZ1_RES512", "0"), kernels=list(K.NAMES),
                   s_lo=K.S_LO, s_hi=K.S_HI, p_two=K.P_TWO), open(pathlib.Path(out) / "rz1_transform.json", "w"))
