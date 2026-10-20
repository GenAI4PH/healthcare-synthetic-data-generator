# Phase 3.2–3.4: Batch, US states and CSV consolidation

This extends the Phase 3.1 CLI; it does not download, fork or modify upstream Synthea.

## Examples (PowerShell, from repository root)

```powershell
python -m pip install -e ".[dev]"
python -m pytest -q
hsg generate-batch csv --patients 100 --state NJ --batch-size 25
hsg generate-batch csv --patients 100 --state NJ --batch-size 25 --merge-csv --approve
hsg generate-batch fhir --patients 1000 --state MA --batch-size 100 --approve
hsg generate-batch ccda --patients 100 --state TX --batch-size 25 --approve
hsg generate-batch csv --all-states --allocation per-state --patients 10 --batch-size 10 --merge-csv --approve
hsg generate-batch csv --all-states --allocation total --patients 1000 --batch-size 20 --merge-csv --approve
```

In `--allocation total`, the requested **living** population is split evenly across selected states, giving earlier states one additional patient if needed. In `per-state` mode, `--patients` applies to **each** state. For a batch run of 1M people, choose smaller batch sizes and evaluate storage and running time before execution; no performance guarantee is made.

Each run creates `output/runs/<format>/<timestamp>-<unique-id>/` with `manifest.json` and individual `batches/<id>/<format>/` folders. CSV merging produces `merged/csv/<table>.csv` containing one header and every input row, plus `merge-report.json`. Batch data is preserved. FHIR and C-CDA remain in individual batch folders; no cross-batch FHIR/C-CDA merge is attempted.

## Resume after error

```powershell
hsg resume-batch "output/runs/csv/<run-id>"                # preview
hsg resume-batch "output/runs/csv/<run-id>" --approve      # reruns failed/incomplete batches
hsg merge-csv "output/runs/csv/<run-id>" --approve         # only after all batches finish
```

The checkpoint manifest is written after each batch. Interrupted or failed batch directories are **moved to `incomplete/`**, not deleted. Completed batches are checked before being skipped. Do not execute two processes against the same run directory concurrently. Keep plenty of free disk capacity; a large CSV consolidation creates another copy.

## Patient-count semantics

`--patients` always means Synthea's targeted **living population**, not an exact total of records. Extra deceased patients may be exported; manifests report CSV patient rows separately. Exact-total selection/filtering is **not provided** yet because it would require preserving all related foreign keys and cross-format patient bundles. Do not advertise it as implemented.

## Known limitations

- Sequential single-machine batches, not distributed or concurrent execution.
- Per-batch output sanity checks; not exhaustive FHIR schema, C-CDA conformance or referential-integrity validation.
- Batch seeds are different and saved, but cross-batch patient identifier uniqueness is not enforced. Validate uniqueness and relationships before claiming production-grade integration fixtures.
- Completed CSV consolidation requires matching CSV headers; it does not deduplicate or fix cross-file references.
- Synthea's Gradle JVM/heap may limit practical performance; test with small volumes before increasing.
- Never commit `external/`, `output/`, patient exports, or secrets.
- This patch has not been verified in a real 100K/1M Synthea run.
