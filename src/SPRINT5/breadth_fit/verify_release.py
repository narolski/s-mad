import hashlib
import json
import pathlib
import sys

r=json.loads(pathlib.Path(sys.argv[1]).read_text());source=pathlib.Path(sys.argv[2]);mode=sys.argv[3]
assert mode in ('smoke','pilot') and r['decision']=='GO_'+mode.upper()
assert r['id']=='SPRINT5_4' and r['seeds']==[511,512,513,514,515]
assert r['fresh_seed_allocation_pass'] is True
assert r['source_sums_sha256']==hashlib.sha256((source/'SHA256SUMS').read_bytes()).hexdigest()
assert r['reviewer'] and r['reviewer']!=r['author']
assert hashlib.sha256(pathlib.Path(r['independent_review_path']).read_bytes()).hexdigest()==r['independent_review_sha256']
if mode=='pilot':
    assert r['h100_smoke_pass'] is True and r['byte_gate_pass'] is True
    assert len(r['smoke_archives'])==2
    assert {e['arm'] for e in r['smoke_archives']}=={'narrow_more_variants','broad_fewer_variants'}
    for e in r['smoke_archives']:
        h=hashlib.sha256()
        with pathlib.Path(e['path']).open('rb') as f:
            for b in iter(lambda:f.read(4<<20),b''):h.update(b)
        assert h.hexdigest()==e['sha256']
print('SPRINT5_4_RELEASE_VALID',mode)
