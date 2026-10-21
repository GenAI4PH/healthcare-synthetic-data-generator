"""Approved local build and smoke test of an already installed official Synthea checkout."""
from __future__ import annotations
import csv
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
import subprocess
from .setup import synthea_process_env, SetupError, load_settings, run_command, check_prerequisites


def _gradle(install_dir: Path) -> list[str]:
    wrapper = install_dir / ('gradlew.bat' if platform.system() == 'Windows' else 'gradlew')
    if not wrapper.is_file():
        raise SetupError(f'Upstream Gradle wrapper missing: {wrapper}')
    if platform.system() == 'Windows':
        return ['cmd', '/c', str(wrapper)]
    return ['sh', str(wrapper)]


def _checked(args: list[str], cwd: Path) -> None:
    # Inherit terminal output for long-running Gradle builds and useful diagnostics.
    result = subprocess.run(args, cwd=cwd, check=False, env=synthea_process_env())
    if result.returncode:
        raise SetupError(f'Upstream process exited with status {result.returncode}')


def verify(config_path: Path, *, approved: bool = False, patients: int = 10,
           state: str = 'Massachusetts') -> dict:
    if not approved:
        raise SetupError('Explicit approval is required before Gradle downloads/builds and sample generation')
    if not 1 <= patients <= 100:
        raise SetupError('Smoke-test patient count must be between 1 and 100')
    check_prerequisites()
    target, revision = load_settings(config_path)
    if not (target / '.git').is_dir():
        raise SetupError('Synthea is not installed. Run hsg setup-synthea --approve first')
    source = run_command(['git', 'remote', 'get-url', 'origin'], cwd=target)
    if source != 'https://github.com/synthetichealth/synthea.git':
        raise SetupError('Unexpected Synthea upstream remote')
    installed = run_command(['git', 'rev-parse', 'HEAD'], cwd=target)
    expected = run_command(['git', 'rev-parse', '--verify', f'{revision}^{{commit}}'], cwd=target)
    if installed != expected:
        raise SetupError('Installed Synthea commit does not match configured revision')
    root = config_path.resolve().parent.parent
    out_dir = (root / 'output' / 'smoke-test').resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    # Keep previous generated files out of the verification count.
    for candidate in out_dir.rglob('*'):
        if candidate.is_file():
            raise SetupError(f'Smoke-test output directory must be empty: {out_dir}')
    gradle = _gradle(target)
    _checked(gradle + ['classes', '--no-daemon'], target)
    # Synthea's Gradle run integration accepts CLI arguments through the Params property.
    # Passing through a dedicated Gradle invocation works on Windows/macOS/Linux.
    args = [f'-p', str(patients), '--exporter.csv.export=true', '--exporter.fhir.export=false',
            '--exporter.ccda.export=false', f'--exporter.baseDirectory={out_dir}', state]
    params = '[' + ','.join("'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'" for s in args) + ']'
    _checked(gradle + ['run', f'-Params={params}', '--no-daemon'], target)
    csv_dir = out_dir / 'csv'
    patients_file = csv_dir / 'patients.csv'
    if not patients_file.is_file():
        raise SetupError(f'CSV smoke test failed: patients.csv not found at {patients_file}')
    with patients_file.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or 'Id' not in reader.fieldnames:
            raise SetupError('CSV smoke test failed: expected patient Id header missing')
        rows = sum(1 for _ in reader)
    if rows < 1:
        raise SetupError('CSV smoke test failed: no patient rows')
    result = {'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'configured_revision': revision,
              'commit': installed, 'requested_population': patients, 'exported_patient_rows': rows,
              'state': state, 'csv_file': str(patients_file), 'passed': True}
    report = out_dir / 'smoke-test-report.json'
    report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result
