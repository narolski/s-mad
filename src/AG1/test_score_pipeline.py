"""Pipeline test of the AG1 scoring path on the DGX smoke images (never data): aligns the local smoke PNGs with
prep_eval.align (CPU detector), writes DATA/manifests/ag1.csv (relative paths) and DATA/AG1_data_pins.sha256.
Then: score_dgx.sh DATA OUT madation_vitb16:rel selfmad_hrnet_w18:own ; this script's 'check' mode prints only the
count and finiteness of the scores (score values are not looked at).
Usage: python -I test_score_pipeline.py build SMOKE_PNG_DIR DATA | check OUT"""
import csv, hashlib, pathlib, sys
import numpy as np


def main():
    if sys.argv[1] == "build":
        import cv2
        src, data = pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
        sys.path.insert(0, "/home/narolski/mambamorph-code/smadcvpr")
        import prep_eval
        from insightface.app import FaceAnalysis
        det = FaceAnalysis(name="buffalo_l", allowed_modules=["detection"], providers=["CPUExecutionProvider"])
        det.prepare(ctx_id=-1, det_size=(512, 512))
        prep_eval._APP = det
        (data / "manifests").mkdir(parents=True, exist_ok=True)
        (data / "frames/smoke").mkdir(parents=True, exist_ok=True)
        rows = []
        for f in sorted(src.glob("*.png")):
            img, ok, _ = prep_eval.align(cv2.imread(str(f)))
            cv2.imwrite(str(data / "frames/smoke" / f.name), img)
            rows.append({"id": f.stem, "path": f"frames/smoke/{f.name}", "label": 1, "aligned": ok})
        with open(data / "manifests/ag1.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        h = hashlib.sha256(open(data / "manifests/ag1.csv", "rb").read()).hexdigest()
        (data / "AG1_data_pins.sha256").write_text(f"{h}  manifests/ag1.csv\n")
        print(len(rows), "rows; aligned", sum(r["aligned"] for r in rows))
    else:
        for f in sorted(pathlib.Path(sys.argv[2]).glob("a41g_out/ag1/*/*/scores_ag1.npz")):
            z = np.load(f)
            v = z["logit_noTTA"]
            print(f.parent.parent.name, f.parent.name, "n", len(v), "finite", bool(np.isfinite(v).all()),
                  "release", str(z["release"]), "bs", int(z["bs"]))


if __name__ == "__main__":
    main()
