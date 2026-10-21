# Healthcare Synthetic Data Generator

[![CI](https://github.com/GenAI4PH/healthcare-synthetic-data-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/GenAI4PH/healthcare-synthetic-data-generator/actions/workflows/ci.yml)

A Python command-line toolkit for generating **synthetic healthcare data** with the official [Synthea](https://github.com/synthetichealth/synthea) simulator and delivering completed runs locally or to Amazon S3.

The toolkit downloads a pinned upstream Synthea checkout when explicitly approved. Synthea is **not bundled** with this repository. The toolkit is licensed under Apache-2.0; review [third-party notices](THIRD_PARTY_NOTICES.md) for upstream licensing information.

## What it does

Generate CSV, FHIR R4 Bundle JSON, and C-CDA XML using unmodified upstream Synthea.
Choose a US state by full name or two-letter abbreviation; allocate generated patients across all 50 states.
Run checkpointed batches, resume interrupted batches, and merge CSV files with a single header per file.
Inspect run manifests and upload completed runs to local storage or private Amazon S3.
Keep uploads and generation preview-only until you supply `--approve`.

**Important limitations:** `--patients` is Synthea's target living population, **not** a guaranteed count of all exported patient records. CSV consolidation does not deduplicate identifiers or rebuild relationships. Output checks are basic structural checks, **not** full FHIR/C-CDA conformance or complete clinical-data integrity verification. This tool is intended for synthetic development and testing data, not production clinical use.

## Prerequisites

Python 3.11 or newer, Git, and JDK 17 (recommended).
Java 26 is not supported by the Gradle wrapper used by the pinned Synthea version.
A suitably short checkout path on Windows to avoid legacy path-length issues.

## Quick start

Clone and install:

```powershell
git clone https://github.com/GenAI4PH/healthcare-synthetic-data-generator.git
cd healthcare-synthetic-data-generator
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q
```

On macOS or Linux, use `python3 -m venv .venv`, `source .venv/bin/activate`, and `python -m pip install -e '.[dev]'`.

Use your installed JDK 17 path on Windows:

```powershell
$env:HSG_JAVA_HOME = 'C:\Program Files\Java\jdk-17'
hsg doctor
hsg setup-synthea
hsg setup-synthea --approve
hsg verify-synthea --approve
```

The first approved setup downloads upstream Synthea and may require network access and substantial disk space. Review dry-run output before approving.

Generate a small sample:

```powershell
hsg generate csv --patients 10 --state NJ
hsg generate csv --patients 10 --state NJ --approve
hsg generate fhir --patients 10 --state 'New Jersey' --approve
hsg generate ccda --patients 10 --state CA --approve
```

Approved runs create `output/runs/<format>/<run-id>/manifest.json`. A failed run retains its files and failed manifest; create a fresh run instead of marking an incomplete run as completed.

## Larger runs and CSV consolidation

```powershell
hsg generate-batch csv --patients 100 --state NJ --batch-size 25 --merge-csv --approve
hsg generate-batch csv --patients 1000 --all-states --allocation total --batch-size 100
hsg resume-batch 'output/runs/csv/<run-id>' --approve
```

The second command is a **preview**. All-state `--allocation per-state` requests a target for *each* state. Start small, monitor resource consumption, and review manifests and merge reports.

## Amazon S3

Install AWS dependencies with `python -m pip install -e '.[aws]'`. Set `storage.provider: s3`, the bucket name, and the prefix in `config/storage.yaml`. Authenticate using an AWS CLI SSO profile (`AWS_PROFILE`) or an IAM role; do not store credentials in this repository.

```powershell
$env:AWS_PROFILE = 'healthcare-synthetic-generator'
hsg storage-plan 'output/runs/csv/<completed-run-id>' --provider s3
hsg upload 'output/runs/csv/<completed-run-id>' --provider s3 --approve
```

Replace the example run ID with a **completed** run path. An upload receipt is written locally after success. The uploader refuses to overwrite existing destinations. Remote content checksum verification and robust recovery after interrupted cloud uploads are not yet implemented.

Azure Blob and Google Drive adapters are present as experimental integrations but are not verified or officially supported by this release.

## Documentation

[Generation and data formats](docs/data-generation.md)
[Batch processing and recovery](docs/batch-processing.md)
[Configuration and troubleshooting](docs/configuration-and-troubleshooting.md)
[Validation and release checklist](docs/validation-and-release.md)
[Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [Changelog](CHANGELOG.md)

## Working with AI coding agents

Read [AGENTS.md](AGENTS.md) and the focused instructions in [`skills/`](skills/). Agents must preview side effects, ask for approval before generation or upload, avoid changing upstream Synthea, and never commit generated records or cloud credentials.

## License and feedback

Apache-2.0. Issues and pull requests are welcome. If this toolkit was useful, you can optionally share reproducible feedback in [GitHub Discussions](https://github.com/GenAI4PH/healthcare-synthetic-data-generator/discussions) when enabled. No feedback is posted automatically.
