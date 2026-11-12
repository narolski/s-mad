import tarfile, hashlib, numpy as np, csv, io, sys
R='/mnt/t7/smad_next/SM1/results_rented'; C='/mnt/t7/smad_next/SM1/lora_scores_vitb'
meta=list(csv.DictReader(open('/mnt/t7/smad_next/SM1/flists/audit.csv')))
keys=sorted({r['key'] for r in meta if r['kind']=='KP'})
idx={(r['kind'],r['key'],int(r['slot'])):r['id'] for r in meta if r['kind'] in('KP','KE')}
dr=np.random.default_rng(20261111).integers(0,len(keys),(10000,len(keys)))
au={}
for arm in ['a','b','bp','c','e','f']:
  L=[]
  for s in ['401','402']:
    T=f'SM1B_{arm}_s{s}'; f=f'{R}/{T}.tar'
    h=hashlib.sha256(open(f,'rb').read()).hexdigest(); ok=h==open(f+'.sha256').read().split()[0]
    t=tarfile.open(f); 
    z=np.load(io.BytesIO(t.extractfile(f'{T}/audit/scores_audit.npz').read()))
    p=np.clip(z['score_noTTA'].astype(float),1e-7,1-1e-7); zi=dict(zip([str(i) for i in z['id']],np.log(p/(1-p))))
    cz=np.load(f'{C}/{arm}_s{s}.npz'); ci=dict(zip([str(i) for i in cz['id']],cz['logit'].astype(float)))
    md=max(abs(zi[k]-ci[k]) for k in zi)
    # also ad4eval
    z2=np.load(io.BytesIO(t.extractfile(f'{T}/ad4eval/scores_eval.npz').read())); n2=len(z2['id'])
    P=np.array([[zi[idx[('KP',k,j)]] for j in range(5)] for k in keys]); E=np.array([[zi[idx[('KE',k,j)]] for j in range(5)] for k in keys])
    d=P[:,:,None]-E[:,None,:]; a=((d>0)+0.5*(d==0)).mean((1,2)); L.append(a)
    print(T,'sha ok',ok,'audit n',len(zi),'max|tar-converted| audit',round(md,6),'ad4eval n',n2,'AUC',round(a.mean(),4))
  au[arm]=np.mean(L,0)
for arm,v in au.items(): print(arm, round(v.mean(),4), np.round(np.percentile(v[dr].mean(1),[2.5,97.5]),4))
for x,y in [('b','bp'),('a','bp'),('a','b')]:
  d=au[x]-au[y]; print(x,'-',y,round(d.mean(),4),np.round(np.percentile(d[dr].mean(1),[2.5,97.5]),4))
