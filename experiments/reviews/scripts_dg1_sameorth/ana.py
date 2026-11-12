import numpy as np, csv, sys
d=np.load(sys.argv[1]); names=list(d['names']); X=d['xT']; ix={n:i for i,n in enumerate(names)}
jobs=[r for r in csv.DictReader(open(sys.argv[2])) if r['pool'] in('AO_SAME20','AO_X20')]
same={r['host']:(r['src_a'],r['src_b']) for r in jobs if r['pool']=='AO_SAME20'}
xx={r['host']:r['src_b'] for r in jobs if r['pool']=='AO_X20'}
def cos(u,v): return float(u.ravel()@v.ravel()/np.linalg.norm(u)/np.linalg.norm(v))
def slerp(a,b):
    t=np.arccos(cos(a,b)); return (np.sin(t/2)*a+np.sin(t/2)*b)/np.sin(t)
fy=np.fft.fftfreq(256)[:,None]; fx=np.fft.fftfreq(256)[None,:]; r=np.sqrt(fx**2+fy**2)
bands=[(0,1/32),(1/32,1/8),(1/8,1/4),(1/4,0.75)]
def bandcos(u,v):
    U=np.fft.fft2(u); V=np.fft.fft2(v); out=[]
    for lo,hi in bands:
        m=(r>=lo)&(r<hi); m=np.broadcast_to(m,U.shape)
        out.append(float(np.real((U[m]*np.conj(V[m])).sum())/np.sqrt((abs(U[m])**2).sum()*(abs(V[m])**2).sum())))
    return out
def lp(u,k=8): return u.reshape(3,256//k,k,256//k,k).mean((2,4))
R=[]
for h,(sa,sb) in list(same.items()):
    if h not in xx: continue
    a=X[ix[sa]].astype(np.float64); b=X[ix[sb]].astype(np.float64); p=X[ix[xx[h]]].astype(np.float64)
    bp=b-(a.ravel()@b.ravel())/(a.ravel()@a.ravel())*a; bp*=np.linalg.norm(b)/np.linalg.norm(bp)
    cs=cos(a,b); ts=np.arccos(cs)
    pp=p-(a.ravel()@p.ravel())/(a.ravel()@a.ravel())*a; u=pp/np.linalg.norm(pp)
    pc=np.linalg.norm(p)*(np.cos(ts)*a/np.linalg.norm(a)+np.sin(ts)*u)
    xs,xo,xX,xc=slerp(a,b),slerp(a,bp),slerp(a,p),slerp(a,pc)
    n=np.linalg.norm
    R.append([cs,cos(a,p),cos(a,bp),cos(lp(a),lp(b)),cos(lp(a),lp(bp)),cos(lp(a),lp(p)),
              n(xo-xs)/n(xs),n(xX-xs)/n(xs),n(xc-xX)/n(xX),n(a)/np.sqrt(a.size),a.std(),b.std(),bp.std(),xs.std(),xo.std(),xX.std()]
             +bandcos(a,b)+bandcos(a,bp)+bandcos(a,p))
R=np.array(R); print(len(R))
lab="cos_ab cos_ap cos_abp lpcos_ab lpcos_abp lpcos_ap d_orth_vs_same d_X_vs_same d_corr_vs_X rms_a sd_a sd_b sd_bp sd_xsame sd_xorth sd_xX".split()+[f"band{i}_ab" for i in range(4)]+[f"band{i}_abp" for i in range(4)]+[f"band{i}_ap" for i in range(4)]
for l,c in zip(lab,R.T): print(f"{l:16s} median {np.median(c):+.4f}  [{np.percentile(c,5):+.4f},{np.percentile(c,95):+.4f}]")
