"""Read-only source-photo resolver audit; outputs new isolated audit only."""
import argparse,csv,hashlib,json,pathlib,re
ap=argparse.ArgumentParser();ap.add_argument('--prepared',type=pathlib.Path,required=True);ap.add_argument('--out',type=pathlib.Path,required=True);a=ap.parse_args()
source=pathlib.Path('/home/narolski/smad-next/src/DATA/partner_overlap_audit.py');raw=source.read_text();prefix=raw.split('# ---------- lists')[0]
assert 'OUT.mkdir' not in prefix and 'json.dump' not in prefix and '"w"' not in prefix
prefix=prefix.replace('return list(csv.DictReader(open(p)))','READ_FILES[str(p)] = sha(p)\n    return list(csv.DictReader(open(p)))')
g={'READ_FILES':{}};exec(compile(prefix,str(source),'exec'),g)
trainpath=pathlib.Path('/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/train_Sb.csv');train=g['rd'](trainpath);assert len(train)==8386
assert g['sha'](trainpath)=='2cf3fda3affc8dd3d1574857f494037ea0382c8a2d314754b615686401b7fa4a'
def resolve(row):
 x=g['resolve'](row['id'],row.get('host',''));assert x is not None,row['id']
 people=set(x[0])|set(x[1]);photos=set(x[2])
 # Historical addendum: S3/S0 use partner's landmark geometry even without donor pixels.
 m=re.fullmatch(r'sp2?_S[034]_opencv_(feret|frgc)_(\d+)(?:_fm\d+|_amsl\d+)?',row['id'])
 if m:
  p=g['pool'][f'{m.group(1)}:{m.group(2)}'];people.add(p['B_pid']);photos.add(g['photo'](p['B']))
 assert photos and people and not any(v.startswith('unmapped:') for v in photos),(row['id'],photos)
 return people,photos
TP=set();TF=set()
for row in train:
 ps,ph=resolve(row);TP|=ps;TF|=ph
cal=json.loads((a.prepared/'calibration_proposal.json').read_text());primary=json.loads((a.prepared/'primary_with_D_components.json').read_text());PP=set();PF=set()
for row in primary:
 ps,ph=resolve(row);PP|=ps;PF|=ph
errors=[];resolved=[]
for row in cal:
 ps,ph=resolve(row)
 overlaps={'training_person':sorted(ps&TP),'training_photo':sorted(ph&TF),'primary_person':sorted(ps&PP),'primary_photo':sorted(ph&PF)}
 if any(overlaps.values()):errors.append({'id':row['id'],**overlaps})
 resolved.append({'id':row['id'],'persons':sorted(ps),'photos':sorted(ph)})
assert not a.out.exists();a.out.mkdir(parents=True)
(a.out/'calibration_resolved_sources.json').write_text(json.dumps(resolved,indent=2)+'\n')
r={'status':'PASS' if not errors else 'FAIL','calibration_rows':len(cal),'training_rows':len(train),'training_persons_including_shape':len(TP),'training_raw_photos_including_shape':len(TF),'primary_persons_including_shape':len(PP),'overlaps':errors,'unresolved_rows':0,'source_sha256':g['sha'](source),'auditor_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'metadata_inputs':g['READ_FILES'],'calibration_sha256':g['sha'](a.prepared/'calibration_proposal.json'),'primary_sha256':g['sha'](a.prepared/'primary_with_D_components.json'),'resolved_sha256':g['sha'](a.out/'calibration_resolved_sources.json'),'limits':'Metadata/source-provenance check, not biometric guarantee of original database identity labels. Sourcephotos and geometry suppliers included. No images or detector scores read.'}
(a.out/'AUDIT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','calibration_rows','training_rows','training_persons_including_shape','training_raw_photos_including_shape','overlaps','unresolved_rows']}))
raise SystemExit(bool(errors))
