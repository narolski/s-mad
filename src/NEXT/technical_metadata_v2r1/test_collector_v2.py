"""Synthetic-only tests; never reference production archive paths."""
import contextlib,hashlib,io,json,pathlib,tempfile,tarfile,unittest
from unittest.mock import patch
import technical_collector_v2 as c


class CollectorTests(unittest.TestCase):
    def run_archive(self,entries,members,alter_hash=False,truncate=False):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d).resolve()/'synthetic.tar'
            with tarfile.open(p,'w') as tf:
                for name,raw,typ in entries:
                    info=tarfile.TarInfo(name);info.type=typ;info.size=len(raw) if typ==tarfile.REGTYPE else 0
                    if typ in (tarfile.SYMTYPE,tarfile.LNKTYPE):info.linkname='outside'
                    tf.addfile(info,io.BytesIO(raw) if typ==tarfile.REGTYPE else None)
            if truncate:p.write_bytes(p.read_bytes()[:520])
            h=hashlib.sha256(p.read_bytes()).hexdigest()
            return c.collect_archive({'archive':str(p),'sha256':'0'*64 if alter_hash else h,'members':members})

    def test_selective_canaries(self):
        schema={'seed':{'type':'int','equals':408},'models':{'*':{'gate':{'type':'str','equals':'passed'}}}}
        for field in ['EER','AUC','APCER','BPCER','val_metrics','scores','logits','threshold','accuracy']:
            outputs=[]
            for number in [0.123456789,987654.321]:
                raw=json.dumps({'seed':408,field:[number,{'loss':number}],'models':[{'gate':'passed',field:number}]}).encode()
                out=c.inspect_member(raw,{'kind':'json','schema':schema});outputs.append(out)
                self.assertNotIn(str(number),json.dumps(out))
            self.assertEqual(*outputs)

    def test_unselected_scalar_not_decoded(self):
        original=json.loads
        def guarded(text,*a,**kw):
            self.assertNotIn('987654321',text)
            return original(text,*a,**kw)
        with patch.object(c.json,'loads',guarded):
            self.assertEqual(c.SelectiveJSON(b'{"seed":408,"AUC":987654321,"scores":[987654321]}').parse({'seed':{'type':'int'}}),{'seed':408})

    def test_duplicates_unknown_nested(self):
        for raw in [b'{"seed":408,"seed":409}',b'{"AUC":{"x":1,"x":2}}']:
            with self.assertRaisesRegex(c.Refused,'JSON_DUPLICATE'):c.SelectiveJSON(raw).parse({'seed':{'type':'int'}})

    def test_json_type_encoding_and_syntax(self):
        out=c.inspect_member(b'{"seed":true}',{'kind':'json','schema':{'seed':{'type':'int','equals':408}}})
        self.assertFalse(out['checks']['seed']['type_ok'])
        for raw in [b'\xff',b'{"x":',b'{"x":"bad\\q"}',b'{"x":NaN}',b'[]garbage']:
            with self.assertRaises(c.Refused):c.SelectiveJSON(raw).parse({})

    def test_mixed_txt_canaries(self):
        specs=[({'kind':'loss'},'loss=0.5\n'),({'kind':'env','expected':{'ARM':'Sb','SEED':408,'TASK':'AB1_Sb_s408'}},'ARM=Sb\nSEED=408\nTASK=AB1_Sb_s408\n'),({'kind':'tokens','expected':{'steps':['6250']}},'steps 6250\n'),({'kind':'gpu'},'NVIDIA H100\n'),({'kind':'guard'},'RZ1 GUARD pre ok\nRZ1 GUARD post ok\n')]
        for spec,base in specs:
            expected=None if spec['kind']=='loss' else c.inspect_member(base.encode(),spec)
            for n in ['0.123456789','987654.321']:
                text=base+'AUC '+n+' EER '+n+' APCER '+n+' BPCER '+n+'\nval_loss='+n+'\nval_metrics={"scores":['+n+']}\n'
                actual=c.inspect_member(text.encode(),spec)
                if expected is None:expected=actual
                self.assertEqual(actual,expected)

    def test_loss_nonfinite_and_ambiguous(self):
        self.assertFalse(c.inspect_member(b'loss=nan',{'kind':'loss'})['native_fit']['all_finite'])
        self.assertTrue(c.inspect_member(b'val_loss=nan',{'kind':'loss'})['presence'])
        self.assertEqual(c.inspect_member(b'epoch 1 loss=0.2',{'kind':'loss'})['native_fit']['status'],'PASS')

    def test_no_npz_access(self):
        members={'x/meta.json':{'kind':'json','schema':{'seed':{'type':'int','equals':408}}}}
        original=tarfile.TarFile.extractfile
        def guarded(tf,member):
            self.assertEqual(member.name,'x/meta.json')
            return original(tf,member)
        with patch.object(tarfile.TarFile,'extractfile',guarded):
            out=self.run_archive([('x/meta.json',b'{"seed":408}',tarfile.REGTYPE),('x/scores.npz',b'CANARY987654321',tarfile.REGTYPE),('x/weights.pt',b'CANARY987654321',tarfile.REGTYPE)],members)
        self.assertNotIn('987654321',json.dumps(out));self.assertEqual(out['status'],'COLLECTED_TECHNICAL_ONLY')

    def test_tar_safety(self):
        for name,typ,code in [('../bad',tarfile.REGTYPE,'TAR_PATH'),('/bad',tarfile.REGTYPE,'TAR_PATH'),('link',tarfile.SYMTYPE,'TAR_TYPE'),('hard',tarfile.LNKTYPE,'TAR_TYPE'),('device',tarfile.CHRTYPE,'TAR_TYPE')]:
            self.assertEqual(self.run_archive([(name,b'',typ)],{})['reason'],code)
        out=self.run_archive([('x',b'',tarfile.REGTYPE),('./x',b'',tarfile.REGTYPE)],{})
        self.assertEqual(out['reason'],'TAR_DUPLICATE')

    def test_hash_missing_and_truncated(self):
        self.assertEqual(self.run_archive([],{},alter_hash=True)['reason'],'ARCHIVE_HASH')
        out=self.run_archive([],{'missing.json':{'kind':'json','schema':{}}})
        self.assertEqual(out['members']['missing.json']['reason'],'MEMBER_MISSING')
        out=self.run_archive([('x',b'a'*2000,tarfile.REGTYPE)],{'x':{'kind':'gpu'}},truncate=True)
        self.assertEqual(out['status'],'HOLD')

    def test_caps(self):
        with patch.object(c,'MAX_MEMBER',4):
            out=self.run_archive([('x',b'12345',tarfile.REGTYPE)],{'x':{'kind':'gpu'}})
            self.assertEqual(out['reason'],'MEMBER_SIZE')
        with patch.object(c,'MAX_TOTAL',4):
            out=self.run_archive([('x',b'123',tarfile.REGTYPE),('y',b'123',tarfile.REGTYPE)],{'x':{'kind':'gpu'},'y':{'kind':'gpu'}})
            self.assertEqual(out['reason'],'PARSE_BUDGET')

    def test_sanitized_failures(self):
        raw=b'{"seed":"CANARY987654321","AUC":'
        out=self.run_archive([('x',raw,tarfile.REGTYPE)],{'x':{'kind':'json','schema':{'seed':{'type':'int'}}}})
        self.assertEqual(out['members']['x']['reason'],'JSON_SYNTAX')
        self.assertNotIn('CANARY',json.dumps(out))

    def test_status_failures_retained(self):
        schema={'models':{'*':{'name':{'type':'str','one_of':['a','b']},'gate':{'type':'str','equals':'passed'}}}}
        out=c.inspect_member(b'{"models":[{"name":"a","gate":"failed","AUC":0.99999},{"name":"b","gate":"passed"}]}',{'kind':'json','schema':schema})
        models=out['checks']['models'];self.assertEqual(models['count'],2)
        self.assertFalse(models['items'][0]['gate']['equals_expected']);self.assertTrue(models['items'][1]['gate']['equals_expected'])

    def test_release_required_before_archive_access(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d);(p/'packet').write_text('{}');(p/'release').write_text('{}')
            with patch('sys.argv',['collector','--packet',str(p/'packet'),'--release',str(p/'release'),'--output',str(p/'out')]),patch.object(c,'collect_archive',side_effect=AssertionError('must not run')),contextlib.redirect_stdout(io.StringIO()) as stdout:
                self.assertEqual(c.main(),2)
            self.assertEqual(stdout.getvalue(),'HOLD RELEASE_REQUIRED\n');self.assertFalse((p/'out').exists())

    def test_source_import_boundary(self):
        source=pathlib.Path(c.__file__).read_text()
        for token in ['import numpy','import torch','import native_adapters','import read_selection','np.load','extractall(']:self.assertNotIn(token,source)


if __name__=='__main__':unittest.main()
