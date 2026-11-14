"""Only adopted labels/inputs/source metadata; accepts no candidate arguments."""
import json
import pathlib
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import admission as A
import policy as P

if __name__=='__main__':
    assert len(sys.argv)==1,'No archive, reader, score or checkpoint arguments accepted'
    b,meta,F,names=A.validate_binding(P.BINDING)
    report=A.obj(b['readability_metadata_path'])
    print(json.dumps({'status':'PASS_INPUT_METADATA_ONLY','experiment_id':P.EXPERIMENT,'primary_rows':len(meta['primary']),
       'primary_components':len({r['component'] for r in meta['primary']}),'floors':len(names),'floor_shape':list(F.shape),
       'expected_fit_plans':len(A.cases(b)),'bootstrap':report,'candidate_payload_accessed':False,
       'camera_auxiliary':'HOLD','scientific_read':'HOLD'},indent=2))
