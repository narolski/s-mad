"""Synthetic diagnostic for the H100 gradient-clipping failure; no model or data is loaded.

Run each --foreach mode in a fresh process in the registered AD5 H100 environment.
An illegal instruction can poison the CUDA context, so never test alternatives in that process.
This is a runtime diagnostic, not permission to change the registered training path.
"""
import argparse
import json
import torch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--foreach', choices=['default', 'true', 'false'], required=True)
    parser.add_argument('--device', choices=['cpu', 'cuda'], default='cuda')
    args = parser.parse_args()
    torch.manual_seed(20261114)
    params = []
    # CLIP ViT-B/16 LoRA q/v rank-2-shaped synthetic gradients, plus header-shaped tensors.
    for _ in range(24):
        for shape in [(768, 2), (2, 768)]:
            param = torch.nn.Parameter(torch.zeros(shape, device=args.device))
            param.grad = torch.randn(shape).to(args.device)
            params.append(param)
    for shape in [(2, 512), (2,)]:
        param = torch.nn.Parameter(torch.zeros(shape, device=args.device))
        param.grad = torch.randn(shape).to(args.device)
        params.append(param)
    if args.device == 'cuda':
        torch.cuda.synchronize()
    kwargs = {} if args.foreach == 'default' else {'foreach': args.foreach == 'true'}
    norm = torch.nn.utils.clip_grad_norm_(params, max_norm=5, norm_type=2, **kwargs)
    if args.device == 'cuda':
        torch.cuda.synchronize()
    norm_after = torch.linalg.vector_norm(torch.stack([p.grad.norm() for p in params]))
    assert torch.isfinite(norm) and torch.isfinite(norm_after)
    assert float(norm_after) <= 5.0001
    print(json.dumps({'torch': torch.__version__, 'cuda': torch.version.cuda,
                      'device': args.device, 'foreach': args.foreach,
                      'norm_before': float(norm), 'norm_after': float(norm_after),
                      'gradient_sum_after': sum(float(p.grad.sum()) for p in params),
                      'synthetic_tensors': len(params), 'pass': True}))


if __name__ == '__main__':
    main()
