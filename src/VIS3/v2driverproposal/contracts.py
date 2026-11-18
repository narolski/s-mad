"""VIS3v2 source-only proposal: grant/source contracts and deterministic metadata checks."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

IDS=['42_samephoto','42_crossphoto','56_samephoto','56_crossphoto']
SEAM=[3,4,10,13]
SURROUND=[0,7,56,63]


def need(ok,message):
    if not ok:raise ValueError(message)


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def rawsha(a):return hashlib.sha256(a.tobytes(order='C')).hexdigest()


def syncdir(path):
    fd=os.open(str(Path(path)),os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)


def write(path,data):
    with Path(path).open('x') as f:
        json.dump(data,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    syncdir(Path(path).parent)


def read(path):return json.loads(Path(path).read_text())


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def authority(invpath,releasepath,phase,model=None):
    """No source-image/model bytes opened: all real payload access is downstream."""
    need(sys.flags.isolated,'python -I required')
    inv=read(invpath);grant=read(releasepath)
    need(inv['experiment']=='VIS3_CONTROLLED_SOFT_SPLICE_V2','wrong inventory')
    need(grant['issued_by']=='root' and grant['phase']==phase,'new exact ROOT phase grant required')
    expected='GO_VIS3_PRIVATE_CPU_CONSTRUCTION' if phase=='construct' else 'GO_VIS3_PRIVATE_NUMERIC_'+phase.upper()
    need(grant['decision']==expected,'incorrect phase release')
    need(grant['author']!=grant['reviewer'] and bool(grant['reviewer']),'OTHER source review required')
    need(sha(grant['independent_review_path'])==grant['independent_review_sha256'],'source review changed')
    need(grant['inventory_sha256']==sha(invpath),'inventory changed')
    need(grant['prereg_sha256']==sha(inv['prereg_path']),'frozen prereg changed')
    need(grant['private_noncommercial_only'] is True and grant['publication_allowed'] is False and grant['render_allowed'] is False,'scope broadened')
    need(grant['source_pixel_export_allowed'] is (phase=='construct'),'wrong pixel-export scope')
    if model is not None:need(model in grant['models'],'model not released')
    sums=Path(__file__).with_name('SHA256SUMS')
    need(sha(sums)==grant['source_manifest_sha256'],'source manifest changed')
    for line in sums.read_text().splitlines():
        h,n=line.split('  ',1);p=(sums.parent/n).resolve()
        need(p.is_relative_to(sums.parent.resolve()) and sha(p)==h,'source changed')
    for item in inv['source_pins']:
        need(sha(item['path'])==item['sha256'],'source/evidence changed: '+item['path'])
    repo=Path(inv['repository']).resolve();release=Path(releasepath).resolve()
    need(release.is_relative_to(repo),'release must be committed in repository')
    owned=inv['owned_paths'];need(owned and len(owned)==len(set(owned)),'bad owned paths')
    for rel in owned:
        need(not Path(rel).is_absolute() and '..' not in Path(rel).parts,'unsafe source path')
        raw=subprocess.check_output(['git','show',grant['source_commit']+':'+rel],cwd=repo)
        need(hashlib.sha256(raw).hexdigest()==sha(repo/rel),'committed source mismatch')
    r=str(release.relative_to(repo))
    subprocess.run(['git','ls-files','--error-unmatch','--',*owned,r],cwd=repo,check=True,capture_output=True)
    need(not subprocess.check_output(['git','status','--porcelain','--',*owned,r],cwd=repo,text=True),'source/release not clean')
    return inv,grant


def geometry(alpha,module):
    plan=module.region_plan(alpha)
    need(rawsha(alpha)=='4b38529ef70b6f72836e1bfee50a4649a63096897450636146c2e1fb092ed57c','alpha differs from registered generated audit')
    need(str(alpha.dtype)=='float32' and list(alpha.shape)==[512,512,1],'alpha schema changed')
    need(plan['seam_candidates']==[3,4,10,13,17,22,25,30,33,38,41,46,50,53,59,60,61] and plan['surround_candidates']==SURROUND,'candidate sets changed')
    need(plan['K']==4 and plan['selected_seam']==SEAM and plan['selected_surround']==SURROUND and plan['area_per_patch']==4096,'selected controls changed')
    return plan


def tasks(phase):
    need(phase in ('smoke','full'),'wrong numeric phase')
    cells=[0,7,27,36,56,63] if phase=='smoke' else list(range(64))
    return [(fill,j) for fill in (0,128) for j in cells]


def regional_means(rows,phase):
    """Mean of separate SINGLE-patch interventions; not simultaneous region removal."""
    result=[]
    for ident in IDS:
        for fill in (0,128):
            part=[r for r in rows if r['input_id']==ident and r['fill_uint8']==fill]
            index={r['cell']:r for r in part}
            expected=[j for f,j in tasks(phase) if f==fill]
            need(len(index)==len(part)==len(expected) and set(index)==set(expected),'missing/duplicate/unregistered task')
            if phase=='full':
                result.append({'input_id':ident,'fill_uint8':fill,
                               'boundary_cells':SEAM,'surround_cells':SURROUND,
                               'mean_boundary_delta_z':sum(index[j]['delta_logit'] for j in SEAM)/4,
                               'mean_surround_delta_z':sum(index[j]['delta_logit'] for j in SURROUND)/4,
                               'estimand':'arithmetic mean of four separate single4096pixel-patch intervention deltas; not simultaneous16384pixel masking'})
    return result
