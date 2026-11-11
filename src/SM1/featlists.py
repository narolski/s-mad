"""SM1 lists for the feature pass (columns id, path + metadata). No image is read.

  python3 -I featlists.py train     -> OUT/flists/train_*.csv (genuine renders, release morphs, our builds, halves)
  python3 -I featlists.py test      -> OUT/flists/test_{eval,mad22,ar1,ar1h}.csv
  python3 -I featlists.py audit     -> OUT/flists/audit.csv (Part 2 images, for the Part 3 heads, A1.1)
Test metadata: cell, label (1 = morph), hist (native / e7), p1, p2 (persons; FRLL ids NNN, AR1 pids).
eval.csv rows of set mad22 (old subset) and all variants other than orig / resmatch are never listed.
"""
import csv
import pathlib
import re
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402

FL = K.OUT / "flists"
L = K.OUT / "lists"
EVAL = K.MC / "smadcvpr_data/manifests/eval.csv"
M22 = pathlib.Path("/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z")
AR1M = pathlib.Path("/mnt/t7/smad_next/AR1/manifest.csv")


def write(name, rows):
    FL.mkdir(parents=True, exist_ok=True)
    keys = list(rows[0])
    with open(FL / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print(name, len(rows))


def rd(name):
    return list(csv.DictReader(open(L / name)))


def halves(rows, prefix):
    out = []
    for r in rows:
        for s in ("hA", "hB"):
            out.append(dict(id=f"{r['id']}_{s}", path=r["out"][:-4] + f"_{s}.png", pair=r["id"],
                            person=r["na"] if s == "hA" else r["nb"]))
    return out


def train():
    if not (FL / "train_bf.csv").exists():
        write("train_bf.csv", [dict(id=f"bf:{p.name[:-4]}", path=str(p), pair="", person=p.name[:-4])
                           for p in sorted(K.BF_T.glob("*.png"))])
    if not (L / "arma.csv").exists():
        return
    write("train_arma.csv", [dict(id=r["id"], path=r["path"], pair=r["id"], person=r["na"], size=r["size"])
                             for r in rd("arma.csv")])
    for arm in ("armb", "armbp", "armc", "armcr", "armd50", "armd500"):
        if not (L / f"{arm}.csv").exists():
            continue
        rows = rd(f"{arm}.csv")
        write(f"train_{arm}.csv", [dict(id=r["id"], path=r["out"], pair=r["id"], person=r["na"]) for r in rows])
        if arm == "armc":                                              # (c') has no halves (A1)
            write(f"train_{arm}_halves.csv", halves(rows, arm))
    # arm (e) shrunk copies (A4): genuine renders = the stored a47 copies; (c) morphs and halves = shrink.py outputs
    st = pathlib.Path("/mnt/t7/smad_heldout/a47/data47/i3/train/smdd_a47e7/os25k_bf_t")
    write("train_arme_bfS.csv", [dict(id=f"bfS:{p.name[:-4]}", path=str(st / p.name), pair="", person=p.name[:-4])
                                 for p in sorted(K.BF_T.glob("*.png"))])
    rc = rd("armc.csv")
    write("train_arme_cS.csv", [dict(id=f"{r['id']}_S", path=str(K.OUT / "img/arme" / pathlib.Path(r["out"]).name),
                                     pair=r["id"], person=r["na"]) for r in rc])
    write("train_arme_hS.csv", [dict(id=f"{h['id']}_S", path=str(K.OUT / "img/arme" / pathlib.Path(h["path"]).name),
                                     pair=h["pair"], person=h["person"]) for h in halves(rc, "armc")])
    # pool-cue check (A1.3): 5,000 non-contributor os25k_m_t renders outside the audit set vs 5,000 os25k_bf_t
    aud = {r["name"] for r in rd("audit_renders.csv")}
    contrib = {x for p in K.release_pairs() for x in p}
    src = sorted(p.name[:-4] for p in K.SRC_T.glob("*.png") if p.name[:-4] not in contrib | aud)
    rng = np.random.default_rng(K.SEED + 13)
    pick = sorted(rng.choice(src, size=5000, replace=False).tolist())
    write("train_srcm_cue.csv", [dict(id=f"srcm:{n}", path=str(K.SRC_T / f"{n}.png"), pair="", person=n) for n in pick])


def smoke():
    for arm in ("armb", "armbp", "armc", "armcr"):
        rows = rd(f"smoke_{arm}.csv")
        write(f"smoke_train_{arm}.csv", [dict(id=r["id"], path=r["out"], pair=r["id"], person=r["na"]) for r in rows])
        if arm == "armc":
            write(f"smoke_train_{arm}_halves.csv", halves(rows, arm))


def frll_persons(name):
    s = re.sub(r"_(orig|resmatch).*$", "", name.replace("morph_", "").replace(".png", ""))
    ids = re.findall(r"(\d{3})(?:_0[38])?", s)
    return ids[0], ids[-1]


def test():
    rows = []
    for r in csv.DictReader(open(EVAL)):
        if r["set"] not in ("frllm", "mordiff", "dim") or r["variant"] not in ("orig", "resmatch"):
            continue
        p = K.MC / "smadcvpr_data" / r["path"]
        p1, p2 = frll_persons(p.name)
        fam = r["family"]
        if r["label"] == "1":
            cell, hist = f"{r['set']}:{fam}", "morph"
        elif r["variant"] == "orig":
            cell, hist = f"{r['set']}:bona", "native"
        else:
            cell, hist = f"{r['set']}:{fam}", "e7"
        rows.append(dict(id=f"ev:{r['id']}", path=str(p), cell=cell, label=r["label"], hist=hist, p1=p1, p2=p2,
                         expr=p.name.split("_")[1] if r["label"] == "0" else ""))
    write("test_eval.csv", rows)
    rows = []
    for fam in sorted(x.name for x in (M22 / "native").iterdir()):
        for p in sorted((M22 / "native" / fam).glob("*.png")):
            if fam == "BonaFide":
                rows.append(dict(id=f"m22:native/{fam}/{p.stem}", path=str(p), cell="mad22:bona", label="0",
                                 hist="native", p1=p.stem[:3], p2=p.stem[:3], expr=p.stem[4:6]))
            else:
                a, b = p.stem.split("-vs-")
                rows.append(dict(id=f"m22:native/{fam}/{p.stem}", path=str(p), cell=f"mad22:{fam}", label="1",
                                 hist="morph", p1=a[:3], p2=b[:3], expr=""))
    for fam in sorted(x.name for x in (M22 / "e7").iterdir()):
        for p in sorted((M22 / "e7" / fam).glob("*.png")):
            rows.append(dict(id=f"m22:e7/{fam}/{p.stem}", path=str(p), cell=f"mad22:{fam}", label="0", hist="e7",
                             p1=p.stem[:3], p2=p.stem[:3], expr=p.stem[4:6]))
    write("test_mad22.csv", rows)
    rows = [dict(id=f"ar1:{r['id']}", path=r["path"], cell=f"ar1:{r['pool']}:{r['tool']}:{r['rung']}",
                 label="1" if r["rung"].startswith("R4") or r["rung"] == "G" else "0", hist=r["level"], p1=r["p1"],
                 p2=r["p2"], expr="") for r in csv.DictReader(open(AR1M))]
    write("test_ar1.csv", rows)
    rows = []
    for r in rd("ar1h.csv"):
        for s, per in (("hA", r["na"]), ("hB", r["nb"])):
            rows.append(dict(id=f"ar1h:{r['id']}_{s}", path=r["out"][:-4] + f"_{s}.png", cell=f"ar1:frgcferet:opencv:H{s[1]}",
                             label="0", hist="", p1=per, p2=per, expr=""))
    write("test_ar1h.csv", rows)


def audit():
    ren = [dict(id=r["id"], path=r["path"], kind=r["kind"], key="", partner=r["name"], slot="")
           for r in rd("audit_renders.csv")]
    for src, dst in (("audit.csv", "audit.csv"), ("smoke_audit.csv", "smoke_audit.csv")):
        rows = [dict(id=r["id"], path=r["out"], kind=r["kind"], key=r["key"], partner=r["partner"], slot=r["slot"])
                for r in rd(src)]
        write(dst, rows + ren)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    {"train": train, "test": test, "audit": audit, "smoke": smoke}[sys.argv[1]]()
