import csv, sys, json, numpy as np, pathlib
from sklearn.metrics import roc_auc_score, roc_curve
B = pathlib.Path('/mnt/t7/smad_next/PN1')
rows = list(csv.DictReader(open(B/'manifests/pn1_eval.csv')))
P = {}
def add(n, r): P.setdefault(n, []).append(r['id'])
for r in rows:
    st = ('_'+r['strength']) if r['strength'] else ''
    if r['fam']=='ladder':
        pre = 'T_' if r['role']=='test' else 'D_'
        tool = '' if r['rung']=='R0' else '_'+r['tool']
        add(f"{pre}{r['rung']}{tool}{st}", r)
    elif r['fam']=='af0':
        rung = 'half' if r['rung'] in ('halfA','halfB') else r['rung']
        add(f"V_{rung}{st}", r)
    elif r['fam']=='bench':
        cell=r['cell']; src='FRLL' if cell.startswith('frllm') else 'MAD22'
        if cell=='frllm_frll_bona' or cell.endswith('_bona'):
            add(f"{src}_bona_{'native' if r['rung']=='orig' else r['rung']}", r)
        else:
            fam=cell.split('_',1)[1]; add(f"{src}_{fam}_{'morph' if r['klass']=='attack' else 'e7'}", r)
    elif r['fam']=='h1':
        add(f"H1_{'morph' if r['klass']=='attack' else 'bona'}", r)
host = {r['id']: r['host'] for r in rows}
def thr(s, a=0.05):
    s=np.sort(s); n=len(s)
    for t in s:
        if (s>t).mean()<=a: return t
def eer(p, n):
    y=np.r_[np.ones(len(p)),np.zeros(len(n))]; f,t,_=roc_curve(y,np.r_[p,n]); fnr=1-t; i=np.nanargmin(abs(fnr-f)); return 100*(f[i]+fnr[i])/2
def load(path):
    z=np.load(path); return dict(zip([str(i) for i in z['id']], z['logit'].astype(float)))
def S_(S,n): return np.array([S[i] for i in P[n]])
def auc(S,pos,neg): 
    p,n=S_(S,pos),S_(S,neg); return roc_auc_score(np.r_[np.ones(len(p)),np.zeros(len(n))],np.r_[p,n])
def read(S):
    o={}
    tcam=max(thr(S_(S,'D_R0')),thr(S_(S,'V_photo'))); o['tcam']=tcam
    o['tcam_D']=thr(S_(S,'D_R0')); o['tcam_V']=thr(S_(S,'V_photo'))
    o['R2w_R4']=auc(S,'T_R4_opencv','T_R2w_opencv'); o['R2w4_R4']=auc(S,'T_R4_opencv','T_R2w4_opencv')
    o['R0_61_R4']=auc(S,'T_R4_opencv','T_R0_61'); o['R2w61_R4']=auc(S,'T_R4_opencv','T_R2w_opencv_61')
    a={host[i]:S[i] for i in P['T_R0']}; b={host[i]:S[i] for i in P['T_R0_61']}; c={host[i]:S[i] for i in P['T_R0_112']}
    hs=sorted(set(a)&set(b)); d=np.array([b[h]-a[h] for h in hs]); sd=np.std([a[h] for h in hs],ddof=1)
    o['shift61']=d.mean(); o['sdR0']=sd; o['shift61_sd']=d.mean()/sd; o['share_rising61']=(d>0).mean()
    d2=np.array([c[h]-a[h] for h in hs]); o['shift112']=d2.mean(); o['shift112_sd']=d2.mean()/sd
    o['R0_mean']=np.mean(list(a.values()))
    o['H1']=auc(S,'H1_morph','H1_bona')
    for f in ('OpenCV','Webmorph'):
        o[f'EER_{f}_e7']=eer(S_(S,f'MAD22_{f}_morph'),S_(S,f'MAD22_{f}_e7'))
        o[f'EER_{f}_nat']=eer(S_(S,f'MAD22_{f}_morph'),S_(S,'MAD22_bona_native'))
    for th,t in (('own',0.0),('cam',tcam)):
        for p in ('T_R0','T_R0_61','T_R0_112','FRLL_bona_native','FRLL_bona_jpeg70','FRLL_bona_jpeg50','FRLL_bona_blur1','FRLL_bona_resample50','MAD22_bona_native','MAD22_OpenCV_e7','MAD22_Webmorph_e7','H1_bona','V_photo','D_R0'):
            o[f'{th}_flag_{p}']=100*(S_(S,p)>t).mean()
        ms=[100*(S_(S,c)<=t).mean() for c in ('T_R4_opencv','MAD22_OpenCV_morph','MAD22_Webmorph_morph','H1_morph')]
        o[f'{th}_miss']=ms; o[f'{th}_fammiss']=np.mean(ms)
    # pool medians
    for p in ('D_R0','V_photo','T_R0','T_R0_61','FRLL_bona_native','MAD22_bona_native','H1_bona','T_R2w_opencv','T_R4_opencv','MAD22_OpenCV_morph','H1_morph'):
        x=S_(S,p); o[f'med_{p}']=(np.percentile(x,5),np.median(x),np.percentile(x,95))
    return o
if __name__=='__main__':
    out={}
    for arm in ('A','B','Bn','C'):
        for s in (401,402):
            out[f'{arm}_{s}']=read(load(B/f'results_rented/unpacked/PN1_{arm}_s{s}/scores_eval.npz'))
    for k in range(1,9):
        out[f'REF_{k}']=read(load(B/f'results_rented/unpacked/PN1_REF_smdd_m3/a12_clip_vitb16_madation_r224_d0_train90_none_lr3.33e-06_s{k}_r/scores_eval.npz'))
    import pickle; pickle.dump(out,open(sys.argv[1],'wb'))
    keys=[k for k in out['A_401'] if not k.startswith('med_')]
    for k in keys:
        print(k.ljust(28), ' '.join((f'{v:7.3f}' if not isinstance(v,list) else '/'.join(f'{x:.1f}' for x in v)) for v in [out[n][k] for n in out]))
