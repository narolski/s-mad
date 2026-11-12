"""MS1 step 2 (prereg part 1, sections 3.3-3.4): FFHQ training and hold-out images, unchanged image code only.

plan    : job lists from OUT/ffhq/persons.csv
          - af0-style pairs (training part 450 persons, 400 per field; hold-out 300 persons, 150 per field): the loop of
            src/AF0/pairs.py (five field types in its order, hosts cycle through the shuffled persons, random partner of
            the same part, per-pair seed); only zero and u50 are built.
          - soft list (src/AF0/lists_extra.py soft_src rule): photos, u50, one half per u50 pair (A even, B odd pair
            index), strengths amsl112 / fm61 alternating by row (soften.py --alternate); training: fm61 rows only;
            hold-out: photos and u50 at both strengths.
          - ladder (150 hosts): partner by Hungarian on glintr100 cos(H_p, H_q) without fixed points (src/AR1/pool.py,
            S := H for a one-photo source).
morph   : af0 zero / u50 through src/AF0/af_morph.py _job (unchanged; written to MS1 paths); halves = the engine's own
          warped images, np.clip(W, 0, 255).astype(uint8) (src/AF0/ghost.py); ladder R4 through
          scripts/78_tool_morph.py opencv (unchanged script, subprocess); ladder halves likewise from warped_pair;
          R2w4 through src/AR1/variants.py warp_cv (unchanged; record only).
soft    : soften.e7_branch (prep_eval's registered shrink-and-enlarge branch, imported unchanged, pin checked).
  python3 -I ffhq_build.py plan | morph | soft [--workers 2] [--limit 8]
"""
import argparse
import csv
import json
import pathlib
import random
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ms1common as C  # noqa: E402

O = C.OUT / "ffhq"
FIELDS = ("zero", "u25", "u50", "grad", "bump")
BUILT = ("zero", "u50")
SEED = 20261111 + 401 + 1000
STRENGTHS = ("amsl112", "fm61")
PY = "/home/narolski/mambamorph-code/.venv-spark/bin/python"


def L(name):
    return O / "lists" / f"{name}.csv"


def plan(a):
    persons = list(csv.DictReader(open(O / "persons.csv")))
    rng = random.Random(SEED)
    pairs = []
    for part, per in (("af0", 400), ("holdout", 150)):
        ps = [p for p in persons if p["part"] == part]
        if part == "holdout":
            hosts_only = ps[:150]          # prereg 3.4: hosts = the first 150 hold-out persons
        frame = {p["pid"]: p["frame"] for p in ps}
        pids = sorted(frame)
        for field in FIELDS:
            order = pids[:] if part == "af0" else sorted(p["pid"] for p in hosts_only)
            rng.shuffle(order)
            combos, k = set(), 0
            while k < per:
                host = order[k % len(order)]
                partner = rng.choice([p for p in pids if p != host])
                key = (host, partner)
                if key in combos and len(combos) < len(pids) * (len(pids) - 1):
                    continue
                combos.add(key)
                seed = rng.randrange(2 ** 31)
                split = "train" if part == "af0" else "hold"
                iid = f"{split}_ffhq_{field}_{k:04d}"
                if field in BUILT:
                    pairs.append(dict(id=iid, kind="morph", split=split, db="ffhq", field=field, seed=seed,
                                      pid_A=host, pid_B=partner, A=frame[host], B=frame[partner],
                                      image=str(O / "img" / split / field / f"{iid}.png"),
                                      map=str(O / "maps" / split / field / f"{iid}.npy"), wave=1))
                k += 1
    C.write_csv(L("af0_pairs"), pairs)
    # halves of every u50 pair
    halves = []
    for r in pairs:
        if r["field"] != "u50":
            continue
        for tag in ("halfA", "halfB"):
            halves.append(dict(id=f"{r['id']}_{tag}", pair=r["id"], split=r["split"], tag=tag,
                               pid=r["pid_A"] if tag == "halfA" else r["pid_B"],
                               path=str(O / "img" / r["split"] / tag / f"{r['id']}_{tag}.png")))
    C.write_csv(L("halves"), halves)
    # soft lists
    soft = []
    for split, part in (("train", "af0"), ("hold", "holdout")):
        src = [dict(id=f"{split}_ffhq_photo_{i:04d}", kind="photo", pid=p["pid"], path=p["frame"])
               for i, p in enumerate([p for p in persons if p["part"] == part])]
        src += [dict(id=r["id"], kind="u50", pid=f"{r['pid_A']}|{r['pid_B']}", path=r["image"])
                for r in pairs if r["split"] == split and r["field"] == "u50"]
        if split == "train":
            for h in halves:
                if h["split"] != split:
                    continue
                k = int(h["pair"].split("_")[3])
                if (h["tag"] == "halfA") == (k % 2 == 0):
                    src.append(dict(id=h["id"], kind="half", pid=h["pid"], path=h["path"]))
        for k, s in enumerate(src):
            sts = [STRENGTHS[k % 2]] if split == "train" else list(STRENGTHS)
            for st in sts:
                build = split == "hold" or st == "fm61"
                soft.append(dict(src_id=s["id"], kind=s["kind"], split=split, pid=s["pid"], strength=st,
                                 build=int(build), src=s["path"],
                                 out=str(O / "img" / "soft" / st / f"{s['id']}_{st}.png")))
    C.write_csv(L("soft"), soft)
    # ladder
    lad = [p for p in persons if p["part"] == "ladder"]
    z = np.load(O / "emb_kept.npz")
    E = {k: e for k, e in zip(z["key"], z["emb"])}
    M = np.stack([E[p["key"]] for p in lad])
    cos = M @ M.T
    cost = -cos.copy()
    np.fill_diagonal(cost, 1e6)
    from scipy.optimize import linear_sum_assignment
    r_, c_ = linear_sum_assignment(cost)
    rows = []
    for i, j in zip(r_, c_):
        h, b = lad[i], lad[j]
        assert i != j
        s = h["pid"].replace(":", "_")
        rows.append(dict(pid=h["pid"], H=h["frame"], B_pid=b["pid"], B=b["frame"], cos_HB=round(float(cos[i, j]), 4),
                         R4=str(O / "img/ladder/opencv/R4" / f"{s}.png"),
                         hA=str(O / "img/ladder/opencv/half" / f"{s}_hA.png"),
                         hB=str(O / "img/ladder/opencv/half" / f"{s}_hB.png"),
                         R2w4=str(O / "img/ladder/opencv/R2w4" / f"{s}.png")))
    C.write_csv(L("ladder"), rows)
    summ = dict(af0_pairs={f"{s}/{f}": sum(1 for r in pairs if r["split"] == s and r["field"] == f)
                           for s in ("train", "hold") for f in BUILT},
                halves=len(halves), soft_rows=len(soft), soft_built=sum(int(r["build"]) for r in soft),
                ladder=len(rows), ladder_cos_median=float(np.median([r["cos_HB"] for r in rows])))
    json.dump(summ, open(O / "plan_summary.json", "w"), indent=1)
    print(json.dumps(summ))


# ---------------------------------------------------------------- morph stage
_AM = None


def am():
    global _AM
    if _AM is None:
        _AM = C.load(C.SRC / "AF0/af_morph.py", "af_morph")
    return _AM


def job_pair(r):
    import cv2
    cv2.setNumThreads(1)
    AM = am()
    st, info = AM._job(r)[1:]
    out = [r["id"], st]
    if r["field"] == "u50":
        hp = [pathlib.Path(r["image"]).parent.parent / t / f"{r['id']}_{t}.png" for t in ("halfA", "halfB")]
        if not all(p.exists() for p in hp):
            a, b = cv2.imread(r["A"]), cv2.imread(r["B"])
            la, lb = AM.parse_tem(r["A"][:-4] + ".tem"), AM.parse_tem(r["B"][:-4] + ".tem")
            wA, wB, _, _ = AM.warped_pair(a, la, b, lb)
            for p, w in zip(hp, (wA, wB)):
                p.parent.mkdir(parents=True, exist_ok=True)
                assert cv2.imwrite(str(p), np.clip(w, 0, 255).astype(np.uint8))   # ghost.py's halves line
    return out


def job_ladder(r):
    import cv2
    cv2.setNumThreads(1)
    AM = am()
    V = C.load(C.SRC / "AR1/variants.py", "ar1variants")
    a, b = cv2.imread(r["H"]), cv2.imread(r["B"])
    la, lb = AM.parse_tem(r["H"][:-4] + ".tem"), AM.parse_tem(r["B"][:-4] + ".tem")
    if not (pathlib.Path(r["hA"]).exists() and pathlib.Path(r["hB"]).exists()):
        wA, wB, _, _ = AM.warped_pair(a, la, b, lb)
        for p, w in ((r["hA"], wA), (r["hB"], wB)):
            pathlib.Path(p).parent.mkdir(parents=True, exist_ok=True)
            assert cv2.imwrite(p, np.clip(w, 0, 255).astype(np.uint8))
    if not pathlib.Path(r["R2w4"]).exists():
        pathlib.Path(r["R2w4"]).parent.mkdir(parents=True, exist_ok=True)
        assert cv2.imwrite(r["R2w4"], V.warp_cv(a, la, lb, AM.hm))
    return r["pid"]


def morph(a):
    from multiprocessing import Pool
    pairs = list(csv.DictReader(open(L("af0_pairs"))))[: a.limit or None]
    lad = list(csv.DictReader(open(L("ladder"))))[: a.limit or None]
    t0 = time.time()
    # R4 through the unchanged script (one subprocess per worker chunk)
    todo = [r for r in lad if not pathlib.Path(r["R4"]).exists()]
    if todo:
        pathlib.Path(lad[0]["R4"]).parent.mkdir(parents=True, exist_ok=True)
        work = O / "_work"
        work.mkdir(parents=True, exist_ok=True)
        procs = []
        for i in range(a.workers):
            ch = work / f"r4_chunk{i}.tsv"
            ch.write_text("".join("\t".join([r["H"], r["H"][:-4] + ".tem", r["B"], r["B"][:-4] + ".tem", r["R4"]]) + "\n"
                                  for r in todo[i::a.workers]))
            procs.append(subprocess.Popen([PY, str(C.MC / "scripts/78_tool_morph.py"), str(ch), "opencv"],
                                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True))
        outs = [p.communicate()[0] for p in procs]
        print("78_tool_morph:", " | ".join(o.strip().splitlines()[-1] for o in outs), flush=True)
    with Pool(a.workers) as p:
        res = list(p.imap_unordered(job_pair, pairs, chunksize=4))
        print(f"af0 pairs {len(res)} {time.time() - t0:.0f}s", flush=True)
        lr = list(p.imap_unordered(job_ladder, lad, chunksize=2))
    log = dict(pairs=len(res), made=sum(1 for x in res if x[1] == "made"), ladder=len(lr),
               r4_present=sum(pathlib.Path(r["R4"]).exists() for r in lad), seconds=round(time.time() - t0))
    json.dump(log, open(O / f"morph_log{'_limit' if a.limit else ''}.json", "w"), indent=1)
    print(json.dumps(log), flush=True)


# ---------------------------------------------------------------- soft stage
_SO = None


def job_soft(r):
    import cv2
    global _SO
    cv2.setNumThreads(1)
    if _SO is None:
        S = C.load(C.SRC / "AF0/soften.py", "af0soften")
        _SO = (S, S.load_pe())
    S, P = _SO
    out = pathlib.Path(r["out"])
    if out.exists():
        return dict(r, aligned="exists", native_ied="", scale="")
    img, flag, nied, sc = S.e7_branch(P, cv2.imread(r["src"]), S.STRENGTHS[r["strength"]])
    if img is None:
        return dict(r, aligned="False", native_ied=nied, scale=sc)
    out.parent.mkdir(parents=True, exist_ok=True)
    assert cv2.imwrite(str(out), img)
    return dict(r, aligned=str(flag), native_ied=nied, scale=sc)


def soft(a):
    from multiprocessing import Pool
    rows = [r for r in csv.DictReader(open(L("soft"))) if r["build"] == "1"][: a.limit or None]
    t0 = time.time()
    with Pool(a.workers) as p:
        res = list(p.imap(job_soft, rows, chunksize=4))
    C.write_csv(O / f"soft_log{'_limit' if a.limit else ''}.csv", res)
    print(json.dumps(dict(rows=len(res), failed=sum(1 for x in res if x["aligned"] == "False"),
                          seconds=round(time.time() - t0))), flush=True)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("plan", "morph", "soft"))
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    {"plan": plan, "morph": morph, "soft": soft}[a.cmd](a)
