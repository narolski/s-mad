"""MS1: sha256 of the raw FFHQ files of all 20,000 excluded keys (file-content part of the exclusion proof).
  python3 -I excl_sha.py -> OUT/ffhq/excluded_raw_sha256.csv"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ms1common as C
ex, _ = C.excluded_keys()
rows = [dict(key=k, sha256=C.sha(C.raw_ffhq(k))) for k in sorted(ex)]
C.write_csv(C.OUT / "ffhq/excluded_raw_sha256.csv", rows)
print(len(rows))
