# Batch processing and recovery

Use `generate-batch` to divide generation into state-specific, manageable tasks. The manifest records inputs, a pinned Synthea revision, seeds, progress and basic output metrics.

```powershell
hsg generate-batch csv --patients 100 --state NJ --batch-size 25 --merge-csv --approve
hsg generate-batch csv --patients 1000 --all-states --allocation total --batch-size 100
hsg generate-batch csv --patients 100 --all-states --allocation per-state --batch-size 25
```

The last two commands are previews only. `--allocation total` distributes the specified target among the selected states; `--allocation per-state` applies it to each state. Counts target living patients and exported totals may differ. The overall configured maximum requested living population is 1,000,000.

If a run fails or is interrupted, inspect its `manifest.json`, address the underlying error, and resume it:

```powershell
hsg resume-batch 'output/runs/csv/<run-id>' --approve
```

Completed batches are validated and retained; incomplete batch outputs are moved aside before retry. Merging is permitted only after all CSV batches complete:

```powershell
hsg merge-csv 'output/runs/csv/<run-id>' --approve
```

The merge operation writes one header per file and preserves the original batch files. It does **not** deduplicate patient IDs, reconstruct foreign keys, or validate clinical relationships. Validate the resulting datasets for your intended use before loading them into downstream systems.
