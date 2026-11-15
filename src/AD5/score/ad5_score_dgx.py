"""Retrains of released methods (AD5): score one network on the DGX through the landmark ladder's (AR1) score.py,
byte-identical copy in src/RS1/ (as RS1's rs1_score.py), with the weight table entry pointed to the given file.
Used for SelfMAD (mode own: dlib 81 landmarks, landmark box + 6.25% margin, 384, /255, softmax[:, 1]).

  python3 -I ad5_score_dgx.py --name NAME --weights FILE -- [score.py arguments without --det]
"""
import hashlib
import pathlib
import sys

RS1 = pathlib.Path("/home/narolski/smad-next/src/RS1")
sys.path.insert(0, str(RS1))


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


for f, h in (("score.py", "56bb124444980f630d676758d25aaefe5b3485874c8aea174e0bd74d3c597cc8"),
             ("ar1_common.py", "42806acb43b0c8d5c6876622dc5cfd5377c6bac3a38cda250824606fb7d407ab")):
    assert sha(RS1 / f) == h, f
rest = sys.argv[1:]
cut = rest.index("--")
o = dict(zip(rest[:cut][0::2], rest[:cut][1::2]))
import ar1_common as K  # noqa: E402
import score  # noqa: E402

assert pathlib.Path(score.__file__).resolve() == (RS1 / "score.py").resolve()
NAME, W = o["--name"], pathlib.Path(o["--weights"])
K.WEIGHTS[NAME] = W
K.WEIGHT_SHA[NAME] = sha(W)
print(f"AD5 DGX scoring {NAME}: {W} sha256 {K.WEIGHT_SHA[NAME]}", flush=True)
sys.argv = ["score.py", "--det", NAME] + rest[cut + 1:]
score.main()
