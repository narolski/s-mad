"""PRIVATE helper: parses the printed supplement tables (smad-cvpr-2027 branch supplement-reorg) into the literal
reference file evaluation/supplement_reference.py of the release repo (value as printed + number of decimals).
  python3 build_supplement_reference.py <supp-worktree>/tables <release-repo>/evaluation/supplement_reference.py"""
import re, sys, pprint

T = sys.argv[1]
REF = {}
FAM = {"aMSL": "amsl", "FaceMorpher": "facemorpher", "OpenCV": "opencv", "StyleGAN": "stylegan", "Webmorph": "webmorph"}
DET = {"SelfMAD (release)": "SelfMAD (release)", "madation\\_vitb16": "MADation B/16", "madation\\_vitl14": "MADation L/14",
       "mixfacenet\\_mad\\_smdd": "MixFaceNet-MAD"}
M22C = ["FaceMorpher", "OpenCV", "Webmorph", "MIPGAN_I", "MIPGAN_II", "LM2", "M4"]
FRLC = ["amsl", "facemorpher", "opencv", "stylegan", "webmorph"]


def num(s):
    s = s.strip().replace("$-$", "-")
    return float(s), (len(s.split(".")[1]) if "." in s else 0)


def pm(s):
    a, b = s.split("$\\pm$")
    return num(a), num(b)


def tables(fn):
    txt = open(f"{T}/{fn}").read()
    for t in re.findall(r"\\begin\{table\*?\}.*?\\end\{table\*?\}", txt, re.S):
        lab = re.search(r"\\label\{([^}]*)\}", t).group(1)
        yield lab, t


def rows(t):
    body = t.split("\\midrule", 1)[1] if "\\midrule" in t else t
    for ln in body.replace("\\midrule", "\n").split("\\\\"):
        ln = ln.replace("\\addlinespace", "").strip()
        if "&" in ln and not ln.startswith("\\bottomrule"):
            yield [c.strip() for c in ln.split("&")]


# FRLL grid
for lab, t in tables("supp_frll_grid.tex"):
    for c in rows(t):
        if len(c) < 7: continue
        f = FAM[c[0]]
        d = c[1] if c[1].startswith("Sb") or c[1].startswith("SelfMAD") else DET[c[1].split(" [")[0]]
        REF["frll_grid", f, d, "eer"] = num(c[2])
        lo, hi = c[3].strip("[]").split(",")
        REF["frll_grid", f, d, "ci_lo"] = num(lo); REF["frll_grid", f, d, "ci_hi"] = num(hi)
        REF["frll_grid", f, d, "auc"] = num(c[4])
        a, b = c[5].split("/")
        REF["frll_grid", f, d, "own_apcer"] = num(a); REF["frll_grid", f, d, "own_bpcer"] = num(b)
    for m in re.finditer(r"\{(\w+): Sb seed mean ([\d.]+), sd ([\d.]+), min ([\d.]+), max ([\d.]+)\}", t):
        for k, v in zip(("mean", "sd", "min", "max"), m.groups()[1:]):
            REF["frll_grid", FAM[m.group(1)], "Sb seeds", k] = num(v)


def cellname(s):
    return s.replace("\\_", "_").replace("MIPGAN-I ", "MIPGAN_I ").replace("MIPGAN-II ", "MIPGAN_II ")


for lab, t in tables("supp_ad5_retrains.tex"):
    for c in rows(t):
        name = cellname(c[0])
        if "dagger" in name: continue
        if lab == "tab:retrain_replication":
            for tag, rw, h in zip(("B16", "L14", "MixFaceNet"), c[2::2], c[3::2]):
                REF["authors", name, tag, "RW"] = num(rw)
                (m, s) = pm(h); REF["authors", name, tag, "v1_mean"] = m; REF["authors", name, tag, "v1_sd"] = s
        elif lab == "tab:retrain_v2":
            for tag, h in zip(("B16", "L14", "MixFaceNet"), c[1:]):
                (m, s) = pm(h); REF["authors", name, tag, "v2_mean"] = m; REF["authors", name, tag, "v2_sd"] = s
        elif lab == "tab:selfmad_retrain":
            for s, v in zip(range(401, 406), c[1:6]):
                REF["selfmad", name, f"s{s}"] = num(v)
            (m, s) = pm(c[6]); REF["selfmad", name, "mean"] = m; REF["selfmad", name, "sd"] = s
    if lab == "tab:selfmad_retrain":
        mm = re.search(r"\(S\) ([\d., ]+) and \(H\) ([\d., ]+) for", t)
        for form, g in zip("SH", mm.groups()):
            for f, v in zip(M22C[:5], g.strip(" ,").split(", ")):
                REF["selfmad", f"MAD22 {f} ({form})", "RW common"] = num(v)

TAB = {"tab:ad6_H_v1": "H_v1", "tab:ad6_S_v1": "S_v1", "tab:ad6_H_v2": "H_v2", "tab:ad6_old_v1": "P_v1"}
for lab, t in tables("supp_ad6_retrains.tex"):
    cur = None
    for c in rows(t):
        if c[0]: cur = c[0]
        if lab in TAB:
            for col, v in zip(M22C, c[2:]):
                REF["ours_mad22", TAB[lab], cur, c[1], col] = num(v)
        elif lab in ("tab:ad6_frll_v1", "tab:ad6_frll_v2"):
            v = lab[-2:]
            if c[1].startswith("mean"):
                for col, x in zip(FRLC, c[2:]):
                    (m, s) = pm(x); REF["ours_frll", v, cur, "mean", col] = m; REF["ours_frll", v, cur, "sd", col] = s
            else:
                for col, x in zip(FRLC, c[2:]):
                    REF["ours_frll", v, cur, c[1], col] = num(x)

for lab, t in tables("supp_sealed_read.tex"):
    form = {"tab:sealed_0": "S", "tab:sealed_1": "H"}.get(lab)
    if not form: continue
    for c in rows(t):
        col = c[0].replace("\\_", "_").split(" ")[0]
        for s, v in zip(range(403, 408), c[1].split(",")):
            REF["sealed_seeds", form, col, f"s{s}"] = num(v)
        m, sd = c[2].split(" (")
        REF["sealed_seeds", form, col, "mean"] = num(m); REF["sealed_seeds", form, col, "sd"] = num(sd.rstrip(")"))
        REF["sealed_seeds", form, col, "best_release"] = num(c[4])

with open(sys.argv[2], "w") as fo:
    fo.write('"""Values as printed in the supplement tables: key -> (value, number of printed decimals).\n'
             'Generated from the supplement LaTeX sources; do not edit by hand."""\n')
    fo.write("REF = " + pprint.pformat(REF, width=120, sort_dicts=False) + "\n")
print(len(REF), "reference cells")
