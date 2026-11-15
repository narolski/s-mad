"""Extract only the permitted training-reference constants from an admitted tar."""
import hashlib
import json
import pathlib
import sys
import tarfile
r=json.loads(pathlib.Path(sys.argv[1]).read_text());out=pathlib.Path(sys.argv[2]);assert not out.exists();out.mkdir(parents=True)
path=pathlib.Path(r['baseline_archive_path']);h=hashlib.sha256()
with path.open('rb') as f:
    for b in iter(lambda:f.read(4<<20),b''):h.update(b)
assert h.hexdigest()==r['baseline_archive_sha256']
prefix='SPRINT5_3_TRAIN_BASELINE_AB1Sb408_v1/'
with tarfile.open(path) as t:
    status=t.extractfile(prefix+'status.txt').read().decode();assert 'exit_status=0' in status.splitlines()
    g=json.load(t.extractfile(prefix+'platform_gate/gate.json'))
    b=json.load(t.extractfile(prefix+'platform_gate/battery.json'))
    assert g['byte_identical'] is True and g['n_differ']==0
    assert b['netcheck']['passed'] is True and b['netcheck']['n_common']==21277
    raw=t.extractfile(prefix+'training_only/TRAIN_ONLY_reference.json').read()
    ref=json.loads(raw)
    assert ref['scope']=='TRAINING_ONLY warm-start continuation constants; not evaluation calibration or performance'
    (out/'TRAIN_ONLY_reference.json').write_bytes(raw)
print('TRAINING_REFERENCE_EXTRACTED',hashlib.sha256(raw).hexdigest())
