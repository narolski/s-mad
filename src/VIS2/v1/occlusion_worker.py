"""VIS2 real constant-occlusion measurement; prospective code, not executed on faces."""
import argparse
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import sys
import time
import subprocess


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def need(ok,message):
    if not ok:raise ValueError(message)


def write(p,obj):
    with Path(p).open('x') as f:
        json.dump(obj,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())


def cells():return [(y,x) for y in range(0,512,64) for x in range(0,512,64)]


def replace(a,y,x,fill):
    need((y,x) in cells() and fill in (0,128),'unregistered patch/fill')
    b=a.copy();b[y:y+64,x:x+64]=fill
    return b


def prep(a,res,torch,np):
    # Exact OCC1 and common.ImageItems pixel operations, before any model adapter.
    from PIL import Image
    im=Image.fromarray(a).convert('RGB')
    if im.size!=(res,res):im=im.resize((res,res),Image.BILINEAR)
    return torch.from_numpy(np.asarray(im,np.float32)/255.).permute(2,0,1)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--inventory',type=Path,required=True)
    ap.add_argument('--release',type=Path)
    ap.add_argument('--model',choices=['selfmad_hrnet_w18','A','B'])
    ap.add_argument('--phase',choices=['smoke','full'])
    ap.add_argument('--metadata-only',action='store_true')
    args=ap.parse_args();need(sys.flags.isolated,'python -I required')
    inv=json.loads(args.inventory.read_text())
    need(inv['experiment']=='VIS2_PRIVATE_OCCLUSION_V1','wrong experiment')
    need(inv['fills']==[0,128] and inv['patch']==64 and inv['native_size']==512,'geometry changed')
    need(inv['inputs_ids']==['00042_native','00042_history','00056_native','00056_history'],'exact four inputs required')
    need(sha(__file__)==inv['worker_sha256'],'worker changed')
    for p in inv['source_pins']+inv['inputs']:
        need(sha(p['path'])==p['sha256'],'input/source changed: '+p['path'])
    for pkg,version in inv['environment']['packages'].items():
        need(importlib.metadata.version(pkg)==version,'package changed: '+pkg)
    need(sys.version.split()[0]==inv['environment']['python'],'Python changed')
    if args.metadata_only:
        print('VIS2_SOURCE_INPUT_PACKAGE_METADATA_ONLY_PASS; no model, image transform, GPU or response read')
        return
    need(args.release and args.model and args.phase,'new release/model/phase required')
    release=json.loads(args.release.read_text())
    need(release['decision']=='GO_VIS2_NUMERIC_OCCLUSION_ONLY','no new VIS2 execution grant')
    need(release['author']!=release['reviewer'] and release['reviewer'],'independent review required')
    need(release['inventory_sha256']==sha(args.inventory),'inventory differs')
    need(sha(release['independent_review_path'])==release['independent_review_sha256'],'review changed')
    need(release['phase']==args.phase and args.model in release['models'],'phase/model not released')
    need(release['new_private_occlusion_transform_allowed'] is True,'legacy VIS1 render grant insufficient')
    need(release['source_pixel_export_allowed'] is False and release['new_overlay_render_allowed'] is False,'numeric worker cannot export/render source pixels')
    need(release['prereg_sha256']==sha(inv['prereg_path']),'prereg changed')
    code=Path(__file__).parent
    need(release['source_manifest_sha256']==sha(code/'SHA256SUMS'),'source manifest changed')
    for line in (code/'SHA256SUMS').read_text().splitlines():
        h,n=line.split('  ',1);need((code/n).resolve().is_relative_to(code.resolve()) and sha(code/n)==h,'source not frozen')
    repo=Path(inv['repository'])
    need(str(args.release.resolve()).startswith(str(repo.resolve())+'/'),'release must be in reviewed repository')
    owned=list(inv['owned_paths'])
    need(owned and len(set(owned))==len(owned),'invalid owned source/input paths')
    for rel in owned:
        need(not Path(rel).is_absolute() and '..' not in Path(rel).parts,'unsafe owned path')
        subprocess.run(['git','ls-files','--error-unmatch','--',rel],cwd=repo,check=True,capture_output=True)
        historical=subprocess.check_output(['git','show',release['source_commit']+':'+rel],cwd=repo)
        need(hashlib.sha256(historical).hexdigest()==sha(repo/rel),'source differs from bound committed snapshot')
    release_rel=str(args.release.resolve().relative_to(repo.resolve()))
    subprocess.run(['git','ls-files','--error-unmatch','--',release_rel],cwd=repo,check=True,capture_output=True)
    need(not subprocess.check_output(['git','status','--porcelain','--',*owned,release_rel],cwd=repo,text=True),'owned inputs/source or release are not clean')
    cfg=inv['models'][args.model]
    for p in cfg['checkpoints']:need(sha(p['path'])==p['sha256'],'weight bytes changed')
    if args.phase=='full':
        need(sha(release['smoke_postreview_path'])==release['smoke_postreview_sha256'],'full requires OTHER smoke postreview')
    out=Path(inv['output_root'])/args.phase/args.model
    out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    write(out/'STARTED.json',{'inventory_sha256':sha(args.inventory),'release_sha256':sha(args.release),'phase':args.phase,'model':args.model,'source_pixels_exported':False})
    try:
        import numpy as np
        import torch
        from PIL import Image
        need(torch.cuda.is_available() and torch.cuda.device_count()==1 and torch.cuda.get_device_name(0)=='NVIDIA GB10','fixed GB10 required; no CPU/H100 substitution')
        need(torch.__version__=='2.12.1+cu130' and torch.version.cuda=='13.0','fixed VIS1 stack required')
        torch.set_num_threads(2);torch.manual_seed(20261114);np.random.seed(20261114)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        torch.backends.cudnn.benchmark=False;torch.backends.cudnn.deterministic=False
        os.environ['HF_HOME']=inv['hf_home'];os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
        sys.path.insert(0,cfg['code']);import common as C
        if cfg['kind']=='own':
            meta=json.loads(Path(cfg['meta']).read_text());need(meta['seed']==403 and meta['final']=='last','fixed seed/last required')
            model,_=C.build_run_model(meta);state=torch.load(cfg['checkpoint'],map_location='cpu',weights_only=True)
            need(set(state)=={n for n,p in model.named_parameters() if p.requires_grad},'trainable key mismatch')
            inc=model.load_state_dict(state,strict=False)
            need(not inc.unexpected_keys and set(inc.missing_keys)==set(model.state_dict())-set(state),'frozen base mismatch')
            fwd=lambda x:C.forward_logit(model,x)[0].float().reshape(-1);res=meta['res']
        else:
            import a12_released as R
            R.torch,R.np,R.C=torch,np,C;spec=R.RELEASES[args.model];model=R.build_release(spec)
            model.load_state_dict(R.extract_state(R.load_release(Path(cfg['checkpoint'])),spec),strict=True)
            fwd=lambda x:R.head_logit(model(R.adapt_input(x,spec)),spec['classes'],spec['morph_index']);res=spec['res']
        model.to('cuda').eval()
        for p in model.parameters():p.requires_grad_(False)
        ds=C.ImageItems([(p['path'],0) for p in inv['inputs']],res,root='/')
        images=[np.asarray(Image.open(p['path']).convert('RGB')) for p in inv['inputs']]
        need(all(a.shape==(512,512,3) and a.dtype==np.uint8 for a in images),'exact native RGB512 required')
        base=[]
        with torch.no_grad():
            for i,a in enumerate(images):
                p=prep(a,res,torch,np);need(torch.equal(p,ds[i][0]),'memory/native preprocessing mismatch')
                x=p.unsqueeze(0).to('cuda');z=fwd(x).item();repeat=fwd(x).item()
                sham=prep(a.copy(),res,torch,np).unsqueeze(0).to('cuda');noop=fwd(sham).item()
                expected=inv['baseline_logits'][args.model][inv['inputs'][i]['id']]
                need(all(math.isfinite(v) for v in [z,repeat,noop]) and max(abs(z-repeat),abs(z-noop),abs(z-expected))<=1e-5,'four-image VIS1 anchor/repeat/noop failed')
                base.append(z)
        full_tasks=[(fill,j) for fill in (0,128) for j in range(64)]
        tasks=[(fill,j) for fill in (0,128) for j in inv['smoke_cells']] if args.phase=='smoke' else full_tasks
        measured=[]
        with torch.no_grad():
            for i,a in enumerate(images):
                image_rows=[]
                for fill,j in tasks:
                    y,x=cells()[j];masked=replace(a,y,x,fill)
                    z=fwd(prep(masked,res,torch,np).unsqueeze(0).to('cuda')).item()
                    need(math.isfinite(z),'nonfinite response')
                    image_rows.append({'input_id':inv['inputs'][i]['id'],'fill_uint8':fill,'cell':j,'row':j//8,'col':j%8,'native_x':x,'native_y':y,'native_area':4096,'baseline_logit':base[i],'occluded_logit':z,'delta_logit':z-base[i]})
                measured.extend(image_rows)
                # Durable numeric progress; never exports RGB/masked images/biometric features.
                write(out/(inv['inputs'][i]['id']+'_RESPONSES.json'),image_rows)
        need(len(measured)==4*len(tasks),'missing response')
        result={'experiment':inv['experiment'],'status':'COMPLETE','phase':args.phase,'model':args.model,'inputs_ids':inv['inputs_ids'],
                'inventory_sha256':sha(args.inventory),'res':res,'baseline_logits':base,'responses':measured,'fills_uint8':[0,128],
                'grid':'8x8 at native512,64px cells; preprocessing follows model-specific standard resize','batch_size':1,
                'seam_masks':'NONE_EXISTS_ON_THESE_GENUINE_PHOTOS; no seam localization claim',
                'threshold':None,'decision_flips':None,'source_pixels_exported':False,'maps_rendered':False,
                'comparison_scope':'Descriptive perturbation response on two potentially exposed photographs; no error-rate, causal or utility conclusion',
                'elapsed_seconds':time.monotonic()-start,'gpu':torch.cuda.get_device_name(0),'torch':torch.__version__,'cuda':torch.version.cuda,
                'noTTA':True,'tf32_matmul':False,'tf32_cudnn':False,'precision':'float32; no autocast/no gradients'}
        write(out/'RESULT.json',result);write(out/'SHA256.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
        print('VIS2_COMPLETE',args.phase,args.model,len(measured))
    except BaseException as exc:
        write(out/'FAILED.json',{'error_type':type(exc).__name__,'error':str(exc),'elapsed_seconds':time.monotonic()-start})
        raise


if __name__=='__main__':main()
