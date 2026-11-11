import csv, numpy as np, sys
from scipy.stats import rankdata
O='/mnt/t7/smad_next/AR1/'
man={}
for f in ['manifest.csv','manifest_extra.csv','manifest_extra2.csv']:
    for r in csv.DictReader(open(O+f)):
        if r['pool']=='frgcferet': man[r['id']]=r
def auc(p,n):
    p,n=np.asarray(p),np.asarray(n); r=rankdata(np.r_[p,n]); return (r[:len(p)].sum()-len(p)*(len(p)+1)/2)/(len(p)*len(n))
dets=['own_selfmad','rel_madation_vitb16','rel_madation_vitl14','rel_mixfacenet_mad_smdd']
for det in dets:
  for var in ['','__face']:
    S={}
    files=[det+var] + ([det+'__extra',det+'__extra2'] if var=='' else [])
    for f in files:
        try: d=np.load(O+'scores/scores_'+f+'.npz',allow_pickle=True)
        except Exception: continue
        for i,s in zip(d['id'],d['score_noTTA']): S[str(i)]=float(s)
    out=[]
    for tool in ['opencv','facemorpher']:
      for db in ['frgc','feret']:
        g=lambda rung:[S[i] for i,r in man.items() if i in S and r['rung']==rung and r['tool']==tool and r['p1'].startswith(db)]
        a=g('R2w');b=g('R4');c=g('R3');w4=g('R2w4')
        out.append(f"{tool[:2]}/{db}: R2wR4 {auc(b,a):.3f}(n{len(a)},{len(b)}) R3R4 {auc(b,c):.3f}" + (f" R2w4R4 {auc(b,w4):.3f}" if w4 else ''))
    print(det,var or 'full','|'.join(out))
