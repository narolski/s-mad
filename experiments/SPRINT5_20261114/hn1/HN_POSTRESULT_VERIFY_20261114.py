import json,hashlib,math
from pathlib import Path
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
J=lambda p:json.loads(Path(p).read_text())
repo=Path('/home/narolski/smad-next'); hn=repo/'experiments/SPRINT5_20261114/hn1'; src=repo/'src/SPRINT5/hn1_reader'; pkt=repo/'experiments/SPRINT5_20261114/collection_admission_packet_hn_20261114/proposal_20261114T181619070351Z/hn'; out=Path('/mnt/t7/smad_next/SPRINT5_2'); col=Path('/mnt/t7/smad_next/coordination_20261114/metadata_collection_hn_10_20261114T181157Z_v1')
r=J(out/'reader_output_v1/RESULT.json');c=J(out/'reader_once_v1/CLAIM.json');t=J(out/'reader_once_v1/TERMINAL.json');rel=J(pkt/'ROOT_PRIMARY_READ_RELEASE.json');ro=J(col/'READER_ROSTER.json')
assert t['status']=='COMPLETE' and H(out/'reader_output_v1/RESULT.json')==t['sha256']
assert H(pkt/'ROOT_PRIMARY_READ_RELEASE.json')==c['release_sha256'] and rel['decision']=='GO_READER_READ'
assert H(hn/'reader_implementation/PILOT_READER_BINDING.json')==r['binding_sha256']==c['binding_sha256']==rel['binding_sha256']
assert H(src/'SHA256SUMS')==r['reader_sums_sha256']==c['reader_sums_sha256']==rel['reader_sums_sha256']
for line in (src/'SHA256SUMS').read_text().splitlines():
 expected,name=line.split(maxsplit=1); f=Path(name); f=f if f.is_absolute() else src/f
 assert H(f)==expected,(str(f),expected)
assert H(col/'READER_ROSTER.json')==c['roster_sha256']==rel['roster_sha256']
assert H(rel['independent_review_path'])==rel['independent_review_sha256']=='731145d479dc721cfc1d3173986bdabcd95128db943ef203f54c4633d368e798'
assert [v['archive_sha256'] for v in ro]==c['archive_sha256']==r['archive_sha256']
assert {(v['arm'],v['seed']) for v in ro}=={(a,s) for a in ('matched','self') for s in range(531,536)} and len(ro)==10
fits=[]
for v in ro:
 assert H(v['receipt_path'])==v['receipt_sha256']; d=J(v['receipt_path'])
 assert d['task']==v['task'] and d['archive_sha256']==v['archive_sha256'] and d['training_complete'] and d['checkpoint_saved']
 assert (d['steps'],d['batch_size'],d['forwards'])==(100,248,24800)
 fits.append({'task':v['task'],'metadata_sha256':v['receipt_sha256'],'training_complete':True,'training_duration':'NOT_RECORDED_IN_ADMITTED_ENVELOPE'})
p=r['primary']; effects=[a-b for a,b in zip(*p['per_network_AUC'])];assert effects==p['per_seed_matched_minus_self'];mean=sum(effects)/5; assert abs(mean-p['mean_gain'])<1e-15
assert p['positive_seed_effects']==sum(x>0 for x in effects)==0 and p['label']=='CRITERIA_NOT_MET';assert p['criteria']=={'mean_gain_at_least':.03,'positive_seed_effects_at_least':4}
def q(x,p):
 x=sorted(x);z=(len(x)-1)*p;i=int(z);return x[i]+(x[min(i+1,len(x)-1)]-x[i])*(z-i)
rep=r['all_bootstrap_replicates'];assert len(rep)==10000 and [v['draw'] for v in rep]==list(range(10000))
for v in rep:assert abs(v['arm_mean_AUC'][0]-v['arm_mean_AUC'][1]-v['matched_minus_self'])<1e-15
ci=[q([v['matched_minus_self'] for v in rep],p) for p in (.025,.975)];assert all(abs(a-b)<1e-15 for a,b in zip(ci,r['primary']['interval']))
for a,comp in enumerate(r['fixed_floors']['comparisons']):
 vals=[v['arm_mean_AUC'][a]-v['max_floor_AUC'] for v in rep];assert all(abs(q(vals,p)-target)<1e-15 for p,target in zip((.025,.975),comp['interval']))
 assert abs(sum(r['primary']['per_network_AUC'][a])/5-r['fixed_floors']['maximum_AUC']-comp['seed_mean_minus_max_floor'])<1e-15
assert len(r['fixed_floors']['per_predictor_AUC'])==15 and max(r['fixed_floors']['per_predictor_AUC'])==r['fixed_floors']['maximum_AUC']
seedhash=hashlib.sha256(json.dumps([v['paired_seed_indices'] for v in rep],separators=(',',':')).encode()).hexdigest();assert seedhash==r['bootstrap']['paired_seed_draw_sha256']
meta=J(hn/'reader_implementation/BOOTSTRAP_READABILITY_METADATA.json')
receipt={'status':'PASS_INDEPENDENT_SAVED_RESULT_ARITHMETIC_AND_INTEGRITY','result_sha256':t['sha256'],'release_sha256':c['release_sha256'],'claim_sha256':H(out/'reader_once_v1/CLAIM.json'),'terminal_sha256':H(out/'reader_once_v1/TERMINAL.json'),'binding_sha256':r['binding_sha256'],'reader_sums_sha256':r['reader_sums_sha256'],'roster_sha256':c['roster_sha256'],'means':[sum(a)/5 for a in p['per_network_AUC']],'effects':effects,'gain':mean,'interval':ci,'bootstrap':r['bootstrap'],'readability_metadata':meta,'fits':fits,'recomputed_floor_intervals':True,'source_manifest_files_verified':True}
(hn/'HN_POSTRESULT_INDEPENDENT_VERIFICATION_20261114.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k not in ('fits','readability_metadata')},indent=2));print('readability',str(meta)[:1300])
