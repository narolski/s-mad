"""Prospective controlled seam construction; exact archived SBI-int body, not a benchmark morph."""
import ast
import hashlib
from pathlib import Path
import random
import sys

SBI_SHA='3c4b06bd4bcd1a51d36afb6bd7dff6f6dc46efa8869eee271719ab33f93ed84f'
SEED=20261115


def need(ok,message):
    if not ok:raise ValueError(message)


def load_registered(path):
    """Extract unchanged function ASTs to avoid importing unrelated dataset modules."""
    import numpy as np
    import cv2
    raw=Path(path).read_bytes();need(hashlib.sha256(raw).hexdigest()==SBI_SHA,'registered SBI source changed')
    tree=ast.parse(raw)
    names={'_hull_mask','_ellipse_mask','_feather','_rgb_jitter','self_blend_int'}
    body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in names]
    constants=[x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SBI_RATIOS' for t in x.targets)]
    need({x.name for x in body}==names and len(constants)==1,'registered function selection incomplete')
    # Preserve exact original bodies/defaults; only unrelated imports/dataset access are omitted.
    module=ast.Module(body=constants+body,type_ignores=[])
    namespace={'np':np,'cv2':cv2,'random':random}
    exec(compile(ast.fix_missing_locations(module),str(path),'exec'),namespace)
    return namespace


def capture_registered(image,namespace):
    """No altered source/RNG calls: observe actual returned src/mask using a profile hook."""
    import numpy as np
    need(image.shape==(512,512,3) and image.dtype==np.uint8,'native RGB512 required')
    need(sys.getprofile() is None,'do not replace existing profiler')
    fn=namespace['self_blend_int'];feather=namespace['_feather'];captured={}
    old_py=random.getstate();old_np=np.random.get_state()
    def profile(frame,event,arg):
        if event=='return' and frame.f_code is feather.__code__:captured['sigma']=int(frame.f_locals['k'])
        if event=='return' and frame.f_code is fn.__code__:
            captured['source']=frame.f_locals['src'].copy();captured['alpha']=frame.f_locals['mask'].copy()
            captured['shift_xy']=[int(frame.f_locals['dx']),int(frame.f_locals['dy'])]
    try:
        random.seed(SEED);np.random.seed(SEED);sys.setprofile(profile)
        output=fn(image,None,rng=random.Random(SEED),max_shift=.04,min_shift=3,ratios=(.5,))
    finally:
        sys.setprofile(None);random.setstate(old_py);np.random.set_state(old_np)
    need(set(captured)=={'sigma','source','alpha','shift_xy'},'actual constructor mask capture incomplete')
    need(np.array_equal(output,compose(image,captured['source'],captured['alpha'])),'captured arithmetic differs from unmodified generator')
    return output,captured


def compose(base,source,alpha):
    """Exact registered self_blend_int float32/clip/truncate arithmetic; cross-source use is NEW."""
    import numpy as np
    need(base.shape==source.shape==(512,512,3),'image shape mismatch')
    need(alpha.shape==(512,512,1) and alpha.dtype==np.float32,'actual generator alpha required')
    need(np.isfinite(alpha).all() and alpha.min()>=0 and alpha.max()<=.5,'unexpected alpha range')
    out=alpha*source.astype(np.float32)+(1.0-alpha)*base.astype(np.float32)
    return np.clip(out,0,255).astype(np.uint8)


def region_plan(alpha):
    """Pixel/shape-equal grid controls chosen BEFORE detector scores, from ACTUAL generation alpha."""
    import numpy as np
    need(alpha.shape==(512,512,1),'actual alpha shape')
    q=alpha[...,0]/.5
    transition=(q>=.10)&(q<=.90)
    seam=[];surround=[];rows=[]
    for i in range(64):
        y,x=(i//8)*64,(i%8)*64
        cut=(slice(y,y+64),slice(x,x+64));fraction=float(transition[cut].mean())
        is_seam=fraction>=.10;is_surround=bool((q[cut]==0).all())
        if is_seam:seam.append(i)
        if is_surround:surround.append(i)
        rows.append({'cell':i,'native_y':y,'native_x':x,'area':4096,'transition_fraction':fraction,'transition_patch':is_seam,'strict_surround_patch':is_surround})
    k=min(len(seam),len(surround));selected_seam=seam[:k];selected_surround=surround[:k]
    need(not(set(selected_seam)&set(selected_surround)),'overlapping region controls')
    return {'selection':'row-major first K=min(candidate seam,surround) before scores; all64views retained',
            'seam_candidates':seam,'surround_candidates':surround,'K':k,'selected_seam':selected_seam,'selected_surround':selected_surround,
            'area_per_patch':4096,'total_masked_area_per_region':k*4096,
            'region_contrast_status':'READY_DESCRIPTIVE_ONLY' if k>=3 else 'INSUFFICIENT_REGION_SUPPORT_HOLD','cells':rows,
            'scope':'Patch overlapping actual new soft blend transition; not pure seam removal, position/texture not matched.'}


def construct_pair(native42,native56,namespace):
    """SOURCE ONLY: prospective CPU function, NOT authorized on real photos yet.

    Exact same-photo SBI is unchanged; cross-photo recombination is explicitly NEW.
    Original/historical genuine arrays are not assigned fake splice masks.
    """
    import numpy as np
    same42,a=capture_registered(native42,namespace)
    same56,b=capture_registered(native56,namespace)
    need(np.array_equal(a['alpha'],b['alpha']),'constructor geometry differs across source photos')
    return {'42_samephoto':same42,'42_crossphoto':compose(native42,b['source'],a['alpha']),
            '56_samephoto':same56,'56_crossphoto':compose(native56,a['source'],b['alpha'])},a['alpha'],region_plan(a['alpha'])
