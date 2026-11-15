"""Generated scalar/metadata fixtures only. NO real RGB/results, PDFs or mock maps."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('renderer',Path(__file__).with_name('render_measured.py'))
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
ANCHORS={model:{id:0.0 for id in M.IDS} for model in M.MODELS}


def fixture():
    rows=[]
    for id in M.IDS:
        for fill in (0,128):
            for i in range(64):
                d=float(i%9-4)/10
                rows.append(dict(input_id=id,fill_uint8=fill,cell=i,row=i//8,col=i%8,native_y=(i//8)*64,native_x=(i%8)*64,native_area=4096,baseline_logit=0.0,occluded_logit=d,delta_logit=d))
    return dict(model=M.MODELS[0],experiment='VIS2_PRIVATE_OCCLUSION_V1',status='COMPLETE',phase='full',inventory_sha256='generated-only',inputs_ids=list(M.IDS),fills_uint8=[0,128],batch_size=1,res=384,threshold=None,decision_flips=None,source_pixels_exported=False,maps_rendered=False,noTTA=True,tf32_matmul=False,tf32_cudnn=False,gpu='NVIDIA GB10',torch='2.12.1+cu130',cuda='13.0',seam_masks='NONE_EXISTS_ON_THESE_GENUINE_PHOTOS; no seam localization claim',baseline_logits=[0.0]*4,responses=rows)


class Contract(unittest.TestCase):
    def valid(self,r):return M.validate_result(r,M.MODELS[0],'generated-only',ANCHORS)

    def test_complete512(self):
        self.assertEqual(len(self.valid(fixture())['values']),512)

    def test_missing_or_duplicate(self):
        for kind in ('missing','duplicate'):
            r=fixture()
            if kind=='missing':r['responses'].pop()
            else:r['responses'][-1]=r['responses'][0].copy()
            with self.assertRaises(ValueError):self.valid(r)

    def test_smoke_refused(self):
        r=fixture();r['phase']='smoke'
        with self.assertRaises(ValueError):self.valid(r)

    def test_nonfinite_boolean_refused(self):
        for bad in (float('nan'),float('inf'),True):
            r=fixture();r['responses'][0]['delta_logit']=bad
            with self.assertRaises(ValueError):self.valid(r)

    def test_wrong_delta_and_geometry(self):
        for field in ['delta_logit','native_x','native_area','fill_uint8']:
            r=fixture();r['responses'][0][field]=999
            with self.assertRaises(ValueError):self.valid(r)

    def test_global_scale_other_photo_other_fill(self):
        r=fixture();q=r['responses'][-1];q.update(occluded_logit=100.,delta_logit=100.)
        v=self.valid(r);self.assertEqual(v['limit'],100.)
        self.assertEqual(M.normalized(v['values'][M.IDS[0],0,0],v['limit']),-.004)

    def test_zero_limit_no_boost(self):
        r=fixture()
        for q in r['responses']:q.update(occluded_logit=0.,delta_logit=0.)
        v=self.valid(r);self.assertEqual(v['limit'],0.);self.assertEqual(M.normalized(0.,0.),0.)
        self.assertEqual(M.color(0.,0.),(1.,1.,1.))
        with self.assertRaises(ValueError):M.normalized(.1,0.)

    def test_tiny_real_limit_without_epsilon(self):
        self.assertEqual(M.normalized(1e-30,1e-30),1.)

    def test_no_clipping_or_per_panel_scale(self):
        with self.assertRaises(ValueError):M.normalized(2.,1.)

    def test_grayscale_sign_preserves_magnitude(self):
        self.assertEqual(M.color(-.2,1.,True),M.color(.2,1.,True))
        self.assertNotEqual(M.color(-.2,1.),M.color(.2,1.))

    def test_large_layout_inside_page(self):
        boxes=M.validate_layout();self.assertEqual(len(boxes),6)
        self.assertTrue(all(x['w']>=58 for x in boxes));self.assertGreaterEqual(M.MIN_FONT,8.2)
        self.assertEqual(M.WIDTH_MM,180);self.assertLessEqual(M.HEIGHT_MM,279.4)
        self.assertEqual(M.MAP_X,(17,105));self.assertEqual(M.MAP_Y,(100,173))

    def test_legacy_grant_rejected_before_real_data(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);(p/'config.json').write_text('{}')
            (p/'grant.json').write_text(json.dumps({'decision':'GO_PRIVATE_RESEARCH_RENDER_ONLY'}))
            with self.assertRaises(ValueError):M.authorize(p/'config.json',p/'grant.json',p/'absent-inputs',p/'absent-output')
            self.assertFalse((p/'absent-output').exists())

    def test_no_operational_threshold(self):
        r=fixture();r['threshold']=.5
        with self.assertRaises(ValueError):self.valid(r)

    def test_fabricated_seam_refused(self):
        r=fixture();r['seam_masks']='fake_face_hull'
        with self.assertRaises(ValueError):self.valid(r)


if __name__=='__main__':unittest.main()
