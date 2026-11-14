"""Execute registered supplementary TT1/MEDS scoring with unchanged gate/scorers.

Runs on the allocated H100 in local scratch, never on a login node. No scientific
contrast or selection statistic is computed. Failed gates refuse further scoring.
"""
import argparse
import csv
import datetime
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys


def sha(path):
    h = hashlib.sha256()
    with pathlib.Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def run(command, *, env=None, cwd=None, logfile=None):
    if logfile is None:
        subprocess.run(command, env=env, cwd=cwd, check=True)
    else:
        with pathlib.Path(logfile).open('a') as log:
            subprocess.run(command, env=env, cwd=cwd, stdout=log,
                           stderr=subprocess.STDOUT, check=True)


def data_root(path, source, *, train=False):
    path.mkdir()
    (path / 'manifests').mkdir()
    (path / 'eval').symlink_to(source / 'eval')
    if train:
        (path / 'train').symlink_to(source / 'train')
    for f in sorted((source / 'manifests').glob('*.csv')):
        (path / 'manifests' / f.name).symlink_to(f)
    return path


def main():
    assert sys.flags.isolated, 'run with python -I'
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', required=True)
    parser.add_argument('--work', required=True)
    parser.add_argument('--results', required=True)
    args = parser.parse_args()
    stage = pathlib.Path(args.stage)
    work = pathlib.Path(args.work)
    results = pathlib.Path(args.results)
    cfg = json.loads((stage / 'config.json').read_text())
    receipt = json.loads((stage / 'pre_read_receipt.json').read_text())
    assert sha(stage / 'pre_read_receipt.json') == cfg['pre_read_receipt_sha256']
    receipt_keys = {'common_input_pins_sha256': 'experiments/NEXT_method-selection-rule/inputs/pins.sha256',
                    'support_input_pins_sha256': 'experiments/NEXT_method-selection-rule/inputs/support/pins.sha256'}
    for key, rel in receipt_keys.items():
        assert receipt['sha256'][rel] == cfg[key], ('pre-read receipt pin mismatch', key)
    assert receipt['clean_git_status'] is True and receipt['challenger_outputs_opened'] is False
    assert receipt['source_commit'] == cfg['pre_read_source_commit']
    assert receipt['verification']['prepare_inputs.py']['require_clean'] is True
    assert receipt['verification']['prepare_support.py']['require_clean'] is True
    assert receipt['verification']['prepare_inputs.py']['pins_verified'] == 44
    assert receipt['verification']['prepare_support.py']['support_pins_verified'] == 20
    assert sha(stage / 'support_v3.json') == cfg['support_sha256']
    outname = cfg['output_name']
    assert not any((results / (outname + suffix)).exists()
                   for suffix in ('.tar', '.tar.part', '.tar.sha256')), 'result/partial/sidecar already exists'
    assert len(cfg['models']) == 10
    assert {m['seed'] for m in cfg['models']} == set(range(408, 413))
    for model in cfg['models']:
        assert sha(model['path']) == model['sha256'], ('model tar pin', model['name'])
    for pack in cfg['packs']:
        assert sha(pack['path']) == pack['sha256'], ('pack pin', pack['name'])
    for script in cfg['scripts'].values():
        assert sha(script['path']) == script['sha256'], ('unchanged scorer pin', script['source'])

    work.mkdir(exist_ok=False)
    tree = work / 'tree'
    tree.mkdir()
    output = work / 'output'
    output.mkdir()
    # Input tar copies and unpacking are exclusively in this job's own local scratch.
    for pack in cfg['packs']:
        local = work / (pack['name'] + '.tar')
        shutil.copyfile(pack['path'], local)
        assert sha(local) == pack['sha256']
        run(['tar', '--skip-old-files', '-xf', str(local), '-C', str(tree)])
        local.unlink()
        sums = tree / pack['sums']
        run(['sha256sum', '-c', '--quiet', sums.name], cwd=sums.parent)
    # The two overlays add data/manifests only; original fit code and images remain exact.
    run(['sha256sum', '-c', '--quiet', 'SHA256SUMS'], cwd=tree / 'pn1')
    roots = {'fit': data_root(work / 'data_fit', tree / 'pn1/data', train=True),
             'tt1': data_root(work / 'data_tt1', tree / 'tt1/data'),
             'meds': data_root(work / 'data_meds', tree / 'tt1m/data')}
    for name, expected in cfg['manifest_sha256'].items():
        family = 'fit' if name.startswith('ab1') else ('tt1' if name.startswith('tt1') else 'meds')
        assert sha(roots[family] / 'manifests' / name) == expected, ('manifest pin', name)
    support = json.loads((stage / 'support_v3.json').read_text())
    ttrows = list(csv.DictReader((roots['tt1'] / 'manifests/tt1_score.csv').open()))
    ttids = {r['id'] for r in ttrows if r['fam'] == 'tt1'}
    assert len(support['border_ids']) == 1582 and set(support['border_ids']) <= ttids
    base = os.environ.copy()
    base.update(HF_HOME=str(tree / 'pn1/hf'), HF_HUB_OFFLINE='1')
    precision = cfg['scripts']['precision']['path']
    run([sys.executable, '-I', precision, '--expect-gpu', cfg['expected_gpu']],
        env=base, logfile=output / 'precision.log')
    runtime = subprocess.check_output([sys.executable, '-I', '-c',
        'import sys,torch,timm,numpy,PIL,json;print(json.dumps(dict(python=sys.version.split()[0],'
        'torch=torch.__version__,cuda=torch.version.cuda,timm=timm.__version__,numpy=numpy.__version__,pillow=PIL.__version__)))'],
        text=True)
    runtime_values = json.loads(runtime)
    (output / 'runtime.json').write_text(runtime)
    shutil.copyfile(stage / 'config.json', output / 'config.json')
    shutil.copyfile(stage / 'pre_read_receipt.json', output / 'pre_read_receipt.json')
    summary = {'started': datetime.datetime.now().astimezone().isoformat(),
               'models': [], 'fits': 0, 'scientific_contrasts_read': False}
    partial_root = results / 'diagnostic_partials' / (outname + '_job' + os.environ.get('SLURM_JOB_ID', 'unknown'))
    partial_root.mkdir(parents=True, exist_ok=False)
    partial_index = 0

    def preserve_partial(active=None):
        """Checkpoint completed technical work; never a final/read-admissible artifact."""
        nonlocal partial_index
        partial_index += 1
        status = {'partial': True, 'final_admission': False, 'summary': summary,
                  'active_model': active, 'at': datetime.datetime.now().astimezone().isoformat()}
        (work / 'PARTIAL_STATUS.json').write_text(json.dumps(status, indent=2) + '\n')
        name = outname + '_partial_' + f'{partial_index:03d}' + '.tar'
        local = work / name
        run(['tar', '-cf', str(local), '-C', str(work), 'output', 'PARTIAL_STATUS.json'])
        digest = sha(local)
        target = partial_root / name
        part = partial_root / (name + '.part')
        assert not target.exists() and not part.exists()
        shutil.copyfile(local, part)
        assert sha(part) == digest
        part.rename(target)
        with (partial_root / (name + '.sha256')).open('x') as f:
            f.write(digest + '  ' + name + '\n')
        local.unlink()
        print('SUPPLEMENT_PARTIAL', partial_index, digest, 'final_admission false', flush=True)

    failures = 0
    smoke_done = False
    for model in cfg['models']:
        name = model['name']
        print('SUPPLEMENT_MODEL', name, datetime.datetime.now().astimezone().isoformat(), flush=True)
        mdir = work / 'models'
        mdir.mkdir(exist_ok=True)
        run(['tar', '-xf', model['path'], '-C', str(mdir),
             name + '/meta.json', name + '/last_trainable.pt', name + '/env.txt', name + '/gpu.txt'])
        gateout = work / ('gate_' + name)
        gateout.mkdir()
        fit_env = dict(base, SMAD_DATA=str(roots['fit']))
        record = {'name': name, 'seed': model['seed'], 'families': []}
        try:
            # The fits wrote these package versions alongside each last checkpoint.
            # Compare versions inside compute; never substitute a different GPU/stack.
            fit_tokens = (mdir / name / 'env.txt').read_text().split()
            for key in ('python', 'torch', 'cuda', 'timm', 'numpy', 'pillow'):
                assert key in fit_tokens and fit_tokens[fit_tokens.index(key) + 1] == runtime_values[key], \
                    ('fit software build differs', name, key)
            assert cfg['expected_gpu'] in (mdir / name / 'gpu.txt').read_text(), 'fit GPU differs'
            run([sys.executable, '-I', cfg['scripts']['gate']['path'], '--tar', model['path'],
                 '--code', str(tree / 'pn1/code'), '--manifest', model['gate_manifest'],
                 '--out', str(gateout), '--workers', '7'], env=fit_env,
                logfile=output / (name + '_gate.log'))
            gate = json.loads((gateout / ('gate_' + name + '.json')).read_text())
            assert gate['verdict'] == 'passed' and gate['n_differ'] == 0 and gate['max_abs'] == 0
            assert gate['n'] == model['gate_rows'] and gate['tar_sha256'] == model['sha256']
            assert gate['manifest'] == model['gate_manifest'] and gate['device'] == cfg['expected_gpu']
            record['gate'] = 'passed'
        except (subprocess.CalledProcessError, AssertionError, FileNotFoundError) as error:
            record.update(gate='refused', error=type(error).__name__)
            failures += 1
            summary['models'].append(record)
            if (gateout / ('gate_' + name + '.json')).exists():
                shutil.copyfile(gateout / ('gate_' + name + '.json'), output / ('gate_' + name + '.json'))
            preserve_partial()
            continue
        shutil.copyfile(gateout / ('gate_' + name + '.json'), output / ('gate_' + name + '.json'))
        for family in cfg['families']:
            data = roots[family['root']]
            manifest = data / 'manifests' / family['manifest']
            env = dict(base, SMAD_DATA=str(data))
            target = output / (name + '__' + family['family'] + '.npz')
            command = [sys.executable, '-I', cfg['scripts']['wrapper']['path'], cfg['scripts']['rescore']['path'],
                       '--resdir', str(mdir / name), '--code', str(tree / 'pn1/code'),
                       '--manifest', family['manifest'], '--fam', family['family'], '--out', str(target), '--workers', '7']
            try:
                if not smoke_done:
                    # Eight real rows, same scorer command and family, scratch-only output.
                    sample = [r for r in csv.DictReader(manifest.open()) if r['fam'] == family['family']][:8]
                    sman = data / 'manifests/supplement_smoke.csv'
                    with sman.open('w', newline='') as f:
                        w = csv.DictWriter(f, fieldnames=list(sample[0])); w.writeheader(); w.writerows(sample)
                    smoke = work / 'smoke.npz'
                    scmd = command.copy()
                    scmd[scmd.index('--manifest') + 1] = sman.name
                    scmd[scmd.index('--out') + 1] = str(smoke)
                    run(scmd, env=env, logfile=output / 'eight_row_smoke.log')
                    run([sys.executable, '-I', str(stage / 'validate_family.py'), '--manifest', str(sman),
                         '--family', family['family'], '--scores', str(smoke), '--seed', str(model['seed']),
                         '--rows', '8'], logfile=output / 'eight_row_smoke.log')
                    smoke_done = True
                run(command, env=env, logfile=output / (name + '_scoring.log'))
                run([sys.executable, '-I', str(stage / 'validate_family.py'), '--manifest', str(manifest),
                     '--family', family['family'], '--scores', str(target), '--seed', str(model['seed']),
                     '--rows', str(family['rows'])], logfile=output / (name + '_scoring.log'))
                record['families'].append({'name': family['family'], 'valid': True, 'sha256': sha(target)})
            except (subprocess.CalledProcessError, AssertionError, FileNotFoundError) as error:
                failures += 1
                record['families'].append({'name': family['family'], 'valid': False, 'error': type(error).__name__})
            preserve_partial(active=record)
        summary['models'].append(record)
        preserve_partial()
    summary.update(finished=datetime.datetime.now().astimezone().isoformat(), failures=failures,
                   eight_row_smoke_passed=smoke_done)
    (output / 'technical_status.json').write_text(json.dumps(summary, indent=2) + '\n')
    # Only newly computed row-ID-keyed outputs and technical metadata leave the node.
    # Fit-time scores, weights, input manifests and private MEDS identifiers do not.
    archive = work / (outname + '.tar')
    run(['tar', '-cf', str(archive), '-C', str(output), '.'])
    digest = sha(archive)
    results.mkdir(exist_ok=True, parents=True)
    part = results / (outname + '.tar.part')
    assert not part.exists(), 'existing partial result; do not overwrite'
    shutil.copyfile(archive, part)
    assert sha(part) == digest
    part.rename(results / archive.name)
    (results / (archive.name + '.sha256')).write_text(digest + '  ' + archive.name + '\n')
    print('SUPPLEMENT_DONE', 'failures', failures, 'archive_sha256', digest, flush=True)
    sys.exit(0 if failures == 0 and smoke_done else 4)


if __name__ == '__main__':
    main()
