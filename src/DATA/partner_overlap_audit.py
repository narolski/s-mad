"""Partner-overlap audit (lead, 13 Nov 2026, urgent): manifests only, CPU, no image opened, no MEDS.

For every training list of the frozen candidate (Sb, FS1 seeds 403-407, with A and B of the same block) and of the
ablation arms (AB1 seeds 408-412, incl. the x / fm / b2 batches, and SE1) against every evaluation set
(pn1_eval, ab1_eval, ab1x_eval, pr1_gd):
  (1) host overlap, (2) partner overlap (either direction), (3) image overlap by source photo,
  (4) connected components of the person graph (host-partner edges of every row, training and evaluation together)
      and the evaluation hosts that are fully clean (no person and no source photo of the training list in any of
      their evaluation rows).
Images are identified by the raw photo they come from (colorFERET <subject>_<date>_<pose>[_a], FRGC still id; FFHQ key):
the AR1 / AF0 source frames are byte copies of the record's aligned frames, mapped to raw names through
dmad/data/maps/feret_map.csv and r6_train_sources.csv (verified copy in volatile_backup_20261113); FRGC r6 frames carry
the still id in their name; AG1 photos through AG1/inputs/pack/photos.json. Landmarks taken from a photo (warp-only
toward a partner shape, the zero field) count as use of that photo.
Each row resolves to host persons, other persons (partners) and photos from the builders' own lists:
AR1 manifests (p1, p2, tem1, tem2), AR1 pool.csv (H, S, B per host; S4 = H + B, S3 = H + S, S0 = H; R2w = H + S
landmarks; R2w4 = H + B landmarks), AF0 manifest (A, B; halfA = A, halfB = B), SM1 halves (hA = H, hB = B), MS1 FFHQ
lists, DG1 set B (src_a, src_b), AG1 (photo_a, photo_b). Unresolved rows are counted.
Outputs: experiments/DATA_builds/partner_overlap_tables.json (counts only) and, on /mnt/t7/smad_next/DATA/overlap/,
the per-arm clean evaluation host lists and the resolved row tables.

  python3 -I partner_overlap_audit.py
"""
import collections
import csv
import glob
import hashlib
import json
import pathlib
import re

T7 = pathlib.Path("/mnt/t7/smad_next")
R = pathlib.Path("/home/narolski/smad-next")
MC = pathlib.Path("/home/narolski/mambamorph-code")
OUT = T7 / "DATA/overlap"
DENY = re.compile(r"valx|fst|a12sp|a12-sp", re.I)


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def rd(p):
    assert not DENY.search(str(p)), p
    return list(csv.DictReader(open(p)))


# ---------- photo identity
fmap = {r["aligned"]: r["src"] for r in rd(MC / "dmad/data/maps/feret_map.csv")}
tsrc = {r["train_path"]: r["raw"] for r in rd(T7 / "volatile_backup_20261113/r6_train_sources.csv")
        if r["db"] == "frgc" and r["subject"] == r["train_subject"]}


def photo(path):
    p = pathlib.Path(path)
    name = p.name.replace(".tem", ".png")
    if "/src/feret/" in path or "/src/frgc/" in path:
        db = "feret" if "/src/feret/" in path else "frgc"
        if db == "feret":
            s = fmap.get(name)
            return f"feret:{s.split('.')[0].lower()}" if s else f"unmapped:{path}"
        if name.startswith("a"):
            s = tsrc.get(f"train/bona_frgc/{name}")
            return f"frgc:{pathlib.Path(s).stem.lower()}" if s else f"unmapped:{path}"
        return f"frgc:{p.stem.split('_', 1)[1].lower()}"
    if "/MS1/ffhq/src/" in path:
        return f"ffhqimg:{p.stem}"
    m = re.search(r"/AR1/mirror/frgcferet/((?:feret|frgc)_\d+)\.", path)
    if m:                                            # lossless mirror of the host photo H (variants.py)
        return photo(pool[norm_pid(m.group(1))]["H"])
    return f"unmapped:{path}"


def pid_of(path):
    m = re.search(r"/src/(feret|frgc)/(\d+)/", path)
    if m:
        return f"{m.group(1)}:{m.group(2)}"
    m = re.search(r"/MS1/ffhq/src/(\d+)\.", path)
    return f"ffhq:{m.group(1)}" if m else None


# ---------- builders' lists
pool = {r["pid"]: r for r in rd(T7 / "AR1/pool.csv")}
role = {r["pid"]: r["role"] for r in rd(R / "experiments/PN1_protocol-network-first-tests/split/ladder_split.csv")}
af0role = {r["pid"]: r["pn1_use"] for r in rd(R / "experiments/PN1_protocol-network-first-tests/split/af0_split.csv")}
ar1 = {}
for f in ("manifest.csv", "manifest_extra.csv", "manifest_extra2.csv"):
    for r in rd(T7 / "AR1" / f):
        ar1[r["id"]] = r
af0 = {r["id"]: r for r in rd(T7 / "AF0/manifest.csv")}
for r in rd(T7 / "MS1/ffhq/lists/af0_pairs.csv"):
    af0[r["id"]] = r
ms1soft = {r["src_id"]: r for r in rd(T7 / "MS1/ffhq/lists/soft.csv")}
ms1lad = {r["pid"]: r for r in rd(T7 / "MS1/ffhq/lists/ladder.csv")}
dg1 = {}
for r in rd(R / "experiments/DG1_diffusion-generation-athena/validity/setB_manifest.csv"):
    dg1[(r["rung"], r["host"])] = r
ag1 = {r["id"]: r for r in rd(T7 / "AG1/data/manifests/ag1.csv")}
agph = json.load(open(T7 / "AG1/inputs/pack/photos.json"))


def agphoto(k):
    s = agph.get(k, {}).get("src", "")
    if "/colorferet/" in s:
        return "feret:" + pathlib.Path(s).name.split(".")[0].lower()
    if "/FRGC-2.0/" in s:
        return "frgc:" + pathlib.Path(s).stem.lower()
    return f"unmapped:ag1:{k}"


def norm_pid(x):
    m = re.fullmatch(r"(feret|frgc|ffhq)_(\d+)", x)
    return f"{m.group(1)}:{m.group(2)}" if m else x


def resolve(i, host_col=""):
    """-> (hosts, others, photos) or None"""
    b = re.sub(r"(__bd|__bg|__face|_jpeg\d+|_fm\d+|_amsl\d+|_selfm|__replay_attack|__msu_mfsd|__oulu_npu|__casia_fasd"
               r"|__lfw_calfw|__cfp_ff|__agedb_30)+$", "", i)
    b = re.sub(r"^bref_", "", b)
    m = re.fullmatch(r"ar1_(\d+)", b)
    if m and m.group(1) in ar1:
        r = ar1[m.group(1)]
        ph, ps = set(), set()
        for t in ("tem1", "tem2"):
            if r.get(t):
                ph.add(photo(r[t]))
                q = pid_of(r[t])
                if q:
                    ps.add(q)
        if not ph and r.get("path"):
            ph.add(photo(r["path"]))
        h = {r["p1"]}
        return h, (ps | {r["p2"]}) - h, ph
    m = re.fullmatch(r"sp2?_(S[034]|R2w4|R2w)_(?:opencv|facemorpher)_(feret|frgc)_(\d+)", b)
    if m:
        h = f"{m.group(2)}:{m.group(3)}"
        P = pool[h]
        g = m.group(1)
        if g == "S4":
            return {h}, {P["B_pid"]}, {photo(P["H"]), photo(P["B"])}
        if g == "S3" or g == "R2w":
            return {h}, set(), {photo(P["H"]), photo(P["S"])}
        if g == "R2w4":
            return {h}, {P["B_pid"]}, {photo(P["H"]), photo(P["B"])}
        return {h}, set(), {photo(P["H"])}
    m = re.fullmatch(r"sm1h_(feret|frgc)_(\d+)_h([AB])", b)
    if m:
        h = f"{m.group(1)}:{m.group(2)}"
        P = pool[h]
        return ({h}, set(), {photo(P["H"])}) if m.group(3) == "A" else (set(), {P["B_pid"]}, {photo(P["B"])})
    m = re.fullmatch(r"((?:train|val|hold)_\w+?_\d+)_half([AB])", b)
    if m and m.group(1) in af0:
        r = af0[m.group(1)]
        if m.group(2) == "A":
            return {r["pid_A"]}, set(), {photo(r["A"])}
        return set(), {r["pid_B"]}, {photo(r["B"])}
    if b in af0:
        r = af0[b]
        h = {r["pid_A"]}
        return h, {r["pid_B"]} - h, {photo(r["A"]), photo(r["B"])}
    if b in ms1soft:
        r = ms1soft[b]
        return {r["pid"]}, set(), {photo(r["src"])}
    m = re.fullmatch(r"lad_ffhq_(\d+)_(\w+)", b)
    if m:
        h = f"ffhq:{m.group(1)}"
        L = ms1lad[h]
        if m.group(2) in ("R0", "hA"):
            return {h}, set(), {photo(L["H"])}
        if m.group(2) == "hB":
            return set(), {L["B_pid"]}, {photo(L["B"])}
        return {h}, {L["B_pid"]}, {photo(L["H"]), photo(L["B"])}
    m = re.fullmatch(r"gd1_dg1_B_G_((?:feret|frgc)_\d+)_([HS])", b)
    if m:
        h = norm_pid(m.group(1))
        return {h}, set(), {photo(pool[h][m.group(2)])}
    m = re.fullmatch(r"gd2_R0__((?:feret|frgc)_\d+)__(s\d)", b)
    if m:
        return {norm_pid(m.group(1))}, set(), {agphoto(f"{m.group(1)}__{m.group(2)}")}
    m = re.fullmatch(r"gd1_dg1_B_([A-Z]+)\d*_((?:feret|frgc)_\d+)(?:__((?:feret|frgc)_\d+))?(?:_H)?", b)
    if m:
        h = norm_pid(m.group(2))
        rg = {"X": "X", "SAME": "SAME", "REC": "REC", "MIR": "MIR", "G": "G", "DOSE": "DOSE"}.get(m.group(1), m.group(1))
        r = dg1.get((rg, h))
        P = pool[h]
        if r is None:
            return {h}, set(), {photo(P["H"])}
        ph, ot = set(), set()
        for s in (r["src_a"], r["src_b"]):
            mm = re.fullmatch(r"((?:feret|frgc)_\d+)_([HS])(?:__flip)?", s)
            if mm:
                q = norm_pid(mm.group(1))
                ph.add(photo(pool[q][mm.group(2)]))
                if q != h:
                    ot.add(q)
        return {h}, ot, ph
    m = re.fullmatch(r"gd2_(mip\d_\w+)", b)
    if m and m.group(1) in ag1:
        r = ag1[m.group(1)]
        h = norm_pid(r["pa"])
        o = {norm_pid(r["pb"])} - {h}
        return {h}, o, {agphoto(r["photo_a"]), agphoto(r["photo_b"])}
    if re.fullmatch(r"gd0_\w+", b) or re.fullmatch(r"(lcomb_)?fq\d+", b):
        hs = set()
        for k in re.findall(r"\d{5}", host_col or ""):
            hs.add(f"ffhq:{k}")
        return hs, set(), {f"ffhqimg:{k}" for k in re.findall(r"\d{5}", host_col or "")}
    return None


# ---------- lists
TRAIN = {
    "Sb (FS1, seeds 403-407; frozen candidate)": T7 / "PN1/fs_tree/pn1/data/manifests/train_Sb.csv",
    "A (FS1)": T7 / "PN1/fs_tree/pn1/data/manifests/train_A.csv",
    "B (FS1)": T7 / "PN1/fs_tree/pn1/data/manifests/train_B.csv",
}
for f in sorted(glob.glob(str(T7 / "AB1/overlay_tree/pn1/data/manifests/train_*.csv")) +
                glob.glob(str(T7 / "AB1/x/manifests/train_*.csv")) + glob.glob(str(T7 / "AB1/fm/manifests/train_*.csv")) +
                glob.glob(str(T7 / "AB1/b2/manifests/train_*.csv")) + glob.glob(str(T7 / "SE1/manifests/train_*.csv"))):
    TRAIN[f"{pathlib.Path(f).stem.replace('train_', '')} ({pathlib.Path(f).parent.parent.relative_to(T7)})"] = pathlib.Path(f)
EVAL = {
    "pn1_eval (FS1)": T7 / "PN1/fs_tree/pn1/data/manifests/pn1_eval.csv",
    "ab1_eval": T7 / "AB1/overlay_tree/pn1/data/manifests/ab1_eval.csv",
    "ab1x_eval": T7 / "AB1/x/manifests/ab1x_eval.csv",
    "pr1_gd (GD ladder)": T7 / "PR1/pr1_gd_tree/pr1g/data/manifests/pr1_gd.csv",
}
BENCH = re.compile(r"^(bench|frllm|mad22|h1)$")

OUT.mkdir(parents=True, exist_ok=True)
train = {}
unres = {}
for name, p in TRAIN.items():
    hosts, others, photos, bad = set(), set(), set(), collections.Counter()
    for r in rd(p):
        x = resolve(r["id"])
        if x is None:
            bad[re.sub(r"\d+", "N", r["id"])] += 1
            continue
        hosts |= x[0]
        others |= x[1]
        photos |= x[2]
    train[name] = dict(hosts=hosts, others=others, persons=hosts | others, photos=photos, file=str(p), sha256=sha(p))
    unres[name] = dict(bad)

evalrows = {}
eunres = {}
for name, p in EVAL.items():
    rows, bad = [], collections.Counter()
    for r in rd(p):
        fam = r.get("fam", "")
        if BENCH.match(fam):
            continue                                   # benchmark cells: not development evaluation, not audited here
        x = resolve(r["id"], r.get("host", ""))
        if x is None:
            bad[re.sub(r"\d+", "N", r["id"]) + "|" + fam] += 1
            continue
        h = x[0] or ({r["host"]} if r.get("host") else set())
        host = sorted(h)[0] if h else (sorted(x[1])[0] if x[1] else "")
        rows.append(dict(id=r["id"], fam=fam, rung=r.get("rung", ""), role=r.get("role", ""),
                         host=host, hosts=h, others=x[1], photos=x[2]))
    evalrows[name] = rows
    eunres[name] = dict(bad)


def hrole(h):
    return role.get(h) or (f"af0_{af0role[h]}" if h in af0role else h.split(":")[0])


# ---------- per training list x evaluation set
tables = {}
clean_lists = {}
for tn, T in train.items():
    tab = {}
    for en, rows in evalrows.items():
        g = collections.defaultdict(lambda: collections.Counter())
        hostsets = collections.defaultdict(lambda: dict(rows=0, dirty=0, host_in=0, partner_in=0, photo_in=0))
        for r in rows:
            key = f"{r['fam']}|{r['rung']}|{hrole(r['host'])}"
            c = g[key]
            c["rows"] += 1
            hi = bool(r["hosts"] & T["persons"])
            pi = bool(r["others"] & T["persons"])
            phi = bool(r["photos"] & T["photos"])
            c["host_is_training_person"] += hi
            c["host_is_training_host"] += bool(r["hosts"] & T["hosts"])
            c["partner_is_training_person"] += pi
            c["shares_training_photo"] += phi
            c["any"] += (hi or pi or phi)
            hs = hostsets[r["host"]]
            hs["rows"] += 1
            hs["dirty"] += (hi or pi or phi)
        per_role = collections.defaultdict(lambda: collections.Counter())
        for h, v in hostsets.items():
            per_role[hrole(h)]["hosts"] += 1
            per_role[hrole(h)]["clean_hosts"] += (v["dirty"] == 0)
        tab[en] = dict(cells={k: dict(v) for k, v in sorted(g.items())},
                       hosts_by_role={k: dict(v) for k, v in sorted(per_role.items())})
        clean_lists[(tn, en)] = sorted(h for h, v in hostsets.items() if v["dirty"] == 0)
    tables[tn] = dict(training_file=T["file"], training_sha256=T["sha256"], training_hosts=len(T["hosts"]),
                      training_partner_only_persons=len(T["others"] - T["hosts"]), training_photos=len(T["photos"]),
                      unresolved_training_ids=unres[tn], by_eval=tab)

# ---------- between evaluation roles (development against test, within the ladder pool)
lad = [r for r in evalrows["ab1x_eval"] if r["fam"] == "ladder" or r["id"].startswith("sp2_")]
byrole = collections.defaultdict(lambda: dict(persons=set(), photos=set()))
for r in lad:
    rl = hrole(r["host"])
    byrole[rl]["persons"] |= r["hosts"] | r["others"]
    byrole[rl]["photos"] |= r["photos"]
cross = {}
for a in sorted(byrole):
    for b2 in sorted(byrole):
        if a < b2:
            cross[f"{a} x {b2}"] = dict(shared_persons=len(byrole[a]["persons"] & byrole[b2]["persons"]),
                                       shared_photos=len(byrole[a]["photos"] & byrole[b2]["photos"]))
# pool partner structure
pp = collections.Counter()
for h, P in pool.items():
    pp[f"{role.get(h, '?')} host -> partner {role.get(P['B_pid'], '?')}"] += 1
bsame = sum(photo(P["B"]) == photo(pool[P["B_pid"]]["S"]) for P in pool.values() if P["B_pid"] in pool)

# ---------- components (person graph, all rows of all lists)
adj = collections.defaultdict(set)


def link(ps):
    ps = [q for q in ps if q]
    for q in ps:
        adj[q]
    for i in range(1, len(ps)):
        adj[ps[0]].add(ps[i])
        adj[ps[i]].add(ps[0])


for tn, p in TRAIN.items():
    for r in rd(p):
        x = resolve(r["id"])
        if x:
            link(sorted(x[0]) + sorted(x[1]))
for en, rows in evalrows.items():
    for r in rows:
        link(sorted(r["hosts"]) + sorted(r["others"]))
comp, seen = {}, set()
sizes = []
for n in sorted(adj):
    if n in seen:
        continue
    stack, cc = [n], []
    seen.add(n)
    while stack:
        u = stack.pop()
        cc.append(u)
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    for u in cc:
        comp[u] = len(sizes)
    sizes.append(cc)
lp = [c for c in sizes if any(q.split(":")[0] in ("feret", "frgc") for q in c)]
compstats = dict(components=len(sizes), feret_frgc_components=len(lp),
                 size_histogram=dict(sorted(collections.Counter(len(c) for c in lp).items())),
                 largest=max(len(c) for c in lp))
mixed = {}
for tn, T in train.items():
    evh = {r["host"] for rows in evalrows.values() for r in rows if r["host"].split(":")[0] in ("feret", "frgc")}
    mixed[tn] = dict(eval_ladder_af0_hosts=len(evh),
                     eval_hosts_whose_component_holds_a_training_person=sum(
                         any(q in T["persons"] for q in sizes[comp[h]]) for h in evh if h in comp))

res = dict(time="see README", training=tables, between_eval_roles=cross, pool_partner_roles=dict(pp),
           pool_partner_photo_is_partners_S=f"{bsame} of {len(pool)}", components=compstats,
           eval_hosts_in_components_with_training_persons=mixed, unresolved_eval_ids=eunres,
           eval_files={k: sha(v) for k, v in EVAL.items()})
json.dump(res, open(R / "experiments/DATA_builds/partner_overlap_tables.json", "w"), indent=1)
with open(OUT / "clean_eval_hosts.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["training_list", "eval_set", "host", "role"])
    for (tn, en), hs in sorted(clean_lists.items()):
        for h in hs:
            w.writerow([tn, en, h, hrole(h)])
print(json.dumps(dict(components=compstats, between=cross, pool=dict(pp), bsame=res["pool_partner_photo_is_partners_S"],
                      unres_train={k: v for k, v in unres.items() if v}, unres_eval=eunres), indent=1))
