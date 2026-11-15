"""Baseline auxiliary source/image metadata only; never opens any result archive/member."""
import csv
import hashlib
import json
import pathlib
import re
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import shared

REPO=pathlib.Path('/home/narolski/smad-next')
OUT=REPO/'experiments/SPRINT5_20261114/tail/baseline_auxiliary_proposal_v1'
BASELINE_SHA='a84b551f2f18c51898213f4932965f89b88fe7eac0398ac28cd37c04e4b3b0aa'
TAIL_SOURCE_SHA='943d47ef9ac0638c46dc1fdaf65782cabbd43d93405ce80305c4bac58c1fce5b'
TAIL_BINDING_SHA='ff2aa74853658d1d318725e42eedbdd2ac16cde8d7da57971c04e4447626c6a2'


def sums(path):
 out={}
 for line in pathlib.Path(path).read_text().splitlines():
  if not line.strip():continue
  h,name=line.split(maxsplit=1);name=name.lstrip('*').removeprefix('./')
  assert re.fullmatch('[0-9a-f]{64}',h) and name not in out
  out[name]=h
 return out


def main():
 assert len(sys.argv)==1,'no archive, score or checkpoint arguments'
 assert not OUT.exists(),'preserve prior proposal; use a new version'
 tail=REPO/'src/SPRINT5/tail_reader_v2r1';assert shared.sha(tail/'SHA256SUMS')==TAIL_SOURCE_SHA
 sys.path.insert(0,str(tail));import admission as A
 bp=REPO/'experiments/SPRINT5_20261114/tail/reader_implementation_v2r1/PILOT_READER_BINDING.json'
 assert shared.sha(bp)==TAIL_BINDING_SHA
 b,meta=A.validate_binding(bp,require_committed=True)
 # Exact original 21277-row dev manifest; no score/checkpoint bytes touched.
 manifest=pathlib.Path('/mnt/t7/smad_next/AB1/overlay_tree/pn1/data/manifests/ab1_eval.csv')
 assert shared.sha(manifest)==shared.load().admit.EVAL_SHA
 rows=list(csv.DictReader(manifest.open()));assert len(rows)==21277 and len({r['id'] for r in rows})==21277
 byid={r['id']:(i,r) for i,r in enumerate(rows)}
 roots=[(pathlib.Path('/mnt/t7/smad_next/PN1/fs_tree/pn1'),'SHA256SUMS'),(pathlib.Path('/mnt/t7/smad_next/AB1/overlay_tree/pn1'),'AB1SUMS')]
 tables=[(root,sums(root/name)) for root,name in roots]
 pins={str(bp):TAIL_BINDING_SHA,str(manifest):shared.sha(manifest),str(tail/'SHA256SUMS'):TAIL_SOURCE_SHA}
 for root,name in roots:pins[str(root/name)]=shared.sha(root/name)
 selected=meta['calibration']+meta['evaluation'];records=[]
 for item in selected:
  i,row=byid[item['id']];assert row['path']==item['path'] and int(row['label'])==int(item['label'])
  assert row['role']=='dev' and item['role']=='dev'
  key='data/'+item['path'];matches=[]
  for root,table in tables:
   if key in table:
    path=root/key;assert path.is_file() and shared.sha(path)==table[key],'input image checksum mismatch '+str(path)
    matches.append((path,table[key]));pins[str(path)]=table[key]
  assert matches,'selected image absent from pinned FS1/AB1 checksums '+key
  assert len({h for _,h in matches})==1,'pack/overlay disagree on selected image bytes'
  records.append({'id':item['id'],'manifest_index':i,'path':item['path'],'label':int(item['label']),
      'source':item['source'],'component':item['component'],'processing':item.get('processing','native'),
      'positive_family':item.get('positive_family'),'image_sha256':matches[0][1],
      'verified_image_paths':[str(p) for p,_ in matches],
      'partition':'positive_calibration' if len(records)<70 else 'evaluation'})
 assert len(records)==538 and sum(r['partition']=='positive_calibration' for r in records)==70
 baseline=pathlib.Path('/mnt/t7/smad_next/AB1/results/AB1_Sb_s408.tar');side=baseline.with_name(baseline.name+'.sha256')
 assert baseline.is_file() and side.read_text().split()[0]==BASELINE_SHA # Sidecar only; no archive open.
 pins[str(side)]=shared.sha(side)
 source=REPO/'src/AB1/run_v2.sh';scorer=pathlib.Path('/mnt/t7/smad_next/PN1/fs_tree/pn1/src/pn1_score.py')
 assert '--eval-manifest ab1_eval.csv' in source.read_text() and 'scores_eval.npz' in scorer.read_text()
 for p in (source,scorer,REPO/'experiments/SPRINT5_20261114/tail/prereg_pilot.md',REPO/'experiments/SPRINT5_20261114/pilot_reader_policy_review/POLICY_PROPOSAL.md',REPO/'experiments/SPRINT5_20261114/tail/TAIL_POSTRESULT_INDEPENDENT_REVIEW_20261114.md'):
  pins[str(p)]=shared.sha(p)
 # Metadata commitments only: original claim/result remain closed and complete.
 original_once=pathlib.Path('/mnt/t7/smad_next/SPRINT5_3/reader_once_primary_ni_v1')
 claim=original_once/'CLAIM.json';terminal=original_once/'TERMINAL.json'
 term=json.loads(terminal.read_text());assert term['status']=='COMPLETE'
 pins[str(claim)]=shared.sha(claim);pins[str(terminal)]=shared.sha(terminal)
 for p in (pathlib.Path(__file__).resolve(),pathlib.Path(shared.__file__).resolve()):pins[str(p)]=shared.sha(p)
 OUT.mkdir(parents=True)
 (OUT/'EXACT_538_ID_IMAGE_MAPPING.json').write_text(json.dumps(records,indent=2)+'\n')
 mapping=OUT/'EXACT_538_ID_IMAGE_MAPPING.json';pins[str(mapping)]=shared.sha(mapping)
 output={'status':'HOLD_AUXILIARY_POLICY_AND_BASELINE_SCORE_ADMISSION','timing':'Primary results already read and independently reviewed; auxiliary reporting was registered earlier, present implementation/policy clarification is after primary outcomes were seen',
   'baseline_archive_path':str(baseline),'baseline_archive_sha256':BASELINE_SHA,'archive_current_access':'stat and admitted sidecar only; no archive bytes/member opened or independently rehashed here',
   'baseline_score_member':'AB1_Sb_s408/scores_eval.npz','baseline_score_member_sha256':None,
   'member_binding_basis':'Admitted whole-archive hash plus exact source-established member name; actual unique-member/NPZ identity/schema/digest admission still HOLD',
   'expected_score_field':'logit','expected_full_manifest_rows':21277,'expected_manifest_sha256':shared.sha(manifest),
   'positive_calibration_ids':[r['id'] for r in meta['calibration']],
   'evaluation_ids':[r['id'] for r in meta['evaluation']],
   'calibration_rows':70,'positive_evaluation_rows':180,'genuine_evaluation_rows':288,
   'input_image_rows_hash_verified':len(records),'id_path_label_native_history_mapping':'PASS_INPUT_METADATA_ONLY; no NPZ ID alignment asserted',
   'threshold_rule_from_adopted_policy':'strict> nextafter(sortedSb408positive[floor(.10*n)],-inf), same original70positive IDs, one common baseline threshold',
   'TRAIN_ONLY_reference_is_evaluation_threshold':False,'candidate_scope_proposal':'Existing15models evaluation468IDs only for fixed-original-baseline auxiliary; own-recalibrated companion values from pinned existing primary result; no primary rerun/rebootstrap',
   'primary_claim_path':str(claim),'primary_claim_sha256':pins[str(claim)],'primary_terminal_path':str(terminal),'primary_terminal_sha256':pins[str(terminal)],
   'new_primary_claim_permitted':False,'auxiliary_journal_and_release':'HOLD_PENDING_SEPARATE_POLICY_REVIEW_AND_ROOT_ADOPTION',
   'baseline_source_technical_gate_evidence':'Earlier root training-baseline/ownfit source gates support reuse; fresh auxiliary member/finiteness/ID alignment not yet inspected or admitted',
   'exact_mapping_path':str(mapping),'exact_mapping_sha256':pins[str(mapping)],'pins':pins,
   'baseline_scores_NPZ_checkpoint_archive_member_accessed':False,'reader_executed':False,'camera_auxiliary':'HOLD','scientific_auxiliary_read':'HOLD','GPU_required_by_this_proposal':False}
 (OUT/'INPUT_BINDING_PROPOSAL.json').write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps({'status':output['status'],'rows':len(records),'calibration':70,'evaluation':468,'image_bytes_hash_verified':True,'raw_baseline_or_candidate_payload_accessed':False,'primary_terminal':'COMPLETE'}))


if __name__=='__main__':main()
