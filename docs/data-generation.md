# Data generation and formats

Run commands from the repository root after installing the Python package and approving a pinned upstream Synthea checkout.

```powershell
hsg generate csv --patients 10 --state NJ
hsg generate csv --patients 10 --state NJ --approve
hsg generate fhir --patients 10 --state 'New Jersey' --approve
hsg generate ccda --patients 10 --state Texas --seed 123 --approve
```

Without `--approve` the command previews its inputs and location but does not run Gradle. Approved single runs use `output/runs/<format>/<UTC timestamp>-<id>/` and contain a `manifest.json` and generated files. The manifest records `running`, `completed`, or `failed`, and failures retain partial output for troubleshooting.

`--patients` sets Synthea's target *living* population. Exported total patient rows may exceed this count. Input range is 1 through 1,000,000, but large single runs are resource intensive; use batch generation instead. The tool does basic structural output validation, not standards conformance or complete data integrity checks. Synthea is downloaded from the official upstream repository, not vendored here.

For checkpointed generation, all-state allocation and CSV consolidation, see [Batch processing and recovery](batch-processing.md).
