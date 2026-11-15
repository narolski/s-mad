"""Pinned FS1 continuation: common warmstart, fixed sampler, constrained tail hook."""
import hashlib
import pathlib
import sys
p=pathlib.Path(sys.argv[1]);raw=p.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='cbb2cbd1b9a3eb59ab080a540a98aab0f6ead51ea69364d2debe06a984b8c1c5'
s=raw.decode()
def replace(old,new):
    global s
    assert s.count(old)==1,old
    s=s.replace(old,new)
replace('    model.to(dev).train()', '''    assert a.regime == 'd0' and a.split == 'train90' and not a.smoke
    assert not C.train_items('d0','val10',a.lofo)
    assert a.bs == 256 and a.accum == 1 and a.steps in (2,100) and a.final == 'last'
    assert a.opt == 'adamw' and a.pos_weight == 1 and a.aug == 'flip'
    warm = torch.load(os.environ['TAIL_WARMSTART'],map_location='cpu',weights_only=True)
    train_names = {n for n,p in model.named_parameters() if p.requires_grad}
    assert set(warm) == train_names
    missing,unexpected = model.load_state_dict(warm,strict=False)
    assert not unexpected and not (set(missing)&train_names)
    model.to(dev).train()
    import tail_runtime as TP
    tail_context = TP.Context(rows,dev,out)
    tail_context.model = model''')
replace('    dl = C.train_loader(rows, a.res, a.bs, a.workers, a.seed, a.recipe, a.sampler, sbi_p, sbi_frac, sbi_kw, sbi_hull,\n                        a.aug)',
        '    dl = tail_context.loader(C,a.res,a.bs,a.workers,a.seed,steps)')
replace('            loss = F.binary_cross_entropy_with_logits(logit, yt, pos_weight=pw)',
        '''            loss = F.binary_cross_entropy_with_logits(logit, yt, pos_weight=pw) + tail_context.penalty(logit,idx)
            if not torch.isfinite(loss).all():tail_context.fail_closed('nonfinite_total_loss')''')
replace('                opt.step()','                opt.step()\n                tail_context.after_step(step)')
pathlib.Path(sys.argv[2]).write_text(s)
