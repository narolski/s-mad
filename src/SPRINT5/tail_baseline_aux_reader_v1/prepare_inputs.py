"""New immutable auxiliary binding from admitted source/input/claim metadata only."""
import json
import pathlib
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import bridge
import metadata as M
import policy as P


def main():
    M.need(len(sys.argv)==1,'no archive/payload arguments')
    repo=pathlib.Path(P.ROOT);out=repo/'experiments/SPRINT5_20261114/tail/baseline_aux_reader_v1'
    M.need(not out.exists(),'preserve frozen binding; use a reviewed revision')
    prior=repo/'experiments/SPRINT5_20261114/tail/baseline_auxiliary_proposal_v1'
    old=prior/'INPUT_BINDING_PROPOSAL.json';M.need(bridge.sha(old)=='d5587ad6c87cee2ddc13e4cb101d9c9887276bd3d0cdc4d9b09f36c89ada7987','old proposal changed')
    mapping=prior/'EXACT_538_ID_IMAGE_MAPPING.json';M.need(bridge.sha(mapping)=='3e20efb6336f2a9aed2439b154539d30bdfe7630e37118455dab3c8a03c61138','mapping changed')
    candidatesp=prior/'EXACT_15_CANDIDATE_AUX_MEMBER_PROPOSAL.json';M.need(bridge.sha(candidatesp)=='090770040496d687e12aa13e579c2d9504ef3681061d777932142853cb084972','candidate metadata changed')
    proposal=M.obj(old);candidates=M.obj(candidatesp);pins=dict(proposal['pins'])
    for p in (old,mapping,candidatesp,pathlib.Path(P.POLICY_PATH)):
        pins[str(p)]=bridge.sha(p)
    M.need(pins[P.POLICY_PATH]==P.POLICY_SHA,'auxiliary policy changed')
    adoption=M.obj(P.POLICY_PATH)
    for key in ('plan','independent_review'):
        p=pathlib.Path(adoption[key+'_path']);M.need(bridge.sha(p)==adoption[key+'_sha256'],'policy evidence changed');pins[str(p)]=bridge.sha(p)
    # Preserve full original source and COMPLETE artifacts; result bytes are only
    # hashed, never decoded by preparation or metadata admission.
    primary=repo/'src/SPRINT5/tail_reader_v2r1';M.need(bridge.sha(primary/'SHA256SUMS')==P.PRIMARY_SOURCE_SHA,'original source changed')
    files={
      'result':{'path':P.PRIMARY_RESULT,'sha256':P.PRIMARY_RESULT_SHA},
      'claim':{'path':P.PRIMARY_ONCE+'/CLAIM.json','sha256':proposal['primary_claim_sha256']},
      'terminal':{'path':P.PRIMARY_ONCE+'/TERMINAL.json','sha256':proposal['primary_terminal_sha256']},
      'release':{'path':candidates['primary_release_path'],'sha256':candidates['primary_release_sha256']},
      'source_manifest':{'path':str(primary/'SHA256SUMS'),'sha256':P.PRIMARY_SOURCE_SHA},
      'input_binding':{'path':str(repo/'experiments/SPRINT5_20261114/tail/reader_implementation_v2r1/PILOT_READER_BINDING.json'),'sha256':P.PRIMARY_BINDING_SHA}}
    for line in (primary/'SHA256SUMS').read_text().splitlines():
        h,name=line.split('  ',1);files['source_'+name]={'path':str(primary/name),'sha256':h};pins[str(primary/name)]=h
    pins[str(primary/'SHA256SUMS')]=P.PRIMARY_SOURCE_SHA
    for entry in candidates['cases']:pins[entry['admitted_metadata_envelope_path']]=entry['admitted_metadata_envelope_sha256']
    # Independent root gate source chain, not a new observed NPZ/runtime pass.
    gatefiles=[prior/'BASELINE_EXISTING_GATE_CHAIN_PROPOSAL.json',prior/'BASELINE_RUN_SOURCE_LINK_PROPOSAL.json',repo/'experiments/SPRINT5_20261114/tail/BASELINE_ADMISSION_ROOT.json',repo/'experiments/SPRINT5_20261114/tail/TRAIN_BASELINE_RELEASE.json',repo/'experiments/SPRINT5_20261114/tail/PILOT_RELEASE.json']
    baseline_source=repo/'src/SPRINT5/tail_baseline';release=M.obj(gatefiles[3]);rootgate=M.obj(gatefiles[2]);pilot=M.obj(gatefiles[4])
    M.need(bridge.sha(baseline_source/'SHA256SUMS')==release['source_sums_sha256'],'baseline producer changed')
    M.need(rootgate['decision']=='ADMIT_TRAIN_ONLY_CONSTANTS' and rootgate['reviewer']!=rootgate['author'],'existing root gate not independently admitted')
    M.need(rootgate['archive_sha256']==pilot['baseline_archive_sha256'] and 'strictreferenceand21277ownfitbytegatePASS' in rootgate['independently_recomputed'],'existing same-baseline gate chain incomplete')
    for p in gatefiles+[baseline_source/'SHA256SUMS']:pins[str(p)]=bridge.sha(p)
    for line in (baseline_source/'SHA256SUMS').read_text().splitlines():
        h,name=line.split('  ',1);M.need(bridge.sha(baseline_source/name)==h,'baseline source checksum');pins[str(baseline_source/name)]=h
    M.need(P.BASELINE_SHA in (baseline_source/'run.sh').read_text(),'baseline producer target mismatch')
    common=pathlib.Path('/mnt/t7/smad_next/PN1/fs_tree/pn1/code/smadcvpr/common.py');expected_common=bridge.sha(common);pins[str(common)]=expected_common
    # Freeze the old proposal and the only imported durable helper without editing them.
    oldsource=repo/'src/SPRINT5/tail_baseline_aux_proposal_v1';M.need(bridge.sha(oldsource/'SHA256SUMS')=='0af907330e1d827486c8965630d3a54d1d502b574aa5aa39ca14defc8a6df099','old source changed')
    pins[str(oldsource/'SHA256SUMS')]=bridge.sha(oldsource/'SHA256SUMS')
    pins[str(bridge.ROOT/'SHA256SUMS')]=bridge.SUMS_SHA
    durable={n:h for h,n in (line.split('  ',1) for line in (bridge.ROOT/'SHA256SUMS').read_text().splitlines())};pins[str(bridge.ROOT/'journal.py')]=durable['journal.py']
    for pin,h in pins.items():M.need(bridge.sha(pin)==h,'input/image/metadata pin mismatch '+pin)
    M.need(not pathlib.Path(P.ONCE).exists() and not pathlib.Path(P.OUTPUT).exists() and not pathlib.Path(P.TECHDIR).exists(),'auxiliary paths must be fresh; no alternate version bypass')
    out.mkdir(parents=True)
    chain=out/'BASELINE_GATE_REUSE_CHAIN.json'
    chain.write_text(json.dumps({'status':'EXISTING_ROOT_ADMITTED_SAME_BASELINE_SOURCE_CHAIN_NOT_NEW_PAYLOAD_PASS','files':{str(p):bridge.sha(p) for p in gatefiles},
        'source_manifest_path':str(baseline_source/'SHA256SUMS'),'source_manifest_sha256':release['source_sums_sha256'],
        'baseline_archive_sha256':P.BASELINE_SHA,'actual_archive_or_NPZ_accessed':False,
        'reuse_requires_independent_technical_admission':True},indent=2)+'\n')
    pins[str(chain)]=bridge.sha(chain)
    b={'schema_version':1,'experiment_id':P.EXPERIMENT,'scope':P.READ_SCOPE,'timing':P.TIMING,
       'status':'PREPARED_REQUIRES_INDEPENDENT_CODE_INPUT_REVIEW_AND_ROOT_ADOPTION','policy_adoption_sha256':P.POLICY_SHA,
       'auxiliary_once':P.ONCE,'auxiliary_output':P.OUTPUT,'technical_directory':P.TECHDIR,
       'baseline_archive':P.BASELINE,'baseline_archive_sha256':P.BASELINE_SHA,'baseline_score_member':P.MEMBER,
       'baseline_score_member_sha256':'UNKNOWN_UNTIL_TECHNICAL_CAPTURE','expected_common_py_sha256':expected_common,
       'manifest_path':P.EVAL,'manifest_sha256':P.EVAL_SHA,'mapping_path':str(mapping),
       'calibration_ids':proposal['positive_calibration_ids'],'evaluation_ids':proposal['evaluation_ids'],
       'candidates':candidates['cases'],'candidate_roster_sha256':candidates['primary_roster_sha256'],
       'primary_files':files,'baseline_gate_chain_path':str(chain),'baseline_gate_chain_sha256':bridge.sha(chain),
       'pins':pins,'technical_member_access':'HOLD','scientific_auxiliary_read':'HOLD','camera_auxiliary':'HOLD',
       'serialization_policy':'Full21277container validation ONLYafter permanentauxclaim; numericstatistics/output ONLYbaseline538/candidate468',
       'primary_rerun_or_new_primary_claim':False,'independent_checkpoint_rehash':False}
    (out/'INPUT_BINDING.json').write_text(json.dumps(b,indent=2)+'\n')
    M.validate(P.BINDING,require_committed=False)
    print(json.dumps({'status':b['status'],'input_pins':len(pins),'candidate_models':len(b['candidates']),'baseline_calibration_ids':70,'evaluation_ids':468,
       'primary_result_only_hashed_not_decoded':True,'archive_member_NPZ_checkpoint_access':False,'technical_member_access':'HOLD','scientific_auxiliary_read':'HOLD'}))


if __name__=='__main__':main()
