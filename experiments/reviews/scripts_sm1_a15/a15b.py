import csv, numpy as np, glob
from scipy.stats import spearmanr, rankdata
D='/mnt/t7/smad_next/SM1/results_rented/dev'
rows=list(csv.DictReader(open('/mnt/t7/smad_next/SM1/dev_a14/sm1_dev_eval.csv')))
fz={r['id']:r for r in csv.DictReader(open('/mnt/t7/smad_next/FZ2/read_addon_items.csv'))}
fzid=lambda p:(p[1:] if p.startswith('x') else p).split('/gen/')[1].split('/',1)[1]
fam={}
for r in rows: fam.setdefault(r['family'],[]).append(r)
hosts=sorted({r['variant'] for r in fam['X20']}); hp={h:i for i,h in enumerate(hosts)}
rng=np.random.default_rng(20261111); B=2000
C=rng.multinomial(len(hosts),np.full(len(hosts),1/len(hosts)),size=B).astype(float)
def wauc(a,b,wa,wb):
    # weighted AUC via sorting
    v=np.r_[a,b]; o=np.argsort(v,kind='mergesort'); v=v[o]
    lab=np.r_[np.ones(len(a)),np.zeros(len(b))][o]
    W=np.c_[wa,wb][:,o]
    # ties ignored (continuous)
    cb=np.cumsum(W*(1-lab),1)
    num=(W*lab*cb).sum(1); return num/(wa.sum(1)*wb.sum(1))
def ids(f): return [r['id'] for r in fam[f]]
def hw(f): return C[:,[hp[r['variant']] for r in fam[f]]]
res={}
for f in sorted(glob.glob(D+'/SM1D_*.tar')):
    T=f.split('/')[-1][:-4]; z=np.load(f'{D}/{T}/scores_audit.npz'); p=np.clip(z['score_noTTA'].astype(float),1e-7,1-1e-7)
    s=dict(zip([str(i) for i in z['id']],np.log(p/(1-p)))); g=lambda f_: np.array([s[i] for i in ids(f_)])
    d={}
    for nm,(A,Bf) in dict(XvREC=('X20','REC20'),XvSAME=('X20','SAME20'),SAMEvREC=('SAME20','REC20'),RECvR0=('REC20','ar1:frgcferet:none:R0'),SAMEvR0=('SAME20','ar1:frgcferet:none:R0')).items():
        d[nm]=wauc(g(A),g(Bf),hw(A),hw(Bf)); d[nm+'_pt']=wauc(g(A),g(Bf),np.ones((1,len(ids(A)))),np.ones((1,len(ids(Bf)))))[0]
    pb=lambda f_: np.array([float(fz[fzid(r['path'])]['png_bytes']) for r in fam[f_]])
    lp=lambda f_: np.array([float(fz[fzid(r['path'])]['lapvar_box']) for r in fam[f_]])
    d['rho_png_inX']=spearmanr(g('X20'),pb('X20'))[0]; d['rho_png_inREC']=spearmanr(g('REC20'),pb('REC20'))[0]
    sc=np.r_[g('X20'),g('REC20')]; P=np.log(np.r_[pb('X20'),pb('REC20')]); L=np.log(np.r_[lp('X20'),lp('REC20')])
    A_=np.c_[np.ones_like(P),P,L]; r_=sc-A_@np.linalg.lstsq(A_,sc,rcond=None)[0]
    n=len(ids('X20')); d['XvREC_resid_png_lap']=wauc(r_[:n],r_[n:],np.ones((1,n)),np.ones((1,n)))[0]
    res[T]=d
arms={}
for T,d in res.items(): arms.setdefault(T.split('_')[1],[]).append(d)
ci=lambda x: np.round(np.percentile(x,[2.5,97.5]),3)
for a,L in arms.items():
    print(a, {k:round(float(np.mean([d[k+'_pt'] for d in L])),3) for k in ['XvREC','XvSAME','SAMEvREC','RECvR0','SAMEvR0']},
          'XvSAME ci',ci(np.mean([d['XvSAME'] for d in L],0)),
          'rho_png X/REC',[round(d['rho_png_inX'],3) for d in L],[round(d['rho_png_inREC'],3) for d in L],'resid AUC',[round(d['XvREC_resid_png_lap'],3) for d in L])
for k in ['XvREC','XvSAME','SAMEvREC']:
    for b in ['e','f']:
        dd=np.mean([d[k] for d in arms['a']],0)-np.mean([d[k] for d in arms[b]],0)
        print(k,'a-'+b, round(float(dd.mean()),3), ci(dd))
# png/lap AUC X vs SAME, SAME vs REC
from scipy.stats import rankdata
def auc(a,b):
    r=rankdata(np.r_[a,b]); return (r[:len(a)].sum()-len(a)*(len(a)+1)/2)/(len(a)*len(b))
for c in ['png_bytes','lapvar_box']:
    v=lambda f_: np.array([float(fz[fzid(r['path'])][c]) for r in fam[f_]])
    print(c,'XvSAME',round(auc(v('X20'),v('SAME20')),3),'SAMEvREC',round(auc(v('SAME20'),v('REC20')),3))
