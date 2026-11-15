"""Source and prior opaque receipt preparation only; no archive open/stat."""
import pathlib,json,hashlib
R=pathlib.Path('/home/narolski/smad-next');B=R/'experiments/AGENTIC_delivery_20261114';O=B/'NEXT_MINIMAL_TECHNICAL_EXTENSION_V1_20261114';V=B/'NEXT_TECHNICAL_COLLECTOR_V2R1_20261114';E=B/'BB2L_SUBMITTED_BATCH_BINDING_PROPOSAL_20261114'
O.mkdir(exist_ok=False)
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=read(V/'TYPED_SCOPE.json');expect=read(E/'PROPOSED_BINDING.json');records={}
original=pathlib.Path('/mnt/t7/smad_next/recovery_20261114_MAIN/COLLECTION_VERIFIED.json');fit_receipts={pathlib.Path(e['path']).stem:e for e in read(original)['archives']}
rzreceipt=B/'ROOT_RZ1_FIFTEEN_OPAQUE_ARRIVAL_VERIFIED_20261114.json';rz=read(rzreceipt)['archives']
for e in expect['records']:
 key=e['task'];prior=old['archives'][key];size=fit_receipts[key]['bytes'];assert fit_receipts[key]['sha256']==prior['sha256'];assert e['expected_batch']==256 and e['expected_accumulation']==1
 records[key]={'kind':'bb2_batch_match','archive':prior['archive'],'sha256':prior['sha256'],'archive_bytes':size,'historical_expected_binding':e,'historical_dispatch_not_actual_verified_job_identity':True,'members':{key+'/task_info.txt':{'operation':'recipe_tokens','expected':{'bs':256,'accum':1}},key+'/task.env':{'operation':'task_env','expected':{'TASK':key,'ARM':key.split('_')[1],'SEED':int(key.rsplit('s',1)[1])}}}}
for s in range(408,413):
 key=f'RZ1_SbMR512_s{s}';prior=old['archives'][key];e=rz[key+'.tar'];assert e['archive_sha256']==prior['sha256']
 records[key]={'kind':'sbmr512_trainable_hash','archive':prior['archive'],'sha256':prior['sha256'],'archive_bytes':e['bytes'],'member_name_source':'src/RZ1/rz1_score.py:68; src/RZ1/run_rz1.sh:118-122','original_full_checkpoint_hash_is_not_overlay_hash':True,'members':{key+'/last_trainable.pt':{'operation':'opaque_sha256'}}}
paths=[V/'TYPED_SCOPE.json',V/'PACKAGE_SHA256SUMS',V/'ACTUAL_TECHNICAL_POSTREVIEW_20261114.md',V/'ACTUAL_TECHNICAL_POSTREVIEW_CHECKS_20261114.json',E/'PROPOSED_BINDING.json',E/'INDEPENDENT_EXPECTED_BATCH_REVIEW_20261114.md',E/'SOURCE_EXCERPTS.json',original,rzreceipt,R/'src/RZ1/rz1_score.py',R/'src/RZ1/run_rz1.sh',R/'src/NEXT/native_adapters.py',R/'src/NEXT/read_selection.py',pathlib.Path('/mnt/t7/smad_next/NEXT/technical_metadata_v2r1_collection_20261114/TECHNICAL_METADATA.json'),pathlib.Path('/mnt/t7/smad_next/NEXT/technical_metadata_v2r1_collection_20261114/SHA256SUMS')]
pins={str(p):sha(p) for p in paths};pins.update({v['path']:v['sha256'] for v in expect['source_pins'].values()})
adoption=E/'ROOT_EXPECTED_BATCH_ADOPTION.json';acceptance=B/'ROOT_NEXT_TECHNICAL_RESULT_ACCEPTANCE_20261114T200359Z.json'
assert read(adoption)['records']==expect['records']
assert read(acceptance)['scientific_admission'] is False
pins.update({str(p):sha(p) for p in (adoption,acceptance)})
scope={'schema':'next-minimal-technical-extension-v1','status':'PROPOSAL_REQUIRES_OTHER_REVIEW_AND_ROOT_RELEASE','scientific_admission':False,'planned_seed_denominator':5,'records':records,'pins':pins,'unknown_policy':'missing member/token remains UNKNOWN; failures retained; no alternate batch or archive substitution','strict_RZ1R_manifest_disposition':'UNCHANGED_OUT_OF_SCOPE'}
# Use computed exact pin as authority; do not rely on manually transcribed text.
scope['prior_result_sha256']=pins['/mnt/t7/smad_next/NEXT/technical_metadata_v2r1_collection_20261114/TECHNICAL_METADATA.json']
assert len(records)==20
(O/'SCOPE_PROPOSAL.json').write_text(json.dumps(scope,indent=2)+'\n')
print('PREPARED_15_BB2_PLUS_5_OPAQUE_CHECKPOINTS_NO_ARCHIVE_ACCESS')
