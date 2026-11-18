"""Root-only post-native-close opaque bundling; no model decode or scientific admission."""
import pathlib,sys,json,tarfile,os
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import verify
from supervise import put

def main(seed):
 assert seed in range(401,406);j=verify.JOURNAL/('s%d'%seed);k=verify.ROOT/'logs/keep/ad5_full_math_v2_20261114'/('s%d'%seed)
 closed=json.loads((j/'ROOT_NATIVE_CLOSED.json').read_text());assert closed['root_confirmed_terminal'] is True and closed['seed']==seed and closed['claim_sha256']==verify.sha(j/'CLAIM.json')
 name=closed['native_receipt_file'];assert pathlib.Path(name).name==name and verify.sha(j/name)==closed['native_receipt_sha256']
 dest=verify.ROOT/'results/ad5_full_math_v2_20261114';dest.mkdir(exist_ok=True)
 path=dest/('NEW_LATE_B_s%d.tar'%seed)
 # Exclusive archive; failed partial archive is retained, never overwritten/retried automatically.
 with path.open('xb') as f:
  with tarfile.open(fileobj=f,mode='w') as tar:
   for root,prefix in ((k,'worker'),(j,'dispatch')):
    for p in sorted(root.rglob('*')):
     assert not p.is_symlink()
     if p.is_file():tar.add(p,arcname=prefix+'/'+str(p.relative_to(root)),recursive=False)
  f.flush();os.fsync(f.fileno())
 put(dest/('NEW_LATE_B_s%d.ARCHIVE.json'%seed),dict(seed=seed,archive=str(path),sha256=verify.sha(path),bytes=path.stat().st_size,native_state=closed['native_state'],scientific_admission=False,verified_arrival_at_gx10='NOT_ESTABLISHED_BY_ARCHIVE_CREATION'))
if __name__=='__main__':main(int(sys.argv[1]))
