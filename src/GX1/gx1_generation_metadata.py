"""Audit generation plans/logs only; never opens an image, latent or candidate result."""
import argparse
import collections
import csv
import hashlib
import json
import math
import pathlib
import re


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(plans, logs, accounting):
    source={}; report={}; bad=[]
    for gen in ('mip1','mip2'):
        all_rows=[]; n_shards=0; expected_minutes=0
        for planpath in sorted(plans.glob('GX1_*.json')):
            p=json.loads(planpath.read_text())
            if p['gen']!=gen or p.get('smoke'):continue
            logfile=logs/f"{p['shard']}.log.csv"; sidecar=logs/f"{p['shard']}.tar.sha256"
            source[str(planpath)]=sha(planpath);source[str(logfile)]=sha(logfile);source[str(sidecar)]=sha(sidecar)
            rows=list(csv.DictReader(logfile.open()))
            expected={j['stem']:j for j in p['jobs']}
            assert len(expected)==len(rows) and set(expected)=={r['stem'] for r in rows},p['shard']
            side=sidecar.read_text().split()
            assert len(side)==2 and re.fullmatch('[0-9a-f]{64}',side[0]) and side[1]==p['shard']+'.tar'
            for row in rows:
                assert 'smoke' not in row['stem']
                assert all(row[k]==expected[row['stem']][k] for k in ('rung','a','b','gen'))
                assert float(row['alpha'])==expected[row['stem']]['alpha']
                if not math.isfinite(float(row['loss'])):bad.append({'shard':p['shard'],'stem':row['stem'],'reason':'nonfinite loss'})
                if not re.fullmatch('[0-9a-f]{64}',row['png_sha256']):bad.append({'shard':p['shard'],'stem':row['stem'],'reason':'invalid PNG hash'})
                all_rows.append(dict(row,group=p['group']))
            n_shards+=1;expected_minutes+=p['est_minutes']
        report[gen]={'shards':n_shards,'logged_images':len(all_rows),
            'group_rung_counts':dict(collections.Counter(f"{r['group']}/{r['rung']}" for r in all_rows)),
            'old_plan_H100_hours':expected_minutes/60}
    source[str(accounting)]=sha(accounting)
    raw=json.loads(accounting.read_text()); seconds={'mip1':0,'mip2':0};jobs={}
    for line in raw['stdout'].splitlines():
        fields=line.split('|')
        if len(fields)<6 or not fields[0].startswith(('6315654_','6315655_')):continue
        assert fields[1]=='COMPLETED' and fields[3]=='0:0',line
        h,m,s=map(int,fields[2].split(':'))
        gen='mip1' if fields[0].startswith('6315654_') else 'mip2'
        seconds[gen]+=h*3600+m*60+s;jobs[fields[0]]=dict(state=fields[1],elapsed=fields[2],exit_code=fields[3],end=fields[5])
    assert len(jobs)==20 and report['mip1']['shards']==12 and report['mip2']['shards']==8
    assert report['mip1']['logged_images']==report['mip2']['logged_images']==1446
    for gen in report:report[gen]['observed_allocated_H100_hours']=seconds[gen]/3600
    return {'scope':'Generation plans, logs, sidecars and scheduler receipts only; not image admission',
        'accounting_time':raw['at'],'sources':source,'generators':report,'jobs':jobs,'errors':bad,
        'remaining_checks':['Fresh archive SHA256 agreement; per-image bytes/dimensions/PNG/finite latents',
            'Unchanged alignment pipeline with >=95% aligned per rung; false-aligned rows dropped and listed',
            'glintr100 identity gate R4 verifies both>=70%,R3 verifies own>=90% per registered group',
            'Committed admitted-image pins; matched training manifests; prefit cue floor; amendment2 and pre-run review',
            'Training smoke then ten fits; same-row Sb rescoring; NEXT transfer learner/support pins'],
        'training_ready':False,'candidate_scores_read':False}


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--plans',type=pathlib.Path,default=pathlib.Path('/mnt/t7/smad_next/GX1/inputs/shards'))
    ap.add_argument('--logs',type=pathlib.Path,default=pathlib.Path('/mnt/t7/smad_next/coordination_20261114/GX1_generation_metadata'))
    ap.add_argument('--accounting',type=pathlib.Path,default=pathlib.Path('/mnt/t7/smad_next/coordination_20261114/GX_GENERATION_AND_JOB_STATE.json'))
    ap.add_argument('--out',type=pathlib.Path,required=True)
    args=ap.parse_args();result=audit(args.plans,args.logs,args.accounting)
    encoded=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.out.exists():assert args.out.read_text()==encoded,'refuse replacing changed receipt'
    else:args.out.write_text(encoded)
    print(json.dumps({'generators':result['generators'],'errors':result['errors'],'training_ready':False},indent=2))
