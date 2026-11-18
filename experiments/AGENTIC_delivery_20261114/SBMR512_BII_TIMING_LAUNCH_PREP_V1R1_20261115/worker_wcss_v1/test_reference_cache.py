"""Instrument actual Backend._references with generated containers; no numpy/torch/model imports."""
import math,pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from backend import Backend
from test_cpu import fixture
class Array:
 def __init__(self,values,dtype):self.values=values;self.dtype=dtype;self.shape=(len(values),)
 def tolist(self):return list(self.values)
 def __getitem__(self,i):return self.values[i]
class Container:
 def __init__(self,arrays):self.arrays=arrays;self.fetches={}
 def __enter__(self):return self
 def __exit__(self,*a):pass
 def __getitem__(self,k):self.fetches[k]=self.fetches.get(k,0)+1;return self.arrays[k]
class FakeNP:
 float32="float32"
 def __init__(self,containers):self.containers=containers;self.opens=[]
 def load(self,path,allow_pickle):assert allow_pickle is False;self.opens.append(path);return self.containers[path]
 def isfinite(self,x):return math.isfinite(x)
def backend():
 c,ids=fixture();b=Backend.__new__(Backend);b.context=c
 b.admission={"reference_paths":{"ab1x_eval":"E","tt1":"T"},"reference_manifest_sha256":{"ab1x_eval":"eval-sha","tt1":"tt1-sha"}}
 z={}
 for pop,name in (("ab1x_eval","E"),("tt1","T")):
  rows=c["ordered_context_rows"][pop];base=0 if pop=="ab1x_eval" else 1000
  z[name]=Container({"id":Array([r["id"] for r in rows],"str"),"logit":Array([float(i+base) for i in range(len(rows))],"float32"),"manifest_sha256":b.admission["reference_manifest_sha256"][pop]})
 b.np=FakeNP(z);return b,z
class References(unittest.TestCase):
 def test_eval_only_boundary_targets_open_eval_once_and_never_tt1(self):
  b,z=backend();r=b._references(["ab1x:64","ab1x:63"])
  self.assertEqual(r,{"ab1x:63":63.,"ab1x:64":64.})
  self.assertEqual(b.np.opens,["E"]);self.assertEqual(z["E"].fetches,{"id":1,"logit":1,"manifest_sha256":1});self.assertEqual(z["T"].fetches,{})
 def test_full_requested_containers_each_array_fetched_once_permutation_preserved_by_id(self):
  b,z=backend();ids=["tt1:64","ab1x:129","ab1x:64","tt1:0","ab1x:63"];r=b._references(ids)
  self.assertEqual([r[i] for i in ids],[1064.,129.,64.,1000.,63.])
  self.assertEqual(b.np.opens,["E","T"])
  for v in z.values():self.assertEqual(v.fetches,{"id":1,"logit":1,"manifest_sha256":1})
 def test_unrequested_container_canary_would_raise_if_opened(self):
  b,z=backend()
  class Forbidden:
   def __enter__(self):raise AssertionError("TT1 must not be opened")
  b.np.containers["T"]=Forbidden()
  self.assertEqual(b._references(["ab1x:0"]),{"ab1x:0":0.})
 def test_duplicate_unknown_schema_and_selected_nonfinite_failclosed(self):
  for mode in ("duplicate","unknown","ids","shape","nan"):
   b,z=backend();ids=["ab1x:63"]
   if mode=="duplicate":ids*=2
   if mode=="unknown":ids=["foreign:63"]
   if mode=="ids":z["E"].arrays["id"].values[0]="foreign"
   if mode=="shape":z["E"].arrays["logit"].shape=(1,)
   if mode=="nan":z["E"].arrays["logit"].values[63]=float("nan")
   with self.assertRaises(AssertionError):b._references(ids)
 def test_empty_targets_opens_no_container(self):
  b,z=backend();self.assertEqual(b._references([]),{});self.assertEqual(b.np.opens,[])
if __name__=="__main__":unittest.main()
