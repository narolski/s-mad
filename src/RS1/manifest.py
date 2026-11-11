"""Own-crop re-score of the audit rows (RS1): image manifest.

  python3 -I manifest.py build   -> OUT/manifest.csv (every image, its set, persons, expression, source) and
                                    OUT/lists/tocrop.csv (images that need a new release crop) and
                                    OUT/lists/cropcheck.csv (32 raw files already cropped by A46, re-cropped as a check)
  python3 -I manifest.py merge   -> after crop_rgb.py: OUT/lists/score.csv (id, path = the crop each release receives)
                                    and OUT/crop_status.json (faces not found, per set)

Sources (no image is changed here):
  A46 RGB crops of the raw files  /mnt/t7/smad_heldout/a46_corrective_20261108 (manifest a46c_rgb_clip.csv, SHA256SUMS)
  raw E7 files (A41 x7 staged)    /mnt/t7/smad_heldout/a41g/x7work/in/<staged>  (sha in x7_inputs.csv)
  aligned frames (eval.csv)       /home/narolski/mambamorph-code/smadcvpr_data/<path>  (eval.csv sha 86d055d3...)
  A43 control images as stored    /mnt/t7/smad_heldout/a43/data/<stored_path>  (a43.csv sha ce3a264a...)
"""
import collections
import csv
import hashlib
import json
import pathlib
import re
import sys

OUT = pathlib.Path("/mnt/t7/smad_next/RS1")
A46 = pathlib.Path("/mnt/t7/smad_heldout/a46_corrective_20261108")
X7W = pathlib.Path("/mnt/t7/smad_heldout/a41g/x7work")
DATA = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr_data")
A43 = pathlib.Path("/mnt/t7/smad_heldout/a43/data")
PIN = {DATA / "manifests/eval.csv": "86d055d349c63a225893ace30cb3db8b1e9aea4e72350d78152126d7a49d56c9",
       A43 / "manifests/a43.csv": "ce3a264adb30928d",
       X7W / "x7_inputs.csv": None}
FRLL_FAM = ("amsl", "facemorpher", "opencv", "webmorph", "stylegan")
DIM_FAM = ("dim_a", "dim_c", "fast_dim", "fast_dim_ode", "greedy_dim", "greedy_dim_s")
E7RAW = ("mordiff", "dim_a", "greedy_dim")
COLS = ["id", "set", "label", "persons", "photo", "expr", "src_path", "src_sha256", "crop_origin", "crop_path"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def forbidden(p):
    s = str(p).lower()
    return any(x in s for x in ("fst", "a12sp", "a12-sp")) or ("valx" in s and not s.endswith("valx_a.csv"))


def pers_of(name, label):
    """FRLL persons from a file name: photo 001_03 -> ('001',), '03'; morph 001_002 / morph_001_03_and_002_03 -> pair."""
    if label == 0:
        m = re.match(r"^(\d{3})_(\d{2})", name)
        return (m.group(1),), f"{m.group(1)}_{m.group(2)}", m.group(2)
    m = re.match(r"^morph_(\d{3})_(\d{2})_and_(\d{3})_(\d{2})", name)
    if m:
        return (m.group(1), m.group(3)), "", m.group(2) if m.group(2) == m.group(4) else "mix"
    m = re.match(r"^(\d{3})_(\d{3})", name)
    return (m.group(1), m.group(2)), "", ""


def build():
    for p, pin in PIN.items():
        if pin:
            assert sha(p).startswith(pin), p
    rows = []
    # 1. A46 RGB crops of the raw files (reused; hash-checked)
    sums = {}
    for ln in open(A46 / "SHA256SUMS"):
        h, f = ln.strip().split(None, 1)
        sums[f.lstrip("*")] = h
    pools = {"frllm_frll_bona": "G_raw", "mordiff_mordiff": "M_mordiff",
             **{f"frllm_{f}": f"M_{f}" for f in FRLL_FAM}, **{f"dim_{f}": f"M_{f}" for f in DIM_FAM}}
    bad = 0
    for r in csv.DictReader(open(A46 / "manifests/a46c_rgb_clip.csv")):
        if r["pool"] not in pools:
            continue
        lab = int(r["label"])
        pp, ph, ex = pers_of(pathlib.Path(r["src_path"]).name, lab)
        h = sha(A46 / r["path"])
        bad += h != sums.get(r["path"])
        rows.append(dict(id=r["id"], set=pools[r["pool"]], label=lab, persons="|".join(pp), photo=ph, expr=ex,
                         src_path=r["src_path"], src_sha256="", crop_origin="a46", crop_path=str(A46 / r["path"])))
    assert bad == 0, f"{bad} A46 crops differ from SHA256SUMS"
    # 2. raw E7 files (staged A41 x7 inputs; NOT the SelfMAD-cropped copies in a41g_x7/)
    n = 0
    for r in csv.DictReader(open(X7W / "x7_inputs.csv")):
        fam = r["set"].replace("e7area_", "") if r["set"].startswith("e7area_") else None
        if fam not in E7RAW:
            continue
        p = X7W / r["staged"]
        assert sha(p) == r["staged_sha256"], p
        pp, ph, ex = pers_of(p.name, 0)
        rows.append(dict(id=f"rs1e7r{n:05d}", set=f"E7raw_{fam}", label=0, persons=pp[0], photo=ph, expr=ex,
                         src_path=str(p), src_sha256=r["staged_sha256"], crop_origin="rs1", crop_path=""))
        n += 1
    # 3. aligned frames (our 512 eye-aligned frames, eval.csv): native and E7 photos
    for r in csv.DictReader(open(DATA / "manifests/eval.csv")):
        if r["label"] != "0" or r["variant"] not in ("orig", "resmatch"):
            continue
        st, fam, var = r["set"], r["family"], r["variant"]
        if st == "frllm" and var == "orig":
            s = "Galn_frll"
        elif st == "mordiff" and var == "orig":
            s = "Galn_mordiff"
        elif var == "resmatch" and st in ("frllm", "mordiff", "dim"):
            s = f"E7aln_{fam}"
        else:
            continue
        p = DATA / r["path"]
        assert not forbidden(p)
        pp, ph, ex = pers_of(p.name, 0)
        rows.append(dict(id=f"rs1{r['id']}", set=s, label=0, persons=pp[0], photo=ph, expr=ex, src_path=str(p),
                         src_sha256="", crop_origin="rs1", crop_path=""))
    # 4. A43 control images as stored (the files a release would receive)
    for r in csv.DictReader(open(A43 / "manifests/a43.csv")):
        if not r["arm"]:
            continue
        p = A43 / r["stored_path"]
        if r["arm"] in ("A", "B", "B20"):
            pp, lab = (r["src_a"][:3], r["src_b"][:3]), 1
            ex = r["src_a"][4:6] if r["src_a"][4:6] == r["src_b"][4:6] else "mix"
            ph = ""
        else:
            pp, lab = (r["src_a"][:3],), 0
            ph = r["src_a"] if r["arm"] not in ("C", "C20") else ""
            ex = r["src_a"][4:6] if r["arm"] not in ("C", "C20") else "mix"
        assert sha(p) == r["stored_sha256"], p
        rows.append(dict(id=f"rs1{r['id']}", set=f"a43_{r['arm']}", label=lab, persons="|".join(pp), photo=ph,
                         expr=ex, src_path=str(p), src_sha256=r["stored_sha256"], crop_origin="rs1", crop_path=""))
    ids = [r["id"] for r in rows]
    assert len(set(ids)) == len(ids)
    (OUT / "lists").mkdir(parents=True, exist_ok=True)
    with open(OUT / "manifest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    with open(OUT / "lists/tocrop.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "path"])
        w.writeheader()
        w.writerows([dict(id=r["id"], path=r["src_path"]) for r in rows if r["crop_origin"] == "rs1"])
    # crop check: 32 raw files already cropped by A46 (8 photos, 8 per FRLL OpenCV, MorDIFF, DiM-A), re-cropped
    chk = []
    for s in ("G_raw", "M_opencv", "M_mordiff", "M_dim_a"):
        chk += [dict(id="chk_" + r["id"], path=r["src_path"]) for r in rows if r["set"] == s][:8]
    with open(OUT / "lists/cropcheck.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "path"])
        w.writeheader()
        w.writerows(chk)
    c = collections.Counter(r["set"] for r in rows)
    print(json.dumps(dict(sorted(c.items())), indent=0))
    print("to crop", sum(r["crop_origin"] == "rs1" for r in rows))
    persons = {p for r in rows for p in r["persons"].split("|")}
    photos = {r["persons"] for r in rows if r["set"] == "G_raw"}
    print("persons", len(persons), "photo persons", len(photos), "outside", sorted(persons - photos)[:5])


def merge():
    rows = list(csv.DictReader(open(OUT / "manifest.csv")))
    st = {}
    for f in sorted((OUT / "crops/main").glob("crops*.csv")):
        for r in csv.DictReader(open(f)):
            st[r["id"]] = r
    miss = collections.Counter()
    out = []
    for r in rows:
        if r["crop_origin"] == "rs1":
            s = st.get(r["id"])
            if s is None:
                sys.exit(f"{r['id']}: not cropped")
            if s["status"] in ("retained",) or s["status"].startswith("flag:"):
                r["crop_path"] = s["path"]
            else:
                miss[r["set"]] += 1
                r["crop_path"] = ""
        if r["crop_path"]:
            out.append(dict(id=r["id"], path=r["crop_path"]))
    with open(OUT / "manifest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    with open(OUT / "lists/score.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "path"])
        w.writeheader()
        w.writerows(out)
    tot = collections.Counter(r["set"] for r in rows)
    flags = collections.Counter(s["status"].split(":")[0] for s in st.values())
    json.dump(dict(missing=dict(miss), totals=dict(tot), crop_status=dict(flags)), open(OUT / "crop_status.json", "w"),
              indent=1)
    print("score list", len(out), "missing", dict(miss), dict(flags))


if __name__ == "__main__":
    {"build": build, "merge": merge}[sys.argv[1]]()
