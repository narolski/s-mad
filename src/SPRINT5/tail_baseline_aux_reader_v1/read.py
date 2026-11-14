"""Auxiliary-only entry point; original primary artifacts are never written/recomputed."""
import argparse
import datetime
import pathlib
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import admission as A
import bridge
import metadata as M
import payload
import point_report
import policy as P


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--release',type=pathlib.Path,required=True);ap.add_argument('--admit-only',action='store_true');args=ap.parse_args()
    b,meta,release,technical=A.admit(args.release)
    primary_before=M.validate_primary(b)
    if args.admit_only:
        print('AUXILIARY_METADATA_ONLY_ADMITTED_NO_CLAIM_OR_PAYLOAD');return
    output=pathlib.Path(P.OUTPUT);M.need(not output.exists(),'existing auxiliary result cannot be replaced');output.parent.mkdir(parents=True,exist_ok=True)
    J=bridge.journal();journal=J.Journal(P.ONCE)
    claim={'experiment_id':P.EXPERIMENT,'scope':P.READ_SCOPE,'timing':P.TIMING,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'binding_sha256':bridge.sha(P.BINDING),'source_sums_sha256':release['source_sums_sha256'],'release_sha256':bridge.sha(args.release),
       'policy_adoption_sha256':P.POLICY_SHA,'technical_receipt_sha256':release['technical_receipt_sha256'],
       'primary_before_sha256':primary_before,'candidate_archive_sha256':[x['archive_sha256'] for x in b['candidates']],
       'baseline_archive_sha256':P.BASELINE_SHA,'allowed_baseline_numeric_ids':538,'allowed_candidate_numeric_ids':468,
       'new_primary_read':False,'full_container_validation_after_auxiliary_claim_only':True,'retry':'FORBIDDEN; no alternate journal/output'}
    journal.claim(claim) # O_EXCL + fsync; first array/result-summary decode only below.
    try:
        C,B,Z=payload.arrays(b,meta,technical);own=payload.own_companion(b)
        result=point_report.analyze(meta,C,B,Z,own)
        result.update(binding_sha256=claim['binding_sha256'],source_sums_sha256=claim['source_sums_sha256'],
             policy_adoption_sha256=P.POLICY_SHA,auxiliary_release_sha256=claim['release_sha256'],technical_receipt_sha256=claim['technical_receipt_sha256'],
             primary_preserved_sha256=primary_before,baseline_archive_sha256=P.BASELINE_SHA,baseline_member=P.MEMBER,
             baseline_member_sha256=technical['score_member_sha256'],candidate_archive_sha256=claim['candidate_archive_sha256'],
             ordered_baseline_calibration_ids=b['calibration_ids'],ordered_evaluation_ids=b['evaluation_ids'])
        M.need(M.validate_primary(b)==primary_before,'original primary bytes changed during auxiliary')
        digest=J.atomic_result(output,result) # allow_nanFalse; structural missing values are explicitNone.
    except BaseException as error:
        journal.finish('FAILED',{'error_type':type(error).__name__,'error':str(error),'auxiliary_result_exists':output.exists(),'primary_artifacts_not_written_by_auxiliary':True});raise
    journal.finish('COMPLETE',{'result':str(output),'sha256':digest,'primary_preserved_sha256':primary_before})
    print('AUXILIARY_POINT_RESULT_COMPLETE_REQUIRES_POSTREVIEW',output,digest)


if __name__=='__main__':main()
