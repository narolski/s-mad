import hashlib,json,pathlib,sys,tarfile
p=pathlib.Path(sys.argv[1]);r=json.loads(pathlib.Path(sys.argv[2]).read_text());h=hashlib.sha256()
with p.open('rb') as f:
 for block in iter(lambda:f.read(4<<20),b''):h.update(block)
assert h.hexdigest()==r['hn_overlay_sha256']
with tarfile.open(p) as t:
 names=[]
 for m in t.getmembers():
  assert m.isfile() and not m.issym() and not m.islnk()
  q=pathlib.PurePosixPath(m.name);assert not q.is_absolute() and '..' not in q.parts
  assert m.name=='pn1/HNSUMS' or m.name in ('pn1/data/manifests/train_HN_matched.csv','pn1/data/manifests/train_HN_self.csv') or (m.name.startswith('pn1/data/train/hn_native/') and m.name.endswith('.png'))
  names.append(m.name)
 assert len(names)==len(set(names))==375
print('HN_OVERLAY_VERIFIED')
