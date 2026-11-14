"""Candidate-free breadth input/provenance binding. Never accepts fit archives."""
import csv
import hashlib
import json
import pathlib
import re
import sys

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import shared
import policy as P
import breadth_stats


def main():
    S=shared.load();repo=pathlib.Path(P.ROOT)
    out=repo/'experiments/SPRINT5_20261114/breadth/reader_implementation'
    out.mkdir(parents=True,exist_ok=True)
    old=out/'PILOT_READER_BINDING.json'
    if old.exists():
        prior=json.loads(old.read_text())
        assert prior['status'].startswith('PREPARED') and prior['scientific_read']=='HOLD','never overwrite adopted/read binding'
        assert not(out/'ROOT_INPUT_ADMISSION.json').exists(),'root input adoption already exists'
    binding_path=repo/'experiments/SPRINT5_20261114/paired_ranking/prefit_binding_v1/BINDING.json'
    assert shared.sha(binding_path)==shared.BINDING_SHA
    binding=json.loads(binding_path.read_text());meta=S.data.metadata(binding)
    # Floor inputs are already independently admitted and candidate-independent.
    S.data.floors(meta)
    source=repo/'src/SPRINT5/breadth_fit';assert shared.sha(source/'SHA256SUMS')==P.TRAIN_SOURCE
    pins=dict(binding['pins']);pins[str(binding_path)]=shared.BINDING_SHA
    pins[str(shared.ROOT/'SHA256SUMS')]=shared.SUMS_SHA
    for line in (shared.ROOT/'SHA256SUMS').read_text().splitlines():
        h,name=line.split('  ',1);pins[str(shared.ROOT/name)]=h
    pins[str(source/'SHA256SUMS')]=P.TRAIN_SOURCE
    for line in (source/'SHA256SUMS').read_text().splitlines():
        h,name=line.split('  ',1);assert shared.sha(source/name)==h;pins[str(source/name)]=h
    prereg=repo/'experiments/SPRINT5_20261114/breadth/prereg_pilot.md'
    release=repo/'experiments/SPRINT5_20261114/breadth/PILOT_RELEASE.json'
    for p in (prereg,release):pins[str(p)]=shared.sha(p)
    root_policy=out/'ROOT_PROSPECTIVE_PRIMARY_POLICY.md'
    assert root_policy.is_file(),'root prospective policy missing'
    pins[str(root_policy)]=shared.sha(root_policy)
    r=json.loads(release.read_text());assert r['decision']=='GO_PILOT' and r['seeds']==list(P.SEEDS) and r['source_sums_sha256']==P.TRAIN_SOURCE
    poolpath=pathlib.Path('/mnt/t7/smad_next/AR1/pool.csv');pool={r['pid']:r for r in csv.DictReader(poolpath.open())}
    ladder=S.data.pinned_path(binding,'/inputs/ladder_split.csv');L={r['pid']:r for r in csv.DictReader(ladder.open())}
    # Reuse only the read-only source-photo canonicalization prefix, not the
    # broad archive/experiment-list execution of the historical audit script.
    resolver=repo/'src/DATA/partner_overlap_audit.py';raw=resolver.read_text();prefix=raw.split("# ---------- builders' lists")[0]
    assert 'OUT.mkdir' not in prefix and 'json.dump' not in prefix and '"w"' not in prefix
    ns={};exec(compile(prefix,str(resolver),'exec'),ns);ns['pool']=pool
    for p in (resolver,poolpath,ns['MC']/'dmad/data/maps/feret_map.csv',ns['T7']/'volatile_backup_20261113/r6_train_sources.csv'):
        pins[str(p)]=shared.sha(p)
    def resolve(row):
        m=re.fullmatch(r'sp2_(S[34])_opencv_(feret|frgc)_(\d+)',row['id']);assert m,row['id']
        rung,db,pid=m.groups();h=db+':'+pid;p=pool[h];people={h,p['B_pid']}
        paths=[p['H'],p['B']]+([p['S']] if rung=='S3' else [])
        photos={ns['photo'](x) for x in paths};assert not any(x.startswith('unmapped:') for x in photos)
        return people,photos
    primary_people=set();primary_photos=set()
    for row in meta['primary']:
        ps,ph=resolve(row);primary_people|=ps;primary_photos|=ph
    parent={}
    def root(x):
        parent.setdefault(x,x)
        if parent[x]!=x:parent[x]=root(parent[x])
        return parent[x]
    for row in L.values():
        a,b=root(row['pid']),root(row['partner_B'])
        if a!=b:parent[max(a,b)]=min(a,b)
    primary_components={root(p) for p in primary_people}
    assetbase=pathlib.Path('/mnt/t7/smad_next/PN1/fs_tree/pn1/data')
    inventory=pathlib.Path('/mnt/t7/smad_next/SPRINT5_4/existing_pair_inventory_v1/inventory.json')
    pins[str(inventory)]=shared.sha(inventory)
    expected=[];audit=[];errors=[]
    for seed in P.SEEDS:
        perarm={}
        for arm in P.ARMS:
            path=source/f'train_{arm}_s{seed}.csv';rows=list(csv.DictReader(path.open()));assert len(rows)==32 and len({r['path'] for r in rows})==32
            assert sum(int(r['label']) for r in rows)==16
            assert {r['kind'] for r in rows}=={'lad_S3','lad_S4'} and all(r['source']=='smdd' and r['hist']=='native' for r in rows)
            assert sum(r['db']=='feret' for r in rows)==sum(r['db']=='frgc' for r in rows)==16
            people=set();photos=set();units=set()
            for row in rows:
                ps,ph=resolve(row);people|=ps;photos|=ph
                assert set(row['unit_person_ids'].split(';'))==ps
                assert set(row['contributing_ids'].split(';'))==(ps if row['label']=='1' else {row['id'].split('_')[-2]+':'+row['id'].split('_')[-1]})
                for p in ps:assert L[p]['role']=='train'
                a,b=sorted(ps);assert L[a]['partner_B']==b and L[b]['partner_B']==a
                units.add(tuple(sorted(ps)))
                image=assetbase/row['path'];pins[str(image)]=shared.sha(image)
            assert len(people)==(16 if arm==P.ARMS[0] else 32)
            overlaps={'person_geometry':sorted(people&primary_people),'source_photo':sorted(photos&primary_photos),
                      'full_component':sorted({root(p) for p in people}&primary_components)}
            if any(overlaps.values()):errors.append({'seed':seed,'arm':arm,'overlap':overlaps})
            audit.append({'seed':seed,'arm':arm,'training_rows':32,'actual_persons':len(people),'source_photos_with_geometry':len(photos),
                          'primary_overlap':overlaps,'provenance':'Pixel contributors and H/B target/hull suppliers included; S3 is not falsely counted as two pixel identities.'})
            perarm[arm]=units
            expected.append({'arm':arm,'seed':seed,'train_manifest_sha256':shared.sha(path),
                 'schedule':{'mode':'full32rowshufflecycle','steps':100,'batch_size':32,'exact_per_image_exposures':100,
                             'total_image_exposures':3200,'row_ids':[r['id'] for r in rows],'seed':seed},
                 'actual_persons':len(people),'training_rows':32})
        assert perarm[P.ARMS[0]]<=perarm[P.ARMS[1]],'broad units must be nested superset'
    exp=out/'EXPECTED_PLANS.json';exp.write_text(json.dumps(expected,indent=2)+'\n')
    provenance=out/'PRIMARY_TRAINING_PROVENANCE.json'
    provenance.write_text(json.dumps({'status':'PASS_PRIMARY_ONLY' if not errors else 'HOLD','cases':audit,'errors':errors,
       'scope':'Primary source-person/photo/geometry and full-component metadata audit only. Camera/auxiliary provenance NOT authorized or established here.',
       'limits':'Metadata identity/source provenance, not a biometric duplicate guarantee; no candidate archive/score/checkpoint read.'},indent=2)+'\n')
    pins[str(exp)]=shared.sha(exp);pins[str(provenance)]=shared.sha(provenance)
    _,readability=breadth_stats.design(meta['primary'])
    readability.update(scope='Input metadata only; no candidate archives/logits/checkpoints',candidate_payload_accessed=False)
    readability_path=out/'BOOTSTRAP_READABILITY_METADATA.json'
    readability_path.write_text(json.dumps(readability,indent=2)+'\n')
    pins[str(readability_path)]=shared.sha(readability_path)
    for p in (pathlib.Path(__file__).resolve(),pathlib.Path(breadth_stats.__file__).resolve(),pathlib.Path(shared.__file__).resolve(),pathlib.Path(P.__file__).resolve()):pins[str(p)]=shared.sha(p)
    output={'schema_version':1,'experiment_id':P.EXPERIMENT,'status':'PREPARED_REQUIRES_ROOT_ADOPTION',
      'scope':'PRIMARY_DESCRIPTIVE_ONLY','arms':list(P.ARMS),'seeds':list(P.SEEDS),'expected_fit_count':10,
      'steps':100,'batch_size':32,'forwards':3200,'checkpoint':'last','training_source_sums_sha256':P.TRAIN_SOURCE,
      'shared_input_binding':str(binding_path),'shared_input_binding_sha256':shared.BINDING_SHA,
      'shared_reader_sums_sha256':shared.SUMS_SHA,'prereg_path':str(prereg),'prereg_sha256':pins[str(prereg)],
      'pilot_release_path':str(release),'pilot_release_sha256':pins[str(release)],
      'expected_plans_path':str(exp),'expected_plans_sha256':pins[str(exp)],
      'provenance_audit_path':str(provenance),'provenance_audit_sha256':pins[str(provenance)],
      'root_policy_path':str(root_policy),'root_policy_sha256':pins[str(root_policy)],
      'readability_metadata_path':str(readability_path),'readability_metadata_sha256':pins[str(readability_path)],
      'primary_policy':{'contrast':'broad_minus_narrow','statistic':'seed_mean_equal_five_fixed_D_stratum_AUC',
          'two_sided_confidence':.95,'draws':10000,'rng':2026111404,
          'draw_order':'each replicate: source-stratified full components, then five jointly resampled arm-seed pairs',
          'unreadable_policy':'conditional_readable_percentile','no_binary_success_gate':True,'no_adoption':True},
      'floor_policy':'Descriptive per-arm seed-mean minus maximum of all15 fixed nuisance AUCs; max recomputed within shared draws; no floor qualification gate',
      'camera_auxiliary':'HOLD_NOT_IMPLEMENTED_NO_CAMERA_ARRAY_ACCESS',
      'exact_input_pins':pins,'implementation_review':'PENDING','scientific_read':'HOLD'}
    (out/'PILOT_READER_BINDING.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'status':output['status'],'provenance_errors':len(errors),'fits':len(expected),'primary_rows':200,
                      'camera_auxiliary':'HOLD','candidate_payload_accessed':False}))


if __name__=='__main__':main()
