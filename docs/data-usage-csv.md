# Using synthetic healthcare CSV data in development and testing

The `csv` exporter produces multiple relational-style CSV files. It is useful for **healthcare data engineering, ETL/ELT pipelines, SQL warehouses, integration tests, QA automation, dashboards and interoperability staging**. Tables and columns depend on the pinned Synthea exporter version and configuration: treat actual exported headers as the source of truth.

## Generate a test dataset

```bash
hsg generate csv --patients 100 --state NJ --seed 12345 --approve
# For state-level and larger warehouse tests:
hsg generate-batch csv --patients 1000 --all-states --allocation total --batch-size 100 --merge-csv --approve
```

A single run stores CSVs beneath `output/runs/csv/<run-id>/csv/`. A batch run stores each segment under `batches/<batch-id>/csv/`, and an optional merge in `merged/csv/`. Check `manifest.json` and, where applicable, `merge-report.json` before loading. **The living-patient target may differ from the total exported rows**, because deceased patients may also be exported.

## Typical CSV entities and how developers use them

| Example Synthea CSV | Typical role in a test data model | Example tests |
| --- | --- | --- |
| `patients.csv` | Patient dimension / identity surrogate | Required fields, ID uniqueness, date handling, cohort filters |
| `encounters.csv` | Patient visits / encounter facts | Encounter-to-patient joins, visit types, dates |
| `conditions.csv` | Diagnoses/problems | Terminology mapping, joins to patients/encounters |
| `observations.csv` | Clinical observations/labs/vitals | Numeric/text values, units, timestamps, missing values |
| `procedures.csv` | Clinical procedures | Procedure code mapping, patient/encounter linkage |
| `medications.csv` | Medication-related records | Normalization, source-to-target mapping |
| `immunizations.csv` | Immunization history | Time-series loading and coverage dashboards |
| `allergies.csv`, `careplans.csv` | Other clinical history | Relationship checks and incremental processing |
| `organizations.csv`, `providers.csv`, `payers.csv` | Reference/master-like entities where exported | Dimension loading, reference lookups |

This is an **illustrative** subset rather than a promised 18-file schema; inspect your actual files. Synthea CSVs are **not automatically payer adjudicated claims, eligibility, or HEDIS-certified measure input**.

## Example ingestion strategy

1. **Raw/bronze:** land files unchanged, retaining `run_id`, source filename, load timestamp, and file hash.
2. **Silver:** parse with explicit column types; normalize dates and terminology; load patients before dependent encounters and clinical records; enforce business and join rules.
3. **Gold:** create purpose-built dimensions/facts, aggregates, test cohorts and dashboards. Record all derived transformations and assumptions.

Use synthetic edge-case fixtures alongside Synthea output: missing values, duplicate business keys, malformed files, late-arriving rows and intentionally broken references. **Do not corrupt the baseline generated files**; create separate negative-test fixtures.

## Validation checklist

- Assert expected CSV filenames and headers against your chosen schema contract.
- Confirm `manifest.json` is `completed` and inspect validation results.
- Validate patient ID uniqueness and referential relationships for your pipeline.
- Validate date sequences, nullable fields, vocabulary/code expectations and distribution assumptions at the consumer layer.
- Test both a small deterministic `--seed` run and a larger multi-state batch.
- Verify downstream counts against actual exports—not just `--patients`.

The project's built-in CSV integrity checks cover selected **patient and encounter** references and do not prove every resource/reference relationship. CSV merge **does not deduplicate or rewrite keys**. For limitations and privacy boundaries see [data limitations](data-limitations.md).
