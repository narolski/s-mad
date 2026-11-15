"""SM1 pair lists and .tem files (no image is made here).

  python3 -I pairs.py tems       -> OUT/tem/{bf,src}/<name>.tem from the existing arrays (pixel = normalised x 256)
  python3 -I pairs.py lists      -> OUT/lists/*.csv + RES/pairs_summary.json
Lists (columns id, a, ta, b, tb, out, halves, + metadata):
  audit.csv    Part 2: 500 keys (unused non-contributor renders) x 5 trained partners (KP) and x 5 matched unused
               partners (KU); first 100 keys x 20 placebo partners (KX, amendment A1.1); P_i x P_j (PP), U_i x U_j (UU);
               the renders themselves in audit_renders.csv
  armb.csv     the release pairs (os25k_m_t contributors) with landmarks on both sides, re-made by our engine
  arma.csv     the release morph files of the same pairs (no build); arma256.csv: only its 256 x 256 files (A1.8)
  armbp.csv    (b'), A1.3: the same first-contributor slots, second contributor = a random unused os25k_m_t render
               (not key / U / placebo), each replacement at most twice
  armc.csv     balanced look-alike pairs on os25k_bf_t, every render a partner at most twice, with halves
  armcr.csv    (c'): balanced random pairs on os25k_bf_t, with halves
  ar1h.csv     halves of the 536 AR1 FRGC/colorFERET (H, B) pairs (checked against AR1's OpenCV R4 files)
  smoke_*.csv  the smoke-pass subsets (first 500 rows of each arm's seeded order; Part 2: first 50 keys)
"""
import csv
import json
import pathlib
import struct
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402

LMS = tuple(K.OUT / f"lm/srcm_if106_{st}.npz" for st in ("pool", "contrib", "evalp"))   # A2: no extra stage
TEM = K.OUT / "tem"
LISTS = K.OUT / "lists"
IMG = K.OUT / "img"
N_KEYS, N_PLACEBO, N_PKEYS, N_SMOKE, N_SMOKE_KEYS = 500, 20, 100, 500, 50
EYE_A, EYE_B, NOSE = list(range(33, 43)), list(range(87, 97)), 86     # 106-point layout (mirror_perm106 groups)


def srcm():
    lms, emb, split = {}, {}, {}
    for f in LMS:
        if not f.exists():
            continue
        z = np.load(f, allow_pickle=False)
        names, sp, L, Em = [str(n) for n in z["names"]], [str(s) for s in z["split"]], z["lms"], z["emb"]
        for i, n in enumerate(names):
            if sp[i] != "bfcheck":
                lms[n], emb[n], split[n] = L[i], Em[i], sp[i]
    return lms, emb, split


def valid(lm):
    """Finite and every point inside the 256-px frame (amendment A5: the unchanged engine fails on out-of-frame points,
    and 78_tool_morph.py then skips the pair; excluded up front so that no pair fails and the arm counts stay equal)."""
    if lm is None or not np.isfinite(lm).all():
        return False
    p = lm * 256
    return bool((p >= 0).all() and (p <= 255).all())


def geom(lm):
    p = lm * 256
    ea, eb = p[EYE_A].mean(0), p[EYE_B].mean(0)
    iod = float(np.hypot(*(eb - ea)))
    return iod, float((p[NOSE, 0] - (ea[0] + eb[0]) / 2) / iod)


def png_size(p):
    with open(p, "rb") as f:
        h = f.read(24)
    return struct.unpack(">II", h[16:24])


def tems():
    bf = K.load_if106()
    lms, _, split = srcm()
    n = {}
    src = {k: v for k, v in lms.items() if split[k] != "evalp"}
    srce = {k: v for k, v in lms.items() if split[k] == "evalp"}
    for sub, d in (("bf", bf), ("src", src), ("srce", srce)):
        (TEM / sub).mkdir(parents=True, exist_ok=True)
        n[sub] = 0
        for name, lm in d.items():
            if valid(lm):
                f = TEM / sub / f"{name}.tem"
                if not f.exists():
                    K.write_tem(f, lm * np.float32(256))
                n[sub] += 1
    print("tem files", n)


def row(i, a, b, sub_a, sub_b, out, halves=0, **kw):
    dirs = {"src": K.SRC_T, "bf": K.BF_T, "srce": K.SRC_E}
    da, db = dirs[sub_a], dirs[sub_b]
    r = dict(id=i, a=str(da / f"{a}.png"), ta=str(TEM / sub_a / f"{a}.tem"), b=str(db / f"{b}.png"),
             tb=str(TEM / sub_b / f"{b}.tem"), out=str(out), halves=halves, na=a, nb=b)
    r.update(kw)
    return r


def write(name, rows):
    LISTS.mkdir(parents=True, exist_ok=True)
    with open(LISTS / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(name, len(rows))


def balanced(names, valid_set, nn, n_pairs, rng, lookalike=True):
    """Round-robin over a seeded order: each render takes the best-ranked look-alike (or a random render) still
    below the cap of 2 appearances, no unordered pair twice; a render with no admissible partner is skipped (it stays
    genuine-only); stops at n_pairs."""
    pos = {n: i for i, n in enumerate(names)}
    order = [names[i] for i in rng.permutation(len(names)) if names[i] in valid_set]
    cnt = dict.fromkeys(names, 0)
    used, out, skipped = set(), [], 0
    vlist = sorted(valid_set)
    for a in order:
        if len(out) >= n_pairs:
            break
        if cnt[a] >= 2:
            continue
        if lookalike:
            cands = [(r, names[j]) for r, j in enumerate(nn[pos[a]]) if j >= 0]
        else:
            cands = [(-1, vlist[j]) for j in rng.choice(len(vlist), size=64, replace=False)]
        for r, b in cands:
            if b != a and b in valid_set and cnt[b] < 2 and frozenset((a, b)) not in used:
                out.append((a, b, r))
                used.add(frozenset((a, b)))
                cnt[a] += 1
                cnt[b] += 1
                break
        else:
            skipped += 1
    assert len(out) == n_pairs, (len(out), n_pairs)
    assert max(cnt.values()) <= 2
    return out, cnt, skipped


def lists_c15k():
    """(c) and (c') with 15,000 pairs (upper bound of N), for the WCSS build before the contributor landmarks exist;
    balanced() is a prefix process, so the N-pair lists are the first N rows (asserted in lists())."""
    bf = K.load_if106()
    zl = np.load(K.LOOK, allow_pickle=False)
    names = [str(n)[:-4] for n in zl["names"]]
    nn_tab = zl["nn"]
    vset = {n for n in names if valid(bf.get(n))}
    for tag, look in (("armc", True), ("armcr", False)):
        pr, cnt, skipped = balanced(names, vset, nn_tab, 15000, np.random.default_rng(K.SEED + (0 if look else 1)), look)
        write(f"{tag}_15k.csv", [row(f"{tag.upper()}_{a}_{b}", a, b, "bf", "bf", IMG / tag / f"{a}_{b}.png",
                                     halves=int(look), rank=r) for a, b, r in pr])
        print(tag, "skipped", skipped, "use counts", np.bincount(np.array(list(cnt.values())), minlength=3).tolist())
        big = list(csv.DictReader(open(LISTS / f"{tag}_15k.csv")))
        write(f"smoke_{tag}.csv", big[:N_SMOKE])


def lists(part="all"):
    lms, emb, split = srcm()
    pool = sorted(n for n, s in split.items() if s == "pool")
    extra = sorted(n for n, s in split.items() if s == "extra")
    rel = K.release_pairs()
    contrib = {x for p in rel for x in p}
    assert not contrib & set(pool) and not contrib & set(extra) and not set(pool) & set(extra)
    bf = K.load_if106()
    assert not set(bf) & set(pool) and not set(bf) & contrib and not set(bf) & set(extra)
    summ = {}
    # ---- Part 2 audit
    rng = np.random.default_rng(K.SEED)
    vpool = [n for n in pool if valid(lms[n])]
    perm = [vpool[i] for i in rng.permutation(len(vpool))]
    keys, cand = perm[:N_KEYS], perm[N_KEYS:]
    E = np.stack([emb[k] for k in keys])
    P = list(K.PARTNERS)
    assert all(valid(lms[p]) for p in P)

    def stats(n):
        c = E @ emb[n]
        iod, yaw = geom(lms[n])
        return np.array([c.mean(), c.std(), iod, yaw])
    cst = {c: stats(c) for c in cand}
    sd = np.stack(list(cst.values())).std(0)
    U, match = [], []
    for p in P:
        sp = stats(p)
        c = min((c for c in cand if c not in U), key=lambda c: float((np.abs(cst[c] - sp) / sd).sum()))
        U.append(c)
        match.append(dict(P=p, U=c, P_stats=np.round(sp, 4).tolist(), U_stats=np.round(cst[c], 4).tolist(),
                          stats=["mean_cos_keys", "sd_cos_keys", "iod_px", "yaw_proxy"]))
    rest = [c for c in cand if c not in U]
    X = [rest[i] for i in np.random.default_rng(K.SEED + 3).choice(len(rest), size=N_PLACEBO, replace=False)]
    rows, d = [], IMG / "audit"
    for ki, k in enumerate(keys):
        for j, (p, u) in enumerate(zip(P, U)):
            rows.append(row(f"KP_{k}_{p}", k, p, "src", "src", d / f"KP_{k}_{p}.png", kind="KP", key=k, partner=p,
                            slot=j, key_rank=ki, cos=round(float(emb[k] @ emb[p]), 4)))
            rows.append(row(f"KU_{k}_{u}", k, u, "src", "src", d / f"KU_{k}_{u}.png", kind="KU", key=k, partner=u,
                            slot=j, key_rank=ki, cos=round(float(emb[k] @ emb[u]), 4)))
        for j, e in enumerate(K.EVAL_PARTNERS):                        # A3: evaluation-split partners (bridge)
            rows.append(row(f"KE_{k}_{e}", k, e, "src", "srce", d / f"KE_{k}_{e}.png", kind="KE", key=k, partner=e,
                            slot=j, key_rank=ki, cos=round(float(emb[k] @ emb[e]), 4)))
        if ki < N_PKEYS:
            for j, x in enumerate(X):
                rows.append(row(f"KX_{k}_{x}", k, x, "src", "src", d / f"KX_{k}_{x}.png", kind="KX", key=k, partner=x,
                                slot=j, key_rank=ki, cos=round(float(emb[k] @ emb[x]), 4)))
    for grp, kind in ((P, "PP"), (U, "UU")):
        for i in range(5):
            for j in range(i + 1, 5):
                rows.append(row(f"{kind}_{grp[i]}_{grp[j]}", grp[i], grp[j], "src", "src",
                                d / f"{kind}_{grp[i]}_{grp[j]}.png", kind=kind, key="", partner=f"{grp[i]}|{grp[j]}",
                                slot=f"{i}{j}", key_rank=-1, cos=round(float(emb[grp[i]] @ emb[grp[j]]), 4)))
    write("audit.csv", rows)
    write("smoke_audit.csv", [r for r in rows if r["kind"] in ("KP", "KU", "KE") and r["key_rank"] < N_SMOKE_KEYS])
    rr = [dict(id=f"R_{n}", path=str(K.SRC_T / f"{n}.png"), kind=kind, name=n)
          for kind, ns in (("Rkey", keys), ("RP", P), ("RU", U), ("RX", X)) for n in ns]
    rr += [dict(id=f"R_{n}", path=str(K.SRC_E / f"{n}.png"), kind="RE", name=n) for n in K.EVAL_PARTNERS]
    write("audit_renders.csv", rr)
    summ["audit"] = dict(n_keys=len(keys), n_candidates=len(cand), match=match, placebo=X,
                         cos_KP_mean=float(np.mean([r["cos"] for r in rows if r["kind"] == "KP"])),
                         cos_KU_mean=float(np.mean([r["cos"] for r in rows if r["kind"] == "KU"])),
                         cos_KX_mean=float(np.mean([r["cos"] for r in rows if r["kind"] == "KX"])),
                         pool_no_face=len(pool) - len(vpool))
    audit_set = set(keys) | set(U) | set(X)
    if part == "audit":
        json.dump(summ, open(K.RES / "pairs_summary_audit.json", "w"), indent=1)
        print(json.dumps(summ, indent=1))
        return
    # ---- arm b / a: release pairs with landmarks on both sides
    ok = [(a, b) for a, b in rel if valid(lms.get(a)) and valid(lms.get(b))]
    N = len(ok)
    order = np.random.default_rng(K.SEED + 11).permutation(N)          # smoke subsets: first N_SMOKE of this order
    rb = [row(f"B_{a}_{b}", a, b, "src", "src", IMG / "armb" / f"morphed_{a}_{b}.png") for a, b in ok]
    write("armb.csv", rb)
    ra = [dict(id=f"A_{a}_{b}", path=str(K.M_T / f"morphed_{a}_{b}.png"), na=a, nb=b,
               size="x".join(map(str, png_size(K.M_T / f"morphed_{a}_{b}.png")))) for a, b in ok]
    write("arma.csv", ra)
    write("arma256.csv", [r for r in ra if r["size"] == "256x256"])
    summ["release"] = dict(n_release=len(rel), n_with_landmarks=N,
                           dropped=[f"{a}_{b}" for a, b in sorted(set(rel) - set(ok))][:20],
                           arma256=sum(r["size"] == "256x256" for r in ra))
    # ---- arm b': release first-contributor slots, random unused second contributors (cap 2)
    repl_pool = [n for n in sorted(set(extra) | set(cand)) if valid(lms.get(n)) and n not in audit_set]
    need = N
    cap = int(np.ceil(need / len(repl_pool)))                           # amendment A2: cap = ceil(N / pool)
    r2 = np.random.default_rng(K.SEED + 5)
    reps = list(np.array(repl_pool)[r2.permutation(len(repl_pool))])
    slots = (reps * cap)[:need]                                         # each replacement at most cap times
    slots = [slots[i] for i in r2.permutation(len(slots))]
    rbp, seen = [], set()
    for i, (a, _) in enumerate(ok):
        if (a, slots[i]) in seen:                                       # same key twice with one partner: swap on
            j = next(j for j in range(i + 1, len(slots)) if (a, slots[j]) not in seen)
            slots[i], slots[j] = slots[j], slots[i]
        x = slots[i]
        seen.add((a, x))
        rbp.append(row(f"BP_{a}_{x}", a, x, "src", "src", IMG / "armbp" / f"{a}_{x}.png"))
    assert max(np.unique(slots, return_counts=True)[1]) <= cap
    write("armbp.csv", rbp)
    for Kd in (50, 500):                                                # A3: partner-count dose curve
        r3 = np.random.default_rng(K.SEED + 30 + Kd)
        parts = [repl_pool[i] for i in r3.choice(len(repl_pool), size=Kd, replace=False)]
        sl = [parts[i % Kd] for i in r3.permutation(need)]             # each partner N / K times
        rd_, seen2 = [], set()
        for i, (a, _) in enumerate(ok):
            if (a, sl[i]) in seen2:
                j = next(j for j in range(i + 1, len(sl)) if (a, sl[j]) not in seen2 and (ok[j][0], sl[i]) not in seen2)
                sl[i], sl[j] = sl[j], sl[i]
            seen2.add((a, sl[i]))
            rd_.append(row(f"D{Kd}_{a}_{sl[i]}", a, sl[i], "src", "src", IMG / f"armd{Kd}" / f"{a}_{sl[i]}.png"))
        write(f"armd{Kd}.csv", rd_)
        summ[f"armd{Kd}"] = dict(n=len(rd_), partners=Kd, uses_max=int(max(np.unique(sl, return_counts=True)[1])))
    summ["armbp"] = dict(n=len(rbp), n_replacements=len(set(slots)), repl_pool=len(repl_pool), cap=cap)
    # ---- arm c / c': balanced pairs on os25k_bf_t
    zl = np.load(K.LOOK, allow_pickle=False)
    names = [str(n)[:-4] for n in zl["names"]]
    nn_tab = zl["nn"]
    vset = {n for n in names if valid(bf.get(n))}
    lists_c = {}
    for tag, look in (("armc", True), ("armcr", False)):
        pr, cnt, skipped = balanced(names, vset, nn_tab, N, np.random.default_rng(K.SEED + (0 if look else 1)), look)
        rc = [row(f"{tag.upper()}_{a}_{b}", a, b, "bf", "bf", IMG / tag / f"{a}_{b}.png", halves=int(look), rank=r)
              for a, b, r in pr]
        if (LISTS / f"{tag}_15k.csv").exists():                      # built early for WCSS: N-list must be its prefix
            big = list(csv.DictReader(open(LISTS / f"{tag}_15k.csv")))
            assert [r["id"] for r in big[:len(rc)]] == [r["id"] for r in rc], tag
        write(f"{tag}.csv", rc)
        lists_c[tag] = rc
        ranks = np.array([r for _, _, r in pr])
        cs = np.bincount(np.array(list(cnt.values())), minlength=3)
        summ[tag] = dict(n=len(pr), renders_used_0_1_2=cs.tolist(), skipped_no_partner=skipped,
                         lookalike_rank_median=float(np.median(ranks)) if look else None,
                         lookalike_rank_max=int(ranks.max()) if look else None)
    # ---- smoke subsets (same seeded order for every arm)
    sm = sorted(order[:N_SMOKE].tolist())
    write("smoke_armb.csv", [rb[i] for i in sm])
    write("smoke_arma.csv", [ra[i] for i in sm])
    write("smoke_armbp.csv", [rbp[i] for i in sm])
    for tag in ("armc", "armcr"):                                       # prefix of the list (built before N existed)
        write(f"smoke_{tag}.csv", lists_c[tag][:N_SMOKE])
    # ---- AR1 halves (FRGC / colorFERET H x B)
    ar = list(csv.DictReader(open("/mnt/t7/smad_next/AR1/pool.csv")))
    rh = []
    for r in ar:
        st = r["pid"].replace(":", "_")
        rh.append(dict(id=f"AH_{st}", a=r["H"], ta=r["H"][:-4] + ".tem", b=r["B"], tb=r["B"][:-4] + ".tem",
                       out=str(IMG / "ar1h" / f"{st}.png"), halves=1, na=r["pid"], nb=r["B_pid"],
                       ref=f"/mnt/t7/smad_next/AR1/img/frgcferet/opencv/R4/{st}.png"))
    write("ar1h.csv", rh)
    summ["ar1h"] = dict(n=len(rh))
    json.dump(summ, open(K.RES / "pairs_summary.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    if sys.argv[1] == "tems":
        tems()
    elif sys.argv[1] == "c15k":
        lists_c15k()
    else:
        lists(sys.argv[2] if len(sys.argv) > 2 else "all")
