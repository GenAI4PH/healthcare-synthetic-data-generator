from pathlib import Path
from typer.testing import CliRunner
import pytest
from healthcare_generator.cli import app
from healthcare_generator.setup import load_settings, SetupError, OFFICIAL_REPO

runner = CliRunner()


def test_requires_pinned_revision(tmp_path: Path):
    config = tmp_path / "generator.yaml"
    config.write_text(f"synthea:\n  source_repo: {OFFICIAL_REPO}\n  version: null\n")
    with pytest.raises(SetupError, match="synthea.version"):
        load_settings(config)


def test_disallows_unofficial_repository(tmp_path: Path):
    config = tmp_path / "generator.yaml"
    config.write_text("synthea:\n  source_repo: https://example.com/test.git\n  version: v1.0.0\n")
    with pytest.raises(SetupError, match="official"):
        load_settings(config)


def test_dry_run_has_no_install(tmp_path: Path):
    config = tmp_path / "generator.yaml"
    config.write_text(f"synthea:\n  source_repo: {OFFICIAL_REPO}\n  install_dir: ./external/synthea\n  version: v1.0.0\n")
    result = runner.invoke(app, ["setup-synthea", "--config", str(config)])
    assert result.exit_code == 0, result.output
    assert "Dry run only" in result.output
    assert not (tmp_path / "external").exists()
