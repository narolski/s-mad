"""Opaque integrity only. Never imports a reader or parses archive members.

Runs on the DGX. Current hashes/sidecars establish bytes, not scientific admission.
The existing independent 49-path receipt supplies expected dependency hashes.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path('/home/narolski/smad-next')
DELIVERY = ROOT / 'experiments/AGENTIC_delivery_20261114'
INTEGRITY = DELIVERY / 'OPENCODE_BATCHC_B2_INDEPENDENT_LOGS_20261114/integrity.json'
COLLECTION = ROOT / 'experiments/RECORDS_ledger/codex_20261114/NEW_COLLECTION_VERIFIED.json'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def opaque(path):
    """No archive decoding; sidecar must identify its exact basename."""
    sidecar = path.with_name(path.name + '.sha256')
    row = {'path': str(path), 'resolved': str(path.resolve()),
           'sidecar': str(sidecar), 'exists': path.is_file(),
           'sidecar_exists': sidecar.is_file()}
    if not row['exists'] or not row['sidecar_exists']:
        return dict(row, passed=False, reason='missing archive or sidecar')
    before = path.stat()
    value = digest(path)
    after = path.stat()
    text = sidecar.read_text()
    lines = text.splitlines()
    match = re.fullmatch(r'([0-9a-f]{64}) [ *](.+)', lines[0]) if len(lines) == 1 else None
    side_ok = bool(match and match[1] == value and Path(match[2]).name == path.name)
    stable = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    return dict(row, bytes=after.st_size, sha256=value,
                sidecar_sha256=digest(sidecar), sidecar_names_archive=bool(
                    match and Path(match[2]).name == path.name),
                unchanged_during_hash=stable, passed=side_ok and stable)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True, type=Path)
    a = ap.parse_args()
    if os.path.lexists(a.out):
        raise FileExistsError(a.out)
    started = datetime.now(timezone.utc).isoformat()
    prior = json.loads(INTEGRITY.read_text())
    collection = json.loads(COLLECTION.read_text())
    collected = {Path(x['path']).name: x for x in collection['archives']}
    dependencies = []
    for expected in prior['checks']:
        p = Path(expected['path'])
        actual = digest(p)
        dependencies.append(dict(path=str(p), resolved=str(p.resolve()),
                                 expected_sha256=expected['sha256'], sha256=actual,
                                 passed=actual == expected['sha256']))
    archives = []
    for prefix, arms, directory in (
        ('AB1C', ('SpV', 'BN', 'BV'), Path('/mnt/t7/smad_next/coordination_20261114/archives/AB1C')),
        ('AB1', ('Sb', 'B', 'Sp'), Path('/mnt/t7/smad_next/AB1/results'))):
        for arm in arms:
            for seed in range(408, 413):
                p = directory / f'{prefix}_{arm}_s{seed}.tar'
                row = dict(opaque(p), arm=arm, seed_requested=seed,
                           native_identity='NOT_INSPECTED')
                source = collected.get(p.name)
                if source:
                    row['collection'] = source
                    row['collection_at'] = collection['at']
                    row['collection_matches'] = (
                        source['path'] == str(p) and source['sha256'] == row.get('sha256')
                        and source['bytes'] == row.get('bytes'))
                    row['passed'] = row['passed'] and row['collection_matches']
                else:
                    row['collection_provenance'] = 'NOT_BOUND_BY_THIS_COLLECTION_RECEIPT'
                archives.append(row)
    journal = Path('/mnt/t7/smad_next/AB1/READ_ONCE_PM3')
    absence = {str(journal / name): not os.path.lexists(journal / name)
               for name in ('C.claim.json', 'C.complete.json')}
    report = dict(
        schema='batchc-opaque-audit-v1', started_utc=started,
        finished_utc=datetime.now(timezone.utc).isoformat(),
        head=subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
        script_sha256=digest(Path(__file__)),
        scope='Byte integrity and metadata only; no archive member or numerical reference parsing.',
        candidate_payloads_opened=False, native_reader_invoked=False,
        scientific_admission=False, production_release=False,
        prior_integrity_receipt=dict(path=str(INTEGRITY), sha256=digest(INTEGRITY)),
        collection_receipt=dict(path=str(COLLECTION), sha256=digest(COLLECTION)),
        dependencies=dependencies, archives=archives, journal_absence=absence,
        all_byte_checks_passed=all(x['passed'] for x in dependencies + archives),
        remaining=['Independent review and committed source/release binding.',
                   'Comparator authoritative collection provenance not established by sidecars alone.',
                   'All arrival/completion dispositions must be bound by lead.',
                   'Native identity/order/fit checks remain for authorized guarded first read.',
                   'Fresh output/journal absence and exact command/environment at release.',
                   'Independent results review; retain failures and every seed.'])
    with a.out.open('x') as f:
        json.dump(report, f, indent=2, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps(dict(output=str(a.out), sha256=digest(a.out),
                          dependencies=len(dependencies), archives=len(archives),
                          all_byte_checks_passed=report['all_byte_checks_passed'],
                          journal_absent=all(absence.values()), production_release=False)))
    if not report['all_byte_checks_passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
