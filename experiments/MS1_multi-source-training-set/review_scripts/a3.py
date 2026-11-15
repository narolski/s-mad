import csv, io, tarfile, numpy as np, itertools, collections
R='/mnt/t7/smad_next/MS1/results_rented/'
M=list(csv.DictReader(open('/mnt/t7/smad_next/MS1/pack_tree/pn1/data/manifests/pn1_eval.csv')))
H=list(csv.DictReader(open('/mnt/t7/smad_next/MS1/heldout_tree/pn1/data/manifests/ms1_heldout.csv')))
def mw(x,y):
    def U(a,b): return sum((ai<bi)+0.5*(ai==bi) for ai in a for bi in b)
    u=U(x,y);p=x+y;c=t=0
    for idx in itertools.combinations(range(10),5):
        a=[p[i] for i in idx];b=[p[i] for i in range(10) if i not in idx];t+=1;c+=U(a,b)>=u-1e-12
    return u,c/t
def load(arm,s):
    with tarfile.open(f'{R}MS1_{arm}_s{s}.tar') as t:
        m=[x for x in t.getmembers() if x.name.endswith('scores_eval.npz')][0]
        z=np.load(io.BytesIO(t.extractfile(m).read()))
    L=dict(zip(map(str,z['id']),z['logit'].astype(float)))
    z=np.load(f'{R}heldout/MS1H_{arm}_s{s}_cfd.npz'); C=dict(zip(map(str,z['id']),z['logit'].astype(float)))
    return L,C
cfdrows=[r for r in H if r['fam']=='cfd']
def grp(r):
    h=r['host'].split(':')[1]; p=h.split('-')
    return p[0] if p[0]!='CFD' else 'CFD-'+p[1][:1]+p[1][1:]  # e.g CFD-AF
sub=collections.defaultdict(list)
for r in cfdrows:
    h=r['host'].split(':')[1]
    if h.startswith('CFD-IND') or 'INDIA' in h: g='INDIA'
    elif h.startswith('CFD-MR') or '-MR' in h: g='MR'
    else: g='CFD-'+h.split('-')[1]
    sub[g].append(r['id'])
print({k:len(v) for k,v in sub.items()})
print(cfdrows[600]['host'],cfdrows[700]['host'],cfdrows[800]['host'])
D={}
for arm in ('Sb','SbM3','SbV'):
  for s in (403,404,405,406,407):
    L,C=load(arm,s)
    cam=[L[r['id']] for r in M if r['role']=='dev' and r['strength']=='' and ((r['fam']=='ladder' and r['rung']=='R0') or (r['fam']=='af0' and r['rung']=='photo'))]
    camt=[L[r['id']] for r in M if r['role']=='test' and r['fam']=='ladder' and r['rung']=='R0' and r['strength']=='']
    lcm=np.array([L[r['id']] for r in M if r['rung']=='landmark_combined_orig']);lcc=np.array([L[r['id']] for r in M if r['rung']=='landmark_complete_orig'])
    hn2=np.array([L[r['id']] for r in M if r['rung']=='ffhq_bona_orig']); rm=np.array([L[r['id']] for r in M if r['rung']=='landmark_complete_resmatch'])
    D[(arm,s)]=dict(cam_flag=np.mean(np.array(cam)>0),camt_flag=np.mean(np.array(camt)>0),lcomb_miss=np.mean(lcm<=0),lcomp_miss=np.mean(lcc<=0),
       lcomp_auc_vs_hn2=None, ffhq_bona_flag=np.mean(hn2>0), resmatch_flag=np.mean(rm>0),
       cfd_flagged=set(k for k,v in C.items() if v>0), **{f'cfd_{g}':np.mean([C[i]>0 for i in ids]) for g,ids in sub.items()})
for k in ['cam_flag','camt_flag','lcomb_miss','lcomp_miss','ffhq_bona_flag','resmatch_flag']+[f'cfd_{g}' for g in sorted(sub)]:
    v={a:[D[(a,s)][k] for s in (403,404,405,406,407)] for a in ('Sb','SbM3','SbV')}
    print(f"{k:14s}", ' | '.join(f"{a} "+' '.join(f'{x:.3f}' for x in v[a]) for a in v), ' MW SbM3>Sb' if k.endswith('miss') else ' MW SbM3<Sb', mw(v['Sb'],v['SbM3']) if k.endswith('miss') else mw(v['SbM3'],v['Sb']))
# overlap of flagged CFD across Sb seeds
fl=[D[('Sb',s)]['cfd_flagged'] for s in (403,404,405,406,407)]
c=collections.Counter(i for f in fl for i in f); print('Sb CFD flagged union',len(c),'in all5',sum(v==5 for v in c.values()),'>=3',sum(v>=3 for v in c.values()))
m3=set().union(*[D[('SbM3',s)]['cfd_flagged'] for s in (403,404,405,406,407)]); print('SbM3 flagged union',m3, 'in Sb union', len(m3&set(c)))
hosts={r['id']:r['host'] for r in cfdrows}
print('Sb all-5 flagged hosts', sorted(hosts[i] for i,v in c.items() if v==5)[:40])
