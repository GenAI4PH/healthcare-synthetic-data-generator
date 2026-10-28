"""Exclusive run ownership and validation inventories.

Lock acquisition uses O_EXCL; locks are intentionally not stolen automatically.
"""
from __future__ import annotations
import contextlib
import hashlib
import json
import os
import socket
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .setup import SetupError


def now():
    return datetime.now(timezone.utc).isoformat()


@contextlib.contextmanager
def run_lock(run_dir: Path):
    lock = Path(run_dir) / '.hsg-run.lock'
    info = {'pid': os.getpid(), 'hostname': socket.gethostname(), 'created_at_utc': now(), 'token': uuid.uuid4().hex}
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise SetupError(f'Run already locked: {lock}. Inspect process ownership before manually removing a stale lock.') from exc
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(info, f)
        yield
    finally:
        # Only delete our own lock; never remove a replacement lock.
        try:
            if json.loads(lock.read_text(encoding='utf-8')).get('token') == info['token']:
                lock.unlink()
        except (FileNotFoundError, OSError, ValueError):
            pass


def inventory(folder: Path) -> dict:
    """Inventory exported data only; omit manifests and transient files."""
    results = []
    for p in sorted(folder.rglob('*')):
        if not p.is_file():
            continue
        if p.is_symlink():
            raise SetupError(f'Symlink in generated output: {p}')
        h = hashlib.sha256()
        with p.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(block)
        results.append({'path': p.relative_to(folder).as_posix(), 'bytes': p.stat().st_size, 'sha256': h.hexdigest()})
    return {'status': 'passed', 'validated_at_utc': now(), 'file_count': len(results), 'files': results}


def check_csv_relationships(folder: Path) -> dict:
    """Check Synthea patient/encounter references for a single CSV export tree.

    Files without the relevant columns are skipped. This is not a complete
    healthcare schema/conformance validator.
    """
    import csv
    folder = Path(folder)
    patients = folder / 'patients.csv'
    encounters = folder / 'encounters.csv'
    if not patients.is_file():
        raise SetupError(f'Missing {patients}')

    def read(path):
        with path.open(encoding='utf-8-sig', newline='') as f:
            yield from csv.DictReader(f)

    patient_ids = set()
    for row in read(patients):
        v = (row.get('Id') or '').strip()
        if not v or v in patient_ids:
            raise SetupError(f'Blank or duplicate patient ID in {patients}: {v!r}')
        patient_ids.add(v)
    encounter_ids = set()
    checked = 0
    if encounters.is_file():
        for row in read(encounters):
            e = (row.get('Id') or '').strip()
            p = (row.get('PATIENT') or '').strip()
            if not e or e in encounter_ids:
                raise SetupError(f'Blank or duplicate encounter ID in {encounters}: {e!r}')
            if p not in patient_ids:
                raise SetupError(f'Unknown PATIENT {p!r} in {encounters}')
            encounter_ids.add(e)
            checked += 1
    rows_checked = 0
    for path in sorted(folder.glob('*.csv')):
        if path.name in ('patients.csv', 'encounters.csv'):
            continue
        with path.open(encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream)
            cols = set(reader.fieldnames or ())
            if 'PATIENT' not in cols and 'ENCOUNTER' not in cols:
                continue
            for row in reader:
                p = (row.get('PATIENT') or '').strip()
                e = (row.get('ENCOUNTER') or '').strip()
                if 'PATIENT' in cols and p and p not in patient_ids:
                    raise SetupError(f'Unknown PATIENT {p!r} in {path}')
                # Some Synthea clinical rows legitimately have no encounter.
                if 'ENCOUNTER' in cols and e and e not in encounter_ids:
                    raise SetupError(f'Unknown ENCOUNTER {e!r} in {path}')
                rows_checked += 1
    return {'status': 'passed', 'patient_ids': len(patient_ids), 'encounter_ids': len(encounter_ids), 'encounters_checked': checked, 'related_rows_checked': rows_checked}
