"""Read-only adapter to the exact independently reviewed ranking utilities."""
import hashlib
import importlib
import pathlib
import sys
from types import SimpleNamespace

ROOT=pathlib.Path('/home/narolski/smad-next/src/SPRINT5/paired_ranking_reader')
SUMS_SHA='02c7401529a8ca8b2a7af220f7ef36f8cbd8a71ffc50052b0a52f6e2606d1b6c'
BINDING_SHA='519546ef7002930f620610f01deb0cc4e8889acf819b829a80c05f95fff6e923'
_loaded=None


def sha(p):
    h=hashlib.sha256()
    with pathlib.Path(p).open('rb') as f:
        for b in iter(lambda:f.read(4<<20),b''):h.update(b)
    return h.hexdigest()


def load():
    global _loaded
    assert sha(ROOT/'SHA256SUMS')==SUMS_SHA,'frozen ranking source manifest changed'
    for line in (ROOT/'SHA256SUMS').read_text().splitlines():
        h,name=line.split('  ',1);p=ROOT/name
        assert p.resolve().is_relative_to(ROOT.resolve()) and sha(p)==h,'frozen ranking dependency changed'
    if _loaded is None:
        sys.path.insert(0,str(ROOT))
        modules={name:importlib.import_module(name) for name in ('admit','data','ranking_statistics','journal','collect_metadata')}
        assert all(pathlib.Path(m.__file__).parent.resolve()==ROOT.resolve() for m in modules.values()),'module shadowing'
        _loaded=SimpleNamespace(admit=modules['admit'],data=modules['data'],stats=modules['ranking_statistics'],
                                journal=modules['journal'],member_bytes=modules['collect_metadata'].member_bytes)
    return _loaded
