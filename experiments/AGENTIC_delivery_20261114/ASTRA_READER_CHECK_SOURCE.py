import json,hashlib,re,zipfile,collections,struct,subprocess
from pathlib import Path
D=Path(__file__).parent;A=D.parent/'typeset_review';H=lambda b:hashlib.sha256(b).hexdigest();load=lambda p:json.loads(p.read_text())
orig=load(A/'supplement_table_cells.json');src={f"{t['id']}:r{r}:c{c}":v for t in orig for r,row in enumerate([t['headers']]+t['rows']) for c,v in enumerate(row)}
j=load(D/'reader_content.json');cw=load(D/'source_crosswalk.json');canon={}
for t in j['tables']:
 for ri,row in enumerate([t['headers']]+t['rows']):
  r=0 if ri==0 else t.get('source_rows',list(range(1,len(t['rows'])+1)))[ri-1]
  for ci,v in enumerate(row):canon[f"{t['id']}:r{r}:c{t.get('source_columns',list(range(len(row))))[ci]}"]=v
seen=set();dedup=0;vectors=0;changes=[]
for x in cw['cells']:
 k=f"{x['source_table']}:r{x['source_row']}:c{x['source_column']}";assert k not in seen;seen.add(k);v=src[k];assert H(v.encode())==x['source_cell_sha256']
 if x['rule'].startswith('identical'):
  assert len(x['canonical'])==1;tar=x['canonical'][0];assert src[tar]==v and canon[tar]==v;dedup+=1
 elif x['rule'].startswith('ordered vector'):
  vv=[canon[c] for c in x['canonical']];assert len(vv)==8 and vv==v.split();vectors+=1
 elif x['rule']=='retained':
  tar=x['canonical'][0];assert tar in canon
  if canon[tar]!=v:changes.append([k,v,canon[tar]])
 else:assert x['source_row']==0 or x['source_column']==0
assert seen==set(src) and len(src)==2580 and dedup==205 and vectors==66
names=['pools_summary.md','result.md','tt1_read_tables.md','tt1_read_fs_tables.md'];paragraphs={p['id']:p for p in j['paragraphs']};diffs=[]
for x in cw['paragraphs']:
 lines=(A/names[x['source']-1]).read_text().splitlines();a,b=x['lines'];ls=lines[a-1:b];v='\n'.join(ls)
 # Ledger encodes original lines with a literal backslash-n separator.
 if H(v.encode())!=x['original_paragraph_sha256']:
  v='\\n'.join(ls);assert H(v.encode())==x['original_paragraph_sha256']
 if x['canonical'] in paragraphs:
  new=paragraphs[x['canonical']]['text']
  if v!=new:diffs.append({'id':x['canonical'],'old':v,'new':new,'disposition':x['disposition']})
 else:diffs.append({'id':x['canonical'],'old':v,'new':'[OMITTED/INDEX]','disposition':x['disposition']})
(D/'independent_redaction_diffs.json').write_text(json.dumps({'cells':changes,'paragraphs':diffs},indent=2))
Z=D.parents[1]/'outputs/smad_supplement_reader_anonymous_20261114.zip'
with zipfile.ZipFile(Z) as z:
 assert z.testzip() is None and len(z.infolist())==15 and not z.comment
 for f in z.infolist():
  assert f.date_time==(2000,1,1,0,0,0) and not f.extra and not f.comment
  assert '/' not in f.filename and '\\' not in f.filename
  data=z.read(f)
  if f.filename.endswith(('.json','.md','.tex','.py','.sty')):
   assert not re.search(rb'narolski|/home/|/Users/|/mnt/|gx10|ui\.wcss|GPU-[a-f0-9]|@gmail|USD',data,re.I),f.filename
  if f.filename.endswith('.png'):
   i=8
   while i<len(data):
    n=int.from_bytes(data[i:i+4],'big');typ=data[i+4:i+8];assert typ not in [b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME'];i+=12+n
for f in load(D/'READER_PACKAGE_MANIFEST.json')['files']:assert H((D/f['path']).read_bytes())==f['sha256']
report={'source_cells':len(seen),'exact_redirects':dedup,'vectors':vectors,'expanded_subcells':vectors*8,'changed_retained_cells':len(changes),'prose_ledger_entries':len(cw['paragraphs']),'prose_dispositions':dict(collections.Counter(x['disposition'] for x in cw['paragraphs'])),'zip_members':15,'zip_metadata_crc_text_png_scan':'PASS scoped patterns','pdf_sha256':H((D/'supplement_reader.pdf').read_bytes()),'zip_sha256':H(Z.read_bytes()),'crosswalk_sha256':H((D/'source_crosswalk.json').read_bytes())}
(D/'ASTRA_READER_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));print('CHANGEDCELLS',changes)
