# Usage guide

Commands are run from the repository root. Preview first (no `--approve`), then execute after reviewing side effects.

## Generate

```powershell
hsg generate csv --patients 10 --state NJ
hsg generate csv --patients 10 --state NJ --seed 12345 --approve
hsg generate fhir --patients 10 --state NY --approve
hsg generate ccda --patients 10 --state CA --approve
```

A completed run has `output/runs/<format>/<run-id>/manifest.json` with `status: completed`. Failed runs have `status: failed` and retain partial files.

## Batches and CSV merge

```powershell
hsg generate-batch csv --patients 100 --state NJ --batch-size 25 --merge-csv --approve
hsg generate-batch csv --patients 1000 --all-states --allocation total --batch-size 100
hsg resume-batch 'output/runs/csv/<run-id>' --approve
hsg merge-csv 'output/runs/csv/<run-id>' --approve
```

`--allocation total` distributes the living-patient target among states; `per-state` applies it to each state. A batch run is resumable with checkpoints. CSV merge creates one header per file without deduplication or FK reconstruction; inspect `merge-report.json`.

## Upload completed run to S3

```powershell
$env:AWS_PROFILE = 'healthcare-synthetic-generator'
python -m pip install -e '.[aws]'
hsg storage-plan 'output/runs/csv/<completed-run-id>' --provider s3
hsg upload 'output/runs/csv/<completed-run-id>' --provider s3 --approve
```

Replace the run placeholder with an existing completed run. The uploader creates `storage-receipt.json` on success; review any partial transfers before retrying. Never upload failed runs or commit patient exports.
