import torch; torch.set_num_threads(4)
import torch, sys, glob, os, re, math
from safetensors.torch import load_file
def base_qkv(path, prefix):
    w=load_file(path); out={}
    for k,v in w.items():
        m=re.match(prefix, k)
        if m: out[int(m.group(1))]=v.float()
    return out
dino=base_qkv('/home/narolski/.cache/huggingface/hub/models--timm--vit_large_patch16_dinov3.lvd1689m/snapshots/30c1109559f65dea34316b0d4842d35c5771fe11/model.safetensors', r'blocks\.(\d+)\.attn\.qkv\.weight$')
clipf=['/mnt/t7/smad_next/PN1/fs_tree/pn1/hf/a12/vit_base_patch16_clip_224.openai.safetensors']
clip=base_qkv(clipf[0], r'blocks\.(\d+)\.attn\.qkv\.weight$') if clipf else {}
scale=4/math.sqrt(2)
def rep(f, base):
    sd=torch.load(f,map_location='cpu',weights_only=False)
    L=sorted({int(re.search(r'blocks\.(\d+)\.',k).group(1)) for k in sd if 'blocks' in k})
    rel=[];spec=[];bn=[]
    for l in L:
        pre=[k for k in sd if f'blocks.{l}.attn' in k][0].rsplit('.',1)[0]
        W=base.get(l)
        d=W.shape[1] if W is not None else None
        for i,t in enumerate('qv'):
            A=sd[f'{pre}.A_{t}'].float(); B=sd[f'{pre}.B_{t}'].float(); dW=scale*B@A
            bn.append(float(B.norm()))
            if W is not None:
                Ws=W[(0 if t=='q' else 2)*d:(1 if t=='q' else 3)*d]
                rel.append(float(dW.norm()/Ws.norm()))
    hw=[k for k in sd if k.endswith('weight') and 'head' in k][0]
    import statistics as st
    return dict(head=float(sd[hw].norm()), B=st.mean(bn), Bmax=max(bn), relF=st.mean(rel) if rel else None, relFmax=max(rel) if rel else None, spec=max(spec) if spec else None, nL=len(L))
for f in [] and sorted(glob.glob('/mnt/t7/smad_next/BB2/results/unpacked/BB2_*/last_trainable.pt')):
    r=rep(f,dino); print(f.split('/')[-2], {k:(round(v,4) if isinstance(v,float) else v) for k,v in r.items()})
for f in sorted(glob.glob('/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/clipfs/*/PN1_*/last_trainable.pt')):
    if re.search(r'PN1_(A|B|Sb)_s',f):
        r=rep(f,clip); print(f.split('/')[-2], {k:(round(v,4) if isinstance(v,float) else v) for k,v in r.items()})
