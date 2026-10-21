# Phase 4 — Storage destinations

This release uploads **completed existing run folders** only, never reruns Synthea. It uses a preview-by-default workflow and explicit `--approve` before any upload. Generated output stays local.

## Apply
Copy the patch files into the repository root, preserving `.git`, `external`, and `output`. Run `python APPLY-PHASE4.py` from the repository root. Review `git diff`. Install with `python -m pip install -e '.[dev]'`, and test with `python -m pytest -q`.

## Local
`config/storage.yaml` defaults to `provider: local` and `path: ./storage-exports`.

```sh
hsg storage-plan output/runs/csv/RUN_ID
hsg upload output/runs/csv/RUN_ID
hsg upload output/runs/csv/RUN_ID --approve
```

## S3
`python -m pip install -e '.[aws]'`. Configure `storage.s3.bucket` and optional `prefix`. Use AWS SDK profile/environment/instance role credentials with permission to list/head and upload objects. Example: `hsg upload output/runs/csv/RUN_ID --provider s3 --approve`.

## Azure Blob
`python -m pip install -e '.[azure]'`. Set `storage.azure_blob.account_url` and `container`. Authenticate via Azure CLI (`az login`), managed identity, or another `DefaultAzureCredential` source. Ensure appropriate Blob Data Contributor access to the target container.

## Google Drive
`python -m pip install -e '.[drive]'`. Set `storage.gdrive.folder_id`. The SDK uses Google Application Default Credentials (ADC) with Drive `drive.file` scope. For local use, configure ADC with OAuth credentials and requested scope, or use an authorized service account/impersonation arrangement and share a destination folder appropriately. Personal-account Drive setup varies; avoid embedding tokens in YAML. The `drive.file` scope may not grant access to arbitrary existing folders without prior app authorization. This connector may require further OAuth onboarding for broad public distribution.

## Semantics & constraints
- Uploaded path is `<prefix>/<format>/<run-id>/...` for S3/Azure; the local layout mirrors format/run ID; Google Drive creates format/run folders.
- Local destinations are staged and checksum-verified; existing run folders are never overwritten.
- Cloud uploads are **not atomic across multiple files**. Failed runs can leave partial remote objects; inspect and clean them before retrying. S3 checks for existing objects, but concurrent uploads can still race. Azure refuses overwrites; Drive refuses an existing run folder.
- Source files must have a `manifest.json` with `status: completed`. Symlinks are refused.
- Receipt is written only after complete upload, but remote checksum verification is not yet implemented for every connector.
- Do not upload proprietary, PHI-bearing, or sensitive data without independently verifying dataset contents and compliance policies. Synthetic-data origin alone does not guarantee every downstream dataset is PHI-free.
- No automatic deletion, storage retention, or post-generation auto-upload is included.
