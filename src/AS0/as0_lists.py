"""Mirror-asymmetry test (AS0), step 1: the item list of every existing image that is measured. Reads file lists and
metadata only (no pixel is read here, no statistic is computed).

  python3 -I as0_lists.py            -> /mnt/t7/smad_next/AS0/items.csv, lists_summary.json (copy in the experiment folder)

Item columns: id, set, role, tool, path, frame, lm (landmark source), persons ("p" or "p|q"), host, db, plus session /
expression metadata where it exists (s_a, s_b = capture dates of the two contributors, gap_days, same_session,
expr_a, expr_b, env_a, env_b), level (graded mixing fraction) and src (the item a history copy was made from).
Landmark sources: tem:<path> | mix:<a>;<b>;<w> (shape (1-w)*a + w*b; a/b are .tem paths) | det (detected by
as0_landmarks.py) | det_of:<id> (a history copy uses the landmarks of its native image) | smdd:<name>;<scale>.
"""
import collections
import datetime
import importlib.util
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import as0_common as K  # noqa: E402

A43 = pathlib.Path("/mnt/t7/smad_heldout/a43")
A256 = pathlib.Path("/mnt/t7/smad_heldout/a41_diffae/data/a41diffae/a256/png256")
AD1B = pathlib.Path("/mnt/t7/smad_next/AD1b")
X123 = pathlib.Path("/mnt/t7/smad_research/diffae-expanded123-v1")
MAD = pathlib.Path("/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z")
EVALF = K.MC / "smadcvpr_data/eval/frllm/frll_bona"
AF0 = pathlib.Path("/mnt/t7/smad_next/AF0")
R8B = pathlib.Path("/mnt/t7/smad_next/volatile_backup_20261111")
PD1G = pathlib.Path("/mnt/t7/smad_next/PD1/gan/items.csv")
RS = pathlib.Path("/mnt/t7/smad_research")
SMDD_LM = pathlib.Path("/dev/shm/smad_arms/smdd_bona_landmarks_if106.npz")
TOOLS = ("opencv", "facemorpher")
RUNGS = ("R2", "R2w", "R2wm", "R3", "R3m", "R4")


def frgc_meta():
    spec = importlib.util.spec_from_file_location("ar1_pool", K.REPO / "src/AR1/pool.py")
    sys.path.insert(0, str(K.REPO / "src/AR1"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.frgc_meta()            # stem -> (environment, ISO date, emotion), AR1 code imported unchanged


def feret_date(s):                  # yymmdd (1993-1997)
    return f"19{s[:2]}-{s[2:4]}-{s[4:6]}"


def days(a, b):
    if not a or not b:
        return ""
    return abs((datetime.date.fromisoformat(a) - datetime.date.fromisoformat(b)).days)


def cap_info(db, cap, meta):
    """capture -> (date, expression code, environment)."""
    if db == "feret":
        p = pathlib.Path(cap).stem.split("_")
        return feret_date(p[1]), p[2][:2], ""
    st = pathlib.Path(cap).stem.lower()
    env, date, emo = meta.get(st, ("", "", ""))
    return date, ("neutral" if emo == "BlankStare" else (emo or "")), env


def pairmeta(db, ca, cb, meta):
    da, ea, va = cap_info(db, ca, meta)
    if cb is None:
        return dict(s_a=da, expr_a=ea, env_a=va)
    dbb, eb, vb = cap_info(db, cb, meta)
    g = days(da, dbb)
    return dict(s_a=da, s_b=dbb, gap_days=g, same_session=int(g == 0) if g != "" else "", expr_a=ea, expr_b=eb,
                env_a=va, env_b=vb)


def main():
    meta = frgc_meta()
    items = []

    def add(**kw):
        assert not K.forbidden(kw["path"]), kw["path"]
        items.append(kw)

    # ---- L: landmark ladder (AR1), primary pool ----
    pool = {r["pid"]: r for r in K.read_csv(K.AR1 / "pool.csv")}
    for pid, r in pool.items():
        st = pid.replace(":", "_")
        H, S, B = r["H"][:-4] + ".tem", r["S"][:-4] + ".tem", r["B"][:-4] + ".tem"
        Hm = str(K.AR1 / "mirror/frgcferet" / f"{st}.tem")
        b = pool[r["B_pid"]]
        mHS = pairmeta(r["db"], r["H_raw"], r["S_raw"], meta)
        mHB = pairmeta(r["db"], r["H_raw"], b["S_raw"], meta)
        assert r["B"] == b["S"]
        base = dict(set="L", host=pid, db=r["db"], frame="ar1_512")
        add(id=f"L|{pid}|R0", role="R0", tool="none", path=r["H"], lm=f"tem:{H}", persons=pid,
            **base, **pairmeta(r["db"], r["H_raw"], None, meta))
        add(id=f"L|{pid}|S0", role="S0", tool="none", path=r["S"], lm=f"tem:{S}", persons=pid,   # second photo (other session)
            **base, **pairmeta(r["db"], r["S_raw"], None, meta))
        shapes = {"R2": f"tem:{H}", "R2w": f"mix:{H};{S};0.5", "R3": f"mix:{H};{S};0.5", "R2wm": f"mix:{H};{Hm};0.5",
                  "R3m": f"mix:{H};{Hm};0.5", "R4": f"mix:{H};{B};0.5"}
        for tool in TOOLS:
            for g in RUNGS:
                md = mHB if g == "R4" else (mHS if g in ("R2w", "R3") else pairmeta(r["db"], r["H_raw"], None, meta))
                add(id=f"L|{pid}|{tool}|{g}", role=g, tool=tool, path=str(K.AR1 / f"img/frgcferet/{tool}/{g}/{st}.png"),
                    lm=shapes[g], persons=f"{pid}|{r['B_pid']}" if g == "R4" else pid, **base, **md)
    gdir = K.AR1 / "img/frgcferet/fm_graded"
    for lev in sorted(d for d in gdir.iterdir() if d.is_dir() and d.name.startswith("m")):
        m = int(lev.name[1:]) / 100
        for f in sorted(lev.glob("*.png")):
            pid = f.stem.replace("_", ":", 1)
            r = pool[pid]
            H, B = r["H"][:-4] + ".tem", r["B"][:-4] + ".tem"
            add(id=f"L|{pid}|fm_graded|{lev.name}", set="L", role="G", level=m, tool="facemorpher", path=str(f),
                lm=f"mix:{H};{B};{m}", persons=f"{pid}|{r['B_pid']}" if m > 0 else pid, host=pid, db=r["db"],
                frame="ar1_512", **pairmeta(r["db"], r["H_raw"], pool[r["B_pid"]]["S_raw"], meta))

    # ---- Lsoft: AR1 photos and warp-only images with the existing shrink-and-enlarge history (AF0 wave 4) ----
    srcs = {r["id"]: r for r in K.read_csv(AF0 / "lists/ar1soft_src.csv")}
    for r in K.read_csv(AF0 / "soft_ar1soft_src.csv"):
        s = srcs[r["src_id"]]
        pid = s["p1"]
        src = f"L|{pid}|R0" if s["rung"] == "R0" else f"L|{pid}|{s['tool']}|{s['rung']}"
        add(id=f"Lsoft|{r['src_id']}|{r['strength']}", set="Lsoft", role=f"{s['rung']}_{r['strength']}",
            tool=s["tool"], path=r["path"], frame="ar1_512", lm=f"same_as:{src}", persons=pid, host=pid,
            db=pool[pid]["db"], src=src, aligned=r["aligned"])

    # ---- R8: landmark same-person morphs of two captures (record's r8 arms, backup copy), both tools ----
    import csv as _csv
    r8 = list(_csv.DictReader(open(K.guard("/dev/shm/smad_arms/r8_pairs.csv"))))
    for tool, d in (("opencv", "r8_cv"), ("facemorpher", "r8_fm")):
        tsv = [l.split("\t") for l in open(R8B / d / "pairs.tsv").read().splitlines() if l.strip()]
        assert len(tsv) == len(r8)
        for row, t in zip(r8, tsv):
            assert t[0].endswith(row["a"]) and t[2].endswith(row["b"])
            f = R8B / d / pathlib.Path(t[4]).name
            p = f"{row['db']}:{row['subject']}"
            add(id=f"R8|{row['idx']}|{tool}", set="R8", role="R3any", tool=tool, path=str(f), frame="ar1_512",
                lm=f"mix:{t[1]};{t[3]};0.5", persons=p, host=p, db=row["db"],
                **pairmeta(row["db"], row["a_cap"], row["b_cap"], meta))

    # ---- G: GAN latent blocks (PD1 GAN set G: x0 photo, x1 reconstruction, x2 same-person mix, x3 two-person) ----
    src = {}
    for pay in ("gan32-vast-v1", "gan32-trainplus-v1"):
        for s in json.load(open(RS / pay / "payload/inputs/SOURCES.json")):
            src[s["name"]] = s
    for r in K.read_csv(PD1G):
        if r["set"] != "G":
            continue
        blk, role = r["cluster"], r["id"].split("|")[2]
        db = r["db"]
        if r["role"] == "x0":
            md = pairmeta(db, src[r["src"]]["capture"], None, meta)
        elif r["role"] == "x1":
            md = pairmeta(db, src[r["src"]]["capture"], None, meta)
        else:
            a, b = r["src"].split(";")
            md = pairmeta(db, src[a]["capture"], src[b]["capture"], meta)
        add(id=r["id"], set="G", role=r["role"], tool="stylegan3", path=r["path"], frame=r["frame"], lm="det",
            persons=blk, host=blk, db=db, src=r["src"], **md)

    # ---- D: diffusion-autoencoder ladder (A43, DiffAE-native 256 frames, FRLL persons, evaluation only) ----
    for f in sorted(A256.glob("*.png")):
        p = f.stem.split("_")[0]
        add(id=f"D|{f.stem}|photo", set="D", role="photo", tool="none", path=str(f), frame="diffae256", lm="det",
            persons=p, host=p, db="frll", expr_a=f.stem.split("_")[1])
    for g, role in (("D20", "rec20"), ("C20", "same20"), ("B20", "two20"), ("B", "two100")):
        for f in sorted((A43 / "gen" / g / "png256").glob("*.png")):
            if g in ("D20",):
                p = f.stem.split("_")[0]; pers = p; ex = f.stem.split("_")[1]
            elif g == "C20":
                p = f.stem.split("_")[0]; pers = p; ex = "03+08"
            else:
                s = f.stem.split("_")
                p, q = s[1], s[4]
                pers = f"{p}|{q}"; ex = "03+03"
            add(id=f"D|{f.stem}|{role}", set="D", role=role, tool="diffae", path=str(f), frame="diffae256", lm="det",
                persons=pers, host=p, db="frll", expr_a=ex, same_session=1 if g == "C20" else "")
    # mirror mix (AD1b): smoke (4 persons) now; the full run is added by --ad1b-full when it has finished
    for g, role in (("PAF", "mirror20"), ("D20r", "rec20r")):
        for f in sorted((AD1B / "smoke_gen" / g / "png256").glob("*.png")):
            p = f.stem.split("_")[0]
            add(id=f"M|{f.stem}|{role}", set="M", role=role, tool="diffae", path=str(f), frame="diffae256", lm="det",
                persons=p, host=p, db="frll")
    # ---- Ds: the same A43 arms after the A43 storage step (stored crops), and the published MorDIFF morphs ----
    for g, role in (("E", "photo"), ("D20", "rec20"), ("C20", "same20"), ("B20", "two20"), ("A", "pub_mordiff")):
        for f in sorted((A43 / "data/a43/stored" / g).glob("*.png")):
            if g in ("E", "D20"):
                p = f.stem.split("_")[0]; pers = p
            elif g == "C20":
                p = f.stem.split("_")[0]; pers = p
            else:
                s = f.stem.split("_"); p, q = s[1], s[4]; pers = f"{p}|{q}"
            add(id=f"Ds|{f.stem}|{role}", set="Ds", role=role, tool="diffae", path=str(f), frame="a43_stored",
                lm="det", persons=pers, host=p, db="frll")

    # ---- Fm: corrected MAD22 canonical frames, native genuine photos and their E7 copies ----
    for f in sorted((MAD / "native/BonaFide").glob("*.png")):
        p = f.stem.split("_")[0]
        add(id=f"Fm|{f.stem}|native", set="Fm", role="native", tool="none", path=str(f), frame="canon512", lm="det",
            persons=p, host=p, db="frll", expr_a=f.stem.split("_")[1])
        for fam in ("FaceMorpher", "OpenCV", "Webmorph"):
            e = MAD / "e7" / fam / f.name
            add(id=f"Fm|{f.stem}|e7_{fam}", set="Fm", role=f"e7_{fam}", tool="none", path=str(e), frame="canon512",
                lm=f"det_of:Fm|{f.stem}|native", persons=p, host=p, db="frll", src=f"Fm|{f.stem}|native",
                expr_a=f.stem.split("_")[1])
    # ---- Fe: FRLL-Morphs evaluation frames, native and history-matched (resmatch) copies ----
    for f in sorted(EVALF.glob("*_orig.png")):
        st = f.stem[:-5]
        p = st.split("_")[0]
        add(id=f"Fe|{st}|native", set="Fe", role="native", tool="none", path=str(f), frame="canon512", lm="det",
            persons=p, host=p, db="frll", expr_a=st.split("_")[1])
        for fam in ("amsl", "facemorpher", "opencv", "webmorph"):
            add(id=f"Fe|{st}|e7_{fam}", set="Fe", role=f"e7_{fam}", tool="none",
                path=str(EVALF / f"{st}_resmatch_{fam}.png"), frame="canon512", lm=f"det_of:Fe|{st}|native",
                persons=p, host=p, db="frll", src=f"Fe|{st}|native", expr_a=st.split("_")[1])
    # ---- S: SMDD genuine renders and their stored-small E7 copies (PD1 set S) ----
    for r in K.read_csv(PD1G):
        if r["set"] != "S":
            continue
        name = pathlib.Path(r["path"]).stem
        if r["role"] == "s0":
            add(id=r["id"], set="S", role="native", tool="none", path=r["path"], frame="smdd256",
                lm=f"smdd:{name};1.0", persons=r["cluster"], host=r["cluster"], db="smdd", part=r["part"])
        else:
            add(id=r["id"], set="S", role="e7", tool="none", path=r["path"], frame="smdd80",
                lm=f"smdd:{name};0.3125", persons=r["cluster"], host=r["cluster"], db="smdd", part=r["part"],
                src=r["id"].rsplit("|", 1)[0] + "|orig")
    # ---- X: diffusion-autoencoder blocks on colorFERET / FRGC (expanded123; secondary, descriptive) ----
    plan = {b["id"]: b for b in json.load(open(X123 / "PLAN.json"))["blocks"]}
    for b in json.load(open(X123 / "run/BLOCKS.json")):
        if not b.get("complete_case"):
            continue
        bid, db = b["block"], b["db"]
        s = plan[bid]["sources"]
        d = X123 / "run" / bid
        for slot in ("a0", "a1", "b0", "b1"):
            add(id=f"X|{bid}|{slot}", set="X", role="photo", tool="none", path=str(d / f"{slot}-aligned.png"),
                frame="diffae256", lm="det", persons=bid, host=bid, db=db, src=s[slot]["capture"],
                **pairmeta(db, s[slot]["capture"], None, meta))
            add(id=f"X|{bid}|R{slot.upper()}", set="X", role="rec", tool="diffae", path=str(d / f"R{slot.upper()}.png"),
                frame="diffae256", lm="det", persons=bid, host=bid, db=db, src=s[slot]["capture"],
                **pairmeta(db, s[slot]["capture"], None, meta))
        for role, (u, v) in (("SA", ("a0", "a1")), ("SB", ("b0", "b1")), ("P0", ("a0", "b0")), ("P1", ("a1", "b1"))):
            add(id=f"X|{bid}|{role}", set="X", role="same" if role[0] == "S" else "two", tool="diffae",
                path=str(d / f"{role}.png"), frame="diffae256", lm="det", persons=bid, host=bid, db=db,
                **pairmeta(db, s[u]["capture"], s[v]["capture"], meta))

    # ---- amendment A3 (11 Nov 18:40): history copies with their OWN detected landmarks (appended rows) ----
    for it in [x for x in items if x["set"] in ("Fm", "Fe", "Lsoft") and x.get("src")]:
        add(**{**it, "id": it["id"] + "|own", "set": it["set"] + "O", "lm": "det"})
    seen = set()
    for it in [x for x in items if x["set"] == "Lsoft"]:
        s = it["src"]
        if s in seen:
            continue
        seen.add(s)
        n = next(x for x in items if x["id"] == s)
        add(**{**n, "id": s + "|own", "set": "LsoftN", "lm": "det"})
    # ---- amendment A10 (lead, 11 Nov 18:45; review of ID0, H-new-2): landmarks DETECTED on the built ladder images
    for it in [x for x in items if x["set"] == "L"]:
        r = it["role"]
        st = "LD1" if r in ("R0", "R3", "R4") else ("LD2" if r in ("S0", "R2w", "R3m", "R2wm", "R2") else "LD3")  # 18:58 S0 -> LD2 (CPU load)
        if r == "R2":
            continue
        add(**{**it, "id": it["id"] + "|det", "set": st, "lm": "det", "src": it["id"]})
    missing = [it["id"] for it in items if not pathlib.Path(it["path"]).exists()]
    fields = ["id", "set", "role", "tool", "level", "path", "frame", "lm", "persons", "host", "db", "src", "part",
              "aligned", "s_a", "s_b", "gap_days", "same_session", "expr_a", "expr_b", "env_a", "env_b"]
    K.write_csv(K.OUT / "items.csv", items, fields)
    summ = dict(n=len(items), missing=len(missing), missing_first=missing[:20],
                by_set_role=collections.Counter(f"{it['set']}|{it['role']}|{it.get('tool', '')}" for it in items),
                n_detect=sum(it["lm"] == "det" for it in items), items_sha256=K.sha(K.OUT / "items.csv"))
    json.dump(summ, open(K.OUT / "lists_summary.json", "w"), indent=1, default=str)
    json.dump(summ, open(K.RES / "lists_summary.json", "w"), indent=1, default=str)
    print(json.dumps(dict(n=summ["n"], missing=summ["missing"], n_detect=summ["n_detect"]), indent=1))


if __name__ == "__main__":
    main()
