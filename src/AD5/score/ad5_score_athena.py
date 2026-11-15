"""Retrains of released methods (AD5): score one retrain through the own-crop re-score (RS1) release path on Athena.

Same mechanism as RS1's athena_run.py (src/RS1/athena_run.py): re-point the landmark ladder's (AR1) ar1_common paths to
the unpacked RS1 pack, keep the sha256 pins of the frozen A46 runtime files, then run the byte-identical score.py.
The only addition: the retrain is registered under its own name as a copy of its release's a12_released spec
(same architecture, channels, mean / std, head adapter, resolution) with its own weight file and sha256.

  python3 -I ad5_score_athena.py ROOT SITE --as RELEASE --name NAME --weights FILE -- [score.py arguments without --det]
ROOT = the unpacked RS1 pack (code/smadcvpr, code/rs1, weights/), SITE = an extra site directory (may be empty).
RELEASE = madation_vitl14 | madation_vitb16 | madation_fe_vitl14 | mixfacenet_mad_smdd | the release itself.
"""
import hashlib
import pathlib
import sys


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


ROOT, SITE = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
rest = sys.argv[3:]
cut = rest.index("--")
opts, score_args = rest[:cut], rest[cut + 1:]
o = dict(zip(opts[0::2], opts[1::2]))
AS, NAME, WEIGHTS = o["--as"], o["--name"], pathlib.Path(o["--weights"])
RS1 = ROOT / "code" / "rs1"
sys.path.insert(0, str(SITE))
sys.path.insert(0, str(RS1))
PINNED = {"score.py": "56bb124444980f630d676758d25aaefe5b3485874c8aea174e0bd74d3c597cc8",
          "ar1_common.py": "42806acb43b0c8d5c6876622dc5cfd5377c6bac3a38cda250824606fb7d407ab"}
for f, h in PINNED.items():
    assert sha(RS1 / f) == h, f
import ar1_common as K  # noqa: E402
import score  # noqa: E402  (RS1's byte-identical score.py; imported before code/smadcvpr enters sys.path)

assert pathlib.Path(score.__file__).resolve() == (RS1 / "score.py").resolve(), score.__file__
old = K.W46 / "smadcvpr"
K.MC = ROOT / "code"
K.W46 = ROOT / "code"
K.PINS = {K.W46 / "smadcvpr" / p.name: h for p, h in K.PINS.items() if p.parent == old}
K.add_paths(K.MC, K.W46 / "smadcvpr")
for p, h in K.PINS.items():
    assert sha(p) == h, p
import a12_released as R  # noqa: E402  (the same module object score.py imports)

assert AS in R.RELEASES, AS
if NAME != AS:
    assert NAME not in R.RELEASES, NAME
    R.RELEASES[NAME] = dict(R.RELEASES[AS])
K.WEIGHTS = {NAME: WEIGHTS}
K.WEIGHT_SHA = {NAME: sha(WEIGHTS)}
print(f"AD5 scoring {NAME} as {AS}: {WEIGHTS} sha256 {K.WEIGHT_SHA[NAME]}", flush=True)
sys.argv = ["score.py", "--det", NAME] + score_args
score.main()
