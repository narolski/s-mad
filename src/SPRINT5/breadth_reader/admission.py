"""Breadth-specific10-fit admission; no candidate score/weight interpretation."""
import json
import pathlib
import re
import subprocess
import sys
import policy as P
import shared


def need(condition,message):
    if not condition:raise ValueError(message)


def obj(path):return json.loads(pathlib.Path(path).read_text())


def cases(binding):return {(r['arm'],r['seed']):r for r in obj(binding['expected_plans_path'])}


def validate_binding(path,require_committed=False):
    b=obj(path);S=shared.load()
    need(b['experiment_id']==P.EXPERIMENT and b['scope']=='PRIMARY_DESCRIPTIVE_ONLY','wrong experiment/scope')
    need(b['arms']==list(P.ARMS) and b['seeds']==list(P.SEEDS) and b['expected_fit_count']==10,'wrong roster policy')
    need((b['steps'],b['batch_size'],b['forwards'],b['checkpoint'])==(100,32,3200,'last'),'wrong protocol')
    need(b['training_source_sums_sha256']==P.TRAIN_SOURCE and b['shared_reader_sums_sha256']==shared.SUMS_SHA,'source binding changed')
    need(b['shared_input_binding_sha256']==shared.BINDING_SHA and shared.sha(b['shared_input_binding'])==shared.BINDING_SHA,'shared inputs changed')
    need(b['camera_auxiliary']=='HOLD_NOT_IMPLEMENTED_NO_CAMERA_ARRAY_ACCESS','camera scope cannot be inherited silently')
    need(shared.sha(b['prereg_path'])==b['prereg_sha256'] and shared.sha(b['pilot_release_path'])==b['pilot_release_sha256'],'prereg/pilot release changed')
    pilot=obj(b['pilot_release_path'])
    need(pilot['decision']=='GO_PILOT' and pilot['seeds']==list(P.SEEDS) and pilot['source_sums_sha256']==P.TRAIN_SOURCE,'wrong fit release')
    p=b['primary_policy']
    need(p['contrast']=='broad_minus_narrow' and p['two_sided_confidence']==.95 and p['draws']==10000 and p['rng']==P.RNG,'primary estimand changed')
    need(p['unreadable_policy']=='conditional_readable_percentile' and p['no_binary_success_gate'] is True and p['no_adoption'] is True,'unapproved inference policy')
    for key,value in b['exact_input_pins'].items():need(shared.sha(key)==value,'input/provenance pin changed '+key)
    need(obj(b['provenance_audit_path'])['status']=='PASS_PRIMARY_ONLY','unresolved primary provenance')
    need(shared.sha(b['expected_plans_path'])==b['expected_plans_sha256'],'expected plans changed')
    need(shared.sha(b['root_policy_path'])==b['root_policy_sha256'],'prospective policy changed')
    c=cases(b);need(set(c)=={(a,s) for a in P.ARMS for s in P.SEEDS},'expected10cases incomplete')
    if require_committed:
        repo=pathlib.Path(P.ROOT)
        own=[pathlib.Path(path).relative_to(repo)]
        own.extend(pathlib.Path(k).relative_to(repo) for k in b['exact_input_pins'] if pathlib.Path(k).is_relative_to(repo))
        code=pathlib.Path(__file__).resolve().parent
        own.extend((code/name).relative_to(repo) for name in ['SHA256SUMS',*[line.split('  ',1)[1] for line in (code/'SHA256SUMS').read_text().splitlines()]])
        for p in own:subprocess.run(['git','ls-files','--error-unmatch',str(p)],cwd=repo,check=True,capture_output=True)
        need(not subprocess.check_output(['git','status','--porcelain','--',*[str(p) for p in own]],cwd=repo,text=True),'input/reader paths not clean and committed')
        shared_binding=obj(b['shared_input_binding'])
        verifier=pathlib.Path(P.ROOT)/'src/SPRINT5/paired_ranking_prefit/verify_prefit.py'
        need(shared.sha(verifier)==shared_binding['pins'][str(verifier)],'shared verifier changed')
        subprocess.run([sys.executable,'-I',str(verifier),'--binding',b['shared_input_binding'],'--require-committed'],check=True,capture_output=True)
    meta=S.data.metadata(obj(b['shared_input_binding']));F,names=S.data.floors(meta)
    return b,meta,F,names


def validate_roster(entries):
    need(len(entries)==10,'all10fits required')
    need({(e['arm'],e['seed']) for e in entries}=={(a,s) for a in P.ARMS for s in P.SEEDS},'missing/duplicate arm seed')
    need(len({e['archive_sha256'] for e in entries})==10,'duplicate archive digest')
    need(len({str(pathlib.Path(e['archive_path']).resolve()) for e in entries})==10,'duplicate archive path')
    for e in entries:need(e['task']==P.task(e['arm'],e['seed']),'wrong task identity')


def validate_envelope(r,e,expected):
    S=shared.load();a,s=e['arm'],e['seed'];task=P.task(a,s)
    need(r['status']=='ELIGIBLE_METADATA_ONLY' and (r['task'],r['arm'],r['seed'])==(task,a,s),'wrong envelope identity')
    need(r['archive_sha256']==e['archive_sha256'] and r['source_sums_sha256']==P.TRAIN_SOURCE,'archive/source mismatch')
    need(r['train_manifest_sha256']==expected['train_manifest_sha256'] and r['eval_manifest_sha256']==S.admit.EVAL_SHA,'manifest mismatch')
    need((r['steps'],r['batch_size'],r['forwards'],r['limit'],r['checkpoint'])==(100,32,3200,0,'last'),'wrong training budget/checkpoint')
    need(r['arch']=='a12_clip_vitb16_madation' and r['res']==224,'wrong model/input')
    need(r['training_complete'] is True and r['checkpoint_saved'] is True and r['all_logged_losses_finite'] is True,'failed fit')
    need('H100' in r['gpu_name'] and r['torch']=='2.11.0+cu128' and r['cuda_runtime']=='12.8','wrong platform')
    need(r['tf32_matmul'] is True and r['tf32_cudnn'] is True and r['cudnn_benchmark'] is False,'wrong arithmetic flags')
    need(r['precision']=='float32, eval mode, no autocast','wrong inference precision')
    need(r['schedule']==expected['schedule'],'wrong exact100/image32image schedule')
    g,n=r['reference_gate'],r['ownfit_gate']
    need(g['byte_identical'] is True and g['n']==2496 and g['n_differ']==0 and g['max_abs']==0,'reference not byte-gated')
    need(n['passed'] is True and n['n_common']==21277 and n['n_differ']==0 and n['max_abs']==0,'own-fit not byte-identical')
    need(set(r['battery_sets'])==set(S.admit.COUNTS),'partial battery')
    for k,count in S.admit.COUNTS.items():
        x=r['battery_sets'][k];need(x['complete'] is True and x['finite'] is True and x['n_scored']==count,'incomplete/nonfinite battery')
    need(set(r['score_member_sha256'])=={task+'/scores_eval.npz',task+'/battery/logits_dev.npz'},'primary-only member allowlist changed')
    need(all(re.fullmatch('[0-9a-f]{64}',x) for x in r['score_member_sha256'].values()),'missing member digests')
    return r


def validate_release(release,binding_path,roster_path,code,decision):
    need(release['decision']==decision and release['experiment_id']==P.EXPERIMENT,'wrong release')
    need(release['scope']=='PRIMARY_DESCRIPTIVE_ONLY' and release['author']!=release['reviewer'] and release['reviewer'],'no independent primary-only release')
    need(release['binding_sha256']==shared.sha(binding_path),'binding changed after review')
    need(shared.sha(release['independent_review_path'])==release['independent_review_sha256'],'review changed')
    need(shared.sha(code/'SHA256SUMS')==release['reader_sums_sha256'],'reader source changed')
    for line in (code/'SHA256SUMS').read_text().splitlines():
        h,name=line.split('  ',1);p=code/name
        need(p.resolve().is_relative_to(code.resolve()) and shared.sha(p)==h,'reader dependency changed')
    need(shared.sha(roster_path)==release['roster_sha256'],'roster changed')
    admission=obj(release['input_admission_path'])
    need(shared.sha(release['input_admission_path'])==release['input_admission_sha256'],'input adoption changed')
    need(admission['decision']=='GO_INPUT_BINDING_ONLY' and admission['binding_sha256']==shared.sha(binding_path),'inputs not adopted')
    need(admission['author']!=admission['reviewer'] and admission['reviewer'],'input binding cannot self-approve')
    need(admission['scientific_read']=='HOLD' and admission['camera_auxiliary']=='HOLD','input adoption cannot grant payload/camera access')
    need(shared.sha(admission['independent_policy_review_path'])==admission['independent_policy_review_sha256'],'input policy review changed')
    need(shared.sha(admission['root_policy_path'])==admission['root_policy_sha256'],'root prospective policy changed')
    return release


def admit(binding_path,roster_path,release_path,code):
    release=obj(release_path);validate_release(release,pathlib.Path(binding_path),pathlib.Path(roster_path),code,'GO_READER_READ')
    need(shared.sha(release['collector_review_path'])==release['collector_review_sha256'],'collector review changed')
    b,meta,F,names=validate_binding(binding_path,require_committed=True)
    expected=cases(b);entries=obj(roster_path);validate_roster(entries)
    accepted=[]
    for e in entries:
        need(shared.sha(e['archive_path'])==e['archive_sha256'],'opaque archive digest changed')
        need(shared.sha(e['receipt_path'])==e['receipt_sha256'],'envelope changed')
        r=validate_envelope(obj(e['receipt_path']),e,expected[e['arm'],e['seed']])
        need(r['collector_review_sha256']==release['collector_review_sha256'],'unreviewed collector')
        accepted.append(dict(e,envelope=r))
    return b,meta,F,names,release,accepted
