import ast
import importlib.util
import pathlib
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('probe', pathlib.Path(__file__).with_name('probe.py'))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)

class Fixtures(unittest.TestCase):
    def request(self, files=None, distributions=None):
        return dict(schema='SBMR512_ENV_SOURCE_REQUEST_V1', interpreter='/synthetic/python', interpreter_sha256='0'*64, distributions=distributions or [], files=files or [])
    def test_empty_source_fixture(self):
        r=self.request(); p.validate_request(r)
        receipt=p.collect(r, lambda _: self.fail('unexpected distribution access'))
        self.assertEqual(receipt['backend_defaults'], 'UNKNOWN')
        self.assertEqual(receipt['native_bytegate'], 'NOT_RUN')
    def test_explicit_source_pin(self):
        with tempfile.TemporaryDirectory() as t:
            f=pathlib.Path(t).resolve()/'generated.py'; f.write_text('GENERATED = True\n')
            r=self.request([dict(path=str(f), sha256=p.sha(f), bytes=f.stat().st_size, kind='python_source')])
            p.validate_request(r); self.assertEqual(len(p.collect(r)['installed_source_files']),1)
            f.write_text('changed\n')
            with self.assertRaises(ValueError): p.collect(r)
    def dist(self, root, name='torch'):
        meta=root/(name+'.dist-info')
        return dict(name=name, metadata_root=str(root),metadata_dir=str(meta),record_sha256='0'*64,record_bytes=0,metadata_sha256='0'*64,metadata_bytes=0)
    def test_missing_distribution_unknown(self):
        with tempfile.TemporaryDirectory() as t:
            r=self.request(distributions=[self.dist(pathlib.Path(t).resolve())]);p.validate_request(r)
            self.assertEqual(p.collect(r)['distributions'][0]['status'],'UNKNOWN_ABSENT')
    def test_record_hash_only(self):
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t).resolve(); d=self.dist(root); meta=pathlib.Path(d['metadata_dir']);meta.mkdir()
            rec=meta/'RECORD';rec.write_text('synthetic only\n');(meta/'METADATA').write_text('Name: torch\nVersion: synthetic\n')
            d.update(record_sha256=p.sha(rec),record_bytes=rec.stat().st_size,metadata_sha256=p.sha(meta/'METADATA'),metadata_bytes=(meta/'METADATA').stat().st_size)
            got=p.collect(self.request(distributions=[d]))
            self.assertEqual(got['distributions'][0]['record_sha256'],p.sha(rec))
            self.assertNotIn('synthetic only',str(got))
    def test_unknown_distribution_refused(self):
        with self.assertRaises(ValueError):p.validate_request(self.request(distributions=[self.dist(pathlib.Path('/synthetic'),'unreviewed')]))
    def test_duplicate_distribution_refused(self):
        d=self.dist(pathlib.Path('/synthetic'))
        with self.assertRaises(ValueError):p.validate_request(self.request(distributions=[d,d]))
    def test_data_suffixes_refused(self):
        for suffix in ('npz','pt','tar','png','json','log'):
            with self.assertRaises(ValueError): p.validate_request(self.request([dict(path='/synthetic/file.'+suffix,sha256='0'*64,bytes=1,kind='python_source')]))
    def test_file_bounds_and_symlinks(self):
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t).resolve(); f=root/'source.py'; f.write_text('fixture'); link=root/'link.py'; link.symlink_to(f)
            with self.assertRaises(ValueError):p.regular(link)
        f=dict(path='/synthetic/file.py',sha256='0'*64,bytes=p.MAX_FILE+1,kind='python_source')
        with self.assertRaises(ValueError):p.validate_request(self.request([f]))
    def test_no_release_before_collection(self):
        with patch.object(p,'collect',side_effect=AssertionError('collection canary')):
            with self.assertRaises((ValueError,KeyError)): p.authorize(self.request(),{},'0'*64,'0'*64)
    def test_root_scope_and_exact_binding_guards(self):
        r=self.request();r['interpreter']=p.sys.executable;r['interpreter_sha256']='1'*64
        release=dict(decision='GO_SBMR512_BII_ENV_SOURCE_METADATA_V1',root_authorized=True,author='author',reviewer='other',request_sha256='2'*64,probe_sha256='3'*64,output=p.OUTPUT,automatic_retry=False,scientific_read='HOLD',gpu_authorized=False,independent_review_path='/synthetic/review',independent_review_sha256='1'*64)
        with patch.object(p,'sha',return_value='1'*64):
            p.authorize(r,release,'2'*64,'3'*64)
            for key,value in [('root_authorized',False),('reviewer','author'),('scientific_read','GO'),('gpu_authorized',True),('automatic_retry',True),('request_sha256','4'*64),('output','/alternate')]:
                bad=dict(release);bad[key]=value
                with self.assertRaises(ValueError):p.authorize(r,bad,'2'*64,'3'*64)
    def test_escaped_metadata_root_refused(self):
        d=self.dist(pathlib.Path('/synthetic'));d['metadata_dir']='/other/torch.dist-info'
        with self.assertRaises(ValueError):p.validate_request(self.request(distributions=[d]))
    def test_create_only_receipt(self):
        with tempfile.TemporaryDirectory() as t:
            f=pathlib.Path(t)/'generated.json';p.put(f,{'fixture':True})
            with self.assertRaises(FileExistsError):p.put(f,{'fixture':False})
    def test_import_surface_and_no_model_execution(self):
        tree=ast.parse(pathlib.Path(p.__file__).read_text())
        imports=[n.module if isinstance(n,ast.ImportFrom) else a.name for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom)) for a in (n.names if isinstance(n,ast.Import) else [None])]
        self.assertFalse(any(x.split('.')[0] in ('torch','timm','numpy','cv2','PIL','subprocess','socket') for x in imports))
        self.assertNotIn('rglob(',pathlib.Path(p.__file__).read_text())

if __name__=='__main__':unittest.main(verbosity=2)
