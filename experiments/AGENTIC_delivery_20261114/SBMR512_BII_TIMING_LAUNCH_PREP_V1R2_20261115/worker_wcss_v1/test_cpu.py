"""Generated toy backends/AST/metadata only; never imports model backend."""
import ast,copy,json,pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from engine import run,mapping
from design import SPECS,work_counts
HERE=pathlib.Path(__file__).resolve().parent
def fixture():
 rows={p:[dict(id=str(i),path=p+"/"+str(i),label=str(i%2)) for i in range(n)] for p,n in (("ab1x_eval",130),("tt1",70))}
 chosen=[("tt1",64),("ab1x_eval",63),("ab1x_eval",64),("ab1x_eval",129),("tt1",0)]
 ids=[("ab1x:" if p=="ab1x_eval" else "tt1:")+str(i) for p,i in chosen]
 maps=[dict(cross_id=c,population=p,index=i,batch=i//64,offset=i%64,path=rows[p][i]["path"],label=rows[p][i]["label"]) for c,(p,i) in zip(ids,chosen)]
 return dict(ordered_context_rows=rows,target_mapping=maps[::-1]),ids
class Toy:
 def __init__(self,c,gate=True,mutation=False):self.c=c;self.gate=gate;self.mutation=mutation;self.events=[];self.specs=[];self.state=0
 def set_spec(self,s):self.specs.append(s)
 def state_digest(self):return self.state
 def batches(self,p):
  for a in range(0,len(self.c["ordered_context_rows"][p]),64):yield a,min(a+64,len(self.c["ordered_context_rows"][p])),(p,a,min(a+64,len(self.c["ordered_context_rows"][p])))
 def native_host(self,x):
  p,a,b=x;self.events.append(("native_host",p,a));return None,[float(i+(1000 if p=="tt1" else 0)) for i in range(a,b)]
 def flip_tta_host_discard(self,x,l0):
  self.events.append(("flip_tta_host_discard",x[0],x[1]))
  if self.mutation:self.state+=1
 def native_reference_equal(self,ids,values):self.events.append(("gate",));return self.gate
class Producer(unittest.TestCase):
 def test_permuted_mapping_crossorder_and_batchboundaries_all14(self):
  c,ids=fixture();b=Toy(c);out=run(c,ids,b)
  self.assertEqual(len(out),14);self.assertEqual(out[0],[1064.,63.,64.,129.,1000.])
  self.assertTrue(all(v==out[0] for v in out));self.assertEqual(b.specs,list(SPECS))
  expected=[("native_host","ab1x_eval",0),("flip_tta_host_discard","ab1x_eval",0),("native_host","ab1x_eval",64),("flip_tta_host_discard","ab1x_eval",64),("native_host","ab1x_eval",128),("flip_tta_host_discard","ab1x_eval",128),("native_host","tt1",0),("native_host","tt1",64),("gate",)]
  self.assertEqual(b.events[:9],expected)
 def test_reference_mismatch_aborts_before_perturbation(self):
  c,ids=fixture();b=Toy(c,gate=False)
  with self.assertRaises(AssertionError):run(c,ids,b)
  self.assertEqual(b.specs,[SPECS[0]])
 def test_model_state_mutation_refused(self):
  c,ids=fixture()
  with self.assertRaises(AssertionError):run(c,ids,Toy(c,mutation=True))
 def test_duplicate_missing_wrongpath_or_offset_refused(self):
  for kind in ("duplicate","missing","wrongpath","offset"):
   c,ids=fixture()
   if kind=="duplicate":c["target_mapping"].append(copy.deepcopy(c["target_mapping"][0]))
   if kind=="missing":c["target_mapping"].pop()
   if kind=="wrongpath":c["target_mapping"][0]["path"]="foreign"
   if kind=="offset":c["target_mapping"][0]["offset"]=999
   with self.assertRaises(AssertionError):mapping(c,ids)
 def test_full_real_metadata_mapping_no_payload(self):
  auth=json.loads((HERE/"AUTHORITY.json").read_text())
  p=HERE.parents[2]/"experiments/RZ1_input-resolution-and-resize/sbmr512_bii_producer_v1r1_20261114/FULL_CONTEXT_BINDING.json"
  c=json.loads(p.read_text());m=mapping(c,auth["cross_ids"]);self.assertEqual(len(m),13771)
  w=work_counts();self.assertEqual(w["total_samples"],5889030);self.assertEqual(w["total_calls"],92120)
 def test_runtime_source_hostsync_and_no_broad_main_or_scientific_metrics(self):
  s=(HERE/"backend.py").read_text()
  self.assertIn("return l0,l0.cpu().tolist()",s)
  self.assertIn("(t.sigmoid(l0)+t.sigmoid(l1))/2).cpu().tolist()",s)
  self.assertNotIn("rz1_score.main",s);self.assertNotIn("torch.save",s);self.assertNotIn("train_acc_rule0",s)
  t=ast.parse((HERE/"produce.py").read_text());main=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=="main")
  source=ast.unparse(main);self.assertLess(source.index("authorize("),source.index("CLAIM.json"));self.assertLess(source.index("CLAIM.json"),source.index("from backend import Backend"))
 def test_unsigned_release_and_unknown_admission_refused_before_model_import(self):
  import produce
  for mode in ("timing","full"):
   with self.assertRaises(AssertionError):produce.authorize(dict(decision="PROPOSED"),{},mode,408,HERE)
if __name__=="__main__":unittest.main()
