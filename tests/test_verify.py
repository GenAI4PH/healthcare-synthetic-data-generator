from pathlib import Path
import pytest
from typer.testing import CliRunner
from healthcare_generator.cli import app
from healthcare_generator.verify import verify
from healthcare_generator.setup import SetupError

runner = CliRunner()

def test_verify_requires_approval(tmp_path: Path):
    with pytest.raises(SetupError, match='approval'):
        verify(tmp_path / 'does-not-exist.yaml')

def test_verify_preview_does_not_execute():
    result = runner.invoke(app, ['verify-synthea'])
    assert result.exit_code == 0
    assert 'Preview:' in result.output

def test_rejects_invalid_smoke_population(tmp_path: Path):
    with pytest.raises(SetupError, match='population|approval|patient count'):
        verify(tmp_path / 'missing.yaml', approved=True, patients=0)
