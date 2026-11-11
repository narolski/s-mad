"""Own-crop re-score of the audit rows (RS1): run the landmark ladder's (AR1) score.py, copied byte-identically into
src/RS1/, with two extra entries in its weight table (the frozen-encoder MADation releases). Nothing else changes:
same adapters, TTA, decision key, feature hook, output format.

  python3 -I rs1_score.py --det madation_fe_vitl14 --mode rel --manifest M.csv --out-dir D --tag T [--limit 8]
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ar1_common as K  # noqa: E402

PAY = pathlib.Path("/mnt/t7/smad_heldout/mad22_production_cpu_stage_v1/payload/models")
EXTRA = {"madation_fe_vitb16": "6a4d93ba80f3c48ecb0a9d8a6ae07e0c64e8c4f49f2cc62b2588dafbffb84d92",
         "madation_fe_vitl14": "74dd7fbce8385ec4c080def2c63300243b04ca2abd8ddea6eb2a519296e054a9",
         "madation_fs_vitb16": "a7cacd4773ed3ef959e78202c7f0e0426e5fff04367418130da78e9e85e64885",
         "madation_fs_vitl14": "6071ec7b7dcb0b3f28f4c8b71c79692a322404c33893a62f5a89964fb79a9421"}
for name, h in EXTRA.items():
    K.WEIGHTS[name] = PAY / f"{h}.safetensors"
    K.WEIGHT_SHA[name] = h

import score  # noqa: E402

if __name__ == "__main__":
    # byte-identical copies of the landmark ladder (AR1) files, checked at every start
    for f, h in (("score.py", "56bb124444980f630d676758d25aaefe5b3485874c8aea174e0bd74d3c597cc8"),
                 ("ar1_common.py", "42806acb43b0c8d5c6876622dc5cfd5377c6bac3a38cda250824606fb7d407ab")):
        assert K.sha(HERE / f) == h, f
    score.main()
