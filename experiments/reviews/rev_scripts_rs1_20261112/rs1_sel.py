import csv, numpy as np
R='/mnt/t7/smad_next/RS1/results_rented/'
man={r['id']:r for r in csv.DictReader(open('/mnt/t7/smad_next/RS1/athena/athena_manifest.csv'))}
def load(det,v):
    z=np.load(f'{R}prod_{v}_rented/scores/scores_rel_{det}__{v}.npz')
    d={}
    for i,l in zip(z['id'].tolist(), z['logit_noTTA']):
        r=man[i]
        if r['origin']=='check' or r['origin']=='a46': continue
        d[i]=(r['set'],float(l))
    return d
def eer(g,m):
    g=np.asarray(g);m=np.asarray(m); t=np.unique(np.concatenate([g,m])); best=(9,0)
    for x in t:
        fpr=(g>=x).mean(); fnr=(m<x).mean()
        if abs(fpr-fnr)<best[0]: best=(abs(fpr-fnr),(fpr+fnr)/2)
    return 100*best[1]
def auc(p,n):
    p=np.asarray(p)[:,None]; n=np.asarray(n)[None,:]
    return ((p>n).mean()+0.5*(p==n).mean())
for det in ['madation_vitb16','mixfacenet_mad_smdd','madation_vitl14']:
    v1=load(det,'v1'); v2=load(det,'v2'); keep=set(v1)
    S=lambda d,s,ids=None:[l for i,(st,l) in d.items() if st==s and (ids is None or i in ids)]
    print(det)
    for cell in ['M_facemorpher','M_mordiff','M_opencv']:
        print(' ',cell,'v2 all %.2f  v2 on v1-kept %.2f  v1 %.2f'%(eer(S(v2,'G_raw'),S(v2,cell)),eer(S(v2,'G_raw'),S(v2,cell,keep)),eer(S(v1,'G_raw'),S(v1,cell))))
    for a,b in [('a43_E','G_raw'),('a43_D20','a43_E'),('a43_B20','a43_D20'),('a43_A','a43_B20')]:
        print(' ',a,'vs',b,'v2 all %.3f  v2 on v1-kept %.3f  v1 %.3f'%(auc(S(v2,a),S(v2,b)),auc(S(v2,a,keep),S(v2,b,keep)),auc(S(v1,a),S(v1,b))))
    # median logit per pool
    for s in ['G_raw','Galn_frll','a43_E','a43_D20','a43_B20','E7raw_mordiff','M_mordiff']:
        print('   median',s,'v1 %.2f v2 %.2f'%(np.median(S(v1,s)),np.median(S(v2,s))))
print('=== spread')
for det in ['madation_vitb16','madation_vitl14','mixfacenet_mad_smdd']:
    v1=load(det,'v1')
    for s in ['G_raw','M_mordiff','a43_E','a43_D20','E7raw_mordiff','Galn_mordiff','M_dim_a','FF_orig','FEI_neutral']:
        x=np.array([l for i,(st,l) in v1.items() if st==s])
        if len(x): print(det[:12],s,len(x),'q05 %.2f q50 %.2f q95 %.2f sd %.3f'%(*np.quantile(x,[.05,.5,.95]),x.std()))
