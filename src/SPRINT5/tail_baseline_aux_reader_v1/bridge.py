"""Only hash verification and the frozen durable journal; no primary/statistics imports."""
import hashlib
import importlib.util
import pathlib

ROOT=pathlib.Path('/home/narolski/smad-next/src/SPRINT5/paired_ranking_reader')
SUMS_SHA='02c7401529a8ca8b2a7af220f7ef36f8cbd8a71ffc50052b0a52f6e2606d1b6c'
_cache=None


def sha(path):
    h=hashlib.sha256()
    with pathlib.Path(path).open('rb') as f:
        for block in iter(lambda:f.read(4<<20),b''):h.update(block)
    return h.hexdigest()


def journal():
    global _cache
    assert sha(ROOT/'SHA256SUMS')==SUMS_SHA,'frozen durable utilities changed'
    entries={name:h for h,name in (line.split('  ',1) for line in (ROOT/'SHA256SUMS').read_text().splitlines())}
    assert sha(ROOT/'journal.py')==entries['journal.py'],'durable journal changed'
    if _cache is None:
        spec=importlib.util.spec_from_file_location('frozen_aux_durable_journal',ROOT/'journal.py')
        _cache=importlib.util.module_from_spec(spec);spec.loader.exec_module(_cache)
    return _cache
