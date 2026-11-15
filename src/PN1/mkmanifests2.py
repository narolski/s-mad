"""PN1 amendment 10: manifests of the spliced LoRA arm (Sb) and its volume control (Bv), and the evaluation manifest
extended by the spliced and blanked ladder images (development and test hosts, OpenCV-style engine).
  python3 -I mkmanifests2.py  -> /mnt/t7/smad_next/PN1/manifests2/{train_A,B,Bn,C,Sb,Bv,pn1_eval}.csv, pack_files.csv
Registered manifests A, B, Bn, C are copied unchanged (byte-equal, checked)."""
import collections
import csv
import json
import pathlib
import shutil
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mkmanifests as MM  # noqa: E402
import pn1lib as K  # noqa: E402

M1 = K.PN1 / "manifests"
M2 = K.PN1 / "manifests2"
AR1 = pathlib.Path("/mnt/t7/smad_next/AR1")


def main():
    M2.mkdir(parents=True, exist_ok=True)
    lad, _ = K.split_tables()
    for n in ("train_A", "train_B", "train_Bn", "train_C"):
        shutil.copy2(M1 / f"{n}.csv", M2 / f"{n}.csv")
        assert K.sha(M1 / f"{n}.csv") == K.sha(M2 / f"{n}.csv")
    files = {r["pack_path"]: r["source"] for r in csv.DictReader(open(M1 / "pack_files.csv"))}
    srcB = list(csv.DictReader(open(M1 / "src_B.csv")))
    sp = list(csv.DictReader(open(AR1 / "manifest_splice2.csv")))
    extra = []
    for r in sp:
        if r["variant"] != "native" or r["tool"] != "opencv":
            continue
        h = lad[r["p1"]]
        if r["rung"] == "S4" and h["train_morph"] == "1":
            extra.append(dict(id=r["id"], src=r["path"], kind="lad_S4", label="1", db=r["p1"].split(":")[0], hist="native"))
        elif r["rung"] in ("S0", "S3") and h["train_genuine"] == "1":
            extra.append(dict(id=r["id"], src=r["path"], kind="lad_" + r["rung"], label="0", db=r["p1"].split(":")[0],
                              hist="native"))
    # volume control: the same number of extra rows drawn from B's unique rows, seeded, in kind proportions
    rng = np.random.default_rng(20261123)
    pick = rng.choice(len(srcB), size=len(extra), replace=False)
    vol = [dict(srcB[i]) for i in sorted(pick)]
    summ = {}
    for name, rows0 in (("Sb", srcB + extra), ("Bv", srcB + vol)):
        rows = []
        for r in rows0:
            pp = f"train/{r['kind']}/{r['id']}.png"
            assert files.get(pp, r["src"]) == r["src"]
            files[pp] = r["src"]
            rows.append(dict(path=pp, label=r["label"], source="smdd", tool="smdd", arm="smdd", val="0", mixed="0",
                             id=r["id"], kind=r["kind"], db=r["db"], hist=r["hist"]))
        bal, strata = MM.balanced_strata(rows)
        with open(M2 / f"train_{name}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=MM.TRCOLS)
            w.writeheader()
            w.writerows(bal)
        summ[name] = dict(rows=len(bal), unique=len({r["id"] for r in rows}), added=len(extra),
                          by_kind=dict(collections.Counter(r["kind"] for r in rows)), strata=strata,
                          sha256=K.sha(M2 / f"train_{name}.csv"))
    # evaluation manifest: registered rows + spliced / blanked ladder rows of development and test hosts (OpenCV)
    ev = list(csv.DictReader(open(M1 / "pn1_eval.csv")))
    keys = list(ev[0].keys())
    bm = {r["id"]: r for r in csv.DictReader(open(AR1 / "blank" / "blank_manifest.csv"))}
    add = []
    for r in sp:
        h = lad[r["p1"]]
        if r["tool"] != "opencv" or h["role"] not in ("test", "dev") or (h["role"] == "test" and h["test_read"] != "1"):
            continue
        v = r["variant"]
        rung = r["rung"] + ("" if v == "native" else "_" + v.split("_")[0])
        if v == "native" and r["rung"] not in ("S0", "S3", "S4"):
            continue
        add.append(dict(id=r["id"], path=f"eval/pn1/{r['id']}.png", src=r["path"], role=h["role"], rung=rung,
                        host=r["p1"], klass="attack" if r["rung"] in ("S4", "R4") else "single"))
    for r in csv.DictReader(open(AR1 / "manifest.csv")):
        if r["pool"] == "frgcferet" and r["rung"] == "R4" and r["tool"] == "opencv" and r["id"] in bm:
            h = lad[r["p1"]]
            if h["role"] not in ("test", "dev") or (h["role"] == "test" and h["test_read"] != "1"):
                continue
            for v, k in (("bg", "bg_path"), ("face", "face_path")):
                i = f"ar1_{r['id']}__{v}"
                add.append(dict(id=i, path=f"eval/pn1/{i}.png", src=bm[r["id"]][k], role=h["role"], rung=f"R4_{v}",
                                host=r["p1"], klass="attack"))
    have = {r["id"] for r in ev}
    for a in add:
        if a["id"] in have:
            continue
        files[a["path"]] = a["src"]
        ev.append(dict({k: "" for k in keys}, id=a["id"], path=a["path"], label="1" if a["klass"] == "attack" else "0",
                       klass=a["klass"], role=a["role"], fam="splice", rung=a["rung"], strength="", tool="opencv",
                       cell="", host=a["host"], neutral=""))
    with open(M2 / "pn1_eval.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(ev)
    with open(M2 / "pack_files.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pack_path", "source"])
        for k in sorted(files):
            w.writerow([k, files[k]])
    summ["eval"] = dict(n=len(ev), added=len(ev) - len(have), sha256=K.sha(M2 / "pn1_eval.csv"))
    K.dump(summ, M2 / "manifests2_summary.json")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "strata"} for k, v in summ.items()}, indent=1))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
