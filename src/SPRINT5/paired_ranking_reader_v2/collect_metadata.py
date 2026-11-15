"""Review-gated metadata-only envelopes. Does NOT open NPZ or weight members."""
import argparse
import hashlib
import json
import math
import pathlib
import re
import sys
import tarfile

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent))
from paired_ranking_reader_v2 import admit
from paired_ranking_reader_v2.journal import exclusive_json


def member_bytes(t,name,limit=8<<20):
    members=[m for m in t.getmembers() if m.name==name]
    admit.require(len(members)==1 and members[0].isfile() and members[0].size<=limit,'invalid metadata member '+name)
    return t.extractfile(members[0]).read()


def envelope(entry,review_hash):
    """Only fixed JSON/TXT/LOG metadata members below are semantically read."""
    task=entry['task'];prefix=task+'/'
    with tarfile.open(entry['archive_path'],'r:*') as t:
        obj=lambda name:json.loads(member_bytes(t,prefix+name))
        meta=obj('meta.json');info=obj('info.json');battery=obj('battery/battery.json')
        gate=obj('battery/gate.json');platform=obj('battery/platform.json')
        schedule=obj('sprint_schedule.json')
        source=member_bytes(t,prefix+'SHA256SUMS');train=member_bytes(t,prefix+'train.log').decode()
        status=member_bytes(t,prefix+'battery_status.txt').decode().strip()
        env=member_bytes(t,prefix+'task.env').decode();taskinfo=member_bytes(t,prefix+'task_info.txt').decode()
        fields=dict(line.split('=',1) for line in env.splitlines() if line)
        admit.require(fields=={'TASK':task,'ARM':entry['arm'],'SEED':str(entry['seed'])},'task.env mismatch')
        admit.require(meta['seed']==info['seed']==battery['seed']==entry['seed'],'seed metadata mismatch')
        admit.require(battery['arm']==entry['arm'] and battery['test_mode'] is False,'wrong battery arm/test mode')
        admit.require(status=='battery_rc=0' and battery['status']=='scored; statistics not computed','failed/partial battery')
        admit.require('steps 6250 limit 0' in taskinfo,'task fit-limit mismatch')
        admit.require('pack_sha256 96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004' in taskinfo,'base pack mismatch')
        admit.require('overlay_sha256 171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149' in taskinfo,'overlay mismatch')
        losses=[float(x) for x in re.findall(r'\bstep\s+\d+/\d+\s+loss\s+(\S+)',train)]
        admit.require(losses and all(math.isfinite(x) for x in losses),'nonfinite/missing logged training loss')
        sets={};score_hash={prefix+'scores_eval.npz':battery['netcheck']['expect_eval_sha256']}
        for k,n in admit.COUNTS.items():
            x=battery['sets'][k]
            admit.require(x['logits_file']=='logits_'+k+'.npz','unexpected battery score member')
            admit.require(x['image_check']['verified'] is True,'input image hashes unverified')
            sets[k]={'n_scored':x['n_scored'],'finite':x['finite'],'complete':x['n_scored']==x['n']==n}
            score_hash[prefix+'battery/logits_'+k+'.npz']=x['logits_sha256']
        # Headers can establish existence; NEVER extract/hash these payload members here.
        for name in [prefix+'last.pt',*score_hash]:
            matches=[m for m in t.getmembers() if m.name==name]
            admit.require(len(matches)==1 and matches[0].isfile() and matches[0].size>0,'missing checkpoint/score member')
        result={'status':'ELIGIBLE_METADATA_ONLY','task':task,'arm':entry['arm'],'seed':entry['seed'],
          'archive_sha256':entry['archive_sha256'],'source_sums_sha256':hashlib.sha256(source).hexdigest(),
          'train_manifest_sha256':battery['train']['sha256'],'eval_manifest_sha256':battery['sets']['dev']['sha256'],
          'steps':meta['steps'],'limit':info['limit'],'checkpoint':meta['final'],
          'arch':meta['arch'],'res':meta['res'],'batch_size':meta['bs'],'schedule':schedule,
          'training_complete':meta['steps']==info['steps']==6250 and meta['train_forward_passes']==6250,
          'all_logged_losses_finite':all(math.isfinite(x) for x in losses),'checkpoint_saved':True,
          'gpu_name':platform['gpu_name'],'torch':platform['torch'],'cuda_runtime':platform['cuda_runtime'],
          'reference_gate':gate,'ownfit_gate':battery['netcheck'],'battery_sets':sets,'score_member_sha256':score_hash,
          'collector_review_sha256':review_hash,'checkpoint_sha256_metadata_only':info['last_pt_sha256'],
          'payload_boundary':'Score digests copied from pinned scorer metadata. NPZ and weights NOT opened; checked after permanent scientific claim.'}
        return admit.validate_envelope(result,entry)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--archive-roster',type=pathlib.Path,required=True)
    ap.add_argument('--release',type=pathlib.Path,required=True);ap.add_argument('--out',type=pathlib.Path,required=True)
    a=ap.parse_args();r=admit.json_file(a.release);code=pathlib.Path(__file__).resolve().parent
    admit.require(r['decision']=='GO_METADATA_COLLECTION_ONLY' and r['binding_sha256']==admit.BINDING_SHA,'metadata collection not released')
    admit.require(r['author']!=r['reviewer'] and r['reviewer'],'collector self-approval forbidden')
    admit.require(admit.sha(r['independent_review_path'])==r['independent_review_sha256'],'collector review changed')
    admit.require(admit.sha(code/'SHA256SUMS')==r['reader_sums_sha256'],'collector source changed')
    for line in (code/'SHA256SUMS').read_text().splitlines():
        h,name=line.split('  ',1);admit.require(admit.sha(code/name)==h,'collector dependency changed')
    admit.require(admit.sha(a.archive_roster)==r['archive_roster_sha256'],'archive roster changed')
    entries=admit.json_file(a.archive_roster);admit.validate_roster(entries)
    # All15 must exist and match opaque digests before even metadata members are read.
    for e in entries:admit.require(admit.sha(e['archive_path'])==e['archive_sha256'],'opaque archive hash mismatch')
    a.out.mkdir(parents=True,exist_ok=False)
    try:
        roster=[]
        for e in entries:
            rec=envelope(e,r['independent_review_sha256']);p=a.out/(e['task']+'.json')
            exclusive_json(p,rec);roster.append(dict(e,receipt_path=str(p.resolve()),receipt_sha256=admit.sha(p)))
        exclusive_json(a.out/'READER_ROSTER.json',roster)
        exclusive_json(a.out/'COLLECTION_COMPLETE.json',{'metadata_only':True,'fits':15,'roster_sha256':admit.sha(a.out/'READER_ROSTER.json')})
    except BaseException as error:
        exclusive_json(a.out/'COLLECTION_FAILED.json',{'error':str(error),'metadata_only':True})
        raise


if __name__=='__main__':main()
