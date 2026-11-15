"""Fail closed on missing review or unpinned H100 smoke; lead creates receipt."""
import hashlib
import json
import pathlib
import sys

r = json.loads(pathlib.Path(sys.argv[1]).read_text())
source = pathlib.Path(sys.argv[2])
assert r['id'] == 'SPRINT5_1' and r['decision'] == 'GO_PRODUCTION'
assert r['reviewer'] != r['author'] and r['reviewer'] and r['author']
assert r['fresh_seed_allocation_pass'] is True
assert r['h100_smoke_pass'] is True and r['byte_gate_pass'] is True
assert r['seeds'] == [501, 502, 503, 504, 505]
assert r['source_sums_sha256'] == hashlib.sha256((source / 'SHA256SUMS').read_bytes()).hexdigest()
assert len(r['smoke_archives']) == 3
for e in r['smoke_archives']:
    p = pathlib.Path(e['path'])
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(4 << 20), b''):
            h.update(b)
    assert h.hexdigest() == e['sha256']
assert set(e['arm'] for e in r['smoke_archives']) == {'bce', 'paired_bce', 'paired_rank'}
assert hashlib.sha256(pathlib.Path(r['independent_review_path']).read_bytes()).hexdigest() == r['independent_review_sha256']
assert hashlib.sha256(pathlib.Path(r['seed_audit_path']).read_bytes()).hexdigest() == r['seed_audit_sha256']
print('SPRINT5_1 production receipt and smoke hashes verified')
