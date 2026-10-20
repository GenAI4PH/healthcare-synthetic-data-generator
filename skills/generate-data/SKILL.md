---
name: generate-data
description: Generate CSV/FHIR/C-CDA with pinned official Synthea; support checkpointed batches, 50 US states, recovery and CSV consolidation.
---
# Generate synthetic data

1. Read root `AGENTS.md`, `docs/PHASE-3X.md` and `config/generator.yaml` before execution.
2. Run `hsg doctor` and check a pinned official Synthea checkout exists. Never modify its source.
3. For small single runs, use `hsg generate csv|fhir|ccda ...` (Phase 3.1). For multiple states, resume, or larger runs, use `hsg generate-batch`.
4. Ask the user to clarify when `--patients` is ambiguous between an all-state total and per-state allocation. `--allocation total` and `per-state` both count *living* population targets, not exact total exports.
5. Always show a dry run with no `--approve`; explain batch count, expected write locations, output growth and possible Gradle downloads. Obtain explicit permission before adding `--approve`.
6. On failure, retain manifest and partial output; use `hsg resume-batch <run_dir> --approve` after reviewing what failed. Never silently delete or rewrite completed batches.
7. Only merge completed CSV batches, with `hsg merge-csv <run_dir> --approve`. Report `merge-report.json`, row counts and caveats; FHIR and C-CDA are not merged.
8. Do not claim an exact total of exported patients, cross-batch uniqueness, FHIR/C-CDA standards conformance or cloud upload unless separately verified.
9. Never push generated data or secrets to Git, or publish feedback without explicit approval.
