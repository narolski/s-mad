"""Pure technical outcome gates; no model/data/torch imports."""
import math


def expected_names():
    model=[f'visual.transformer.resblocks.{i}.attn.{p}.w_lora_{ab}' for i in range(12) for p in ('q_proj','v_proj') for ab in ('A','B')]
    return {'model':sorted(model),'header':['linear.bias','linear.weight']}


def gradients(records):
    expected=expected_names()
    for group,names in expected.items():
        rows=records[group]
        assert sorted(rows)==names,'unexpected/missing trainable names '+group
        for name,item in rows.items():
            assert item['present'] and item['finite'],'missing/nonfinite expected gradient '+group+':'+name
            assert math.isfinite(item['norm']) and item['norm']>=0
        # A gradients may be zero at first step since source initializes B=0.
        assert any(v['norm']>0 for v in rows.values()),'all expected gradients zero '+group


def updates(records):
    for group,names in expected_names().items():
        rows=records[group];assert sorted(rows)==names
        assert all(v['finite'] and v['optimizer_step']==1 for v in rows.values()),'nonfinite/missing/non-single update '+group
        assert any(v['changed'] for v in rows.values()),'all trainable tensors unchanged '+group


def batch_order(expected,observed):
    assert len(expected)==len(observed)==256
    assert observed==expected,'actual first dataset visits differ from original sampler order'
