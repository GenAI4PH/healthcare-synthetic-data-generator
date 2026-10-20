"""Cross-platform CLI; upstream Synthea remains an external dependency."""
import platform
import shutil
from pathlib import Path
import typer
import yaml
from .setup import SetupError, install, load_settings, windows_path_warning

app = typer.Typer(help='Healthcare Synthetic Data Generator orchestration CLI')

@app.command()
def doctor() -> None:
    """Check local prerequisites without changing the machine."""
    typer.echo(f'OS: {platform.system()} ({platform.machine()})')
    typer.echo(f'Python: {platform.python_version()}')
    for executable in ('java','git'):
        typer.echo(f"{executable}: {shutil.which(executable) or 'NOT FOUND'}")
    typer.echo('Synthea installation is not attempted by this command.')

@app.command('config-show')
def config_show(path: Path = typer.Option(Path('config/generator.yaml'),'--path')) -> None:
    if not path.is_file():
        typer.echo(f'Config not found: {path}',err=True)
        raise typer.Exit(code=1)
    typer.echo(yaml.safe_dump(yaml.safe_load(path.read_text(encoding='utf-8')),sort_keys=False))

@app.command('setup-synthea')
def setup_synthea(config: Path = typer.Option(Path('config/generator.yaml'),'--config'),
    approve: bool = typer.Option(False,'--approve')) -> None:
    try:
        target, revision = load_settings(config)
        typer.echo('Official source: https://github.com/synthetichealth/synthea.git')
        typer.echo(f'Revision: {revision}\nDestination: {target}')
        warning = windows_path_warning(target)
        if warning: typer.echo(f'WARNING: {warning}')
        if not approve:
            typer.echo('Dry run only. Re-run with --approve after reviewing network and disk changes.')
            return
        manifest = install(config, approved=True)
        typer.echo(f"Installed Synthea at commit: {manifest['commit']}")
    except SetupError as exc:
        typer.echo(f'ERROR: {exc}', err=True)
        raise typer.Exit(code=1) from exc

@app.command('verify-synthea')
def verify_synthea(config: Path = typer.Option(Path('config/generator.yaml'),'--config'),
    approve: bool = typer.Option(False,'--approve')) -> None:
    from .verify import verify
    try:
        if not approve:
            typer.echo('Preview: build upstream Synthea with Gradle and generate 10 patients into output/smoke-test.')
            typer.echo('Gradle may download dependencies. This does not upload data.')
            typer.echo('Re-run with --approve to execute.')
            return
        report = verify(config, approved=True)
        typer.echo(f"PASS: {report['exported_patient_rows']} patient rows at {report['csv_file']}")
    except SetupError as exc:
        typer.echo(f'ERROR: {exc}',err=True)
        raise typer.Exit(code=1) from exc

@app.command('generate')
def generate(format: str = typer.Argument(...,help='csv, fhir, or ccda'),
    patients: int = typer.Option(10,'--patients','-p',min=1,max=1000000),
    state: str = typer.Option('Massachusetts','--state'),
    seed: int | None = typer.Option(None,'--seed'),
    config: Path = typer.Option(Path('config/generator.yaml'),'--config'),
    output_root: Path | None = typer.Option(None,'--output-root'),
    approve: bool = typer.Option(False,'--approve',help='Approve executing Synthea')) -> None:
    """Preview or run one pinned Synthea export into a unique local directory."""
    from .generate import prepare,run
    try:
        if not approve:
            spec=prepare(config,format,patients,state,seed,output_root)
            typer.echo(f"Preview: {format} | living population={patients} | state={state} | seed={seed}")
            typer.echo(f"Synthea: {spec['install_dir']} ({spec['revision']})")
            typer.echo(f"Output: {spec['output_dir']}")
            if patients>=100000:
                typer.echo('WARNING: large single run, no batching or checkpoint/restart support yet.')
            typer.echo('No changes made. Re-run with --approve to execute.')
            return
        report=run(config,format,patients,state,seed,output_root,approved=True)
        typer.echo(f"PASS: {report['format']} output at {report['output_dir']}")
        typer.echo(f"Manifest: {Path(report['output_dir'])/'manifest.json'}")
    except SetupError as exc:
        typer.echo(f'ERROR: {exc}',err=True)
        raise typer.Exit(code=1) from exc

if __name__=='__main__':
    app()
