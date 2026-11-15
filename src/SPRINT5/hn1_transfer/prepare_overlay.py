"""Package verified native controls without reading any detector outputs."""
import argparse,csv,hashlib,io,json,pathlib,tarfile
ap=argparse.ArgumentParser();ap.add_argument('--controls',type=pathlib.Path,required=True);ap.add_argument('--out',type=pathlib.Path,required=True);a=ap.parse_args()
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r=json.loads((a.controls/'RECEIPT.json').read_text());assert r['status']=='PASS' and r['count']==r['completed']==124
assert sha(a.controls/'records.json')==r['records_sha256']
records=json.loads((a.controls/'records.json').read_text());assert len({x['host'] for x in records})==124
assert not a.out.exists();a.out.mkdir(parents=True)
fields='path,label,source,tool,arm,val,mixed,id,kind,db,hist'.split(',');rows={'matched':[],'self':[]};assets=[];pins={};contributors=[]
for x in records:
 assert x['status']=='PASS' and x['warps_per_layer']==1 and x['blend_weight']==.5
 assert x['source'] in ('feret','frgc')
 host=x['host'].replace(':','_');contributors.append({'host':x['host'],'partner':x['partner'],'db':x['source']})
 for kind,meta in [('P',x['common_positive']),('Nmatched',x['matched_negative']),('Nself',x['outputs']['Nself'])]:
  path=pathlib.Path(meta['path']);assert sha(path)==meta['sha256'];name=f'pn1/data/train/hn_native/{host}/{kind}.png';assets.append((name,path));pins[name]=meta['sha256']
 for arm,n in [('matched','Nmatched'),('self','Nself')]:
  for label,k in [(1,'P'),(0,n)]:
   rows[arm].append(dict(path=f'train/hn_native/{host}/{k}.png',label=label,source='smdd',tool='smdd',arm='smdd',val=0,mixed=0,id=f'hn_{host}_{k}',kind='lad_S4' if label else 'lad_S3',db=x['source'],hist='native'))
blobs={}
for arm,rr in rows.items():
 assert len(rr)==len({x['path'] for x in rr})==248 and sum(x['label'] for x in rr)==124
 assert sum(x['db']=='feret' for x in rr)==44
 f=io.StringIO(newline='');w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rr);raw=f.getvalue().encode();name=f'pn1/data/manifests/train_HN_{arm}.csv';blobs[name]=raw;pins[name]=hashlib.sha256(raw).hexdigest();(a.out/f'train_HN_{arm}.csv').write_bytes(raw)
assert [x for x in rows['matched'] if x['label']]==[x for x in rows['self'] if x['label']]
blobs['pn1/HNSUMS']=''.join(f'{h}  {name.removeprefix("pn1/")}\n' for name,h in sorted(pins.items())).encode()
with tarfile.open(a.out/'hn_native_overlay.tar','w') as t:
 for name,path in assets:t.add(path,arcname=name,recursive=False)
 for name,raw in blobs.items():
  info=tarfile.TarInfo(name);info.size=len(raw);t.addfile(info,io.BytesIO(raw))
report={'status':'PASS','scope':'training input packaging only','control_receipt_sha256':sha(a.controls/'RECEIPT.json'),'control_records_sha256':sha(a.controls/'records.json'),'overlay_sha256':sha(a.out/'hn_native_overlay.tar'),'rows_per_arm':248,'images_total':372,'positive_common_images':124,'source_rows_per_arm':{'feret':44,'frgc':204},'pins':pins,'contributors':contributors,'script_sha256':sha(__file__)}
(a.out/'OVERLAY_RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('pins','contributors')},indent=2))
