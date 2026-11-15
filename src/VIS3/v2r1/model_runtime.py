"""Model-loading body copied verbatim (AST) from pinned VIS2 worker49fac2668... .
No new model APIs, checkpoints, preprocessing or precision choices.
"""
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace
from contracts import need


def load_runtime(inv,model_name):
    args=SimpleNamespace(model=model_name)
    cfg=inv['models'][model_name]
    import numpy as np
    import torch
    from PIL import Image
    need(torch.cuda.is_available() and torch.cuda.device_count() == 1 and (torch.cuda.get_device_name(0) == 'NVIDIA GB10'), 'fixed GB10 required; no CPU/H100 substitution')
    need(torch.__version__ == '2.12.1+cu130' and torch.version.cuda == '13.0', 'fixed VIS1 stack required')
    torch.set_num_threads(2)
    torch.manual_seed(20261114)
    np.random.seed(20261114)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = False
    os.environ['HF_HOME'] = inv['hf_home']
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    sys.path.insert(0, cfg['code'])
    import common as C
    if cfg['kind'] == 'own':
        meta = json.loads(Path(cfg['meta']).read_text())
        need(meta['seed'] == 403 and meta['final'] == 'last', 'fixed seed/last required')
        model, _ = C.build_run_model(meta)
        state = torch.load(cfg['checkpoint'], map_location='cpu', weights_only=True)
        need(set(state) == {n for n, p in model.named_parameters() if p.requires_grad}, 'trainable key mismatch')
        inc = model.load_state_dict(state, strict=False)
        need(not inc.unexpected_keys and set(inc.missing_keys) == set(model.state_dict()) - set(state), 'frozen base mismatch')
        fwd = lambda x: C.forward_logit(model, x)[0].float().reshape(-1)
        res = meta['res']
    else:
        import a12_released as R
        R.torch, R.np, R.C = (torch, np, C)
        spec = R.RELEASES[args.model]
        model = R.build_release(spec)
        model.load_state_dict(R.extract_state(R.load_release(Path(cfg['checkpoint'])), spec), strict=True)
        fwd = lambda x: R.head_logit(model(R.adapt_input(x, spec)), spec['classes'], spec['morph_index'])
        res = spec['res']
    model.to('cuda').eval()
    for p in model.parameters():
        p.requires_grad_(False)
    return model,fwd,res,C,torch,np
