---
name: phase5-validation
description: Check generator runtime prerequisites, run focused test matrix, and prepare safe small-run validation.
---
# Phase 5 validation

1. Read `AGENTS.md`, `docs/PHASE-5.md`, and `config/generator.yaml`.
2. Run `python -m pytest -q`, then `hsg doctor`. Confirm the configured Synthea commit and JDK choice.
3. For Windows, if system Java is incompatible, find an installed compatible JDK and seek approval before setting `HSG_JAVA_HOME` in the shell. Never change machine-wide PATH automatically.
4. Preview a small CSV generation with `hsg generate csv --patients 10 --state NJ`; confirm preview normalizes to New Jersey. Ask for approval before `--approve`.
5. Inspect `manifest.json`, check `status`, and validate expected format output. Failed run data is preserved for diagnosis.
6. Upload to S3 only after separate consent. Never post feedback or modify cloud policies automatically.
7. Report what was actually tested; do not claim cloud integrity or million-patient load testing without evidence.
