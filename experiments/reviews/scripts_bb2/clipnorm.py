import torch, glob, re, math, statistics as st
torch.set_num_threads(4)
from safetensors.torch import load_file
w=load_file('/mnt/t7/smad_next/PN1/fs_tree/pn1/hf/a12/vit_base_patch16_clip_224.openai.safetensors')
base={int(re.search(r'resblocks\.(\d+)\.',k).group(1)):v.float() for k,v in w.items() if k.endswith('attn.in_proj_weight') and k.startswith('transformer.')}
sc=4/math.sqrt(2)
for f in sorted(glob.glob('clipfs/*/PN1_*/last_trainable.pt')):
    sd=torch.load(f,map_location='cpu',weights_only=False); rel=[]
    for k in sd:
        m=re.search(r'\.(\d+)\..*A_([qv])$',k)
        if not m: continue
        l=int(m.group(1)); t=m.group(2); A=sd[k].float(); B=sd[k[:-3]+'B_'+t].float()
        W=base[l]; d=W.shape[1]; Ws=W[0:d] if t=='q' else W[2*d:3*d]
        rel.append(float((sc*B@A).norm()/Ws.norm()))
    print(f.split('/')[-2], 'relF mean %.4f max %.4f n %d'%(st.mean(rel),max(rel),len(rel)))
