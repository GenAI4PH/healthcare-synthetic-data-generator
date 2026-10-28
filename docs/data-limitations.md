# Synthetic healthcare data: intended uses, limitations and privacy

This project uses the official Synthea simulator to create **fictional clinical records** for development, test automation, data engineering, analytics demos and interoperability prototypes. It does **not** anonymize uploaded real records, and it should not be described as a de-identification service.

## Appropriate uses

- Local or CI development of parsers, schema mappings, ETL/ELT pipelines and data quality checks.
- Test environments for data warehouses, dashboards and synthetic API fixtures.
- Demonstrations and prototyping where simulated clinical histories are acceptable.
- Regression testing on a fixed simulator revision and seed, with additional custom negative-test cases.

## Limitations to consider

| Area | Limitation and implication |
| --- | --- |
| **PHI and privacy** | Synthea-created records do not originate from real patients, but this does **not** certify every workflow as PHI-free. External enrichment, copied identifiers, files, logs or combining data with real records can introduce PHI. Do not treat this as a HIPAA compliance or de-identification certification. |
| **Clinical realism** | Model-generated encounters, conditions, demographics, care pathways and correlations may not match actual patient populations. They are unsuitable for clinical decision making or real-world effectiveness claims. |
| **Population counts** | `--patients` requests a target living population; exported totals can be higher because deceased patients may also be present. Validate actual counts. |
| **Sampling and representativeness** | State-level simulations are not guaranteed to match state-specific population statistics, rare disease prevalence, health equity indicators or payer/member composition. |
| **Format conformance** | Basic parse and structural checks are not full HL7 FHIR R4 or C-CDA implementation-guide conformance testing. |
| **CSV relationships** | Built-in CSV checks cover selected patient/encounter references; they do not validate every table, foreign key, code system, unit or timeline. |
| **Batch merge** | CSV merge preserves individual outputs and combines matching headers; it does not repair references, deduplicate identifiers or infer missing business relationships. |
| **Domain coverage** | Native Synthea exports do not guarantee complete payer claims, enrollment, eligibility, HEDIS measures, CMS reporting, pharmacy benefit, authorization or revenue-cycle datasets. Those require distinct modeled and validated transformations. |
| **Performance** | Small samples cannot stand in for representative production volumes, skew, concurrency, privacy controls or data drift. Add stress/edge-case fixtures and production-like performance testing. |
| **Storage and uploads** | S3 delivery must be configured with correct permissions and private bucket controls. Independent remote checksum verification and automatic recovery from partial S3 upload are not implemented; Azure/Google Drive adapters are experimental. |
| **Reproducibility** | Seeds and pinned source improve reproducibility, but runtime environment, configuration and exporter changes can affect output. Save manifests and generated-file inventories. |

## Minimum release or sharing checklist

1. Confirm the generator ran from the official pinned revision and the manifest is `completed`.
2. Check file counts, formats and integrity reports; validate against any consumer schema or implementation guide.
3. Inspect for accidentally included secrets, personal identifiers from external systems or data derived from real people.
4. Keep exports out of Git; use private access-controlled storage and appropriate retention even for synthetic data.
5. Label exports **synthetic / simulated / not for clinical use** in documentation and downstream test environments.

See [CSV guide](data-usage-csv.md), [FHIR guide](data-usage-fhir.md), and [C-CDA guide](data-usage-ccda.md).
