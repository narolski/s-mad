"""Patch precisely the pinned FS1 source; never edit original pack files."""
import hashlib
import pathlib
import sys

BASE_SHA = 'cbb2cbd1b9a3eb59ab080a540a98aab0f6ead51ea69364d2debe06a984b8c1c5'
p = pathlib.Path(sys.argv[1])
raw = p.read_bytes()
if hashlib.sha256(raw).hexdigest() != BASE_SHA:
    raise SystemExit('FS1 train.py pin mismatch')
s = raw.decode()
old = '    dl = C.train_loader(rows, a.res, a.bs, a.workers, a.seed, a.recipe, a.sampler, sbi_p, sbi_frac, sbi_kw, sbi_hull,\n                        a.aug)'
new = '''    import sprint_paired as SP
    sprint_arm = os.environ['SPRINT_ARM']
    assert a.final == 'last' and a.accum == 1 and a.opt == 'adamw'
    assert a.aug == 'flip' and a.recipe == 'v1' and not a.smoke
    assert not arms and not a.kd_teacher and not a.es_snaps
    assert a.pos_weight == 1 and a.label_smoothing == 0
    assert a.regime == 'd0' and a.split == 'train90'
    assert not C.train_items(a.regime, 'val10', a.lofo, tools=tools), 'val10 must be empty'
    dl = SP.loader(C, rows, a.res, a.bs, a.workers, a.seed, steps, sprint_arm, out)'''
assert s.count(old) == 1
s = s.replace(old, new)
old = '            loss = F.binary_cross_entropy_with_logits(logit, yt, pos_weight=pw)'
new = old + '''
            if sprint_arm == 'paired_rank':
                rank_term, rank_pairs = SP.rank_loss(logit, idx, rows, margin=1.0, return_count=True)
                if step < 2 or step % 1000 == 0:
                    print(f'SPRINT_RANK step={step} pairs={rank_pairs} rank_loss={float(rank_term.detach()):.8f}', flush=True)
                loss = loss + 0.1 * rank_term'''
assert s.count(old) == 1
s = s.replace(old, new)
pathlib.Path(sys.argv[2]).write_text(s)
