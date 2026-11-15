import csv, sys, json, numpy as np
from scipy.stats import rankdata
T=sys.argv[1]; M=sys.argv[2]
man=list(csv.DictReader(open(M)))
def ids(f,role,rung): return [r['id'] for r in man if r['fam']==f and r['role']==role and r['rung']==rung]
def auc(p,n):
    p,n=np.asarray(p),np.asarray(n); r=rankdata(np.r_[p,n]); return (r[:len(p)].sum()-len(p)*(len(p)+1)/2)/(len(p)*len(n))
lm=ids('ffhq_lcomb','a14','landmark_combined_orig'); lg=ids('ffhq_lcomb','a14','landmark_combined_resmatch')
nat={r['host']:r['id'] for r in man if r['fam']=='ffhq' and r['rung']=='ffhq_bona_orig'}
rm={r['host']:r['id'] for r in man if r['fam']=='ffhq' and r['rung']=='landmark_complete_resmatch'}
keys=sorted(set(nat)&set(rm))
out={}
for s in (403,404,405):
  for a in ('Sp','Sb','B'):
    z=np.load(f"{T}/PN1_{a}_s{s}/scores_eval.npz"); x=dict(zip([str(i) for i in z['id']],z['logit'].astype(float)))
    g=lambda rung:np.array([x[i] for i in ids('splice','dev',rung)])
    S0,S3,S4=g('S0'),g('S3'),g('S4')
    d=np.array([x[rm[k]]-x[nat[k]] for k in keys])
    o=dict(S0f=(S0>0).mean(),S3f=(S3>0).mean(),S4f=(S4>0).mean(),auc04=auc(S4,S0),auc03=auc(S3,S0),auc34=auc(S4,S3),
       face=auc(g('S4_bg'),g('S0_bg')), S0med=np.median(S0),S3med=np.median(S3),S4med=np.median(S4),
       lcomb=auc([x[i] for i in lm],[x[i] for i in lg]), store=(d>0).mean(), nkeys=len(keys),
       ffhq_nat_flag=np.mean([x[nat[k]]>0 for k in keys]), ffhq_rm_flag=np.mean([x[rm[k]]>0 for k in keys]))
    out[(s,a)]=o
    print(s,a,' '.join(f"{k}={v:.3f}" if isinstance(v,float) else f"{k}={v}" for k,v in o.items()))
  sp,sb=out[(s,'Sp')],out[(s,'Sb')]
  print(' p1',sp['S0f']>=max(2*sb['S0f'],sb['S0f']+0.10),' p2',sp['auc04']<=sb['auc04']-0.05)
