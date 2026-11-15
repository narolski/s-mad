"""Native fit/supplement decoders for NEXT, pending independent review.

No CLI, archive extraction, weights, automatic discovery, or scientific verdicts.
Callers must first bind every record, manifest row list and config hash through
the reviewed admission. These functions do NOT assert registration eligibility.
The selector pins this module and calls it only after its atomic once claim.
"""
import contextlib
import hashlib
import io
import json
import math
import pathlib
import re
import tarfile

import numpy as np


class NativeRefusal(ValueError):
    """Incomplete or inconsistent native evidence; never a scientific verdict."""


class NativeIntegrityError(NativeRefusal):
    """Artifact bytes changed after admission; abort the entire invocation."""


def require(ok, message):
    if not ok:
        raise NativeRefusal(message)


@contextlib.contextmanager
def archive(record):
    """Hash and read one descriptor; normalize ./ but reject alias collisions."""
    with pathlib.Path(record['archive']).open('rb') as f:
        if hashlib.file_digest(f, 'sha256').hexdigest() != record['sha256']:
            raise NativeIntegrityError('archive digest changed')
        f.seek(0)
        with tarfile.open(fileobj=f, mode='r:') as tf:
            members = {}
            for member in tf.getmembers():
                p = pathlib.PurePosixPath(member.name)
                require(not p.is_absolute() and '..' not in p.parts, 'unsafe member path')
                name = str(p)
                require(name not in members, 'duplicate/aliased archive member')
                members[name] = member

            def read(name, limit=8 * 1024 * 1024):
                member = members.get(name)
                require(member is not None, 'required native member absent')
                require(member.isfile() and member.size <= limit, 'invalid member type/size')
                with tf.extractfile(member) as stream:
                    return stream.read()

            yield read


def unpack_npz(raw):
    with np.load(io.BytesIO(raw), allow_pickle=False) as z:
        return {k: z[k] for k in z.files}


def scalar(z, field):
    value = np.asarray(z[field])
    require(value.shape == (), 'native scalar shape differs')
    return value.item()


def row_scores(z, expected_ids, seed=None):
    ids = np.asarray(z['id'])
    values = np.asarray(z['logit'])
    require(ids.ndim == 1 and ids.dtype.kind in 'US', 'invalid native ID vector')
    require(ids.tolist() == list(expected_ids) and len(set(expected_ids)) == len(expected_ids),
            'native row identity/order differs')
    require(values.shape == ids.shape and values.dtype.kind == 'f' and np.isfinite(values).all(),
            'invalid/non-finite native logit vector')
    if seed is not None:
        require(scalar(z, 'seed') == seed, 'native scoring seed differs')
    return dict(zip(ids.tolist(), values.astype(float).tolist()))


def exact_gate(gate, source, manifest, count):
    expected = dict(tar=source['name'] + '.tar', tar_sha256=source['sha256'],
                    manifest=manifest, n=count, verdict='passed', n_differ=0,
                    max_abs=0, own_rule_agree=1, device='NVIDIA H100')
    require(all(gate.get(k) == v for k, v in expected.items()),
            'full-manifest exact identity gate refused')


def source_identity(source):
    """Only existing registered selection formats; fresh sources stay blocked."""
    name, seed, arm = source['name'], source['seed'], source['arm']
    if name.startswith('AB1FM_'):
        require(arm == 'SbFM' and seed in range(408, 413), 'unregistered SbFM source')
        manifest, count = 'ab1x_eval.csv', 24859
        prefix = 'AB1FM'
    elif name.startswith('AB1_'):
        require(arm in ('A', 'Sb') and seed in range(408, 413), 'unregistered AB1 source')
        manifest, count = 'ab1_eval.csv', 21277
        prefix = 'AB1'
    else:
        require(name.startswith('BB2L_') and arm in ('A', 'B', 'Sb') and seed in range(403, 408),
                'unregistered E3 source')
        manifest, count = 'pn1_eval.csv', 19797
        prefix = 'BB2L'
    require(name == f'{prefix}_{arm}_s{seed}', 'native source identity differs')
    require(re.fullmatch('[0-9a-f]{64}', source['sha256']) is not None, 'invalid source digest')
    return prefix, manifest, count


def load_sbfm_supplement(record, source, family_ids):
    """Decode one model from the final AB1FMSUPP-v1 archive, gate before NPZ.

    record.config_sha256 must be the independently pinned submitted config hash.
    family_ids are ordered rows of the pinned tt1/meds manifests (not a subset).
    Other models' failures remain in technical_status; they cannot veto this
    model or silently turn a failed model into a valid one.
    """
    origin, manifest, count = source_identity(source)
    require(origin in ('AB1FM', 'AB1') and source['arm'] != 'A', 'source not in supplement')
    require(set(family_ids) == {'tt1', 'meds'}, 'supplement family coverage differs')
    with archive(record) as read:
        raw = read('config.json')
        require(hashlib.sha256(raw).hexdigest() == record['config_sha256'], 'submitted config differs')
        config = json.loads(raw)
        require(config['schema'] == 'AB1FMSUPP-v1' and config['expected_gpu'] == 'NVIDIA H100',
                'supplement configuration differs')
        models = [m for m in config['models'] if m['name'] == source['name']]
        require(len(models) == 1, 'supplement source not uniquely configured')
        expected = dict(seed=source['seed'], sha256=source['sha256'],
                        gate_manifest=manifest, gate_rows=count)
        require(all(models[0].get(k) == v for k, v in expected.items()), 'supplement source differs')
        receipt = read('pre_read_receipt.json')
        require(hashlib.sha256(receipt).hexdigest() == config['pre_read_receipt_sha256'],
                'supplement pre-read receipt differs')
        status = json.loads(read('technical_status.json'))  # final output only
        require(status.get('eight_row_smoke_passed') is True and status.get('fits') == 0
                and status.get('scientific_contrasts_read') is False, 'supplement technical status incomplete')
        records = [m for m in status['models'] if m['name'] == source['name']]
        require(len(records) == 1 and records[0].get('seed') == source['seed']
                and records[0].get('gate') == 'passed', 'supplement model refused')
        exact_gate(json.loads(read('gate_' + source['name'] + '.json')), source, manifest, count)
        families = records[0]['families']
        require(len(families) == 2 and {v['name'] for v in families} == set(family_ids),
                'supplement model families incomplete')
        output = {}
        for family in ('tt1', 'meds'):
            item = next(v for v in families if v['name'] == family)
            require(item.get('valid') is True, 'supplement family failed')
            raw = read(source['name'] + '__' + family + '.npz', 256 * 1024 * 1024)
            require(hashlib.sha256(raw).hexdigest() == item['sha256'], 'supplement family digest differs')
            output[family] = row_scores(unpack_npz(raw), family_ids[family], source['seed'])
        output['border_path'] = 'AB1FMSUPP:' + record['sha256']
        return output


W2_SCRIPTS = {
    'rescore_tf32.py': '0d0b6b6fb5ebc4d5bdbe15384fcd00e13c0756785ed22743893186e68245d8d5',
    'rescore.py': '6f6eede71c6d9a895199dabc8bc90b882adb25f5f91cd2fcc676ebe7a380b51e',
    'precision_probe.py': 'b49c1e704bc8957db76398abfd5ab54218ee152ac32ed9e061c634378148605e',
}


def load_dinov3_w2(record, source, family_ids):
    """Decode required W2 families, using amendment 7d's per-network gate.

    Global failure counters are returned as metadata, not used to drop surviving
    seeds. gd0/gd1/gd2 are outside NEXT and are not opened by this adapter.
    """
    origin, manifest, count = source_identity(source)
    require(origin == 'BB2L' or (origin == 'AB1' and source['arm'] == 'Sb'), 'source not in W2')
    require(set(family_ids) in ({'ms1ffhq', 'tt1', 'meds'}, {'ms1ffhq'}), 'W2 family coverage differs')
    with archive(record) as read:
        tasks = read('out/tasks.txt').decode().splitlines()
        require(len(set(tasks)) == len(tasks) and tasks.count(source['name']) == 1, 'W2 task identity differs')
        require('NVIDIA H100' in read('out/gpu.txt').decode(), 'W2 GPU differs')
        lines = [line.split() for line in read('out/scripts.sha256').decode().splitlines()]
        require(len(lines) == len(W2_SCRIPTS) and all(len(line) == 2 for line in lines), 'W2 script pins malformed')
        require({pathlib.PurePosixPath(p).name: h for h, p in lines} == W2_SCRIPTS, 'W2 scorer pins differ')
        counters = {k: int(read('out/' + k + '.txt')) for k in ('n_fail', 'n_refused')}
        require(all(v >= 0 for v in counters.values()), 'invalid W2 failure counters')
        exact_gate(json.loads(read('out/gate_' + source['name'] + '.json')), source, manifest, count)
        output = {family: row_scores(unpack_npz(read('out/W2_' + source['name'] + '_' + family + '.npz',
                                                   256 * 1024 * 1024)), ids, source['seed'])
                  for family, ids in family_ids.items()}
        output.update(border_path='BB2LW2:' + record['sha256'], technical_failures=counters)
        return output


def load_fit(record, eval_ids, train_rows, train_sha256, eval_sha256, n_items):
    """Decode AB1/SbFM/E3 native fit arrays with exact manifest identity.

    train_rows must be the first-occurrence unique-path projection of the pinned
    training manifest; n_items is its full repeated-row count. Returned training
    scores permit the E3 splice-fit gate; no gate verdict is inferred here.
    """
    source = dict(record, name=record['prefix'])
    origin, _, count = source_identity(source)
    require(len(eval_ids) == count, 'fit evaluation manifest row count differs')
    overlay = {'AB1': '171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149',
               'AB1FM': 'e554b84f74e5de8791fddc168b99a7c46376ee48ab7902baf358ecbe668d8e47',
               'BB2L': '7c0a0b41f2e7bf656dc49db33c34a33ef62b10e8f0aaec24e247e684098d0bad'}[origin]
    with archive(record) as read:
        def raw(name):
            return read(record['prefix'] + '/' + name)
        require('H100' in raw('gpu.txt').decode(), 'fit GPU differs')
        tokens = raw('task_info.txt').decode().split()
        def token(k, v):
            return tokens.count(k) == 1 and tokens.index(k) + 1 < len(tokens) and tokens[tokens.index(k) + 1] == str(v)
        arch = 'a12_dinov3_vitl16_madation' if origin == 'BB2L' else 'a12_clip_vitb16_madation'
        required = dict(pack_sha256='96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004',
                        overlay_sha256=overlay, steps=6250, limit=0, arch=arch)
        if origin == 'BB2L':
            # WCSS runner permits these two registered effective-batch-256
            # configurations. Exact submitted setting belongs in admission.
            batch = record['batch_spec']
            require(batch in ([256, 1], [128, 2]), 'unregistered E3 batch setting')
            required.update(lr='1.17e-05', bs=batch[0], accum=batch[1])
        require(all(token(k, v) for k, v in required.items()), 'fit recipe/pins differ')
        task = raw('task.env').decode().splitlines()
        require(all(task.count(f'{k}={v}') == 1 for k, v in dict(ARM=record['arm'], SEED=record['seed'],
                                                              TASK=record['prefix']).items()), 'fit task identity differs')
        meta = json.loads(raw('meta.json'))
        require(all(meta.get(k) == v for k, v in dict(seed=record['seed'], steps=6250, n_items=n_items,
                                                     res=224, arch=arch).items()), 'fit metadata differs')
        loss = re.findall(r'loss[ =:]+(-?(?:inf|nan)|[-+0-9.eE]+)', raw('train.log').decode(), re.I)
        require(bool(loss) and all(math.isfinite(float(v)) for v in loss), 'fit loss absent/non-finite')
        z = unpack_npz(read(record['prefix'] + '/scores_eval.npz', 256 * 1024 * 1024))
        require(scalar(z, 'manifest_sha256') == eval_sha256, 'fit evaluation manifest differs')
        x = row_scores(z, eval_ids)
        tr = unpack_npz(read(record['prefix'] + '/scores_train.npz', 256 * 1024 * 1024))
        require(scalar(tr, 'manifest_sha256') == train_sha256, 'fit training manifest differs')
        paths = [r['path'] for r in train_rows]
        require(len(set(paths)) == len(paths), 'expected training paths not unique')
        for field in ('path', 'kind', 'label'):
            expected = [int(r[field]) if field == 'label' else r[field] for r in train_rows]
            require(np.asarray(tr[field]).shape == (len(paths),) and tr[field].tolist() == expected,
                    'fit training row identity/order differs')
        lg = np.asarray(tr['logit'])
        require(lg.shape == (len(paths),) and lg.dtype.kind == 'f' and np.isfinite(lg).all(),
                'invalid/non-finite training scores')
        return {'x': x, 'train': tr}
