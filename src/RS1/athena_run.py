"""Own-crop re-score of the audit rows (RS1), Athena run: entry point that re-points the landmark ladder's (AR1)
ar1_common paths to the unpacked tar and then runs the byte-identical crop_rgb.py or score.py.

  python3 -I athena_run.py ROOT SITE crop  --manifest M.csv --out DIR [--shard i/n] [--limit 8]
  python3 -I athena_run.py ROOT SITE score --det NAME --mode rel --manifest M.csv --out-dir D --tag T [--limit 8]
ROOT = the unpacked pack (code/, weights/, img/); SITE = the directory with facenet_pytorch / cv2 / requests.
Only paths change: K.W46 / K.MC -> ROOT/code, the pinned A46 runtime files keep their sha256 pins, K.WEIGHTS ->
ROOT/weights with the same sha256 pins (plus the four FE / FS releases).
"""
import hashlib
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT, SITE, CMD = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
sys.path.insert(0, str(SITE))
sys.path.insert(0, str(HERE))
import ar1_common as K  # noqa: E402

PINNED = {"score.py": "56bb124444980f630d676758d25aaefe5b3485874c8aea174e0bd74d3c597cc8",
          "ar1_common.py": "42806acb43b0c8d5c6876622dc5cfd5377c6bac3a38cda250824606fb7d407ab",
          "crop_rgb.py": "07b179bdc5f9532b85326022c241a329e059fd3ee632f4a74033112dc669e922"}
for f, h in PINNED.items():
    assert hashlib.sha256((HERE / f).read_bytes()).hexdigest() == h, f
old = K.W46 / "smadcvpr"
K.MC = ROOT / "code"
K.W46 = ROOT / "code"
K.PINS = {K.W46 / "smadcvpr" / p.name: h for p, h in K.PINS.items() if p.parent == old}
SHA = {"madation_vitb16": "ddb1455bae4b72331aff4806590bd88ba2447563d803e207099c6b712d6bbe2f",
       "madation_vitl14": "bb452ded624ffce2dc85168f8dde9293fc3709ec8cce755d8ecf1d5f5370e980",
       "madation_fe_vitb16": "6a4d93ba80f3c48ecb0a9d8a6ae07e0c64e8c4f49f2cc62b2588dafbffb84d92",
       "madation_fe_vitl14": "74dd7fbce8385ec4c080def2c63300243b04ca2abd8ddea6eb2a519296e054a9",
       "madation_fs_vitb16": "a7cacd4773ed3ef959e78202c7f0e0426e5fff04367418130da78e9e85e64885",
       "madation_fs_vitl14": "6071ec7b7dcb0b3f28f4c8b71c79692a322404c33893a62f5a89964fb79a9421",
       "mixfacenet_mad_smdd": "3d507c8bbd5dbd06bd735ae809fa0095e589c17c0c94cd2ed530cf34a014ab1c"}
K.WEIGHTS = {n: ROOT / "weights" / (f"{h}.pth" if n.startswith("mixfacenet") else f"{h}.safetensors")
             for n, h in SHA.items()}
K.WEIGHT_SHA = dict(SHA)
sys.argv = [CMD] + sys.argv[4:]
if CMD == "crop":
    import crop_rgb
    crop_rgb.main()
elif CMD == "score":
    import score
    score.main()
else:
    sys.exit(f"unknown command {CMD}")
