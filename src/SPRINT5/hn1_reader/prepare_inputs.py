"""Candidate-free immutable HN input binding; source/labels/provenance only."""
import csv
import json
import pathlib
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import shared
import policy as P
import hn_stats


def main():
    repo=pathlib.Path(P.ROOT);out=repo/'experiments/SPRINT5_20261114/hn1/reader_implementation'
    out.mkdir(parents=True,exist_ok=True)
    assert not(out/'PILOT_READER_BINDING.json').exists(),'never overwrite a prepared/adopted binding'
    S=shared.load();bp=repo/'experiments/SPRINT5_20261114/paired_ranking/prefit_binding_v1/BINDING.json'
    assert shared.sha(bp)==shared.BINDING_SHA
    sb=json.loads(bp.read_text());meta=S.data.metadata(sb);S.data.floors(meta)
    pins=dict(sb['pins']);pins[str(bp)]=shared.BINDING_SHA
    for root in (shared.ROOT,repo/'src/SPRINT5/hn1_transfer'):
        expected=shared.SUMS_SHA if root==shared.ROOT else P.TRAIN_SOURCE
        assert shared.sha(root/'SHA256SUMS')==expected;pins[str(root/'SHA256SUMS')]=expected
        for line in (root/'SHA256SUMS').read_text().splitlines():
            h,n=line.split('  ',1);assert shared.sha(root/n)==h;pins[str(root/n)]=h
    pol=pathlib.Path(P.POLICY_ROOT);pb=pol/'BINDING_PROPOSAL.json';ps=pol/'SHA256SUMS';pa=pol/'ROOT_POLICY_INPUT_ADMISSION.json'
    assert shared.sha(pb)==P.POLICY_BINDING_SHA and shared.sha(ps)==P.PACKET_SHA
    adopted=json.loads(pa.read_text());assert adopted['decision']=='GO_POLICY_INPUTS_ONLY' and adopted['binding_sha256']==P.POLICY_BINDING_SHA
    assert adopted['packet_manifest_sha256']==P.PACKET_SHA and adopted['scientific_read']=='HOLD'
    for path,h in json.loads(pb.read_text())['input_pins'].items():assert shared.sha(path)==h;pins[path]=h
    root_policy=pathlib.Path(adopted['root_review_path']);assert shared.sha(root_policy)==adopted['root_review_sha256']
    for p in (pb,ps,pa,root_policy):pins[str(p)]=shared.sha(p)
    # Source receipts and ordered training manifests only; never fit results.
    prereg=repo/'experiments/SPRINT5_20261114/hn1/prereg_transfer.md';release=prereg.parent/'PILOT_RELEASE.json'
    audit=prereg.parent/'TRANSFER_EXCLUSION_AUDIT.json';a=json.loads(audit.read_text());assert a['status']=='PASS'
    assert a['train_hosts']==124 and a['train_people']==143 and a['dev_hosts']==100 and a['dev_people']==200
    assert all(a[k]==[] for k in ('identity_intersection','path_intersection','input_bytehash_intersection'))
    for path,h in a['metadata_pins'].items():assert shared.sha(path)==h;pins[path]=h
    overlay=pathlib.Path('/mnt/t7/smad_next/SPRINT5_2/transfer_overlay_v1');receipt=overlay/'OVERLAY_RECEIPT.json';o=json.loads(receipt.read_text())
    r=json.loads(release.read_text());assert r['decision']=='GO_PILOT' and r['source_sums_sha256']==P.TRAIN_SOURCE and r['seeds']==list(P.SEEDS)
    assert o['status']=='PASS' and o['rows_per_arm']==248 and o['positive_common_images']==124
    assert o['overlay_sha256']==r['hn_overlay_sha256'] and o['control_receipt_sha256']==r['control_receipt_sha256']
    records_path=pathlib.Path('/mnt/t7/smad_next/SPRINT5_2/transfer_control124_v1/records.json')
    assert shared.sha(records_path)==o['control_records_sha256'];records=json.loads(records_path.read_text())
    assert len(records)==124 and len({x['host'] for x in records})==124
    records_by_host={x['host'].replace(':','_'):x for x in records}
    for x in records:
        assert x['status']=='PASS' and x['warps_per_layer']==1 and x['blend_weight']==.5
        for path,h in x['input_pins'].items():assert shared.sha(path)==h;pins[path]=h
        for image in (x['common_positive'],x['matched_negative'],x['outputs']['Nself']):
            assert shared.sha(image['path'])==image['sha256'];pins[image['path']]=image['sha256']
    plans=[];perarm={}
    for arm in P.ARMS:
        path=overlay/f'train_HN_{arm}.csv';rows=list(csv.DictReader(path.open()))
        assert len(rows)==len({x['id'] for x in rows})==len({x['path'] for x in rows})==248
        assert sum(int(x['label']) for x in rows)==124 and sum(x['db']=='feret' for x in rows)==44
        assert all(x['hist']=='native' and x['source']=='smdd' and x['kind']==('lad_S4' if x['label']=='1' else 'lad_S3') for x in rows)
        assert shared.sha(path)==o['pins']['pn1/data/manifests/'+path.name];pins[str(path)]=shared.sha(path)
        for row in rows:
            _,_,host,kind=row['path'].split('/');x=records_by_host[host]
            image=x['common_positive'] if kind=='P.png' else x['matched_negative'] if kind=='Nmatched.png' else x['outputs']['Nself']
            assert kind==('P.png' if row['label']=='1' else 'Nmatched.png' if arm=='matched' else 'Nself.png')
            assert row['id']=='hn_'+host+'_'+kind.removesuffix('.png')
            assert o['pins']['pn1/data/'+row['path']]==image['sha256']
        perarm[arm]=rows
        for seed in P.SEEDS:
            plans.append({'arm':arm,'seed':seed,'train_manifest_sha256':shared.sha(path),
                 'schedule':{'mode':'full248rowshufflecycle','steps':100,'batch_size':248,'exact_per_image_exposures':100,
                             'total_image_exposures':24800,'row_ids':[x['id'] for x in rows],'seed':seed}})
    assert [x for x in perarm['matched'] if x['label']=='1']==[x for x in perarm['self'] if x['label']=='1']
    for p in (prereg,release,audit,receipt,records_path):pins[str(p)]=shared.sha(p)
    exp=out/'EXPECTED_PLANS.json';exp.write_text(json.dumps(plans,indent=2)+'\n');pins[str(exp)]=shared.sha(exp)
    _,report=hn_stats.design(meta['primary'],verify_registered=True)
    report.update(scope='Input metadata only; no candidate payloads, archives, score members or checkpoints',candidate_payload_accessed=False)
    rp=out/'BOOTSTRAP_READABILITY_METADATA.json';rp.write_text(json.dumps(report,indent=2)+'\n');pins[str(rp)]=shared.sha(rp)
    for p in (pathlib.Path(__file__).resolve(),pathlib.Path(hn_stats.__file__).resolve(),pathlib.Path(shared.__file__).resolve(),pathlib.Path(P.__file__).resolve()):pins[str(p)]=shared.sha(p)
    b={'schema_version':1,'experiment_id':P.EXPERIMENT,'status':'PREPARED_REQUIRES_ROOT_ADOPTION','scope':'PRIMARY_DESCRIPTIVE_ONLY',
       'arms':list(P.ARMS),'seeds':list(P.SEEDS),'expected_fit_count':10,'steps':100,'batch_size':248,'forwards':24800,'checkpoint':'last',
       'training_source_sums_sha256':P.TRAIN_SOURCE,'shared_input_binding':str(bp),'shared_input_binding_sha256':shared.BINDING_SHA,
       'shared_reader_sums_sha256':shared.SUMS_SHA,'prereg_path':str(prereg),'prereg_sha256':pins[str(prereg)],
       'pilot_release_path':str(release),'pilot_release_sha256':pins[str(release)],
       'expected_plans_path':str(exp),'expected_plans_sha256':pins[str(exp)],'provenance_audit_path':str(audit),'provenance_audit_sha256':pins[str(audit)],
       'policy_binding_path':str(pb),'policy_binding_sha256':P.POLICY_BINDING_SHA,'policy_packet_manifest_path':str(ps),'policy_packet_manifest_sha256':P.PACKET_SHA,
       'policy_input_admission_path':str(pa),'policy_input_admission_sha256':pins[str(pa)],'root_policy_path':str(root_policy),'root_policy_sha256':pins[str(root_policy)],
       'readability_metadata_path':str(rp),'readability_metadata_sha256':pins[str(rp)],
       'primary_policy':{'contrast':'matched_minus_self','statistic':'seed_mean_equal_five_fixed_D_stratum_AUC','two_sided_confidence':.95,'draws':10000,'rng':P.RNG,
           'unreadable_policy':'accepted_label_conditional_draws_then_seed_matrix','criteria':['mean_gain>=.03','positive_seed_effects>=4'],'no_adoption':True},
       'floor_policy':'Descriptive only; fixed15predictor maximum recomputed in every shared accepted draw; no floor advantage gate',
       'warmstart':'Single common admitted AB1 Sb408; reset AdamW moments; five continuation seeds, not independent full training',
       'provenance_limits':'Existing direct source-person/input-byte/geometry-byte exclusion covers fixed dev100 only; no inherited camera admission or independent HN construction generalization claim',
       'camera_auxiliary':'HOLD_NOT_IMPLEMENTED_NO_CAMERA_ARRAY_ACCESS','exact_input_pins':pins,'implementation_review':'PENDING','scientific_read':'HOLD'}
    (out/'PILOT_READER_BINDING.json').write_text(json.dumps(b,indent=2)+'\n')
    print(json.dumps({'status':b['status'],'training_rows_per_arm':248,'source_contributors':143,'primary_rows':200,'primary_components':40,
                      'accepted_draws':report['accepted'],'attempts':report['attempts'],'candidate_payload_accessed':False}))


if __name__=='__main__':main()
