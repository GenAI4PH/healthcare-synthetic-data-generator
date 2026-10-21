"""Attach  storage CLI to existing Typer app."""
from pathlib import Path
import typer
from .setup import SetupError
from .storage import plan, upload


def register(app: typer.Typer) -> None:
    @app.command('storage-plan')
    def storage_plan(run_dir: Path = typer.Argument(..., help='Completed run folder'),
                     config: Path = typer.Option(Path('config/storage.yaml'), '--storage-config'),
                     provider: str | None = typer.Option(None, '--provider')) -> None:
        """Preview destination, file count and bytes without cloud access."""
        try:
            p = plan(run_dir, config, provider)
            typer.echo(f"Provider: {p['provider']}\nDestination: {p['destination']}")
            typer.echo(f"Files: {p['file_count']} | Bytes: {p['bytes']}")
        except (SetupError, OSError, ValueError) as exc:
            typer.echo(f'ERROR: {exc}', err=True)
            raise typer.Exit(code=1) from exc

    @app.command('upload')
    def upload_command(run_dir: Path = typer.Argument(..., help='Completed run folder'),
                       config: Path = typer.Option(Path('config/storage.yaml'), '--storage-config'),
                       provider: str | None = typer.Option(None, '--provider'),
                       approve: bool = typer.Option(False, '--approve')) -> None:
        """Copy a completed run to configured storage, with explicit approval."""
        try:
            if not approve:
                p = plan(run_dir, config, provider)
                typer.echo(f"Preview only: {p['file_count']} files ({p['bytes']} bytes) -> {p['destination']}")
                typer.echo('Use --approve for external storage writes.')
                return
            receipt = upload(run_dir, config, provider, True)
            typer.echo(f"PASS: {receipt['file_count']} files -> {receipt['destination']}")
            typer.echo(f"Receipt: {Path(run_dir).resolve()/'storage-receipt.json'}")
        except (SetupError, OSError, ValueError) as exc:
            typer.echo(f'ERROR: {exc}', err=True)
            raise typer.Exit(code=1) from exc
