"""Pinned FS1 BCE continuation; original loader/loss/optimizer unchanged."""
import hashlib,pathlib,sys
p=pathlib.Path(sys.argv[1]);raw=p.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='cbb2cbd1b9a3eb59ab080a540a98aab0f6ead51ea69364d2debe06a984b8c1c5'
s=raw.decode()
needle='    model.to(dev).train()'
assert s.count(needle)==1
patch='''    assert a.regime == 'd0' and a.split == 'train90' and not a.smoke
    assert not C.train_items('d0','val10',a.lofo), 'val10 must be empty'
    assert a.bs == 248 and a.accum == 1 and a.steps in (2,100) and a.final == 'last'
    assert a.opt == 'adamw' and a.pos_weight == 1 and a.aug == 'flip'
    assert a.sampler == 'prior' and a.recipe == 'v1'
    assert len(rows)==248 and len({r['path'] for r in rows})==248
    assert sum(int(r['label']) for r in rows)==124
    assert {r['kind'] for r in rows}=={'lad_S3','lad_S4'}
    assert all(r['hist']=='native' for r in rows)
    warm_path=os.environ['HN_WARMSTART']
    warm = torch.load(warm_path,map_location='cpu',weights_only=True)
    train_names = {n for n,p in model.named_parameters() if p.requires_grad}
    assert set(warm) == train_names
    missing,unexpected = model.load_state_dict(warm,strict=False)
    assert not unexpected and not (set(missing)&train_names)
    pathlib.Path(out,'HN_warmstart.json').write_text(json.dumps({'path':warm_path,'trainable_parameter_names':sorted(train_names),'optimizer':'fresh AdamW; no inherited moments','conditioning':'single admitted AB1 Sb408 initialization'},indent=2)+'\\n')
    pathlib.Path(out,'sprint_schedule.json').write_text(json.dumps({'mode':'full248rowshufflecycle','steps':a.steps,'batch_size':248,'exact_per_image_exposures':a.steps,'total_image_exposures':248*a.steps,'row_ids':[r['id'] for r in rows],'seed':a.seed},indent=2)+'\\n')
    model.to(dev).train()'''
pathlib.Path(sys.argv[2]).write_text(s.replace(needle,patch))
