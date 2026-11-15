"""Original pinned FS1 trainer; validation only, unchanged training loss/loader."""
import hashlib
import pathlib
import sys

p=pathlib.Path(sys.argv[1]);raw=p.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='cbb2cbd1b9a3eb59ab080a540a98aab0f6ead51ea69364d2debe06a984b8c1c5'
s=raw.decode();needle='    model, extra = C.build_model(a.arch, a.res, a.drop_path)'
assert s.count(needle)==1
validation='''    assert a.regime == 'd0' and a.split == 'train90' and not a.smoke
    assert not C.train_items('d0', 'val10', a.lofo), 'val10 must be empty'
    assert a.bs == 32 and a.final == 'last' and a.accum == 1 and a.opt == 'adamw'
    assert a.steps in (2,100) and len(rows) == 32
    assert len({r['path'] for r in rows}) == 32
    assert sum(int(r['label']) for r in rows) == 16
    assert {r['kind'] for r in rows} == {'lad_S3','lad_S4'}
    assert sum(r['db']=='feret' for r in rows) == 16
    assert sum(r['db']=='frgc' for r in rows) == 16
    assert a.sampler == 'prior' and a.recipe == 'v1' and a.aug == 'flip'
    pathlib.Path(out, 'sprint_schedule.json').write_text(json.dumps({
        'mode': 'full32rowshufflecycle', 'steps': a.steps, 'batch_size':32,
        'exact_per_image_exposures':a.steps, 'total_image_exposures':32*a.steps,
        'row_ids':[r['id'] for r in rows], 'seed':a.seed},indent=2)+'\\n')
'''
pathlib.Path(sys.argv[2]).write_text(s.replace(needle,validation+needle))
