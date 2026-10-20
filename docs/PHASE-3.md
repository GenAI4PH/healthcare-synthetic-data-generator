# Phase 3: format-specific generation

Commands from repository root (after `python -m pip install -e ".[dev]"`):

```powershell
hsg generate csv --patients 10 --state Massachusetts
hsg generate csv --patients 10 --state Massachusetts --approve
hsg generate fhir --patients 1000 --state "New Jersey" --approve
hsg generate ccda --patients 10 --state Texas --seed 123 --approve
```

Default is preview-only, without running Gradle. Each approved run gets a unique directory:
`output/runs/<format>/<UTC timestamp>-<id>/` containing `csv/`, `fhir/`, or `ccda/` and a `manifest.json`.

The `--patients` value is Synthea's *living population target*, not necessarily the total number of generated patients. Supported range: 1–1,000,000. 100K and 1M are accepted as single runs but can exhaust resources; reliable batching, resume and progress checkpointing remain a later milestone. Start with 10 and 1000.

Output is local only. Cloud uploads are not implemented. FHIR export is R4 Bundle JSON; C-CDA is XML. Output validation checks existence and basic parseability, **not** conformance to FHIR or C-CDA schemas. Preserve the generated run manifest.

This code runs the unmodified upstream Synthea checkout. Generated output and Synthea installation are gitignored. Manual deletion of old runs is user's responsibility.
