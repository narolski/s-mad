import sys, csv, re, numpy as np, importlib.util
from scipy.stats import spearmanr
spec=importlib.util.spec_from_file_location("p3","/home/narolski/smad-next/src/MS1/ms1_part3.py")
# reuse xlsx parser only (no main run)
src=open("/home/narolski/smad-next/src/MS1/ms1_part3.py").read()
ns={}
body=src[src.index("def xlsx_rows"):src.index("def load_npz")]; exec("import zipfile,re,pathlib\nimport xml.etree.ElementTree as ET\nNORM=pathlib.Path(\"/mnt/t7/Datasety/downloads/ChicagoFaceDatabase/cfd/CFD Version 3.0.1/CFD 3.0.1 Norming Data and Codebook.xlsx\")\n"+body,ns)
norm=ns["norming"]()
pool=list(csv.DictReader(open("/mnt/t7/smad_next/MS1/cfd/pool.csv")))
mo={}
for r in pool:
    m=re.search(r"CFD-([ABLW][FM]-\d+)-\d+-N\.jpg$",r["raw"])
    if m and r["aligned"]=="1" and "/CFD/" in r["raw"]: mo[r["id"]]=m.group(1)
ids=[i for i in sorted(mo) if mo[i] in norm]
print("pool",len(pool),"main aligned",len(mo),"with norming",len(ids),"unique models",len(set(mo[i] for i in ids)))
# gender self vs code
gs=[(mo[i][1],norm[mo[i]]["GenderSelf"]) for i in ids]
from collections import Counter; print(Counter(gs))
L={}
for a in ("Sb","SbM3","SbV"):
    for s in range(403,408):
        z=np.load(f"/mnt/t7/smad_next/MS1/results_rented/heldout/MS1H_{a}_s{s}_cfd.npz")
        L[(a,s)]=dict(zip(z["id"].astype(str),z["logit"].astype(float)))
print("flag rate logit>0 all 831:",{a:[round(np.mean(np.array(list(L[(a,s)].values()))>0),4) for s in range(403,408)] for a in ("Sb","SbM3")})
fem=lambda i:norm[mo[i]]["Feminine"]
for a in ("Sb","SbM3","SbV"):
    print("==",a)
    for g in "ABLW":
        gi=[i for i in ids if mo[i][0]==g]
        r=[spearmanr([L[(a,s)][i] for i in gi],[fem(i) for i in gi]).correlation for s in range(403,408)]
        # within sex
        ws={}
        for sx in "FM":
            gg=[i for i in gi if mo[i][1]==sx]
            ws[sx]=(len(gg),round(np.median([spearmanr([L[(a,s)][i] for i in gg],[fem(i) for i in gg]).correlation for s in range(403,408)]),3))
        # sex-only point-biserial
        rs=np.median([spearmanr([L[(a,s)][i] for i in gi],[mo[i][1]=="F" for i in gi]).correlation for s in range(403,408)])
        print(" ",g,"n",len(gi),"rho fem per seed",np.round(r,3),"med",round(np.median(r),3),"| rho(sex=F)",round(rs,3),"| within sex",ws)
    # pooled within sex across groups
    for sx in "FM":
        gg=[i for i in ids if mo[i][1]==sx]
        print("  pooled",sx,len(gg),round(np.median([spearmanr([L[(a,s)][i] for i in gg],[fem(i) for i in gg]).correlation for s in range(403,408)]),3))
# flags counts by group-sex for Sb (count of images, per seed)
for a in ("Sb","SbM3"):
    for g in "ABLW":
        for sx in "FM":
            gg=[i for i in ids if mo[i][:2]==g+sx]
            print(a,g+sx,len(gg),[sum(L[(a,s)][i]>0 for i in gg) for s in range(403,408)])
