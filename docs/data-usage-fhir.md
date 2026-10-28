# Using synthetic HL7 FHIR R4 JSON in development and testing

Synthea's FHIR exporter produces JSON resources and **Bundle** documents suitable for **FHIR ingestion, EHR interoperability prototypes, resource transformation, mapping tests, and API test fixtures**. The generator orchestrates the upstream exporter; it is **not a FHIR server** and does not host a FHIR REST API.

## Generate

```bash
hsg generate fhir --patients 25 --state NJ --seed 12345 --approve
hsg generate-batch fhir --patients 100 --state NJ --batch-size 25 --approve
```

Look under `output/runs/fhir/<run-id>/fhir/` or `batches/<batch-id>/fhir/`. Synthea may also produce supplementary organization/practitioner information JSON files. **Do not assume every JSON file is one patient, or that every Bundle contains a Patient resource.** Inspect the top-level `resourceType` and `entry[*].resource.resourceType`.

## Development and QA scenarios

| Scenario | Tests to implement |
| --- | --- |
| Bundle parser | JSON decoding, `resourceType`, `entry`, missing/unknown resources |
| Resource mappings | Patient, Encounter, Condition, Observation, Procedure, Medication-related records as present |
| Reference resolution | Patient/Encounter relationships, local Bundle reference resolution, unresolved references |
| FHIR API test clients | Submit fixtures to a **separately configured** FHIR test server and verify accepted/rejected responses |
| Data pipeline ingestion | Flatten nested arrays, handle extensions and terminology codings, preserve identifiers |
| Compatibility testing | Test with the target FHIR server's supported R4 profiles and validation rules |

For example, a test can load a JSON file, assert `resourceType == "Bundle"`, extract `entry[*].resource`, route by `resourceType`, and then test expected foreign-key mappings and handling of optional elements. Record upstream exporter revision and your destination's FHIR version for reproducibility.

## Validation boundaries

This repository checks JSON parseability, basic resource/Bundle structure and minimum expected Patient resources where applicable. It does **not** perform full **HL7 FHIR R4 schema, profile, terminology, cardinality, SMART-on-FHIR, security or server-interoperability validation**. Use an appropriate FHIR validator and the receiving system's implementation guides for conformance testing. Synthetic resources are not clinically authoritative and should not drive patient care.

See [data limitations](data-limitations.md) and [setup](setup.md).
