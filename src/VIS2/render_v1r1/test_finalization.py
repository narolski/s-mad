"""Generated-only finalization: mocked canvas, no valid PDF/SVG/RGB ever produced."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

spec=importlib.util.spec_from_file_location('contract_fixture',Path(__file__).with_name('test_contract.py'))
F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
M=F.M


class Writer(unittest.TestCase):
    def test_create_only_and_nonfinite(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'new.json';M.write(p,{'ok':True});before=p.read_bytes()
            with self.assertRaises(FileExistsError):M.write(p,{'overwrite':True})
            self.assertEqual(p.read_bytes(),before)
            q=Path(td)/'bad.json'
            with self.assertRaises(ValueError):M.write(q,{'nan':float('nan')})
            self.assertFalse(q.exists())


class Alpha(unittest.TestCase):
    def test_real_reportlab_state_without_paint_or_save(self):
        try:
            from reportlab.pdfgen.canvas import Canvas
            from reportlab.lib.colors import Color
        except ImportError:self.skipTest('ReportLab unavailable; requires bundled4.4.9 runtime')
        b=io.BytesIO();c=Canvas(b,pagesize=(100,100))
        # State setters only: no rect/drawImage/showPage/save call, no PDF bytes.
        for alpha in (0.,.45,1.):
            M.set_overlay_fill(c,Color,(.2,.3,.4),alpha)
            self.assertEqual(c._extgstate.getValue('ca'),alpha)
        self.assertEqual(b.getvalue(),b'')


class FakeCanvas:
    instances=[]
    virtual=None
    def __init__(self,path,**kw):
        self.path=Path(path);self.alpha=1.;self.stack=[];self.rects=[];self.pages=0;self.images=0
        self.instances.append(self)
    def setFillColor(self,color):self.alpha=color.alpha  # exact relevant ReportLab4.4.9 reset
    def setFillAlpha(self,alpha):self.alpha=alpha
    def saveState(self):self.stack.append(self.alpha)
    def restoreState(self):self.alpha=self.stack.pop()
    def rect(self,x,y,w,h,**kw):self.rects.append((x,y,w,h,self.alpha))
    def setTitle(self,*a):pass
    def setAuthor(self,*a):pass
    def setFont(self,*a):pass
    def drawString(self,*a):pass
    def drawImage(self,*a,**kw):self.images+=1
    def beginPath(self):return mock.Mock()
    def clipPath(self,*a,**kw):pass
    def setLineWidth(self,*a):pass
    def setStrokeColor(self,*a):pass
    def line(self,*a):pass
    def showPage(self):self.pages+=1
    def save(self):self.virtual[self.path]=b'GENERATED_MOCK_CANVAS_NOT_A_PDF'


class Finalization(unittest.TestCase):
    def run_generated(self,td,fail=False):
        try:import reportlab
        except ImportError:self.skipTest('E2E uses bundled ReportLab module interfaces, no rendering')
        root=Path(td);data=root/'generated';data.mkdir();out=root/'out'
        virtual={};FakeCanvas.virtual=virtual;FakeCanvas.instances=[]
        real_sha=M.sha;real_write=M.write;real_text=Path.write_text
        models={};roster=[]
        for model in M.MODELS:
            r=F.fixture();r['model']=model;r['res']=384 if model==M.MODELS[0] else 224
            if model==M.MODELS[0]:
                for row in r['responses']:row.update(occluded_logit=0.,delta_logit=0.)
            p=data/model/'RESULT.json';p.parent.mkdir();p.write_text(json.dumps(r))
            roster.append({'model':model,'replica_relpath':model+'/RESULT.json','sha256':real_sha(p)})
        (data/'inputs').mkdir();inputs=[]
        for id in M.IDS:
            p=data/'inputs'/(id+'.png');p.write_bytes(b'GENERATED_NON_RGB_SENTINEL_'+id.encode())
            inputs.append({'id':id,'replica_name':id+'.png','sha256':real_sha(p)})
        font=root/'not-a-font';font.write_bytes(b'GENERATED_FONT_SENTINEL')
        cfg={'numeric_inventory_sha256':'generated-only','baseline_anchors':F.ANCHORS,'inputs':inputs,
             'fonts':{'regular':str(font),'bold':str(font),'regular_sha256':real_sha(font),'bold_sha256':real_sha(font)},
             'labels':{m:m for m in M.MODELS},'overlay_alpha':.45,'source_credits':{},'render_mode':'source_overlay',
             'credits_short':{k:'Generated fixture, no real photograph' for k in M.KEYS},
             'history_facts':{'00042':'1024→265→alignment512','00056':'1024→249→alignment512'}}
        grant={'full_result_roster':roster};conf=root/'config.json';rel=root/'grant.json'
        conf.write_text('{}');rel.write_text('{}')
        def safe_sha(p):
            p=Path(p)
            if p in virtual:return M.hashlib.sha256(virtual[p]).hexdigest()
            return real_sha(p)
        def text_to_memory(p,text,*a,**kw):
            if p.suffix=='.svg':virtual[p]=text.encode();return len(text)
            return real_text(p,text,*a,**kw)
        def checked_write(p,obj):
            if fail and Path(p).name=='CELL_RENDER_RECORDS.json':raise OSError('generated finalization failure')
            return real_write(p,obj)
        argv=['render','--config',str(conf),'--release',str(rel),'--data-root',str(data),'--out-root',str(out)]
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(M,'authorize',return_value=(cfg,grant)))
            stack.enter_context(mock.patch.object(M,'sha',side_effect=safe_sha))
            stack.enter_context(mock.patch.object(M,'write',side_effect=checked_write))
            stack.enter_context(mock.patch.object(sys,'argv',argv))
            stack.enter_context(mock.patch('reportlab.pdfgen.canvas.Canvas',FakeCanvas))
            stack.enter_context(mock.patch('reportlab.pdfbase.pdfmetrics.registerFont'))
            stack.enter_context(mock.patch('reportlab.pdfbase.pdfmetrics.stringWidth',side_effect=lambda s,f,z:len(s)*z*.35))
            stack.enter_context(mock.patch('reportlab.pdfbase.ttfonts.TTFont',return_value=object()))
            stack.enter_context(mock.patch('reportlab.lib.utils.ImageReader',side_effect=lambda p:('NON_RGB_SENTINEL',p)))
            stack.enter_context(mock.patch.object(Path,'write_text',text_to_memory))
            if fail:
                with self.assertRaises(OSError):M.main()
            else:
                captured=io.StringIO()
                with contextlib.redirect_stdout(captured):M.main()
                self.assertIn('VIS2_ACTUAL_MEASURED_PRIVATE_RENDER_COMPLETE',captured.getvalue())
        # Any PDF/SVG exists only as invalid sentinel/string in memory, never a document on disk.
        self.assertFalse(list(out.glob('*.pdf')));self.assertFalse(list(out.glob('*.svg')))
        return cfg,out,virtual

    def test_complete_flow_3072_records_and_alpha_history(self):
        with tempfile.TemporaryDirectory() as td:
            cfg,out,virtual=self.run_generated(td)
            records=json.loads((out/'CELL_RENDER_RECORDS.json').read_text())
            self.assertEqual(len(records),3072)
            self.assertEqual(len([p for p in virtual if p.suffix=='.svg']),12)
            self.assertEqual(len([p for p in virtual if p.suffix=='.pdf']),2)
            self.assertEqual([c.pages for c in FakeCanvas.instances],[6,6])
            self.assertEqual(json.loads((out/'COMPLETE.json').read_text())['status'],'COMPLETE')
            man=json.loads((out/'MANIFEST.json').read_text())
            self.assertEqual(man['history_facts'],cfg['history_facts'])
            rects=[r for c in FakeCanvas.instances for r in c.rects if abs(r[2]-M.EDGE_MM/8*M.MM)<1e-9 and abs(r[3]-M.EDGE_MM/8*M.MM)<1e-9]
            self.assertEqual(len(rects),3072)
            self.assertEqual([r[4] for r in rects],[r['overlay_alpha'] for r in records])
            self.assertEqual(set(r['overlay_alpha'] for r in records),{0.,.45})
            svgtext=''.join(v.decode() for p,v in virtual.items() if p.suffix=='.svg')
            self.assertIn('opacity="0.0"',svgtext);self.assertIn('opacity="0.45"',svgtext)
            self.assertFalse((out/'FAILED.json').exists())

    def test_injected_failure_receipt_not_complete(self):
        with tempfile.TemporaryDirectory() as td:
            cfg,out,virtual=self.run_generated(td,fail=True)
            self.assertEqual(json.loads((out/'FAILED.json').read_text())['status'],'FAILED')
            self.assertFalse((out/'COMPLETE.json').exists());self.assertFalse((out/'MANIFEST.json').exists())


if __name__=='__main__':unittest.main()
