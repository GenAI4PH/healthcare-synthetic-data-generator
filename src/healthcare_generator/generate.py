"""Single-run format generation through the user's pinned external Synthea checkout."""
from __future__ import annotations
import csv
import json
import re
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .setup import synthea_process_env, SetupError, load_settings, check_prerequisites, run_command, OFFICIAL_REPO
from .verify import _gradle
from .states import normalized_state

FORMATS = ('csv', 'fhir', 'ccda')
PRESETS = (10, 1000, 100000, 1000000)
FLAGS = {'csv':'exporter.csv.export', 'fhir':'exporter.fhir.export', 'ccda':'exporter.ccda.export'}


def prepare(config: Path, fmt: str, patients: int, state: str, seed: int | None,
            output_root: Path | None = None) -> dict:
    if fmt not in FORMATS:
        raise SetupError(f'Unsupported format: {fmt}')
    if patients < 1 or patients > 1000000:
        raise SetupError('Patients must be between 1 and 1,000,000')
    state = normalized_state(state)
    if seed is not None and (seed < 0 or seed > 2**63-1):
        raise SetupError('Seed must be a nonnegative signed 64-bit integer')
    install_dir, revision = load_settings(config)
    root = config.resolve().parent.parent
    if output_root is None:
        output_root = root / 'output' / 'runs'
    elif not output_root.is_absolute():
        output_root = root / output_root
    # Distinct run folder: never mix results or overwrite a previous run.
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
    return {'install_dir': install_dir, 'revision': revision, 'format': fmt,
            'patients': patients, 'state': state, 'seed': seed,
            'output_dir': output_root.resolve() / fmt / run_id,
            'run_id': run_id}


def validate_output(out_dir: Path, fmt: str) -> dict:
    folder = out_dir / fmt
    if fmt == 'csv':
        file = folder / 'patients.csv'
        if not file.is_file():
            raise SetupError(f'CSV output missing: {file}')
        with file.open('r', encoding='utf-8-sig', newline='') as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or 'Id' not in reader.fieldnames:
                raise SetupError('CSV patients.csv missing Id header')
            rows = sum(1 for r in reader if r.get('Id'))
        if rows == 0:
            raise SetupError('No patient rows in CSV output')
        return {'patient_rows': rows, 'files': len(list(folder.glob('*.csv')))}
    suffix = '*.json' if fmt == 'fhir' else '*.xml'
    files = sorted(folder.glob(suffix)) if folder.exists() else []
    if not files:
        raise SetupError(f'No {fmt} files found under {folder}')
    if fmt == 'fhir':
        # Parsing one file confirms that the exported data is JSON; supplemental metadata may also exist.
        with files[0].open(encoding='utf-8-sig') as handle:
            document = json.load(handle)
        if not isinstance(document, dict) or 'resourceType' not in document:
            raise SetupError('FHIR output does not have resourceType')
    else:
        import xml.etree.ElementTree as ET
        ET.parse(files[0])
    return {'files': len(files)}


def run(config: Path, fmt: str, patients: int, state: str, seed: int | None = None,
        output_root: Path | None = None, approved: bool = False) -> dict:
    spec = prepare(config, fmt, patients, state, seed, output_root)
    if not approved:
        raise SetupError('Explicit approval required before running Synthea')
    check_prerequisites()
    target = spec['install_dir']
    if not (target / '.git').is_dir():
        raise SetupError('Official Synthea checkout missing; run hsg setup-synthea --approve')
    if run_command(['git', 'remote', 'get-url', 'origin'], cwd=target) != OFFICIAL_REPO:
        raise SetupError('Unexpected Synthea origin')
    head = run_command(['git', 'rev-parse', 'HEAD'], cwd=target)
    expected = run_command(['git', 'rev-parse', '--verify', f"{spec['revision']}^{{commit}}"], cwd=target)
    if head != expected:
        raise SetupError('Installed Synthea does not match configured revision')
    out_dir = spec['output_dir']
    out_dir.mkdir(parents=True, exist_ok=False)
    manifest_path = out_dir / 'manifest.json'
    manifest = {'created_at_utc': datetime.now(timezone.utc).isoformat(),
                'run_id':spec['run_id'], 'status':'running',
                'synthea_commit':head, 'synthea_revision':spec['revision'],
                'format':fmt, 'requested_living_population':patients,
                'state':spec['state'], 'seed':seed, 'output_dir':str(out_dir)}
    def write_manifest():
        temporary = manifest_path.with_suffix('.tmp')
        temporary.write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
        temporary.replace(manifest_path)
    write_manifest()
    try:
        flags = [f'--{v}={str(k==fmt).lower()}' for k,v in FLAGS.items()]
        args = ['-p', str(patients), *flags, '--exporter.fhir_stu3.export=false',
                '--exporter.fhir_dstu2.export=false', '--exporter.fhir.bulk_data=false',
                '--exporter.csv.append_mode=false', f'--exporter.baseDirectory={out_dir}']
        if seed is not None:
            args.extend(['-s', str(seed)])
        args.append(spec['state'])
        params = '[' + ','.join("'" + x.replace('\\', '\\\\').replace("'", "\\'") + "'" for x in args) + ']'
        command = _gradle(target) + ['run', f'-Params={params}', '--no-daemon']
        result = subprocess.run(command, cwd=target, check=False, env=synthea_process_env())
        if result.returncode:
            raise SetupError(f'Synthea run failed (exit {result.returncode}); partial output retained: {out_dir}')
        manifest['actual_output'] = validate_output(out_dir, fmt)
        manifest['status'] = 'completed'
        manifest['completed_at_utc'] = datetime.now(timezone.utc).isoformat()
        write_manifest()
    except Exception as exc:
        manifest['status'] = 'failed'
        manifest['error'] = str(exc)
        manifest['failed_at_utc'] = datetime.now(timezone.utc).isoformat()
        write_manifest()
        raise
    return manifest
