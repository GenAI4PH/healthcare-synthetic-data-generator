"""Durable sequential Synthea batch runner; upstream source remains external.

A completed batch is immutable. Retry resumes only failed/unstarted batches.
CSV merge is non-destructive and preserves individual batch files.
"""
from __future__ import annotations
import csv
import json
import os
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .generate import FLAGS, FORMATS, validate_output
from .setup import synthea_process_env, SetupError, OFFICIAL_REPO, check_prerequisites, load_settings, run_command
from .verify import _gradle

from .states import US_STATES, normalized_state
from .run_integrity import run_lock, inventory, check_csv_relationships


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def allocation(states: list[str], patients: int, mode: str) -> dict[str, int]:
    if patients < 1 or patients > 1_000_000:
        raise SetupError('patients must be between 1 and 1,000,000')
    if mode not in ('total', 'per-state'):
        raise SetupError('allocation mode must be total or per-state')
    if len(set(states)) != len(states) or not states:
        raise SetupError('states must be unique and nonempty')
    if mode == 'per-state':
        if patients * len(states) > 1_000_000:
            raise SetupError('Total requested population exceeds 1,000,000')
        return {s: patients for s in states}
    if patients < len(states):
        raise SetupError('Total patients must be >= number of selected states')
    q, r = divmod(patients, len(states))
    return {s: q + (i < r) for i, s in enumerate(states)}


def plan(fmt: str, patients: int, state: str | None = None, all_states: bool = False,
         allocation_mode: str = 'total', batch_size: int = 1000,
         seed: int | None = None) -> list[dict]:
    if fmt not in FORMATS:
        raise SetupError('Choose csv, fhir, or ccda')
    if all_states and state:
        raise SetupError('Use --state OR --all-states')
    if not 1 <= batch_size <= 10000:
        raise SetupError('Batch size must be 1..10,000; use smaller batches for limited RAM')
    if seed is not None and not 0 <= seed <= 2**63-1:
        raise SetupError('Seed must fit signed 64-bit nonnegative range')
    states = list(US_STATES.values()) if all_states else [normalized_state(state or 'Massachusetts')]
    chunks = []
    for s, count in allocation(states, patients, allocation_mode).items():
        for n, offset in enumerate(range(0, count, batch_size)):
            batch_count = min(batch_size, count-offset)
            # Synthea seeds must differ to prevent repeated people across batches.
            # With no user seed use stable random seed per planned run; saved in manifest.
            chunks.append({'id': f'{list(US_STATES.values()).index(s)+1:02d}-{n+1:05d}',
                           'state':s, 'patients':batch_count, 'ordinal':len(chunks)})
    return chunks


def _write_json(path: Path, data: dict) -> None:
    temp = path.with_suffix('.tmp')
    with temp.open('w', encoding='utf-8') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    temp.replace(path)


def _source(config: Path) -> tuple[Path, str, str]:
    check_prerequisites()
    target, version = load_settings(config)
    if not (target/'.git').is_dir():
        raise SetupError('Synthea not installed: use hsg setup-synthea --approve')
    if run_command(['git','remote','get-url','origin'],cwd=target) != OFFICIAL_REPO:
        raise SetupError('Unexpected upstream repository')
    commit = run_command(['git','rev-parse','HEAD'],cwd=target)
    pinned = run_command(['git','rev-parse','--verify',f'{version}^{{commit}}'],cwd=target)
    if commit != pinned:
        raise SetupError('Synthea checkout does not match pinned configuration')
    return target, version, commit


def new_run(config: Path, fmt: str, patients: int, state: str | None, all_states: bool,
            allocation_mode: str, batch_size: int, seed: int | None,
            output_root: Path | None) -> tuple[Path, dict]:
    jobs = plan(fmt, patients, state, all_states, allocation_mode, batch_size, seed)
    root = config.resolve().parent.parent
    dest = (output_root or root/'output'/'runs')
    if not dest.is_absolute():
        dest = root/dest
    name = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
    run_dir = dest.resolve()/fmt/name
    if run_dir.exists():
        raise SetupError('Run directory already exists')
    _, version, commit = _source(config)
    effective_seed = seed if seed is not None else int.from_bytes(os.urandom(7),'big')
    # Do not allow overflow as chunk ordinals increase.
    if effective_seed + len(jobs) > 2**63-1:
        raise SetupError('Seed too close to signed 64-bit maximum for number of batches')
    manifest = {'schema_version':1, 'run_id':name, 'created_at_utc':utcnow(), 'status':'running',
                'format':fmt, 'requested_living_population':sum(j['patients'] for j in jobs),
                'allocation':allocation_mode, 'all_states':all_states, 'batch_size':batch_size,
                'base_seed':effective_seed,'synthea_revision':version,'synthea_commit':commit,
                'batches':[{**j, 'seed':effective_seed+j['ordinal']+1, 'status':'pending'} for j in jobs]}
    run_dir.mkdir(parents=True)
    _write_json(run_dir/'manifest.json',manifest)
    return run_dir, manifest


def _read_manifest(run_dir: Path) -> dict:
    mpath = run_dir/'manifest.json'
    if not mpath.is_file():
        raise SetupError(f'Missing run manifest: {mpath}')
    data=json.loads(mpath.read_text(encoding='utf-8'))
    if data.get('schema_version') != 1 or data.get('format') not in FORMATS:
        raise SetupError('Unsupported run manifest version/format')
    return data


def _params(args: list[str]) -> str:
    return '['+','.join("'"+s.replace('\\','\\\\').replace("'","\\'")+"'" for s in args)+']'


def execute(config: Path, run_dir: Path, approved: bool = False, resume: bool = False) -> dict:
    if not approved:
        raise SetupError('Explicit --approve required to execute Synthea')
    with run_lock(Path(run_dir).resolve()):
        return _execute_locked(config, run_dir, approved=approved, resume=resume)


def _execute_locked(config: Path, run_dir: Path, approved: bool = False, resume: bool = False) -> dict:
    if not approved:
        raise SetupError('Explicit --approve required to execute Synthea')
    run_dir=run_dir.resolve()
    manifest=_read_manifest(run_dir)
    target, ver, commit=_source(config)
    if manifest['synthea_commit'] != commit or manifest['synthea_revision'] != ver:
        raise SetupError('Pinned Synthea version differs from the run manifest')
    if manifest['status']=='completed':
        return manifest

    if not resume and any(b['status']!='pending' for b in manifest['batches']):
        raise SetupError('Run already started; use --resume to retry incomplete batches')
    fmt=manifest['format']
    gradle=_gradle(target)
    for b in manifest['batches']:
        if b['status']=='completed':
            # Revalidate completed batch before trusting it during resume.
            validate_output(run_dir/'batches'/b['id'],fmt,expected_living=b['patients'])
            continue
        folder=run_dir/'batches'/b['id']
        if folder.exists():
            # Never reuse partial output; move it aside for forensic investigation.
            archive=run_dir/'incomplete'/f"{b['id']}-{uuid.uuid4().hex[:6]}"
            archive.parent.mkdir(parents=True,exist_ok=True)
            folder.rename(archive)
        folder.mkdir(parents=True)
        b['status']='running'; b['started_at_utc']=utcnow()
        _write_json(run_dir/'manifest.json',manifest)
        flags=[f'--{flag}={str(name==fmt).lower()}' for name,flag in FLAGS.items()]
        args=['-p',str(b['patients']),'-s',str(b['seed']),*flags,
              '--exporter.fhir_stu3.export=false','--exporter.fhir_dstu2.export=false',
              '--exporter.fhir.bulk_data=false','--exporter.csv.append_mode=false',
              f'--exporter.baseDirectory={folder}',b['state']]
        command=gradle+['run',f'-Params={_params(args)}','--no-daemon']
        try:
            result=subprocess.run(command,cwd=target,check=False,env=synthea_process_env())
            if result.returncode:
                raise SetupError(f'Synthea batch {b["id"]} exited with {result.returncode}')
            b['actual_output']=validate_output(folder,fmt,expected_living=b['patients'])
            b['validation'] = inventory(folder / fmt)
            b['status']='completed'; b['completed_at_utc']=utcnow()
        except Exception as exc:
            b['status']='failed';b['error']=str(exc);manifest['status']='failed'
            _write_json(run_dir/'manifest.json',manifest)
            raise
        _write_json(run_dir/'manifest.json',manifest)
    manifest['status']='completed';manifest['completed_at_utc']=utcnow()
    manifest['validation'] = {'status': 'passed', 'completed_batches': len(manifest['batches'])}
    manifest['summary']={'completed_batches':len(manifest['batches']),
                         'requested_living_population':manifest['requested_living_population'],
                         'csv_exported_patient_rows':sum(b['actual_output'].get('patient_rows',0) for b in manifest['batches']) if fmt=='csv' else None,
                         'exported_files':sum(b['actual_output'].get('files',0) for b in manifest['batches'])}
    _write_json(run_dir/'manifest.json',manifest)
    return manifest


def merge_csv(run_dir: Path) -> dict:
    """Merge matching CSV filenames with one header. Atomic publish after validations.

    Does not rewrite identifiers, deduplicate records, or remove input batches.
    """
    run_dir=run_dir.resolve()
    manifest=_read_manifest(run_dir)
    if manifest['status']!='completed' or manifest['format']!='csv':
        raise SetupError('Only fully completed CSV runs can be merged')
    target=run_dir/'merged'/'csv'
    if target.exists():
        raise SetupError('Merged destination already exists; refusing to overwrite')
    staging=run_dir/f'.merge-{uuid.uuid4().hex}'
    staging.mkdir()
    batch_paths=[run_dir/'batches'/b['id']/'csv' for b in manifest['batches']]
    try:
        names=sorted({p.name for base in batch_paths for p in base.glob('*.csv')})
        if not names or 'patients.csv' not in names:
            raise SetupError('CSV source files missing')
        summaries={}
        for name in names:
            header=None;rows=0
            with (staging/name).open('w',encoding='utf-8',newline='') as out:
                writer=csv.writer(out)
                for base in batch_paths:
                    path=base/name
                    if not path.exists():
                        continue
                    with path.open('r',encoding='utf-8-sig',newline='') as src:
                        reader=csv.reader(src)
                        first=next(reader,None)
                        if not first:
                            continue
                        if header is None:
                            header=first;writer.writerow(header)
                        elif header!=first:
                            raise SetupError(f'CSV header mismatch: {name} in {base}')
                        for row in reader:
                            if len(row)!=len(header):
                                raise SetupError(f'Malformed CSV row in {path}')
                            writer.writerow(row); rows+=1
            summaries[name]=rows
        target.parent.mkdir(parents=True,exist_ok=True)
        staging.rename(target)
        report={'merged_at_utc':utcnow(),'files':len(names),'rows_by_file':summaries,
                'warning':'No deduplication or foreign-key reconstruction is performed.'}
        _write_json(run_dir/'merge-report.json',report)
        return report
    finally:
        if staging.exists():
            import shutil
            shutil.rmtree(staging)
