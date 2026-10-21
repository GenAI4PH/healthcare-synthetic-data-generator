import json
import os
from pathlib import Path
from unittest.mock import patch
import pytest
from healthcare_generator.states import normalized_state
from healthcare_generator.setup import SetupError, synthea_process_env
from healthcare_generator.generate import prepare
from healthcare_generator import batch

@pytest.mark.parametrize('source,expected', [('NJ','New Jersey'),('nj','New Jersey'),('New Jersey','New Jersey'),('ca','California'),('MA','Massachusetts')])
def test_state_aliases(source,expected):
    assert normalized_state(source) == expected

@pytest.mark.parametrize('source', ['ZZ', '', 'New Zersey', None])
def test_invalid_state(source):
    with pytest.raises(SetupError): normalized_state(source)

def test_dedicated_jdk_without_global_mutation(tmp_path):
    jdk_home = tmp_path / "jdk17"
    original_java_home = os.environ.get("JAVA_HOME")

    with patch.dict(os.environ, {
        "HSG_JAVA_HOME": str(jdk_home),
        "JAVA_HOME": "original-java"
    }):
        env = synthea_process_env()

        assert env["JAVA_HOME"] == str(jdk_home)
        assert env["PATH"].split(os.pathsep)[0] == str(jdk_home / "bin")

        # Verify subprocess configuration doesn't change global JAVA_HOME
        assert os.environ["JAVA_HOME"] == "original-java"

    assert os.environ.get("JAVA_HOME") == original_java_home

def test_single_run_normalizes_state(tmp_path):
    config=tmp_path/'config'/'generator.yaml'; config.parent.mkdir()
    config.write_text('synthea:\n  install_dir: ./external/synthea\n  source_repo: https://github.com/synthetichealth/synthea.git\n  version: v4.0.0\n')
    assert prepare(config, 'csv', 10, 'NJ', None)['state']=='New Jersey'


@pytest.mark.parametrize('resume', [False, True])
def test_batch_uses_dedicated_jdk_for_every_subprocess(tmp_path, monkeypatch, resume):
    jdk_home = tmp_path / 'jdk17'
    monkeypatch.setenv('HSG_JAVA_HOME', str(jdk_home))
    monkeypatch.setenv('JAVA_HOME', 'jdk26')
    original_path = os.environ['PATH']
    run_dir = tmp_path / 'run'
    run_dir.mkdir()
    manifest = {
        'schema_version': 1, 'format': 'csv',
        'status': 'failed' if resume else 'running',
        'synthea_revision': 'v4.0.0', 'synthea_commit': 'pinned-commit',
        'requested_living_population': 2,
        'batches': [
            {'id': str(i), 'state': 'New Jersey', 'patients': 1, 'seed': i,
             'status': 'failed' if resume else 'pending'}
            for i in (1, 2)
        ],
    }
    (run_dir / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    monkeypatch.setattr(batch, '_source', lambda config: (tmp_path, 'v4.0.0', 'pinned-commit'))
    monkeypatch.setattr(batch, '_gradle', lambda target: ['gradle'])
    monkeypatch.setattr(batch, 'validate_output', lambda folder, fmt: {'patient_rows': 1, 'files': 1})

    with patch.object(batch.subprocess, 'run') as launch:
        launch.return_value.returncode = 0
        result = batch.execute(tmp_path / 'config.yaml', run_dir, approved=True, resume=resume)

    assert result['status'] == 'completed'
    assert launch.call_count == 2
    for call in launch.call_args_list:
        env = call.kwargs['env']
        assert env['JAVA_HOME'] == str(jdk_home)
        assert env['PATH'].split(os.pathsep)[0] == str(jdk_home / 'bin')
    assert os.environ['JAVA_HOME'] == 'jdk26'
    assert os.environ['PATH'] == original_path
