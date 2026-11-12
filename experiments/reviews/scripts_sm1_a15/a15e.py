import csv, numpy as np
from scipy.stats import rankdata
D='/mnt/t7/smad_next/SM1/results_rented/dev'
rows=list(csv.DictReader(open('/mnt/t7/smad_next/SM1/dev_a14/sm1_dev_eval.csv')))
fz={r['id']:r for r in csv.DictReader(open('/mnt/t7/smad_next/FZ2/read_addon_items.csv'))}
fzid=lambda p:(p[1:] if p.startswith('x') else p).split('/gen/')[1].split('/',1)[1]
fam={}
for r in rows: fam.setdefault(r['family'],[]).append(r)
def auc(a,b):
    r=rankdata(np.r_[a,b]); return (r[:len(a)].sum()-len(a)*(len(a)+1)/2)/(len(a)*len(b))
def strat(sc,L,lab,k=5):
    q=np.quantile(L,np.linspace(0,1,k+1)[1:-1]); b=np.digitize(L,q); num=den=0
    for j in range(k):
        m=b==j; a1=sc[m&(lab==1)]; a0=sc[m&(lab==0)]
        if len(a1) and len(a0): w=len(a1)*len(a0); num+=auc(a1,a0)*w; den+=w
    return num/den
cue=lambda f,c: np.array([float(fz[fzid(r['path'])][c]) for r in fam[f]])
for A,Bf in [('X20','SAME20'),('X20','REC20')]:
    L=np.log(np.r_[cue(A,'lapvar_box'),cue(Bf,'lapvar_box')]); P=np.log(np.r_[cue(A,'png_bytes'),cue(Bf,'png_bytes')]); lab=np.r_[np.ones(536),np.zeros(536)]
    print(A,Bf,'lap oriented',round(max(auc(L[:536],L[536:]),1-auc(L[:536],L[536:])),3),'png oriented',round(max(auc(P[:536],P[536:]),1-auc(P[:536],P[536:])),3))
    for T in ['a_s401','a_s402','e_s401','e_s402','f_s401','f_s402']:
        z=np.load(f'{D}/SM1D_{T}/scores_audit.npz'); p=np.clip(z['score_noTTA'].astype(float),1e-7,1-1e-7)
        s=dict(zip([str(i) for i in z['id']],np.log(p/(1-p))))
        sc=np.r_[[s[r['id']] for r in fam[A]],[s[r['id']] for r in fam[Bf]]]
        print(' ',T,'raw',round(auc(sc[:536],sc[536:]),3),'lap-strat',round(strat(sc,L,lab),3),'png-strat',round(strat(sc,P,lab),3))
