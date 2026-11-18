"""Prospective metadata-only probe. No live release or runtime package imports."""
import argparse
import hashlib
import importlib.metadata as md
import json
import os
import pathlib
import sys
import sysconfig
import datetime

OUTPUT = '/mnt/t7/smad_next/RZ1/SbMR512_bii_environment_source_probe_v1_20261114'
ALLOWED = frozenset(('torch', 'torchvision', 'timm', 'numpy', 'Pillow', 'opencv-python', 'opencv-python-headless', 'transformers', 'huggingface-hub', 'safetensors', 'tokenizers'))
MAX_FILE = 512 * 1024 * 1024
MAX_TOTAL = 2 * 1024 * 1024 * 1024

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

def sha(path):
    h = hashlib.sha256()
    with pathlib.Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()

def hex64(value):
    return type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value)

def validate_request(r):
    require(set(r) == {'schema', 'interpreter', 'interpreter_sha256', 'distributions', 'files'}, 'request_keys')
    require(r['schema'] == 'SBMR512_ENV_SOURCE_REQUEST_V1', 'request_schema')
    require(pathlib.Path(r['interpreter']).is_absolute() and hex64(r['interpreter_sha256']), 'interpreter_binding')
    ds = r['distributions']
    require(type(ds) is list and len(ds) <= len(ALLOWED), 'distribution_bound')
    names = []
    for d in ds:
        require(set(d) == {'name', 'metadata_root', 'metadata_dir', 'record_sha256', 'record_bytes', 'metadata_sha256', 'metadata_bytes'}, 'distribution_keys')
        names.append(d['name'])
        root, meta = pathlib.Path(d['metadata_root']), pathlib.Path(d['metadata_dir'])
        require(root.is_absolute() and meta.is_absolute() and meta.parent == root and meta.name.endswith('.dist-info'), 'explicit_metadata_root')
        require(hex64(d['record_sha256']) and type(d['record_bytes']) is int and 0 <= d['record_bytes'] <= 16 * 1024 * 1024, 'record_pin')
        require(hex64(d['metadata_sha256']) and type(d['metadata_bytes']) is int and 0 <= d['metadata_bytes'] <= 16 * 1024 * 1024, 'metadata_pin')
    require(len(names) == len(set(names)) and set(names) <= ALLOWED, 'distribution_allowlist')
    require(type(r['files']) is list and len(r['files']) <= 256, 'file_bound')
    seen = set()
    for f in r['files']:
        require(set(f) == {'path', 'sha256', 'bytes', 'kind'}, 'file_keys')
        p = pathlib.Path(f['path'])
        require(p.is_absolute() and str(p) == f['path'] and '..' not in p.parts, 'absolute_normal_path')
        require(str(p) not in seen, 'duplicate_file'); seen.add(str(p))
        require(f['kind'] in ('python_source', 'native_library'), 'file_kind')
        require((f['kind'] == 'python_source' and p.suffix == '.py') or (f['kind'] == 'native_library' and (p.suffix in ('.so', '.dylib') or '.so.' in p.name)), 'source_suffix')
        require(not set(p.parts) & {'Datasety', 'datasets', 'data', '.cache', 'checkpoints', 'models--', 'snapshots'}, 'forbidden_path')
        require(type(f['bytes']) is int and 0 <= f['bytes'] <= MAX_FILE and hex64(f['sha256']), 'file_pin')
    require(sum(f['bytes'] for f in r['files']) <= MAX_TOTAL, 'total_byte_bound')

def authorize(r, release, request_hash, script_hash):
    validate_request(r)
    require(release['decision'] == 'GO_SBMR512_BII_ENV_SOURCE_METADATA_V1', 'decision')
    require(release['root_authorized'] is True and release['author'] != release['reviewer'] and bool(release['reviewer']), 'independent_root_release')
    require(release['request_sha256'] == request_hash and release['probe_sha256'] == script_hash, 'source_request_binding')
    require(release['output'] == OUTPUT and release['automatic_retry'] is False, 'fixed_once_output')
    require(release['scientific_read'] == 'HOLD' and release['gpu_authorized'] is False, 'scope')
    require(release['independent_review_sha256'] == sha(release['independent_review_path']), 'review_pin')
    require(sys.flags.optimize == 0 and sys.flags.isolated == 1 and sys.flags.no_site == 1, 'isolated_nosite_unoptimized_required')
    require(pathlib.Path(sys.executable).resolve() == pathlib.Path(r['interpreter']).resolve(), 'interpreter_path')
    require(sha(pathlib.Path(sys.executable).resolve()) == r['interpreter_sha256'], 'interpreter_hash')

def regular(path):
    p = pathlib.Path(path)
    require(p.is_file() and not p.is_symlink() and p.resolve() == p, 'regular_canonical_file_required')
    return p

def collect(r, distribution_at=md.Distribution.at):
    """Only explicit frozen metadata directories; no package discovery/import or cache crawl."""
    files = []
    for f in r['files']:
        candidate = pathlib.Path(f['path'])
        if not candidate.exists():
            files.append(dict(f, status='UNKNOWN_ABSENT')); continue
        p = regular(f['path'])
        require(p.stat().st_size == f['bytes'] and sha(p) == f['sha256'], 'installed_source_pin_mismatch')
        files.append(dict(f, status='CONTENT_HASHED'))
    distributions = []
    for dspec in r['distributions']:
        name = dspec['name']; meta = pathlib.Path(dspec['metadata_dir'])
        if not meta.exists():
            distributions.append({'name': name, 'status': 'UNKNOWN_ABSENT'}); continue
        require(meta.is_dir() and meta.resolve() == meta, 'canonical_metadata_directory')
        record = regular(str(meta/'RECORD'))
        require(record.stat().st_size == dspec['record_bytes'] and sha(record) == dspec['record_sha256'], 'record_pin_mismatch')
        # Distribution.at is the public exact-directory API: unlike discovery it never
        # enumerates unrelated installed distributions. METADATA supplies only name/version.
        metadata_file = regular(str(meta/'METADATA'))
        require(metadata_file.stat().st_size == dspec['metadata_bytes'] and sha(metadata_file) == dspec['metadata_sha256'], 'metadata_pin_mismatch')
        dist = distribution_at(meta)
        require(dist.metadata['Name'].lower().replace('_','-') == name.lower().replace('_','-'), 'distribution_name_mismatch')
        distributions.append({'name': name, 'version': dist.version, 'metadata_root': dspec['metadata_root'], 'metadata_dir': str(meta), 'record_sha256': dspec['record_sha256'], 'metadata_sha256': sha(metadata_file), 'status': 'CONTENT_HASHED'})
    return {'schema_version': 'SBMR512_ENV_SOURCE_RECEIPT_V1', 'status': 'PROSPECTIVE_METADATA_ONLY_NOT_HISTORICAL_IDENTITY',
            'timestamp_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'python': {'version': sys.version, 'executable': sys.executable, 'prefix': sys.prefix, 'base_prefix': sys.base_prefix, 'flags': {'isolated':sys.flags.isolated,'no_site':sys.flags.no_site,'optimize':sys.flags.optimize}, 'sysconfig_paths': sysconfig.get_paths(), 'nosite_caveat': '-S prefix/sysconfig may differ from target venv; explicit metadata roots define target installation'},
            'distributions': distributions, 'installed_source_files': files,
            'historical_executed_identity': 'UNKNOWN', 'checkpoint_schema': 'UNKNOWN', 'pretrained_content': 'UNKNOWN',
            'image_bytes': 'UNKNOWN', 'backend_defaults': 'UNKNOWN', 'worker_runtime': 'UNKNOWN',
            'native_bytegate': 'NOT_RUN', 'timing': 'NOT_RUN', 'scientific_read': 'HOLD'}

def put(path, value):
    with pathlib.Path(path).open('x') as f:
        json.dump(value, f, indent=2, allow_nan=False); f.write('\n'); f.flush(); os.fsync(f.fileno())
    fd = os.open(pathlib.Path(path).parent, os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)

def main():
    p = argparse.ArgumentParser(); p.add_argument('--request', required=True); p.add_argument('--release', required=True); args = p.parse_args()
    request = json.loads(pathlib.Path(args.request).read_text()); release = json.loads(pathlib.Path(args.release).read_text())
    authorize(request, release, sha(args.request), sha(__file__))
    out = pathlib.Path(OUTPUT); out.mkdir(parents=True, exist_ok=False)
    put(out/'CLAIM.json', {'request_sha256': sha(args.request), 'release_sha256': sha(args.release), 'automatic_retry': False})
    try:
        receipt = collect(request)
        receipt.update(probe_sha256=sha(__file__), release_sha256=sha(args.release), request_sha256=sha(args.request), interpreter_requested=request['interpreter'], interpreter_resolved=str(pathlib.Path(sys.executable).resolve()), interpreter_sha256=request['interpreter_sha256'])
        put(out/'RECEIPT.json', receipt)
        put(out/'COMPLETE.json', {'receipt_sha256': sha(out/'RECEIPT.json'), 'scientific_read': 'HOLD'})
    except BaseException as e:
        put(out/'FAILED.json', {'error_type': type(e).__name__, 'status': 'HOLD_NO_RETRY'})
        raise SystemExit(1) from None

if __name__ == '__main__':
    main()
