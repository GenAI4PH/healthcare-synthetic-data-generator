"""Approved file transfer of existing synthetic-data run directories.

No Synthea execution or credentials are stored here. Cloud SDKs are optional.
"""
from __future__ import annotations
import hashlib
import json
import os
import shutil
from pathlib import Path, PurePosixPath

import yaml
from .setup import SetupError

PROVIDERS = ('local', 's3', 'azure_blob', 'gdrive')


def load_storage(path: Path) -> dict:
    if not path.is_file():
        raise SetupError(f'Storage config missing: {path}')
    obj = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    data = obj.get('storage', {})
    if not isinstance(data, dict) or data.get('provider') not in PROVIDERS:
        raise SetupError('storage.provider must be local, s3, azure_blob or gdrive')
    return data


def _safe_prefix(prefix: str) -> str:
    parts = str(prefix or '').replace('\\', '/').strip('/').split('/')
    if any(p in ('.', '..') for p in parts):
        raise SetupError('Storage prefix must not contain traversal segments')
    return '/'.join(p for p in parts if p)


def _files(run_dir: Path) -> list[tuple[Path, str, int, str]]:
    if not run_dir.is_dir() or not (run_dir / 'manifest.json').is_file():
        raise SetupError('Source must be a generated run folder with manifest.json')
    data = json.loads((run_dir / 'manifest.json').read_text(encoding='utf-8'))
    if data.get('status') != 'completed':
        raise SetupError('Only completed run manifests can be uploaded')
    found = []
    for p in sorted(run_dir.rglob('*')):
        if p.is_symlink():
            raise SetupError(f'Symlink in run directory is not permitted: {p}')
        if not p.is_file():
            continue
        rel = p.relative_to(run_dir).as_posix()
        if rel.startswith('.') or '/.' in rel or rel == 'storage-receipt.json':
            continue
        h = hashlib.sha256()
        with p.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(chunk)
        found.append((p, rel, p.stat().st_size, h.hexdigest()))
    if not found:
        raise SetupError('No run files to upload')
    return found


def plan(run_dir: Path, config: Path, provider: str | None = None) -> dict:
    run_dir = run_dir.resolve()
    conf = load_storage(config)
    provider = provider or conf['provider']
    if provider not in PROVIDERS:
        raise SetupError(f'Unknown storage provider: {provider}')
    opts = conf.get(provider) or {}
    if not isinstance(opts, dict):
        raise SetupError(f'Missing configuration for {provider}')
    file_list = _files(run_dir)
    prefix = _safe_prefix(opts.get('prefix', ''))
    key_prefix = '/'.join(x for x in (prefix, run_dir.parent.name, run_dir.name) if x)
    if provider == 'local':
        base = opts.get('path')
        if not base:
            raise SetupError('storage.local.path is required')
        destination = Path(base).expanduser()
        if not destination.is_absolute():
            destination = config.resolve().parent.parent / destination
        destination = destination.resolve()
        target = destination / run_dir.parent.name / run_dir.name
        if target == run_dir or run_dir in target.parents or target in run_dir.parents:
            raise SetupError('Local destination must not overlap the source run directory')
        descriptor = str(target)
    elif provider == 's3':
        bucket = opts.get('bucket')
        if not bucket:
            raise SetupError('storage.s3.bucket required')
        descriptor = f's3://{bucket}/{key_prefix}/'
    elif provider == 'azure_blob':
        container = opts.get('container')
        if not container:
            raise SetupError('storage.azure_blob.container required')
        descriptor = f'azure-blob://{container}/{key_prefix}/'
    else:
        folder_id = opts.get('folder_id')
        if not folder_id:
            raise SetupError('storage.gdrive.folder_id required')
        descriptor = f'Google Drive parent folder ID: {folder_id}; run: {run_dir.name}'
    return {'provider': provider, 'destination': descriptor, 'run_dir': str(run_dir),
            'file_count': len(file_list), 'bytes': sum(x[2] for x in file_list),
            'files': file_list, 'options': opts, 'key_prefix': key_prefix}


def _local(spec: dict) -> list[dict]:
    target = Path(spec['destination'])
    if target.exists():
        raise SetupError(f'Local destination already exists (no overwrite): {target}')
    target.parent.mkdir(parents=True, exist_ok=True)
    stage = target.parent / (target.name + '.uploading')
    if stage.exists():
        raise SetupError(f'Existing staging folder requires manual review: {stage}')
    stage.mkdir()
    try:
        for src, rel, _, _ in spec['files']:
            dest = stage / Path(rel)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
        for _, rel, _, sha in spec['files']:
            with (stage / rel).open('rb') as copied:
                h = hashlib.file_digest(copied, 'sha256').hexdigest()
            if h != sha:
                raise SetupError(f'Local copy integrity check failed: {rel}')
        stage.rename(target)
    except Exception:
        # Retain partial uploads for inspection; never remove user files automatically.
        raise
    return [{'path': rel, 'destination': str(target / rel)} for _, rel, _, _ in spec['files']]


def _s3(spec: dict) -> list[dict]:
    try:
        import boto3
        from botocore.exceptions import ClientError
    except ImportError as exc:
        raise SetupError('Install AWS extra: pip install -e ".[aws]"') from exc
    client = boto3.client('s3')  # environment, profile, instance-role, etc.
    bucket = spec['options']['bucket']
    out = []
    for src, rel, _, sha in spec['files']:
        key = '/'.join((spec['key_prefix'], rel))
        try:
            client.head_object(Bucket=bucket, Key=key)
            raise SetupError(f'S3 object already exists: s3://{bucket}/{key}')
        except ClientError as exc:
            status = exc.response.get('ResponseMetadata', {}).get('HTTPStatusCode')
            if status != 404:
                raise SetupError(f'S3 head check failed for {key}: {exc}') from exc
        client.upload_file(str(src), bucket, key, ExtraArgs={'Metadata': {'sha256': sha}})
        out.append({'path': rel, 'destination': f's3://{bucket}/{key}'})
    return out


def _azure(spec: dict) -> list[dict]:
    try:
        from azure.identity import DefaultAzureCredential
        from azure.storage.blob import BlobServiceClient, ContentSettings
    except ImportError as exc:
        raise SetupError('Install Azure extra: pip install -e ".[azure]"') from exc
    account_url = spec['options'].get('account_url') or os.getenv('AZURE_STORAGE_ACCOUNT_URL')
    if not account_url or not account_url.startswith('https://'):
        raise SetupError('Set azure_blob.account_url (https) or AZURE_STORAGE_ACCOUNT_URL')
    service = BlobServiceClient(account_url=account_url, credential=DefaultAzureCredential())
    client = service.get_container_client(spec['options']['container'])
    out = []
    for src, rel, _, sha in spec['files']:
        key = '/'.join((spec['key_prefix'], rel))
        with src.open('rb') as handle:
            client.upload_blob(name=key, data=handle, overwrite=False, metadata={'sha256': sha}, max_concurrency=2)
        out.append({'path': rel, 'destination': f'{account_url}/{spec["options"]["container"]}/{key}'})
    return out


def _drive(spec: dict) -> list[dict]:
    try:
        import google.auth
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError as exc:
        raise SetupError('Install Drive extra: pip install -e ".[drive]"') from exc
    credentials, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/drive.file'])
    service = build('drive', 'v3', credentials=credentials, cache_discovery=False)
    def create_folder(name: str, parent: str, *, allow_existing: bool = False) -> str:
        query = f"name = '{name.replace(chr(39), chr(92)+chr(39))}' and '{parent}' in parents and trashed = false and mimeType = 'application/vnd.google-apps.folder'"
        found = service.files().list(q=query, fields='files(id,name)', supportsAllDrives=True, includeItemsFromAllDrives=True).execute().get('files', [])
        if found:
            if allow_existing and len(found) == 1:
                return found[0]['id']
            raise SetupError(f'Drive destination folder already exists or is ambiguous: {name} under {parent}')
        info = service.files().create(body={'name':name,'mimeType':'application/vnd.google-apps.folder','parents':[parent]}, fields='id',supportsAllDrives=True).execute()
        return info['id']
    parent = spec['options']['folder_id']
    parent = create_folder(Path(spec['run_dir']).parent.name, parent, allow_existing=True)
    parent = create_folder(Path(spec['run_dir']).name, parent)
    cache: dict[str,str] = {'':parent}
    out = []
    for src, rel, _, sha in spec['files']:
        parts = PurePosixPath(rel).parts
        sub = ''
        for seg in parts[:-1]:
            next_sub = '/'.join((sub, seg)).strip('/')
            if next_sub not in cache:
                cache[next_sub] = create_folder(seg, cache[sub], allow_existing=True)
            sub = next_sub
        media = MediaFileUpload(str(src), resumable=True)
        result = service.files().create(body={'name':parts[-1],'parents':[cache[sub]],'description':f'SHA256: {sha}'}, media_body=media, fields='id,name',supportsAllDrives=True).execute()
        out.append({'path':rel,'destination':f'https://drive.google.com/file/d/{result["id"]}/view'})
    return out


def upload(run_dir: Path, config: Path, provider: str | None, approved: bool) -> dict:
    spec = plan(run_dir, config, provider)
    if not approved:
        raise SetupError('Upload requires explicit --approve')
    dest = Path(spec['run_dir']) / 'storage-receipt.json'
    if dest.exists():
        raise SetupError(f'Existing receipt must be archived before another upload: {dest}')
    action = {'local':_local, 's3':_s3, 'azure_blob':_azure, 'gdrive':_drive}[spec['provider']]
    completed = action(spec)
    receipt = {'provider':spec['provider'], 'destination':spec['destination'], 'file_count':len(completed),
               'total_bytes':spec['bytes'], 'uploaded':completed}
    dest.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    return receipt
