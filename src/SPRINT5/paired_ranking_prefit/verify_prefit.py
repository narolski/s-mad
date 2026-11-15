"""Verify committed pre-fit metadata/review pins without detector payload access."""
import argparse,hashlib,json,pathlib,subprocess
ap=argparse.ArgumentParser();ap.add_argument('--binding',type=pathlib.Path,required=True);ap.add_argument('--require-committed',action='store_true');a=ap.parse_args()
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(4<<20),b''):h.update(b)
 return h.hexdigest()
b=json.loads(a.binding.read_text());assert b['status']=='BOUND_PREFIT_METADATA' and b['root_policy_approved'] is True
assert b['seeds']==[501,502,503,504,505] and b['protected_NEXT']==[413,414,415,416,417]
assert b['calibration']['n']==132 and b['calibration']['order']==127 and b['calibration']['strict_gt'] is True
assert b['guards']['genuine_cells']==119 and b['guards']['mode']=='IUT_marginal_one_sided_95' and b['guards']['zero_variance']!='PASS'
for p,h in b['pins'].items():assert sha(p)==h,('pin',p)
review=pathlib.Path(b['review_path']).read_text();assert 'PREFIT_METADATA_GO '+sha(a.binding) in review
pinfile=a.binding.parent/'pins.sha256'
for line in pinfile.read_text().splitlines():
 h,p=line.split('  ',1);assert sha(p)==h,('packagepin',p)
if a.require_committed:
 repo=pathlib.Path(b['repo']);owned=b['owned_repo_paths']
 for p in owned:subprocess.run(['git','ls-files','--error-unmatch',p],cwd=repo,stdout=subprocess.DEVNULL,check=True)
 dirty=subprocess.check_output(['git','status','--porcelain','--',*owned],cwd=repo,text=True);assert not dirty,dirty
print('PREFIT_METADATA_VERIFIED; GPU smoke/production receipt still separate; no candidate read')
