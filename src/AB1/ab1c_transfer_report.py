"""Descriptive Batch-C same-data learner companion; no candidate archive access.

AB1 amendments 7/7b and ADV amendment 6/addendum require these printed references.
Reproduce the existing per-row summaries, embed the existing transfer summaries,
and retain exact row IDs/labels/components. No new hypothesis, CI, model fit,
threshold calibration, or network-minus-learner inference is performed.

Production (after review): python -I src/AB1/ab1c_transfer_report.py --out FILE
Synthetic checks: python -I src/AB1/ab1c_transfer_report.py --self-test
The exclusive output create refuses overwriting. Inputs must be committed,
unchanged, and match committed stage-11/12 pins (plus sel360 stage pin).
"""
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
FDIR = ROOT / 'experiments/ADV_shortcut-floors/floors'
ARMS = ('SpV', 'BN', 'BV')
LIST_SHA = {
    'SpV': 'f6521d96de7d93ff62232c4eb8236d2560cf39f2e8ca6a56d676f3c0c39af759',
    'BN': 'c1b4497bb59343b7f5dd48149e300fb136533790724dfdf83aa395a703fe6af1',
    'BV': 'ee4e227b2cd6648d196b5d61300a9cf483c85f05a80afae0fd6e774153baf04f',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def committed(path):
    relative = path.relative_to(ROOT).as_posix()
    saved = subprocess.run(['git', '-C', str(ROOT), 'show', 'HEAD:' + relative],
                           check=True, capture_output=True).stdout
    data = path.read_bytes()
    need(data == saved, 'uncommitted input bytes: ' + relative)
    return data


def load_pinned(name, stage=None):
    path = FDIR / name
    data = committed(path)
    digest = hashlib.sha256(data).hexdigest()
    candidates = [FDIR / ('pins_stage' + str(stage) + '.sha256')] if stage else sorted(FDIR.glob('pins_stage*.sha256'))
    for pf in candidates:
        pins = committed(pf).decode().splitlines()
        if digest + '  ' + name in pins:
            return data, {'path': path.relative_to(ROOT).as_posix(), 'sha256': digest,
                          'pinfile': pf.relative_to(ROOT).as_posix(),
                          'pinfile_sha256': hashlib.sha256(pf.read_bytes()).hexdigest()}
    raise ValueError('no committed pin: ' + name)


def auc(rows, model):
    pos = sorted(float(r[model]) for r in rows if int(r['label']) == 1)
    neg = sorted(float(r[model]) for r in rows if int(r['label']) == 0)
    need(pos and neg, 'AUC requires both classes')
    from bisect import bisect_left, bisect_right
    return sum((bisect_left(neg, x) + bisect_right(neg, x)) / 2 for x in pos) / (len(pos) * len(neg))


def metadata(rows):
    result = {}
    for r in rows:
        key = (r['set'], r['id'])
        need(key not in result, 'duplicate row key')
        need(r['set'] in ('sel360', 'splice80'), 'unexpected row set')
        need(int(r['label']) in (0, 1), 'invalid label')
        need(int(r['component']) >= 0, 'invalid component')
        for model in ('logreg', 'gbt'):
            need(math.isfinite(float(r[model])), 'nonfinite learner score')
        result[key] = (r['rung'], int(r['label']), int(r['component']))
    return result


def summarize(rows, exact_counts=True):
    metadata(rows)
    sel = [r for r in rows if r['set'] == 'sel360']
    spl = [r for r in rows if r['set'] == 'splice80']
    need(all(r['rung'] == '' for r in sel), 'unexpected sel360 rung')
    need(all(r['rung'] in ('S4', 'S3', 'S0') and int(r['label']) == int(r['rung'] == 'S4') for r in spl),
         'splice label/rung mismatch')
    if exact_counts:
        need(len(sel) == 360 and sum(int(r['label']) for r in sel) == 180, 'sel360 counts differ')
        need(len(spl) == 240 and all(sum(r['rung'] == k for r in spl) == 80 for k in ('S4', 'S3', 'S0')),
             'splice80 counts differ')
    compare = [r for r in spl if r['rung'] in ('S4', 'S3')]
    out = {'sel360': {'n': len(sel), **{m: auc(sel, m) for m in ('logreg', 'gbt')}},
           'splice80': {'n': len(spl), 'S4_vs_S3': {m: auc(compare, m) for m in ('logreg', 'gbt')}}}
    for m, threshold in (('logreg', 0), ('gbt', 0.5)):
        out['splice80']['flag_' + m] = {}
        for k in ('S4', 'S3', 'S0'):
            group = [r for r in spl if r['rung'] == k]
            need(group, 'missing splice rung')
            out['splice80']['flag_' + m][k] = sum(float(r[m]) > threshold for r in group) / len(group)
    return out


def same_summary(actual, expected):
    need(actual.keys() == expected.keys(), 'summary keys differ')
    for k in actual:
        if isinstance(actual[k], dict):
            same_summary(actual[k], expected[k])
        else:
            need(abs(float(actual[k]) - float(expected[k])) < 1e-12, 'summary value differs: ' + k)


def build_report():
    raw, pin = load_pinned('sel360_rows.csv')
    sel = list(csv.DictReader(io.StringIO(raw.decode())))
    expected = {r['id']: (int(r['label']), int(r['component'])) for r in sel}
    need(len(sel) == len(expected) == 360, 'reference selection rows differ')
    output = {'schema': 'ab1c-transfer-print-v1', 'scope': 'registered descriptive learner references only',
              'hypothesis_test': False, 'network_scores_read': False, 'new_fit': False,
              'notes': [
                  'AUCs in reproduced summaries are unstratified, as in ADV amendment 6; they are not the D-stratified AB1 primary statistic.',
                  'sel360 is OpenCV R4 versus R3 on 100 development and 80 clean test hosts; splice80 contains S4/S3/S0 on 80 clean test hosts.',
                  'Components are preserved within each set; numerical component IDs across different sets are not interchangeable.',
                  'Full transfer JSONs include original contrast populations; do not relabel test191 AUCs as clean80.',
                  'Learner fixed thresholds (logreg > 0, gbt > 0.5) reproduce ADV summaries, not candidate operating thresholds.',
                  'These learners are trained on each named training list; they are not in-domain cross-fitted floors or new candidate results.',
                  'No network-minus-learner difference, significance verdict, or new bootstrap is computed.'
              ], 'pins': [pin], 'arms': {}}
    common = None
    for arm in ARMS:
        stage = 12 if arm == 'BV' else 11
        inputs = {}
        for suffix in ('.json', '_rows.csv', '_rows_summary.json'):
            data, p = load_pinned('transfer_' + arm + suffix, stage)
            inputs[suffix] = data
            output['pins'].append(p)
        rows = list(csv.DictReader(io.StringIO(inputs['_rows.csv'].decode())))
        meta = metadata(rows)
        if common is None:
            common = meta
        else:
            need(meta == common, 'arm row/label/rung/component mismatch')
        actual_sel = {i: (label, comp) for (s, i), (_, label, comp) in meta.items() if s == 'sel360'}
        need(actual_sel == expected, 'sel360 identity/label/component mismatch')
        ref = json.loads(inputs['_rows_summary.json'])
        full = json.loads(inputs['.json'])
        need(ref['arm'] == full['arm'] == arm and ref['list_sha256'] == LIST_SHA[arm], 'arm/list provenance mismatch')
        computed = summarize(rows)
        same_summary(computed, ref['summary'])
        output['arms'][arm] = {'list_sha256': ref['list_sha256'], 'transfer_summary_registered': full,
                               'per_row_summary_reproduced': computed}
    output['row_metadata'] = [{'set': s, 'id': i, 'rung': r, 'label': label, 'component': comp}
                              for (s, i), (r, label, comp) in sorted(common.items())]
    return output


def self_test():
    rows = [dict(set='sel360', id='p', rung='', label=1, component=0, logreg=1., gbt=.5),
            dict(set='sel360', id='n', rung='', label=0, component=1, logreg=0., gbt=.5)]
    for k, score in (('S4', 1.), ('S3', 0.), ('S0', -.2)):
        rows.append(dict(set='splice80', id=k, rung=k, label=int(k == 'S4'), component=0,
                         logreg=score, gbt=.5 + score / 4))
    summary = summarize(rows, exact_counts=False)
    need(summary['sel360']['logreg'] == 1 and summary['sel360']['gbt'] == .5, 'tie AUC failure')
    need(summary['splice80']['flag_gbt']['S3'] == 0, 'strict threshold failure')
    same_summary(summary, json.loads(json.dumps(summary)))
    bads = [rows + [rows[0]], [{**r, 'gbt': float('nan')} for r in rows],
            [{**r, 'label': 0} if r['rung'] == 'S4' else r for r in rows]]
    for bad in bads:
        try:
            summarize(bad, exact_counts=False)
        except ValueError:
            pass
        else:
            raise AssertionError('bad synthetic fixture accepted')
    try:
        summarize(rows)
    except ValueError:
        pass
    else:
        raise AssertionError('wrong counts accepted')
    print('PASS: tied AUC, strict thresholds, summary roundtrip, duplicate/nonfinite/label/count rejection; synthetic only')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path)
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if a.self_test:
        need(a.out is None, '--self-test does not create a report')
        self_test()
        return
    need(a.out is not None, '--out is required')
    need(not a.out.exists(), 'output already exists')
    report = build_report()
    with a.out.open('x') as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print('Wrote registered descriptive learner references:', a.out)


if __name__ == '__main__':
    main()
