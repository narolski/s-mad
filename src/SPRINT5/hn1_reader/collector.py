"""Separately reviewed HN metadata collector; never opens score/weight members."""
import argparse
import hashlib
import json
import math
import pathlib
import re
import sys
import tarfile
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import shared
import policy as P
import admission as A


def envelope(entry,expected,review_hash):
    S=shared.load();prefix=entry['task']+'/'
    with tarfile.open(entry['archive_path'],'r:*') as t:
        raw=lambda name:S.member_bytes(t,prefix+name)
        obj=lambda name:json.loads(raw(name))
        meta=obj('meta.json');info=obj('info.json');battery=obj('battery/battery.json')
        platform=obj('battery/platform.json');gate=obj('battery/gate.json');schedule=obj('sprint_schedule.json');warmstart=obj('HN_warmstart.json')
        env=dict(line.split('=',1) for line in raw('task.env').decode().splitlines() if line)
        A.need(env=={'TASK':entry['task'],'ARM':entry['arm'],'SEED':str(entry['seed'])},'task.env identity mismatch')
        A.need(meta['seed']==info['seed']==battery['seed']==entry['seed'] and battery['arm']==entry['arm'],'seed/arm metadata mismatch')
        A.need(raw('battery_status.txt').decode().strip()=='battery_rc=0' and battery['status']=='scored; statistics not computed' and battery['test_mode'] is False,'failed/partial battery')
        ti=raw('task_info.txt').decode();A.need('steps 100 limit 0' in ti,'wrong fit budget')
        A.need('pack_sha256 96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004' in ti and 'overlay_sha256 171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149' in ti,'pack mismatch')
        losses=[float(x) for x in re.findall(r'\bstep\s+\d+/\d+\s+loss\s+(\S+)',raw('train.log').decode())]
        A.need(losses and all(math.isfinite(x) for x in losses),'missing/nonfinite logged training loss')
        sets={}
        for k,n in S.admit.COUNTS.items():
            v=battery['sets'][k]
            A.need(v['image_check']['verified'] is True,'unverified input images')
            sets[k]={'n_scored':v['n_scored'],'finite':v['finite'],'complete':v['n_scored']==v['n']==n}
        hashes={prefix+'scores_eval.npz':battery['netcheck']['expect_eval_sha256'],
                prefix+'battery/logits_dev.npz':battery['sets']['dev']['logits_sha256']}
        for name in [prefix+'last.pt',*hashes]:
            members=[m for m in t.getmembers() if m.name==name]
            A.need(len(members)==1 and members[0].isfile() and members[0].size>0,'missing checkpoint/score header')
        result={'status':'ELIGIBLE_METADATA_ONLY','task':entry['task'],'arm':entry['arm'],'seed':entry['seed'],
          'archive_sha256':entry['archive_sha256'],'source_sums_sha256':hashlib.sha256(raw('SHA256SUMS')).hexdigest(),
          'train_manifest_sha256':battery['train']['sha256'],'eval_manifest_sha256':battery['sets']['dev']['sha256'],
          'arch':meta['arch'],'res':meta['res'],'batch_size':meta['bs'],'steps':meta['steps'],
          'forwards':meta['train_forward_passes']*meta['bs'],'limit':info['limit'],'checkpoint':meta['final'],
          'training_complete':meta['steps']==info['steps']==meta['train_forward_passes']==100,
          'checkpoint_saved':True,'all_logged_losses_finite':True,'schedule':schedule,'warmstart':warmstart,
          'gpu_name':platform['gpu_name'],'torch':platform['torch'],'cuda_runtime':platform['cuda_runtime'],
          'tf32_matmul':platform['tf32_matmul'],'tf32_cudnn':platform['tf32_cudnn'],
          'cudnn_benchmark':platform['cudnn_benchmark'],'precision':platform['precision'],
          'reference_gate':gate,'ownfit_gate':battery['netcheck'],'battery_sets':sets,'score_member_sha256':hashes,
          'collector_review_sha256':review_hash,
          'payload_boundary':'Only fixedJSON/TXT/LOG metadata interpreted; NPZ/weights never opened. Camera payloads not selected.'}
        return A.validate_envelope(result,entry,expected)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--archive-roster',type=pathlib.Path,required=True)
    ap.add_argument('--release',type=pathlib.Path,required=True);ap.add_argument('--out',type=pathlib.Path,required=True)
    a=ap.parse_args();code=pathlib.Path(__file__).resolve().parent;r=A.obj(a.release)
    A.validate_release(r,pathlib.Path(P.BINDING),a.archive_roster,code,'GO_METADATA_COLLECTION_ONLY')
    binding,*_=A.validate_binding(P.BINDING,require_committed=True)
    expected=A.cases(binding);entries=A.obj(a.archive_roster);A.validate_roster(entries)
    for e in entries:A.need(shared.sha(e['archive_path'])==e['archive_sha256'],'opaque archive changed')
    a.out.mkdir(parents=True,exist_ok=False);S=shared.load()
    try:
        roster=[]
        for e in entries:
            result=envelope(e,expected[e['arm'],e['seed']],r['independent_review_sha256'])
            p=a.out/(e['task']+'.json');S.journal.exclusive_json(p,result)
            roster.append(dict(e,receipt_path=str(p.resolve()),receipt_sha256=shared.sha(p)))
        S.journal.exclusive_json(a.out/'READER_ROSTER.json',roster)
        S.journal.exclusive_json(a.out/'COLLECTION_COMPLETE.json',{'metadata_only':True,'fits':10,'roster_sha256':shared.sha(a.out/'READER_ROSTER.json')})
    except BaseException as error:
        S.journal.exclusive_json(a.out/'COLLECTION_FAILED.json',{'metadata_only':True,'error':str(error)});raise


if __name__=='__main__':main()
