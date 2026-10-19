# Phase 2.1: official Synthea build and smoke test

Prerequisites: Python 3.11+, Git, JDK 17+ (`java` and `javac`), network access for Maven/Gradle dependencies.

The `setup-synthea` command pins v4.0.0 to its immutable Git commit under `external/synthea` (ignored). `verify-synthea` invokes the upstream Gradle wrapper `classes` then `run` with CSV enabled, 10 requested patients, Massachusetts, output at `output/smoke-test` (ignored). It validates CSV header and at least one patient row and writes a report.

```powershell
python -m pip install -e '.[dev]'
python -m pytest -q
hsg doctor
hsg setup-synthea
hsg setup-synthea --approve
hsg verify-synthea
hsg verify-synthea --approve
```

The sample run requires an empty `output/smoke-test` directory, to prevent counting older files. No uploads occur. Both network installation and verification require distinct explicit approvals. Patient count in Synthea's `-p` parameter is a target population, not a guarantee of an exact number of exported patient rows; the report captures actual rows. This milestone has not been end-to-end tested on each OS: perform local verification and attach logs before PR merge.
