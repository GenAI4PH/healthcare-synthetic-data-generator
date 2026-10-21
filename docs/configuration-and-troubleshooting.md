# Configuration and troubleshooting

## Java version on Windows

The pinned Synthea release uses a Gradle wrapper that does not run with Java 26. Use JDK 17:

```powershell
$env:HSG_JAVA_HOME = 'C:\Program Files\Java\jdk-17'
hsg doctor
hsg generate csv --patients 10 --state NJ
```

`HSG_JAVA_HOME` selects a JDK for generator subprocesses without changing system settings. It takes precedence over `JAVA_HOME` and is scoped to the active shell session.

## Invalid states

Supply a US state name or postal abbreviation, e.g. `--state NJ` or `--state 'New Jersey'`. Invalid names are rejected before running Synthea.

## Failed runs

Check `output/runs/<format>/<run-id>/manifest.json` and the console output. The failed run's partial files are intentionally retained. Single-run generation must be restarted in a new run directory; checkpointed batches can use `hsg resume-batch`.

## S3 uploads

The S3 adapter requires AWS credentials with access to the configured bucket and prefix. Prefer AWS IAM Identity Center/SSO or temporary IAM role credentials. Set the bucket and prefix in `config/storage.yaml`; install `.[aws]` and set `AWS_PROFILE` if using a named CLI profile.

```powershell
hsg storage-plan 'output/runs/csv/<completed-run-id>' --provider s3
hsg upload 'output/runs/csv/<completed-run-id>' --provider s3 --approve
```

A run must have a `completed` manifest. The uploader refuses to overwrite existing objects and refuses to reuse a run with an existing local `storage-receipt.json`. A failed partial S3 upload may require manual review. Remote checksum verification is not currently performed.

## Git safety

Never commit `external/`, `output/`, `.venv/`, `storage-exports/`, credentials, environment files or patient exports. Review `git status` before pushing.
