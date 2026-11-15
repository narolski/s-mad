"""Tail positive-calibrated primary/NI reader; real invocation remains separately gated."""
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
import tail_stats
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
    b,meta,release,entries=A.admit(P.BINDING,a.roster,a.release,code)
    if a.admit_only:
        print('TAIL15METADATA_AND_INPUTS_ADMITTED; no payload/claim/camera access');return
    out=pathlib.Path(P.OUTPUT);A.need(not out.exists(),'existing result never replaced');out.parent.mkdir(parents=True,exist_ok=True)
    S=shared.load();j=S.journal.Journal(P.ONCE)
    claim={'experiment_id':P.EXPERIMENT,'scope':P.SCOPE,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'binding_sha256':shared.sha(P.BINDING),'reader_sums_sha256':shared.sha(code/'SHA256SUMS'),
       'release_sha256':shared.sha(a.release),'roster_sha256':shared.sha(a.roster),
       'archive_sha256':[e['archive_sha256'] for e in entries],
       'population':'exact70positivecalibration+180positiveevaluation+288genuine; no inheritedcamera/baseline/diagnostic/historical191metrics',
       'failure_policy':'Permanent claim; no automatic retry, alternative journal path or seed replacement'}
    j.claim(claim)
    try:
        # First candidate NPZ access occurs only after create-only/fsynced claim.
        C,Z=payload.arrays(entries,meta,pathlib.Path(P.ONCE)/'CLAIM.json')
        result=tail_stats.analyze(meta,C,Z,draws=10000)
        result.update(binding_sha256=claim['binding_sha256'],reader_sums_sha256=claim['reader_sums_sha256'],
                      archive_sha256=claim['archive_sha256'],
                      policy_binding_sha256=P.POLICY_BINDING_SHA)
        digest=S.journal.atomic_result(out,clean(result))
    except BaseException as error:
        j.finish('FAILED',{'error_type':type(error).__name__,'error':str(error),'result_exists':out.exists()});raise
    j.finish('COMPLETE',{'result':str(out),'sha256':digest})
    print('TAIL_PRIMARY_NI_COMPLETE',out,digest)


if __name__=='__main__':main()
