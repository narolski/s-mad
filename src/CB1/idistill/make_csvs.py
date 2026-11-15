"""CB1 IDistill: CSV lists in the authors' format (image_path,label with ./relative paths; label bonafide|attack).
  python3 -I make_csvs.py train SMDD_DIR LAT_DIR [--limit N]   -> SMDD_DIR/train.csv (name must be train.csv: the
        authors' loader strips 9 characters). Bona fide: ./os25k_bf_t_cropped/*; attacks: ./m15k_t_cropped/morphed_A_B.png
        kept only when both contributor latents LAT_DIR/os25k_m_t_cropped/A.png.npy and B.png.npy exist (else counted).
  python3 -I make_csvs.py frll CROP_DIR OUT_DIR   -> OUT_DIR/{asml,stylegan,facemorpher,opencv,webmorph}.csv (the
        authors' run_extra_test lists: FRLL genuine crops + one morph family's crops), and OUT_DIR/eval_all.csv
        (every crop folder of CROP_DIR, label attack for morph folders) with OUT_DIR/eval_all_meta.csv (folder, file).
        Paths relative to OUT_DIR, which must be the parent of CROP_DIR."""
import csv, os, pathlib, sys

def w(path, rows):
    with open(path, "w", newline="") as f:
        x = csv.writer(f); x.writerow(["image_path", "label"]); x.writerows(rows)

mode = sys.argv[1]
if mode == "train":
    s, lat = pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
    lim = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    bf = sorted(p.name for p in (s / "os25k_bf_t_cropped").iterdir())
    have = {p.name for p in (lat / "os25k_m_t_cropped").iterdir()}
    bfl = {p.name for p in (lat / "os25k_bf_t_cropped").iterdir()}
    rows, miss = [], 0
    for n in bf:
        if n + ".npy" in bfl:
            rows.append([f"./os25k_bf_t_cropped/{n}", "bonafide"])
        else:
            miss += 1
    for p in sorted((s / "m15k_t_cropped").iterdir()):
        a, b = p.name[8:17], p.name[18:27]
        if f"{a}.png.npy" in have and f"{b}.png.npy" in have:
            rows.append([f"./m15k_t_cropped/{p.name}", "attack"])
        else:
            miss += 1
    if lim:
        rows = rows[:lim // 2] + [r for r in rows if r[1] == "attack"][:lim // 2]
    w(s / "train.csv", rows)
    print(f"train.csv: {sum(r[1]=='bonafide' for r in rows)} bona fide, {sum(r[1]=='attack' for r in rows)} attacks; "
          f"dropped for missing latents: {miss}")
elif mode == "frll":
    crop, out = pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
    rel = os.path.relpath(crop, out)
    bona = sorted((crop / "frll_bona").iterdir())
    for fam, csvn in (("amsl", "asml"), ("stylegan", "stylegan"), ("facemorpher", "facemorpher"),
                      ("opencv", "opencv"), ("webmorph", "webmorph")):
        rows = [[f"./{rel}/frll_bona/{p.name}", "bonafide"] for p in bona]
        rows += [[f"./{rel}/frll_{fam}/{p.name}", "attack"] for p in sorted((crop / f"frll_{fam}").iterdir())]
        w(out / f"{csvn}.csv", rows)
    rows, meta = [], []
    for d in sorted(crop.iterdir()):
        lab = "bonafide" if ("bona" in d.name or "_e7_" in d.name or "native" in d.name) else "attack"
        for p in sorted(d.iterdir()):
            rows.append([f"./{rel}/{d.name}/{p.name}", lab]); meta.append([d.name, p.name])
    w(out / "eval_all.csv", rows)
    with open(out / "eval_all_meta.csv", "w", newline="") as f:
        x = csv.writer(f); x.writerow(["folder", "file"]); x.writerows(meta)
    print(f"eval_all.csv: {len(rows)} crops in {len(set(m[0] for m in meta))} folders")
