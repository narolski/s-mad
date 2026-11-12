import csv, numpy as np, collections
def load(f): return list(csv.DictReader(open(f)))
a=load('/mnt/t7/smad_next/FZ2/read_addon_items.csv'); p=load('/mnt/t7/smad_next/FZ2/read_prod_items.csv')
print(len(a),len(p))
c=collections.Counter((r['rung'],r['steps']) for r in a); print(sorted(c.items()))
c=collections.Counter((r['rung'],r['steps']) for r in p); print(sorted(c.items()))
print(collections.Counter((r['platform'],r['db']) for r in a if r['rung']=='REC' and r['steps']=='20'))
for rung in ['REC','SAME','X','MIR']:
    A={(r['host'],r['partner']):r for r in a if r['rung']==rung and r['steps']=='20'}
    P={(r['host'],r['partner']):r for r in p if r['rung']==rung and r['steps']=='20'}
    k=sorted(set(A)&set(P))
    pe=np.mean([A[x]['png_bytes']==P[x]['png_bytes'] for x in k])
    for col in ['lapvar_box','smdd_s401','clip_mad|P_XS']:
        va=np.array([float(A[x][col]) for x in k]); vp=np.array([float(P[x][col]) for x in k])
        print(rung,len(A),len(P),len(k),'png_eq',round(pe,3),col,'maxabs',np.nanmax(np.abs(va-vp)),'corr',np.corrcoef(va,vp)[0,1])
print('--- png equality by platform/db')
for rung in ['REC','X']:
    A={(r['host'],r['partner']):r for r in a if r['rung']==rung and r['steps']=='20'}
    P={(r['host'],r['partner']):r for r in p if r['rung']==rung and r['steps']=='20'}
    cc=collections.Counter((A[x]['platform'],A[x]['db'],A[x]['list'],A[x]['png_bytes']==P[x]['png_bytes']) for x in A)
    for k in sorted(cc): print(rung,k,cc[k])
