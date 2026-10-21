# Changelog

## Unreleased

### Added
- Cross-platform CLI for pinned official Synthea, CSV/FHIR/C-CDA generation, checkpointed batches, state normalization, CSV consolidation and local/S3 transfers.
- Python unit test matrix, run manifests, Java override for generator subprocesses, developer documentation and release workflow.

### Known limitations
- Exact patient counts, cross-batch identifier uniqueness, complete clinical data integrity, and remote S3 checksum verification are not guaranteed.
- Azure Blob and Google Drive integrations remain experimental and unverified.

Release maintainers: move relevant changes into a dated version section when publishing a tag.
