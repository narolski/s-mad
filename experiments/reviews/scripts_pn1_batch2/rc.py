import csv, numpy as np, sys
U='/mnt/t7/smad_next/PN1/results_rented/unpacked/'
def auc(p,n):
    p=np.asarray(p);n=np.asarray(n)
    allv=np.concatenate([p,n]); r=allv.argsort().argsort().astype(float)
    # ties: use scipy-free average ranks
    from collections import defaultdict
    order=np.argsort(allv,kind='mergesort'); ranks=np.empty(len(allv)); 
    sv=allv[order]; i=0
    while i<len(sv):
        j=i
        while j+1<len(sv) and sv[j+1]==sv[i]: j+=1
        ranks[order[i:j+1]]=(i+j)/2+1; i=j+1
    return (ranks[:len(p)].sum()-len(p)*(len(p)+1)/2)/(len(p)*len(n))
def load(path):
    z=np.load(path); return dict(zip([str(i) for i in z['id']], z['logit'].astype(float)))
ev=list(csv.DictReader(open('/mnt/t7/smad_next/PN1/manifests2/pn1_eval.csv')))
def ids(**kw): return [r['id'] for r in ev if all(r[k]==v for k,v in kw.items())]
hn=list(csv.DictReader(open('/mnt/t7/smad_next/PN1/hn2_tree/pn1h/data/manifests/pn1_hn2.csv')))
G={k:[r['id'] for r in hn if r['rung']==k] for k in ('ffhq_bona_orig','landmark_complete_orig','landmark_complete_resmatch')}
print({k:len(v) for k,v in G.items()})
print('--- HN2')
for s in (401,402):
  for a in ('A','B','Bn','C'):
    S=load(U+f'PN1_HN2_s{s}/scores_hn2_{a}.npz')
    b=np.array([S[i] for i in G['ffhq_bona_orig']]); m=np.array([S[i] for i in G['landmark_complete_orig']]); rm=np.array([S[i] for i in G['landmark_complete_resmatch']])
    print(a,s,'flag_own %.3f'%np.mean(b>0),'auc %.4f'%auc(m,b),'auc_rm %.4f'%auc(m,rm),'rm_flag %.3f'%np.mean(rm>0),
      'med b %.2f rm %.2f m %.2f'%(np.median(b),np.median(rm),np.median(m)), 'auc rm vs bona %.3f'%auc(rm,b), 'morph miss %.3f'%np.mean(m<=0))
print('--- splice / H1')
def sc(arm,s):
    S=load(U+f'PN1_{arm}_s{s}/scores_eval.npz')
    if arm=='B': S.update(load(U+f'PN1_Brescore_s{s}/scores_splice.npz'))
    return S
for s in (401,402):
  for arm in ('A','B','Sb','Bv','Bn','C'):
    S=sc(arm,s)
    def A(pos,neg,role):
        P=ids(fam='splice',role=role,rung=pos); N=ids(fam='splice',role=role,rung=neg)
        if not all(i in S for i in P+N): return float('nan')
        return auc([S[i] for i in P],[S[i] for i in N])
    h1=auc([S[i] for i in ids(fam='h1',rung='morph')],[S[i] for i in ids(fam='h1',rung='bona')])
    print(arm,s,'H1 %.3f'%h1, 'T faceblank R4vR2w %.4f'%A('R4_face','R2w_face','test'),'D %.4f'%A('R4_face','R2w_face','dev'),
      '| T faceonly R4vR2w %.3f'%A('R4_bg','R2w_bg','test'),'faceonly R4vR2w4 %.3f'%A('R4_bg','R2w4_bg','test'),
      '| S4vS0 %.3f'%A('S4','S0','test'),'S4vS3 %.3f'%A('S4','S3','test'),'S4_bg v S0_bg %.3f'%A('S4_bg','S0_bg','test'),'S4_face v S0_face %.3f'%A('S4_face','S0_face','test'),
      '| R4 v S4 %.3f'%A('R4_face','S4_face','test'))
