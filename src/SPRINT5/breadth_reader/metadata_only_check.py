"""No candidate path input, collector invocation, scientific journal or payload."""
import json
import pathlib
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import shared
import policy as P
import admission as A
import breadth_stats

b,meta,F,names=A.validate_binding(P.BINDING,require_committed=False)
_,draws=breadth_stats.design(meta['primary'])
expected=A.obj(b['readability_metadata_path'])
assert draws['design_sha256']==expected['design_sha256']
assert draws['undefined_draw_indices']==expected['undefined_draw_indices']
result={'scope':'Adopted input metadata only; no actual fit archive/logit/checkpoint/roster/claim',
   'binding_sha256':shared.sha(P.BINDING),'expected_fit_cases':len(A.cases(b)),
   'primary_rows':len(meta['primary']),'primary_full_components':len({r['component'] for r in meta['primary']}),
   'fixed_floor_vectors':len(names),'readability':draws,
   'source_provenance_status':A.obj(b['provenance_audit_path'])['status'],
   'camera_auxiliary':'HOLD_NOT_READ','candidate_payload_accessed':False,
   'frozen_reader_sums_sha256':shared.sha(shared.ROOT/'SHA256SUMS')}
print(json.dumps(result,indent=2))
