"""Cross-platform CLI; upstream Synthea remains an external dependency."""
import platform
import shutil
from pathlib import Path
import typer
import yaml
from .setup import SetupError, install, load_settings, check_prerequisites

app = typer.Typer(help="Healthcare Synthetic Data Generator orchestration CLI")

@app.command()
def doctor() -> None:
    """Check local prerequisites without modifying the machine."""
    typer.echo(f"OS: {platform.system()} ({platform.machine()})")
    typer.echo(f"Python: {platform.python_version()}")
    for executable in ("java", "git"):
        location = shutil.which(executable)
        typer.echo(f"{executable}: {location or 'NOT FOUND'}")
    typer.echo("Synthea installation is not attempted by this command.")

@app.command("config-show")
def config_show(path: Path = typer.Option(Path("config/generator.yaml"), "--path")) -> None:
    """Show the non-secret example generator configuration."""
    if not path.is_file():
        typer.echo(f"Config not found: {path}", err=True)
        raise typer.Exit(code=1)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    typer.echo(yaml.safe_dump(data, sort_keys=False))

@app.command("setup-synthea")
def setup_synthea(
    config: Path = typer.Option(Path("config/generator.yaml"), "--config"),
    approve: bool = typer.Option(False, "--approve", help="Approve download/update of official upstream repository"),
) -> None:
    """Install pinned upstream Synthea outside of the tracked repository files."""
    try:
        target, revision = load_settings(config)
        typer.echo(f"Official source: https://github.com/synthetichealth/synthea.git")
        typer.echo(f"Revision: {revision}\nDestination: {target}")
        if not approve:
            typer.echo("Dry run only. Re-run with --approve after reviewing network and disk changes.")
            return
        manifest = install(config, approved=True)
        typer.echo(f"Installed Synthea at commit: {manifest['commit']}")
        typer.echo("Next: build/run upstream Synthea smoke test (Phase 2 follow-up).")
    except SetupError as exc:
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(code=1) from exc

@app.command("verify-synthea")
def verify_synthea(
    config: Path = typer.Option(Path("config/generator.yaml"), "--config"),
    approve: bool = typer.Option(False, "--approve", help="Approve Gradle downloads, build and local synthetic patient generation"),
) -> None:
    """Build the pinned Synthea checkout and generate a 10-patient CSV smoke test."""
    from .verify import verify
    try:
        if not approve:
            typer.echo("Preview: build upstream Synthea with Gradle and generate 10 patients into output/smoke-test.")
            typer.echo("Gradle may download dependencies. This does not upload data.")
            typer.echo("Re-run with --approve to execute.")
            return
        report = verify(config, approved=True)
        typer.echo(f"PASS: {report['exported_patient_rows']} patient rows at {report['csv_file']}")
    except SetupError as exc:
        typer.echo(f"ERROR: {exc}", err=True)
        raise typer.Exit(code=1) from exc

if __name__ == "__main__":
    app()
