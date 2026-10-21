"""Run from repository root after copying patch files. Idempotent CLI/package integration."""
from pathlib import Path
cli=Path('src/healthcare_generator/cli.py')
code=cli.read_text(encoding='utf-8')
line='from .storage_cli import register as register_storage_commands\nregister_storage_commands(app)\n\n'
if 'register_storage_commands(app)' not in code:
    marker="if __name__=='__main__':"
    if marker not in code:
        marker='if __name__ == "__main__":'
    if marker not in code: raise SystemExit('Could not identify CLI entry point; update manually')
    code=code.replace(marker,line+marker)
    cli.write_text(code,encoding='utf-8')
proj=Path('pyproject.toml')
code=proj.read_text(encoding='utf-8')
if 'aws = ["boto3' not in code:
    marker='[project.optional-dependencies]'
    if marker not in code:raise SystemExit('Missing project.optional-dependencies in pyproject.toml')
    code=code.replace(marker, marker+'\n'+Path('pyproject..toml.txt').read_text(encoding='utf-8').split('\n',1)[1],1)
    proj.write_text(code,encoding='utf-8')
ignore=Path('.gitignore'); content=ignore.read_text(encoding='utf-8')
if 'storage-exports/' not in content:
    ignore.write_text(content+'\nstorage-exports/\n',encoding='utf-8')
print(' integration complete')
