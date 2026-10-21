---
name: release-maintenance
description: Validate, document and publish tagged releases of the healthcare synthetic data generator without bundling patient data or upstream Synthea.
---
# Release maintenance

1. Read `AGENTS.md`, `docs/validation-and-release.md`, `SECURITY.md` and `CHANGELOG.md`.
2. Inspect the Git diff and identify any generated output, credentials, personally identifiable information or vendor binaries; do not publish them.
3. Run unit tests and report results honestly. Request approval before side-effectful operations or live smoke tests.
4. Validate one small CSV/FHIR/C-CDA generation run where supported; do not claim CI alone verifies upstream Synthea behavior.
5. Confirm `pyproject.toml` version, release tag, changelog and documentation are consistent.
6. Obtain explicit user approval before creating or pushing a Git tag or publishing a release.
7. Do not publish to PyPI or upload Synthea/source data without separate authorization.
