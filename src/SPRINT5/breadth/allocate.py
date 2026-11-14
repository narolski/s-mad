"""Equal-row identity breadth vs variants allocation [SPRINT5-4]. Metadata only."""
import argparse
import collections
import csv
import hashlib
import json
import pathlib
import random


def allocate(rows,k,v,seed):
    assert k>0 and v>0
    by_source=collections.defaultdict(lambda:collections.defaultdict(lambda:collections.defaultdict(list)))
    persons={};seen_persons={}
    for r in rows:
        unit=r['unit_id'];key=(r['source'],unit)
        ids=tuple(sorted(set(r['unit_person_ids'].split(';'))))
        assert len(ids)==2,'unit must represent exactly two authoritative identities'
        assert set(r['contributing_ids'].split(';'))<=set(ids) and r['contributing_ids']
        if key in persons:assert persons[key]==ids
        persons[key]=ids
        for person in ids:
            p=(r['source'],person)
            assert p not in seen_persons or seen_persons[p]==unit,'identities reused across allocation units'
            seen_persons[p]=unit
        by_source[r['source']][unit][r['variant_id']].append(r)
    rng=random.Random(seed);arms={'narrow_more_variants':[],'broad_fewer_variants':[]}
    for source,units in sorted(by_source.items()):
        eligible=sorted(u for u,variants in units.items() if len(variants)>=2*v)
        assert len(eligible)>=2*k,'insufficient eligible disjoint identity units'
        rng.shuffle(eligible);selected=eligible[:2*k]
        reference_signature=None
        for j,u in enumerate(selected):
            variants=sorted(units[u]);rng.shuffle(variants)
            for arm,n in [('narrow_more_variants',2*v),('broad_fewer_variants',v)]:
                if arm=='narrow_more_variants' and j>=k:continue
                for variant in variants[:n]:
                    block=sorted(units[u][variant],key=lambda r:(r['kind'],r['label'],r['path']))
                    signature=collections.Counter((r['kind'],r['label'],r['processing']) for r in block)
                    if reference_signature is None:reference_signature=signature
                    assert signature==reference_signature,'variant/source class/family/processing budgets differ'
                    arms[arm].extend(block)
    summary={}
    for arm,rs in arms.items():
        assert len({r['path'] for r in rs})==len(rs),'repeated asset breaks equal unique-content allocation'
        summary[arm]={'rows':len(rs),'unique_images':len(rs),
         'identities':len({(r['source'],p) for r in rs for p in r['unit_person_ids'].split(';')}),
         'source_kind_label_processing':dict(collections.Counter('|'.join((r['source'],r['kind'],r['label'],r['processing'])) for r in rs)),
         'per_identity_exposure':dict(collections.Counter(r['source']+':'+p for r in rs for p in r['contributing_ids'].split(';')))}
    a,b=summary.values()
    assert a['rows']==b['rows'] and a['source_kind_label_processing']==b['source_kind_label_processing']
    assert b['identities']==2*a['identities']
    return arms,summary


def smoke():
    rows=[]
    for source in ('one','two'):
        for u in range(8):
            for variant in range(4):
                for kind,label in [('S3','0'),('S4','1')]:
                    rows.append(dict(unit_id=str(u),unit_person_ids=f'{2*u};{2*u+1}',source=source,variant_id=str(variant),
                       kind=kind,label=label,contributing_ids=(str(2*u) if label=='0' else f'{2*u};{2*u+1}'),processing='native',path=f'{source}/{u}/{variant}/{kind}.png'))
    results=[]
    for seed in (511,512,513,514,515):
        _,s=allocate(rows,2,2,seed);results.append({'seed':seed,'summary':s})
    return {'status':'SYNTHETIC_METADATA_PASS','runs':results}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=pathlib.Path)
    ap.add_argument('--out',type=pathlib.Path);ap.add_argument('--k',type=int);ap.add_argument('--v',type=int)
    ap.add_argument('--seed',type=int);ap.add_argument('--smoke',action='store_true');a=ap.parse_args()
    if a.smoke:print(json.dumps(smoke(),indent=2));return
    assert a.input and a.out and a.k and a.v and a.seed is not None
    assert not a.out.exists();a.out.mkdir(parents=True)
    rows=list(csv.DictReader(a.input.open()));arms,summary=allocate(rows,a.k,a.v,a.seed)
    for arm,rs in arms.items():
        with (a.out/(arm+'.csv')).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
    (a.out/'allocation.json').write_text(json.dumps({'seed':a.seed,'k':a.k,'v':a.v,'summary':summary,
       'input_sha256':hashlib.sha256(a.input.read_bytes()).hexdigest(),'scope':'metadata allocation only; actual image/identity provenance not admitted'},indent=2)+'\n')


if __name__=='__main__':main()
