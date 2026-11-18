"""Fail-closed future release validation; no model/data/scheduler imports."""
import hashlib,json,pathlib,time,math
ROOT=pathlib.Path('/lustre/pd03/hpc-narolski-1790461090/smad-next/AD5')
SOURCE=ROOT/'ad5_full_math_v2'
JOURNAL=ROOT/'dispatch/ad5_full_math_v2_20261114'
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
def release(seed,submission=False):
 assert type(seed) is int and seed in range(401,406)
 j=JOURNAL/('s%d'%seed);r=json.loads((j/'ROOT_RELEASE.json').read_text())
 assert r['decision']=='GO_ONE_NEW_FULL_B_MATH_V2_SEED' and r['root_authorized'] is True
 assert r['seed']==seed and r['cohort_seeds']==[401,402,403,404,405] and r['arm']=='B'
 assert r['automatic_retry'] is False and r['scientific_read']=='HOLD' and r['converter_execution']=='HOLD'
 assert r['cohort']=='NEW_LATE_RECOVERY' and r['arrival_deadline']=='2026-11-15T18:00:00+01:00'
 assert r['root_smoke_acceptance_sha256']=='0eba6268b5e0c759bb89b4a051794d6944966a3c9d916d1e8aa50d0dbb21366b'
 assert r['root_late_ruling_sha256']=='e8a6909574a6062e7fdf0faf18a342d7697be9077f258ac1d2330466d2ea7624'
 assert r['author']!=r['reviewer'] and r['owned_source_clean_committed'] is True
 assert r['source_manifest_sha256']==sha(SOURCE/'SHA256SUMS')
 for line in (SOURCE/'SHA256SUMS').read_text().splitlines():
  digest,name=line.split('  ',1);p=SOURCE/name
  assert p.resolve().is_relative_to(SOURCE.resolve()) and sha(p)==digest
 assert r['full_csv_sha256']=='83c01705e140843afa6cb4c89765d0528ff21e2f444aee23aa50de49eaf894a3'
 assert r['resource_profile']==dict(partition='lem-gpu-short',gpus=1,cpus=8,mem_gib=120,local_gib=150,wall_seconds=21600,child_seconds=21000,collection_seconds=300,concurrency=1)
 for key in ('independent_review','prereg','root_late_ruling','root_smoke_acceptance','commit_check','site_capacity','budget_ledger'):
  name=r[key+'_file'];assert pathlib.Path(name).name==name and sha(j/name)==r[key+'_sha256']
 budget=json.loads((j/r['budget_ledger_file']).read_text());assert budget['accounting_convention_explicit'] is True and type(budget['available_h100_hours']) in (float,int) and math.isfinite(budget['available_h100_hours']) and budget['available_h100_hours']>=6 and budget['reserved_this_seed_hours']==6
 site=json.loads((j/r['site_capacity_file']).read_text());assert site['no_duplicate_seed_active'] is True and site['no_other_full_v2_fit_active'] is True and site['six_hour_profile_supported'] is True and site['durable_free_gib']>=50
 if submission:
  assert 0<=time.time()-site['checked_epoch']<=900
  # Sequential401..405; completed/failed previous allocations explicitly closed by root.
  for prior in range(401,seed):
   q=JOURNAL/('s%d'%prior);claim=json.loads((q/'CLAIM.json').read_text());closed=json.loads((q/'ROOT_NATIVE_CLOSED.json').read_text())
   assert closed['root_confirmed_terminal'] is True and closed['seed']==prior and closed['claim_sha256']==sha(q/'CLAIM.json')
   assert closed['native_state'] in ('COMPLETED','FAILED','TIMEOUT','CANCELLED','OUT_OF_MEMORY','NODE_FAIL')
   name=closed['native_receipt_file'];assert pathlib.Path(name).name==name and sha(q/name)==closed['native_receipt_sha256']
  assert not any((JOURNAL/('s%d'%later)/'CLAIM.json').exists() for later in range(seed+1,406))
 return r
