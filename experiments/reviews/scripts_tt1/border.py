import csv, numpy as np
S='/mnt/t7/smad_next/TT1/results/unpacked_tt1c/TT1_A100_tt1c_full/scores/'
lst=list(csv.DictReader(open('/mnt/t7/smad_next/TT1/tt1_score.csv')))
al={r['id']:r for r in csv.DictReader(open('/mnt/t7/smad_next/TT1/aligned_manifest.csv'))}
FAMS=['replay_attack','msu_mfsd','oulu_npu','casia_fasd','lfw_calfw','cfp_ff','agedb_30']
cam=sorted([r['id'] for r in lst if r['rung']=='R_cam'])
# border refs: id pattern? map to cam id
cb=[r for r in lst if r['rung']=='R_cam_border']; print(cb[0])
geo=[r for r in lst if r['rung']=='R_cam_geo112']; print(geo[0])
rfb=[r for r in lst if r['rung']=='R_ffhq_border']
AS=FAMS[:4]
U={f:[] for f in FAMS}
for r in lst:
    if r['fam']=='tt1' and r['rung'] in AS+['lfw','calfw','cfp_ff','agedb_30']:
        a=al[r['id']]; lo,hi=(1.2,2.5) if r['rung'] in AS else (2.5,5.0)
        if a['aligned']=='1' and lo<=float(a['enlarge'])<=hi: U['lfw_calfw' if r['rung'] in ('lfw','calfw') else r['rung']].append(r['id'])
fq={r['id'] for r in lst if r['rung']=='R_ffhq'}
for n in [f'PN1_{a}_s{s}' for a in ('A','B','Sb') for s in (401,402)]:
    L={}
    for f in ('gate','tt1'):
        z=np.load(S+f'{n}__{f}.npz'); L.update(zip(z['id'].tolist(),z['logit'].astype(float).tolist()))
    cm=np.median([L[i] for i in cam])
    row=[]
    for f in FAMS:
        ex=np.median([L[i] for i in U[f]])-cm
        bs=np.median([L[r['id']]-L[r['id'][5:].split('__')[0]] for r in cb if r['cell']==f])
        row.append(f"{f[:5]} ex {ex:.2f} bord {bs:.2f}")
    g112=np.median([L[r['id']]-L[r['strength']] for r in geo]); 
    g224=np.median([L[r['id']]-L[r['strength']] for r in lst if r['rung']=='R_cam_geo224'])
    ffs=np.median([L[r['id']]-L[r['id'][5:]] for r in rfb]); ffp=np.mean([L[r['id']]>0 for r in rfb]); ff0=np.mean([L[r['id'][5:]]>0 for r in rfb])
    print(n,' | '.join(row)); print('    geo224 paired %.2f geo112 paired %.2f | ffhq border paired med %.3f flag %.3f->%.3f'%(g224,g112,ffs,ff0,ffp))
