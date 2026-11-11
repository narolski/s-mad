import sys, csv, re, numpy as np, pathlib, collections, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lib import *
R = rows_eval(); ids = [r["id"] for r in R]
dev = sel(R, "devbona","devbona","orig","0"); orig = sel(R,"frllm","frll_bona","orig","0")
src = np.array(["FRGC" if "nd1" in R[i]["name"] else "FERET" for i in dev])
fb = np.array([float(R[i]["file_bytes"]) for i in dev])
print("devbona stored-file bytes median: FERET %.0f  FRGC %.0f ; FRLL orig aligned? (manifest bytes are raw files)" % (np.median(fb[src=="FERET"]), np.median(fb[src=="FRGC"])))
# gender effect on genuine photos
MDR = pathlib.Path("/mnt/t7/Datasety/downloads/MorDIFF/MorDIFF_crop"); rx = re.compile(r"^morph_(\d{3})_(\d{2})_and_(\d{3})_(\d{2})"); gp = {}
for d in MDR.glob("*_front_*_aligned"):
    g = "F" if "_female_" in d.name else "M"
    for p in (d/"morphed").glob("*.png"):
        m = rx.match(p.name); gp[m.group(1)] = g; gp[m.group(3)] = g
gg = np.array([gp[R[i]["name"][:3]] for i in orig])
FQ = list(csv.DictReader(open(FFHQM))); fid = [r["id"] for r in FQ]; fq = np.array([i for i, r in enumerate(FQ) if r["family"]=="ffhq_bona"])
a43 = list(csv.DictReader(open(A43/"data/manifests/a43.csv"))); a43ids = [r["id"] for r in a43]
arm = lambda a: [i for i, r in enumerate(a43) if r["source"]=="a43" and r["arm"]==a]
for nm, d in (("ViT-L/14","madation_vitl14"),("ViT-B/16","madation_vitb16"),("FE ViT-L/14","madation_fe_vitl14"),("SelfMAD ours","selfmad_hrnet_w18")):
    s = rel(d, ids); t = thr(s[dev], .05)
    print(f"\n{nm}: devbona 5% threshold; FA FERET {100*(s[dev][src=='FERET']>t).mean():.1f}% FRGC {100*(s[dev][src=='FRGC']>t).mean():.1f}%; AUC(FERET > FRGC) {auc(s[dev][src=='FERET'], s[dev][src=='FRGC']):.2f}")
    tF, tG = thr(s[dev][src=="FERET"], .05), thr(s[dev][src=="FRGC"], .05)
    print(f"   thresholds: all {t:.3f} FERET-only {tF:.3f} FRGC-only {tG:.3f}; FRLL orig FA at each: {100*(s[orig]>t).mean():.1f} / {100*(s[orig]>tF).mean():.1f} / {100*(s[orig]>tG).mean():.1f}")
    fm = lambda tt: np.mean([100*(s[sel(R, SETOF[f], f, 'orig', '1')] <= tt).mean() for f in FAMS])
    print(f"   family-mean miss at: all-dev {fm(t):.1f} | FERET-only {fm(tF):.1f} | FRGC-only {fm(tG):.1f} | FRLL-orig-fitted {fm(thr(s[orig], .05)):.1f}")
    print(f"   genuine FRLL orig: AUC(male > female) {auc(s[orig][gg=='M'], s[orig][gg=='F']):.2f}; FA at dev thr male {100*(s[orig][gg=='M']>t).mean():.1f}% female {100*(s[orig][gg=='F']>t).mean():.1f}%")
    sf = rel(d, fid, "ffhqm")[fq]
    print(f"   FFHQ orig n={len(sf)}: FA at dev thr {100*(sf>t).mean():.1f}%; share P>0.5 {100*(sf>0).mean():.2f}%; AUC(FFHQ > devbona) {auc(sf, s[dev]):.2f}; AUC(FFHQ > FRLL orig) {auc(sf, s[orig]):.2f}")
    sa = load(A43/f"a43_out/a43/{d}/rel/scores_a43.npz", a43ids, "logit_noTTA")
    print("   A43: " + " | ".join(f"{a} flag@dev {100*(sa[arm(a)]>t).mean():.1f} P>0.5 {100*(sa[arm(a)]>0).mean():.1f}" for a in ("E","D20","D","C20","A","B20")))
# M3 / M3L sample
nets = []
for ln in open(MC/"experiments/A36_published-detector-shortcuts/raw/A36_networks.tsv"):
    if ln.startswith("#"): continue
    f = ln.rstrip("\n").split("\t")
    if len(f) >= 7 and f[3] == "primary" and f[4].split()[0] in ("M3","M3L"): nets.append((f[4].split()[0], int(f[6]), pathlib.PurePath(f[0]).name))
P = {"jpeg50": sel(R,"frllm","frll_bona","jpeg50","0"), "jpeg70": sel(R,"frllm","frll_bona","jpeg70","0"), "resample50": sel(R,"frllm","frll_bona","resample50","0"),
     "E7 mordiff": sel(R,"mordiff","mordiff","resmatch","0"), "MorDIFF align": sel(R,"mordiff","mordiff_bona","orig","0"), "E7 dim_a": sel(R,"dim","dim_a","resmatch","0"), "E7 amsl": sel(R,"frllm","amsl","resmatch","0")}
print("\nMADation-recipe retrains (trained and scored on our frames), last checkpoint, FA % at own devbona 5% threshold [share with score>0.5]")
for meth, seed, run in sorted(nets):
    s = load(A12BR/run/"scores_eval_last.npz", ids, "score"); t = thr(s[dev], .05)
    print(f"  {meth} s{seed}: orig {100*(s[orig]>t).mean():4.1f} [{100*(s[orig]>.5).mean():4.1f}] " + " ".join(f"{k} {100*(s[v]>t).mean():4.1f} [{100*(s[v]>.5).mean():4.1f}]" for k, v in P.items()) + f" | thr {t:.4f}")
