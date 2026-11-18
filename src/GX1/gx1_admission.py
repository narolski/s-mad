"""PROPOSED GX1 admission/manifests, pending pre-run review before image access.

Reuses AG1's unchanged frame alignment and glintr100 oracle helpers. Never calls
AG1 stage_frames (which includes benchmark material), loads a detector candidate,
or reads candidate scores. Main commands must be run only after lead admission.
"""
import argparse
import collections
import csv
import hashlib
import importlib.util
import io
import json
import math
import pathlib
import struct
import sys
import tarfile
import zlib

import numpy as np

ROOT=pathlib.Path(__file__).resolve().parents[2]
BASE=pathlib.Path('/mnt/t7/smad_next/GX1')
INPUT=BASE/'inputs'
SOURCE_PINS={
    str(ROOT/'src/AG1/ag1_manifest.py'):'0effcf883bbfdab3df02b943fa8b41d39b23f497106dc926a3b6f061d7b37107',
    str(ROOT/'src/AG1/build_inputs.py'):'8fad6a50034c006796c3259a7377341b677cc798c69792a5947ac99c7cb14f8e',
    str(INPUT/'pack/photos.json'):'4221e2637fc75c58f51786e68c6ae072b6cc8bc3e7f0542f1e7ceedf9e3a5274',
    str(INPUT/'pairs.csv'):'c5b9c978affd6440dec07fe5c6e740001aafd62f5f143fa47a6a415bc779721f',
    str(BASE.parent/'PN1/manifests2/train_Sb.csv'):'2cf3fda3affc8dd3d1574857f494037ea0382c8a2d314754b615686401b7fa4a',
    str(BASE.parent/'PR1/pr1_gd_tree/pr1g/data/manifests/pr1_gd.csv'):'3577a91351131b104457424054c29ca3c6f3fc59666e9204598e45e608e15157',
    '/home/narolski/mambamorph-code/smadcvpr/prep_eval.py':'374408ab3a886e6df25b563bc2344d190efe2ab7b3163efbb17c9b6ca9100628',
    '/mnt/t7/smad_heldout/arc2face/scripts/a2f_common.py':'d27701dbe187dd6fcc2b50f21e3631a1c1a0678cfdc9d5a6989cd9c355bfcc3c',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def readcsv(path):
    return list(csv.DictReader(path.open()))


def verify_sources():
    for name,expected in SOURCE_PINS.items():assert sha(pathlib.Path(name))==expected,('source pin differs',name)


def immutable_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    text=json.dumps(data,sort_keys=True,indent=2)+'\n'
    if path.exists():assert path.read_text()==text,('immutable receipt differs',path)
    else:path.write_text(text)


def helpers():
    spec=importlib.util.spec_from_file_location('gx1_ag1_helpers',ROOT/'src/AG1/ag1_manifest.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod


def png_check(buf):
    assert buf[:8]==b'\x89PNG\r\n\x1a\n','not PNG'
    pos=8;types=[];header=None
    while pos<len(buf):
        length=struct.unpack('>I',buf[pos:pos+4])[0];kind=buf[pos+4:pos+8]
        payload=buf[pos+8:pos+8+length]
        crc=struct.unpack('>I',buf[pos+8+length:pos+12+length])[0]
        assert zlib.crc32(kind+payload)&0xffffffff==crc,'PNG CRC'
        types.append(kind)
        if kind==b'IHDR':header=struct.unpack('>IIBBBBB',payload)
        pos+=12+length
    assert pos==len(buf) and header==(1024,1024,8,2,0,0,0),('not 1024 RGB8 PNG',header)
    assert types[0]==b'IHDR' and types[-1]==b'IEND' and all(k==b'IDAT' for k in types[1:-1])


def get(tf,name):
    member=tf.getmember(name)
    assert member.isfile() and member.size>0,('not a regular member',name)
    return tf.extractfile(member).read()


def process_shard(tar,data):
    """After review: verify one generation tar, align stored frames, measure oracle."""
    import cv2
    stem=tar.stem
    assert stem.startswith('GX1_') and 'smoke' not in stem
    planfile=INPUT/'shards'/f'{stem}.json';plan=json.loads(planfile.read_text())
    assert not plan.get('smoke') and plan['group'] in ('train','dev')
    expected=pathlib.Path(str(tar)+'.sha256').read_text().split()[0]
    assert sha(tar)==expected,'generation archive hash differs'
    output=data/'shards'/f'{stem}.json'
    assert not output.exists(),'existing shard receipt: verify it explicitly instead of rerunning'
    AM=helpers();PE=AM.detector();records=[];crops=[];ids=[];invhash={}
    planned={r['stem']:r for r in plan['jobs']}
    with tarfile.open(tar) as tf:
        meta=json.loads(get(tf,f'{stem}/meta.json'))
        assert 'H100' in meta['device'] and meta['torch']=='2.11.0+cu128'
        assert meta['shard_sha256']==sha(planfile)
        assert meta['script_sha256']==sha(ROOT/'src/AG1/ag1_gen.py')
        logs=list(csv.DictReader(io.StringIO(get(tf,f'{stem}/log.csv').decode())))
        assert len(logs)==len(planned) and {r['stem'] for r in logs}==set(planned)
        for row in logs:
            job=planned[row['stem']]
            assert all(row[k]==job[k] for k in ('rung','a','b','gen'))
            assert math.isfinite(float(row['loss'])) and float(row['alpha'])==job['alpha']
            buf=get(tf,f"{stem}/png/{row['stem']}.png")
            assert hashlib.sha256(buf).hexdigest()==row['png_sha256']
            png_check(buf)
            latent=np.load(io.BytesIO(get(tf,f"{stem}/lat/{row['stem']}.npz")),allow_pickle=False)
            assert latent.files==['w'] and np.isfinite(latent['w']).all()
            image=cv2.imdecode(np.frombuffer(buf,np.uint8),cv2.IMREAD_COLOR)
            assert image is not None and image.shape==(1024,1024,3)
            rel=pathlib.Path('train' if plan['group']=='train' else 'eval')/'gx1'/row['rung']/f"{row['stem']}.png"
            assert not (data/rel).exists(),'refuse overwriting a frame'
            aligned=AM.write_frame(PE,image,data/rel)
            crop=AM.oracle_crop(PE,image)
            if crop is not None:crops.append(crop);ids.append(row['stem'])
            records.append(dict(id=row['stem'],path=str(rel),gen=row['gen'],rung=row['rung'],group=plan['group'],
                db=plan['db'],photo_a=row['a'],photo_b=row['b'],aligned=aligned,
                raw_sha256=row['png_sha256'],frame_sha256=sha(data/rel),loss=float(row['loss'])))
        if plan['gen']=='mip1':
            for photo in plan['invert']:
                w=np.load(io.BytesIO(get(tf,f'{stem}/lat/inv_{photo}.npz')),allow_pickle=False)['w']
                assert np.isfinite(w).all()
                invhash[photo]=hashlib.sha256(w.dtype.str.encode()+str(w.shape).encode()+w.tobytes()).hexdigest()
    embedding=AM.embed(crops) if crops else np.empty((0,512),np.float32)
    assert np.isfinite(embedding).all()
    oracle=data/'shards'/f'{stem}_oracle.npz';oracle.parent.mkdir(parents=True,exist_ok=True)
    assert not oracle.exists();np.savez(oracle,id=np.array(ids),emb=embedding)
    immutable_json(output,{'source_tar':str(tar),'source_sha256':expected,'plan_sha256':sha(planfile),
        'procedure_sha256':sha(pathlib.Path(__file__)),'helper_sha256':sha(ROOT/'src/AG1/ag1_manifest.py'),
        'rows':records,'oracle_sha256':sha(oracle),'inversion_value_hashes':invhash})


def camera(data):
    """After review: same original camera route as AG1; GX persons only."""
    AM=helpers();PE=AM.detector()
    photos=json.loads((INPUT/'pack/photos.json').read_text())
    selected={r['person']:r for r in json.loads((INPUT/'select.json').read_text())}
    assert {r['db'] for r in selected.values()}=={'feret','frgc'}
    rows=[];crops=[];ids=[]
    for ph,meta in sorted(photos.items()):
        assert meta['person'] in selected and meta['slot'] in ('s1','s2')
        assert sha(pathlib.Path(meta['src']))==meta['src_sha256']
        image=AM.BI.read_bgr(meta['src'])
        crop=AM.oracle_crop(PE,image)
        assert crop is not None,('missing source oracle crop',ph)
        crops.append(crop);ids.append(ph)
        group=selected[meta['person']]['group']
        if group=='dev':
            rel=pathlib.Path('eval/gx1/R0')/f'R0__{ph}.png'
            assert not (data/rel).exists()
            aligned=AM.write_frame(PE,image,data/rel)
            rows.append(dict(id='R0__'+ph,path=str(rel),gen='camera',rung='R0',group=group,
                db=meta['db'],photo_a=ph,photo_b=ph,aligned=aligned,frame_sha256=sha(data/rel)))
    path=data/'camera_oracle.npz';path.parent.mkdir(parents=True,exist_ok=True)
    embedding=AM.embed(crops);assert np.isfinite(embedding).all()
    assert not path.exists();np.savez(path,id=np.array(ids),emb=embedding)
    immutable_json(data/'camera.json',{'photos_sha256':sha(INPUT/'pack/photos.json'),
        'procedure_sha256':sha(pathlib.Path(__file__)),'helper_sha256':sha(ROOT/'src/AG1/ag1_manifest.py'),
        'oracle_sha256':sha(path),'rows':rows})


def gate_records(records,embeddings,source_embeddings,photos,selected):
    """Pure function: binding groups are literal train/dev, as in shard schema."""
    reports={};accepted=[];dropped=[]
    for gen in sorted({r['gen'] for r in records}):
        for group in ('train','dev'):
            rows=[r for r in records if r['gen']==gen and r['group']==group]
            if not rows:continue
            phs=sorted(p for p,m in photos.items() if selected[m['person']]['group']==group)
            assert all(ph in source_embeddings for ph in phs)
            E=np.stack([source_embeddings[ph] for ph in phs]);iu=np.triu_indices(len(phs),1)
            mask=np.array([photos[phs[a]]['person']!=photos[phs[b]]['person'] for a,b in zip(*iu)])
            assert mask.any();threshold=float(np.quantile((E@E.T)[iu][mask],.999))
            aligned_rate={rung:float(np.mean([bool(r['aligned']) for r in rows if r['rung']==rung]))
                          for rung in ('R2','R3','R4')}
            by={rung:[r for r in rows if r['rung']==rung] for rung in ('R2','R3','R4')}
            def verifies(r,both):
                if r['id'] not in embeddings:return False
                a=float(embeddings[r['id']]@source_embeddings[r['photo_a']])
                b=float(embeddings[r['id']]@source_embeddings[r['photo_b']])
                return min(a,b)>=threshold if both else a>=threshold
            rates={'R4_verifies_both':float(np.mean([verifies(r,True) for r in by['R4']])),
                   'R3_verifies_own':float(np.mean([verifies(r,False) for r in by['R3']]))}
            passed={'R2':aligned_rate['R2']>=.95,
                    'R3':aligned_rate['R3']>=.95 and rates['R3_verifies_own']>=.90,
                    'R4':aligned_rate['R4']>=.95 and rates['R4_verifies_both']>=.70}
            diagnostic=collections.Counter((r['db'],photos[r['photo_a']]['gender'],r['rung']) for r in rows)
            reports[f'{gen}/{group}']={'threshold_fmr1e3':threshold,'aligned_rate':aligned_rate,
                **rates,'rung_admitted':passed,'raw_n':{k:len(v) for k,v in by.items()},
                'db_gender_rung_counts':{'/'.join(k):v for k,v in diagnostic.items()}}
            for r in rows:
                if r['aligned'] and passed[r['rung']]:accepted.append(r)
                else:dropped.append(dict(id=r['id'],reason='alignment flag or registered group/rung gate'))
    return reports,accepted,dropped


def finalize(data):
    photos=json.loads((INPUT/'pack/photos.json').read_text())
    selected={r['person']:r for r in json.loads((INPUT/'select.json').read_text())}
    planfiles=[p for p in (INPUT/'shards').glob('GX1_mip1_*.json') if not json.loads(p.read_text()).get('smoke')]
    assert len(planfiles)==12
    assert all((data/'shards'/p.name).exists() for p in planfiles),'every mandatory mip1 shard required'
    camera_meta=json.loads((data/'camera.json').read_text())
    assert camera_meta['photos_sha256']==sha(INPUT/'pack/photos.json')
    assert camera_meta['procedure_sha256']==sha(pathlib.Path(__file__))
    assert camera_meta['helper_sha256']==sha(ROOT/'src/AG1/ag1_manifest.py')
    assert camera_meta['oracle_sha256']==sha(data/'camera_oracle.npz')
    cz=np.load(data/'camera_oracle.npz',allow_pickle=False)
    source=dict(zip(cz['id'].tolist(),cz['emb']))
    records=[];emb={};provenance={};inversions=collections.defaultdict(list)
    for path in sorted((data/'shards').glob('GX1_*.json')):
        receipt=json.loads(path.read_text());oracle=path.with_name(path.stem+'_oracle.npz')
        assert receipt['procedure_sha256']==sha(pathlib.Path(__file__))
        assert receipt['helper_sha256']==sha(ROOT/'src/AG1/ag1_manifest.py')
        assert receipt['plan_sha256']==sha(INPUT/'shards'/path.name)
        assert receipt['oracle_sha256']==sha(oracle)
        z=np.load(oracle,allow_pickle=False);emb.update(zip(z['id'].tolist(),z['emb']))
        for r in receipt['rows']:
            assert sha(data/r['path'])==r['frame_sha256']
            records.append(r)
        for photo,h in receipt['inversion_value_hashes'].items():inversions[photo].append((path.stem,h))
        provenance[str(path)]=sha(path)
    assert len({r['id'] for r in records})==len(records)
    reports,accepted,dropped=gate_records(records,emb,source,photos,selected)
    admitted={r['id']:r for r in accepted};pairrows=readcsv(INPUT/'pairs.csv')
    appended=[];positive=[];matched_drops=[]
    for pair in pairrows:
        if pair['group']!='train':continue
        ident=f"gx1_mip1_R4c{pair['cover']}_{pair['person']}"
        neg=f"gx1_mip1_R2_{pair['person']}__s1" if pair['cover']=='0' else f"gx1_mip1_R3_{pair['person']}"
        if ident not in admitted or neg not in admitted:
            matched_drops.append({'positive':ident,'negative':neg});continue
        for name,label,kind in [(ident,1,'gx_R4'),(neg,0,'gx_R2' if pair['cover']=='0' else 'gx_R3')]:
            row=admitted[name]
            item=dict(path=row['path'],label=str(label),source='smdd',tool='mip1',arm='GX',val='0',mixed='0',
                      id=name,kind=kind,db=row['db'],hist='native')
            appended.append(item)
            if label:positive.append(dict(item,arm='GXp'))
    assert len(appended)==2*len(positive) and len(positive)>0,'no balanced admitted GX data'
    basepath=BASE.parent/'PN1/manifests2/train_Sb.csv';base=basepath.read_bytes();baserows=readcsv(basepath)
    fields=list(baserows[0]);assert len(baserows)==8386 and base.endswith(b'\n')
    target=data/'manifests';target.mkdir(parents=True,exist_ok=True)
    for arm,extra in [('GX',appended),('GXp',positive)]:
        text=io.StringIO(newline='');writer=csv.DictWriter(text,fieldnames=fields);writer.writerows(extra)
        p=target/f'train_{arm}.csv';assert not p.exists();p.write_bytes(base+text.getvalue().encode())
        assert p.read_bytes().startswith(base),'Sb prefix must remain byte-identical'
    eval_fields=['id','path','label','klass','role','fam','rung','strength','tool','cell','host','neutral']
    ev=[]
    for r in accepted+camera_meta['rows']:
        if r['group']!='dev' or not r['aligned']:continue
        host=photos[r['photo_a']]['person']
        ev.append(dict(id=r['id'],path=r['path'],label='1' if r['rung'] in ('R3','R4') else '0',
            klass='morph' if r['rung'] in ('R3','R4') else 'genuine',role='dev',fam='gx1',rung=r['rung'],
            strength='',tool=r['gen'],cell=r['gen'],host=host,neutral=''))
    gd=BASE.parent/'PR1/pr1_gd_tree/pr1g/data/manifests/pr1_gd.csv'
    for r in readcsv(gd):
        ev.append({k:r.get(k,{'klass':'morph' if r['label']=='1' else 'genuine','role':'dev'}.get(k,'')) for k in eval_fields})
    assert len({r['id'] for r in ev})==len(ev),'duplicate GX/GD eval IDs'
    efile=target/'gx1_eval.csv';assert not efile.exists()
    with efile.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=eval_fields);writer.writeheader();writer.writerows(ev)
    paths={r['path'] for r in accepted+camera_meta['rows']}
    pins='\n'.join(f'{sha(data/p)}  {p}' for p in sorted(paths))+'\n'
    pinfile=data/'pins_images.sha256';assert not pinfile.exists();pinfile.write_text(pins)
    boundaries={ph:values for ph,values in inversions.items() if len(values)>1}
    boundary=next(iter(sorted(boundaries)),None)
    boundary_result=None if boundary is None else {'photo':boundary,'shards':boundaries[boundary],
        'byte_identical_latent_values':len({v for _,v in boundaries[boundary]})==1}
    immutable_json(data/'admission.json',{'scope':'Image/admission and manifests, not model fitting',
        'gate_group_definition':'literal shard group train/dev, separately by generator',
        'procedure_sha256':sha(pathlib.Path(__file__)),'sources':provenance,'gates':reports,
        'matched_pair_drops':matched_drops,'dropped_rows':dropped,'training_extra_rows':len(appended),
        'training_counts':{'GX':8386+len(appended),'GXp':8386+len(positive)},
        'Sb_prefix_sha256':sha(basepath),'gd_manifest_sha256':sha(gd),'inversion_boundary_check':boundary_result,
        'manifest_pins':{p.name:sha(p) for p in target.glob('*.csv')},'images_pin_sha256':sha(pinfile),
        'training_ready':False,'remaining':['prefit cue floor','amendment2 final pins and pre-run review',
            'full-path training smoke','NEXT per-row transfer learner and eligibility/score pins']})


if __name__=='__main__':
    assert sys.flags.isolated,'run with python -I'
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('stage',choices=['shard','camera','finalize'])
    ap.add_argument('--data',type=pathlib.Path,required=True)
    ap.add_argument('--tar',type=pathlib.Path)
    args=ap.parse_args()
    verify_sources()
    if args.stage=='shard':assert args.tar is not None;process_shard(args.tar,args.data)
    elif args.stage=='camera':camera(args.data)
    else:finalize(args.data)
