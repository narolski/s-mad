"""Technical row/finite-output validation inside the scoring job; prints no scores."""
import argparse
import csv
import json
import pathlib

import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--family', required=True)
    parser.add_argument('--scores', required=True)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--rows', type=int, required=True)
    args = parser.parse_args()
    rows = [r for r in csv.DictReader(open(args.manifest)) if r['fam'] == args.family]
    expected = [r['id'] for r in rows]
    assert len(expected) == args.rows and len(set(expected)) == len(expected)
    with np.load(args.scores, allow_pickle=False) as data:
        assert data['id'].tolist() == expected, 'row ID/order differs from pinned family'
        values = data['logit']
        assert values.shape == (args.rows,) and np.isfinite(values).all(), 'missing/non-finite logits'
        assert int(data['seed']) == args.seed, 'seed differs'
    print(json.dumps({'family': args.family, 'rows': args.rows, 'finite': True,
                      'same_id_order': True, 'seed': args.seed}))


if __name__ == '__main__':
    main()
