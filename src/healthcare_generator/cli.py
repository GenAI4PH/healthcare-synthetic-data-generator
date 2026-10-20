"""Cross-platform CLI; pinned official Synthea is an external dependency."""
import platform
import shutil
from pathlib import Path
import typer
import yaml
from .setup import SetupError, install, load_settings, windows_path_warning

app = typer.Typer(help='Healthcare Synthetic Data Generator orchestration CLI')

@app.command()
def doctor() -> None:
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
    approve: bool = typer.Option(False,'--approve')) -> None:
    """Phase 3.1 single-run generator; use generate-batch for large workloads."""
    from .generate import prepare,run
    try:
        if not approve:
            spec=prepare(config,format,patients,state,seed,output_root)
            typer.echo(f"Preview: {format} | living population={patients} | state={state} | seed={seed}")
            typer.echo(f"Synthea: {spec['install_dir']} ({spec['revision']})")
            typer.echo(f"Output: {spec['output_dir']}")
            if patients>=100000:
                typer.echo('WARNING: large single run; prefer generate-batch.')
            typer.echo('No changes made. Re-run with --approve to execute.')
            return
        report=run(config,format,patients,state,seed,output_root,approved=True)
        typer.echo(f"PASS: {report['format']} output at {report['output_dir']}")
        typer.echo(f"Manifest: {Path(report['output_dir'])/'manifest.json'}")
    except SetupError as exc:
        typer.echo(f'ERROR: {exc}',err=True)
        raise typer.Exit(code=1) from exc

@app.command('generate-batch')
def generate_batch(
    format: str = typer.Argument(...,help='csv, fhir, or ccda'),
    patients: int = typer.Option(1000,'--patients','-p',min=1,max=1000000),
    state: str | None = typer.Option(None,'--state'),
    all_states: bool = typer.Option(False,'--all-states'),
    allocation: str = typer.Option('total','--allocation',help='total or per-state'),
    batch_size: int = typer.Option(1000,'--batch-size',min=1,max=10000),
    seed: int | None = typer.Option(None,'--seed'),
    config: Path = typer.Option(Path('config/generator.yaml'),'--config'),
    output_root: Path | None = typer.Option(None,'--output-root'),
    merge_csv: bool = typer.Option(False,'--merge-csv'),
    approve: bool = typer.Option(False,'--approve')) -> None:
    """Run checkpointed batches, optionally distributed across all 50 states."""
    from .batch import plan, new_run, execute, merge_csv as do_merge
    try:
        tasks=plan(format,patients,state,all_states,allocation,batch_size,seed)
        total=sum(t['patients'] for t in tasks)
        typer.echo(f'Plan: {len(tasks)} batches | {total} requested living patients | {format}')
        typer.echo(f'States: {50 if all_states else 1}; allocation: {allocation}; batch size: {batch_size}')
        if not approve:
            typer.echo('Preview only: no generation, directories, or uploads. Use --approve to execute.')
            return
        if merge_csv and format!='csv':
            raise SetupError('--merge-csv only applies to CSV')
        run_dir,_=new_run(config,format,patients,state,all_states,allocation,batch_size,seed,output_root)
        typer.echo(f'Run directory: {run_dir}')
        result=execute(config,run_dir,approved=True)
        if merge_csv: do_merge(run_dir)
        typer.echo(f"PASS: {result['status']} | manifest: {run_dir/'manifest.json'}")
    except (SetupError, OSError) as exc:
        typer.echo(f'ERROR: {exc}',err=True)
        raise typer.Exit(code=1) from exc

@app.command('resume-batch')
def resume_batch(
    run_dir: Path = typer.Argument(...,help='Existing batch run directory'),
    config: Path = typer.Option(Path('config/generator.yaml'),'--config'),
    merge_csv: bool = typer.Option(False,'--merge-csv'),
    approve: bool = typer.Option(False,'--approve')) -> None:
    """Resume failed or interrupted batches; keep already-completed outputs."""
    from .batch import execute, merge_csv as do_merge
    try:
        if not approve:
            typer.echo(f'Preview: resume incomplete batches under {run_dir}; --approve required.')
            return
        report=execute(config,run_dir,approved=True,resume=True)
        if merge_csv: do_merge(run_dir)
        typer.echo(f"PASS: {report['status']} | manifest: {run_dir/'manifest.json'}")
    except (SetupError, OSError) as exc:
        typer.echo(f'ERROR: {exc}',err=True)
        raise typer.Exit(code=1) from exc

@app.command('merge-csv')
def merge_csv_command(run_dir: Path = typer.Argument(...), approve: bool = typer.Option(False,'--approve')) -> None:
    """Consolidate batch CSV files, preserving source files and headers."""
    from .batch import merge_csv
    try:
        if not approve:
            typer.echo(f'Preview: merge completed CSV batches from {run_dir}; --approve required.')
            return
        report=merge_csv(run_dir)
        typer.echo(f"PASS: {report['files']} CSV files merged; report: {run_dir/'merge-report.json'}")
    except (SetupError, OSError) as exc:
        typer.echo(f'ERROR: {exc}',err=True)
        raise typer.Exit(code=1) from exc

if __name__=='__main__':
    app()
