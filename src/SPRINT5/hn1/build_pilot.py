"""Direct target-matched one-warp composites [SPRINT5-2]; preparation/pilot only."""
import argparse
import csv
import hashlib
import importlib.util
import json
import pathlib
import shutil
import time

REPO=pathlib.Path('/home/narolski/smad-next')
POOL=pathlib.Path('/mnt/t7/smad_next/AR1/pool.csv')
SPLIT=REPO/'experiments/PN1_protocol-network-first-tests/split/ladder_split.csv'
KERNEL=pathlib.Path('/home/narolski/mambamorph-code/scripts/68_hires_morph.py')
PINS={str(POOL):'861019781e79159fe7904eb60e8cda6a57e978023722615dd46023db2f299352',
 str(SPLIT):'2299ac2b1f3a8a4798fe1730ab8722780933ba956d4b38080fdeeb730b391ec3',
 str(KERNEL):'71643aad7deaabbead698367342434242ec6955fc654c4d19a8f504b41f96d7a'}


def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def tem(p):
    import numpy as np
    lines=pathlib.Path(p).with_suffix('.tem').read_text().splitlines()
    n=int(lines[0]); pts=np.array([list(map(float,x.split())) for x in lines[1:n+1]],dtype=np.float32)
    assert pts.shape==(106,2) and np.isfinite(pts).all()
    return pts


def geometry(lh,lb,h,w):
    import cv2
    import numpy as np
    corners=np.float32([[0,0],[w//2,0],[w-1,0],[0,h//2],[w-1,h//2],[0,h-1],[w//2,h-1],[w-1,h-1]])
    target=(np.vstack([lh,corners])+np.vstack([lb,corners]))/2
    assert np.isfinite(target).all()
    assert ((target[:,0]>=0)&(target[:,0]<=w-1)&(target[:,1]>=0)&(target[:,1]<=h-1)).all(),'raw target outside frame'
    assert len(np.unique(target,axis=0))==len(target),'duplicate destination vertices'
    sub=cv2.Subdiv2D((0,0,w,h))
    for p in target:sub.insert((float(p[0]),float(p[1])))
    triangles=[]
    for tri in sub.getTriangleList():
        points=np.array(tri).reshape(3,2)
        ids=[int(np.argmin(np.sum((target-p)**2,axis=1))) for p in points]
        assert len(set(ids))==3,'degenerate vertex mapping'
        assert max(float(np.linalg.norm(target[i]-p)) for i,p in zip(ids,points))<=1e-3,'unmapped triangulation vertex'
        aa,bb,cc=target[ids]
        area=float((bb[0]-aa[0])*(cc[1]-aa[1])-(bb[1]-aa[1])*(cc[0]-aa[0]))
        assert abs(area)>1e-6,'zero-area triangle'
        triangles.append(ids)
    assert triangles,'empty triangulation'
    return target,triangles,corners


def warp(image,landmarks,target,triangles,corners,kernel):
    import numpy as np
    source=np.vstack([landmarks,corners])
    out=np.zeros_like(image,dtype=np.float32)
    src=image.astype(np.float32)
    # Exact existing triangle kernel; only the cached explicit destination is new.
    for ids in triangles:
        kernel._warp_tri(src,out,[source[i] for i in ids],[target[i] for i in ids])
    return np.clip(out,0,255).astype(np.uint8)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=pathlib.Path,required=True)
    ap.add_argument('--build-smoke','--build',dest='build_smoke',action='store_true')
    ap.add_argument('--count',type=int,choices=(8,124),default=8)
    a=ap.parse_args()
    assert all(sha(p)==h for p,h in PINS.items()),'source/input pin mismatch'
    if a.build_smoke:assert shutil.disk_usage('/mnt/t7').free>=50*(1<<30),'T7 free-space reserve'
    assert not a.out.exists(),'never overwrite prior pilot/output'
    a.out.mkdir(parents=True)
    split={r['pid']:r for r in csv.DictReader(SPLIT.open())}
    pool={r['pid']:r for r in csv.DictReader(POOL.open())}
    eligible=[h for h,r in split.items() if r['role']=='train' and split[r['partner_B']]['role']=='train']
    excluded=[h for h,r in split.items() if r['role']=='train' and split[r['partner_B']]['role']!='train']
    assert len(eligible)==124 and len(excluded)==32
    metadata={'label':'MAD22-informed separate-cycle geometry pilot; no detector fit',
      'source_pins':{str(p):sha(p) for p in (POOL,SPLIT,KERNEL)},'builder_sha256':sha(__file__),
      'eligible_train_hosts':sorted(eligible),'excluded_train_hosts':sorted(excluded),
      'pilot_hosts':sorted(eligible)[:a.count],
      'construction_scope':('eight_pair_smoke' if a.count==8 else 'all124TRAIN_floor_construction_only'),
      'dev_partner_roles':{k:sum(r['role']=='dev' and split[r['partner_B']]['role']==k for r in split.values()) for k in ('train','dev','test','excluded')},
      'build':'NOT_REQUESTED','fits':'HELD_FOR_FLOOR_PILOT_AND_REGISTRATION'}
    (a.out/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    if not a.build_smoke:
        print(json.dumps({'eligible':len(eligible),'excluded':len(excluded),'status':'METADATA_ONLY'}));return
    import cv2
    import numpy as np
    spec=importlib.util.spec_from_file_location('hn_triangle_kernel',KERNEL)
    kernel=importlib.util.module_from_spec(spec);spec.loader.exec_module(kernel)
    results=[]
    for host in metadata['pilot_hosts']:
        r=pool[host];assert r['B_pid']==split[host]['partner_B']
        t=time.monotonic();record={'host':host,'partner':r['B_pid'],'source':r['db']}
        try:
            files=[pathlib.Path(r[k]) for k in ('H','S','B')]
            donor=pool[r['B_pid']]
            assert files[2].resolve()==pathlib.Path(donor['S']).resolve(),'B must be pinned partner second capture S'
            assert files[2].parent.name==donor['subject'] and files[2].parent.parent.name==donor['db']
            record['B_provenance']={'identity':r['B_pid'],'pool_capture':'S','raw':donor['S_raw'],
                                    'session':donor['S_session'],'role':split[r['B_pid']]['role']}
            assert all(not any(x in str(p).lower() for x in ('frll','mordiff','mad22','valx','fst','a12sp')) for p in files)
            images=[cv2.imread(str(p)) for p in files]
            assert all(x is not None and x.shape==images[0].shape for x in images)
            lms=[tem(p) for p in files]
            h,w=images[0].shape[:2]
            target,tris,corners=geometry(lms[0],lms[2],h,w)
            layers=[warp(x,l,target,tris,corners,kernel) for x,l in zip(images,lms)]
            wh,ws,wb=layers
            positive=np.clip(.5*wh.astype(np.float32)+.5*wb.astype(np.float32),0,255).astype(np.uint8)
            negative=np.clip(.5*wh.astype(np.float32)+.5*ws.astype(np.float32),0,255).astype(np.uint8)
            d=a.out/host.replace(':','_');d.mkdir()
            outputs={}
            for role,img in zip(('P','N','WH','WS','WB'),(positive,negative,wh,ws,wb)):
                p=d/(role+'.png');assert cv2.imwrite(str(p),img)
                assert np.array_equal(cv2.imread(str(p)),img)
                outputs[role]={'path':str(p),'sha256':sha(p),'pixel_sha256':hashlib.sha256(img.tobytes()).hexdigest()}
            record.update(status='BUILT',input_pins={str(p):sha(p) for p in files+ [p.with_suffix('.tem') for p in files]},
              target_sha256=hashlib.sha256(target.tobytes()).hexdigest(),triangle_sha256=hashlib.sha256(json.dumps(tris).encode()).hexdigest(),
              shared_host_layer_sha256=outputs['WH']['pixel_sha256'],warps_per_layer=1,outputs=outputs)
        except Exception as e:
            record.update(status='FAILED_PAIR',error=repr(e))
        record['seconds']=time.monotonic()-t;results.append(record)
        (a.out/'pilot.json').write_text(json.dumps(results,indent=2)+'\n')
    assert all(r['status']=='BUILT' for r in results),'pilot failed; no full build/fit'
    print(json.dumps({'pairs':len(results),'seconds':sum(r['seconds'] for r in results),'status':'GEOMETRY_PILOT_ONLY'}))


if __name__=='__main__':main()
