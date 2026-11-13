import csv, numpy as np, glob
man=list(csv.DictReader(open('/mnt/t7/smad_next/BB2/test_clip_Sb/data_pin/manifests/pn1_eval.csv')))
fam=lambda f,r:{x['host']:x['id'] for x in man if x['fam']==f and x['rung']==r}
nat=fam('ffhq','ffhq_bona_orig'); rm=fam('ffhq','landmark_complete_resmatch'); co=fam('ffhq','landmark_complete_orig')
keys=sorted(set(nat)&set(rm))
lcm=[x['id'] for x in man if x['fam']=='ffhq_lcomb' and x['rung']=='landmark_combined_orig']
lcg=[x['id'] for x in man if x['fam']=='ffhq_lcomb' and x['rung']=='landmark_combined_resmatch']
from collections import Counter
print(Counter((x['fam'],x['rung']) for x in man if x['fam'].startswith('ffhq')))
def auc(p,n):
    p=np.asarray(p);n=np.asarray(n); r=np.argsort(np.argsort(np.r_[p,n]))+1
    return (r[:len(p)].sum()-len(p)*(len(p)+1)/2)/(len(p)*len(n))
for arm in 'A','B','Sb':
  for s in range(403,408):
    z=np.load(f'/mnt/t7/smad_next/BB2/results/unpacked/BB2_{arm}_s{s}/scores_eval.npz')
    L=dict(zip(z['id'],z['logit']))
    a=np.array([L[nat[k]] for k in keys]); b=np.array([L[rm[k]] for k in keys]); c=np.array([L[co[k]] for k in sorted(set(co)&set(nat))])
    d=b-a
    print(arm,s,'nat mean %.2f sd %.2f | resm mean %.2f | shift/SD %+.2f | share>0 %.3f | flag nat %.3f resm %.3f | AUC complete orig vs resm %.3f | AUC resm vs nat %.3f | lcomb morph mean %.2f gen %.2f'%(
      a.mean(),a.std(),b.mean(),d.mean()/a.std(),(d>0).mean(),(a>0).mean(),(b>0).mean(),auc(c,b),auc(b,a),np.mean([L[i] for i in lcm]),np.mean([L[i] for i in lcg])))
