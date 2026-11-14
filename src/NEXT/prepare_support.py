"""Pin criterion (b)-(f) metadata without candidate/result/image access.

Uses only development manifests and previously reviewed reader definitions.
MEDS is exported as manifest row indices and order-preserving opaque person
groups: no original MEDS image or subject identifier is put in the package.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT/'experiments/NEXT_method-selection-rule/inputs/support'
T7 = pathlib.Path('/mnt/t7/smad_next')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    data=list(csv.DictReader(path.open()))
    assert data and not {'logit','score','probability'}.intersection(data[0]), 'manifest required, not scores'
    return data


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def prepare():
    rz=module('next_rz_metadata',ROOT/'src/RZ1/rz1_read.py')
    source_paths=[
        ROOT/'src/RZ1/rz1_read.py', ROOT/'src/RZ1/rz1_score.py',
        ROOT/'src/AB1/ab1_read.py',ROOT/'src/PN1/c2p_read.py',
        ROOT/'src/TT1/tt1_read.py',ROOT/'src/TT1/tt1common.py',
        ROOT/'src/TT1/meds/tt1_read_meds.py',
        ROOT/'experiments/RZ1_input-resolution-and-resize/prereg.md',
        ROOT/'experiments/NEXT_method-selection-rule/prereg_draft_v3.md',
        rz.X_EVAL, rz.CROSS, rz.T.OUT/'tt1_score.csv',
        rz.T.OUT/'raw_manifest.csv',rz.T.OUT/'aligned_manifest.csv',
        rz.MR.MEDS,rz.T.OUT/'meds/meds_score.csv',
        rz.FSMAN/'train_A.csv',rz.FSMAN/'train_Sb.csv',
    ]
    sources={str(p):sha(p) for p in source_paths}
    assert sha(rz.X_EVAL)==rz.X_EVAL_SHA
    assert sha(rz.CROSS)==rz.CROSS_SHA
    assert sha(rz.T.OUT/'tt1_score.csv')==rz.TT1_SHA
    assert sha(rz.MR.MEDS)=='3698bcb4ff9e694219a0d1675920621724303eee034692f9374f70400fec6c8d'
    assert sha(ROOT/'src/PN1/c2p_read.py')==rz.A.C2P_SHA
    manifest=rows(rz.X_EVAL)
    p=rz.A.pools([r for r in manifest if r['fam']!='border'])
    native_photo,native_morph,photo_pairs,morph_pairs=rz.C2.holdout(manifest)
    pools,_=rz.TR.load_pools()
    tt_families={family:[i for source in ([family] if family!='lfw_calfw' else ['lfw','calfw'])
                            for i,_ in pools[f'U:{source}']] for family in rz.T.FAMILIES}
    assert len(tt_families)==7 and all(tt_families.values())
    ttrows=rows(rz.T.OUT/'tt1_score.csv')
    assert all(set(ids)<={r['id'] for r in ttrows} for ids in tt_families.values())
    meds=rows(rz.MR.MEDS)
    meds_score=rows(rz.T.OUT/'meds/meds_score.csv')
    # Full manifests have identical order, as used by rz1_score.py scores_meds.
    assert [r['id'] for r in meds] == [r['id'] for r in meds_score]
    primary=[(i,r) for i,r in enumerate(meds) if r['aligned']=='1']
    persons=sorted({r['person'] for _,r in primary})
    groups={person:f'p{i:06d}' for i,person in enumerate(persons)}
    primary_export=[{'row_index':i,'person':groups[r['person']]} for i,r in primary]
    assert len(primary_export)==865 and len(persons)==400
    assert [groups[k] for k in persons]==sorted(groups.values())
    assert all(meds_score[i]['cell']=='primary' for i,_ in primary)

    cross=rows(rz.CROSS);crossmap={r['id']:r for r in cross}
    genuine=[f'ab1x:{i}' for i in p['camera']+native_photo]
    genuine += [i for i,r in crossmap.items() if r['src']=='tt1' and
                (r['rung']=='R_cam' or (r['role']=='tt1' and r['rung'] in rz.T.SOURCES))]
    genuine=[i for i in genuine if i in crossmap]
    morph=[f'ab1x:{i}' for i in p['lc_m']]
    assert set(genuine)|set(morph)<=set(crossmap)
    border=[r['id'] for r in manifest if r['fam']=='border' and r['rung']=='R_cam_border']
    assert len(border)==1582 and len(p['S3'])==100
    support={
        'schema':'next-support-v1','sources':sources,
        'eval_sha256':sha(rz.X_EVAL),'tt1_sha256':sha(rz.T.OUT/'tt1_score.csv'),
        'cross_sha256':sha(rz.CROSS),
        'train':{name:{'sha256':sha(rz.FSMAN/file),'n_items':len(rows(rz.FSMAN/file))}
                 for name,file in [('A0','train_A.csv'),('Sb0','train_Sb.csv')]},
        'storage':{'native_photo_ids':native_photo,'native_morph_ids':native_morph,
            'pairs':{z:[{'native':i,'stored':f'{i}_{z}'} for i in photo_pairs[z]] for z in rz.C2.SIZES},
            'morph_pairs':{z:[{'native':i,'stored':f'{i}_{z}'} for i in morph_pairs[z]] for z in rz.C2.SIZES},
            'plain_control':{'minimum_d_flag_inclusive':.05,'minimum_d_mean_sd_exclusive':0},
            'H_new_1_falsified':{'d_mean_att_sd_minimum_inclusive':-.10,'minimum_seeds':4,'every_storage_size':True},
            'native_scale':'sample SD (ddof=1) of native photo logits',
            'bootstrap':{'n':rz.C2.B_BOOT,'photo_seed':rz.C2.RNG_G,'morph_seed':rz.C2.RNG_M}},
        'S3_ids':p['S3'],'border_ids':border,'tt1_families':tt_families,
        'meds_manifest_path':str(rz.MR.MEDS),'meds_manifest_sha256':sha(rz.MR.MEDS),
        'meds_score_manifest_path':str(rz.T.OUT/'meds/meds_score.csv'),
        'meds_score_manifest_sha256':sha(rz.T.OUT/'meds/meds_score.csv'),
        'meds_primary':primary_export,
        'meds_mapping':{'index':'zero-based index into FULL meds_manifest.csv; identical id order to meds_score.csv',
            'id_column':'id','primary_condition':'aligned == 1',
            'person':'pNNNNNN = ordinal rank of original person in sorted primary-person keys; preserves bootstrap order',
            'bootstrap_seed':20261125,'bootstrap_draws':2000,'persons':400,
            'privacy':'Original MEDS row and subject identifiers are not serialized. Reader resolves ids privately and emits aggregates only.'},
        'kernel':{'genuine_ids':genuine,'morph_ids':morph,'primary':'fixed:pil_bilinear',
                  'train9':rz.TRAIN9,'held4':rz.HELD4},
        'platform_recipe':{'gpu':'H100','steps':6250,'packs':rz.PINS,
            'arms':{name:dict(zip(('manifest','training_spec','primary_spec','res','batch_size','accum','cross_specs'),spec))
                    for name,spec in rz.ARM.items()}},
        'refit_yardstick':{'source_tar_sha_prefix':rz.RZ1R_PIN,'n_gate_rows':21277,
            'required_gate_verdict':'passed','seeds':list(rz.SEEDS)},
        'own_rule':{'statistic':'logit','operator':'>','cutoff':0},
        'limits':['Metadata alone does not establish platform/fit/gate eligibility or any criterion outcome.',
                  'Native non-RZ1 adapters need separate complete provenance and support before candidate access.',
                  'Do not copy MEDS identifiers into outputs; aggregate flag shares and bounds only.'],
    }
    # Only opaque MEDS groups/indices, never original subject keys or row IDs.
    serialized=json.dumps(support,indent=2,sort_keys=True)+'\n'
    for _,r in primary:
        assert json.dumps(r['person']) not in serialized and json.dumps(r['id']) not in serialized
    OUT.mkdir(parents=True,exist_ok=True)
    target=OUT/'support_v3.json'
    if target.exists():assert target.read_text()==serialized,'refuse replacing changed support'
    else:target.write_text(serialized)
    paths=[target,pathlib.Path(__file__).resolve(),*source_paths]
    lines=[]
    for path in paths:
        label=str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
        lines.append(f'{sha(path)}  {label}')
    pinfile=OUT/'pins.sha256';text='\n'.join(lines)+'\n'
    if pinfile.exists():assert pinfile.read_text()==text,'refuse replacing changed support pins'
    else:pinfile.write_text(text)
    report={'pinned_files':len(lines),'tt1_family_primary_counts':{k:len(v) for k,v in tt_families.items()},
        'storage_photo_pairs':{k:len(v) for k,v in photo_pairs.items()},
        'storage_morph_pairs':{k:len(v) for k,v in morph_pairs.items()},
        'S3':len(p['S3']),'border':len(border),'MEDS_primary':len(primary),'MEDS_person_groups':len(persons),
        'kernel_genuine':len(genuine),'kernel_morph':len(morph),'no_scores_or_images_read':True}
    print(json.dumps(report,indent=2))


def verify(require_clean):
    target=OUT/'support_v3.json';support=json.loads(target.read_text())
    count=0
    for line in (OUT/'pins.sha256').read_text().splitlines():
        expected,label=line.split(None,1);p=ROOT/label
        assert sha(p)==expected,('support pin failed',label)
        if require_clean and p.is_relative_to(ROOT):
            committed=subprocess.check_output(['git','-C',str(ROOT),'show',f'HEAD:{p.relative_to(ROOT)}'])
            assert committed==p.read_bytes(),('uncommitted support/source',label)
        count+=1
    for path,h in support['sources'].items():assert sha(pathlib.Path(path))==h,('source drift',path)
    if require_clean:
        assert not subprocess.check_output(['git','-C',str(ROOT),'status','--porcelain']).strip(),'dirty tree'
        assert subprocess.check_output(['git','-C',str(ROOT),'show',f'HEAD:{(OUT/"pins.sha256").relative_to(ROOT)}'])==(OUT/'pins.sha256').read_bytes()
    print(json.dumps({'support_pins_verified':count,'require_clean':require_clean,'candidate_read_admission':False},indent=2))


if __name__=='__main__':
    assert sys.flags.isolated,'run with python -I'
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['prepare','verify'])
    parser.add_argument('--require-clean',action='store_true')
    args=parser.parse_args()
    if args.command=='prepare':prepare()
    else:verify(args.require_clean)
