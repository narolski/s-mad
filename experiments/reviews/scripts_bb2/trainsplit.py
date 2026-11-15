import numpy as np, glob, json
def auc(p,n):
    p=np.asarray(p);n=np.asarray(n); r=np.argsort(np.argsort(np.r_[p,n]))+1
    return (r[:len(p)].sum()-len(p)*(len(p)+1)/2)/(len(p)*len(n))
S='/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/clipfs'
for bb,pat in [('DINOv3','/mnt/t7/smad_next/BB2/results/unpacked/BB2_Sb_s%d/scores_train.npz'),('CLIP',S+'/Sb_%d/PN1_Sb_s%d/scores_train.npz')]:
  for s in range(403,408):
    f=pat%((s,) if bb=='DINOv3' else (s,s))
    z=np.load(f,allow_pickle=True); L=z['logit'];K=z['kind']
    g=lambda k:L[K==k]
    print(bb,s,'S4 miss %.2f S3 flag %.2f S0 flag %.2f | train AUC S4vsS3 %.3f S4vsS0 %.3f | acc %.3f'%((g('lad_S4')<=0).mean(),(g('lad_S3')>0).mean(),(g('lad_S0')>0).mean(),auc(g('lad_S4'),g('lad_S3')),auc(g('lad_S4'),g('lad_S0')),json.load(open(f.replace('scores_train.npz','info.json')))['train_acc_rule0']))
