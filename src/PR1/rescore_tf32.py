"""TT1 FS1 block gate scorer: src/PN1/rescore.py run UNCHANGED (imported from the given path, sha256 asserted) with TF32
switched on for matmul and cuDNN first, as pn1_score.py does (torch.backends.cuda.matmul.allow_tf32 = True;
torch.backends.cudnn.allow_tf32 = True). Arguments are passed through to rescore.py.
  python rescore_tf32.py /path/to/rescore.py --resdir ... --code ... --manifest ... --fam ... --out ..."""
import hashlib
import importlib.util
import sys

RESCORE_SHA = "6f6eede71c6d9a895199dabc8bc90b882adb25f5f91cd2fcc676ebe7a380b51e"

path = sys.argv[1]
assert hashlib.sha256(open(path, "rb").read()).hexdigest() == RESCORE_SHA, "rescore.py not at its pin"
import torch  # noqa: E402

torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
sys.argv = [path] + sys.argv[2:]
spec = importlib.util.spec_from_file_location("rescore", path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.main()
