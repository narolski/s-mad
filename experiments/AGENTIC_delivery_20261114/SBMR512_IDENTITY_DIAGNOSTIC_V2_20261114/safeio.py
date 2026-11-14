"""Prospective metadata-only probe. No live release or runtime package imports."""
import argparse
import hashlib
import email.parser
import email.policy
import stat
import re
import json
import os
import pathlib
import sys
import sysconfig
import datetime

OUTPUT = '/mnt/t7/smad_next/RZ1/SbMR512_bii_environment_source_probe_v1r1_20261114'
ALLOWED = frozenset(('torch', 'torchvision', 'timm', 'numpy', 'Pillow', 'opencv-python', 'opencv-python-headless', 'transformers', 'huggingface-hub', 'safetensors', 'tokenizers'))
MAX_FILE = 512 * 1024 * 1024
MAX_TOTAL = 2 * 1024 * 1024 * 1024

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

CONTROL_CAP = 4 * 1024 * 1024

def absolute_parts(path):
    require(type(path) is str and path.startswith('/') and str(pathlib.PurePosixPath(path)) == path and '..' not in pathlib.PurePosixPath(path).parts, 'canonical_absolute_path')
    return pathlib.PurePosixPath(path).parts[1:]

def directory_fd(path):
    parts = absolute_parts(path)
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd); fd = child
        return fd
    except BaseException:
        os.close(fd); raise

def fingerprint(st):
    return (st.st_dev, st.st_ino, st.st_mode, st.st_size, st.st_mtime_ns, st.st_ctime_ns)

def snapshot(path, cap, expected_size=None, expected_hash=None, capture=True):
    """One descriptor, no-follow EVERY component, fstat/capped read/hash SAME bytes.
    No reopens, discovery or following symlinks, including for controls and source.
    """
    parts = absolute_parts(path); require(bool(parts), 'file_required')
    parent = directory_fd('/' + '/'.join(parts[:-1]))
    try:
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
    finally:
        os.close(parent)
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode), 'regular_descriptor_required')
        require(0 <= before.st_size <= cap, 'file_cap')
        if expected_size is not None: require(before.st_size == expected_size, 'size_mismatch')
        limit = before.st_size
        h = hashlib.sha256(); chunks = []; total = 0
        while total <= limit:
            block = os.read(fd, min(1 << 20, limit + 1 - total))
            if not block: break
            total += len(block)
            require(total <= limit, 'file_grew')
            h.update(block)
            if capture: chunks.append(block)
        after = os.fstat(fd)
        require(total == limit and fingerprint(before) == fingerprint(after), 'file_changed')
        digest = h.hexdigest()
        if expected_hash is not None: require(digest == expected_hash, 'hash_mismatch')
        return (b''.join(chunks) if capture else None), digest, total
    finally:
        os.close(fd)

def sha(path):
    return snapshot(str(path), MAX_FILE, capture=False)[1]

def control(path):
    raw, digest, _ = snapshot(path, CONTROL_CAP)
    return json.loads(raw), digest


def hex64(value):
    return type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value)

def validate_request(r):
    require(set(r) == {'schema', 'interpreter', 'interpreter_sha256', 'distributions', 'files'}, 'request_keys')
    require(r['schema'] == 'SBMR512_ENV_SOURCE_REQUEST_V1R1', 'request_schema')
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
    require(release['decision'] == 'GO_SBMR512_BII_ENV_SOURCE_METADATA_V1R1', 'decision')
    require(release['root_authorized'] is True and release['author'] != release['reviewer'] and bool(release['reviewer']), 'independent_root_release')
    require(release['request_sha256'] == request_hash and release['probe_sha256'] == script_hash, 'source_request_binding')
    require(release['output'] == OUTPUT and release['automatic_retry'] is False, 'fixed_once_output')
    require(release['scientific_read'] == 'HOLD' and release['gpu_authorized'] is False, 'scope')
    snapshot(release['independent_review_path'], CONTROL_CAP, expected_hash=release['independent_review_sha256'], capture=False)
    require(sys.flags.optimize == 0 and sys.flags.isolated == 1 and sys.flags.no_site == 1, 'isolated_nosite_unoptimized_required')
    require(os.path.realpath(sys.executable) == r['interpreter'], 'interpreter_path')
    require(sha(r['interpreter']) == r['interpreter_sha256'], 'interpreter_hash')

def metadata_fields(raw, expected_name):
    # Parse only the authenticated snapshot. Never Distribution.at/read_text/fallback.
    message = email.parser.BytesParser(policy=email.policy.default).parsebytes(raw)
    require(not message.defects, 'malformed_metadata')
    values = {}
    for key in ('Name', 'Version'):
        entries = message.get_all(key, [])
        require(len(entries) == 1, 'missing_duplicate_' + key)
        value = str(entries[0])
        require(bool(value) and value.strip() == value and not any(c.isspace() for c in value), 'invalid_' + key)
        require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*' if key == 'Name' else r'[A-Za-z0-9][A-Za-z0-9.!+_-]*', value) is not None, 'malformed_' + key)
        values[key] = value
    require(values['Name'].lower().replace('_', '-') == expected_name.lower().replace('_', '-'), 'distribution_name_mismatch')
    return values

def collect(r):
    files = []
    for f in r['files']:
        try:
            _, digest, size = snapshot(f['path'], MAX_FILE, f['bytes'], f['sha256'], capture=False)
        except FileNotFoundError:
            files.append(dict(f, status='UNKNOWN_ABSENT')); continue
        files.append(dict(f, status='CONTENT_HASHED'))
    distributions = []
    for dspec in r['distributions']:
        name, meta = dspec['name'], dspec['metadata_dir']
        try:
            # Both are exact allowlisted files. RECORD paths are never parsed/opened.
            _, record_hash, _ = snapshot(meta + '/RECORD', 16 << 20, dspec['record_bytes'], dspec['record_sha256'], capture=False)
            raw, metadata_hash, _ = snapshot(meta + '/METADATA', 16 << 20, dspec['metadata_bytes'], dspec['metadata_sha256'])
        except FileNotFoundError:
            distributions.append({'name':name, 'status':'UNKNOWN_ABSENT'}); continue
        fields = metadata_fields(raw, name)
        distributions.append({'name': name, 'version': fields['Version'], 'metadata_root': dspec['metadata_root'], 'metadata_dir': meta, 'record_sha256': record_hash, 'metadata_sha256': metadata_hash, 'status': 'CONTENT_HASHED'})
    return {'schema_version': 'SBMR512_ENV_SOURCE_RECEIPT_V1R1', 'status': 'PROSPECTIVE_METADATA_ONLY_NOT_HISTORICAL_IDENTITY',
            'timestamp_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'python': {'version': sys.version, 'executable': sys.executable, 'prefix': sys.prefix, 'base_prefix': sys.base_prefix, 'flags': {'isolated':sys.flags.isolated,'no_site':sys.flags.no_site,'optimize':sys.flags.optimize}, 'sysconfig_paths': sysconfig.get_paths(), 'nosite_caveat': '-S prefix/sysconfig may differ from target venv; explicit metadata roots define target installation'},
            'distributions': distributions, 'installed_source_files': files,
            'historical_executed_identity': 'UNKNOWN', 'checkpoint_schema': 'UNKNOWN', 'pretrained_content': 'UNKNOWN',
            'image_bytes': 'UNKNOWN', 'backend_defaults': 'UNKNOWN', 'worker_runtime': 'UNKNOWN',
            'native_bytegate': 'NOT_RUN', 'timing': 'NOT_RUN', 'scientific_read': 'HOLD'}

def put(outfd, name, value):
    require('/' not in name, 'output_basename')
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=outfd)
    raw = (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()
    with os.fdopen(fd, 'wb') as f:
        f.write(raw); f.flush(); os.fsync(f.fileno())
    os.fsync(outfd)
    return hashlib.sha256(raw).hexdigest()


def main():
    p = argparse.ArgumentParser(); p.add_argument('--request', required=True); p.add_argument('--release', required=True); args = p.parse_args()
    # Snapshot and authenticate the SAME bounded bytes later parsed/used/receipted.
    request, request_hash = control(args.request)
    release, release_hash = control(args.release)
    probe_hash = sha(os.path.abspath(__file__))
    authorize(request, release, request_hash, probe_hash)
    parent = directory_fd(str(pathlib.PurePosixPath(OUTPUT).parent))
    try:
        os.mkdir(pathlib.PurePosixPath(OUTPUT).name, mode=0o700, dir_fd=parent)
        os.fsync(parent)
        outfd = os.open(pathlib.PurePosixPath(OUTPUT).name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
    finally: os.close(parent)
    try:
        put(outfd, 'CLAIM.json', {'request_sha256':request_hash,'release_sha256':release_hash,'probe_sha256':probe_hash,'automatic_retry':False})
        try:
            receipt = collect(request)
            receipt.update(probe_sha256=probe_hash, release_sha256=release_hash, request_sha256=request_hash, interpreter_requested=request['interpreter'], interpreter_resolved=os.path.realpath(sys.executable), interpreter_sha256=request['interpreter_sha256'])
            receipt_hash = put(outfd, 'RECEIPT.json', receipt)
            put(outfd, 'COMPLETE.json', {'receipt_sha256':receipt_hash,'scientific_read':'HOLD'})
        except BaseException as e:
            put(outfd, 'FAILED.json', {'error_type':type(e).__name__,'status':'HOLD_NO_RETRY'})
            raise SystemExit(1) from None
    finally: os.close(outfd)

if __name__ == '__main__':
    main()
