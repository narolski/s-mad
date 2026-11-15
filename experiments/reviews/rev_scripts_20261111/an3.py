import json,sys,itertools
import numpy as np
R=json.load(open(sys.argv[1]))
G={}
for r in R:
    G.setdefault((r['arch'].split('_conv')[0].replace('mm2_t_',''),r['exp']),{})[r['seed']]=r['valxs']*100
C={}
for g,d in G.items():
    m=np.mean(list(d.values()))
    C[g]={s:v-m for s,v in d.items()}
fam_init={'c2','c2noscan','c2nomem'}
def pooled(pred):
    xs=[];ys=[]
    for g1,g2 in itertools.combinations(C,2):
        if not pred(g1,g2): continue
        for s in set(C[g1])&set(C[g2]):
            xs+= [C[g1][s],C[g2][s]]; ys+=[C[g2][s],C[g1][s]]
    return len(xs)//2, np.corrcoef(xs,ys)[0,1]
print('same config, different batch (replicates):',pooled(lambda a,b:a[0]==b[0]))
print('different config, same init (K/N/M family):',pooled(lambda a,b:a[0]!=b[0] and a[0] in fam_init and b[0] in fam_init))
print('different config, different init (data order only):',pooled(lambda a,b:a[0]!=b[0] and not (a[0] in fam_init and b[0] in fam_init)))
print('groups',{f'{k[0]}@{k[1]}':len(v) for k,v in G.items()})
# per-seed table of centred values
for s in range(1,7):
    print(s,' '.join(f"{g[0]}@{g[1][-3:]}:{C[g][s]:+.2f}" for g in sorted(C) if s in C[g]))
