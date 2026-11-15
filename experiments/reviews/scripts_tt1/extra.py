import csv, numpy as np
from scipy.stats import beta
S='/mnt/t7/smad_next/TT1/results/unpacked_tt1c/TT1_A100_tt1c_full/scores/'
lst=list(csv.DictReader(open('/mnt/t7/smad_next/TT1/tt1_score.csv')))
al={r['id']:r for r in csv.DictReader(open('/mnt/t7/smad_next/TT1/aligned_manifest.csv'))}
AS=['replay_attack','msu_mfsd','oulu_npu','casia_fasd']; FAMS=AS+['lfw_calfw','cfp_ff','agedb_30']
def fam(r): return 'lfw_calfw' if r['rung'] in ('lfw','calfw') else r['rung']
U={f:[] for f in FAMS}; Ual={f:[] for f in FAMS}; host={}
for r in lst:
    if r['fam']=='tt1' and r['rung'] in AS+['lfw','calfw','cfp_ff','agedb_30']:
        a=al[r['id']]; lo,hi=(1.2,2.5) if r['rung'] in AS else (2.5,5.0)
        if a['aligned']=='1':
            Ual[fam(r)].append(r['id'])
            if lo<=float(a['enlarge'])<=hi: U[fam(r)].append(r['id'])
geo=[r['id'] for r in lst if r['rung']=='R_cam_geo112']; geo224=[r['id'] for r in lst if r['rung']=='R_cam_geo224']
cam=[r['id'] for r in lst if r['rung']=='R_cam']; ff=[r['id'] for r in lst if r['rung']=='R_ffhq']
nets=[f'PN1_{a}_s{s}' for a in ('A','B','Bv','Sb','C') for s in (401,402)]+['PN1_Bn_s402']
def cp(k,n): return (0 if k==0 else beta.ppf(.025,k,n-k+1), 1 if k==n else beta.ppf(.975,k+1,n-k))
Lall={}
for n in nets:
    L={}
    for f in ('gate','tt1'):
        z=np.load(S+f'{n}__{f}.npz'); L.update(zip(z['id'].tolist(),z['logit'].astype(float).tolist()))
    Lall[n]=L
    g=lambda ids: np.array([L[i] for i in ids])
    allU=np.concatenate([g(U[f]) for f in FAMS])
    Fb=lambda t,P=U: np.mean([np.mean(g(P[f])>t) for f in FAMS])
    cpu=max(cp(int((g(U[f])>0).sum()),len(U[f]))[1] for f in FAMS)
    print(n,'F>0 %.3f F>-0.5 %.3f F>-1 %.3f F>-2 %.3f | F(aligned-all,MS1 pool) %.4f | maxCPupper %.3f | geo112 flag %.3f med %.2f geo224 flag %.3f | ffhq>0 %.3f | U p95 %.2f p99 %.2f'%(
      Fb(0),Fb(-0.5),Fb(-1),Fb(-2),Fb(0,Ual),cpu,np.mean(g(geo)>0),np.median(g(geo)),np.mean(g(geo224)>0),np.mean(g(ff)>0),np.percentile(allU,95),np.percentile(allU,99)))
# paired geo112 vs cam shift per image
for n in nets:
    L=Lall[n]
    gm={r['host']:None for r in lst}
print('n geo',len(geo))
# Sb-B at various thresholds
for t in (0,-0.5,-1,-2):
    for s in (401,402):
        d=[]
        for a in ('Sb','B','Bv'):
            L=Lall[f'PN1_{a}_s{s}']; d.append(np.mean([np.mean(np.array([L[i] for i in U[f]])>t) for f in FAMS]))
        print('t',t,'s',s,'Sb-B %.3f Sb-Bv %.3f Bv-B %.3f'%(d[0]-d[1],d[0]-d[2],d[2]-d[1]))
