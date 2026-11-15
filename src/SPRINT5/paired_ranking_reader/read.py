"""Bound paired-ranking reader. NO real invocation without independent release."""
import argparse
import datetime
import hashlib
import json
import math
import pathlib
import sys

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import admit
import data
import ranking_statistics as stats
from journal import Journal,atomic_result

BINDING=pathlib.Path('/home/narolski/smad-next/experiments/SPRINT5_20261114/paired_ranking/prefit_binding_v1/BINDING.json')
ONCE=pathlib.Path('/mnt/t7/smad_next/SPRINT5_1/reader_once_v1')
OUTPUT=pathlib.Path('/mnt/t7/smad_next/SPRINT5_1/reader_output_v1/RESULT.json')


def json_ready(value):
    if isinstance(value,dict):return {str(k):json_ready(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [json_ready(v) for v in value]
    if isinstance(value,float) and not math.isfinite(value):return None
    return value


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--roster',type=pathlib.Path,required=True)
    ap.add_argument('--release',type=pathlib.Path,required=True)
    ap.add_argument('--admit-only',action='store_true',help='Metadata receipts and opaque hashes only; no claim or payload access')
    a=ap.parse_args()
    code=pathlib.Path(__file__).resolve().parent
    binding,release,entries=admit.admit(BINDING,a.roster,a.release,code)
    meta=data.metadata(binding)
    # Floors are independently admitted, candidate-independent inputs; validate
    # their schema/order/finiteness BEFORE consuming the scientific read claim.
    F,names=data.floors(meta)
    if a.admit_only:
        print('ALL15_METADATA_ADMITTED; no candidate score payload read; no claim created')
        return
    admit.require(not OUTPUT.exists(),'result already exists; never replace')
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    journal=Journal(ONCE)
    claim={'experiment':'SPRINT5_1','claimed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'binding_sha256':admit.BINDING_SHA,'reader_sums_sha256':admit.sha(code/'SHA256SUMS'),
       'reader_review_sha256':release['independent_review_sha256'],'release_sha256':admit.sha(a.release),
       'roster_sha256':admit.sha(a.roster),'archive_sha256':[e['archive_sha256'] for e in entries],
       'population':'200devS4/S3 rows;132calibrationpersons;119boundgenuinecells; historical191neverreturned',
       'support_policy':'<20independentcomponents or zero bootstrapvariance => INCONCLUSIVE; no validboundimplemented',
       'output':str(OUTPUT),'failure_policy':'Permanent claim, no automatic retry, replacement or new journal path.'}
    journal.claim(claim)
    try:
        # First candidate NPZ access is strictly BELOW the durable claim.
        P,C,G=data.arrays(entries,meta,ONCE/'CLAIM.json')
        result=stats.analyze(meta['primary'],meta['calibration'],meta['cells'],P,C,G,F,draws=10000)
        result.update(binding_sha256=admit.BINDING_SHA,reader_sums_sha256=claim['reader_sums_sha256'],
                      archive_sha256=claim['archive_sha256'],floor_columns=names,
                      primary_components=len({r['component'] for r in meta['primary']}),
                      calibration_components=len({r['component'] for r in meta['calibration']}),
                      disclosures=['MAD22-informed development; historical FRLL photo exposure disclosed in upstream registration.',
                                   'All15networks retained; no scores averaged into a detector and no seed selection.',
                                   'No historical191metrics, still-sealed benchmark metrics or NEXT-selection result.'])
        digest=atomic_result(OUTPUT,json_ready(result))
        journal.finish('COMPLETE',{'result':str(OUTPUT),'sha256':digest})
        print('SPRINT5_1_READER_COMPLETE',str(OUTPUT),digest)
    except BaseException as error:
        journal.finish('FAILED',{'error_type':type(error).__name__,'error':str(error),
                                 'diagnostics':getattr(error,'details',None),
                                 'result_exists':OUTPUT.exists(),'retry':'FORBIDDEN without prospective repair review'})
        raise


if __name__=='__main__':main()
