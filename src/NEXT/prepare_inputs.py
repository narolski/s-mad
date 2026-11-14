"""Assemble/verify the approved NEXT rule's candidate-independent pre-read inputs.

Reads only explicit development manifests and existing adversary outputs. Never
opens a candidate archive, image, checkpoint, score file, or benchmark product.
This is deterministic packaging, not a new fit or selection-rule application.
"""
import argparse
import collections
import csv
import hashlib
import io
import json
import math
import pathlib
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXP = ROOT / 'experiments/NEXT_method-selection-rule'
OUT = EXP / 'inputs'
FLOORS = ROOT / 'experiments/ADV_shortcut-floors/floors'
T7 = pathlib.Path('/mnt/t7/smad_next')
RULE = EXP / 'prereg_draft_v3.md'
CODE = pathlib.Path(__file__).resolve()
FORBIDDEN = ('fst', 'valx', 'a12sp', 'a12-sp', 'train90', 'val10')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    assert not any(t in str(path).lower() for t in FORBIDDEN), path
    return list(csv.DictReader(path.open()))


def unique(rows_, key='id'):
    result = {r[key]: r for r in rows_}
    assert len(result) == len(rows_), ('duplicate', key)
    return result


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


def committed(path):
    rel = str(path.relative_to(ROOT))
    content = subprocess.check_output(['git', '-C', str(ROOT), 'show', f'HEAD:{rel}'])
    assert content == path.read_bytes(), ('not committed at HEAD', rel)
    return git('log', '-1', '--format=%H', '--', rel)


def historical_pin(path):
    digest = sha(path)
    for pin in sorted(FLOORS.glob('pins_stage*.sha256')):
        for line in pin.read_text().splitlines():
            expected, name = line.split(None, 1)
            if name.strip() == path.name and expected == digest:
                committed(pin)
                return str(pin.relative_to(ROOT))
    raise AssertionError(('no matching committed ADV stage pin', path.name))


def csv_bytes(rows_, fields):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows_)
    return stream.getvalue().encode()


def put(name, data):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == data, ('refuse overwrite changed input', path)
    else:
        path.write_bytes(data)


def prepare():
    OUT.mkdir(exist_ok=True)
    assert '**Status: APPROVED.**' in RULE.read_text()
    committed(RULE)
    metadata = {'source_head': git('rev-parse', 'HEAD'),
                'scope': 'Development manifests and existing adversary products only; no challenger results read',
                'rule_sha256': sha(RULE), 'sources': {}, 'files': {}}
    sources = {}

    def source(path, destination, adversary=False):
        info = {'sha256': sha(path), 'bytes': path.stat().st_size, 'snapshot': destination}
        if path.is_relative_to(ROOT):
            info['last_commit'] = committed(path)
        if adversary:
            info['historical_pin'] = historical_pin(path)
        sources[str(path)] = info
        if destination:
            put(destination, path.read_bytes())
        return path

    # These sources are manifests, not candidate score outputs.
    manifest = source(T7/'AB1/x/manifests/ab1x_eval.csv', None)
    split = source(ROOT/'experiments/PN1_protocol-network-first-tests/split/ladder_split.csv', 'ladder_split.csv')
    pool = source(T7/'AR1/pool.csv', None)
    dvalues = source(T7/'BD1/d_values.csv', 'd_values.csv')
    clean = source(T7/'DATA/overlap/test_hosts_clean_of_dev.csv', 'test_hosts_clean_of_dev.csv')
    shape = source(T7/'DATA/overlap/shape_linked_test_hosts.csv', 'shape_linked_test_hosts.csv')
    source(ROOT/'experiments/DATA_builds/selection_hosts.json', 'selection_hosts_provenance.json')
    source(ROOT/'src/DATA/selection_hosts.py', 'provenance/selection_hosts.py')
    source(ROOT/'src/adversary/amend5.py', 'provenance/amend5.py')
    source(ROOT/'src/adversary/run_floors.py', 'provenance/run_floors.py')
    source(ROOT/'experiments/ADV_shortcut-floors/prereg.md', 'provenance/adversary_prereg.md')
    # Check the formerly failing ADV source pin without modifying it.
    advpins = ROOT/'experiments/ADV_shortcut-floors/pins.sha256'
    source(advpins, 'provenance/adversary_source_pins.sha256')
    for line in advpins.read_text().splitlines():
        digest, filename = line.split(None, 1)
        p = pathlib.Path(filename)
        if not p.is_absolute(): p = ROOT/p
        assert sha(p) == digest, ('ADV source pin fails', str(p))

    floor_names = [
        'sel360_rows.csv', 'sel360_withinD.json',
        'lcomb_smatch_rows.csv', 'lcomb_smatch_build.json',
        'transfer_Sb_rows.csv', 'transfer_SbFM_rows.csv',
        'lcomb.json', 'lcomb_heldout.csv', 'lcomb_regional.json', 'lcomb_regional_heldout.csv',
        'ri_R4_vs_R3.json', 'ri_R4_vs_R3_heldout.csv',
        'ri_R4_vs_R3_regional.json', 'ri_R4_vs_R3_regional_heldout.csv', 'ri_R4_vs_R3_withinD.json',
        'test_cv_R4_vs_R3_withinD.json', 'lcomb_bal_rows.csv',
        'lcomb_bal.json', 'lcomb_bal_heldout.csv', 'lcomb_bal_regional.json', 'lcomb_bal_regional_heldout.csv',
    ]
    for name in floor_names:
        source(FLOORS/name, 'floors/'+name, adversary=True)
    for arm, path in [('Sb', T7/'PN1/manifests2/train_Sb.csv'), ('SbFM', T7/'AB1/fm/manifests/train_SbFM.csv')]:
        source(path, f'train_{arm}.csv')

    man = unique(rows(manifest))
    spl = unique(rows(split), 'pid')
    clean_hosts = set(unique(rows(clean), 'host'))
    shape_rows = rows(shape)
    shape_hosts = set(unique(shape_rows, 'test_host'))
    assert len(clean_hosts) == 80 and len(shape_hosts) == 32
    pp = unique(rows(pool), 'pid')
    expected_shape = {p['B_pid']: p['pid'] for p in pp.values()
                      if spl[p['pid']]['role'] == 'train' and spl.get(p['B_pid'], {}).get('role') == 'test'}
    # The original audit t32 uses all training-role hosts whose partner is test.
    assert set(expected_shape) == shape_hosts
    assert all(expected_shape[r['test_host']] == r['training_host_whose_partner_it_is'] for r in shape_rows)
    assert len(shape_hosts & clean_hosts) == 11

    ri = unique(rows(FLOORS/'ri_R4_vs_R3_heldout.csv'))
    sel = rows(FLOORS/'sel360_rows.csv')
    expected_sel = [r for r in ri.values() if man[r['id']]['role'] == 'dev' or man[r['id']]['host'] in clean_hosts]
    assert [r['id'] for r in expected_sel] == [r['id'] for r in sel]
    assert len(sel) == 360 and sum(int(r['label']) for r in sel) == 180
    assert len({r['component'] for r in sel}) == 110
    assert len({r['host'] for r in sel if r['role'] == 'dev'}) == 100
    assert len({r['host'] for r in sel if r['role'] == 'test'}) == 80
    D = {(r['host'], r['rung']): r['D'] for r in rows(dvalues)}
    regional = unique(rows(FLOORS/'ri_R4_vs_R3_regional_heldout.csv'))
    merged = []
    for r in sel:
        i = r['id']; m = man[i]
        assert m['tool'] == 'opencv' and m['rung'] in ('R4', 'R3')
        assert r['component'] == ri[i]['component'] == regional[i]['component']
        assert r['label'] == ri[i]['label'] == regional[i]['label'] == m['label']
        value = D[(m['host'], {'R4':'S4', 'R3':'S3'}[m['rung']])]
        assert math.isfinite(float(value)) and float(value) > 0
        new = dict(r, rung=m['rung'], path=m['path'], D=value,
                   shape_linked_test_host=int(m['host'] in shape_hosts))
        new.update({k:v for k,v in ri[i].items() if k not in new})
        new.update({k:v for k,v in regional[i].items() if k not in new})
        merged.append(new)
    put('sel360_with_D_and_floors.csv', csv_bytes(merged, list(merged[0])))
    # Explicitly commit every descriptive ladder variant before candidate access.
    variants = {
        'sel360_without_shape_linked.csv': [r for r in merged if not r['shape_linked_test_host']],
        'sel360_development_only.csv': [r for r in merged if r['role'] == 'dev'],
        'sel360_clean_test_only.csv': [r for r in merged if r['role'] == 'test'],
    }
    assert [len(v) for v in variants.values()] == [338, 200, 160]
    for name, subset in variants.items():
        put(name, csv_bytes(subset, list(merged[0])))
    hosts = {r['host'] for r in sel}
    fm = [dict(r) for r in man.values() if r['fam'] == 'ladder' and r['tool'] == 'facemorpher'
          and r['rung'] in ('R4','R3') and r['strength'] == '' and r['host'] in hosts]
    assert len(fm) == 360 and sum(int(r['label']) for r in fm) == 180
    assert {r['host'] for r in fm} == hosts
    for r in fm:
        # Reuse the fixed OpenCV host component for the descriptive same-host read.
        r['component'] = next(x['component'] for x in sel if x['host'] == r['host'])
    put('facemorpher_same_180_hosts_R4_vs_R3.csv', csv_bytes(fm, list(fm[0])))
    # Pin exact edges from the 360 rows; reader applies BD1's fixed stratum rule.
    logd = np.log(np.array([float(r['D']) for r in merged]))
    edges = np.quantile(logd, [.2,.4,.6,.8])
    q = np.searchsorted(edges, logd, side='right')
    strata = []
    for k in range(5):
        labels = [int(r['label']) for r,s in zip(merged,q) if s == k]
        strata.append({'quintile':k,'positive':sum(labels),'negative':len(labels)-sum(labels)})
    assert all(s['positive'] >= 10 and s['negative'] >= 10 for s in strata)
    put('sel360_D_strata.json', (json.dumps({'log_D_edges':edges.tolist(),'strata':strata,
         'coverage':1.0,'bootstrap_unit':'component from ri_R4_vs_R3_heldout.csv'},indent=2)+'\n').encode())

    lc = unique(rows(FLOORS/'lcomb_heldout.csv'))
    lcr = rows(FLOORS/'lcomb_regional_heldout.csv')
    assert len(lc) == len(lcr) == 3000
    assert sum(int(r['label']) for r in lc.values()) == 1000
    assert set(lc) == set(r['id'] for r in lcr)
    lcm = []
    for r in lcr:
        i = r['id']; m = man[i]
        assert r['label'] == lc[i]['label'] == m['label']
        assert r['component'] == lc[i]['component']
        item = dict(id=i,path=m['path'],label=r['label'],host=m['host'],role=m['role'],component=r['component'])
        item.update({k:v for k,v in lc[i].items() if k not in item})
        item.update({k:v for k,v in r.items() if k not in item})
        lcm.append(item)
    put('landmark_combined_rows_and_floors.csv', csv_bytes(lcm,list(lcm[0])))

    # Exact reproduction of amend5.smatch matching, without any floor/model refit.
    y = np.array([int(r['label']) for r in lcr])
    score = np.clip(np.array([float(r['surround_gbt']) for r in lcr]),1e-6,1-1e-6)
    z = np.log(score/(1-score)); sd = z.std()
    free = set(np.where(y == 0)[0].tolist()); pairs=[]
    for i in np.random.default_rng(20261117).permutation(np.where(y == 1)[0]):
        if not free: break
        cand=np.array(sorted(free)); distance=np.abs(z[cand]-z[i])/sd
        j=int(np.argmin(distance))
        if distance[j] <= .1:
            pairs.append((int(i),int(cand[j])));free.remove(int(cand[j]))
    expected=[dict(id=lcr[a]['id'],label='1',pair=str(k)) for k,(a,b) in enumerate(pairs)]
    expected += [dict(id=lcr[b]['id'],label='0',pair=str(k)) for k,(a,b) in enumerate(pairs)]
    smatch=rows(FLOORS/'lcomb_smatch_rows.csv')
    assert expected == smatch and len(pairs) == 360
    lcm_by_id = unique(lcm)
    smatch_merged = [dict(lcm_by_id[r['id']], pair=r['pair']) for r in smatch]
    put('lcomb_smatch_rows_and_floors.csv',csv_bytes(smatch_merged,list(smatch_merged[0])))
    # The rule's .504 surround/.949 face references identify heldout predictions
    # from the full 3000-row fit restricted to the 720 matching rows. The separate
    # amendment-5 matched-only balance refit has different numbers and is not used.
    def auc(column):
        pos=np.array([float(r[column]) for r in smatch_merged if r['label']=='1'])
        neg=np.array([float(r[column]) for r in smatch_merged if r['label']=='0'])
        return float(((pos[:,None]>neg).sum()+.5*(pos[:,None]==neg).sum())/(len(pos)*len(neg)))
    known = {'surround_gbt':auc('surround_gbt'),'face_gbt':auc('face_gbt'),'all_cue_logreg':auc('logreg')}
    assert round(known['surround_gbt'],3) == .504 and round(known['face_gbt'],3) == .949
    assert round(known['all_cue_logreg'],3) == .945
    put('matched_floor_provenance.json',(json.dumps({
        'prediction_source':'Full-landmark-contrast cross-fitted heldout scores, restricted to pinned matched IDs',
        'rule_reference_values_reproduced':known,
        'distinct_diagnostic':'floors/lcomb_smatch_build.json balance_refit re-fits only matched rows; not the rule reference',
        'no_new_fit':True,'shared_network_minus_floor_draw_seed':20261115,
        'standalone_existing_sel360_CI_seed':20261119,
        'warning':'Never substitute standalone floor CIs for shared network-minus-floor bootstrap draws.'},indent=2)+'\n').encode())

    ids_by_set={'lcomb':set(lc),'sel360':{r['id'] for r in sel},'lcomb_smatch':{r['id'] for r in smatch}}
    for arm in ('Sb','SbFM'):
        transfer=rows(FLOORS/f'transfer_{arm}_rows.csv')
        for subset,want in ids_by_set.items():
            rr=[r for r in transfer if r['set'] == subset]
            assert set(unique(rr)) == want
            for r in rr:
                origin=ri[r['id']] if subset == 'sel360' else lc[r['id']]
                assert r['label'] == origin['label'] and r['component'] == origin['component']
                assert all(math.isfinite(float(r[k])) for k in ('logreg','gbt'))
    metadata['sources']=sources
    metadata['checks']={'sel360_rows':360,'sel360_positive':180,'sel360_components':110,
        'shape_linked_test_hosts':32,'shape_linked_in_clean_test':11,'landmark_rows':3000,
        'landmark_positive':1000,'matched_pairs':360,'transfer_rows_per_list':4080,
        'ladder_without_shape_rows':338,'ladder_dev_only_rows':200,'ladder_test_only_rows':160,
        'facemorpher_same_hosts_rows':360,'matched_rule_floor_provenance_reproduced':True,
        'matching_reproduced_exactly':True,'ADV_source_pins_pass':True,
        'no_new_floor_fit':True,'no_challenger_results_read':True}
    metadata['remaining']=[
        'Lead must review and commit these inputs and final pins from a clean work tree before read admission.',
        'GX training manifest and its per-row transfer learner do not yet exist in this package; GX is not input-ready.',
        'Full selection reader and candidate eligibility/receipt verification are separate requirements.',
        'Existing floor subset rows can be used to compute all-cue/non-F27/non-BLEND/regional within-D prints; full-582-row JSONs are context, not sel360 summaries.',
        'No input-ready status establishes challenger registration, platform, fit, kernel, border or TT1 gates.'
    ]
    for p in sorted(OUT.rglob('*')):
        if p.is_file() and p.name not in ('manifest.json','pins.sha256'):
            metadata['files'][str(p.relative_to(OUT))]={'sha256':sha(p),'bytes':p.stat().st_size}
    encoded=(json.dumps(metadata,indent=2,sort_keys=True)+'\n').encode()
    put('manifest.json',encoded)
    pinpaths=[p for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'pins.sha256']+[CODE]
    pinlines=[f'{sha(p)}  {p.relative_to(ROOT)}' for p in pinpaths]
    put('pins.sha256', ('\n'.join(pinlines)+'\n').encode())
    print(json.dumps(metadata['checks'],indent=2))


def verify(require_clean):
    metadata=json.loads((OUT/'manifest.json').read_text())
    assert metadata['rule_sha256'] == sha(RULE), 'approved rule changed after packaging'
    for rel,info in metadata['files'].items():
        assert sha(OUT/rel) == info['sha256'], ('input drift',rel)
    for name,info in metadata['sources'].items():
        assert sha(pathlib.Path(name)) == info['sha256'], ('source drift',name)
    pinfile=OUT/'pins.sha256'
    count=0
    for line in pinfile.read_text().splitlines():
        expected,relative=line.split(None,1)
        path=ROOT/relative
        assert sha(path) == expected, ('pin mismatch',relative)
        if require_clean: committed(path)
        count+=1
    if require_clean:
        assert not git('status','--porcelain'), 'selection read refused: work tree is not clean'
        committed(pinfile)
    print(json.dumps({'pins_verified':count,'require_clean':require_clean,
        'read_admission':False,'reason':'This verifies inputs only, not challenger eligibility or full selection admission.'},indent=2))


if __name__ == '__main__':
    assert sys.flags.isolated, 'run with python -I'
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['prepare','verify'])
    parser.add_argument('--require-clean',action='store_true')
    args=parser.parse_args()
    if args.command == 'prepare': prepare()
    else: verify(args.require_clean)
