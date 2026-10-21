# Validation and release checklist

## Automated checks

```powershell
python -m pip install -e '.[dev]'
python -m pytest -q
python -m compileall -q src tests
```

The GitHub Actions CI workflow runs Python unit tests on Windows, macOS and Linux with Python 3.11 and 3.12. CI does not build or run the external Synthea engine and cannot substitute for live smoke tests.

## Live acceptance checks

Validate `hsg setup-synthea --approve` and `hsg verify-synthea --approve` on a clean machine with JDK 17.
Generate 10-patient CSV, FHIR and C-CDA samples using both full-state names and abbreviations.
Confirm manifests report accurate `completed` and `failed` statuses.
Run a small checkpointed batch; inspect resume behavior and merged CSV headers.
Preview and approve a small upload to a private S3 test location; confirm object visibility and the local receipt.
Review tracked files for secrets, generated outputs, outdated docs and unsupported claims.
Confirm Apache-2.0 and third-party notices are retained. Check package and release versions match.

## Known limitations

No exact-total patient guarantee, cross-batch deduplication, complete referential-integrity test, FHIR/C-CDA conformance test, remote S3 content checksum verification, or large-scale performance certification is provided. Azure Blob and Google Drive adapters are experimental and unverified. Make no production clinical-readiness claim without additional testing.

## Release process

1. Complete PR review and ensure all CI jobs pass.
2. Update `CHANGELOG.md` and the version in `pyproject.toml`.
3. Confirm `git status` is clean and the tag matches the package version.
4. Create an annotated version tag, e.g. `git tag -a v0.1.0 -m 'v0.1.0 release'`, and push the tag.
5. GitHub Actions creates a source-code release from the tag. It does **not** package Synthea, upload patient data, or publish to PyPI.
