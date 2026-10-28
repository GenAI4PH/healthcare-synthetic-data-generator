# Using synthetic C-CDA XML in development and testing

C-CDA (**Consolidated Clinical Document Architecture**) is an HL7 clinical document format based on XML. Synthea exports synthetic clinical documents useful for **document ingestion, XML parser tests, CDA section mapping, clinical document transformation and interoperability prototyping**.

## Generate

```bash
hsg generate ccda --patients 25 --state NJ --seed 12345 --approve
hsg generate-batch ccda --patients 100 --state NJ --batch-size 25 --approve
```

Find XML documents under `output/runs/ccda/<run-id>/ccda/` or `batches/<batch-id>/ccda/` and inspect `manifest.json` for completion. The number of exported documents may differ from assumptions about unique living patients; use actual output counts.

## Development and QA scenarios

| Scenario | Recommended tests |
| --- | --- |
| XML ingestion | UTF-8 parsing, malformed XML rejection, size and performance limits |
| CDA namespaces | Namespace-qualified `ClinicalDocument` root and nested section parsing |
| Section mapping | Extract supported sections and map to an internal normalized model |
| Clinical document exchange | Transport synthetic XML to a **separate** test integration service |
| Transformation | Compare extracted facts with your mapping specification and downstream schemas |
| Negative cases | Missing required sections, unexpected namespaces, invalid dates and malformed documents in separate fixtures |

**Security note:** Apply secure XML parser settings. Avoid parsers that resolve untrusted external entities (XXE) or allow unbounded entity expansion. Do not assume generated files are the only XML your production ingestion system will encounter.

## Validation boundaries

The project's built-in C-CDA validation checks XML parseability, a `ClinicalDocument` root, and minimum document counts when applicable. It does **not** prove conformance to specific C-CDA templates, implementation guides, required sections or clinical correctness. Use an independent **C-CDA conformance validator** and your receiving system's specifications when conformance matters.

See [data limitations](data-limitations.md) and [setup](setup.md).
