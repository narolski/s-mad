"""CPU source/metadata-only preparation; never loads torch/models/score arrays."""
from pathlib import Path
import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
import platform
import sys

REPO = Path('/home/narolski/smad-next')
DEST = REPO / 'experiments/VIS1_shortcut_examples_20261114/v1'
CODE = REPO / 'src/VIS1/v1'


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''):h.update(b)
    return h.hexdigest()


def pin(p):return {'path':str(p),'sha256':sha(p)}
def load(p):return json.loads(Path(p).read_text())
def write(p,obj):
    with p.open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')


def main():
    assert sys.flags.isolated
    DEST.mkdir(parents=True,exist_ok=False)
    oldpath=REPO/'experiments/AGENTIC_delivery_20261114/XAI_INVENTORY_20261114_FP32.json'
    assert sha(oldpath)=='b6874f51611854383946dc5afe4e333edc4e42913251fa2a3f13e8b8f972cb29'
    old=load(oldpath)
    for row in old['sources']:
        assert sha(row['path'])==row['sha256'],row['path']
    root=Path('/mnt/t7/smad_heldout/ffhq_morphs')
    manifest_path=root/'manifests/ffhqm.csv'; meta_path=root/'manifests/ffhqm_meta.csv'
    rows=list(csv.DictReader(manifest_path.open())); metas=list(csv.DictReader(meta_path.open()))
    attrs=list(csv.DictReader((root/'licence/attribution_ffhq_images.csv').open()))
    inputs=[dict(old['inputs'][0],id='reference_00010',role='existing admitted XAI numeric reproduction control')]
    details=[]
    for key in ['00042','00056']:
        match=[x for x in attrs if x['role']=='bona_fide' and x['ffhq_key']==key]
        assert len(match)==1 and match[0]['license_url']=='https://creativecommons.org/licenses/by-nc/2.0/'
        for variant,tag in [('orig','native'),('resmatch_landmark_complete','history')]:
            p=root/'eval/ffhqm/ffhq_bona'/f'{key}_{variant}.png'
            found=[x for x in rows if x['path']==str(p.relative_to(root))]
            assert len(found)==1 and found[0]['label']=='0'
            row=found[0];metadata=[x for x in metas if x['id']==row['id']];assert len(metadata)==1
            inputs.append(dict(pin(p),id=key+'_'+tag,photo_key=key,condition=tag,manifest_id=row['id']))
            details.append(dict(input=inputs[-1],manifest=row,construction_metadata=metadata[0],attribution=match[0]))
    assert len(inputs)==5 and len({x['id'] for x in inputs})==5
    train=[]
    for arm in ['A','B']:
        p=Path('/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests')/('train_'+arm+'.csv')
        tr=list(csv.DictReader(p.open()))
        exact=[x for x in tr if x['path'] in {a['path'] for a in inputs} or any('/ffhq_bona/'+k+'_' in x['path'] for k in ['00042','00056'])]
        train.append(dict(pin(p),arm=arm,rows=len(tr),manifest_db_values=sorted({x.get('db','') for x in tr}),exact_path_or_explicit_FFHQ_key_matches=exact))
        assert not exact
    score_csv=REPO/'manuscript_cvpr2027/figures/shortcut_attribution_20261114/per_image_scores.csv'
    text=score_csv.read_text();assert '00042' not in text and '00056' not in text
    overlap={'exact_path_key_check':train,'full_training_image_hash_overlap':'NOT_VERIFIED; no full training-image reread performed',
             'person_overlap':'UNKNOWN; FFHQ keys are photograph IDs, not person IDs; no synthetic identity labels',
             'component_overlap':'UNKNOWN across FFHQ/SMDD/FERET/FRGC; no inherited independent-component claim',
             'SelfMAD_original_training_overlap':'UNKNOWN beyond release recipe record; not independently auditable here',
             'permitted_interpretation':'Potentially exposed descriptive development examples, not held-out test or benchmark evidence'}
    age={'00042':{'method':'manual visual description of original aligned photo','description':'adult-appearing person with full beard and glasses; no numeric age metadata or documentary adulthood verification'},
         '00056':{'method':'manual visual description of original aligned photo','description':'adult-appearing person with short hair and facial stubble; no numeric age metadata or documentary adulthood verification'},
         'publication_clearance':'PENDING separately; apparent age is not consent or identity verification'}
    audit={'at':datetime.now(timezone.utc).isoformat(),'preparation':'CPU metadata/source only; no torch/model/score-array imports',
           'scope':'proposed new private descriptive image response; NOT inherited XAI execution authority',
           'inputs':details,'age_review':age,'overlap':overlap,
           'existing_score_search':{'checked':pin(score_csv),'result':'No00042/00056 response in this specifically admitted XAI CSV; global absence not asserted; other scientific arrays not opened'},
           'rights':'CC BY-NC2.0 per-image attribution plus dataset BY-NC-SA4.0. Private noncommercial research is proposed; require root exact release. Publication/privacy disposition pending.',
           'threshold':None,'operations':'Existing PNG bytes only; history is E7 INTER_AREA shrink then alignment, not isolated JPEG/blur. No new image construction.'}
    audit_path=DEST/'INPUT_AUDIT.json';write(audit_path,audit)
    prior=REPO/'manuscript_cvpr2027/figures/shortcut_attribution_20261114'
    ref={};source=list(old['sources'])
    for model,folder in [('selfmad_hrnet_w18','selfmad_hrnet_w18_fp32'),('A','A_fp32'),('B','B_fp32')]:
        p=prior/folder/'result.json';j=load(p);ref[model]=next(x['logit_morph'] for x in j['results'] if x['condition']=='native');source.append(pin(p))
    for p in [oldpath,manifest_path,meta_path,root/'licence/attribution_ffhq_images.csv',root/'licence/LICENSE_FFHQ.txt',root/'licence/LICENSE_FFHQ-Morphs.txt',root/'prep_ffhqm.py',audit_path,CODE/'prepare_vis1.py']:
        source.append(pin(p))
    # Exact existing package versions, not recalled model defaults.
    environment={'python':sys.version.split()[0],'python_executable':sys.executable,'python_resolved':os.path.realpath(sys.executable),
                 'machine':platform.machine(),'packages':{x:importlib.metadata.version(x) for x in ['torch','torchvision','timm','numpy','pillow','safetensors']},
                 'gpu':'NVIDIA GB10','cudnn_benchmark':False,'cudnn_deterministic':False,
                 'precision':'float32 noTTA noAMP TF32disabled; explicit benchmark/deterministic=False fixed prospectively'}
    inv={'scope':'VIS1_PRIVATE_DESCRIPTIVE_ONLY','threshold':None,'runner_sha256':sha(CODE/'score_vis1.py'),
         'models_order':['selfmad_hrnet_w18','A','B'],'models':{x:old['models'][x] for x in ['selfmad_hrnet_w18','A','B']},
         'sources':source,'inputs':inputs,'hf_home':old['hf_home'],'environment':environment,'reference_logits':ref,
         'overlap_status':overlap,'output_root':'/mnt/t7/smad_next/VIS1/20261114/v1',
         'execution':'HOLD_REQUIRES_INDEPENDENT_REVIEW_AND_EXACT_ROOT_RELEASE'}
    write(DEST/'INVENTORY.json',inv)
    print(json.dumps({'audit_sha256':sha(audit_path),'inventory_sha256':sha(DEST/'INVENTORY.json'),'inputs':len(inputs),'new_inference':False}))


if __name__=='__main__':main()
