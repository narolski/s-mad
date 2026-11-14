"""Input/provenance metadata only; no primary reader, statistic, NPZ or RNG imports."""
import csv
import json
import pathlib
import subprocess
import bridge
import policy as P


def need(value,message):
    if not value:raise ValueError(message)


def obj(path):return json.loads(pathlib.Path(path).read_text())


def committed_paths(binding_path,binding,code):
    repo=pathlib.Path(P.ROOT)
    out=[pathlib.Path(binding_path).resolve().relative_to(repo)]
    out.extend(pathlib.Path(pin).relative_to(repo) for pin in binding['pins'] if pathlib.Path(pin).is_relative_to(repo))
    out.extend((code/name).relative_to(repo) for name in ['SHA256SUMS',*[line.split('  ',1)[1] for line in (code/'SHA256SUMS').read_text().splitlines()]])
    return out


def git_clean(repo,paths):
    for path in paths:subprocess.run(['git','ls-files','--error-unmatch',str(path)],cwd=repo,check=True,capture_output=True)
    need(not subprocess.check_output(['git','status','--porcelain','--',*[str(path) for path in paths]],cwd=repo,text=True),'binding/input/source paths must be tracked and clean')


def validate_primary(binding):
    files=binding['primary_files']
    for name,spec in files.items():need(bridge.sha(spec['path'])==spec['sha256'],'original primary bytes changed '+name)
    need(files['result']['path']==P.PRIMARY_RESULT and files['result']['sha256']==P.PRIMARY_RESULT_SHA,'different primary result')
    need(files['claim']['path']==P.PRIMARY_ONCE+'/CLAIM.json' and files['terminal']['path']==P.PRIMARY_ONCE+'/TERMINAL.json','different primary journal')
    terminal=obj(files['terminal']['path']);claim=obj(files['claim']['path']);release=obj(files['release']['path'])
    need(terminal['status']=='COMPLETE' and terminal['sha256']==P.PRIMARY_RESULT_SHA,'primary must be original COMPLETE result')
    need(claim['reader_sums_sha256']==P.PRIMARY_SOURCE_SHA and claim['binding_sha256']==P.PRIMARY_BINDING_SHA,'different primary source/binding')
    need(claim['release_sha256']==files['release']['sha256'] and claim['roster_sha256']==binding['candidate_roster_sha256'],'primary release/roster mismatch')
    need(release['decision']=='GO_READER_READ' and release['roster_sha256']==binding['candidate_roster_sha256'],'original primary release missing')
    need(set(claim['archive_sha256'])=={x['archive_sha256'] for x in binding['candidates']} and len(claim['archive_sha256'])==15,'different candidate cohort')
    return {name:spec['sha256'] for name,spec in files.items()}


def validate_candidate_cases(cases):
    need(len(cases)==15 and {(x['arm'],x['seed']) for x in cases}=={(a,s) for a in P.ARMS for s in P.SEEDS},'all15candidate cases required')
    need(len({x['archive_sha256'] for x in cases})==len({x['archive_path'] for x in cases})==15,'duplicate candidate archive')
    for x in cases:
        need(x['task']==f'SPRINT5_3_pilot_v1_{x["arm"]}_s{x["seed"]}' and x['exact_aux_score_member']==x['task']+'/battery/logits_dev.npz','wrong candidate member')


def validate(binding_path=P.BINDING,require_committed=False):
    binding_path=pathlib.Path(binding_path).resolve();b=obj(binding_path)
    need(b['experiment_id']==P.EXPERIMENT and b['scope']==P.READ_SCOPE and b['timing']==P.TIMING,'wrong auxiliary scope/timing')
    need((b['auxiliary_once'],b['auxiliary_output'],b['technical_directory'])==(P.ONCE,P.OUTPUT,P.TECHDIR),'alternate journal/output forbidden')
    need(bridge.sha(P.POLICY_PATH)==P.POLICY_SHA and b['policy_adoption_sha256']==P.POLICY_SHA,'policy changed')
    adoption=obj(P.POLICY_PATH)
    need(adoption['decision']=='GO_POLICY_AND_IMPLEMENTATION_ONLY_AUXILIARY_AFTER_PRIMARY_RESULTS_SEEN' and adoption['timing']==P.TIMING,'auxiliary policy not adopted')
    need(adoption['auxiliary_once']==P.ONCE and adoption['auxiliary_output']==P.OUTPUT and adoption['new_primary_read']=='FORBIDDEN','primary boundary changed')
    need(adoption['allowed_candidate_numerical_ids']==468 and adoption['allowed_baseline_numerical_ids']==538 and adoption['uncertainty_status']=='NOT_ESTIMATED_DESCRIPTIVE_AUXILIARY','policy populations/uncertainty changed')
    need(adoption['author']!=adoption['reviewer'] and adoption['scientific_auxiliary_read']==adoption['technical_member_access']=='HOLD','policy cannot grant live read')
    for key in ('plan','independent_review'):need(bridge.sha(adoption[key+'_path'])==adoption[key+'_sha256'],'policy review/plan changed')
    for pin_path,digest in b['pins'].items():need(bridge.sha(pin_path)==digest,'input/source pin changed '+pin_path)
    need(b['baseline_archive']==P.BASELINE and b['baseline_archive_sha256']==P.BASELINE_SHA and b['baseline_score_member']==P.MEMBER,'baseline cannot be replaced')
    need(b['manifest_path']==P.EVAL and b['manifest_sha256']==P.EVAL_SHA,'manifest changed')
    rows=list(csv.DictReader(open(P.EVAL)));need(len(rows)==21277 and len({r['id'] for r in rows})==21277,'full manifest duplicates/count')
    ids=[r['id'] for r in rows];mapping=obj(b['mapping_path']);byid={r['id']:r for r in rows}
    need(len(mapping)==538 and len({r['id'] for r in mapping})==538,'selected mapping count/duplicates')
    for row in mapping:
        actual=byid[row['id']]
        need(actual['path']==row['path'] and int(actual['label'])==row['label'] and actual['role']=='dev','ID/path/label/history changed')
        need(ids[row['manifest_index']]==row['id'],'mapping order changed')
    C=[r for r in mapping if r['partition']=='positive_calibration'];E=[r for r in mapping if r['partition']=='evaluation']
    need(len(C)==70 and len(E)==468 and all(r['label']==1 and r['processing']=='native' for r in C),'wrong original calibration')
    need([r['id'] for r in C]==b['calibration_ids'] and [r['id'] for r in E]==b['evaluation_ids'],'ordered allowlist changed')
    need(not {r['component'] for r in C}&{r['component'] for r in E},'calibration/evaluation components overlap')
    cells=[];guards=[]
    for source,processing in P.CELLS:
        ii=[i for i,r in enumerate(E) if r['label']==0 and (r['source'],r['processing'])==(source,processing)]
        n,k=(70,20) if source=='feret' else (26,14)
        need((len(ii),len({E[i]['component'] for i in ii}))==(n,k),'fixed genuine cell changed')
        cells.append({'source':source,'processing':processing,'indices':ii,'rows':n,'components':k})
    for family,n,k in zip(P.FAMILIES,(146,0,17,17),(10,0,17,17)):
        ii=[i for i,r in enumerate(E) if r['label']==1 and r['positive_family']==family]
        need((len(ii),len({E[i]['component'] for i in ii}))==(n,k),'positive family/proxy changed')
        need(all(E[i]['processing']=='native' for i in ii),'processed positive proxy')
        guards.append({'family':family,'indices':ii,'rows':n,'components':k})
    cases=b['candidates'];validate_candidate_cases(cases)
    for x in cases:
        need(bridge.sha(x['admitted_metadata_envelope_path'])==x['admitted_metadata_envelope_sha256'],'candidate admitted envelope changed')
        envelope=obj(x['admitted_metadata_envelope_path'])
        need(envelope['status']=='ELIGIBLE_METADATA_ONLY' and envelope['archive_sha256']==x['archive_sha256'],'candidate admission changed')
        need(envelope['score_member_sha256'][x['exact_aux_score_member']]==x['score_member_sha256'],'candidate member digest changed')
    validate_primary(b)
    if require_committed:git_clean(pathlib.Path(P.ROOT),committed_paths(binding_path,b,pathlib.Path(__file__).resolve().parent))
    return b,{'calibration':C,'evaluation':E,'genuine_cells':cells,'positive_guards':guards,'manifest':{'ids':ids,'sha256':P.EVAL_SHA}}
