"""Synthetic-only efficient SDPA backward localization; no model/data/weight loading."""
import argparse,contextlib,hashlib,json,sys
import torch
import torch.nn.functional as F

def main():
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=('default','math'),required=True);a=p.parse_args()
 assert sys.flags.isolated and sys.version_info[:2]==(3,9)
 assert torch.__version__=='2.0.1+cu118' and torch.version.cuda=='11.8'
 assert torch.cuda.device_count()==1 and 'H100' in torch.cuda.get_device_name(0)
 torch.manual_seed(20261114)
 # Inferred from exact B/16 source:224px/16=>14*14+CLS197;768dim/12heads=64.
 # Original L,N,E projection then view/transpose/view gives this noncontiguous layout.
 vals=[];hashes=[]
 for _ in range(3):
  cpu=torch.randn(197,256,768,dtype=torch.float32)
  hashes.append(hashlib.sha256(cpu.numpy().tobytes()).hexdigest())
  v=cpu.view(197,256*12,64).transpose(0,1).view(256,12,197,64).to('cuda').requires_grad_(True)
  vals.append(v)
 grad_cpu=torch.randn(256,12,197,64,dtype=torch.float32)
 grad_hash=hashlib.sha256(grad_cpu.numpy().tobytes()).hexdigest();grad=grad_cpu.to('cuda')
 torch.cuda.synchronize()
 print(json.dumps({'phase':'INPUTS_READY','mode':a.mode,'shape':list(vals[0].shape),'strides':[list(v.stride()) for v in vals],
  'dtype':str(vals[0].dtype),'input_hashes':hashes,'upstream_gradient_hash':grad_hash,
  'torch':torch.__version__,'cuda':torch.version.cuda,'device':torch.cuda.get_device_name(0),
  'dropout':0.,'mask':None,'causal':False,'shape_status':'SOURCE_INFERRED_NOT_CAPTURED_ACTIVATIONS'}),flush=True)
 ctx=contextlib.nullcontext() if a.mode=='default' else torch.backends.cuda.sdp_kernel(enable_flash=False,enable_math=True,enable_mem_efficient=False)
 with ctx,torch.autograd.detect_anomaly(check_nan=False):
  y=F.scaled_dot_product_attention(*vals,attn_mask=None,dropout_p=0.,is_causal=False)
  torch.cuda.synchronize()
  print(json.dumps({'phase':'FORWARD_OK','grad_fn':type(y.grad_fn).__name__,'mode':a.mode}),flush=True)
  y.backward(grad)
  torch.cuda.synchronize()
  assert torch.isfinite(y).all().item()
  assert all(v.grad is not None and torch.isfinite(v.grad).all().item() for v in vals)
  print(json.dumps({'phase':'BACKWARD_FINITE','mode':a.mode,'output_norm':y.norm().item(),
   'gradient_norms':[v.grad.norm().item() for v in vals],
   'interpretation':'Synthetic operator completion only; no fit/smoke/production/equivalence admission'}),flush=True)
if __name__=='__main__':main()
