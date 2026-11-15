import io,tarfile,tempfile,pathlib,json,hashlib,unittest,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import ad5_technical_core as C
from launch_inference import command
class Tests(unittest.TestCase):
 def test_only_selected_json_and_header(self):
  with tempfile.TemporaryDirectory() as td:
   p=pathlib.Path(td).resolve()/'fake.tar'
   with tarfile.open(p,'w') as t:
    for name,data in [('job.json',b'{"seed":401,"hidden_score":0.987}'),('40_backbone.pth',b'NOT_A_CHECKPOINT'),('scores.npz',b'NOT_SCIENTIFIC_DATA')]:
     m=tarfile.TarInfo(name);m.size=len(data);t.addfile(m,io.BytesIO(data))
   r=C.collect_archive({'archive':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'members':{'job.json':{'kind':'json','schema':{'seed':{'type':'int','equals':401}}},'40_backbone.pth':{'kind':'header'}}})
   self.assertEqual(r['members']['40_backbone.pth']['status'],'HEADER_ONLY')
   self.assertEqual(r['members']['job.json']['checks'],{'seed':{'type_ok':True,'equals_expected':True}})
   self.assertNotIn('hidden_score',json.dumps(r));self.assertNotIn('scores.npz',r['members'])
 def test_duplicate_json_rejected(self):
  with self.assertRaises(C.Refused): C.SelectiveJSON(b'{"seed":401,"seed":402}').parse({'seed':{'type':'int'}})
 def test_path_traversal_refused(self):
  with self.assertRaises(C.Refused): C.normalize('../epoch_100.tar')
 def test_scoped_command(self):
  s={'phase':'corrected_MAD22_and_approved_dev','admission':'OTHER_TECHNICAL_PASS_CHECKPOINT_AND_INPUTS','mode':'rel','resource':{'gpus':1,'seconds':600,'workers':1,'batch_size':32},'python':'/fake/python','wrapper':'/fake/ad5_score_athena.py','runtime_root':'/fake/runtime','site':'/fake/site','release_spec':'madation_vitb16','name':'madation_B_s401','weights':'/fake/model','manifest':'/fake/MAD22_only.csv','output':'/fake/newout','tag':'MAD22_B401'}
  a=command(s);self.assertIn('/fake/MAD22_only.csv',a);self.assertNotIn('allsets',str(a))
  s['phase']='RS1_allsets'
  with self.assertRaises(ValueError):command(s)
if __name__=='__main__':unittest.main()
