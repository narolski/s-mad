"""Real gradient pilot; no benchmark loaders, archive readers or training."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()


def write_json(p, v):
    with p.open('x') as f:
        json.dump(v, f, indent=2, allow_nan=False); f.write('\n')
        f.flush(); os.fsync(f.fileno())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--inventory', required=True, type=Path)
    ap.add_argument('--model', required=True)
    ap.add_argument('--out', required=True, type=Path)
    a = ap.parse_args()
    if not sys.flags.isolated:
        raise RuntimeError('python -I required')
    inv = json.loads(a.inventory.read_text())
    if sha(__file__) != inv['runner_sha256']:
        raise ValueError('runner hash differs from reviewed inventory')
    cfg = inv['models'][a.model]
    for row in inv['sources'] + cfg['checkpoints'] + inv['inputs']:
        if sha(row['path']) != row['sha256']:
            raise ValueError('pinned bytes changed: '+row['path'])
    a.out.mkdir(parents=True, exist_ok=False)
    t0 = time.monotonic()
    receipt = dict(model=a.model, started_utc=datetime.now(timezone.utc).isoformat(),
                   inventory_sha256=sha(a.inventory), runner_sha256=sha(__file__),
                   scope='Private descriptive single-person aligned-frame local sensitivity pilot',
                   status='STARTED', model_config=cfg, inputs=inv['inputs'])
    write_json(a.out/'started.json',receipt)
    try:
        import numpy as np
        import torch
        from PIL import Image
        torch.set_num_threads(2)
        torch.manual_seed(20261114); np.random.seed(20261114)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        dev = 'cuda' if torch.cuda.is_available() else 'cpu'
        os.environ['HF_HOME'] = inv['hf_home']
        os.environ['HF_HUB_OFFLINE'] = '1'
        os.environ['TRANSFORMERS_OFFLINE'] = '1'
        sys.path.insert(0,cfg['code'])
        import common as C
        if cfg['kind'] == 'own':
            meta = json.loads(Path(cfg['meta']).read_text())
            if meta['seed'] != 403 or meta['final'] != 'last':
                raise ValueError('fixed seed/checkpoint identity mismatch')
            model,_ = C.build_run_model(meta)
            state = torch.load(cfg['checkpoint'], map_location='cpu', weights_only=True)
            expected = {n for n,p in model.named_parameters() if p.requires_grad}
            if set(state) != expected:
                raise ValueError('trainable checkpoint keys differ from exact trainable model keys')
            incompat = model.load_state_dict(state,strict=False)
            if incompat.unexpected_keys or set(incompat.missing_keys) != set(model.state_dict())-set(state):
                raise ValueError('nontrainable reconstruction mismatch')
            fwd = lambda x: C.forward_logit(model,x)[0].float().reshape(-1)
            res = meta['res']
        else:
            import a12_released as R
            R.torch,R.np,R.C = torch,np,C
            spec = R.RELEASES[a.model]
            model = R.build_release(spec)
            model.load_state_dict(R.extract_state(R.load_release(Path(cfg['checkpoint'])),spec),strict=True)
            fwd = lambda x: R.head_logit(model(R.adapt_input(x,spec)),spec['classes'],spec['morph_index'])
            res = spec['res']
        model.to(dev).eval()
        for p in model.parameters(): p.requires_grad_(False)
        ds = C.ImageItems([(x['path'],0) for x in inv['inputs']],res,root='/')
        precision_references=[]
        for i in range(len(inv['inputs'])):
            xx=ds[i][0].unsqueeze(0).to(dev).float()
            with torch.no_grad():
                torch.backends.cuda.matmul.allow_tf32=True
                torch.backends.cudnn.allow_tf32=True
                ht=fwd(xx).item();hf=fwd(xx.flip([3])).item()
                torch.backends.cuda.matmul.allow_tf32=False
                torch.backends.cudnn.allow_tf32=False
                rt=fwd(xx).item();rf=fwd(xx.flip([3])).item()
            precision_references.append((ht,hf,rt,rf))
        model.double()
        maps, results = [],[]
        for i,item in enumerate(inv['inputs']):
            x = ds[i][0].unsqueeze(0).to(dev).double().requires_grad_(True)
            historical_tf32,historical_flip_tf32,reference_fp32,reference_flip_fp32=precision_references[i]
            with torch.no_grad():
                ref = fwd(x).item(); flip_ref = fwd(x.flip([3])).item()
            z = fwd(x)
            g, = torch.autograd.grad(z.sum(),x)
            zval = z.item()
            if abs(zval-ref)>1e-5 or abs(float(torch.sigmoid(z.detach()))-float(torch.sigmoid(torch.tensor(ref,dtype=z.dtype))))>1e-6:
                raise ValueError('no-grad/autograd forward parity failed')
            with torch.no_grad():
                repeat = fwd(x).item(); flip_repeat = fwd(x.flip([3])).item()
            if max(abs(repeat-ref),abs(flip_repeat-flip_ref))>1e-5:
                raise ValueError('repeat noTTA/flip forward parity failed')
            if not torch.isfinite(g).all() or not float(g.abs().max())>0:
                raise ValueError('nonfinite or zero input gradient')
            gen = torch.Generator(device=dev).manual_seed(20261114+i)
            direction = x.detach()*(torch.randint(0,2,x.shape,generator=gen,device=dev)*2-1)
            analytic = (g*direction).sum().item()
            checks = []
            for eps in (1e-3,1e-4):
                with torch.no_grad():
                    numeric = (fwd(x.detach()+eps*direction).item()-fwd(x.detach()-eps*direction).item())/(2*eps)
                error = abs(numeric-analytic)
                checks.append(dict(epsilon=eps,numeric=numeric,analytic=analytic,absolute_error=error,
                                   passed=error<=max(.01,.1*abs(analytic))))
            if not any(c['passed'] for c in checks):
                raise ValueError('finite-difference diagnostic failed: '+str(checks))
            raw = g.detach().cpu().numpy()[0]
            pixels = x.detach().cpu().numpy()[0]
            gxi = raw*pixels
            d = dict(input=pixels,gradient=raw,gradient_times_input=gxi,
                     signed=gxi.sum(0),magnitude=np.abs(gxi).sum(0),
                     gradient_magnitude=np.abs(raw).sum(0))
            if not all(np.isfinite(v).all() for v in d.values()):
                raise ValueError('nonfinite raw map')
            name=item['condition']
            np.savez(a.out/(name+'_raw.npz'),**d)
            maps.append(d)
            results.append(dict(condition=name,source_sha256=item['sha256'],logit_morph=zval,
                                score_noTTA=float(torch.sigmoid(torch.tensor(zval))),
                                flip_logit=flip_ref,score_TTA=float((torch.sigmoid(torch.tensor(zval))+torch.sigmoid(torch.tensor(flip_ref)))/2),
                                repeated_noTTA_logit=repeat,repeated_flip_logit=flip_repeat,
                                historical_tf32_noTTA_logit=historical_tf32,
                                historical_tf32_flip_logit=historical_flip_tf32,
                                fp32_noTTA_logit=reference_fp32,fp32_flip_logit=reference_flip_fp32,
                                fp64_minus_fp32_logit=zval-reference_fp32,
                                fp64_minus_tf32_logit=zval-historical_tf32,
                                raw_npz_sha256=sha(a.out/(name+'_raw.npz')),
                                directional_derivative=checks))
            print(a.model,name,'real gradient done',flush=True)
        # Algebraic dependency check only, not evidence of faithful localization.
        head = [m for m in model.modules() if isinstance(m,torch.nn.Linear)][-1]
        saved = {k:v.detach().clone() for k,v in head.state_dict().items()}
        try:
            with torch.no_grad():
                for p in head.parameters(): p.zero_()
            xx=ds[0][0].unsqueeze(0).to(dev).double().requires_grad_(True)
            zz=fwd(xx); gg,=torch.autograd.grad(zz.sum(),xx)
            head_zero=dict(logit=zz.item(),gradient_max=gg.abs().max().item(),passed=bool(gg.abs().max().item()<=1e-8))
        finally:
            head.load_state_dict(saved,strict=True)
        if not head_zero['passed']:
            raise ValueError('head-zero algebraic sanity failed')
        scales = dict(signed=max(float(np.abs(d['signed']).max()) for d in maps),
                      magnitude=max(float(d['magnitude'].max()) for d in maps),
                      gradient_magnitude=max(float(d['gradient_magnitude'].max()) for d in maps))
        for item,d in zip(inv['inputs'],maps):
            n=item['condition']
            Image.fromarray(np.rint(np.clip(d['input'].transpose(1,2,0),0,1)*255).astype('uint8')).save(a.out/(n+'_input_grid.png'))
            v=np.clip(d['signed']/max(scales['signed'],1e-30),-1,1)
            rgb=np.stack([1-np.maximum(-v,0),1-np.abs(v),1-np.maximum(v,0)],axis=2)
            Image.fromarray(np.rint(rgb*255).astype('uint8')).save(a.out/(n+'_signed_heatmap.png'))
            for key in ('magnitude','gradient_magnitude'):
                v=np.clip(d[key]/max(scales[key],1e-30),0,1)
                Image.fromarray(np.rint(v*255).astype('uint8')).save(a.out/(n+'_'+key+'_grayscale.png'))
        native=results[0]['logit_morph']
        for row in results: row['logit_delta_from_native']=row['logit_morph']-native
        receipt.update(status='COMPLETE',results=results,scales=scales,head_zero_algebraic_check=head_zero,
                       seconds=time.monotonic()-t0,device=torch.cuda.get_device_name(0) if dev=='cuda' else dev,
                       versions=dict(python=sys.version,torch=torch.__version__,numpy=np.__version__),
                       tf32_matmul=torch.backends.cuda.matmul.allow_tf32,tf32_cudnn=torch.backends.cudnn.allow_tf32,
                       arithmetic_dtype='float64 network/input; inherited forward_logit casts output to float32',
                       image_preprocessing='Existing aligned-frame ImageItems only; no own-face recropping.',
                       maps_explain='noTTA morph logit; sensitivity only; signed and raw gradient have separate common scales across3conditions',
                       completed_utc=datetime.now(timezone.utc).isoformat())
        write_json(a.out/'result.json',receipt)
    except Exception as exc:
        receipt.update(status='FAILED',error=repr(exc),seconds=time.monotonic()-t0)
        write_json(a.out/'failure.json',receipt)
        raise


if __name__=='__main__': main()
