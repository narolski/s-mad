import hashlib,json,pathlib,tempfile,unittest
from assemble_receipt_roster import assemble,WANTED
class ReceiptFailures(unittest.TestCase):
 def fixture(self,p):
  files=[]
  for i,name in enumerate(WANTED):
   h=hashlib.sha256(("generated"+str(i)).encode()).hexdigest()
   (p/name).write_bytes(b"opaque-generated-fixture-not-read")
   side=p/(name+".sha256");side.write_text(h+"  "+name+"\n")
   files += [dict(name=name,size=(p/name).stat().st_size,sha256=h),dict(name=side.name,size=side.stat().st_size,sha256=hashlib.sha256(side.read_bytes()).hexdigest())]
  d=dict(files=files,remote_local_sidecar_equal=True,archive_members_opened=False,scientific_read_authorized=False)
  r=p/"COLLECTION_VERIFIED.json";r.write_text(json.dumps(d));return r,d
 def test_complete15_and_stable_seedarm_order(self):
  with tempfile.TemporaryDirectory() as td:
   r,d=self.fixture(pathlib.Path(td));x,p,m=assemble([r]);self.assertEqual(len(x),15);self.assertFalse(m);self.assertEqual(x[0]["task"],"SPRINT5_1_production_v3_bce_s501")
 def test_missing_duplicate_foreign_wronghash_untrusted_and_boolsize_refused(self):
  for mode in ("missing","duplicate","foreign","sidecarhash","untrusted","boolsize","dupdigest"):
   with self.subTest(mode=mode),tempfile.TemporaryDirectory() as td:
    r,d=self.fixture(pathlib.Path(td))
    if mode=="missing":d["files"]=d["files"][2:]
    if mode=="duplicate":d["files"].append(d["files"][0])
    if mode=="foreign":d["files"][0]["name"]="SPRINT5_1_production_v3_bce_s999.tar"
    if mode=="sidecarhash":d["files"][1]["sha256"]="0"*64
    if mode=="untrusted":d["remote_local_sidecar_equal"]=1
    if mode=="boolsize":d["files"][0]["size"]=True
    if mode=="dupdigest":d["files"][2]["sha256"]=d["files"][0]["sha256"]
    r.write_text(json.dumps(d))
    with self.assertRaises(AssertionError):assemble([r])
 def test_duplicate_receipt_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   r,d=self.fixture(pathlib.Path(td))
   with self.assertRaises(AssertionError):assemble([r,r])
 def test_draft_missing_explicit_not_silently_admitted(self):
  with tempfile.TemporaryDirectory() as td:
   r,d=self.fixture(pathlib.Path(td));d["files"]=d["files"][:-2];r.write_text(json.dumps(d))
   x,p,m=assemble([r],require_complete=False);self.assertEqual(len(x),14);self.assertEqual(len(m),1)
if __name__=="__main__":unittest.main()
