from typer.testing import CliRunner
from healthcare_generator.cli import app

runner = CliRunner()

def test_doctor():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "Synthea installation is not attempted" in result.output

def test_missing_config():
    result = runner.invoke(app, ["config-show", "--path", "does-not-exist.yaml"])
    assert result.exit_code == 1
