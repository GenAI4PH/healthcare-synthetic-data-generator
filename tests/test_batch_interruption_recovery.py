"""Regression coverage for failure and recovery of a checkpointed batch run."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from healthcare_generator import batch
from healthcare_generator.setup import SetupError


def test_interrupted_batch_recovers_without_rerunning_completed_batch(tmp_path, monkeypatch):
    """First batch succeeds, second fails, resume archives partial second output."""
    run_dir = tmp_path / 'run'
    run_dir.mkdir()
    manifest = {
        'schema_version': 1,
        'run_id': 'test-recovery',
        'format': 'csv',
        'status': 'running',
        'synthea_revision': 'v4.0.0',
        'synthea_commit': 'test-commit',
        'requested_living_population': 2,
        'batches': [
            {'id': '01', 'state': 'New Jersey', 'patients': 1, 'seed': 111, 'status': 'pending'},
            {'id': '02', 'state': 'New Jersey', 'patients': 1, 'seed': 112, 'status': 'pending'},
        ],
    }
    (run_dir / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')

    monkeypatch.setattr(batch, '_source', lambda config: (tmp_path, 'v4.0.0', 'test-commit'))
    monkeypatch.setattr(batch, '_gradle', lambda target: ['gradle'])
    monkeypatch.setattr(batch, 'validate_output', lambda folder, fmt, expected_living=None: {
        'patient_rows': 1, 'living_patient_rows': 1, 'files': 1,
    })

    attempted = []
    fail_second_once = True

    def fake_run(command, **kwargs):
        nonlocal fail_second_once
        params = next(x for x in command if x.startswith('-Params='))

        # Normalize escaped Windows paths used in Gradle parameters.
        normalized_params = params.replace("\\\\", "/").replace("\\", "/")

        batch_id = None

        for candidate in ("01", "02"):
            if f"/batches/{candidate}" in normalized_params:
                batch_id = candidate
                break

        if batch_id is None:
            raise AssertionError(
                f"Unable to identify batch from Gradle parameters: {params}"
            )
        attempted.append(batch_id)
        export_dir = run_dir / 'batches' / batch_id / 'csv'
        export_dir.mkdir(parents=True, exist_ok=True)
        if batch_id == '02' and fail_second_once:
            fail_second_once = False
            (export_dir / 'partial.txt').write_text('incomplete', encoding='utf-8')
            return SimpleNamespace(returncode=1)
        (export_dir / 'patients.csv').write_text('Id,DEATHDATE\n' + batch_id + ',\n', encoding='utf-8')
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(batch.subprocess, 'run', fake_run)

    with pytest.raises(SetupError, match='batch 02 exited'):
        batch.execute(tmp_path / 'config.yaml', run_dir, approved=True)

    failed = json.loads((run_dir / 'manifest.json').read_text(encoding='utf-8'))
    assert failed['status'] == 'failed'
    assert [b['status'] for b in failed['batches']] == ['completed', 'failed']
    assert attempted == ['01', '02']
    first_output = (run_dir / 'batches' / '01' / 'csv' / 'patients.csv').read_bytes()
    assert (run_dir / 'batches' / '02' / 'csv' / 'partial.txt').exists()
    assert not (run_dir / '.hsg-run.lock').exists()

    complete = batch.execute(tmp_path / 'config.yaml', run_dir, approved=True, resume=True)

    assert complete['status'] == 'completed'
    assert [b['status'] for b in complete['batches']] == ['completed', 'completed']
    assert attempted == ['01', '02', '02'], 'completed first batch must not rerun'
    assert (run_dir / 'batches' / '01' / 'csv' / 'patients.csv').read_bytes() == first_output
    archives = list((run_dir / 'incomplete').glob('02-*'))
    assert len(archives) == 1
    assert (archives[0] / 'csv' / 'partial.txt').read_text(encoding='utf-8') == 'incomplete'
    assert (run_dir / 'batches' / '02' / 'csv' / 'patients.csv').is_file()
    assert not (run_dir / '.hsg-run.lock').exists()
    saved = json.loads((run_dir / 'manifest.json').read_text(encoding='utf-8'))
    assert saved['status'] == 'completed'
    assert saved['validation']['status'] == 'passed'
