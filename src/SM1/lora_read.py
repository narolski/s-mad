"""SM1 amendment A9: convert the Athena LoRA result tars (SM1L_<arm>_s<seed>.tar, extracted) into the score format of
read_p3.py: OUT/lora_scores/<arm>_s<seed>.npz (id in the SM1 test-list id space, logit = log(p / (1 - p)) of the
no-TTA score of ad4_score.py; monotone, so AUC, EER and thresholded flags are unchanged).
Id mapping: AD4 eval ids "e…" -> "ev:e…"; "mad22c/<native|e7>/<fam>/<file>.png" -> "m22:<native|e7>/<fam>/<stem>";
AR1 ids are the SM1 ids already.

  python3 -I lora_read.py DIR   (DIR holds the extracted SM1L_* folders)
"""
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402


def conv(i):
    i = str(i)
    if i.startswith("mad22c/"):
        return "m22:" + i[len("mad22c/"):-4] if i.endswith(".png") else "m22:" + i[len("mad22c/"):]
    if i.startswith("ar1:") or i.startswith("ar1h:"):
        return i
    return "ev:" + i


def main():
    d = pathlib.Path(sys.argv[1])
    od = K.OUT / "lora_scores"
    od.mkdir(parents=True, exist_ok=True)
    out = {}
    for t in sorted(d.glob("SM1L_*_s*")):
        if t.name.endswith("_smoke"):
            continue
        arm, seed = t.name.split("_")[1], t.name.split("_")[2][1:]
        ids, z = [], []
        for sub in ("ad4eval", "ar1eval"):
            f = np.load(t / sub / "scores_eval.npz", allow_pickle=False)
            p = np.clip(f["score_noTTA"].astype(np.float64), 1e-7, 1 - 1e-7)
            ids += [conv(i) for i in f["id"]]
            z.append(np.log(p / (1 - p)))
        z = np.concatenate(z)
        np.savez(od / f"{arm}_s{seed}.npz", id=np.array(ids), logit=z.astype(np.float32))
        m = json.load(open(t / "ad4eval" / "metrics.json"))
        out[t.name] = dict(n=len(ids), train=m.get("train"), steps=m["info"].get("steps"),
                           train_hours=m["info"].get("train_hours"))
    json.dump(out, open(od / "lora_read_log.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
