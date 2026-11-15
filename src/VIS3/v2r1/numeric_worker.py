"""SOURCE-ONLY VIS3 numeric adapter; requires independent construction admission and NEW phase grant."""
import argparse
import importlib.metadata
import math
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parent))
import contracts as K


def construction_admission(inv,grant,inventory_sha256):
    from authority_snapshot import capture_json
    root=Path(inv['construction_output']).resolve()
    receipt_path=root/'CONSTRUCTION_RECEIPT.json';roster_path=root/'DERIVED_INPUT_ROSTER.json'
    K.need(grant['construction_receipt_path']==str(receipt_path),'wrong construction receipt')
    receipt_snap=capture_json(receipt_path,grant['construction_receipt_sha256']);receipt=receipt_snap.value
    K.need(receipt['status']=='COMPLETE_PRIVATE_CONSTRUCTION_ONLY' and receipt['inventory_sha256']==inventory_sha256,'construction inventory mismatch')
    K.need(Path(grant['constructed_input_admission_path']).resolve().is_relative_to(Path(inv['repository']).resolve()),'admission outside repository')
    admission_snap=capture_json(grant['constructed_input_admission_path'],grant['constructed_input_admission_sha256'])
    admission=admission_snap.value
    K.need(admission['decision']=='GO_VIS3_PRIVATE_DERIVED_INPUTS' and admission['reviewer'] and admission['reviewer']!=admission['author'] and admission['author']==receipt['author'],'OTHER input review required')
    K.need(admission['construction_receipt_sha256']==receipt_snap.sha256 and admission['inventory_sha256']==inventory_sha256,'admission scope differs')
    K.need(admission['derivative_roster_sha256']==receipt['derivative_roster_sha256']==grant['derivative_roster_sha256'],'actual roster hash differs')
    K.need(admission['render_allowed'] is False and admission['publication_allowed'] is False,'input admission cannot grant presentation')
    roster_snap=capture_json(roster_path,grant['derivative_roster_sha256'],kind=list);roster=roster_snap.value
    K.need([p['id'] for p in roster]==K.IDS,'four fixed constructed cases required')
    for item in roster:
        host='00042' if item['id'].startswith('42') else '00056'
        donor=host if item['id'].endswith('samephoto') else ('00056' if host=='00042' else '00042')
        K.need(item['host_photo']==host and item['donor_photo']==donor and item['host_history']=='native512 only','host/donor/history differs')
        K.need(Path(item['path']).resolve().parent==root,'constructed input outside reviewed output')
    mask=receipt['actual_alpha'];K.need(Path(mask['path']).resolve().parent==root,'wrong mask path')
    K.need(admission['actual_alpha_npy_sha256']==mask['sha256'],'mask not independently admitted')
    return receipt,roster,{'construction_receipt_sha256':receipt_snap.sha256,
                          'constructed_input_admission_sha256':admission_snap.sha256,'derivative_roster_sha256':roster_snap.sha256}


def smoke_admission(inv,grant,captured,model):
    from authority_snapshot import capture_bytes,capture_json
    K.need(Path(grant['smoke_postreview_path']).resolve().is_relative_to(Path(inv['repository']).resolve()),'smoke review outside repository')
    snap=capture_json(grant['smoke_postreview_path'],grant['smoke_postreview_sha256']);review=snap.value
    K.need(review['decision']=='GO_VIS3_FULL_NUMERIC' and model in review['models'] and review['reviewer']!=review['author'],'full not independently admitted')
    K.need(review['inventory_sha256']==captured['inventory_sha256'] and review['derivative_roster_sha256']==captured['derivative_roster_sha256'],'smoke review scope differs')
    K.need(review['generated_regional_indexing_verified'] is True,'smoke lacks boundary cells; generated regional-index gate required')
    result_path=Path(inv['numeric_output'])/'smoke'/model/'RESULT.json'
    result_snap=capture_bytes(result_path,review['smoke_result_sha256'][model])
    return {'smoke_postreview_sha256':snap.sha256,'admitted_smoke_result_sha256':result_snap.sha256}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inventory',type=Path,required=True);ap.add_argument('--release',type=Path,required=True)
    ap.add_argument('--model',choices=['selfmad_hrnet_w18','A','B'],required=True);ap.add_argument('--phase',choices=['smoke','full'],required=True)
    ap.add_argument('--expected-release-sha256',required=True)
    args=ap.parse_args();inv,grant,captured=K.authority(args.inventory,args.release,args.phase,args.model,expected_release_sha256=args.expected_release_sha256)
    K.need(grant['new_derived_image_numeric_allowed'] is True and grant['original_four_anchor_inference_allowed'] is True,'numeric scope not granted')
    receipt,roster,derived_captured=construction_admission(inv,grant,captured['inventory_sha256']);captured.update(derived_captured)
    if args.phase=='full':captured.update(smoke_admission(inv,grant,captured,args.model))
    for pkg,v in inv['environment']['packages'].items():K.need(importlib.metadata.version(pkg)==v,'runtime package changed')
    K.need(sys.version.split()[0]==inv['environment']['python'],'Python changed')
    out=Path(inv['numeric_output'])/args.phase/args.model;out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    K.write(out/'STARTED.json',{'phase':args.phase,'model':args.model,'authority_snapshots':captured,'inventory_sha256':captured['inventory_sha256'],'release_sha256':captured['root_release_sha256'],'roster_sha256':captured['derivative_roster_sha256']})
    try:
        # All scientific payload reads occur only AFTER phase authority and OTHER actual-input admission.
        for p in inv['anchor_inputs']+roster:K.need(K.sha(p['path'])==p['sha256'],'image payload changed')
        for p in inv['models'][args.model]['checkpoints']:K.need(K.sha(p['path'])==p['sha256'],'checkpoint changed')
        K.need(K.sha(receipt['actual_alpha']['path'])==receipt['actual_alpha']['sha256'],'actual mask changed')
        from construct_driver import exact_rgb
        import numpy as np
        alpha=np.load(receipt['actual_alpha']['path'],allow_pickle=False)
        constructor=K.load(inv['constructor_path'],'frozen_vis3_constructor')
        plan=K.geometry(alpha,constructor)
        worker=K.load(inv['reference_worker'],'approved_vis2_worker')
        from model_runtime import load_runtime
        model,fwd,res,C,torch,np=load_runtime(inv,args.model)
        anchors=[exact_rgb(p['path']) for p in inv['anchor_inputs']]
        ds=C.ImageItems([(p['path'],0) for p in inv['anchor_inputs']],res,root='/')
        anchor_results=[]
        with torch.no_grad():
            for i,a in enumerate(anchors):
                p=worker.prep(a,res,torch,np);K.need(torch.equal(p,ds[i][0]),'reference ImageItems preprocessing differs')
                x=p.unsqueeze(0).to('cuda');z=fwd(x).item();repeat=fwd(x).item()
                noop=fwd(worker.prep(a.copy(),res,torch,np).unsqueeze(0).to('cuda')).item()
                expected=inv['baseline_logits'][args.model][inv['anchor_inputs'][i]['id']]
                K.need(all(math.isfinite(v) for v in (z,repeat,noop)) and max(abs(z-repeat),abs(z-noop),abs(z-expected))<=1e-5,'four original anchor/repeat/literalcopy gate failed')
                anchor_results.append({'id':inv['anchor_inputs'][i]['id'],'z':z,'repeat_z':repeat,'literal_copy_z':noop,'reference_z':expected})
        images=[exact_rgb(p['path']) for p in roster]
        for a,p in zip(images,roster):K.need(K.rawsha(a)==p['rgb_raw_sha256'],'derived pixels differ from admitted capture')
        ds=C.ImageItems([(p['path'],0) for p in roster],res,root='/')
        baseline=[];baseline_checks=[]
        with torch.no_grad():
            for i,a in enumerate(images):
                p=worker.prep(a,res,torch,np);K.need(torch.equal(p,ds[i][0]),'derived ImageItems preprocessing differs')
                x=p.unsqueeze(0).to('cuda');z=fwd(x).item();repeat=fwd(x).item()
                noop=fwd(worker.prep(a.copy(),res,torch,np).unsqueeze(0).to('cuda')).item()
                K.need(all(math.isfinite(v) for v in (z,repeat,noop)) and max(abs(z-repeat),abs(z-noop))<=1e-5,'new baseline/repeat/literalcopy failed')
                baseline.append(z);baseline_checks.append({'input_id':K.IDS[i],'z':z,'repeat_z':repeat,'literal_copy_z':noop,'old_reference':None})
        tasklist=K.tasks(args.phase);measured=[]
        torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats();loop_start=time.monotonic()
        with torch.no_grad():
            for i,a in enumerate(images):
                rows=[]
                for fill,j in tasklist:
                    y,x=worker.cells()[j];masked=worker.replace(a,y,x,fill)
                    z=fwd(worker.prep(masked,res,torch,np).unsqueeze(0).to('cuda')).item()
                    K.need(math.isfinite(z),'nonfinite response')
                    rows.append({'input_id':K.IDS[i],'fill_uint8':fill,'cell':j,'row':j//8,'col':j%8,'native_x':x,'native_y':y,'native_area':4096,
                                 'baseline_logit':baseline[i],'occluded_logit':z,'delta_logit':z-baseline[i]})
                measured.extend(rows);K.write(out/(K.IDS[i]+'_RESPONSES.json'),rows)
        torch.cuda.synchronize();loop_seconds=time.monotonic()-loop_start
        regional=K.regional_means(measured,args.phase)
        K.need(len(measured)==4*len(tasklist),'response count differs')
        result={'experiment':inv['experiment'],'status':'COMPLETE','phase':args.phase,'model':args.model,'responses':measured,'regional_means':regional,
                'authority_snapshots':captured,'inventory_sha256':captured['inventory_sha256'],'release_sha256':captured['root_release_sha256'],'construction_receipt_sha256':captured['construction_receipt_sha256'],
                'actual_derived_roster_sha256':captured['derivative_roster_sha256'],'actual_alpha':receipt['actual_alpha'],'per_source_captures':receipt['per_source_captures'],
                'anchor_controls':anchor_results,'derived_baseline_checks':baseline_checks,'baseline_logits':baseline,'inputs_ids':K.IDS,'fills_uint8':[0,128],
                'grid':'8x8 native512,64px singlepatch interventions','threshold':None,'decision_flips':None,'source_pixels_exported':False,'maps_rendered':False,
                'regional_estimand':'mean of four separate single4096pixelpatch intervention deltas, NOT simultaneous region removal',
                'smoke_scope':'mechanics/timing only; registered smoke has no selected boundary cells; generated grouping gate precedes full',
                'claim_scope':'NEW controlled soft-splice illustration; potentially exposed two photographs; no benchmark/anatomical/identity-causal/ranking claim',
                'res':res,'batch_size':1,'precision':'float32 noTTA noAMP TF32off; no gradients','gpu':torch.cuda.get_device_name(0),'torch':torch.__version__,'cuda':torch.version.cuda,
                'loop_seconds':loop_seconds,'seconds_per_response':loop_seconds/len(measured),'peak_allocated_bytes':torch.cuda.max_memory_allocated(),
                'peak_reserved_bytes':torch.cuda.max_memory_reserved(),'elapsed_seconds':time.monotonic()-start,'publication_allowed':False}
        K.write(out/'RESULT.json',result);K.write(out/'SHA256.json',{p.name:K.sha(p) for p in out.iterdir() if p.is_file()})
        print('VIS3_NUMERIC_COMPLETE_PENDING_OTHER_REVIEW',args.phase,args.model,len(measured))
    except BaseException as exc:
        K.write(out/'FAILED.json',{'authority_snapshots':captured,'error_type':type(exc).__name__,'error':str(exc),'elapsed_seconds':time.monotonic()-start});raise


if __name__=='__main__':main()
