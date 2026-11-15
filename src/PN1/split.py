"""Protocol network, first tests (PN1): the fixed person split of the landmark ladder (AR1) and of the alpha-field
probe (AF0) persons. Written and run before any score or statistic of PN1 exists. CPU only, reads only lists.

Rules (prereg.md, section "Persons"):
  V  = validation-reserved persons: smadcvpr/prep_train.is_val(subject) (imported unchanged and checked here).
  T  = test ladder: random.Random(401).sample(sorted 536 frgcferet hosts, 200)  (= the AF0 softened-host list
       ar1soft_src, checked). Test reads use the hosts h in T with h not in V and B(h) not in V.
  D  = development ladder: random.Random(402).sample(sorted({B(t): t in T} - T - V, restricted to hosts whose own
       partner is not in V), 100). Chosen among partners of test hosts so that fewer persons are lost to training.
  X  = T u B(T) u D u B(D) u V  (every person that appears in a test or development ladder image, plus V).
  L  = ladder training hosts: h not in X. Genuine-side rows (R0, R2w OpenCV) for every h in L; the morph R4(h) and
       its two warped halves only if B(h) not in X ("L_morph").
  AF0 persons in V are dropped from every PN1 training and development set (images whose pid_A or pid_B is in V).
Outputs: /home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/split/{ladder_split.csv,
         af0_split.csv, split_summary.json}

  python3 -I split.py
"""
import collections
import csv
import hashlib
import json
import pathlib
import random
import sys

AR1 = pathlib.Path("/home/narolski/smad-next/experiments/AR1")
AF0 = pathlib.Path("/mnt/t7/smad_next/AF0")
OUT = pathlib.Path("/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/split")
MC = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr")


def is_val_local(subject):
    return int(hashlib.sha1(f"smadcvpr:{subject}".encode()).hexdigest(), 16) % 10 == 0


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    sys.path.insert(0, str(MC))
    import prep_train                                    # only its is_val; prep_train is never edited
    V_of = lambda pid: pid.split(":")[0] in ("frgc", "feret") and prep_train.is_val(pid.split(":")[1])  # noqa: E731
    pool = list(csv.DictReader(open(AR1 / "pool.csv")))
    pids = sorted(r["pid"] for r in pool)
    for p in pids:
        assert prep_train.is_val(p.split(":")[1]) == is_val_local(p.split(":")[1])
    B = {r["pid"]: r["B_pid"] for r in pool}
    assert sorted(B.values()) == pids, "partner map is not a permutation of the hosts"
    cand = [r for r in csv.DictReader(open(AF0 / "lists" / "ar1.csv"))
            if r["cell"] == "frgcferet" and r["rung"] in ("R0", "R2w")]
    hosts = sorted({r["p1"] for r in cand})
    assert hosts == pids
    T = set(random.Random(401).sample(hosts, 200))
    assert T == {r["p1"] for r in csv.DictReader(open(AF0 / "lists" / "ar1soft_src.csv"))}, "T != AF0 ar1soft hosts"
    V = {p for p in pids if V_of(p)}
    Dpool = sorted(h for h in ({B[t] for t in T} - T - V) if B[h] not in V)
    D = set(random.Random(402).sample(Dpool, 100))
    X = T | {B[h] for h in T} | D | {B[h] for h in D} | V
    L = sorted(h for h in pids if h not in X)
    Lm = sorted(h for h in L if B[h] not in X)
    T_read = sorted(h for h in T if h not in V and B[h] not in V)
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "ladder_split.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pid", "db", "partner_B", "is_val", "role", "test_read", "train_genuine", "train_morph"])
        for h in pids:
            role = "test" if h in T else "dev" if h in D else "train" if h in L else "excluded"
            w.writerow([h, h.split(":")[0], B[h], int(h in V), role, int(h in T_read), int(h in L), int(h in Lm)])
    # AF0 persons
    man = list(csv.DictReader(open(AF0 / "manifest.csv")))
    af = collections.defaultdict(set)
    for r in man:
        for k in ("pid_A", "pid_B"):
            if r[k]:
                af[r[k]].add(r["split"])
    with open(OUT / "af0_split.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pid", "db", "af0_split", "is_val", "pn1_use"])
        for p in sorted(af):
            sp = "|".join(sorted(af[p]))
            v = V_of(p)
            w.writerow([p, p.split(":")[0], sp, int(v), "none" if v else ("train" if sp == "train" else "dev")])
    ladder_persons = set(pids)
    assert not (ladder_persons & set(af)), "AF0 and ladder persons overlap"
    summ = dict(
        rule="prereg.md section Persons", seeds=dict(test=401, dev=402),
        n_hosts=len(pids), n_V_hosts=len(V), n_T=len(T), n_T_read=len(T_read), n_D=len(D),
        n_partner_pool_for_D=len(Dpool), n_X=len(X), n_L_genuine=len(L), n_L_morph=len(Lm),
        L_db=dict(collections.Counter(h.split(":")[0] for h in L)),
        Lm_db=dict(collections.Counter(h.split(":")[0] for h in Lm)),
        T_db=dict(collections.Counter(h.split(":")[0] for h in T)),
        D_db=dict(collections.Counter(h.split(":")[0] for h in D)),
        V_hosts=sorted(V), V_in_T=sorted(V & T), T_with_V_partner=sorted(h for h in T if B[h] in V),
        af0_persons=len(af), af0_V=sum(1 for p in af if V_of(p)),
        af0_train_persons_kept=sum(1 for p in af if not V_of(p) and af[p] == {"train"}),
        af0_dev_persons_kept=sum(1 for p in af if not V_of(p) and af[p] == {"val"}),
        sha256=dict(pool_csv=sha(AR1 / "pool.csv"), ar1_list=sha(AF0 / "lists" / "ar1.csv"),
                    ar1soft_src=sha(AF0 / "lists" / "ar1soft_src.csv"), af0_manifest=sha(AF0 / "manifest.csv"),
                    ladder_split=sha(OUT / "ladder_split.csv"), af0_split=sha(OUT / "af0_split.csv")))
    json.dump(summ, open(OUT / "split_summary.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in summ.items() if k != "sha256"}, indent=1))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
