"""HN10 receipt-only collection proposal. Never interprets tar members."""
import argparse
import datetime
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys

REPO=pathlib.Path('/home/narolski/smad-next')
COORD=pathlib.Path('/mnt/t7/smad_next/coordination_20261114')
RECEIPTS=[COORD/'sprint_complete_cohorts_20261114T180257Z/COLLECTION_VERIFIED.json',COORD/'hn_pair_collection_20261114T181157Z/COLLECTION_VERIFIED.json']
PACKROOT=REPO/'experiments/SPRINT5_20261114/collection_admission_packet_hn_20261114'
CONFIG={
 'hn':{'reader':'hn1_reader','evidence':'hn1/reader_implementation','adoption':'ROOT_INPUT_ADMISSION.json','experiment':'SPRINT5_2',
  'arms':['matched','self'],'seeds':[531,532,533,534,535],
  'source_sha':'a8a083a686ab47cf8f02e5a7da9e6dec92a797e33c5ec9b4e75f979e30400794','binding_sha':'51ae40530ee4a848aece44693c143923a68636eb769468e5e5637904ab8eede3',
  'review':'ASTRA_IMPLEMENTATION_REVIEW.md','acceptance':'ROOT_CODE_ACCEPTANCE.md','scope':'PRIMARY_DESCRIPTIVE_ONLY'}
}


def sha(path):
 h=hashlib.sha256()
 with pathlib.Path(path).open('rb') as f:
  for block in iter(lambda:f.read(4<<20),b''):h.update(block)
 return h.hexdigest()


def obj(path):return json.loads(pathlib.Path(path).read_text())


def write(path,value):
 path=pathlib.Path(path)
 with path.open('x') as f:
  f.write(json.dumps(value,indent=2)+'\n');f.flush();os.fsync(f.fileno())


def git_clean(paths):
 relative=sorted({str(pathlib.Path(p).relative_to(REPO)) for p in paths if pathlib.Path(p).is_relative_to(REPO)})
 for p in relative:subprocess.run(['git','ls-files','--error-unmatch',p],cwd=REPO,check=True,capture_output=True)
 status=subprocess.check_output(['git','status','--porcelain','--',*relative],cwd=REPO,text=True)
 assert not status,'dependency paths dirty: '+status
 return relative


def reader_preflight(kind):
 c=CONFIG[kind];code=REPO/'src/SPRINT5'/c['reader'];e=REPO/'experiments/SPRINT5_20261114'/c['evidence'];binding=e/'PILOT_READER_BINDING.json';adoption=e/c['adoption']
 assert sha(code/'SHA256SUMS')==c['source_sha'] and sha(binding)==c['binding_sha']
 sys.path.insert(0,str(code));import admission as A
 result=A.validate_binding(binding,require_committed=True) # Actual committed metadata only, no collector/read.
 b=result[0];paths=[binding,code/'SHA256SUMS',adoption,e/c['review'],e/c['acceptance']]+[pathlib.Path(p) for p in b['exact_input_pins']]
 for line in (code/'SHA256SUMS').read_text().splitlines():
  h,n=line.split('  ',1);p=code/n;assert sha(p)==h;paths.append(p)
 adopted=obj(adoption)
 assert adopted['decision']=='GO_INPUT_BINDING_ONLY' and adopted['binding_sha256']==c['binding_sha'] and adopted['scientific_read']=='HOLD'
 assert adopted['author']!=adopted['reviewer'] and adopted['reviewer']
 if kind=='tail':
  assert sha(adoption)=='1d85babbc525f4b3dcf966e988ca7e9eba0caab980f228fa093e4ce25f6c9556'
  assert adopted['baseline_threshold_auxiliary']=='HOLD' and adopted['diagnostic_panels']=='ADOPTED_POINT_ONLY_NOT_ESTIMATED'
  assert adopted['baseline_reporting_requirement']=='REQUIRED_BUT_HOLD_PENDING_SEPARATE_BINDING_AND_ADMISSION'
 else:assert adopted['camera_auxiliary']=='HOLD'
 tracked=git_clean(paths)
 return {'status':'PASS_REAL_COMMITTED_METADATA_BINDING','reader':c['reader'],'binding_sha256':sha(binding),'reader_sums_sha256':sha(code/'SHA256SUMS'),
   'git_tracked_clean_paths':tracked,'git_tracked_clean_count':len(tracked),'input_pin_count':len(b['exact_input_pins']),
   'root_input_admission_path':str(adoption),'root_input_admission_sha256':sha(adoption),
   'prior_independent_code_review_path':str(e/c['review']),'prior_independent_code_review_sha256':sha(e/c['review']),
   'root_acceptance_path':str(e/c['acceptance']),'root_acceptance_sha256':sha(e/c['acceptance']),
   'candidate_archive_members_opened':False,'collector_or_reader_invoked':False,'scientific_read':'HOLD'}


def receipt_index():
 index={};pins={};waiting=[]
 for receipt in RECEIPTS:
  if not receipt.exists():waiting.append(str(receipt));continue
  data=obj(receipt)
  assert data['status']=='OPAQUE_COLLECTION_HASH_VERIFIED' and data['missing']==[] and data['remote_local_sidecar_equal'] is True
  assert data['archive_members_opened'] is False and data['scientific_read_authorized'] is False
  table={r['name']:r for r in data['files']};assert len(table)==len(data['files'])
  assert len([n for n in table if n.endswith('.tar')])==data['archive_count']
  pins[str(receipt)]=sha(receipt)
  for name,record in table.items():
   if not name.endswith('.tar'):continue
   assert pathlib.Path(name).name==name and re.fullmatch('[0-9a-f]{64}',record['sha256'])
   assert name not in index,'duplicate archive across durable receipts'
   index[name]={'archive_path':str(receipt.parent/name),'archive_sha256':record['sha256'],'archive_bytes':record['size'],
       'remote_source_path':record['path'],'transfer_receipt_path':str(receipt),'transfer_receipt_sha256':pins[str(receipt)],
       'sidecar':table[name+'.sha256']}
 return index,pins,waiting


def build():
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');out=PACKROOT/('proposal_'+stamp);out.mkdir(parents=True,exist_ok=False)
 index,receipt_pins,waiting=receipt_index();summary=[]
 for kind,c in CONFIG.items():
  p=out/kind;p.mkdir()
  child=subprocess.run([sys.executable,'-I',str(pathlib.Path(__file__).resolve()),'--preflight-reader',kind],cwd=REPO,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  (p/'PREFLIGHT_STDERR.txt').write_text(child.stderr);assert child.returncode==0,child.stderr
  pre=json.loads(child.stdout);write(p/'INPUT_SOURCE_PREFLIGHT.json',pre)
  expected=[];roster=[];missing=[]
  for seed in c['seeds']:
   for arm in c['arms']:
    task=f"{c['experiment']}_pilot_v1_{arm}_s{seed}";expected.append({'task':task,'arm':arm,'seed':seed})
    name=task+'.tar'
    if name not in index:missing.append(task);continue
    meta=index[name];remote='/lustre/pd03/hpc-narolski-1790461090/smad-next/results/'+c['experiment']+'/pilot_v1/'+name
    assert meta['remote_source_path']==remote,'unregistered archive origin'
    roster.append({'task':task,'arm':arm,'seed':seed,**meta})
  write(p/'EXPECTED_TASKS.json',expected)
  collector_out=COORD/(f'metadata_collection_{kind}_{len(expected)}_20261114T181157Z_v1')
  assert not collector_out.exists(),'fixed collector output must be fresh; never reuse/overwrite'
  if not missing:
   for entry in roster:
    archive=pathlib.Path(entry['archive_path']);assert archive.is_file() and not archive.is_symlink() and archive.stat().st_size==entry['archive_bytes']
    assert sha(archive)==entry['archive_sha256'],'opaque archive differs from durable receipt'
    side=archive.with_name(archive.name+'.sha256');assert side.is_file() and sha(side)==entry['sidecar']['sha256'],'sidecar metadata changed'
    words=side.read_text().strip().split();assert words==[entry['archive_sha256'],archive.name],'sidecar archive binding differs'
    del entry['sidecar']
   write(p/'OPAQUE_ARCHIVE_ROSTER.json',roster)
  roster_path=p/'OPAQUE_ARCHIVE_ROSTER.json';review_path=p/'INDEPENDENT_COLLECTION_PACKET_REVIEW.md'
  proposal={'decision':'PROPOSED_GO_METADATA_COLLECTION_ONLY','required_root_decision':'GO_METADATA_COLLECTION_ONLY','status':'UNSIGNED_REQUIRES_INDEPENDENT_ACTUAL_ROSTER_AND_COLLECTOR_REVIEW',
   'experiment_id':c['experiment'],'scope':c['scope'],'author':'sol_sprint_experiments','reviewer':'root',
   'binding_sha256':c['binding_sha'],'reader_sums_sha256':c['source_sha'],
   'roster_sha256':sha(roster_path) if roster_path.exists() else None,'independent_review_path':str(review_path),'independent_review_sha256':None,
   'input_admission_path':pre['root_input_admission_path'],'input_admission_sha256':pre['root_input_admission_sha256'],
   'fixed_fresh_collector_output':str(collector_out),'scientific_read':'HOLD','camera_auxiliary':'HOLD','baseline_threshold_auxiliary':'REQUIRED_BUT_HOLD_PENDING_SEPARATE_BINDING_AND_ADMISSION' if kind=='tail' else 'NOT_IN_SCOPE',
   'warmstart_provenance':'Pinned worker source and admitted Sb408 archive to checkpoint extraction; no independent checkpoint rehash asserted','independent_checkpoint_rehash':False,
   'archive_members_opened':False,'missing_tasks':missing,'remaining_gate':'Root must issue a separate exact signed release after independent review; this proposal cannot pass actual decision gate'}
  write(p/'PROPOSED_METADATA_COLLECTION_RELEASE.json',proposal)
  state={'status':'READY_FOR_INDEPENDENT_COLLECTION_PACKET_REVIEW' if not missing else 'WAIT_DURABLE_COLLECTION_RECEIPT',
    'expected_archives':len(expected),'arrived_in_durable_receipts':len(roster),'missing_tasks':missing,'waiting_receipts':waiting,
    'receipt_pins':receipt_pins,'opaque_archive_hashes_reverified':not missing,'fixed_output_absent':True,
    'independent_review':'PENDING','root_collection_release':'HOLD','scientific_read':'HOLD','archive_members_opened':False}
  write(p/'PACKET_STATUS.json',state)
  command=f'OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 CUDA_VISIBLE_DEVICES="" nice -n10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I {REPO}/src/SPRINT5/{c["reader"]}/collector.py --archive-roster {roster_path} --release {p}/ROOT_METADATA_COLLECTION_RELEASE.json --out {collector_out}\n'
  (p/'ROOT_COMMAND_AFTER_REVIEW_ONLY.txt').write_text(command)
  if kind=='tail':
   original=REPO/'experiments/SPRINT5_20261114/tail/reader_implementation_v2r1/ROOT_INPUT_ADMISSION.json';compat=pathlib.Path(pre['root_input_admission_path']);a,b=obj(original),obj(compat)
   delta={k:{'original':a.get(k),'compatibility':b.get(k)} for k in sorted(a.keys()|b.keys()) if a.get(k)!=b.get(k)}
   write(p/'ROOT_ADMISSION_COMPAT_EXACT_DELTA.json',{'original_path':str(original),'original_sha256':sha(original),'compat_path':str(compat),'compat_sha256':sha(compat),'delta':delta,'source_and_policy_changed':False})
  summary.append({'kind':kind,'packet_path':str(p),**state})
 write(out/'PREPARATION_SUMMARY.json',{'candidate_archive_members_opened':False,'collector_or_reader_invoked':False,'packets':summary})
 pins={str(q.relative_to(out)):sha(q) for q in sorted(out.rglob('*')) if q.is_file()}
 write(out/'IMMUTABLE_MANIFEST.json',{'preparer_path':str(pathlib.Path(__file__).resolve()),'preparer_sha256':sha(__file__),'files':pins,'scientific_read':'HOLD'})
 print(json.dumps({'packet_root':str(out),'packets':[{'kind':x['kind'],'status':x['status'],'arrived':x['arrived_in_durable_receipts'],'expected':x['expected_archives']} for x in summary]}))


if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--preflight-reader',choices=CONFIG);args=ap.parse_args()
 if args.preflight_reader:print(json.dumps(reader_preflight(args.preflight_reader)))
 else:build()
