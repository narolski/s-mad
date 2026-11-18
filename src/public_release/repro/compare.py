"""PRIVATE (release reproduction 2026-11-18): compare a release-code retrain with the frozen network.
  python -I compare.py FROZEN_DIR RESULT_DIR [sb|mf]
Prints: sha256 equal; max |diff| over the trainable tensors (and relative to max |w|); max |diff| of the stored
development/training scores (sb: logit on scores_eval/scores_train; mf: sigmoid(logit) vs score_noTTA on scores_train);
loss trace of train.log (every 100 updates)."""
import hashlib, re, sys, pathlib
import numpy as np, torch

F, R, kind = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
fa, ra = F / "last_trainable.pt", R / "run" / "last_trainable.pt"
print("sha256 frozen", sha(fa)[:16], "release", sha(ra)[:16], "EQUAL" if sha(fa) == sha(ra) else "differ")
a, b = torch.load(fa, map_location="cpu", weights_only=True), torch.load(ra, map_location="cpu", weights_only=True)
assert set(a) == set(b), set(a) ^ set(b)
d = max((a[k].float() - b[k].float()).abs().max().item() for k in a)
w = max(a[k].float().abs().max().item() for k in a)
neq = sum(not torch.equal(a[k], b[k]) for k in a)
print(f"tensors {len(a)}, not bit-equal {neq}, max abs diff {d:.3e} (max |w| {w:.3e})")
if kind == "sb":
    for s in ("eval", "train"):
        p = R / f"rescore_{s}.npz"
        if p.exists():
            x, y = np.load(p)["logit"], np.load(F / f"scores_{s}.npz")["logit"]
            e = np.abs(x.astype(np.float64) - y)
            print(f"scores_{s}: n {len(x)} logit max abs diff {e.max():.3e} median {np.median(e):.3e} sign flips {(np.sign(x) != np.sign(y)).sum()}")
else:
    p = R / "rescore_train.npz"
    if p.exists():
        x, y = 1 / (1 + np.exp(-np.load(p)["logit"].astype(np.float64))), np.load(F / "scores_train.npz")["score_noTTA"]
        e = np.abs(x - y)
        print(f"scores_train: n {len(x)} sigmoid max abs diff {e.max():.3e} median {np.median(e):.3e}")
lf = [re.findall(r"step +(\d+)/\d+ loss ([\d.]+)", l) for l in open(F / "train.log")]
lr = [re.findall(r"step +(\d+)/\d+ loss ([\d.]+)", l) for l in open(R / "run" / "train.log")]
lf = dict(m[0] for m in lf if m); lr = dict(m[0] for m in lr if m)
common = [k for k in lr if k in lf]
same = sum(lf[k] == lr[k] for k in common)
print(f"loss trace: {len(common)} common log points, {same} identical to 4 dp;",
      "first diffs:", [(k, lf[k], lr[k]) for k in common if lf[k] != lr[k]][:5])
