# Healthcare Synthetic Data Generator

[![CI](https://github.com/GenAI4PH/healthcare-synthetic-data-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/GenAI4PH/healthcare-synthetic-data-generator/actions/workflows/ci.yml)

A Python CLI for generating synthetic healthcare data with the [official Synthea simulator](https://github.com/synthetichealth/synthea). Produce CSV, FHIR R4 Bundle JSON, or C-CDA XML; process batches across US states; and deliver completed datasets locally or to private Amazon S3.

Synthea is installed separately at a pinned revision and is never bundled, redistributed, or modified by this project. Apache-2.0; see [third-party notices](THIRD_PARTY_NOTICES.md).

## Quick start (Windows PowerShell)

Prerequisites: Python 3.11+, Git and JDK 17.

```powershell
git clone https://github.com/GenAI4PH/healthcare-synthetic-data-generator.git
cd healthcare-synthetic-data-generator
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e '.[dev,aws]'
$env:HSG_JAVA_HOME = 'C:\Program Files\Java\jdk-17'
hsg doctor
hsg setup-synthea
hsg setup-synthea --approve
hsg verify-synthea --approve
hsg generate csv --patients 10 --state NJ
hsg generate csv --patients 10 --state NJ --approve
```

On Linux/macOS: use `python3 -m venv .venv`, `source .venv/bin/activate`, and export `HSG_JAVA_HOME` if necessary. Approval flags are required for actions with side effects.

## Documentation

- [Setup](docs/setup.md) — prerequisites, installation and verification
- [Configuration](docs/configuration.md) — states, formats, seeds, output paths and S3
- [Usage](docs/usage.md) — single runs, batching, resume, merging, upload
- [Troubleshooting](docs/troubleshooting.md) — Java, paths, failed runs, permissions, CI

For contributors: [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), [CHANGELOG.md](CHANGELOG.md), and [AGENTS.md](AGENTS.md).

## Safety and limitations

`--patients` requests a target *living* population; total exported patients can be larger. CSV merge does not deduplicate identifiers or guarantee foreign-key integrity. Validation is basic format/structure checking, not full FHIR/C-CDA conformance. S3 upload is available but remote content checksum verification and reliable partial-upload recovery have not been implemented. Azure Blob and Google Drive adapters are experimental and unverified. Do not use the generated data as real clinical records or claim verified production clinical suitability.

Generated files (`output/`), upstream Synthea (`external/`) and credentials must never be committed. See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.
