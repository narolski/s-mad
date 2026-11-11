"""AR1: score lists from the crop outputs and the manifest.
  python3 -I lists.py crops <crops.csv> <out.csv>        rows with status 'retained' (flagged crops kept, flag printed)
  python3 -I lists.py frames <out.csv>                    manifest rows of kind frame512 / pe (our-pipeline nets)
  python3 -I lists.py blank <out.csv>                     blank_manifest rows (id, path, bg_path, face_path)
"""
import collections
import csv
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ar1_common as K  # noqa: E402


def main():
    mode = sys.argv[1]
    if mode == "crops":
        import glob
        src = sys.argv[2]
        parts = sorted(glob.glob(src.replace("crops.csv", "crops_*of*.csv"))) if not pathlib.Path(src).exists() else [src]
        rows = [r for p in parts for r in csv.DictReader(open(p))]
        print(collections.Counter(r["status"] for r in rows))
        keep = [dict(id=r["id"], path=r["path"]) for r in rows if r["status"] == "retained" or r["status"].startswith("flag")]
        out = sys.argv[3]
    elif mode == "frames":
        keep = [dict(id=r["id"], path=r["path"]) for r in csv.DictReader(open(K.OUT / "manifest.csv"))
                if r["kind"] in ("frame512", "pe") and r["pool"] != "frll_bridge"]   # retrain bridge would cross frame pipelines
        out = sys.argv[2]
    else:
        keep = list(csv.DictReader(open(K.OUT / "blank/blank_manifest.csv")))
        out = sys.argv[2]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(keep[0]))
        w.writeheader()
        w.writerows(keep)
    print(out, len(keep))


if __name__ == "__main__":
    main()
