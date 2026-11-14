import json
import pathlib
import sys
p=pathlib.Path(sys.argv[1]);g=json.loads((p/'gate.json').read_text());b=json.loads((p/'battery.json').read_text())
assert g['byte_identical'] is True and g['n_differ']==0 and g['max_abs']==0
assert b['netcheck']['passed'] is True and b['netcheck']['n_common']==21277 and b['netcheck']['n_differ']==0
print('TRAIN_BASELINE_BYTE_GATE_PASS')
