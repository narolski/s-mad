"""Pin existing metadata/checkpoints and deterministic input selection; no score access."""
import csv,hashlib,json
from pathlib import Path
R=Path('/home/narolski/smad-next');E=R/'experiments/OCC1_seam-surround-pilot_20261114'
AR=Path('/mnt/t7/smad_next/AR1')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def pin(p):return dict(path=str(p),sha256=sha(p))
def rows(p):
 with p.open() as f:return list(csv.DictReader(f))
split=R/'experiments/PN1_protocol-network-first-tests/split/ladder_split.csv'
splices=rows(AR/'manifest_splice2.csv');main=rows(AR/'manifest.csv');extra=rows(AR/'manifest_extra2.csv')
pool={r['pid']:r for r in rows(AR/'pool.csv')}
eligible=[]
for host in sorted((r for r in rows(split) if r['role']=='dev'),key=lambda r:r['pid']):
 pid=host['pid'];images={}
 for r in splices:
  if r['p1']==pid and r['tool']=='opencv' and r['variant']=='native' and r['rung'] in ('S0','S3','S4'):
   images[r['rung']]=dict(r)
 for r in main+extra:
  if r['p1']==pid and r['tool']=='opencv' and r['rung'] in ('R2w','R2w4','R3','R4'):
   images[r['rung']]=dict(r)
 if set(images)=={'S0','S3','S4','R2w','R2w4','R3','R4'} and all(Path(x['path']).is_file() for x in images.values()):
  eligible.append((host,images));break
host,images=eligible[0];p=pool[host['pid']]
assert host['pid']=='feret:00026' and p['B_pid']=='feret:00140'
images['R0']=dict(path=p['H'],rung='R0',id='existing_H_'+host['pid'],role='dev',p1=host['pid'])
H=Path(p['H']).with_suffix('.tem');B=Path(p['B']).with_suffix('.tem')
old=R/'experiments/AGENTIC_delivery_20261114/XAI_INVENTORY_20261114_FP32.json'
ref=json.loads(old.read_text())
src=[x for x in ref['sources'] if '/smadcvpr/' in x['path']]
for q in (E/'prereg.md',old,split,AR/'pool.csv',AR/'manifest.csv',AR/'manifest_extra2.csv',AR/'manifest_splice2.csv',
          R/'src/AR1/splice.py',R/'src/AR1/ar1_common.py',H,B,
          Path('/mnt/t7/Datasety/colorferet/dvd2/gray_feret_cd2/doc/feret/FERET_Database_Release_Agreement_feb2001.pdf')):
 src.append(pin(q))
out=dict(schema='OCC1-preread-pins-v1',selection='First lexicographic dev host with all7existing OpenCV same-hull source/control images',
 host=host,pool_row=p,source_pixel_export_allowed=False,
 rights='No FERET image-release approval found; internal in-place research numeric-only. No original/occluded pixel export or face figure.',
 runner_sha256=sha(R/'src/OCC1/occlusion_runner.py'),sources=src,
 inputs=[dict(pin(Path(images[n]['path'])),condition=n,source_manifest_row=images[n]) for n in ('R0','R2w','R2w4','R3','R4','S0','S3','S4')],
 H_tem=str(H),B_tem=str(B),ar1_source=str(R/'src/AR1'),hf_home=ref['hf_home'],models=ref['models'])
with (E/'INPUT_MODEL_PINS.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print('Pinned metadata, sources,8images,7models; NO scores/decoded image arrays read',sha(E/'INPUT_MODEL_PINS.json'))
