---
name: generate-data
description: Generate and validate Synthea CSV, FHIR and C-CDA runs including batching, resume and CSV consolidation.
---
# Generate synthetic data

Read `AGENTS.md`, `docs/usage.md` and `config/generator.yaml`. Preview CLI commands without `--approve` and request explicit permission before running them. Use `hsg generate` for small runs, `hsg generate-batch` for larger or multi-state tasks, `hsg resume-batch` for incomplete batches and `hsg merge-csv` for completed CSV batches. Check manifests and report actual export counts. Do not claim exact patient totals, cross-batch uniqueness, FHIR/C-CDA conformance or uploads without verification. Never commit generated files or secrets.
