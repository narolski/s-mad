"""Synthetic fixtures only. No actual photos/checkpoints/torch/CUDA; temporary generated PNGs removed."""
import ast
from contextlib import nullcontext
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
import contracts as K
import construct_driver as D
import numeric_worker as N

ROOT=Path('/home/narolski/smad-next')
CONSTRUCTOR=ROOT/'src/VIS3/seam_v1/construction.py'
REGISTERED='/mnt/t7/smad_next/PN1/fs_tree/pn1/code/morphmamba/data/selfblend.py'
REFERENCE=ROOT/'src/VIS2/v1/occlusion_worker.py'


class Generated(unittest.TestCase):
    def setUp(self):
        self.module=K.load(CONSTRUCTOR,'frozen_constructor');self.ns=self.module.load_registered(REGISTERED)

    def test_capture_metadata_and_math_unchanged(self):
        a=np.full((512,512,3),80,np.uint8);b=np.full_like(a,170)
        result,alpha,plan,records=D.construct_record([a,b],self.module,self.ns)
        original,origalpha,_=self.module.construct_pair(a,b,self.ns)
        self.assertTrue(all(np.array_equal(result[x],original[x]) for x in K.IDS));self.assertTrue(np.array_equal(alpha,origalpha))
        self.assertEqual(records[0]['shift_xy'],[-1,-19]);self.assertEqual(records[1]['feather_sigma'],11)
        self.assertEqual(records[0]['input_rgb_raw_sha256'],K.rawsha(a));self.assertNotEqual(records[0]['transformed_source_rgb_raw_sha256'],records[1]['transformed_source_rgb_raw_sha256'])
        self.assertTrue((a==80).all());self.assertEqual(K.geometry(alpha,self.module)['K'],4)

    def test_changed_alpha_rejected(self):
        _,c=self.module.capture_registered(np.zeros((512,512,3),np.uint8),self.ns)
        a=c['alpha'].copy();a[0,0,0]=.01
        with self.assertRaises(ValueError):K.geometry(a,self.module)

    def test_lossless_generated_png_createonly_and_exact_schema(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'synthetic.png';a=np.full((512,512,3),101,np.uint8)
            D.lossless(p,a);self.assertTrue(np.array_equal(D.exact_rgb(p),a))
            with self.assertRaises(FileExistsError):D.lossless(p,a)
            bad=Path(tmp)/'gray.png';Image.fromarray(np.zeros((512,512),np.uint8)).save(bad)
            with self.assertRaises(ValueError):D.exact_rgb(bad)

    def test_regional_indices_means_individual_not_simultaneous(self):
        rows=[{'input_id':i,'fill_uint8':f,'cell':j,'delta_logit':float(j)} for i in K.IDS for f,j in K.tasks('full')]
        means=K.regional_means(rows,'full');self.assertEqual(len(means),8)
        self.assertEqual(means[0]['mean_boundary_delta_z'],7.5);self.assertEqual(means[0]['mean_surround_delta_z'],31.5)
        self.assertEqual(len(rows),512);self.assertEqual(len(K.tasks('smoke'))*4,48)
        self.assertFalse(set(j for _,j in K.tasks('smoke'))&set(K.SEAM))
        with self.assertRaises(ValueError):K.regional_means(rows[:-1],'full')
        with self.assertRaises(ValueError):K.regional_means(rows+[rows[0]],'full')

    def test_json_createonly_and_nonfinite(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'record.json';K.write(p,{'status':'FAILED','error':'fixture'})
            self.assertEqual(K.read(p)['status'],'FAILED')
            with self.assertRaises(FileExistsError):K.write(p,{})
            with self.assertRaises(ValueError):K.write(Path(tmp)/'bad.json',{'value':float('nan')})

    def test_model_loading_ast_is_exact_old20statements(self):
        old=ast.parse(REFERENCE.read_text());main=next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name=='main')
        tr=next(n for n in main.body if isinstance(n,ast.Try));block=[]
        for n in tr.body:
            if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='ds' for x in n.targets):break
            block.append(n)
        new=ast.parse(Path(__file__).with_name('model_runtime.py').read_text());fn=next(n for n in new.body if isinstance(n,ast.FunctionDef))
        self.assertEqual(len(block),20)
        self.assertEqual(ast.dump(ast.Module(body=block,type_ignores=[]),include_attributes=False),ast.dump(ast.Module(body=fn.body[2:-1],type_ignores=[]),include_attributes=False))

    def test_cpu_authority_failure_precedes_any_pixels(self):
        with patch.object(sys,'argv',['construct_driver','--inventory','never.json','--release','absent.json']),patch.object(K,'authority',side_effect=ValueError('fixture: no grant')),patch.object(D,'exact_rgb') as rgb:
            with self.assertRaises(ValueError):D.main()
            rgb.assert_not_called()

    def test_numeric_authority_failure_precedes_any_admission(self):
        with patch.object(sys,'argv',['numeric_worker','--inventory','never.json','--release','absent.json','--model','A','--phase','smoke']),patch.object(K,'authority',side_effect=ValueError('fixture: no grant')),patch.object(N,'construction_admission') as admission:
            with self.assertRaises(ValueError):N.main()
            admission.assert_not_called()

    def test_cpu_main_generated_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);paths=[]
            for ident,value in [('00042_native',80),('00056_native',170)]:
                p=root/(ident+'.png');D.lossless(p,np.full((512,512,3),value,np.uint8))
                paths.append({'id':ident,'path':str(p),'sha256':K.sha(p)})
            inv={'constructor_packages':{},'construction_output':str(root/'out'),'construction_inputs':paths,
                 'constructor_path':str(CONSTRUCTOR),'registered_source_path':REGISTERED,'prereg_path':str(CONSTRUCTOR),'rights':[]}
            ip=root/'inventory.json';rp=root/'grant.json';K.write(ip,inv);K.write(rp,{'fixture':True})
            grant={'new_derivative_construction_allowed':True}
            with patch.object(sys,'argv',['construct_driver','--inventory',str(ip),'--release',str(rp)]),patch.object(K,'authority',return_value=(inv,grant)):
                D.main()
            out=Path(inv['construction_output']);receipt=K.read(out/'CONSTRUCTION_RECEIPT.json');roster=K.read(out/'DERIVED_INPUT_ROSTER.json')
            self.assertEqual([p['id'] for p in roster],K.IDS);self.assertEqual(len(receipt['per_source_captures']),2)
            self.assertEqual(K.sha(out/'actual_used_alpha.npy'),receipt['actual_alpha']['sha256'])
            self.assertEqual(receipt['numeric_admission'],'HOLD_OTHER_REVIEW_REQUIRED');self.assertFalse((out/'FAILED.json').exists())
            with self.assertRaises(FileExistsError):
                with patch.object(sys,'argv',['construct_driver','--inventory',str(ip),'--release',str(rp)]),patch.object(K,'authority',return_value=(inv,grant)):D.main()

    def test_numeric_all_three_full_finalize_with_generated_fake_runtime(self):
        # Entire numeric writer path, synthetic scalar stub; NEVER imports torch or opens images/weights.
        import model_runtime
        class Token:
            def __init__(self,v):self.v=v
            def unsqueeze(self,*a):return self
            def to(self,*a):return self
            def item(self):return self.v
        fakecuda=SimpleNamespace(synchronize=lambda:None,reset_peak_memory_stats=lambda:None,
                                 get_device_name=lambda i:'GENERATED_FIXTURE_NO_GPU',max_memory_allocated=lambda:0,max_memory_reserved=lambda:0)
        faketorch=SimpleNamespace(no_grad=nullcontext,cuda=fakecuda,equal=lambda a,b:a.v==b.v,__version__='GENERATED_NO_TORCH',version=SimpleNamespace(cuda=None))
        worker=K.load(REFERENCE,'fixture_reference_vis2')
        worker.prep=lambda a,res,t,n:Token(float(a[0,0,0])/255.)
        modelcode=SimpleNamespace(ImageItems=lambda *a,**kw:[(Token(100/255.),0)]*4)
        a=np.full((512,512,3),100,np.uint8)
        _,capture=self.module.capture_registered(a,self.ns);alpha=capture['alpha']
        roster=[{'id':ident,'path':'GENERATED_'+ident,'sha256':'fixture','rgb_raw_sha256':K.rawsha(a)} for ident in K.IDS]
        anchors=[{'id':ident,'path':'GENERATED_'+ident,'sha256':'fixture'} for ident in ['00042_native','00042_history','00056_native','00056_history']]
        receipt={'derivative_roster_path':'GENERATED_ROSTER','actual_alpha':{'path':'GENERATED_ALPHA','sha256':'fixture'},'per_source_captures':[]}
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);review=root/'smoke_review.json'
            K.write(review,{'decision':'GO_VIS3_FULL_NUMERIC','author':'fixtureauthor','reviewer':'other','models':['selfmad_hrnet_w18','A','B'],
                            'inventory_sha256':'fixture','derivative_roster_sha256':'fixture','generated_regional_indexing_verified':True,
                            'smoke_result_sha256':{x:'fixture' for x in ['selfmad_hrnet_w18','A','B']}})
            inv={'experiment':'GENERATED_NUMERIC_FIXTURE_NOT_REAL','numeric_output':str(root/'numeric'),'environment':{'packages':{},'python':'3.12.3'},
                 'anchor_inputs':anchors,'models':{x:{'checkpoints':[]} for x in ['selfmad_hrnet_w18','A','B']},'constructor_path':str(CONSTRUCTOR),'reference_worker':str(REFERENCE),
                 'baseline_logits':{x:{p['id']:100/255. for p in anchors} for x in ['selfmad_hrnet_w18','A','B']}}
            grant={'new_derived_image_numeric_allowed':True,'original_four_anchor_inference_allowed':True,'smoke_postreview_path':str(review),
                   'smoke_postreview_sha256':'fixture','construction_receipt_path':'GENERATED_RECEIPT'}
            total=0;original_load=K.load
            def source_load(path,name):
                if path==str(REFERENCE):return worker
                return original_load(path,name)
            for modelname in ['selfmad_hrnet_w18','A','B']:
                with patch.object(sys,'argv',['numeric_worker','--inventory','fixture','--release','fixture','--model',modelname,'--phase','full']),patch.object(K,'authority',return_value=(inv,grant)),patch.object(N,'construction_admission',return_value=(receipt,roster)),patch.object(K,'sha',return_value='fixture'),patch.object(K,'load',side_effect=source_load),patch.object(D,'exact_rgb',return_value=a),patch.object(np,'load',return_value=alpha),patch.object(model_runtime,'load_runtime',return_value=(None,lambda x:x,224,modelcode,faketorch,np)):
                    N.main()
                out=root/'numeric'/'full'/modelname;result=K.read(out/'RESULT.json')
                self.assertEqual(len(result['responses']),512);self.assertEqual(len(result['regional_means']),8)
                self.assertEqual(result['inputs_ids'],K.IDS);self.assertIsNone(result['threshold']);self.assertFalse((out/'FAILED.json').exists())
                self.assertTrue((out/'SHA256.json').exists());total+=len(result['responses'])
            self.assertEqual(total,1536)

    def test_real_authority_rejects_wrong_phase_and_same_reviewer(self):
        with tempfile.TemporaryDirectory() as tmp:
            ip=Path(tmp)/'inventory.json';rp=Path(tmp)/'release.json'
            K.write(ip,{'experiment':'VIS3_CONTROLLED_SOFT_SPLICE_V2'})
            K.write(rp,{'issued_by':'root','phase':'full','decision':'GO_VIS3_PRIVATE_NUMERIC_FULL'})
            with self.assertRaises(ValueError):K.authority(ip,rp,'construct')
            rp2=Path(tmp)/'release2.json'
            K.write(rp2,{'issued_by':'root','phase':'construct','decision':'GO_VIS3_PRIVATE_CPU_CONSTRUCTION','author':'same','reviewer':'same'})
            with self.assertRaises(ValueError):K.authority(ip,rp2,'construct')

    def test_numeric_main_failure_has_durable_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            inv={'numeric_output':str(Path(tmp)/'numeric'),'environment':{'packages':{},'python':'3.12.3'},'anchor_inputs':[{'path':'NOT_A_REAL_IMAGE','sha256':'x'}]}
            grant={'new_derived_image_numeric_allowed':True,'original_four_anchor_inference_allowed':True}
            receipt={'derivative_roster_path':'fixture'}
            with patch.object(sys,'argv',['numeric_worker','--inventory','fixture','--release','fixture','--model','A','--phase','smoke']),patch.object(K,'authority',return_value=(inv,grant)),patch.object(N,'construction_admission',return_value=(receipt,[])),patch.object(K,'sha',return_value='fixture'):
                with self.assertRaises(ValueError):N.main()
            out=Path(inv['numeric_output'])/'smoke'/'A'
            self.assertTrue((out/'FAILED.json').exists());self.assertFalse((out/'RESULT.json').exists())

    def test_cpu_main_failure_has_durable_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            inv={'constructor_packages':{},'construction_output':str(Path(tmp)/'out'),'construction_inputs':[{'path':'NOT_A_REAL_IMAGE','sha256':'x'}]}
            grant={'new_derivative_construction_allowed':True}
            with patch.object(sys,'argv',['construct_driver','--inventory','fixture','--release','fixture']),patch.object(K,'authority',return_value=(inv,grant)),patch.object(K,'sha',return_value='fixture'),patch.object(D,'exact_rgb') as rgb:
                with self.assertRaises(ValueError):D.main()
                rgb.assert_not_called()
            out=Path(inv['construction_output']);self.assertTrue((out/'STARTED.json').exists());self.assertTrue((out/'FAILED.json').exists());self.assertFalse((out/'CONSTRUCTION_RECEIPT.json').exists())


if __name__=='__main__':unittest.main()
