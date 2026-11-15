"""Addendum to the partner-overlap audit (record keeper's gaps, lead 13 Nov 2026). Manifests and lists only, CPU.

Runs src/DATA/partner_overlap_audit.py (runpy; same resolution, same outputs) and adds:
(1) the positive control, as code: the development-host ladder rows of ab1x_eval treated as a training list; count of
    test-host rows that share a person or a source photo with them;
(2) unmapped photos (keyed by path, so the same raw photo reached by two paths would not match) per training list and
    evaluation set, and a scan of every AR1 / AF0 source frame for frames without a raw photo name, with whether any
    such frame is used by any audited row;
(3) geometry sharing: the persons whose landmarks shape a row's warp or mask, from the builders' definitions:
    AR1 rungs: persons of tem1 / tem2 (R2w4 and R4 = host + partner B; R2w, R3 = host only);
    7b splices (src/AR1/splice.py ARMS7B, one hull of the R4 geometry for every arm): S4, S3, S0 and their blanked
    R2w4 / R2w copies carry the hull of the host + partner landmarks; S0 and S4 sit on the R2w4 base (warped to the
    host + partner mean shape);
    SM1 halves of R4 (hA, hB) and AF0 / MS1 fields and halves: both persons of the pair; AF0 photos: the photo's person;
    GAN / diffusion rows (GD): latent mixing, no landmark geometry (not counted).
    Counts per training list: training rows whose geometry uses a person who appears in an evaluation set (host or
    partner, or as a geometry person), and the reverse; and the Sb rows of the training hosts whose pool partner is a
    test host.
  python3 -I partner_overlap_addendum.py -> experiments/DATA_builds/partner_overlap_addendum.json
"""
import collections
import json
import pathlib
import re
import runpy

HERE = pathlib.Path(__file__).resolve().parent
g = runpy.run_path(str(HERE / "partner_overlap_audit.py"))
R = pathlib.Path("/home/narolski/smad-next")
T7 = pathlib.Path("/mnt/t7/smad_next")
pool, role, photo, rd = g["pool"], g["role"], g["photo"], g["rd"]
TRAIN, train, evalrows, resolve = g["TRAIN"], g["train"], g["evalrows"], g["resolve"]
hrole, ar1, af0, ms1lad = g["hrole"], g["ar1"], g["af0"], g["ms1lad"]
out = {}

# ---------- (1) positive control
ev = evalrows["ab1x_eval"]
dev = [r for r in ev if r["role"] == "dev" and r["fam"] == "ladder"]
P = set().union(*[r["hosts"] | r["others"] for r in dev])
Ph = set().union(*[r["photos"] for r in dev])
test = [r for r in ev if hrole(r["host"]) == "test"]
out["positive_control"] = dict(
    definition="ab1x_eval rows with role dev and fam ladder taken as a training list; test-host rows of ab1x_eval "
               "sharing a host / partner person or a source photo with them",
    dev_rows=len(dev), test_rows=len(test),
    test_rows_flagged=sum(bool((r["hosts"] | r["others"]) & P or r["photos"] & Ph) for r in test))

# ---------- (2) unmapped photos
out["unmapped_photos_per_training_list"] = {k: sum(p.startswith("unmapped") for p in v["photos"]) for k, v in train.items()}
out["unmapped_photos_per_eval_set"] = {k: sum(p.startswith("unmapped") for p in set().union(*[r["photos"] for r in rows]))
                                       for k, rows in evalrows.items()}
used = set()
for v in train.values():
    used |= v["photos"]
for rows in evalrows.values():
    for r in rows:
        used |= r["photos"]
scan = collections.Counter()
unm_frames = []
for base in (T7 / "AR1/src", T7 / "AF0/src"):
    for f in sorted(base.glob("*/*/*.png")):
        k = photo(str(f))
        db = f.parent.parent.name
        scan[f"{base.parent.name}:{db}:{'unmapped' if k.startswith('unmapped') else 'mapped'}"] += 1
        if k.startswith("unmapped"):
            unm_frames.append(k)
out["source_frame_scan"] = dict(scan)
out["unmapped_source_frames_used_by_any_audited_row"] = sum(k in used for k in unm_frames)

# ---------- (3) geometry
partner = {h: p["B_pid"] for h, p in pool.items()}


def geom(i, host_col=""):
    b = re.sub(r"(__bd|__bg|__face|_jpeg\d+|_fm\d+|_amsl\d+|_selfm|__replay_attack|__msu_mfsd|__oulu_npu|__casia_fasd"
               r"|__lfw_calfw|__cfp_ff|__agedb_30)+$", "", i)
    b = re.sub(r"^bref_", "", b)
    m = re.fullmatch(r"ar1_(\d+)", b)
    if m and m.group(1) in ar1:
        r = ar1[m.group(1)]
        ps = {r["p1"]}
        for t in ("tem1", "tem2"):
            q = g["pid_of"](r.get(t, "") or "")
            if q:
                ps.add(q)
        if r.get("rung") in ("R4", "NC", "G") and r.get("p2"):
            ps.add(r["p2"])
        return ps, f"ar1_{r.get('rung', '')}"
    m = re.fullmatch(r"sp2?_(S[034]|R2w4|R2w)_(?:opencv|facemorpher)_(feret|frgc)_(\d+)", b)
    if m:
        h = f"{m.group(2)}:{m.group(3)}"
        return {h, partner[h]}, f"splice_{m.group(1)}"
    m = re.fullmatch(r"sm1h_(feret|frgc)_(\d+)_h([AB])", b)
    if m:
        h = f"{m.group(1)}:{m.group(2)}"
        return {h, partner[h]}, "sm1_half"
    m = re.fullmatch(r"((?:train|val|hold)_\w+?_\d+)_half([AB])", b)
    if m and m.group(1) in af0:
        r = af0[m.group(1)]
        return {r["pid_A"], r["pid_B"]}, "af0_half"
    if b in af0:
        r = af0[b]
        return {r["pid_A"], r["pid_B"]}, f"af0_{r.get('field', r.get('kind', ''))}"
    m = re.fullmatch(r"lad_ffhq_(\d+)_(\w+)", b)
    if m:
        h = f"ffhq:{m.group(1)}"
        return ({h} if m.group(2) == "R0" else {h, ms1lad[h]["B_pid"]}), f"ms1lad_{m.group(2)}"
    x = resolve(i, host_col)
    return (x[0] if x else set()), "other_no_landmark_geometry"


evP = set()
for rows in evalrows.values():
    for r in rows:
        evP |= r["hosts"] | r["others"] | geom(r["id"])[0]
geo = {}
for tn, p in TRAIN.items():
    T = train[tn]
    Tg = set(T["persons"])
    rows_t = rd(p)
    kinds = collections.Counter()
    n = 0
    for r in rows_t:
        gp, kind = geom(r["id"])
        Tg |= gp
        if gp & evP:
            n += 1
            kinds[kind] += 1
    rev = collections.Counter()
    for en, rows in evalrows.items():
        for r in rows:
            gp, kind = geom(r["id"])
            if gp & Tg:
                rev[en] += 1
    geo[tn] = dict(training_rows=len(rows_t), training_rows_geometry_uses_eval_person=n, by_kind=dict(kinds),
                   eval_rows_geometry_uses_training_person=dict(rev))
out["geometry"] = geo

# ---------- the 32 training hosts with a test partner, in the Sb list
sb = TRAIN["Sb (FS1, seeds 403-407; frozen candidate)"]
t32 = {h for h, P_ in pool.items() if role.get(h) == "train" and role.get(P_["B_pid"]) == "test"}
kinds = collections.Counter()
partner_landmarks = collections.Counter()
for r in rd(sb):
    x = resolve(r["id"])
    if x and x[0] & t32:
        gp, kind = geom(r["id"])
        kinds[f"{r['kind']}|{kind}"] += 1
        if any(partner[h] in gp for h in x[0] & t32):
            partner_landmarks[f"{r['kind']}|{kind}"] += 1
out["sb_rows_of_32_training_hosts_with_test_partner"] = dict(hosts=len(t32), rows_by_kind=dict(kinds),
                                                            rows_using_partner_landmarks=dict(partner_landmarks))
json.dump(out, open(R / "experiments/DATA_builds/partner_overlap_addendum.json", "w"), indent=1)
print(json.dumps(out, indent=1))
