"""Tail-specific complete15fit metadata and independently gated release admission."""
import json
import pathlib
import re
import subprocess
import sys
import policy as P
import shared
import tail_inputs
import tail_stats


def need(condition,message):
    if not condition:raise ValueError(message)


def obj(path):return json.loads(pathlib.Path(path).read_text())


def cases(binding):
    rr=obj(binding['expected_plans_path']);need(len(rr)==15,'expected15plans')
    return {(r['arm'],r['seed']):r for r in rr}


def committed_paths(binding_path,binding,repo,code):
    """Keep the actual binding first, independently of iteration over input pins."""
    own=[pathlib.Path(binding_path).relative_to(repo)]
    own.extend(pathlib.Path(pin_path).relative_to(repo) for pin_path in binding['exact_input_pins'] if pathlib.Path(pin_path).is_relative_to(repo))
    own.extend((code/name).relative_to(repo) for name in ['SHA256SUMS',*[line.split('  ',1)[1] for line in (code/'SHA256SUMS').read_text().splitlines()]])
    return own


def require_clean_committed(repo,paths):
    for tracked_path in paths:
        subprocess.run(['git','ls-files','--error-unmatch',str(tracked_path)],cwd=repo,check=True,capture_output=True)
    need(not subprocess.check_output(['git','status','--porcelain','--',*[str(tracked_path) for tracked_path in paths]],cwd=repo,text=True),'reader/input paths must be clean committed')


def validate_binding(path,require_committed=False):
    binding_path=pathlib.Path(path).resolve()
    b=obj(binding_path);S=shared.load()
    need(b['experiment_id']==P.EXPERIMENT and b['scope']==P.SCOPE,'wrong scope')
    need(b['arms']==list(P.ARMS) and b['seeds']==list(P.SEEDS) and b['expected_fit_count']==15,'wrong roster')
    need((b['steps'],b['batch_size'],b['forwards'],b['checkpoint'])==(100,256,25600,'last'),'wrong budget')
    need(b['training_source_sums_sha256']==P.TRAIN_SOURCE and b['shared_reader_sums_sha256']==shared.SUMS_SHA,'source changed')
    need(b['shared_input_binding_sha256']==shared.BINDING_SHA and shared.sha(b['shared_input_binding'])==shared.BINDING_SHA,'shared inputs changed')
    need(b['camera_auxiliary']=='HOLD' and b['baseline_threshold_auxiliary']=='HOLD' and b['diagnostic_panels']=='ADOPTED_POINT_ONLY_NOT_ESTIMATED','auxiliary scope changed')
    for pin_path,h in b['exact_input_pins'].items():need(shared.sha(pin_path)==h,'input pin changed '+pin_path)
    need(shared.sha(b['policy_binding_path'])==P.POLICY_BINDING_SHA and shared.sha(b['policy_packet_manifest_path'])==P.PACKET_SHA,'policy packet changed')
    adopted=obj(b['policy_input_admission_path'])
    need(adopted['decision']=='GO_POLICY_INPUTS_ONLY' and adopted['binding_sha256']==P.POLICY_BINDING_SHA and adopted['packet_manifest_sha256']==P.PACKET_SHA,'policy not adopted')
    need(adopted['author']!=adopted['reviewer'] and adopted['scientific_read']=='HOLD','policy adoption cannot release payload')
    need(shared.sha(b['root_policy_path'])==adopted['root_review_sha256'],'root policy changed')
    pilot=obj(b['pilot_release_path']);need(pilot['decision']=='GO_PILOT' and pilot['source_sums_sha256']==P.TRAIN_SOURCE and pilot['seeds']==list(P.SEEDS),'fit release changed')
    need(obj(b['baseline_admission_path'])['reference_sha256']==P.REFERENCE_SHA,'training reference changed')
    policy=obj(b['policy_binding_path'])['tail']
    need(policy['arms']==list(P.ARMS) and policy['seeds']==list(P.SEEDS) and policy['rng']==P.RNG,'tail policy changed')
    need(policy['simultaneous_NI_guards']==8 and policy['NI_one_sided_alpha']==P.NI_ALPHA and policy['NI_margin']==P.NI_MARGIN,'NI family changed')
    need(policy['NI_support_components_minimum']==20 and policy['bootstrap_attempts']==10000,'support or draws changed')
    need(shared.sha(b['diagnostic_adoption_path'])==P.DIAGNOSTIC_ADOPTION_SHA,'diagnostic adoption changed')
    diagnostic=obj(b['diagnostic_adoption_path'])
    need(diagnostic['decision']=='GO_PROSPECTIVE_DIAGNOSTIC_POLICY_FOR_IMPLEMENTATION_ONLY' and diagnostic['primary_unchanged'] is True,'diagnostic policy not adopted')
    need(diagnostic['quantile_grid']==[.1,.5,.9,.95] and diagnostic['scientific_read']=='HOLD','diagnostic scope changed')
    for key in ('proposal','independent_review'):need(shared.sha(diagnostic[key+'_path'])==diagnostic[key+'_sha256'],'diagnostic review/proposal changed')
    need(b['threshold_rule']=='strict> nextafter(sortedpositive[floor(.10*n)],-inf)','wrong positive threshold')
    c=cases(b);need(set(c)=={(a,s) for a in P.ARMS for s in P.SEEDS},'plans incomplete')
    if require_committed:
        repo=pathlib.Path(P.ROOT);code=pathlib.Path(__file__).resolve().parent
        own=committed_paths(binding_path,b,repo,code)
        require_clean_committed(repo,own)
        sb=obj(b['shared_input_binding']);v=repo/'src/SPRINT5/paired_ranking_prefit/verify_prefit.py'
        need(shared.sha(v)==sb['pins'][str(v)],'shared verifier changed')
        subprocess.run([sys.executable,'-I',str(v),'--binding',b['shared_input_binding'],'--require-committed'],check=True,capture_output=True)
    common=S.data.metadata(obj(b['shared_input_binding']))
    meta=tail_inputs.load(b,common['manifests']['dev']);meta['manifests']={'dev':common['manifests']['dev']}
    _,report=tail_stats.design(meta)
    need(report==obj(b['draw_metadata_path']),'registered metadata draw report changed')
    return b,meta


def validate_roster(entries):
    need(len(entries)==15 and {(e['arm'],e['seed']) for e in entries}=={(a,s) for a in P.ARMS for s in P.SEEDS},'all15unique arm/seeds required')
    need(len({e['archive_sha256'] for e in entries})==15 and len({str(pathlib.Path(e['archive_path']).resolve()) for e in entries})==15,'duplicate archive')
    for e in entries:need(e['task']==P.task(e['arm'],e['seed']),'wrong task')


def validate_envelope(r,e,expected):
    S=shared.load();task=P.task(e['arm'],e['seed'])
    need(r['status']=='ELIGIBLE_METADATA_ONLY' and (r['task'],r['arm'],r['seed'])==(task,e['arm'],e['seed']),'wrong envelope identity')
    need(r['archive_sha256']==e['archive_sha256'] and r['source_sums_sha256']==P.TRAIN_SOURCE,'archive/source changed')
    need(r['train_manifest_sha256']==expected['train_manifest_sha256'] and r['eval_manifest_sha256']==S.admit.EVAL_SHA,'manifest changed')
    need((r['steps'],r['batch_size'],r['forwards'],r['limit'],r['checkpoint'])==(100,256,25600,0,'last'),'budget/checkpoint changed')
    need(r['arch']=='a12_clip_vitb16_madation' and r['res']==224,'wrong model/input')
    need(r['training_complete'] is True and r['checkpoint_saved'] is True and r['all_logged_losses_finite'] is True,'fit incomplete')
    need(r['schedule']==expected['schedule'],'exact common stratified schedule differs')
    need(r['training_reference_sha256']==P.REFERENCE_SHA,'optimization reference differs')
    need(r['objective_trace_valid'] is True,'objective state/trace incomplete or nonfinite')
    need('H100' in r['gpu_name'] and r['torch']=='2.11.0+cu128' and r['cuda_runtime']=='12.8','wrong platform')
    need(r['tf32_matmul'] is True and r['tf32_cudnn'] is True and r['cudnn_benchmark'] is False and r['precision']=='float32, eval mode, no autocast','wrong arithmetic')
    g,n=r['reference_gate'],r['ownfit_gate']
    need(g['byte_identical'] is True and g['n']==2496 and g['n_differ']==0 and g['max_abs']==0,'reference byte gate failed')
    need(n['passed'] is True and n['n_common']==21277 and n['n_differ']==0 and n['max_abs']==0,'ownfit gate failed')
    need(set(r['battery_sets'])==set(S.admit.COUNTS),'partial battery')
    for k,count in S.admit.COUNTS.items():
        v=r['battery_sets'][k];need(v['n_scored']==count and v['complete'] is True and v['finite'] is True,'incomplete/nonfinite battery')
    need(set(r['score_member_sha256'])=={task+'/scores_eval.npz',task+'/battery/logits_dev.npz'},'primary-only member allowlist changed')
    need(all(re.fullmatch('[0-9a-f]{64}',h) for h in r['score_member_sha256'].values()),'member digest missing')
    return r


def validate_release(r,binding_path,roster_path,code,decision):
    need(r['decision']==decision and r['experiment_id']==P.EXPERIMENT and r['scope']==P.SCOPE,'wrong independent release scope')
    need(r['reviewer'] and r['author']!=r['reviewer'],'cannot self-review')
    need(r['binding_sha256']==shared.sha(binding_path) and r['roster_sha256']==shared.sha(roster_path),'binding/roster changed')
    need(shared.sha(r['independent_review_path'])==r['independent_review_sha256'],'independent review changed')
    need(shared.sha(code/'SHA256SUMS')==r['reader_sums_sha256'],'reader changed')
    for line in (code/'SHA256SUMS').read_text().splitlines():
        h,n=line.split('  ',1);p=code/n;need(p.resolve().is_relative_to(code.resolve()) and shared.sha(p)==h,'source pin changed')
    need(shared.sha(r['input_admission_path'])==r['input_admission_sha256'],'input adoption changed')
    a=obj(r['input_admission_path']);need(a['decision']=='GO_INPUT_BINDING_ONLY' and a['binding_sha256']==shared.sha(binding_path),'new input binding not adopted')
    need(a['reviewer'] and a['author']!=a['reviewer'] and a['scientific_read']=='HOLD','input binding cannot grant scientific read')
    need(a['camera_auxiliary']==a['baseline_threshold_auxiliary']=='HOLD' and a['diagnostic_panels']=='ADOPTED_POINT_ONLY_NOT_ESTIMATED','scope cannot inherit auxiliaries')
    need(shared.sha(a['policy_input_admission_path'])==a['policy_input_admission_sha256'],'policy input adoption changed')
    return r


def admit(binding_path,roster_path,release_path,code):
    r=obj(release_path);validate_release(r,pathlib.Path(binding_path),pathlib.Path(roster_path),code,'GO_READER_READ')
    need(shared.sha(r['collector_review_path'])==r['collector_review_sha256'],'collector review changed')
    b,meta=validate_binding(binding_path,require_committed=True);plans=cases(b);entries=obj(roster_path);validate_roster(entries);accepted=[]
    for e in entries:
        need(shared.sha(e['archive_path'])==e['archive_sha256'] and shared.sha(e['receipt_path'])==e['receipt_sha256'],'archive/envelope changed')
        envelope=validate_envelope(obj(e['receipt_path']),e,plans[e['arm'],e['seed']])
        need(envelope['collector_review_sha256']==r['collector_review_sha256'],'unreviewed collector')
        accepted.append(dict(e,envelope=envelope))
    return b,meta,r,accepted
