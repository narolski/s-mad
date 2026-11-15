"""Metadata-only population/seed audit; never opens scores or result archives."""
import collections
import csv
import hashlib
import json
import pathlib
import re

repo=pathlib.Path('/home/narolski/smad-next')
out=repo/'experiments/SPRINT5_20261114/paired_ranking'
paths={
 'dev':pathlib.Path('/mnt/t7/smad_next/AB1/overlay_tree/pn1/data/manifests/ab1_eval.csv'),
 'tt1':pathlib.Path('/mnt/t7/smad_next/TT1/pack_tree/tt1/data/manifests/tt1_score.csv'),
 'meds':pathlib.Path('/mnt/t7/smad_next/TT1/meds/pack_tree/tt1m/data/manifests/meds_score.csv'),
 'gd':pathlib.Path('/mnt/t7/smad_next/PR1/pr1_gd_tree/pr1g/data/manifests/pr1_gd.csv')}
report={'scope':'metadata only; no score/result/checkpoint read','manifests':{}}
for name,p in paths.items():
    rows=list(csv.DictReader(p.open()))
    assert rows
    # These are exact allowlisted existing development manifests, not glob-discovered sets.
    for r in rows:
        value=' '.join(str(v) for v in r.values()).lower()
        assert not any(x in value for x in ('mordiff','mad22','frll','dimorph','h1_poisson','casia_webface')),(name,r['id'])
    report['manifests'][name]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rows':len(rows),
       'families':dict(collections.Counter(r.get('fam',r.get('family','unknown')) for r in rows))}
    if name=='dev':
        assert set(r['fam'] for r in rows)=={'af0','ladder','splice','ffhq','ffhq_lcomb','ms1ffhq'}
        primary=[r for r in rows if r['fam']=='splice' and r['role']=='dev' and r['rung'] in ('S3','S4') and r['strength']=='']
        assert len(primary)==200
        assert len({r['host'] for r in primary})==100
        (out/'primary_rows.json').write_text(json.dumps(primary,indent=2)+'\n')
        report['primary']={'rows':200,'hosts':100,'ids_sha256':hashlib.sha256('\n'.join(r['id'] for r in primary).encode()).hexdigest()}

# Scope deliberately excludes results, scientific output JSON and imported archives.
# Search only prospective registration and source metadata for existing allocations.
hits=[]
pattern=re.compile(r'(?<!\d)(?:501|502|503|504|505)(?!\d)')
for root in (repo/'experiments',repo/'src'):
    for p in sorted(root.rglob('*')):
        if not p.is_file() or 'SPRINT5' in str(p):continue
        if any(x in str(p).lower() for x in ('valx','fst','a12sp','a12-sp')):continue
        if p.suffix not in ('.md','.sh','.sbatch','.py'):continue
        if p.suffix=='.md' and not any(x in p.name.lower() for x in ('prereg','registration','seed','plan')):continue
        if p.stat().st_size>2000000:continue
        for n,line in enumerate(p.read_text(errors='replace').splitlines(),1):
            if pattern.search(line) and re.search(r'seed|s501|s502|s503|s504|s505',line,re.I):
                hits.append({'path':str(p.relative_to(repo)),'line':n,'text':line[:400]})
report['seed_audit']={'proposed':[501,502,503,504,505],'protected_next':[413,414,415,416,417],
  'prior_metadata_hits':hits,'status':'REVIEW_HITS' if hits else 'NO_PRIOR_ALLOCATION_FOUND_IN_SCOPED_METADATA',
  'limit':'No universal scheduler/history claim; lead must cross-check concurrent allocations and bind allocation before production.'}
(out/'METADATA_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'primary':report['primary'],'seed_hits':len(hits),'manifest_counts':{k:v['rows'] for k,v in report['manifests'].items()}}))
