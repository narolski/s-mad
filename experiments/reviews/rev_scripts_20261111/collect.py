import json,glob,re,sys
rows={}
for f in glob.glob('/home/narolski/mambamorph-code/smadcvpr/results/A13/a13*/*.json'):
    try: d=json.load(open(f))
    except Exception: continue
    if not isinstance(d,dict) or 'per_run' not in d: continue
    for r in d['per_run']:
        key=r['file']
        rows[key]=r
out=[]
for k,r in rows.items():
    m=re.search(r'cluster/(\w+)/(\S+)_s(\d+)_(v\w+)/scores',k)
    exp,arch,seed,var=m.group(1),m.group(2),int(m.group(3)),m.group(4)
    out.append(dict(exp=exp,arch=arch,seed=seed,var=var,valxs=r['valxs'],b1s=r['eer_b1s/v_amsl'],feret=r['eer_b2/v_amsl@feret'],frgc=r['eer_b2/v_amsl@frgc'],gan=r['eer_b2/v_gan_unmatched'],valx=r['valx']))
json.dump(out,open(sys.argv[1],'w'),indent=0)
for o in sorted(out,key=lambda o:(o['arch'],o['exp'],o['seed'])):
    print(o['exp'],o['arch'][:22],o['var'],o['seed'],round(o['valxs']*100,2),round(o['b1s']*100,2),round(o['feret']*100,2),round(o['frgc']*100,2))
