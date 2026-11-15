import csv, json, glob, collections, numpy as np
R='/mnt/t7/smad_next/RS1/results_rented/'
man={r['id']:r for r in csv.DictReader(open('/mnt/t7/smad_next/RS1/athena/athena_manifest.csv'))}
B={}
for f in glob.glob(R+'prod_v2_rented/v2meta/boxes_*.jsonl'):
    for l in open(f):
        d=json.loads(l); B[d['id']]=d['box']
miss=set(json.load(open(R+'prod_v1_rented/crop_summary.json'))['v1_missing'])
z=np.load(R+'prod_v1_rented/scores/scores_rel_madation_vitb16__v1.npz'); L1=dict(zip(z['id'].tolist(),z['logit_noTTA']))
z=np.load(R+'prod_v2_rented/scores/scores_rel_madation_vitb16__v2.npz'); L2=dict(zip(z['id'].tolist(),z['logit_noTTA']))
by=collections.defaultdict(list)
for i in B: by[man[i]['set']].append(i)
for s in sorted(by):
    ids=by[s]; neg=[];ok=[]
    for i in ids:
        b=B[i]
        if b is None: continue
        x1,y1,x2,y2=b; w=x2-x1;h=y2-y1
        (neg if (round(x1-0.05*w)<0 or round(y1-0.05*h)<0) else ok).append(i)
    negk=[i for i in neg if i not in miss]
    if not neg: continue
    f=lambda S,L:'%.2f'%np.median([L[i] for i in S if i in L]) if any(i in L for i in S) else '-'
    print('%-22s n=%4d negstart=%4d kept-negstart(v1 sliver)=%4d  ViT-B v1 median logit sliver %s / ok %s ; v2 same imgs %s / %s'%(s,len(ids),len(neg),len(negk),f(negk,L1),f(ok,L1),f(negk,L2),f(ok,L2)))
