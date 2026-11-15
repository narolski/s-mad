"""VIS1 score-only pilot. Grounded in pinned XAI FP32 runner, no gradients/training."""
import argparse
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import sys
import time


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def need(ok, message):
    if not ok:
        raise ValueError(message)


def write_new(path, obj):
    with Path(path).open('x') as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write('\n'); f.flush(); os.fsync(f.fileno())


def summarize(rows):
    need(len(rows) == 5 and len({r['id'] for r in rows}) == 5, 'exact five input IDs required')
    lookup = {r['id']: r for r in rows}
    need(set(lookup) == {'reference_00010', '00042_native', '00042_history',
                         '00056_native', '00056_history'}, 'wrong IDs')
    for r in rows:
        need(math.isfinite(r['logit']) and math.isfinite(r['repeat_logit']), 'nonfinite logit')
        need(abs(r['logit'] - r['repeat_logit']) <= 1e-5, 'repeat/no-op parity failed')
    return [{'photo_key': key, 'native_logit': lookup[key + '_native']['logit'],
             'history_logit': lookup[key + '_history']['logit'],
             'delta_logit': lookup[key + '_history']['logit'] - lookup[key + '_native']['logit'],
             'threshold': None, 'decision_flip': None,
             'scope': 'Existing compound processing history; descriptive, not JPEG-only'}
            for key in ('00042', '00056')]


def preflight(inventory_path, inv):
    need(inv['scope'] == 'VIS1_PRIVATE_DESCRIPTIVE_ONLY' and inv['threshold'] is None, 'scope changed')
    need(sha(__file__) == inv['runner_sha256'], 'runner changed')
    need(inv['models_order'] == ['selfmad_hrnet_w18', 'A', 'B'], 'fixed model list changed')
    for x in inv['sources'] + inv['inputs']:
        need(sha(x['path']) == x['sha256'], 'source/input changed: ' + x['path'])
    for cfg in inv['models'].values():
        for x in cfg['checkpoints']:
            need(sha(x['path']) == x['sha256'], 'checkpoint bytes changed')
    for pkg, version in inv['environment']['packages'].items():
        need(importlib.metadata.version(pkg) == version, 'environment changed: ' + pkg)
    need(sys.version.split()[0] == inv['environment']['python'], 'Python changed')
    need(os.path.realpath(sys.executable) == inv['environment']['python_resolved'], 'Python executable changed')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--inventory', required=True, type=Path)
    ap.add_argument('--release', type=Path)
    ap.add_argument('--model', choices=['selfmad_hrnet_w18', 'A', 'B'])
    ap.add_argument('--out', type=Path)
    ap.add_argument('--metadata-only', action='store_true')
    args = ap.parse_args()
    need(sys.flags.isolated, 'python -I required')
    inv = json.loads(args.inventory.read_text())
    preflight(args.inventory, inv)
    if args.metadata_only:
        print('VIS1_METADATA_PINS_ONLY_PASS; no model import, GPU, score, or output claim')
        return
    need(args.release is not None and args.out is not None and args.model is not None, 'release/model/out required')
    release = json.loads(args.release.read_text())
    need(release['decision'] == 'GO_VIS1_SCORE_ONLY', 'no execution release')
    need(release['author'] != release['reviewer'] and release['reviewer'], 'independent review required')
    need(release['inventory_sha256'] == sha(args.inventory), 'inventory differs after review')
    need(sha(release['independent_review_path']) == release['independent_review_sha256'], 'review changed')
    need(args.model in release['models'], 'model not released')
    need(str(args.out) == str(Path(inv['output_root']) / args.model), 'fixed output path required')
    args.out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    receipt = {'status': 'STARTED', 'inventory_sha256': sha(args.inventory),
               'release_sha256': sha(args.release), 'model': args.model,
               'threshold': None, 'scope': inv['scope']}
    write_new(args.out / 'STARTED.json', receipt)
    try:
        import numpy as np
        import torch
        need(torch.cuda.is_available(), 'registered GB10 GPU unavailable; CPU fallback forbidden')
        need(torch.cuda.device_count() == 1 and torch.cuda.get_device_name(0) == 'NVIDIA GB10', 'GPU changed')
        torch.set_num_threads(2)
        torch.manual_seed(20261114); np.random.seed(20261114)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = inv['environment']['cudnn_benchmark']
        torch.backends.cudnn.deterministic = inv['environment']['cudnn_deterministic']
        os.environ['HF_HOME'] = inv['hf_home']
        os.environ['HF_HUB_OFFLINE'] = '1'; os.environ['TRANSFORMERS_OFFLINE'] = '1'
        cfg = inv['models'][args.model]
        sys.path.insert(0, cfg['code'])
        import common as C
        if cfg['kind'] == 'own':
            # Exact loader/key accounting from reviewed xai_gradient_pilot_fp32.py.
            meta = json.loads(Path(cfg['meta']).read_text())
            need(meta['seed'] == 403 and meta['final'] == 'last', 'fixed seed/last checkpoint required')
            model, _ = C.build_run_model(meta)
            state = torch.load(cfg['checkpoint'], map_location='cpu', weights_only=True)
            expected = {n for n, p in model.named_parameters() if p.requires_grad}
            need(set(state) == expected, 'trainable key mismatch')
            incompatible = model.load_state_dict(state, strict=False)
            need(not incompatible.unexpected_keys and set(incompatible.missing_keys) == set(model.state_dict()) - set(state), 'state mismatch')
            fwd = lambda x: C.forward_logit(model, x)[0].float().reshape(-1)
            res = meta['res']
        else:
            import a12_released as R
            R.torch, R.np, R.C = torch, np, C
            spec = R.RELEASES[args.model]
            model = R.build_release(spec)
            model.load_state_dict(R.extract_state(R.load_release(Path(cfg['checkpoint'])), spec), strict=True)
            fwd = lambda x: R.head_logit(model(R.adapt_input(x, spec)), spec['classes'], spec['morph_index'])
            res = spec['res']
        model.to('cuda').eval()
        for p in model.parameters():
            p.requires_grad_(False)
        ds = C.ImageItems([(x['path'], 0) for x in inv['inputs']], res, root='/')
        results = []
        load_seconds = time.monotonic() - start
        for i, row in enumerate(inv['inputs']):
            x = ds[i][0].unsqueeze(0).to('cuda').float()
            torch.cuda.synchronize(); t = time.monotonic()
            with torch.no_grad():
                z = fwd(x).item(); repeat = fwd(x).item()
            torch.cuda.synchronize()
            need(math.isfinite(z) and abs(z - repeat) <= 1e-5, 'nonfinite/repeat parity failure')
            if row['id'] == 'reference_00010':
                need(abs(z - inv['reference_logits'][args.model]) <= 1e-5, 'existing XAI reference failed; no new scores admitted')
            results.append({'id': row['id'], 'source_sha256': row['sha256'],
                            'logit': z, 'repeat_logit': repeat,
                            'uncalibrated_sigmoid': float(torch.sigmoid(torch.tensor(z))),
                            'seconds_two_forwards': time.monotonic() - t})
        receipt.update(status='COMPLETE', rows=results, pairs=summarize(results),
                       load_seconds=load_seconds, total_seconds=time.monotonic() - start,
                       gpu=torch.cuda.get_device_name(0), torch=torch.__version__, cuda=torch.version.cuda,
                       res=res, tf32_matmul=False, tf32_cudnn=False,
                       noTTA=True, no_gradients=True, no_source_pixels_saved=True,
                       exclusion_limits=inv['overlap_status'])
        write_new(args.out / 'RESULT.json', receipt)
        write_new(args.out / 'SHA256.json', {p.name: sha(p) for p in args.out.iterdir() if p.is_file()})
        print('VIS1_SCORE_ONLY_COMPLETE', args.model, args.out)
    except BaseException as exc:
        write_new(args.out / 'FAILED.json', dict(error_type=type(exc).__name__, error=str(exc), seconds=time.monotonic()-start))
        raise


if __name__ == '__main__':
    main()
