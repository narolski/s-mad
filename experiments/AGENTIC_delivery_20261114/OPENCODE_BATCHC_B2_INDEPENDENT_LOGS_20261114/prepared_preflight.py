import csv, hashlib, importlib.util, json, math, os, pathlib, subprocess
import numpy as np
root = pathlib.Path('/home/narolski/smad-next')
out = root / 'experiments/AGENTIC_delivery_20261114/OPENCODE_BATCHC_B2_REVIEWER_PREFLIGHT_20261114.json'
if os.path.lexists(out):
    raise FileExistsError(out)
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name, relative, expected):
    path = root / relative
    assert sha(path) == expected, relative
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj
m = module('batchc_context', 'src/AB1/ab1_pm3_read.py',
           '11dd5aef7e3a86a4d208e3ad75f81b6be80a62bce5ad958fad3c74f454cbf7f0')
k = module('batchc_floor_check', 'src/adversary/check.py',
           'e08bcecb59d892daf8900d7e3993ba8f7620555ea93e698d59b095239f155837')
context = m._within_d_context()
assert set(context) == set(m.WITHIN_D_CONTRASTS)
assert all(not x['synthetic'] and 'context only' in x['scope'] for x in context.values())
eval_ids = {r['id'] for r in csv.DictReader(m.A.EVAL.open())}
receipt = {'scope': 'candidate-free reference preflight; not scientific admission',
           'candidate_payloads_opened': False, 'synthetic_candidate': 'constant zero',
           'context_sources': {c: x['source'] for c, x in context.items()}, 'checks': []}
for c in m.PM.ADV_CONTRASTS:
    for suffix in ('.json', '_heldout.csv'):
        p = k.FDIR / (c + suffix)
        saved = subprocess.run(['git', '-C', str(root), 'show',
                                'HEAD:' + p.relative_to(root).as_posix()],
                               check=True, capture_output=True).stdout
        assert p.read_bytes() == saved, str(p)
    rows = list(csv.DictReader((k.FDIR / (c + '_heldout.csv')).open()))
    assert len({r['id'] for r in rows}) == len(rows)
    assert {int(r['label']) for r in rows} == {0, 1}
    assert all(int(r['component']) >= 0 for r in rows)
    for floor in ('all', 'nuisance'):
        rep, key, model, ids, y, groups, predictions, pins = k._load(c, floor)
        assert set(ids) <= eval_ids
        assert np.isfinite(predictions).all()
        # _load checks committed pin membership and exact AUC reproduction at 1e-9.
        synthetic = {i: 0.0 for i in ids}
        result = k.exceeds(c, synthetic, floor=floor, n_boot=2000, seed=20261115)
        assert all(math.isfinite(result[n]) for n in ('arm_auc', 'floor_auc', 'diff', 'diff_lo', 'diff_hi'))
        receipt['checks'].append({'contrast': c, 'floor': floor, 'rows': len(ids),
                                 'components': len(set(groups.tolist())), 'passed': True,
                                 'pins': pins})
receipt['head'] = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
with out.open('x') as f:
    json.dump(receipt, f, indent=2, allow_nan=False)
    f.write('\n')
print('Reference-only preflight completed:', out, sha(out))
