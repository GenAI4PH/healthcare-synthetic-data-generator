import json
import os
from pathlib import Path
from unittest.mock import patch
import pytest
from healthcare_generator.states import normalized_state
from healthcare_generator.setup import SetupError, synthea_process_env
from healthcare_generator.generate import prepare

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
