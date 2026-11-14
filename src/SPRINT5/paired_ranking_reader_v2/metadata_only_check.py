"""Permitted input metadata check ONLY. Does not accept candidate paths."""
import json
import pathlib
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent))
from paired_ranking_reader_v2 import admit
from paired_ranking_reader_v2 import data
from paired_ranking_reader_v2 import ranking_statistics as S

p=pathlib.Path('/home/narolski/smad-next/experiments/SPRINT5_20261114/paired_ranking/prefit_binding_v1/BINDING.json')
assert admit.sha(p)==admit.BINDING_SHA
m=data.metadata(json.loads(p.read_text()))
counts=[len(set(S.merged_components(c['rows']))) for c in m['cells']]
result={'scope':'bound input metadata only; NO candidate archives, scores, checkpoints, roster or journal accessed',
   'binding_sha256':admit.BINDING_SHA,'primary_rows':len(m['primary']),
   'full_primary_components':len({r['component'] for r in m['primary']}),
   'calibration_rows':len(m['calibration']),'calibration_components':len({r['component'] for r in m['calibration']}),
   'genuine_cells':len(m['cells']),'guard_components_after_geometry_union':counts,
   'guards_below_20_independent_components':sum(n<20 for n in counts),
   'cell_count_consequence':'No sparse cell can be dropped; operational qualification will remain INCONCLUSIVE if any unsupported guard remains.',
   'candidate_payload_accessed':False}
print(json.dumps(result,indent=2))
