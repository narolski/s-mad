# Batch-C within-D context repair — 14 November 2026

**Implementation author report; separate independent review REQUIRED. Production remains NO-GO.** The author of this patch previously audited admission, but is no longer an independent approver of this changed artifact. The earlier audit's source hashes describe the prior snapshot.

## Narrow change

AB1 amendment 4b item 3 requires the two already committed within-D context reports. Batch-C now adds `within_D_floors` to its output JSON, with entries `ri_R4_vs_R3` and `test_cv_R4_vs_R3`. Each entry contains:

- `context`: the complete existing JSON, preserved without numerical recomputation;
- `scope`: explicit **different row sets / context only**, not floors on dev+clean80 or clean80 and not used in decisions, thresholds, bootstrap or network-minus-floor comparisons;
- `synthetic`: false in production, true in mock;
- `source`: resolved input and stage-6 pinfile paths and SHA256 values (null in mock).

Production reads both files and `pins_stage6.sha256` relative to the reader's repository root. Each file must equal its committed HEAD bytes, and each context digest must appear as an exact named entry in the committed stage-6 pinfile. Dirty inputs, dirty pinfiles, absent git objects and missing/wrong pins refuse. Both reports are verified before the reader's existing atomic claim, so a context failure consumes no native-read claim. The helper neither creates claims nor accesses archives. Existing claim creation, permanence, output exclusivity and archive checks are preserved. Other pair modes do not acquire this new dependency.

Mock mode uses two explicitly synthetic placeholders, never real context values or git operations. The context is printed in the JSON artifact; stdout retains its concise verdict summary. The existing descriptive transfer companion is untouched. No deciding statistic, threshold, population, seed, RNG draw or interval code changed.

## Validation performed

Commands ran from `/home/narolski/smad-next` with `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2` and the existing Python interpreter, `-I`:

1. `TMPDIR=/tmp/opencode /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/AB1/tests/test_pm3_admission.py`: **24 passed**, 0.046 seconds. Original 18 guard tests retained, plus six context regressions: both complete contexts and labels/hashes; committed wrong pin refusal; dirty context refusal; dirty pinfile refusal; mock isolation from files/git; output integration before claim and scoped to C. Three existing manifest ResourceWarnings remain in historical `ab1_read.py:59`.
2. `/home/narolski/mambamorph-code/.venv-spark/bin/python -I src/AB1/ab1_pm3_read.py --pair C --mock --out experiments/AGENTIC_delivery_20261114/OPENCODE_BATCHC_CONTEXT_MOCK_20261114.json`: exit 0.
3. Loaded only old/new synthetic mock JSONs; removed the new `within_D_floors` field and asserted exact equality of the entire remaining objects. PASS. All statistics, intervals, per-seed outputs and verdicts identical.
4. Filesystem `lexists` checks after testing: neither canonical `C.claim.json` nor `C.complete.json` exists.

No real context/floor predictions were analysed, no candidate payload opened, no production helper invoked, no cluster contacted and no commit made. Git's committed-byte boundary in the new tests is mocked using synthetic saved bytes; real git/provenance execution remains for the independent preflight below.

## Exact artifact hashes

| File | SHA256 |
|---|---|
| `src/AB1/ab1_pm3_read.py` (modified, preserving prior dirty guards) | `11dd5aef7e3a86a4d208e3ad75f81b6be80a62bce5ad958fad3c74f454cbf7f0` |
| `src/AB1/tests/test_pm3_admission.py` (six added tests) | `2c49cf1fb9d64f202eb9f49b510b8b991652762f31065d5790697fef0b7c7e3f` |
| `src/AB1/ab1c_transfer_report.py` (unchanged) | `d47f597712bb793a00a7dff9da104a6b43eb09f5bac845fc2c90d462efddd9ef` |
| `experiments/AGENTIC_delivery_20261114/OPENCODE_BATCHC_CONTEXT_MOCK_20261114.json` (new, synthetic) | `9ee7bbdae973db9818e234c55bb1f21605abca51e3da4638b48d6bf0195038f8` |

The source imports, metadata hashes and stage pinfile inventory in `OPENCODE_BATCHC_ADMISSION_20261114.md` remain applicable. Independent reviewer must verify them afresh against the final release snapshot; implementation hashes do not imply committed binding.

## B2 candidate-free preflight — PREPARED, NOT EXECUTED

Assign a distinct reviewer. This is a real existing-floor/learner numerical validation, unlike the synthetic author tests. It requires lead authorization for those existing reference values, **not candidate archive access**. Never run the production reader or `_validate_native_archive` as preflight. The code below calls only the context helper, floor helper and descriptive companion; no main reader, archive loader, candidate source, scoring model or once-claim function.

### Review before execution

1. Independently review the context patch, six tests and source hashes above; inspect the exact delta relative to the earlier audited guarded reader, preserving its overlay/identity/order/once repairs.
2. Verify all source, metadata and pinfile hashes in the admission audit, including the live absolute floor path used by `check.py`. Check that the reader-relative context path and companion ROOT refer to the intended reviewed repository. Record HEAD and worktree state; coordinate any approved source commit/pin update with MAIN. Do not commit or reset as part of the preflight.
3. Confirm a fresh output namespace and no candidate input in the proposed commands. Do not delete outputs on failure. Preserve the error and investigate source/input integrity before retry; do not alter floors or numerical tolerances to force a pass.

### Exact floor/context preflight command (reviewer only)

Run from `/home/narolski/smad-next`. Output is create-only in the existing workflow directory. The check performs all 12 floor-type loads and checks the same 2,000-draw helper using an explicitly synthetic zero-valued candidate vector. It does not retain or interpret any synthetic effect size or verdict. Floor values are real existing references: this command is deliberately **not executed by this implementation author**.

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 \
/home/narolski/mambamorph-code/.venv-spark/bin/python -I - <<'PY'
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
PY
```

The constant synthetic vector tests candidate-independent floor-helper execution and bootstrap feasibility; it does not validate candidate score identity, archive provenance, real network-minus-floor findings or new statistical coverage. Record full stderr/exit status, elapsed time, interpreter/package versions and hashes as part of the independent receipt. If a preflight fails before output publication, retain the log; absence of output is not success.

### Exact descriptive learner command (reviewer only; NOT EXECUTED)

After separately checking the unchanged companion hash and its registered input pins, use this fresh exclusive output:

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 \
/home/narolski/mambamorph-code/.venv-spark/bin/python -I \
  src/AB1/ab1c_transfer_report.py \
  --out experiments/AGENTIC_delivery_20261114/OPENCODE_BATCHC_B2_REVIEWER_TRANSFER_20261114.json
```

This validates stage-11/12 inputs, sel360 row/label/component equality, common cross-arm metadata, 360/240 row counts, finite learner values and summary reproduction at 1e-12. Reviewer checks all three arms and descriptive labels and records output hash. It must not be described as D-stratified inference or a candidate result. No refit, new threshold or network-minus-learner inference is authorized.

## Remaining handoff

B1 implementation is ready for separate review, not independently approved. B2 is prepared only. MAIN still needs opaque integrity/provenance verification for all 30 archives, exact source/input release binding, registered output/arrival dispositions and independent admission. Native payload facts remain unknown until the authorized guarded read. No automatic retry, scientific GO, NEXT action or publication change follows from this repair.
