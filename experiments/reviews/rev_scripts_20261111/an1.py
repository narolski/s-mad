import json,sys,itertools
import numpy as np
R=json.load(open(sys.argv[1]))
A={'mm2_t_c2_conv_v2_p8_r384_d1_train90_none_lr0.0002':'K','mm2_t_c2noscan_conv_v2_p8_r384_d1_train90_none_lr0.0002':'N',
   'mm2_t_c2nomem_conv_v2_p8_r384_d1_train90_none_lr0.0002':'M','mm2_t_v2_conv_v2_p8_r384_d1_train90_none_lr0.0002':'E10',
   'mm2_t_v1_conv_v2_p8_r384_d1_train90_none_lr0.0002':'V','mm2_t_dt_conv_v2_p8_r384_d1_train90_none_lr0.0002':'D'}
T={}
for r in R:
    T[(A[r['arch']],r['exp'],r['seed'])]=r
def g(c,e,s,k='valxs'): return T[(c,e,s)][k]*100
# replicate pairs
groups={
 'V2-V (A13 vs A10)':[(g('V','A9A13',s),g('V','A9W2L0',s)) for s in (1,2,3)],
 "E10'-E10 (A133 vs A10)":[(g('E10','A9A133',s),g('E10','A9W2L0',s)) for s in (4,5,6)],
 "V'-V (A133 vs A10)":[(g('V','A9A133',s),g('V','A9W2L0',s)) for s in (4,5,6)],
 "K'-K (A133 vs A13)":[(g('K','A9A133',s),g('K','A9A13',s)) for s in (4,5,6)],
 "K''-K (A135 vs A13)":[(g('K','A9A135',s),g('K','A9A13',s)) for s in (1,2,3)],
}
diffs=[];gm=[]
for k,v in groups.items():
    d=[a-b for a,b in v]; diffs.append(d); gm.append(np.mean(d))
    print(k,[round(x,2) for x in d],'mean',round(np.mean(d),2),'sd',round(np.std(d,ddof=1),2))
allD=np.concatenate(diffs)
print('all 15 pairs mean',allD.mean().round(3),'sd',allD.std(ddof=1).round(3),'rms',np.sqrt((allD**2).mean()).round(3))
k=len(diffs);n=3
msw=sum(((np.array(d)-np.mean(d))**2).sum() for d in diffs)/(k*(n-1))
msb=n*np.var(gm,ddof=1)
print('MS_within',round(msw,3),'MS_between',round(msb,3),'F',round(msb/msw,3),'df',k-1,k*(n-1))
from math import *
# F p-value
try:
    from scipy import stats
    print('p(F>=obs)',round(1-stats.f.cdf(msb/msw,k-1,k*(n-1)),3))
except Exception as e: print('no scipy',e)
print('implied per-run sd (sqrt(msw/2))',round(sqrt(msw/2),3))
# seed correlation: pairs of same-seed runs
a=[x for v in groups.values() for x,_ in v]; b=[y for v in groups.values() for _,y in v]
# center within config-batch group to remove config means
ac=[];bc=[]
for v in groups.values():
    x=np.array([p[0] for p in v]);y=np.array([p[1] for p in v])
    ac+=list(x-x.mean());bc+=list(y-y.mean())
print('within-group same-seed corr (15 pairs, centred)',round(np.corrcoef(ac,bc)[0,1],3))
# within-config between-seed sd per batch
for c,e in [('K','A9A13'),('N','A9A133'),('M','A9A135'),('E10','A9W2L0'),('V','A9W2L0'),('D','A9A13')]:
    x=[g(c,e,s) for s in range(1,7)]
    print(c,e,'mean',round(np.mean(x),2),'sd',round(np.std(x,ddof=1),2))
