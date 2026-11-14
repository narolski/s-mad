"""HN native transfer descriptive reader; real invocation remains separately gated."""
import argparse
import datetime
import json
import math
import pathlib
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import shared
import policy as P
import admission as A
import hn_stats
import payload


def clean(value):
    if isinstance(value,dict):return {k:clean(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [clean(v) for v in value]
    if isinstance(value,float) and not math.isfinite(value):return None
    return value


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--roster',type=pathlib.Path,required=True)
    ap.add_argument('--release',type=pathlib.Path,required=True);ap.add_argument('--admit-only',action='store_true')
    a=ap.parse_args();code=pathlib.Path(__file__).resolve().parent
    b,meta,F,names,release,entries=A.admit(P.BINDING,a.roster,a.release,code)
    if a.admit_only:
        print('HN_TRANSFER10METADATA_AND_INPUTS_ADMITTED; no payload/claim/camera access');return
    out=pathlib.Path(P.OUTPUT);A.need(not out.exists(),'existing result never replaced');out.parent.mkdir(parents=True,exist_ok=True)
    S=shared.load();j=S.journal.Journal(P.ONCE)
    claim={'experiment_id':P.EXPERIMENT,'scope':'PRIMARY_DESCRIPTIVE_ONLY','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'binding_sha256':shared.sha(P.BINDING),'reader_sums_sha256':shared.sha(code/'SHA256SUMS'),
       'release_sha256':shared.sha(a.release),'roster_sha256':shared.sha(a.roster),
       'archive_sha256':[e['archive_sha256'] for e in entries],
       'population':'exact200nativeS4/S3dev100; no camera/guard/historical191metrics',
       'failure_policy':'Permanent claim; no automatic retry, alternative journal path or seed replacement'}
    j.claim(claim)
    try:
        # First candidate NPZ access occurs only after create-only/fsynced claim.
        z=payload.arrays(entries,meta,pathlib.Path(P.ONCE)/'CLAIM.json')
        result=hn_stats.analyze(meta['primary'],z,F,draws=10000)
        result.update(binding_sha256=claim['binding_sha256'],reader_sums_sha256=claim['reader_sums_sha256'],
                      archive_sha256=claim['archive_sha256'],floor_columns=names,
                      provenance_audit_sha256=b['provenance_audit_sha256'])
        digest=S.journal.atomic_result(out,clean(result))
    except BaseException as error:
        j.finish('FAILED',{'error_type':type(error).__name__,'error':str(error),'result_exists':out.exists()});raise
    j.finish('COMPLETE',{'result':str(out),'sha256':digest})
    print('HN_TRANSFER_PRIMARY_COMPLETE',out,digest)


if __name__=='__main__':main()
