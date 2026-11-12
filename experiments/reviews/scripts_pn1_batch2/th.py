import tarfile, io, csv, numpy as np
from scipy.stats import spearmanr
fy=np.fft.fftfreq(256)[:,None]; fx=np.fft.fftfreq(256)[None,:]; R=np.sqrt(fx**2+fy**2)
B=[(0,1/32),(1/32,1/8),(1/8,1/4),(1/4,0.75)]; M=[(R>=a)&(R<b) for a,b in B]
print('band coefficient shares', [round(m.mean(),4) for m in M])
t='/mnt/t7/smad_next/DG1/rented_results/DG1_addon_s2_codes.tar'
with tarfile.open(t) as tf:
    m=[x for x in tf.getmembers() if x.name.endswith('codes.npz')][0]; z=np.load(io.BytesIO(tf.extractfile(m).read()))
names=list(z['names']); X=z['xT']; ix={n:i for i,n in enumerate(names)}
jobs=list(csv.DictReader(open('/mnt/t7/smad_next/DG1/addon_jobs/addon_s2.csv')))
same={j['host']:(j['src_a'],j['src_b']) for j in jobs if j['pool']=='AO_SAME20'}
res=[]
for h,(a,b) in same.items():
    A=np.fft.fft2(X[ix[a]].astype(float)); Bf=np.fft.fft2(X[ix[b]].astype(float))
    pw=[];bc=[]
    for mm in M:
        mm=np.broadcast_to(mm,A.shape); num=np.real((A[mm]*np.conj(Bf[mm])).sum()); den=np.sqrt((abs(A[mm])**2).sum()*(abs(Bf[mm])**2).sum())
        bc.append(num/den); pw.append(den)
    pw=np.array(pw); c=np.dot(X[ix[a]].ravel().astype(float),X[ix[b]].ravel().astype(float))/np.linalg.norm(X[ix[a]])/np.linalg.norm(X[ix[b]])
    res.append((c, (np.array(bc)*pw).sum()/pw.sum(), *bc, *(pw/pw.sum())))
r=np.array(res); print('n',len(r),'corr whole cos vs power-weighted band cos', np.corrcoef(r[:,0],r[:,1])[0,1], 'max abs diff', np.abs(r[:,0]-r[:,1]).max())
print('median power shares', np.median(r[:,6:],0).round(4))
for k in range(4): print('spearman whole cos vs c%d'%k, round(spearmanr(r[:,0],r[:,2+k])[0],3))
