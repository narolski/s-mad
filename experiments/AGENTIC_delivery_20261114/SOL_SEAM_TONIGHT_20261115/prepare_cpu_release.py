"""ROOT-operated proposal builder, not authorization; reads controls/source only."""
import argparse, hashlib, json, subprocess
from pathlib import Path
R=Path('/home/narolski/smad-next')
E=R/'experiments/VIS3_true_seam_private_20261115/v2r1'
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser()
p.add_argument('--source-commit',required=True)
p.add_argument('--other-review',type=Path,required=True)
p.add_argument('--other-review-sha256',required=True)
p.add_argument('--reviewer',required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args()
assert a.reviewer!='shortcut_visual_examples'
assert a.other_review.resolve().is_relative_to(R)
assert a.out.resolve().is_relative_to(R) and a.out.suffix=='.json'
assert digest(a.other_review)==a.other_review_sha256
inv=E/'INVENTORY.json'
assert digest(inv)=='d67d18e3193887ea085e9cd7be95054bb2bb946fde655e9d5e158a8f2ae4aecf'
assert digest(E/'FROZEN_SOURCE_HANDOFF.json')=='08d91fbd367c835f68c861422584b3d5708acee263b71b687f016f2a6cb032dd'
i=json.loads(inv.read_bytes())
for rel in i['owned_paths']:
    committed=subprocess.check_output(['git','show',a.source_commit+':'+rel],cwd=R)
    assert hashlib.sha256(committed).hexdigest()==digest(R/rel),rel
assert not subprocess.check_output(['git','status','--porcelain','--',*i['owned_paths']],cwd=R)
g={
 'issued_by':'root','author':'shortcut_visual_examples','reviewer':a.reviewer,
 'independent_review_path':str(a.other_review.resolve()),'independent_review_sha256':a.other_review_sha256,
 'inventory_sha256':'d67d18e3193887ea085e9cd7be95054bb2bb946fde655e9d5e158a8f2ae4aecf',
 'prereg_sha256':'636428eb3a2db72f287ee8eadbb2fd54f2dcd1606d93e309d15b0d9d9aa88e57',
 'source_manifest_sha256':'4aa997c961f65487d7cf46fd9a9629760adf643c2cb04411a8f8ea4945b666c5',
 'source_commit':a.source_commit,'private_noncommercial_only':True,'publication_allowed':False,
 'render_allowed':False,'phase':'construct','decision':'GO_VIS3_PRIVATE_CPU_CONSTRUCTION',
 'source_pixel_export_allowed':True,'new_derivative_construction_allowed':True}
with a.out.open('x') as f: json.dump(g,f,indent=2); f.write('\n')
print('PROPOSED_ROOT_GRANT',a.out)
print('EXTERNAL_ROOT_DIGEST_FOR_REVIEW',digest(a.out))
print('ROOT must approve exact grant, commit grant clean, mirror frozen source, verify output root absent/capacity, and supply approved digest out-of-band. Builder never invokes constructor.')
