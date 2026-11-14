"""Pre-score admission: external envelopes and opaque archive hashes only."""
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ARMS=('bce','paired_bce','paired_rank')
SEEDS=(501,502,503,504,505)
BINDING_SHA='519546ef7002930f620610f01deb0cc4e8889acf819b829a80c05f95fff6e923'
SOURCE_SHA='ef6bccb43d1c8936af8730957ee4da35c0a04fb97ff5ee373920523d63d73f6f'
COUNTS={'dev':21277,'tt1':34411,'meds':1018,'gd':11042}
TRAIN_SHA='2cf3fda3affc8dd3d1574857f494037ea0382c8a2d314754b615686401b7fa4a'
EVAL_SHA='93a5ba234f91e57951829c5536fabbe0f792ee4ad0a293f074aaca72f7465bd5'


def require(value,message):
    if not value:raise ValueError(message)


def sha(path):
    h=hashlib.sha256()
    with pathlib.Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(4<<20),b''):h.update(chunk)
    return h.hexdigest()


def json_file(path):return json.loads(pathlib.Path(path).read_text())


def validate_envelope(r,entry):
    """Collector must be independently reviewed; this is not an archive parser."""
    a,s=entry['arm'],entry['seed']
    require(a in ARMS and s in SEEDS,'unregistered arm/seed')
    task=f'SPRINT5_1_production_v3_{a}_s{s}'
    require(entry['task']==task and r['task']==task and r['arm']==a and r['seed']==s,'task/arm/seed mismatch')
    require(r['status']=='ELIGIBLE_METADATA_ONLY','collector did not admit metadata')
    require(r['archive_sha256']==entry['archive_sha256'],'receipt/archive hash mismatch')
    require(r['source_sums_sha256']==SOURCE_SHA,'wrong training source')
    require(r['train_manifest_sha256']==TRAIN_SHA and r['eval_manifest_sha256']==EVAL_SHA,'wrong input manifest')
    require(r['steps']==6250 and r['limit']==0 and r['checkpoint']=='last','wrong fit protocol')
    require(r['arch']=='a12_clip_vitb16_madation' and r['res']==224 and r['batch_size']==256,'wrong model/input recipe')
    require(r['training_complete'] is True and r['all_logged_losses_finite'] is True and r['checkpoint_saved'] is True,'failed/incomplete fit')
    require('H100' in r['gpu_name'] and r['torch']=='2.11.0+cu128' and r['cuda_runtime']=='12.8','wrong platform')
    g=r['reference_gate'];n=r['ownfit_gate']
    require(g['byte_identical'] is True and g['n']==2496 and g['n_differ']==0 and g['max_abs']==0,'reference is not byte-gated')
    require(n['passed'] is True and n['n_common']==21277 and n['n_differ']==0 and n['max_abs']==0,'own-fit logits not byte-identical')
    require(set(r['battery_sets'])==set(COUNTS),'partial battery sets')
    for k,count in COUNTS.items():
        v=r['battery_sets'][k]
        require(v['n_scored']==count and v['finite'] is True and v['complete'] is True,'incomplete/nonfinite battery '+k)
    names=[task+'/scores_eval.npz']+[task+'/battery/logits_'+k+'.npz' for k in COUNTS]
    require(set(r['score_member_sha256'])==set(names),'wrong score-member allowlist')
    require(all(isinstance(h,str) and re.fullmatch('[0-9a-f]{64}',h) for h in r['score_member_sha256'].values()),'missing score-member hashes')
    plan=r['schedule']
    require(plan['arm']==a and plan['seed']==s and plan['steps']==6250 and plan['bs']==256,'schedule identity mismatch')
    require(plan['row_occurrences']==1600000 and plan['unique_row_indices']==8386 and plan['pair_units_per_cycle']==124,'row exposure count mismatch')
    require(all(re.fullmatch('[0-9a-f]{64}',plan[k]) for k in ('schedule_sha256','exposure_sha256')),'schedule digest missing')
    expected=json_file(pathlib.Path(__file__).parent/'EXPECTED_PLANS.json')['plans']
    matches=[p for p in expected if p['arm']==a and p['seed']==s]
    require(len(matches)==1 and plan==matches[0],'schedule differs from pinned full pre-fit CPU plan')
    return r


def validate_roster(entries):
    require(len(entries)==15,'all15 final fits are required')
    require({(e['arm'],e['seed']) for e in entries}=={(a,s) for a in ARMS for s in SEEDS},'incomplete/duplicate roster')
    require(len({e['archive_sha256'] for e in entries})==15,'repeated archive hash')
    require(len({str(pathlib.Path(e['archive_path']).resolve()) for e in entries})==15,'repeated archive path')


def validate_release(release,roster_path,code_root):
    code_root=pathlib.Path(code_root)
    require(release['decision']=='GO_READER_READ' and release['binding_sha256']==BINDING_SHA,'reader read not independently released')
    require(release['reviewer'] and release['author']!=release['reviewer'],'reader cannot self-approve')
    require(sha(release['independent_review_path'])==release['independent_review_sha256'],'reader review hash changed')
    require(sha(release['collector_review_path'])==release['collector_review_sha256'],'metadata collector lacks bound review')
    require(release['minimum_guard_components']==20 and release['zero_variance_policy']=='INCONCLUSIVE','unapproved guard support policy')
    require(release['reader_sums_sha256']==sha(code_root/'SHA256SUMS'),'reader source changed')
    for line in (code_root/'SHA256SUMS').read_text().splitlines():
        h,name=line.split('  ',1)
        p=code_root/name
        require(p.resolve().is_relative_to(code_root.resolve()) and sha(p)==h,'reader source pin '+name)
    require(sha(roster_path)==release['roster_sha256'],'roster changed after release')


def admit(binding_path,roster_path,release_path,code_root):
    """Never opens candidate tar members, NPZ arrays, logs or checkpoints."""
    binding_path=pathlib.Path(binding_path);code_root=pathlib.Path(code_root)
    require(sha(binding_path)==BINDING_SHA,'pre-fit binding changed')
    binding=json_file(binding_path)
    verifier=pathlib.Path(binding['repo'])/'src/SPRINT5/paired_ranking_prefit/verify_prefit.py'
    require(sha(verifier)==binding['pins'][str(verifier)],'prefit verifier changed')
    subprocess.run([sys.executable,'-I',str(verifier),'--binding',str(binding_path),'--require-committed'],check=True,capture_output=True)
    release=json_file(release_path)
    validate_release(release,roster_path,code_root)
    entries=json_file(roster_path);validate_roster(entries)
    admitted=[]
    for e in sorted(entries,key=lambda e:(e['seed'],ARMS.index(e['arm']))):
        require(sha(e['archive_path'])==e['archive_sha256'],'opaque archive SHA mismatch')
        require(sha(e['receipt_path'])==e['receipt_sha256'],'eligibility receipt changed')
        r=validate_envelope(json_file(e['receipt_path']),e)
        require(r['collector_review_sha256']==release['collector_review_sha256'],'unreviewed collector receipt')
        admitted.append(dict(e,envelope=r))
    for seed in SEEDS:
        plans={e['arm']:e['envelope']['schedule'] for e in admitted if e['seed']==seed}
        require(len({p['exposure_sha256'] for p in plans.values()})==1,'unequal exact row exposure across arms')
        require(plans['paired_bce']['schedule_sha256']==plans['paired_rank']['schedule_sha256'],'paired schedules differ')
        require(plans['bce']['schedule_sha256']!=plans['paired_bce']['schedule_sha256'],'independent sampling schedule unexpectedly identical')
    return binding,release,admitted
