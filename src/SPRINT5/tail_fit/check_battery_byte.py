"""Stricter sprint gate: tolerance-gated is never relabelled byte-identical."""
import json
import pathlib
import sys

p=pathlib.Path(sys.argv[1])
g=json.loads((p/'gate.json').read_text())
b=json.loads((p/'battery.json').read_text())
assert g['byte_identical'] is True and g['n_differ']==0 and g['max_abs']==0
assert g['gate_class']=='byte-gated'
assert b['netcheck']['passed'] is True and b['netcheck']['n_differ']==0
assert b['netcheck']['n_common']==21277
assert all(b['sets'][k]['finite'] is True for k in ('dev','tt1','meds','gd'))
print('SPRINT_BYTE_GATE_PASS reference and all21277ownfitdevlogits exact')
