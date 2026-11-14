import hashlib
import json
import pathlib
import sys
r=json.loads(pathlib.Path(sys.argv[1]).read_text());p=pathlib.Path(sys.argv[2])
assert r['id']=='SPRINT5_3' and r['decision']=='GO_TRAINING_BASELINE_ONLY'
assert r['scope']=='training-only anchor/reference, no intervention fit or scientific dev read'
assert r['reviewer'] and r['reviewer']!=r['author']
assert r['source_sums_sha256']==hashlib.sha256((p/'SHA256SUMS').read_bytes()).hexdigest()
assert hashlib.sha256(pathlib.Path(r['independent_review_path']).read_bytes()).hexdigest()==r['independent_review_sha256']
print('TRAIN_BASELINE_RELEASE_VALID')
