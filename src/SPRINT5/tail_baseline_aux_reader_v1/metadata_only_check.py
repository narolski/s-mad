"""Safe metadata validation only; no candidate/baseline archive or array operation."""
import argparse
import json
import pathlib
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import metadata as M
import policy as P

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--require-committed',action='store_true');args=ap.parse_args()
    b,m=M.validate(require_committed=args.require_committed)
    print(json.dumps({'status':'PASS_AUXILIARY_INPUT_METADATA_ONLY','input_pins':len(b['pins']),
       'baseline_calibration_ids':len(m['calibration']),'evaluation_ids':len(m['evaluation']),'candidate_models':len(b['candidates']),
       'genuine_denominators':[c['rows'] for c in m['genuine_cells']],'positive_denominators':[g['rows'] for g in m['positive_guards']],
       'after_primary_results_seen':True,'new_primary_claim':False,'arrays_decoded':False,'technical_member_access':'HOLD','scientific_auxiliary_read':'HOLD'},indent=2))
