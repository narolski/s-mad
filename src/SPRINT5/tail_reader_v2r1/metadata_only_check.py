"""Input-only validation; no archive/score/model arguments accepted."""
import json
import pathlib
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import admission as A
import policy as P
import diagnostics

if __name__=='__main__':
    assert len(sys.argv)==1,'no candidate arguments'
    b,m=A.validate_binding(P.BINDING)
    print(json.dumps({'status':'PASS_INPUT_METADATA_ONLY','calibration_rows':len(m['calibration']),
       'calibration_components':m['calibration_components'],'positive_evaluation_rows':len(m['positive_evaluation']),
       'genuine_evaluation_rows':len(m['genuine_evaluation']),'fit_plans':len(A.cases(b)),
       'positive_guards':[{k:v for k,v in g.items() if k!='indices'} for g in m['positive_guards']],
       'bootstrap':A.obj(b['draw_metadata_path']),'candidate_payload_accessed':False,'scientific_read':'HOLD',
       'diagnostic_panels':b['diagnostic_panels'],'diagnostic_positive_pools':[{k:v for k,v in p.items() if k!='indices'} for p in diagnostics.pools(m)],'camera_auxiliary':'HOLD','baseline_threshold_auxiliary':'HOLD'},indent=2))
