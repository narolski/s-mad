import hashlib,json
from pathlib import Path

R=Path('/home/narolski/smad-next')
D=R/'experiments/AGENTIC_delivery_20261114'
P=Path('/mnt/t7/smad_next/PN1/fs_tree/pn1/code/smadcvpr')
F=Path('/home/narolski/mambamorph-code-a46/smadcvpr')
A=R/'manuscript_cvpr2027/figures/shortcut_prototype_assets'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def pin(p):return dict(path=str(p),sha256=sha(p))
sources=[D/'XAI_PROTOCOL_20261114.md', A/'source_manifest.json']
for code in (P,F):
 for n in ('common.py','archs_a12.py','archs_v2.py'):
  sources.append(code/n)
for n in ('a12_released.py','a36_madation.py','mixfacenet_port.py'):
 sources.append(F/n)
inputs=[dict(pin(A/name),condition=c) for name,c in (
 ('aligned_native.png','native'),('existing_storage_matched.png','storage'),('existing_border_matched.png','border'))]
models={}
base=Path('/mnt/t7/smad_next/PN1/fs_tree/pn1/hf/a12/vit_base_patch16_clip_224.openai.safetensors')
for arm in ('A','B','Sb'):
 n=Path('/mnt/t7/smad_next/TT1/nets_fs')/f'PN1_{arm}_s403'
 models[arm]=dict(kind='own',code=str(P),meta=str(n/'meta.json'),checkpoint=str(n/'last_trainable.pt'),
                  checkpoints=[pin(n/'meta.json'),pin(n/'last_trainable.pt'),pin(base)],seed=403,checkpoint_type='last_trainable plus pinned frozen CLIP base')
rels=dict(madation_vitb16=('ddb1455bae4b72331aff4806590bd88ba2447563d803e207099c6b712d6bbe2f','safetensors'),
 madation_vitl14=('bb452ded624ffce2dc85168f8dde9293fc3709ec8cce755d8ecf1d5f5370e980','safetensors'))
for name,(h,ext) in rels.items():
 p=Path('/mnt/t7/smad_heldout/mad22_production_cpu_stage_v1/payload/models')/(h+'.'+ext)
 assert sha(p)==h
 models[name]=dict(kind='release',code=str(F),checkpoint=str(p),checkpoints=[pin(p)])
for name,p,h in (
 ('mixfacenet_mad_smdd',Path('/mnt/t7/mixfacenet_mad_official/mixfacenet_SMDD.pth'),'3d507c8bbd5dbd06bd735ae809fa0095e589c17c0c94cd2ed530cf34a014ab1c'),
 ('selfmad_hrnet_w18',Path('/mnt/t7/smad_next/AR1/weights/selfmad_release/hrnet_w18_checkpoint.model.safetensors'),'0ad8db6f8f156cb21606e03ab32c88d122640cb835f7a93c77cca30c01386a26')):
 assert sha(p)==h
 models[name]=dict(kind='release',code=str(F),checkpoint=str(p),checkpoints=[pin(p)])
out=D/'XAI_INVENTORY_20261114.json'
with out.open('x') as f:json.dump(dict(runner_sha256=sha(D/'xai_gradient_pilot.py'),sources=[pin(p) for p in sources],inputs=inputs,models=models,hf_home='/mnt/t7/smad_next/PN1/fs_tree/pn1/hf'),f,indent=2);f.write('\n')
print(out,sha(out))
