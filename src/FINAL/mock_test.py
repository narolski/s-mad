"""Sealed MAD22 read (FINAL): mock tests of the reader on SYNTHETIC scores for every outcome branch. No real score of
any network on any benchmark row is used or exists; the release file is synthetic too (same format as
release_scores_existing.npz). Each branch builds a stand-in result tar exactly like remote_final.sh's, a mock pins
file, runs final_read.py as a subprocess (python -I) with its own marker, and asserts the registered outcome.
  python3 -I mock_test.py --pack PACK.tar [--branches all|exceeded,...] --work DIR"""
import argparse
import csv
import hashlib
import io
import json
import pathlib
import shutil
import subprocess
import sys
import tarfile

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
CFG = json.load(open(HERE / "final_config.json"))
FAMS = ("FaceMorpher", "MIPGAN_I", "MIPGAN_II", "OpenCV", "Webmorph")
DETS = ("madation_vitb16", "madation_vitl14", "mixfacenet_mad_smdd")


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def manifest(pack):
    with tarfile.open(pack) as t:
        return list(csv.DictReader(io.StringIO(t.extractfile("final/data/manifests/final_bench.csv").read().decode())))


def latent(man, seed):
    """one latent per row: morphs N(2, 1), genuine N(0, 1); the BE copy of a row shares its original's latent."""
    rng = np.random.default_rng(seed)
    base = {}

    def key(r):      # a genuine photo has one latent in every pool (native, E7, BE copies); a morph one per file
        nm = pathlib.PurePath(r["path"]).name
        return ("morph", r["family"], nm) if r["label"] == "1" else ("genuine", nm)
    for r in man:
        if key(r) not in base:
            base[key(r)] = rng.normal(2.0 if r["label"] == "1" else 0.0, 1.0)
    return {r["id"]: base[key(r)] for r in man}


def our_scores(man, L, branch, k):
    rng = np.random.default_rng(1000 + k)
    out = {}
    for r in man:
        x = L[r["id"]]
        if branch == "exceeded":
            x = x * 0.2 + (3.0 if r["label"] == "1" else 0.0)          # near-perfect separation
        elif branch == "lost":
            x = rng.normal(0.3 if r["label"] == "1" else 0.0, 1.0)      # near chance
        elif branch == "comparable":
            # seeds disagree: two seeds better than the best release, three worse -> wide seed-level interval around 0
            x = (x * 0.75 + (0.5 if r["label"] == "1" else 0.0)) if k < 2 else (x + rng.normal(0, 0.45))
        elif branch == "border":
            if r["form"].startswith("be:") and r["label"] == "0":
                x = x + 1.5                                            # genuine look like morphs once blanked
        out[r["id"]] = x
    return out


def release_npz(man, L, path, branch):
    cols = dict(det=[], variant=[], pool=[], logit=[], pa=[], pb=[], expr=[])
    rng = np.random.default_rng(77)
    std = [r for r in man if r["form"] == "std"]
    for det in DETS:
        for v in ("v1", "v2"):
            shift = {"madation_vitb16": 0.0, "madation_vitl14": 0.6, "mixfacenet_mad_smdd": 1.2}[det]
            for r in std:
                if r["pool"] == "morph":
                    pool = f"M22_{r['family']}"
                elif r["pool"] == "e7":
                    pool = f"E7aln22_{r['family']}"
                else:
                    pool = "G22_raw"
                x = L[r["id"]]
                if det != "madation_vitb16" or branch in ("lost", "comparable", "exceeded"):
                    x = x - (shift if r["label"] == "1" else 0.0) + (rng.normal(0, 0.3) if branch != "matched" else 0.0)
                cols["det"].append(det); cols["variant"].append(v); cols["pool"].append(pool)
                cols["logit"].append(x); cols["pa"].append(r["pa"]); cols["pb"].append(r["pb"]); cols["expr"].append(r["expr"])
                if pool == "G22_raw":
                    cols["det"].append(det); cols["variant"].append(v); cols["pool"].append("G22_aln")
                    cols["logit"].append(x); cols["pa"].append(r["pa"]); cols["pb"].append(r["pb"]); cols["expr"].append(r["expr"])
            for i in range(50):
                cols["det"].append(det); cols["variant"].append(v); cols["pool"].append("FF_orig")
                cols["logit"].append(rng.normal()); cols["pa"].append("ffhq"); cols["pb"].append("ffhq"); cols["expr"].append("")
    np.savez(path, **{k: np.array(v) for k, v in cols.items()})


def result_tar(work, man, branch, scores):
    rid = CFG["read_id"]
    T = f"{rid}_mock{branch}"
    R = work / "res" / T
    (R / "scores").mkdir(parents=True)
    gate_fail = branch == "gatefail"
    (R / "rc").write_text("FATAL GATE FAILED (no benchmark row scored)\n" if gate_fail else "0\n")
    g = dict(all_pass=not gate_fail, passed=[] if gate_fail else [n["name"] for n in CFG["networks"]],
             failed=[CFG["networks"][2]["name"]] if gate_fail else [])
    (R / "gate.json").write_text(json.dumps(g))
    (R / "gate.txt").write_text("FINALGATE mock\n")
    (R / "versions.txt").write_text("mock\n"); (R / "gpu.txt").write_text("mock\n")
    shutil.copy(HERE / "final_config.json", R / "final_config.json")
    if not gate_fail:
        ids = [r["id"] for r in man]
        for k, n in enumerate(CFG["networks"]):
            s = scores[k]
            np.savez(R / "scores" / f"{n['name']}__final.npz", id=np.array(ids), logit=np.array([s[i] for i in ids], np.float32), seed=n["seed"])
    tp = work / f"{T}.tar"
    with tarfile.open(tp, "w") as t:
        t.add(R, arcname=T)
    (work / f"{T}.tar.sha256").write_text(f"{sha(tp)}  {tp.name}\n")
    return tp


EXPECT = {"exceeded": "exceeded", "matched": "matched", "lost": "lost", "comparable": "comparable, not separated",
          "gatefail": "no read", "border": "matched", "nonfinite": "no read"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True); ap.add_argument("--work", required=True)
    ap.add_argument("--branches", default="all"); ap.add_argument("--thresholds", required=True)
    a = ap.parse_args()
    man = manifest(a.pack)
    L = latent(man, 5)
    branches = list(EXPECT) if a.branches == "all" else a.branches.split(",")
    res = {}
    for br in branches:
        w = pathlib.Path(a.work) / br
        if w.exists():
            shutil.rmtree(w)
        w.mkdir(parents=True)
        if br == "matched" or br == "border":
            sc = [dict(L) for _ in CFG["networks"]]                     # identical to the best release, every seed
        else:
            sc = [our_scores(man, L, br, k) for k in range(len(CFG["networks"]))]
        if br == "border":
            sc = [our_scores(man, L, "border", k) for k in range(len(CFG["networks"]))]
        if br == "nonfinite":
            sc = [dict(L) for _ in CFG["networks"]]
            sc[1][man[3]["id"]] = float("nan")
        rel = w / "rel.npz"; release_npz(man, L, rel, br)
        tp = result_tar(w, man, br, sc)
        pins = dict(config=CFG, pack=sha(a.pack), release_existing=sha(rel), thresholds=sha(a.thresholds))
        extra_args = []
        if br == "exceeded":                                            # also exercise the SelfMAD and statistic inputs
            z = dict(np.load(rel))
            k = (z["det"] == "madation_vitb16") & (z["variant"] == "v1")
            sm = {c: z[c][k] for c in z}
            sm["det"] = np.array(["selfmad_hrnet_w18"] * int(k.sum())); sm["variant"] = np.array(["own_dgx"] * int(k.sum()))
            sm["logit"] = sm["logit"] + np.random.default_rng(3).normal(0, 0.5, int(k.sum()))
            np.savez(w / "selfmad.npz", **sm)
            np.savez(w / "beststat.npz", id=np.array([r["id"] for r in man]),
                     noise_std_face=np.array([-L[r["id"]] + np.random.default_rng(4).normal() for r in man]))
            pins.update(selfmad=sha(w / "selfmad.npz"), beststat=sha(w / "beststat.npz"))
            extra_args = ["--selfmad", str(w / "selfmad.npz"), "--beststat", str(w / "beststat.npz")]
        cmd = [sys.executable, "-I", str(HERE / "final_read.py"), "--result", str(tp), "--pack", a.pack,
               "--release-existing", str(rel), "--thresholds", a.thresholds, "--pins", str(w / "pins.json")] + extra_args + [
               "--out", str(w / "read.json"), "--tables", str(w / "tables.md"), "--marker", str(w / "marker")]
        (w / "pins.json").write_text(json.dumps(pins))
        p = subprocess.run(cmd, capture_output=True, text=True)
        if p.returncode != 0:
            res[br] = dict(ok=False, err=p.stderr[-2000:]); continue
        o = json.load(open(w / "read.json"))
        ok = o["outcome"] == EXPECT[br]
        extra = {}
        if br == "border":
            extra["border_caveat"] = [f for f, b in o["border"].items() if b["caveat"]]
            ok = ok and set(extra["border_caveat"]) == {"FaceMorpher", "MIPGAN_I", "MIPGAN_II"}
        if br == "exceeded":
            c = o["cells"]["H"]["OpenCV"]
            extra["selfmad_row"] = c["releases"].get("selfmad_hrnet_w18/own_dgx") is not None
            extra["selfmad_be_na"] = o["cells"]["BE_H"]["OpenCV"]["releases"].get("selfmad_hrnet_w18/own_dgx") is None
            extra["reference_row"] = c["reference_statistic"] is not None
            ok = ok and extra["selfmad_row"] and extra["selfmad_be_na"] and extra["reference_row"]
        if br != "gatefail":
            extra["selfmad_note"] = any("SelfMAD" in n for n in o["notes"])
            extra["forecasts"] = {k: v["verdict"] for k, v in o["forecasts"].items()}
        # second run must refuse (run-once)
        p2 = subprocess.run(cmd[:-6] + ["--out", str(w / "read2.json"), "--tables", str(w / "t2.md"), "--marker", str(w / "marker")],
                            capture_output=True, text=True)
        extra["second_run_refused"] = p2.returncode != 0 and "runs once" in (p2.stderr + p2.stdout)
        ok = ok and extra["second_run_refused"]
        res[br] = dict(ok=ok, outcome=o["outcome"], expected=EXPECT[br], sentence=o["sentences"].get("primary"), **extra)
    print(json.dumps(res, indent=1))
    (pathlib.Path(a.work) / "mock_results.json").write_text(json.dumps(res, indent=1))
    sys.exit(0 if all(v["ok"] for v in res.values()) else 1)


if __name__ == "__main__":
    main()
