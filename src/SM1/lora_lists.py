"""SM1 amendment A9: manifests for the Athena LoRA fits (train.py, regime d0) and the AR1 evaluation manifest.

Images are taken from the GPU-pack image tars already on Athena (sm1gpu_img_{base,armsc,arme,test,audit}.tar),
extracted under <data root>/x/, so a path is "x/" + the absolute DGX path without its leading slash.
  train_sm1<arm>_s<seed>.csv  columns of train.csv: path,label,source,tool,arm,val,mixed; source = smdd (regime d0
                              keeps every row), val = 0, mixed = 0; the composition of compose.py
  sm1_ar1_eval.csv            ad4_eval.csv columns: id,path,set,family,label,variant,src_id (set = ar1)

  python3 -I lora_lists.py  -> OUT/lora/manifests/*.csv, OUT/lora/lists.json
"""
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402

FL = K.OUT / "flists"
ARMS = ("a", "c", "d", "e", "f")
TRAIN = ("train_bf", "train_m15k", "train_armc", "train_armc_halves", "train_arme_bfS", "train_arme_cS",
         "train_arme_hS", "train_armf_jpeg")
COLS = ["path", "label", "source", "tool", "arm", "val", "mixed"]


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    path = {}
    for n in TRAIN:
        for r in csv.DictReader(open(FL / f"{n}.csv")):
            path[r["id"]] = "x/" + r["path"].lstrip("/")
    od = K.OUT / "lora/manifests"
    od.mkdir(parents=True, exist_ok=True)
    info = {}
    for arm in ARMS:
        for s in K.SEEDS:
            c = json.load(open(K.OUT / "compose" / f"{arm}_s{s}.json"))
            rows = [dict(path=path[i], label=0, source="smdd", tool="smdd", arm=f"sm1{arm}", val=0, mixed=0)
                    for i in c["genuine"]] + \
                   [dict(path=path[i], label=1, source="smdd", tool=f"sm1{arm}", arm=f"sm1{arm}", val=0, mixed=0)
                    for i in c["morph"]]
            f = od / f"train_sm1{arm}_s{s}.csv"
            with open(f, "w", newline="") as fo:
                w = csv.DictWriter(fo, fieldnames=COLS, lineterminator="\n")
                w.writeheader()
                w.writerows(rows)
            info[f.name] = dict(n=len(rows), n_morph=len(c["morph"]), sha256=K.sha(f))
    ev = []
    for n in ("test_ar1", "test_ar1h"):
        for r in csv.DictReader(open(FL / f"{n}.csv")):
            ev.append(dict(id=r["id"], path="x/" + r["path"].lstrip("/"), set="ar1", family=r["cell"],
                           label=r["label"], variant="", src_id=r["id"]))
    jv = [dict(id=r["id"], path="x/" + r["path"].lstrip("/"), set="frlljpeg", family=r["cell"], label=r["label"],
               variant=r["hist"], src_id=r["id"]) for r in csv.DictReader(open(FL / "test_eval_jpeg.csv"))]
    fj = od / "sm1_jpeg_eval.csv"
    with open(fj, "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(jv[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(jv)
    info[fj.name] = dict(n=len(jv), sha256=K.sha(fj))
    f = od / "sm1_ar1_eval.csv"
    with open(f, "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(ev[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(ev)
    info[f.name] = dict(n=len(ev), sha256=K.sha(f))
    json.dump(info, open(K.OUT / "lora/lists.json", "w"), indent=1)
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
