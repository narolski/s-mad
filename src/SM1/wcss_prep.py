"""SM1: pack and stage a WCSS CPU build task (OWNER_BRIEF "WCSS CPU jobs"): one tar in, one tar out.

  python3 -I wcss_prep.py --task c                -> (c) armc + (c') armcr, 15,000 pairs each, from os25k_bf_t
  python3 -I wcss_prep.py --task b                -> (b) armb + (b') armbp, from os25k_m_t (after the contributor pass)
Writes, under OUT/wcss/ (mirrors /lustre/.../smad-next/):
  packs/SM1/sm1_<task>_pack.tar   code (the unchanged 68/78 engine files, build.py, sm1_common.py), lists with paths
                                  relative to the work dir, the renders and .tem files the lists use, DGX reference
                                  outputs of the first 8 rows of each list (cross-machine pixel check)
  staging/SM1/cpu/SM1_cpu_<task>/{run.sh, est_minutes, cpus}
The DGX reference outputs are made here with the same build.py (local engine, OpenCV of the DGX venv).
"""
import argparse
import csv
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tarfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
W = K.OUT / "wcss"
LUS = "/lustre/pd03/hpc-narolski-1790461090/smad-next"
TASKS = {"c": ("armc_15k", "armcr_15k"), "b": ("armb", "armbp", "armd50", "armd500")}
NAMES = {"armc_15k": "armc", "armcr_15k": "armcr", "armb": "armb", "armbp": "armbp", "armd50": "armd50",
         "armd500": "armd500"}


def rel(p):
    p = str(p)
    for src, dst in ((str(K.BF_T) + "/", "bf/"), (str(K.SRC_T) + "/", "srcm/"), (str(K.OUT / "tem") + "/", "tem/"),
                     (str(K.OUT / "img") + "/", "out/")):
        if p.startswith(src):
            return dst + p[len(src):]
    raise ValueError(p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, choices=sorted(TASKS))
    ap.add_argument("--cpus", type=int, default=48)
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    src = W / f"packsrc_{a.task}"
    if src.exists():
        shutil.rmtree(src)
    (src / "code/scripts").mkdir(parents=True)
    (src / "code/sm1").mkdir(parents=True)
    (src / "lists").mkdir()
    for f in (K.S68, K.S78):
        shutil.copy2(f, src / "code/scripts" / f.name)
        assert K.sha(f) == K.sha(src / "code/scripts" / f.name)
    for f in ("build.py", "sm1_common.py"):
        shutil.copy2(HERE / f, src / "code/sm1" / f)
    files, comp, refrows = set(), [], []
    for ln in TASKS[a.task]:
        rows = list(csv.DictReader(open(K.OUT / "lists" / f"{ln}.csv")))
        out = []
        for r in rows:
            q = dict(r)
            for k in ("a", "ta", "b", "tb"):
                q[k] = rel(r[k])
                if k in ("a", "b"):
                    files.add(r[k])
                else:
                    files.add(r[k])
            q["out"] = rel(r["out"]).replace(f"out/{NAMES[ln]}/", f"out/{NAMES[ln]}/")
            out.append(q)
        with open(src / "lists" / f"{NAMES[ln]}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(out[0]))
            w.writeheader()
            w.writerows(out)
        for r, q in zip(rows[:8], out[:8]):                      # DGX references (absolute paths for the local build)
            rr = dict(r)
            rr["out"] = str(src / "ref" / NAMES[ln] / pathlib.Path(r["out"]).name)
            refrows.append(rr)
            names = [pathlib.Path(q["out"]).name]
            if r["halves"] == "1":
                names += [names[0][:-4] + "_hA.png", names[0][:-4] + "_hB.png"]
            for n in names:
                comp.append(dict(out=f"out/{NAMES[ln]}/{n}", ref=f"ref/{NAMES[ln]}/{n}"))
    with open(W / f"ref_{a.task}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(refrows[0]))
        w.writeheader()
        w.writerows(refrows)
    p = subprocess.run([K.PY, "-I", str(HERE / "build.py"), "--list", str(W / f"ref_{a.task}.csv"), "--workers", "1",
                        "--log-dir", str(src / "ref")], capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    with open(src / "lists/compare_ref.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["out", "ref"])
        w.writeheader()
        w.writerows(comp)
    pk = W / "packs/SM1" / f"sm1_{a.task}_pack.tar"
    pk.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(pk, "w") as t:
        t.add(src, arcname=".")
        for fp in sorted(files):
            t.add(fp, arcname=rel(fp))
    sha = hashlib.sha256(open(pk, "rb").read()).hexdigest()
    td = W / "staging/SM1/cpu" / f"SM1_cpu_{a.task}"
    td.mkdir(parents=True, exist_ok=True)
    shutil.copy2(HERE / "wcss_run.sh", td / "run.sh")
    os.chmod(td / "run.sh", 0o755)
    (td / "cpus").write_text(f"{a.cpus}\n")
    (td / "est_minutes").write_text("45\n")
    (td / "task.env").write_text(f"SM1_TASK={a.task}\nSM1_LISTS=\"{' '.join(NAMES[x] for x in TASKS[a.task])}\"\n"
                                 f"SM1_PACK_SHA256={sha}\n")
    info = dict(task=a.task, pack=str(pk), pack_bytes=pk.stat().st_size, pack_sha256=sha, n_files=len(files),
                lists={NAMES[x]: sum(1 for _ in open(src / "lists" / f"{NAMES[x]}.csv")) - 1 for x in TASKS[a.task]},
                lustre_pack=f"{LUS}/packs/SM1/{pk.name}", lustre_task=f"{LUS}/staging/SM1/cpu/{td.name}")
    json.dump(info, open(W / f"pack_{a.task}.json", "w"), indent=1)
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
