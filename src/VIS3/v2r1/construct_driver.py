"""SOURCE-ONLY proposal: separate ROOT grant required BEFORE real PNG reads/transforms."""
import argparse
import ast
import hashlib
import importlib.metadata
import json
import os
import platform
from pathlib import Path
import sys
import time
import threading

# -I does not put this file's directory on sys.path. Only source-local imports are inserted.
sys.path.insert(0,str(Path(__file__).resolve().parent))
import contracts as K


def exact_rgb(path):
    from PIL import Image
    import numpy as np
    with Image.open(path) as im:
        K.need(im.format=='PNG' and im.mode=='RGB' and im.size==(512,512),'exact RGB512 PNG required; no convert/resize')
        a=np.asarray(im).copy()
    K.need(a.dtype==np.uint8 and a.shape==(512,512,3),'bad image dtype/shape')
    return a


def lossless(path,a):
    from PIL import Image
    import numpy as np
    with Path(path).open('xb') as f:
        Image.fromarray(a).save(f,format='PNG');f.flush();os.fsync(f.fileno())
    K.need(np.array_equal(exact_rgb(path),a),'saved PNG roundtrip differs')


def construct_record(images,module,namespace):
    """Metadata-return wrapper; frozen constructor/math unmodified, second capture equality checked."""
    import numpy as np
    output,alpha,plan=module.construct_pair(images[0],images[1],namespace)
    captures=[]
    for image,ident in zip(images,['42','56']):
        same,c=module.capture_registered(image,namespace)
        K.need(np.array_equal(same,output[ident+'_samephoto']) and np.array_equal(c['alpha'],alpha),'second capture differs')
        K.need(c['sigma']==11 and c['shift_xy']==[-1,-19],'captured operation parameters changed')
        captures.append(c)
    for i,ident in enumerate(['42','56']):
        j=1-i
        K.need(np.array_equal(output[ident+'_crossphoto'],module.compose(images[i],captures[j]['source'],alpha)),'cross arithmetic differs')
        for kind in ('samephoto','crossphoto'):
            K.need(np.array_equal(output[ident+'_'+kind][alpha[...,0]==0],images[i][alpha[...,0]==0]),'changed outside actual alpha support')
    K.geometry(alpha,module)
    provenance=[{'source_photo':photo,'shift_xy':c['shift_xy'],'feather_sigma':c['sigma'],
                 'input_rgb_raw_sha256':K.rawsha(a),'transformed_source_rgb_raw_sha256':K.rawsha(c['source']),
                 'source_dtype':str(c['source'].dtype),'source_shape':list(c['source'].shape),
                 'alpha_raw_float32_sha256':K.rawsha(c['alpha'])}
                for photo,a,c in zip(['00042','00056'],images,captures)]
    return output,alpha,plan,provenance


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inventory',required=True,type=Path);ap.add_argument('--release',required=True,type=Path)
    ap.add_argument('--expected-release-sha256',required=True)
    args=ap.parse_args()
    # Authority before input PNG hash/decode, any transforms, and output directory creation.
    inv,grant,captured=K.authority(args.inventory,args.release,'construct',expected_release_sha256=args.expected_release_sha256)
    K.need(grant['new_derivative_construction_allowed'] is True,'new transform not granted')
    K.need(platform.machine()=='aarch64','fixed constructor architecture required')
    K.need(threading.active_count()==1,'isolated single-threaded RNG process required')
    K.need(sys.version.split()[0]=='3.12.3','constructor Python changed')
    for pkg,v in inv['constructor_packages'].items():K.need(importlib.metadata.version(pkg)==v,'constructor package changed')
    out=Path(inv['construction_output']);out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    K.write(out/'STARTED.json',{'inventory_sha256':captured['inventory_sha256'],'release_sha256':captured['root_release_sha256'],'stage':'construct','authority_snapshots':captured})
    try:
        import numpy as np
        for p in inv['construction_inputs']:K.need(K.sha(p['path'])==p['sha256'],'source PNG changed')
        images=[exact_rgb(p['path']) for p in inv['construction_inputs']]
        K.need([p['id'] for p in inv['construction_inputs']]==['00042_native','00056_native'],'input order changed')
        module=K.load(inv['constructor_path'],'vis3_frozen_constructor');namespace=module.load_registered(inv['registered_source_path'])
        arrays,alpha,plan,provenance=construct_record(images,module,namespace)
        roster=[]
        for ident in K.IDS:
            path=out/(ident+'.png');lossless(path,arrays[ident])
            host='00042' if ident.startswith('42') else '00056'
            donor=host if ident.endswith('samephoto') else ('00056' if host=='00042' else '00042')
            roster.append({'id':ident,'host_photo':host,'donor_photo':donor,'host_history':'native512 only','condition':ident.split('_',1)[1],
                           'path':str(path),'sha256':K.sha(path),'rgb_raw_sha256':K.rawsha(arrays[ident]),'shape':[512,512,3],'dtype':'uint8'})
        mask=out/'actual_used_alpha.npy'
        with mask.open('xb') as f:np.save(f,alpha,allow_pickle=False);f.flush();os.fsync(f.fileno())
        saved=np.load(mask,allow_pickle=False);K.need(np.array_equal(saved,alpha),'saved alpha mismatch')
        mask_record={'path':str(mask),'sha256':K.sha(mask),'raw_float32_sha256':K.rawsha(alpha),'dtype':'float32','shape':[512,512,1],
                     'range':[float(alpha.min()),float(alpha.max())],'geometry':plan}
        roster_digest=K.write(out/'DERIVED_INPUT_ROSTER.json',roster)
        source=Path(inv['registered_source_path']).read_bytes();tree=ast.parse(source)
        body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='self_blend_int'][0]
        result={'author':'shortcut_visual_examples','status':'COMPLETE_PRIVATE_CONSTRUCTION_ONLY','inventory_sha256':captured['inventory_sha256'],'release_sha256':captured['root_release_sha256'],
                'authority_snapshots':captured,'prereg_sha256':captured['prereg_sha256'],'constructor_sha256':K.sha(inv['constructor_path']),
                'registered_source_sha256':K.sha(inv['registered_source_path']),
                'registered_function_ast_sha256':hashlib.sha256(ast.dump(body,include_attributes=False).encode()).hexdigest(),
                'per_source_captures':provenance,'actual_alpha':mask_record,'derivative_roster_path':str(out/'DERIVED_INPUT_ROSTER.json'),
                'derivative_roster_sha256':roster_digest,'source_inputs':inv['construction_inputs'],
                'rights':inv['rights'],'source_pixel_exports':'only four registered lossless derivedPNGs and actualalpha; no transformed-source export',
                'literal_copy_sham':'image.copy(), not floating same-source blend','elapsed_seconds':time.monotonic()-start,
                'numeric_admission':'HOLD_OTHER_REVIEW_REQUIRED','render_allowed':False,'publication_allowed':False}
        K.write(out/'CONSTRUCTION_RECEIPT.json',result)
        K.write(out/'SHA256.json',{p.name:K.sha(p) for p in out.iterdir() if p.is_file()})
        print('VIS3_CPU_CONSTRUCTION_COMPLETE_PENDING_OTHER_INPUT_ADMISSION')
    except BaseException as exc:
        K.write(out/'FAILED.json',{'authority_snapshots':captured,'error_type':type(exc).__name__,'error':str(exc),'elapsed_seconds':time.monotonic()-start});raise


if __name__=='__main__':main()
