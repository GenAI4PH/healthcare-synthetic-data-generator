# Healthcare Synthetic Data Generator

AI-agent-friendly Python orchestration for the official [Synthea](https://github.com/synthetichealth/synthea) engine. Synthea is downloaded separately, pinned, and never included in this repository. Apache-2.0 licensed.

## Current capabilities

- Official pinned Synthea checkout with local build validation.
- CSV, FHIR R4, C-CDA local generation.
- State names or two-letter abbreviations, batch and all-50-state generation, CSV consolidation and resume.
- Local and Amazon S3 uploads with explicit approval. Azure/Google Drive connectors remain experimental/untested and are outside the current phase.
- Phase 5: cross-platform Python CI, `HSG_JAVA_HOME` override for a project-scoped JDK, and failure manifests for single runs.

## Windows quick start

```powershell
python -m pip install -e ".[dev,aws]"
python -m pytest -q
$env:HSG_JAVA_HOME = 'C:\Program Files\Java\jdk-17'  # adjust if needed
hsg doctor
hsg generate csv --patients 10 --state NJ
hsg generate csv --patients 10 --state NJ --approve
```

## Storage

Set `config/storage.yaml` to use `s3` and the private bucket `healthcare-synthetic-data`. Use your AWS SSO profile via `AWS_PROFILE`; never commit credentials. Preview with `hsg storage-plan RUN_DIR --provider s3` and only upload after approval with `hsg upload RUN_DIR --provider s3 --approve`.

Run manifests record `running`, `completed`, or `failed`. Requested patient counts target *living patients*; actual total may be larger. For large counts prefer `hsg generate-batch` with checkpoints and test progressively. See [Phase 5 guidance](docs/PHASE-5.md).
