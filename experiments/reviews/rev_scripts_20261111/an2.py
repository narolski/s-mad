import json,sys
import numpy as np
R=json.load(open(sys.argv[1]))
A={'mm2_t_c2_conv_v2_p8_r384_d1_train90_none_lr0.0002':'K','mm2_t_c2noscan_conv_v2_p8_r384_d1_train90_none_lr0.0002':'N',
   'mm2_t_c2nomem_conv_v2_p8_r384_d1_train90_none_lr0.0002':'M','mm2_t_v2_conv_v2_p8_r384_d1_train90_none_lr0.0002':'E10',
   'mm2_t_v1_conv_v2_p8_r384_d1_train90_none_lr0.0002':'V','mm2_t_dt_conv_v2_p8_r384_d1_train90_none_lr0.0002':'D'}
rng=np.random.default_rng(0)
def runs(c,exps=None,key='valxs'):
    return np.array([r[key]*100 for r in R if A[r['arch']]==c and (exps is None or r['exp'] in exps)])
def boot(a,b,B=20000):
    m=[rng.choice(a,len(a)).mean()-rng.choice(b,len(b)).mean() for _ in range(B)]
    return np.percentile(m,[5,95])
# null false-positive rate of H-new-5 rule
sd=np.sqrt(2.031)
sims=rng.normal(0,sd,(200000,3,3)).mean(2)
neg=(sims<=-0.5).sum(1);pos=(sims>=0.5).sum(1)
print('P(H-new-5 supported | no batch effect, diff sd %.2f)'%sd, ((neg>=2)|(pos>=2)).mean().round(3))
sims=rng.normal(0,1.32,(200000,3,3)).mean(2)
neg=(sims<=-0.5).sum(1);pos=(sims>=0.5).sum(1)
print('  with diff sd 1.32:', ((neg>=2)|(pos>=2)).mean().round(3), ' P(falsified: all |s|<0.5)', (np.abs(sims)<0.5).all(1).mean().round(3))
# SE of a 3-pair shift
print('SE of 3-pair shift', round(sd/np.sqrt(3),2))
for key in ['valxs','b1s','feret','frgc']:
    K=runs('K',None,key); K0=runs('K',['A9A13'],key); N=runs('N',None,key); M=runs('M',None,key); E=runs('E10',None,key); E0=runs('E10',['A9W2L0'],key)
    print('\n==',key,'| K all n',len(K),'mean',K.mean().round(2),'| K A13',K0.mean().round(2),'| N',N.mean().round(2),'| M',M.mean().round(2),'| E10 all n',len(E),E.mean().round(2),'| E10 A10',E0.mean().round(2))
    for nm,a,b in [('N-K(A13)',N,K0),('M-K(A13)',M,K0),('N-Kpool12',N,K),('M-Kpool12',M,K),('M-N',M,N),('N-E10pool9',N,E),('M-E10pool9',M,E),('Kpool-E10pool',K,E),('N-E10(A10)',N,E0)]:
        ci=boot(a,b,5000)
        print('  %-14s %+.2f [%+.2f, %+.2f]'%(nm,a.mean()-b.mean(),ci[0],ci[1]))
# same batch N vs E10' seeds 4-6
def g(c,e,s,key='valxs'):
    return [r[key]*100 for r in R if A[r['arch']]==c and r['exp']==e and r['seed']==s][0]
d=[g('N','A9A133',s)-g('E10','A9A133',s) for s in (4,5,6)]
print("\nsame batch N - E10' s4-6",[round(x,2) for x in d],'mean',round(np.mean(d),2))
d=[g('N','A9A133',s)-g('K','A9A133',s) for s in (4,5,6)]
print("same batch N - K' s4-6",[round(x,2) for x in d],'mean',round(np.mean(d),2))
# V regression to mean
V=[g('V','A9W2L0',s) for s in range(1,7)]
print('\nA10 V s1-3 mean',round(np.mean(V[:3]),2),'s4-6',round(np.mean(V[3:]),2),'all',round(np.mean(V),2),'| V2 s1-3',round(np.mean([g('V','A9A13',s) for s in (1,2,3)]),2),"| V' s4-6",round(np.mean([g('V','A9A133',s) for s in (4,5,6)]),2))
Ev=[g('E10','A9W2L0',s) for s in range(1,7)]
print('A10 E10 s1-3',round(np.mean(Ev[:3]),2),'s4-6',round(np.mean(Ev[3:]),2),"E10' s4-6",round(np.mean([g('E10','A9A133',s) for s in (4,5,6)]),2))
Kv=[g('K','A9A13',s) for s in range(1,7)]
print('A13 K s1-3',round(np.mean(Kv[:3]),2),'s4-6',round(np.mean(Kv[3:]),2),"K'' s1-3",round(np.mean([g('K','A9A135',s) for s in (1,2,3)]),2),"K' s4-6",round(np.mean([g('K','A9A133',s) for s in (4,5,6)]),2))
