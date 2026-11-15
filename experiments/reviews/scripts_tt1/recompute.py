import csv, json, numpy as np, sys
from scipy.stats import rankdata, mannwhitneyu
S='/mnt/t7/smad_next/TT1/results/unpacked_tt1c/TT1_A100_tt1c_full/scores/'
lst=list(csv.DictReader(open('/mnt/t7/smad_next/TT1/tt1_score.csv')))
raw={r['id']:r for r in csv.DictReader(open('/mnt/t7/smad_next/TT1/raw_manifest.csv'))}
al={r['id']:r for r in csv.DictReader(open('/mnt/t7/smad_next/TT1/aligned_manifest.csv'))}
AS=['replay_attack','msu_mfsd','oulu_npu','casia_fasd']
SRC=AS+['lfw','calfw','cfp_ff','agedb_30']
def prim(i):
    a=al[i]; s=a['source']; lo,hi=(1.2,2.5) if s in AS else (2.5,5.0)
    return a['aligned']=='1' and lo<=float(a['enlarge'])<=hi
pools={}
for r in lst:
    k=r['rung']
    if r['fam']=='gate': pools.setdefault(k,[]).append(r['id'])
    elif k in SRC:
        if prim(r['id']): pools.setdefault('U:'+k,[]).append(r['id'])
    elif k=='R_cam_border': pools.setdefault('Rcb:'+r['cell'],[]).append(r['id'])
    elif k=='R_ffhq_border': pools.setdefault('Rfb',[]).append(r['id'])
    else: pools.setdefault(k,[]).append(r['id'])
print({k:len(v) for k,v in pools.items()})
def auc(p,n):
    p=np.asarray(p);n=np.asarray(n)
    r=rankdata(np.concatenate([p,n])); return (r[:len(p)].sum()-len(p)*(len(p)+1)/2)/(len(p)*len(n))
FAM={'lfw_calfw':['lfw','calfw']}
FAMS=AS+['lfw_calfw','cfp_ff','agedb_30']
nets=[f'PN1_{a}_s{s}' for a in ('A','B','Sb','C','Bv','Bn') for s in (401,402) if not (a=='Bn' and s==401)]
out={}
for n in nets:
    L={}
    for f in ('gate','tt1'):
        z=np.load(S+f'{n}__{f}.npz'); L.update(zip(z['id'].tolist(),z['logit'].astype(float).tolist()))
    g=lambda p: np.array([L[i] for i in pools[p]])
    fam={f: np.mean(np.concatenate([g('U:'+s) for s in FAM.get(f,[f])])>0) for f in FAMS}
    src={s: np.mean(g('U:'+s)>0) for s in SRC}
    A={s: auc(g('U:'+s),g('R_cam')) for s in SRC}
    Ag={s: auc(g('U:'+s),g('R_cam_geo224' if s in AS else 'R_cam_geo112')) for s in SRC}
    Ac={s: auc(g('U:'+s),g('Rcb:'+('lfw_calfw' if s in ('lfw','calfw') else s))) for s in SRC}
    e={f: auc(g('Rcb:'+f),g('R_cam')) for f in FAMS}
    fgeo={k: auc(g(k),g('R_cam')) for k in ('R_cam_geo224','R_cam_geo112')}
    d=auc(g('Rfb'),g('R_ffhq'))
    cam=g('R_cam'); 
    out[n]=dict(Fbar=np.mean(list(fam.values())),Fmax=max(fam.values()),fam=fam,src=src,A=A,Ag=Ag,Ac=Ac,e=e,d=d,fgeo=fgeo,
      cam_flag=np.mean(cam>0),cam_med=np.median(cam),cam_q=np.percentile(cam,[5,50,95]).tolist(),cam_max=cam.max(),
      ffhq_flag=np.mean(g('R_ffhq')>0),mffhq_flag=np.mean(g('M_ffhq')>0),mffhq_med=np.median(g('M_ffhq')),
      Umed={s:np.median(g('U:'+s)) for s in SRC}, Uq={s:np.percentile(g('U:'+s),[10,50,90]).tolist() for s in SRC},
      geomed={k:np.median(g(k)) for k in ('R_cam_geo224','R_cam_geo112')},
      geoflag={k:np.mean(g(k)>0) for k in ('R_cam_geo224','R_cam_geo112')},
      cbflag={f:np.mean(g('Rcb:'+f)>0) for f in FAMS}, cbmed={f:np.median(g('Rcb:'+f)) for f in FAMS},
      ffhqmed=np.median(g('R_ffhq')), rfbmed=np.median(g('Rfb')), rfbflag=np.mean(g('Rfb')>0))
json.dump(out,open(sys.argv[1],'w'),default=float,indent=1)
for n,o in out.items():
    print(n,'Fbar %.3f Fmax %.3f cam %.3f camq %s ffhq %.3f Mffhq %.3f'%(o['Fbar'],o['Fmax'],o['cam_flag'],np.round(o['cam_q'],3),o['ffhq_flag'],o['mffhq_flag']))
    print('  fam',{k:round(v,3) for k,v in o['fam'].items()})
    print('  src',{k:round(v,3) for k,v in o['src'].items()})
    print('  A',{k:round(v,3) for k,v in o['A'].items()})
    print('  Ag',{k:round(v,3) for k,v in o['Ag'].items()},' fgeo',{k:round(v,3) for k,v in o['fgeo'].items()})
    print('  Ac',{k:round(v,3) for k,v in o['Ac'].items()},' e',{k:round(v,2) for k,v in o['e'].items()},'d %.3f'%o['d'])
    print('  Umed',{k:round(v,2) for k,v in o['Umed'].items()},'geomed',{k:round(v,2) for k,v in o['geomed'].items()},'geoflag',o['geoflag'])
    print('  cbmed',{k:round(v,2) for k,v in o['cbmed'].items()},'cbflag',{k:round(v,3) for k,v in o['cbflag'].items()})
