import csv, numpy as np, pathlib
from scipy.stats import spearmanr
U='/mnt/t7/smad_next/PN1/results_rented/unpacked/'
ev=[r for r in csv.DictReader(open('/mnt/t7/smad_next/PN1/manifests2/pn1_eval.csv')) if r['fam']=='h1']
h1={'h1_'+r['id']:r for r in csv.DictReader(open('/mnt/t7/smad_heldout/h1_poisson/data/manifests/h1poisson.csv'))}
def load(p):
    z=np.load(p); return dict(zip([str(i) for i in z['id']], z['logit'].astype(float)))
miss=sum(r['id'] not in h1 for r in ev); print('unmapped',miss,len(ev))
for s in (401,402):
    S={a:load(U+f'PN1_{a}_s{s}/scores_eval.npz') for a in ('A','B','Sb','Bv','C')}
    mor=[r for r in ev if r['label']=='1']; bon={h1[r['id']]['host']:r['id'] for r in ev if r['label']=='0'}
    for a in S:
        pr=[S[a][r['id']]>S[a][bon[h1[r['id']]['host']]] for r in mor if h1[r['id']]['host'] in bon]
        print(s,a,'paired share morph>own host bona %.3f n=%d'%(np.mean(pr),len(pr)), 'own-rule miss %.3f'%np.mean([S[a][r['id']]<=0 for r in mor]), 'bona flag own %.3f'%np.mean([S[a][r['id']]>0 for r in ev if r['label']=='0']))
    d=np.array([S['Sb'][r['id']]-S['B'][r['id']] for r in mor]); bm=np.array([float(h1[r['id']]['blend_mask_frac']) for r in mor])
    cw=np.array([float(h1[r['id']]['cos_w600k_b'] or 'nan') for r in mor])
    ok=np.isfinite(cw)
    print(s,'Sb-B on morphs vs blend_mask_frac rho %.3f'%spearmanr(d,bm)[0], 'vs cos_w600k_b rho %.3f'%spearmanr(d[ok],cw[ok])[0])
    db=np.array([S['Sb'][r['id']]-S['B'][r['id']] for r in ev if r['label']=='0'])
    print(s,'median Sb-B logit: morphs %.2f bona %.2f'%(np.median(d),np.median(db)))
