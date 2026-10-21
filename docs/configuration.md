# Configuration

`config/generator.yaml` sets the pinned official Synthea source, version and installation directory. Review it before setup; leave Synthea outside source control.

`hsg generate` accepts `csv`, `fhir`, `ccda`; `--patients` (living target), `--state` (e.g. `NJ` or `New Jersey`), and optionally `--seed`. A run receives a unique directory under `output/runs/<format>/<run-id>/`. For large jobs prefer `generate-batch` with smaller `--batch-size` values.

`HSG_JAVA_HOME` takes precedence over `JAVA_HOME` for generator subprocesses without changing the system-wide Java installation.

## Amazon S3

Install `python -m pip install -e '.[aws]'`. In `config/storage.yaml`, set:

```yaml
storage:
  provider: s3
  s3:
    bucket: healthcare-synthetic-data
    prefix: synthea/
```

Preserve the existing `local`, `azure_blob` and `gdrive` entries if present. The bucket name is an example suitable for the project's existing development environment; other users must choose their own bucket. Use AWS SSO (`AWS_PROFILE`) or temporary IAM role credentials; never commit access keys.

A completed manifest is required before upload. The S3 uploader refuses to overwrite existing objects. It does not independently download and validate remote checksums.
