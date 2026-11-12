import csv, numpy as np
from sklearn.metrics import roc_auc_score as AUC
U='/mnt/t7/smad_next/PN1/results_rented/unpacked/'
def load(p):
    z=np.load(p); return dict(zip([str(i) for i in z['id']], z['logit'].astype(float)))
hn=list(csv.DictReader(open('/mnt/t7/smad_next/PN1/hn2_tree/pn1h/data/manifests/pn1_hn2.csv')))
G={k:[r['id'] for r in hn if r['rung']==k] for k in ('ffhq_bona_orig','landmark_complete_resmatch')}
rng=np.random.default_rng(7)
for s in (401,402):
  for a in ('A','B','Bn','C'):
    S=load(U+f'PN1_HN2_s{s}/scores_hn2_{a}.npz'); b=np.array([S[i] for i in G['ffhq_bona_orig']]); rm=np.array([S[i] for i in G['landmark_complete_resmatch']])
    bs=[AUC(np.r_[np.ones(len(rm)),np.zeros(len(b))], np.r_[rm[rng.integers(0,len(rm),len(rm))], b[rng.integers(0,len(b),len(b))]]) for _ in range(500)]
    print(s,a,'AUC resmatch vs bona %.3f [%.3f, %.3f]'%(AUC(np.r_[np.ones(len(rm)),np.zeros(len(b))],np.r_[rm,b]),*np.percentile(bs,[2.5,97.5])))
ev=[r for r in csv.DictReader(open('/mnt/t7/smad_next/PN1/manifests2/pn1_eval.csv')) if r['fam']=='h1']
y=np.array([int(r['label']) for r in ev])
for s in (401,402):
    S={a:load(U+f'PN1_{a}_s{s}/scores_eval.npz') for a in ('A','B','Sb')}
    v={a:np.array([S[a][r['id']] for r in ev]) for a in S}
    pos=np.where(y==1)[0]; neg=np.where(y==0)[0]; d1=[];d2=[]
    for _ in range(1000):
        i=np.r_[rng.choice(pos,len(pos)),rng.choice(neg,len(neg))]
        d1.append(AUC(y[i],v['Sb'][i])-AUC(y[i],v['A'][i])); d2.append(AUC(y[i],v['Sb'][i])-AUC(y[i],v['B'][i]))
    print(s,'H1 Sb-A %.3f [%.3f, %.3f]'%(AUC(y,v['Sb'])-AUC(y,v['A']),*np.percentile(d1,[2.5,97.5])),'Sb-B %.3f [%.3f, %.3f]'%(AUC(y,v['Sb'])-AUC(y,v['B']),*np.percentile(d2,[2.5,97.5])))
