import sys, csv, re, numpy as np, pathlib, collections, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lib import *
from scipy.stats import binomtest
R = rows_eval(); ids = [r["id"] for r in R]; dev = sel(R, "devbona","devbona","orig","0")
FQ = list(csv.DictReader(open(FFHQM))); fid = [r["id"] for r in FQ]
c = collections.Counter((r["family"], r["label"], r["variant"]) for r in FQ)
for k, v in sorted(c.items()): print(k, v)
ob = [i for i, r in enumerate(FQ) if r["family"]=="ffhq_bona"]; print(FQ[ob[0]])
fams = ("landmark_complete","landmark_combined","stylegan_w","stylegan_wplus","diffae")
for f in fams:
    rm = [i for i, r in enumerate(FQ) if r["family"]==f and r["label"]=="0"]; mm = [i for i, r in enumerate(FQ) if r["family"]==f and r["label"]=="1"]
    print(f, "E7 example", FQ[rm[0]]["path"], "| morph native_w med", np.median([float(FQ[i]["native_w"]) for i in mm]), "ied med", np.median([float(FQ[i]["ied"]) for i in mm]))
stem = lambda p: re.sub(r"_(orig|resmatch.*)$", "", pathlib.PurePath(p).stem)
okey = {stem(FQ[i]["path"]): i for i in ob}
for nm, d in (("ViT-L/14","madation_vitl14"),("ViT-B/16","madation_vitb16"),("FE ViT-L/14","madation_fe_vitl14"),("SelfMAD ours","selfmad_hrnet_w18")):
    s = rel(d, ids); t = thr(s[dev], .05); sf = rel(d, fid, "ffhqm"); to = thr(sf[ob], .05)
    print(f"\n{nm}: FFHQ orig FA@dev {100*(sf[ob]>t).mean():.1f}  (FFHQ-orig-fitted thr {to:.3f} vs dev thr {t:.3f})")
    for f in fams:
        rm = [i for i, r in enumerate(FQ) if r["family"]==f and r["label"]=="0"]
        pr = [(i, okey.get(stem(FQ[i]["path"]))) for i in rm]; pr = [(a, b) for a, b in pr if b is not None]
        if not pr: print("   ", f, "no pairing by stem", stem(FQ[rm[0]]["path"])); continue
        x = sf[[a for a, _ in pr]]; o = sf[[b for _, b in pr]]
        up = int(((x>t)&~(o>t)).sum()); dn = int((~(x>t)&(o>t)).sum())
        print(f"    E7 {f:18s} n={len(pr)} FA@dev {100*(x>t).mean():5.1f} (+{up}/-{dn}) | FA@FFHQ-orig-thr {100*(x>to).mean():5.1f} | P>0.5 {100*(x>0).mean():.1f} (orig {100*(o>0).mean():.1f}) | share up {100*(x>o).mean():.0f}% median shift {np.median(x-o):+.3f} ({np.median(x-o)/o.std():+.2f} SD)")
