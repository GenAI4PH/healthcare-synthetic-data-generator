# Phase 5 — Reliability and release-readiness

Scope: Windows/macOS/Linux Python CI, consistent US state normalization, optional dedicated JDK via `HSG_JAVA_HOME`, and durable single-run failure manifests. AWS S3 remains supported as before. Azure/Drive work and S3 remote checksum verification are excluded.

## Windows: Select JDK 17 per shell

```powershell
$env:HSG_JAVA_HOME = 'C:\Program Files\Java\jdk-17'
java -version  # may show system Java 26; HSG subprocesses use HSG_JAVA_HOME
hsg generate csv --patients 10 --state NJ
hsg generate csv --patients 10 --state NJ --approve
```

`HSG_JAVA_HOME` takes precedence over `JAVA_HOME` for generator prerequisites and subprocesses. It is not persisted to the machine. For a persistent project-level setting, configure your private VS Code terminal environment, not committed credentials or hardcoded system paths.

## Troubleshooting / recovery

- A failed single-run generation now writes `manifest.json` with `status: failed` and an error. Its partial output is preserved; rerun using a new run directory.
- Never mark an incomplete manifest completed to enable uploading.
- Existing completed generation directories are not modified by this patch.
- Batch resume continues to use `hsg resume-batch RUN_DIR --approve`.

## Release validation

1. `python -m pytest -q` on each operating system.
2. Windows Java 26 on PATH + JDK 17 via `HSG_JAVA_HOME`: generate 10 patients with `--state NJ`.
3. Test CSV/FHIR/C-CDA 10-patient runs with local manifests.
4. Test a 100-patient batched run, all-state preview, resume behavior, CSV merge.
5. Preview and manually approve one small S3 upload to `healthcare-synthetic-data`; confirm contents in AWS Console.
6. Preserve manifests, avoid uploading failed runs, and never commit `output/` or `external/`.

CI tests do not install or run Synthea. Large-scale benchmarking and cross-record integrity validation require separate live integration tests before any production-readiness claim.
