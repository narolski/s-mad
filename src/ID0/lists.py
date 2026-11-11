"""ID0 lists: the genuine-only fit set and the evaluation items. No image is made or written.

fit.csv  : key, pid, db, subject, session, neutral, path, tem   (FRGC + colorFERET candidates of AR1's pool.py, minus AR1
           hosts/partners, minus is_val persons; within-person pixel duplicates dropped by AR1's rule pool.fp / SAME_MAD)
items.csv: key, group, path, p1, p2, w2, expr, src1, src2, extra
           group = the evaluation set; p1/p2 = persons (bootstrap units); w2 = weight of the second contributor;
           src1/src2 = item keys of the contributors' source images (fidelity / similarity); expr = 'nn' etc. if known.
  python3 -I lists.py
"""
import collections
import csv
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import id0_common as C  # noqa: E402


def fit_set():
    P = C.ar1_pool_module()
    cand = P.candidates()
    ar1 = C.rows(C.AR1_POOL)
    used = {r["pid"] for r in ar1} | {r["B_pid"] for r in ar1}
    by = collections.defaultdict(list)
    seen = set()
    nval = set()
    for c in sorted(cand, key=lambda c: c["path"]):
        if c["path"] in seen:
            continue
        seen.add(c["path"])
        pid = f"{c['db']}:{c['subject']}"
        if pid in used:
            continue
        if C.is_val(c["subject"]):
            nval.add(pid)
            continue
        assert not C.forbidden(c["path"])
        by[pid].append(c)
    ndup = 0
    out = []
    for pid in sorted(by):
        kept = []
        for c in by[pid]:
            f = P.fp(c["path"])
            if any(np.abs(f - g).mean() < P.SAME_MAD for _, g in kept):
                ndup += 1
                continue
            kept.append((c, f))
        for c, _ in kept:
            p = P.K.DATA / c["path"]
            out.append(dict(key=f"fit|{pid}|{p.stem}", pid=pid, db=c["db"], subject=c["subject"], session=c["session"],
                            neutral=c["neutral"], path=str(p), tem=str(p.with_suffix(".tem"))))
    n = collections.Counter(r["pid"] for r in out)
    ses = collections.defaultdict(set)
    for r in out:
        ses[r["pid"]].add(r["session"])
    summ = dict(persons=len(n), by_db=dict(collections.Counter(p.split(":")[0] for p in n)), photos=len(out),
                pixel_duplicates_dropped=ndup, is_val_persons_excluded=len(nval),
                persons_ge2_photos=sum(v >= 2 for v in n.values()),
                persons_ge2_sessions=sum(len(v) >= 2 for v in ses.values()),
                within_dof=sum(v - 1 for v in n.values()), ar1_persons_excluded=len(used))
    return out, summ


def items():
    it = []

    def add(key, group, path, p1, p2=None, w2=0.0, expr="", src1="", src2="", extra=""):
        assert not C.forbidden(path), path
        it.append(dict(key=key, group=group, path=str(path), p1=p1, p2=p2 or p1, w2=w2, expr=expr, src1=src1,
                       src2=src2, extra=extra))

    # AR1 sources, mirrors, rungs (both pools), graded
    pools = {"frgcferet": C.rows(C.AR1_OUT / "pool_m.csv"), "frll": C.rows(C.AR1_OUT / "pool_frll_m.csv")}
    part = {}
    for pool, rs in pools.items():
        for r in rs:
            part[(pool, r["pid"])] = r["B_pid"]
            add(f"ar1src|{pool}|{r['pid']}|H", f"ar1src_{pool}_H", r["H"], r["pid"])
            add(f"ar1src|{pool}|{r['pid']}|S", f"ar1src_{pool}_S", r["S"], r["pid"])
            if r.get("R"):
                add(f"ar1src|{pool}|{r['pid']}|R", f"ar1src_{pool}_R", r["R"], r["pid"])
            if r.get("M"):
                add(f"ar1src|{pool}|{r['pid']}|M", f"ar1src_{pool}_M", r["M"], r["pid"])
    srcmap = {"R2": ("H", "H"), "R2w": ("H", "S"), "R3": ("H", "S"), "R3m": ("H", "M"), "NC": ("S", "H")}
    for r in C.rows(C.AR1_OUT / "manifest.csv"):
        pool, tool, rung = r["pool"], r["tool"], r["rung"]
        if pool in ("frgcferet", "frll") and rung in ("R2", "R2w", "R3", "R3m", "R4", "NC"):
            h = r["p1"]
            b = part[(pool, h)]
            if rung == "R4":
                assert r["p2"] == b, (r, b)
                add(f"ar1|{pool}|{tool}|R4|{h}", f"ar1_{pool}_{tool}_R4", r["path"], h, b, 0.5,
                    src1=f"ar1src|{pool}|{h}|H", src2=f"ar1src|{pool}|{b}|S")
            else:
                s1, s2 = srcmap[rung]
                add(f"ar1|{pool}|{tool}|{rung}|{h}", f"ar1_{pool}_{tool}_{rung}", r["path"], h, h,
                    0.0 if rung == "R2" else 0.5, src1=f"ar1src|{pool}|{h}|{s1}", src2=f"ar1src|{pool}|{h}|{s2}")
        elif pool == "frgcferet" and rung == "G":
            h = r["p1"]
            b = part[(pool, h)]
            m = float(r["level"])
            add(f"ar1g|m{int(round(m * 100)):03d}|{h}", f"ar1g_m{int(round(m * 100)):03d}", r["path"], h, b, m,
                src1=f"ar1src|{pool}|{h}|H", src2=f"ar1src|{pool}|{b}|S")
        elif pool == "frll_bench" and rung in ("R4f",):
            a, b = r["p1"], r["p2"]
            st = pathlib.Path(r["path"]).stem
            add(f"bench|{tool}|R4f|{st}", f"bench_{tool}_R4f", r["path"], a, b, 0.5, expr="nn",
                src1=f"frllsrc|{a.split(':')[1]}_03", src2=f"frllsrc|{b.split(':')[1]}_03")
    for p in sorted((C.AR1_OUT / "frll_src").glob("*.png")):
        add(f"frllsrc|{p.stem}", "frllsrc", p, f"frll:{p.stem[:3]}", expr=p.stem[4:])
    # FRLL native vs E7 (eval.csv frames)
    for r in C.rows(C.EVAL_CSV):
        st, fam, lab, var = r["set"], r["family"], r["label"], r["variant"]
        if lab != "0":
            continue
        photo = pathlib.Path(r["path"]).stem.split("_")
        pk = f"{photo[0]}_{photo[1]}"
        if (st, fam, var) == ("frllm", "frll_bona", "orig"):
            add(f"e7|native|{pk}", "e7_native", C.MC / "smadcvpr_data" / r["path"], f"frll:{photo[0]}", expr=photo[1])
        elif var == "resmatch" and (st, fam) in C.E7_PRIMARY + C.E7_DESC:
            add(f"e7|{fam}|{pk}", f"e7_{fam}", C.MC / "smadcvpr_data" / r["path"], f"frll:{photo[0]}", expr=photo[1])
    # A43 stored (identical storage for all groups)
    for arm in ("A", "B", "B20", "C", "C20", "D", "D20", "E"):
        for p in sorted((C.A43 / "data/a43/stored" / arm).glob("*.png")):
            add(*a43_item(f"a43|{arm}|{p.stem}", f"a43_{arm}", p, "e"))
    # DiffAE-native 256 frames (DiffAE arm): a256 photos and generated png256
    for p in sorted((C.A41X3 / "a256" / "png256").glob("*.png")):
        add(f"dae|a256|{p.stem}", "dae_a256", p, f"frll:{p.stem[:3]}", expr=p.stem[4:])
    for arm in ("B", "B20", "C20", "D20"):
        for p in sorted((C.A43 / "gen" / arm / "png256").glob("*.png")):
            add(*a43_item(f"dae|{arm}|{p.stem}", f"dae_{arm}", p, "d"))
    # StyleGAN3
    for r in C.rows(C.H3_MAN):
        if r["variant"] != "orig":
            continue
        g = r["family"]
        add(f"sg3|{g}|{r['id']}", f"sg3_{g}", C.H3_DATA / r["path"], f"h3:{int(r['pair']):04d}",
            w2=0.5 if g == "h3_sg3" else 0.0, extra=f"{r['contrib_a']};{r['contrib_b']}")
    for r in C.rows(C.A37_MAN):
        if r["variant"] != "orig":
            continue
        add(f"sg3|a37spread|{r['id']}", "sg3_a37spread", C.A37_DATA / r["path"], f"h3:{int(r['pair']):04d}",
            extra=f"{r['contrib_a']};")
    return it


def a43_item(key, group, p, kind):
    """A43 names: morph_001_03_and_032_03 / 001_self / 001_03 -> (key, group, path, p1, p2, w2, expr, src1, src2)."""
    s = p.stem
    src = "a43|E|" if kind == "e" else "dae|a256|"
    if s.startswith("morph_"):
        t = s.split("_")
        a, ea, b, eb = t[1], t[2], t[4], t[5]
        return (key, group, p, f"frll:{a}", f"frll:{b}", 0.5, ea + eb, src + f"{a}_{ea}", src + f"{b}_{eb}")
    if s.endswith("_self"):
        a = s.split("_")[0]
        return (key, group, p, f"frll:{a}", f"frll:{a}", 0.5, "03+08", src + f"{a}_03", src + f"{a}_08")
    a, e = s.split("_")
    return (key, group, p, f"frll:{a}", f"frll:{a}", 0.0, e, src + s, src + s)


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    C.OUT.mkdir(parents=True, exist_ok=True)
    fit, summ = fit_set()
    it = items()
    keys = [r["key"] for r in it]
    assert len(keys) == len(set(keys)), [k for k, v in collections.Counter(keys).items() if v > 1][:5]
    for name, rs in (("fit", fit), ("items", it)):
        with open(C.OUT / f"{name}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rs[0]))
            w.writeheader()
            w.writerows(rs)
    summ["items"] = dict(sorted(collections.Counter(r["group"] for r in it).items()))
    summ["missing_paths"] = [r["path"] for r in fit + it if not pathlib.Path(r["path"]).is_file()][:20]
    json.dump(summ, open(C.RES / "lists_summary.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
