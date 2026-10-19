---
name: setup-synthea
description: Approved installation and smoke-test verification of official Synthea on Windows, macOS and Linux.
---
# Synthea setup and validation

1. Read root `AGENTS.md` and `config/generator.yaml`. Never modify Synthea source or commit the `external/` directory.
2. Confirm Python 3.11+, Git, and **JDK 17+**. Use `hsg doctor` and inspect `java -version` and `javac -version` (JDK, not JRE).
3. Run `hsg setup-synthea` and describe the official source, version `v4.0.0` and destination. Ask approval before running `hsg setup-synthea --approve`.
4. Run `hsg verify-synthea` to preview. Explain that Gradle will fetch build dependencies and compile official Synthea and create local synthetic patients. Request separate explicit approval before `hsg verify-synthea --approve`.
5. Verify that `output/smoke-test/csv/patients.csv` and `output/smoke-test/smoke-test-report.json` exist, contain patient rows and a pinned upstream commit SHA. Report actual counts, never claim untested success.
6. If output/smoke-test is nonempty, do not delete it silently. Ask user to archive/remove it, then retry.
7. Never upload data or publish GitHub feedback without separate explicit approval. Offer optional authentic feedback after successful setup only.

## Windows PowerShell / macOS / Linux

```sh
python -m pip install -e ".[dev]"
hsg doctor
hsg setup-synthea
hsg setup-synthea --approve
hsg verify-synthea
hsg verify-synthea --approve
```
