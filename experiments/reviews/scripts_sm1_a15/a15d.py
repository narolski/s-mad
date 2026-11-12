import csv, numpy as np
D='/mnt/t7/smad_next/SM1/results_rented/dev'
rows=list(csv.DictReader(open('/mnt/t7/smad_next/SM1/dev_a14/sm1_dev_eval.csv')))
fam={}
for r in rows: fam.setdefault(r['family'],[]).append(r)
hosts=sorted({r['variant'] for r in fam['X20']}); hp={h:i for i,h in enumerate(hosts)}
C=np.random.default_rng(20261111).multinomial(len(hosts),np.full(len(hosts),1/len(hosts)),size=10000).astype(float)
S={}
for T in ['a_s401','a_s402','e_s401','e_s402','f_s401','f_s402']:
    z=np.load(f'{D}/SM1D_{T}/scores_audit.npz'); p=np.clip(z['score_noTTA'].astype(float),1e-7,1-1e-7)
    S[T]=dict(zip([str(i) for i in z['id']],np.log(p/(1-p))))
for st in ('amsl112','fm61'):
    rs=fam[f'R0_soft_{st}']; W=C[:,[hp[r['variant']] for r in rs]]
    val={}
    for arm in 'aef':
        v=[]
        for s in ('401','402'):
            inc=np.array([S[f'{arm}_s{s}'][r['id']]-S[f'{arm}_s{s}'][r['src_id']] for r in rs])
            sgn=(inc>0)+0.5*(inc==0); v.append((W*sgn).sum(1)/W.sum(1)); 
            print(st,arm,s,'ties',int((inc==0).sum()),'|inc|<0.01 share',round((abs(inc)<0.01).mean(),3))
        val[arm]=np.mean(v,0)
        print(st,arm,'true paired',round(float(np.mean([((np.array([S[f"{arm}_s{s}"][r["id"]]-S[f"{arm}_s{s}"][r["src_id"]] for r in rs])>0)).mean() for s in ("401","402")])),3),np.round(np.percentile(val[arm],[2.5,97.5]),3))
    d=val['e']-val['f']; print(st,'e-f true paired',round(float(d.mean()),3),np.round(np.percentile(d,[2.5,97.5]),3))
