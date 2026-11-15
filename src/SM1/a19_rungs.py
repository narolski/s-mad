"""SM1 A19 H-N1 (registered 71a08f6): the three saved A18 fits on the DG1 rungs NOISEX20, NOISES20, SEMX20, SEMS20,
FRESH1_20, REC20 of the test shards 6-7, on the DGX CPU (torch threads 2, nice 10; GPU hidden).

  python3 -I a19_rungs.py build   -> OUT/a19/{sm1_a19_rungs.csv, data/manifests/, data/x -> /}
  python3 -I a19_rungs.py score   -> runs sm1_lora_audit.py per fit (reproduction check on the 401 stored test rows,
                                     tolerance 2e-3, unchanged; --continue-on-fail marks "ranks only") -> OUT/a19/res/
  python3 -I a19_rungs.py read    -> RES/a19_rungs.json (AUCs, host bootstrap, 2-seed means; verdict only if all
                                     checks passed)
"""
import csv
import json
import os
import pathlib
import subprocess
import sys
import tarfile

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import sm1_stats as S  # noqa: E402

O = K.OUT / "a19"
G = pathlib.Path("/mnt/t7/smad_next/DG1/gen")
RUNGS = ("NOISEX20", "NOISES20", "SEMX20", "SEMS20", "FRESH1_20", "REC20")
FITS = ("HN2_RS_s401", "HN2_RS_s402", "HN2_RS_s403")
H2 = K.OUT / "results_rented/hn2"


def build():
    (O / "data/manifests").mkdir(parents=True, exist_ok=True)
    x = O / "data/x"
    if not x.exists():
        x.symlink_to("/")
    test_hosts = {r["src_id"] for r in csv.DictReader(open(K.OUT / "hn2/sm1_hn2_test.csv"))}
    rows = []
    for r in csv.DictReader(open("/mnt/t7/smad_next/FZ2/read_addon_items.csv")):
        if r["key"] in RUNGS and r["host"] in test_hosts:
            p = G / r["list"] / r["id"]
            assert p.exists(), p
            rows.append(dict(id=f"a19:{r['key']}:{r['host']}", path="x" + str(p), set="a19", family=r["key"], label=0,
                             variant="orig", src_id=r["host"]))
    f = O / "data/manifests/sm1_a19_rungs.csv"
    with open(f, "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    import shutil
    shutil.copy2(K.OUT / "hn2/sm1_hn2_test.csv", O / "data/manifests/sm1_hn2_test.csv")
    # code + weights (ad4 pack without its data folders)
    if not (O / "ad4/code").exists():
        with tarfile.open("/mnt/t7/smad_next/AD4/ad4_pack.tar") as t:
            t.extractall(O, members=[m for m in t.getmembers() if not m.name.startswith(("ad4/data/eval", "ad4/data/train"))])
    for T in FITS:                                       # fit view: ad4eval -> hn2test (where ad4_score saved them)
        v = O / "fits" / T
        v.mkdir(parents=True, exist_ok=True)
        for n in ("meta.json",):
            if not (v / n).exists():
                (v / n).symlink_to(H2 / T / n)
        if not (v / "ad4eval").exists():
            (v / "ad4eval").symlink_to(H2 / T / "hn2test")
    print(len(rows), "rung rows;", {k: sum(r["family"] == k for r in rows) for k in RUNGS})


def score():
    env = dict(os.environ, SMAD_DATA=str(O / "data"), HF_HOME=str(O / "ad4/hf"), HF_HUB_OFFLINE="1",
               CUDA_VISIBLE_DEVICES="", OMP_NUM_THREADS="2", MKL_NUM_THREADS="2", PYTHONUNBUFFERED="1")
    for T in FITS:
        out = O / "res" / T
        if (out / "scores_audit.npz").exists():
            continue
        cmd = ["nice", "-n", "10", sys.executable, str(pathlib.Path(__file__).parent / "sm1_lora_audit.py"),
               "--fit", str(O / "fits" / T), "--code", str(O / "ad4/code"), "--manifest", "sm1_a19_rungs.csv",
               "--out", str(out), "--workers", "2", "--bs", "32", "--ncheck", "401",
               "--check-npz", "ad4eval/scores_eval.npz", "--check-manifest", "sm1_hn2_test.csv", "--continue-on-fail"]
        print(" ".join(cmd), flush=True)
        subprocess.run(cmd, env=env, check=True)


def read():
    rows = list(csv.DictReader(open(O / "data/manifests/sm1_a19_rungs.csv")))
    fam, host = {}, {}
    for r in rows:
        fam.setdefault(r["family"], []).append(r["id"])
        host[r["id"]] = r["src_id"]
    hosts = sorted(set(host.values()))
    hp = {h: i for i, h in enumerate(hosts)}
    Cb = np.random.default_rng(K.SEED).multinomial(len(hosts), np.full(len(hosts), 1 / len(hosts)), size=10000).astype(float)
    W = lambda ids: Cb[:, [hp[host[i]] for i in ids]]  # noqa: E731
    per, checks = {}, {}
    for T in FITS:
        chk = json.load(open(O / "res" / T / "check.json"))
        checks[T] = {k: chk.get(k) for k in ("max_abs_score_diff", "passed", "rank_agreement_spearman", "platform")}
        z = np.load(O / "res" / T / "scores_audit.npz")
        p = np.clip(z["score_noTTA"].astype(float), 1e-7, 1 - 1e-7)
        zi = dict(zip([str(i) for i in z["id"]], np.log(p / (1 - p))))
        g = lambda ids: np.array([zi[i] for i in ids])  # noqa: E731
        m = {}
        for a, b in (("NOISEX20", "NOISES20"), ("SEMX20", "SEMS20"), ("FRESH1_20", "REC20"), ("NOISES20", "REC20"),
                     ("SEMS20", "REC20")):
            m[f"{a}_over_{b}"] = (float(S.wauc(g(fam[a]), g(fam[b]), np.ones((1, len(fam[a]))), np.ones((1, len(fam[b]))))[0]),
                                  S.wauc(g(fam[a]), g(fam[b]), W(fam[a]), W(fam[b])))
        per[T] = m
    two = [per[t] for t in FITS[:2]]
    out = dict(checks=checks, per_fit={T: {k: round(v[0], 4) for k, v in m.items()} for T, m in per.items()})
    out["two_seed"] = {k: dict(mean=round(float(np.mean([m[k][0] for m in two])), 4),
                               ci=[round(x, 4) for x in S.ci(np.mean([m[k][1] for m in two], 0))]) for k in two[0]}
    nx, sx = out["two_seed"]["NOISEX20_over_NOISES20"]["mean"], out["two_seed"]["SEMX20_over_SEMS20"]["mean"]
    if all(c["passed"] for c in checks.values()):
        out["verdict"] = ("supported: noise path" if nx >= 0.90 and sx <= 0.70 else
                          "falsified: semantic or identity path" if sx >= 0.85 and sx > nx else "undecided")
    else:
        out["verdict"] = "no registered verdict: platform not equivalent (reproduction check failed); ranks only"
    json.dump(out, open(K.RES / "a19_rungs.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    dict(build=build, score=score, read=read)[sys.argv[1]]()
