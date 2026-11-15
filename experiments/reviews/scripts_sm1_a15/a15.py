import csv, numpy as np, hashlib, glob, json
from scipy.stats import spearmanr, rankdata
D='/mnt/t7/smad_next/SM1/results_rented/dev'
rows=list(csv.DictReader(open('/mnt/t7/smad_next/SM1/dev_a14/sm1_dev_eval.csv')))
fz={r['id']:r for r in csv.DictReader(open('/mnt/t7/smad_next/FZ2/read_addon_items.csv'))}
def fzid(p):
    p=p[1:] if p.startswith('x') else p
    return p.split('/addon_s')[0].split('/gen/')[1] if False else p.split('/gen/')[1].split('/',1)[1]
def auc(a,b):
    r=rankdata(np.r_[a,b]); return (r[:len(a)].sum()-len(a)*(len(a)+1)/2)/(len(a)*len(b))
fam={}
for r in rows: fam.setdefault(r['family'],[]).append(r)
X=fam['X20']; REC=fam['REC20']; SAME=fam['SAME20']
cue={}
for r in X+REC+SAME:
    k=fzid(r['path']); cue[r['id']]=fz.get(k)
print('cue matched', sum(v is not None for v in cue.values()), len(cue))
def cv(ids,c): return np.array([float(cue[i][c]) for i in ids])
Xi=[r['id'] for r in X]; Ri=[r['id'] for r in REC]; Si=[r['id'] for r in SAME]
for c in ['lapvar_box','png_bytes','asym_box','d','smdd_s401','release_fe_vitl14']:
    try: print(c,'AUC X>REC',round(auc(cv(Xi,c),cv(Ri,c)),3),'med X',np.median(cv(Xi,c)).round(2),'REC',np.median(cv(Ri,c)).round(2),'SAME',np.median(cv(Si,c)).round(2))
    except Exception as e: print(c,e)
# host pairing
hX={r['variant']:r['id'] for r in X}; hR={r['variant']:r['id'] for r in REC}
hosts=sorted(set(hX)&set(hR)); print('paired hosts',len(hosts))
out={}
for f in sorted(glob.glob(D+'/SM1D_*.tar')):
    T=f.split('/')[-1][:-4]
    assert hashlib.sha256(open(f,'rb').read()).hexdigest()==open(f+'.sha256').read().split()[0]
    z=np.load(f'{D}/{T}/scores_audit.npz'); p=np.clip(z['score_noTTA'].astype(float),1e-7,1-1e-7)
    s=dict(zip([str(i) for i in z['id']],np.log(p/(1-p))))
    g=lambda ids: np.array([s[i] for i in ids])
    R0=[r['id'] for r in fam['ar1:frgcferet:none:R0']]
    o=dict(native=auc(g(Xi),g(R0)),hm=auc(g(Xi),g(Ri)),same_vs_rec=auc(g(Si),g(Ri)),x_vs_same=auc(g(Xi),g(Si)))
    xs=np.array([s[hX[h]] for h in hosts]); rs=np.array([s[hR[h]] for h in hosts])
    o['paired_share_X_gt_REC']=float(((xs>rs)+0.5*(xs==rs)).mean())
    lx=np.array([float(cue[hX[h]]['lapvar_box']) for h in hosts]); lr=np.array([float(cue[hR[h]]['lapvar_box']) for h in hosts])
    o['paired_lap_X_gt_REC']=float((lx>lr).mean())
    o['rho_dscore_dloglap']=spearmanr(xs-rs,np.log(lx)-np.log(lr))[0]
    allid=Xi+Ri; L=np.log(cv(allid,'lapvar_box')); sc=g(allid)
    o['rho_score_loglap_pooled']=spearmanr(sc,L)[0]
    o['rho_in_X']=spearmanr(g(Xi),np.log(cv(Xi,'lapvar_box')))[0]; o['rho_in_REC']=spearmanr(g(Ri),np.log(cv(Ri,'lapvar_box')))[0]
    # residualise score on log lap (pooled linear) then AUC
    A=np.c_[np.ones_like(L),L]; beta=np.linalg.lstsq(A,sc,rcond=None)[0]; res=sc-A@beta
    o['auc_resid_lap']=auc(res[:len(Xi)],res[len(Xi):])
    # quintile-stratified AUC
    q=np.quantile(L,[.2,.4,.6,.8]); b=np.digitize(L,q); lab=np.r_[np.ones(len(Xi)),np.zeros(len(Ri))]
    num=den=0
    for k in range(5):
        m=b==k; a1=sc[m&(lab==1)]; a0=sc[m&(lab==0)]
        if len(a1) and len(a0): w=len(a1)*len(a0); num+=auc(a1,a0)*w; den+=w
    o['auc_strat_lap5']=num/den
    # H-new-E pieces: paired AUC
    for st in ('amsl112','fm61'):
        rs_=fam[f'R0_soft_{st}']; inc=np.array([s[r['id']]-s[r['src_id']] for r in rs_])
        o[f'inc_{st}']=inc.mean(); o[f'truepaired_{st}']=float(((inc>0)+0.5*(inc==0)).mean())
        o[f'unpaired_{st}']=auc(g([r['id'] for r in rs_]),g([r['src_id'] for r in rs_]))
    R4=[r['id'] for r in fam['ar1:frgcferet:opencv:R4']]; o['R4_vs_R0']=auc(g(R4),g(R0)); o['X_vs_R4']=auc(g(Xi),g(R4))
    o['median_logit']={k:float(np.median(g(v))) for k,v in dict(X=Xi,REC=Ri,SAME=Si,R0=R0,R4=R4).items()}
    out[T]={k:(round(float(v),4) if not isinstance(v,dict) else {a:round(b,2) for a,b in v.items()}) for k,v in o.items()}
for T,o in out.items(): print(T,json.dumps(o))
