# Healthcare Synthetic Data Generator — PHI-Free Synthetic Clinical Data for Development and Testing

[![CI](https://github.com/GenAI4PH/healthcare-synthetic-data-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/GenAI4PH/healthcare-synthetic-data-generator/actions/workflows/ci.yml)

**Generate synthetic healthcare and clinical data with the official Synthea simulator** using an AI-agent-friendly, cross-platform Python CLI. Create **CSV, HL7 FHIR R4 JSON, and C-CDA XML** exports for software development, QA, ETL/ELT pipeline testing, analytics, interoperability prototyping, and demos—without supplying real patient records.

**Keywords:** synthetic healthcare data · synthetic clinical data · PHI-free test data · Synthea data generator · FHIR R4 sample data · C-CDA XML · healthcare CSV datasets · healthcare ETL testing · EHR interoperability testing · patient data simulation.

> **Privacy and intended use:** Synthea generates fictional patients rather than transforming real patient records; the resulting dataset is designed for **PHI-free development and testing**. Do **not** assume an arbitrary file is PHI-free merely because it is stored or processed by this tool: inspect any custom inputs, enrichment, joins, and uploads. Synthetic output is **not clinically validated**, is not a substitute for representative real-world distributions, and must not be used to make patient-care decisions.

This project orchestrates a **separately installed, pinned, unmodified official [Synthea](https://github.com/synthetichealth/synthea)** engine. It supports one state or all **50 US states**, checkpointed batch runs, resume, structural validation, CSV relationship checks, run inventory, local storage, and optional **Amazon S3** delivery. The orchestrator is Apache-2.0 licensed; see [third-party notices](THIRD_PARTY_NOTICES.md).

## What can I build or test with it?

| Format | Example use cases | Starting guide |
| --- | --- | --- |
| **CSV** | Healthcare data warehouses, landing/raw-to-silver-to-gold pipelines, SQL models, ETL unit/integration tests, analytics dashboards | [CSV development and testing](docs/data-usage-csv.md) |
| **FHIR R4 JSON** | FHIR ingestion, Bundle parsing, resource mapping, API payload testing, EHR interoperability prototypes | [FHIR development and testing](docs/data-usage-fhir.md) |
| **C-CDA XML** | Clinical document ingestion, XML namespace handling, CDA extraction, document-to-FHIR mapping prototypes | [C-CDA development and testing](docs/data-usage-ccda.md) |

All three formats have [important limitations](docs/data-limitations.md). The project **does not** provide validated production datasets, clinical decision-support data, guaranteed payer claims/HEDIS measures, or comprehensive format conformance certification.

## Quick start: Windows, Linux or macOS

Install **Python 3.11+**, **Git**, and **JDK 17**. Follow the step-by-step [cross-platform setup guide](docs/setup.md) for OS-specific installation and Java configuration.

```bash
# After cloning, creating/activating a virtual environment, and installing the package:
hsg doctor
hsg setup-synthea                  # preview
hsg setup-synthea --approve        # install the pinned official engine
hsg verify-synthea --approve       # smoke test
hsg generate csv --patients 10 --state NJ   # preview
hsg generate csv --patients 10 --state NJ --approve
```

Generated runs live under `output/runs/<format>/<run-id>/` with a `manifest.json`. `--patients` is the **requested living population**; total exported patient rows may be higher because Synthea can also export deceased patients.

## AI-agent workflow

Open the repository in an AI coding agent such as ChatGPT Codex or a VS Code coding agent. Give it access to your **authorized** workspace, and ask it to follow [AGENTS.md](AGENTS.md) and [`skills/`](skills/).

> Set up the pinned Synthea simulator after showing me the prerequisites and seeking approval. Generate CSV data for 1,000 requested living patients across all 50 US states in batches of 100. Preview the plan and storage requirements. After my approval, run generation, validate the manifest and outputs, merge the CSVs, and report the generated file paths. Do not commit datasets or credentials.

You can also request FHIR R4 or C-CDA output, different state selections, seeds, or a private S3 destination. The agent must obtain execution access and explicit approvals; GitHub access does not grant shell or cloud permissions.

## CLI examples

```bash
# Preview all-state CSV generation; then execute with approval
hsg generate-batch csv --patients 1000 --all-states --allocation total --batch-size 100
hsg generate-batch csv --patients 1000 --all-states --allocation total --batch-size 100 --merge-csv --approve

# FHIR R4 patient exports
hsg generate fhir --patients 100 --state NJ --approve

# C-CDA clinical documents
hsg generate ccda --patients 100 --state NY --approve

# 100 requested living patients *per state* = 5,000 requested total
hsg generate-batch csv --patients 100 --all-states --allocation per-state --batch-size 25 --approve

# Resume a failed or interrupted batch run
hsg resume-batch 'output/runs/csv/<run-id>' --approve
```

The CLI previews plans without `--approve`; it does not implicitly modify your environment or push data to S3.

## Documentation

- [Set up on Windows, Linux, and macOS](docs/setup.md)
- [Use synthetic healthcare CSV in development and testing](docs/data-usage-csv.md)
- [Use HL7 FHIR R4 JSON in development and testing](docs/data-usage-fhir.md)
- [Use C-CDA XML in development and testing](docs/data-usage-ccda.md)
- [Synthetic-data limitations, privacy, and validation](docs/data-limitations.md)
- [Configuration](docs/configuration.md) · [Usage guide](docs/usage-guide.md) · [Troubleshooting](docs/troubleshooting.md)
- [Agent instructions](AGENTS.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [Changelog](CHANGELOG.md)

## Security and scope

Never commit `output/`, `external/`, `.env` files, access tokens, or cloud credentials. Review every output before sharing it externally; synthetic data can still contain unintended sensitive information if users blend it with real records. The repository's CSV checks cover selected patient and encounter relationships, **not every foreign key in every exporter file**. Structural FHIR and C-CDA checks do **not** certify HL7 conformance. See [limitations](docs/data-limitations.md) for details.
