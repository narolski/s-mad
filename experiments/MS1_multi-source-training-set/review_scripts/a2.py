import csv, io, tarfile, numpy as np, json, itertools
from scipy.stats import mannwhitneyu
R='/mnt/t7/smad_next/MS1/results_rented/'
M=list(csv.DictReader(open('/mnt/t7/smad_next/MS1/pack_tree/pn1/data/manifests/pn1_eval.csv')))
H=list(csv.DictReader(open('/mnt/t7/smad_next/MS1/heldout_tree/pn1/data/manifests/ms1_heldout.csv')))
def auc(p,n):
    p=np.asarray(p);n=np.asarray(n)
    return mannwhitneyu(p,n).statistic/(len(p)*len(n))
def load(arm,s):
    with tarfile.open(f'{R}MS1_{arm}_s{s}.tar') as t:
        m=[x for x in t.getmembers() if x.name.endswith('scores_eval.npz')][0]
        z=np.load(io.BytesIO(t.extractfile(m).read()))
    L=dict(zip(map(str,z['id']),z['logit'].astype(float)))
    Hd={}
    for fam in ('cfd','kdef','tt1ref'):
        z=np.load(f'{R}heldout/MS1H_{arm}_s{s}_{fam}.npz'); Hd.update(dict(zip(map(str,z['id']),z['logit'].astype(float))))
    return L,Hd
def sel(L,f): return np.array([L[r['id']] for r in M if f(r)])
out={}
for arm in ('Sb','SbM3','SbV'):
  for s in (403,404,405,406,407):
    L,Hd=load(arm,s)
    o={}
    cam=np.concatenate([sel(L,lambda r:r['fam']=='ladder' and r['role']=='dev' and r['rung']=='R0' and r['strength']==''),
                        sel(L,lambda r:r['fam']=='af0' and r['role']=='dev' and r['rung']=='photo' and r['strength']=='')])
    r4=sel(L,lambda r:r['fam']=='ladder' and r['role']=='dev' and r['rung']=='R4' and r['strength']=='')
    u50=sel(L,lambda r:r['fam']=='af0' and r['role']=='dev' and r['rung']=='u50' and r['strength']=='')
    r4t=sel(L,lambda r:r['fam']=='ladder' and r['role']=='test' and r['rung']=='R4' and r['strength']=='')
    r2wt=sel(L,lambda r:r['fam']=='ladder' and r['role']=='test' and r['rung']=='R2w' and r['strength']=='')
    s4=sel(L,lambda r:r['fam']=='splice' and r['role']=='dev' and r['rung']=='S4')
    s0=sel(L,lambda r:r['fam']=='splice' and r['role']=='dev' and r['rung'] in('S0','S3'))
    r4_61=sel(L,lambda r:r['fam']=='ladder' and r['rung']=='R4' and r['strength']=='61')
    r4_112=sel(L,lambda r:r['fam']=='ladder' and r['rung']=='R4' and r['strength']=='112')
    hu=sel(L,lambda r:r['fam']=='ms1ffhq' and r['rung']=='u50' and r['strength']=='')
    lcm=sel(L,lambda r:r['fam']=='ffhq_lcomb' and r['rung']=='landmark_combined_orig')
    lcg=sel(L,lambda r:r['fam']=='ffhq_lcomb' and r['rung']=='landmark_combined_resmatch')
    tt1=sel(L,lambda r:r['fam']=='tt1')
    cfd=np.array([v for k,v in Hd.items() if k.startswith('cfd_')])
    kdef=np.array([v for k,v in Hd.items() if k.startswith('kdef_')])
    rcam_off=np.array([Hd['rcam_'+r['id'][5:]] if False else Hd[r['id']] for r in H if r['rung']=='R_cam'])
    rcam_on=np.array([L[r['id'][5:]] for r in H if r['rung']=='R_cam'])
    d=rcam_off-rcam_on
    o['tf32_dmax']=float(np.abs(d).max()); o['tf32_dmed']=float(np.median(np.abs(d)))
    o['tf32_flagchg']=int(((rcam_off>0)!=(rcam_on>0)).sum())
    o['cfd_flag']=float((cfd>0).mean()); o['kdef_flag']=float((kdef>0).mean())
    o['cfd_med']=float(np.median(cfd)); o['cfd_p95']=float(np.percentile(cfd,95)); o['cfd_max']=float(cfd.max())
    o['kdef_med']=float(np.median(kdef)); o['kdef_max']=float(kdef.max())
    o['cam_med']=float(np.median(cam)); o['cam_sd']=float(cam.std(ddof=1)); o['cam_max']=float(cam.max())
    o['rcam_off_med']=float(np.median(rcam_off))
    o['att_med']=float(np.median(np.r_[r4,u50])); o['att_p05']=float(np.percentile(np.r_[r4,u50],5)); o['att_min']=float(np.r_[r4,u50].min())
    o['tt1_med']=float(np.median(tt1))
    # rank reads
    o['auc_cfd_vs_rcam_off']=auc(cfd,rcam_off)          # same TF32 setting (off)
    o['auc_cfd_vs_cam_mixed']=auc(cfd,cam)
    o['auc_att_vs_cfd_mixed']=auc(np.r_[r4,u50],cfd)
    o['auc_r4_vs_cfd']=auc(r4,cfd); o['auc_u50_vs_cfd']=auc(u50,cfd)
    o['auc_r4test_vs_cfd']=auc(r4t,cfd)
    o['auc_s4_vs_cfd']=auc(s4,cfd); o['auc_r4_61_vs_cfd']=auc(r4_61,cfd); o['auc_r4_112_vs_cfd']=auc(r4_112,cfd)
    o['auc_ms1u50_vs_cfd']=auc(hu,cfd); o['auc_lcomb_vs_cfd']=auc(lcm,cfd)
    o['auc_r4t_vs_r2wt']=auc(r4t,r2wt); o['auc_s4_vs_s0s3']=auc(s4,s0)
    o['auc_r4_61_vs_r4']=None
    o['auc_lcomb']=auc(lcm,lcg)
    o['auc_att_vs_tt1']=auc(np.r_[r4,u50],tt1)
    # threshold matched to dev-attack miss 5% (attack 5th pct): CFD flag
    t=np.percentile(np.r_[r4,u50],5)
    o['cfd_flag_at_att5']=float((cfd>t).mean()); o['tt1_flag_at_att5']=float((tt1>t).mean())
    t=np.percentile(np.r_[r4t],5); o['cfd_flag_at_r4test5']=float((cfd>t).mean())
    t=np.percentile(r4_61,5); o['cfd_flag_at_r4_61_5']=float((cfd>t).mean())
    # standardized CFD position
    o['cfd_z_cam']=float((np.median(cfd)-np.median(cam))/cam.std(ddof=1))
    o['att_miss_own']=float((np.r_[r4,u50]<=0).mean()); o['r4_61_miss']=float((r4_61<=0).mean()); o['r4_112_miss']=float((r4_112<=0).mean())
    o['s4_miss']=float((s4<=0).mean()); o['s0s3_flag']=float((s0>0).mean()); o['r2wt_flag']=float((r2wt>0).mean())
    o['ms1u50_miss']=float((hu<=0).mean()); o['lcomb_miss']=float((lcm<=0).mean()); o['lcg_flag']=float((lcg>0).mean())
    out[(arm,s)]=o
keys=list(out[('Sb',403)].keys())
for k in keys:
    if out[('Sb',403)][k] is None: continue
    row=[]
    for arm in ('Sb','SbM3','SbV'):
        v=[out[(arm,s)][k] for s in (403,404,405,406,407)]
        row.append(f"{arm}: "+" ".join(f"{x:.4f}" for x in v)+f" | med {np.median(v):.4f}")
    print(f"{k:22s}", "  ||  ".join(row))
json.dump({f"{a}_{s}":v for (a,s),v in out.items()},open('/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/ms1rev/a2.json','w'),indent=1)
