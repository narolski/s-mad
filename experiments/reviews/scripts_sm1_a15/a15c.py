import csv, numpy as np, glob
from PIL import Image
D='/mnt/t7/smad_next/SM1/results_rented/dev'
rows=list(csv.DictReader(open('/mnt/t7/smad_next/SM1/dev_a14/sm1_dev_eval.csv')))
fam={}
for r in rows: fam.setdefault(r['family'],[]).append(r)
for f,L in fam.items():
    r=L[0]; p=r['path'][1:] if r['path'].startswith('x') else r['path']
    try: im=Image.open(p); print(f,im.size,im.mode,p.split('.')[-1])
    except Exception as e: print(f,'ERR',e)
rng=np.random.default_rng(20261111)
for T in ['SM1D_e_s401','SM1D_e_s402','SM1D_f_s401','SM1D_f_s402','SM1D_a_s401','SM1D_a_s402']:
    z=np.load(f'{D}/{T}/scores_audit.npz'); p=np.clip(z['score_noTTA'].astype(float),1e-7,1-1e-7)
    s=dict(zip([str(i) for i in z['id']],np.log(p/(1-p))))
    out=[]
    for st in ('amsl112','fm61'):
        inc=np.array([s[r['id']]-s[r['src_id']] for r in fam[f'R0_soft_{st}']])
        out.append((st,round(np.median(inc),3),round((inc<0).mean(),3),round(np.percentile(inc,90),3)))
    print(T,out)
