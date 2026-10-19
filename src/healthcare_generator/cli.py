"""Phase-1 diagnostics only. Install/generate/upload added in future phases."""
import platform
import shutil
from pathlib import Path
import typer
import yaml

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

if __name__ == "__main__":
    app()
