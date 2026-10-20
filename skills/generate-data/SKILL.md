---
name: generate-data
description: Run approved CSV, FHIR R4, or C-CDA generation using pinned upstream Synthea.
---
# Generate healthcare synthetic data

1. Read `AGENTS.md`, `config/generator.yaml`, and confirm a verified official Synthea checkout.
2. Ask user for format, requested living population, state, and optional random seed. Defaults are CSV, 10, Massachusetts. Supported counts include 10, 1000, 100000, 1000000, and custom (1..1000000).
3. Preview `hsg generate csv --patients 10 --state Massachusetts` (or selected format) and explain local disk/CPU usage. For 100K+ request, warn that Phase 3 single-run mode does not provide batching/resume. Recommend small validation first.
4. Run only after explicit approval: `hsg generate csv --patients 10 --state Massachusetts --approve`.
5. Verify actual output and manifest. Synthea's `-p` targets living population, so total patients may exceed requested count.
6. Do not upload or publish files automatically. Never commit generated patient files.
