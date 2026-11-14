"""Bind adopted positive-calibration/evaluation source metadata only, no candidate arguments."""
import ast
import collections
import csv
import hashlib
import json
import pathlib
import random
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import shared
import policy as P
import tail_inputs
import tail_stats
import diagnostics


def main():
    assert len(sys.argv)==1,'candidate arguments forbidden'
    repo=pathlib.Path(P.ROOT);out=repo/'experiments/SPRINT5_20261114/tail/reader_implementation_v2r1'
    out.mkdir(parents=True,exist_ok=True);assert not(out/'PILOT_READER_BINDING.json').exists(),'never overwrite binding'
    bp=repo/'experiments/SPRINT5_20261114/paired_ranking/prefit_binding_v1/BINDING.json';assert shared.sha(bp)==shared.BINDING_SHA
    S=shared.load();sb=json.loads(bp.read_text());common=S.data.metadata(sb);pins=dict(sb['pins']);pins[str(bp)]=shared.BINDING_SHA
    source=repo/'src/SPRINT5/tail_fit'
    for root,expected in ((shared.ROOT,shared.SUMS_SHA),(source,P.TRAIN_SOURCE)):
        assert shared.sha(root/'SHA256SUMS')==expected;pins[str(root/'SHA256SUMS')]=expected
        for line in (root/'SHA256SUMS').read_text().splitlines():
            h,n=line.split('  ',1);assert shared.sha(root/n)==h;pins[str(root/n)]=h
    pol=pathlib.Path(P.POLICY_ROOT);pb=pol/'BINDING_PROPOSAL.json';ps=pol/'SHA256SUMS';pa=pol/'ROOT_POLICY_INPUT_ADMISSION.json'
    assert shared.sha(pb)==P.POLICY_BINDING_SHA and shared.sha(ps)==P.PACKET_SHA
    for path,h in json.loads(pb.read_text())['input_pins'].items():assert shared.sha(path)==h;pins[path]=h
    a=json.loads(pa.read_text());assert a['decision']=='GO_POLICY_INPUTS_ONLY' and a['binding_sha256']==P.POLICY_BINDING_SHA and a['packet_manifest_sha256']==P.PACKET_SHA and a['scientific_read']=='HOLD'
    rp=pathlib.Path(a['root_review_path']);assert shared.sha(rp)==a['root_review_sha256']
    for p in (pb,ps,pa,rp):pins[str(p)]=shared.sha(p)
    prereg=repo/'experiments/SPRINT5_20261114/tail/prereg_pilot.md';release=prereg.parent/'PILOT_RELEASE.json';baseline=prereg.parent/'BASELINE_ADMISSION_ROOT.json'
    pilot=json.loads(release.read_text());ref=json.loads(baseline.read_text())
    assert pilot['decision']=='GO_PILOT' and pilot['seeds']==list(P.SEEDS) and pilot['source_sums_sha256']==P.TRAIN_SOURCE
    assert ref['decision']=='ADMIT_TRAIN_ONLY_CONSTANTS' and ref['reference_sha256']==P.REFERENCE_SHA and ref['archive_sha256']==pilot['baseline_archive_sha256']
    for p in (prereg,release,baseline):pins[str(p)]=shared.sha(p)
    da=pol/'ROOT_TAIL_DIAGNOSTIC_ADOPTION.json';assert shared.sha(da)==P.DIAGNOSTIC_ADOPTION_SHA
    adoption=json.loads(da.read_text());assert adoption['primary_unchanged'] is True
    for k in ('proposal','independent_review'):
        q=pathlib.Path(adoption[k+'_path']);assert shared.sha(q)==adoption[k+'_sha256'];pins[str(q)]=shared.sha(q)
    for path,h in adoption['input_pins'].items():assert shared.sha(path)==h;pins[path]=h
    pins[str(da)]=P.DIAGNOSTIC_ADOPTION_SHA
    b={'calibration_path':str(pol/'TAIL_POSITIVE_CALIBRATION_PROPOSAL.json'),
       'positive_evaluation_path':str(pol/'TAIL_POSITIVE_EVALUATION_PROPOSAL.json'),
       'genuine_evaluation_path':str(pol/'TAIL_GENUINE_EVALUATION_PROPOSAL.json')}
    meta=tail_inputs.load(b,common['manifests']['dev']);diagnostics.pools(meta);_,report=tail_stats.design(meta)
    dp=out/'BOOTSTRAP_METADATA.json';dp.write_text(json.dumps(report,indent=2)+'\n');pins[str(dp)]=shared.sha(dp)
    # Recompute exact registered training schedules without torch/model execution.
    path=source/'tail_runtime.py';tree=ast.parse(path.read_text());node=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='make_plan'];assert len(node)==1
    ns={'collections':collections,'random':random};exec(compile(ast.Module(body=node,type_ignores=[]),str(path),'exec'),ns)
    train=pathlib.Path('/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/train_Sb.csv');rows=list(csv.DictReader(train.open()))
    metadata={r['path']:r for r in csv.DictReader((source/'training_identity_groups.csv').open())}
    cpu=prereg.parent/'CPU_REAL_SAMPLER_SMOKE.json';prior={x['seed']:x for x in json.loads(cpu.read_text())};pins[str(cpu)]=shared.sha(cpu);pins[str(train)]=shared.sha(train)
    expected=[]
    for seed in P.SEEDS:
        batches=ns['make_plan'](rows,metadata,seed,100)
        digest=hashlib.sha256(json.dumps(batches,separators=(',',':')).encode()).hexdigest()
        assert prior[seed]['shared_schedule_sha256']==digest and prior[seed]['image_exposures_per_arm']==25600
        schedule={'seed':seed,'steps':100,'bs':256,'row_exposures':25600,'schedule_sha256':digest,
          'camera_per_step':118,'positive_per_step':128,'protocol_controls_per_step':10,'smallest_camera_group_ids':22,
          'common_warmstart':'AB1_Sb_s408; conditional continuation'}
        exposure=collections.Counter(i for batch in batches for i in batch)
        eh=hashlib.sha256(json.dumps(sorted(exposure.items()),separators=(',',':')).encode()).hexdigest()
        for arm in P.ARMS:expected.append({'arm':arm,'seed':seed,'schedule':schedule,'train_manifest_sha256':shared.sha(train),'exposure_sha256':eh,'rows_per_fit':25600})
    ep=out/'EXPECTED_PLANS.json';ep.write_text(json.dumps(expected,indent=2)+'\n');pins[str(ep)]=shared.sha(ep)
    for p in (pathlib.Path(__file__).resolve(),pathlib.Path(tail_inputs.__file__).resolve(),pathlib.Path(tail_stats.__file__).resolve(),pathlib.Path(shared.__file__).resolve(),pathlib.Path(P.__file__).resolve(),pathlib.Path(diagnostics.__file__).resolve()):pins[str(p)]=shared.sha(p)
    b.update(schema_version=1,experiment_id=P.EXPERIMENT,status='PREPARED_REQUIRES_ROOT_ADOPTION',scope=P.SCOPE,
       arms=list(P.ARMS),seeds=list(P.SEEDS),expected_fit_count=15,steps=100,batch_size=256,forwards=25600,checkpoint='last',
       training_source_sums_sha256=P.TRAIN_SOURCE,shared_reader_sums_sha256=shared.SUMS_SHA,
       shared_input_binding=str(bp),shared_input_binding_sha256=shared.BINDING_SHA,
       policy_binding_path=str(pb),policy_binding_sha256=P.POLICY_BINDING_SHA,policy_packet_manifest_path=str(ps),policy_packet_manifest_sha256=P.PACKET_SHA,
       policy_input_admission_path=str(pa),policy_input_admission_sha256=pins[str(pa)],root_policy_path=str(rp),root_policy_sha256=pins[str(rp)],
       prereg_path=str(prereg),prereg_sha256=pins[str(prereg)],pilot_release_path=str(release),pilot_release_sha256=pins[str(release)],
       baseline_admission_path=str(baseline),baseline_admission_sha256=pins[str(baseline)],training_reference_sha256=P.REFERENCE_SHA,
       expected_plans_path=str(ep),expected_plans_sha256=pins[str(ep)],draw_metadata_path=str(dp),draw_metadata_sha256=pins[str(dp)],
       threshold_rule='strict> nextafter(sortedpositive[floor(.10*n)],-inf)',
       calibration_rows=70,calibration_components=26,positive_evaluation_rows=180,positive_evaluation_components=27,genuine_evaluation_rows=288,genuine_cells=6,
       NI_guards=8,NI_alpha=.00625,NI_margin=-.02,NI_support_components_minimum=20,
       overall_utility_known_from_metadata='INCONCLUSIVE_MISSING_OR_SPARSE_POSITIVE_FAMILIES',
       exact_input_pins=pins,camera_auxiliary='HOLD',baseline_threshold_auxiliary='HOLD',
       diagnostic_panels='ADOPTED_POINT_ONLY_NOT_ESTIMATED',diagnostic_adoption_path=str(da),diagnostic_adoption_sha256=P.DIAGNOSTIC_ADOPTION_SHA,implementation_review='PENDING',scientific_read='HOLD')
    (out/'PILOT_READER_BINDING.json').write_text(json.dumps(b,indent=2)+'\n')
    print(json.dumps({'status':b['status'],'candidate_payload_accessed':False,'calibration_rows':70,'positive_evaluation_rows':180,'genuine_evaluation_rows':288,
          'plans':len(expected),'draws':report['attempts'],'empty_guard_draws':report['empty_sparse_or_absent_guard_draws'],'overall_utility':'INCONCLUSIVE'}))


if __name__=='__main__':main()
