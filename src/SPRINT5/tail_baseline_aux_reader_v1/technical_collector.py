"""Explicitly released technical phase: headers/fixed metadata and opaque NPZ hash ONLY."""
import argparse
import hashlib
import json
import pathlib
import sys
import tarfile
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import admission as A
import bridge
import metadata as M
import policy as P


def member(t,name,limit):
    matches=[x for x in t.getmembers() if x.name==name]
    M.need(len(matches)==1 and matches[0].isfile() and 0<matches[0].size<=limit,'missing/duplicate/nonregular/oversized member '+name)
    return matches[0]


def fixed_bytes(t,name):
    return t.extractfile(member(t,name,8<<20)).read()


def capture(archive,binding,release):
    M.need(bridge.sha(archive)==P.BASELINE_SHA,'baseline opaque archive hash mismatch')
    prefix='AB1_Sb_s408/'
    with tarfile.open(archive,'r:*') as t:
        raw={name:fixed_bytes(t,prefix+name) for name in ('meta.json','info.json','task_info.txt','env.txt','gpu.txt')}
        meta=json.loads(raw['meta.json']);info=json.loads(raw['info.json']);text=raw['task_info.txt'].decode()
        M.need(meta['seed']==info['seed']==408 and meta['arch']=='a12_clip_vitb16_madation' and meta['res']==224,'baseline model/source identity mismatch')
        M.need(info['n_eval']==21277 and info['limit']==0,'baseline evaluation scope incomplete')
        M.need('pack_sha256 96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004' in text and 'overlay_sha256 171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149' in text,'baseline input pack mismatch')
        runtime=info.get('torch')=='2.11.0+cu128' and 'H100' in info.get('device','') and info.get('common_py_sha256')==binding['expected_common_py_sha256']
        # Byte hashing is opaque: no NumPy/ZIP import, decoding, ID inspection or
        # finiteness/statistic operation occurs in this phase.
        header=member(t,P.MEMBER,32<<20);digest=hashlib.sha256()
        with t.extractfile(header) as stream:
            for block in iter(lambda:stream.read(1<<20),b''):digest.update(block)
        return {'status':'TECHNICAL_BASELINE_METADATA_HASH_CAPTURED_NO_ARRAY_DECODE','experiment_id':P.EXPERIMENT,
           'timing':P.TIMING,'binding_sha256':release['binding_sha256'],'source_sums_sha256':release['source_sums_sha256'],
           'policy_adoption_sha256':P.POLICY_SHA,'technical_release_sha256':release['_release_sha256'],
           'baseline_archive_sha256':P.BASELINE_SHA,'score_member':P.MEMBER,'score_member_bytes':header.size,'score_member_sha256':digest.hexdigest(),
           'fixed_metadata_member_sha256':{prefix+k:hashlib.sha256(v).hexdigest() for k,v in raw.items()},
           'source_identity_check':'PASS','runtime_provenance_status':'PASS_RECORDED_TORCH_H100_AND_PINNED_SCORER_SOURCE' if runtime else 'UNKNOWN_OR_MISMATCH_HOLD',
           'runtime':{'torch':info.get('torch'),'device':info.get('device'),'common_py_sha256':info.get('common_py_sha256'),
              'precision':'Source-pinned scorer uses float32/eval/noautocast and explicitly enables TF32; not inferred from fresh env-process defaults'},
           'baseline_checkpoint_hash_metadata_only':info.get('last_pt_sha256'),'independent_checkpoint_rehash':False,
           'bytegate':'Existing same-baseline gate chain requires independent technical admission; no new gate rerun or array comparison performed here',
           'baseline_gate_chain_sha256':binding['baseline_gate_chain_sha256'],'payload_ID_schema_finiteness':'UNKNOWN_UNTIL_AUXILIARY_CLAIM',
           'array_deserialization':False,'scientific_auxiliary_read':'HOLD','camera_auxiliary':'HOLD'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--release',type=pathlib.Path,required=True);args=ap.parse_args()
    b,meta,release,_=A.admit(args.release,technical=True)
    release=dict(release,_release_sha256=bridge.sha(args.release));out=pathlib.Path(P.TECHDIR)
    out.mkdir(parents=True,exist_ok=False) # Permanent attempt namespace; no retry/overwrite.
    J=bridge.journal()
    try:J.exclusive_json(out/'RECEIPT.json',capture(P.BASELINE,b,release))
    except BaseException as error:
        J.exclusive_json(out/'FAILURE.json',{'status':'FAILED','error_type':type(error).__name__,'error':str(error),'array_deserialization':False});raise
    print('BASELINE_TECHNICAL_METADATA_CAPTURED_NO_ARRAY_DECODE',out/'RECEIPT.json')


if __name__=='__main__':main()
