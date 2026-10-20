# Healthcare Synthetic Data Generator

A cross-platform, agent-friendly **orchestration framework** for the official [Synthea](https://github.com/synthetichealth/synthea) simulator. The external upstream engine is downloaded from its original repository and is **not vendored, modified, or distributed here**. Licensed Apache 2.0; see `LICENSE` and `THIRD_PARTY_NOTICES.md`.

## Current status
- Phase 1: foundation, license, configuration, diagnostics.
- Phase 2 / 2.1 / 2.2: pinned Synthea checkout, Windows long-path handling, Java checks, smoke test.
- Phase 3: single-run CSV, FHIR R4 Bundle JSON, C-CDA XML generation; unique output folders and per-run manifests.
- Planned: batch/resume for 100K–1M, exact-total patient targeting, multi-state orchestration, S3/Azure Blob/Drive uploads.

## Install CLI (Windows PowerShell)
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q
hsg doctor
hsg setup-synthea
hsg setup-synthea --approve
hsg verify-synthea
```

For macOS/Linux use `python3 -m venv .venv` and `source .venv/bin/activate`.
If you already have Synthea installed and validated, do not reinstall it. Configure `JAVA_HOME` with a supported JDK (17 recommended).

## Generate (Phase 3)
```powershell
hsg generate csv --patients 10 --state Massachusetts
hsg generate csv --patients 10 --state Massachusetts --approve
hsg generate fhir --patients 1000 --state "New Jersey" --approve
hsg generate ccda --patients 10 --state Texas --seed 123 --approve
```

All generation is preview-only unless `--approve` is supplied. Output goes to `output/runs/<format>/<unique-run-id>/` with a `manifest.json`. The requested population targets **living patients**; actual total can be larger. 100K and 1M are accepted but not yet batched or resumable; verify a small run first.

See [Phase 3 guide](docs/PHASE-3.md) and [`skills/generate-data/SKILL.md`](skills/generate-data/SKILL.md). Never commit generated output, upstream checkout, or credentials. No cloud uploads are implemented.
