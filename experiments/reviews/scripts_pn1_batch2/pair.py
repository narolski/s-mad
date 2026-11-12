import csv, numpy as np, re
U='/mnt/t7/smad_next/PN1/results_rented/unpacked/'
def load(p):
    z=np.load(p); return dict(zip([str(i) for i in z['id']], z['logit'].astype(float)))
fm={r['id']:r for r in csv.DictReader(open('/mnt/t7/smad_heldout/ffhq_morphs/manifests/ffhqm.csv'))}
hn=list(csv.DictReader(open('/mnt/t7/smad_next/PN1/hn2_tree/pn1h/data/manifests/pn1_hn2.csv')))
key=lambda i: re.search(r'ffhq_bona/(\d+)_', fm[i]['path']).group(1)
ob={key(r['id']):r['id'] for r in hn if r['rung']=='ffhq_bona_orig'}
rmb={key(r['id']):r['id'] for r in hn if r['rung']=='landmark_complete_resmatch'}
common=sorted(set(ob)&set(rmb)); print('paired keys',len(common))
for s in (401,402):
  for a in ('A','B','Bn','C'):
    S=load(U+f'PN1_HN2_s{s}/scores_hn2_{a}.npz')
    d=np.array([S[rmb[k]]-S[ob[k]] for k in common])
    print(s,a,'share rising %.3f'%((d>0).mean()+0.5*(d==0).mean()),'median shift %.3f'%np.median(d),'mean %.3f'%d.mean())
