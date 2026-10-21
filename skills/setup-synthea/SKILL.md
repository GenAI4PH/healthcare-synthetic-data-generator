-
name: setup-synthea
description: Approved installation and smoke-test verification of official Synthea on Windows, macOS and Linux.
-
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

## Windows reliability / recovery

Before cloning, inspect the installation path. On Windows, recommend `C:/synthea` when the path is long. `git -c core.longpaths=true` is applied to clone and checkout; this does not remove all operating-system limits.
If setup reports an incomplete checkout, never automatically delete or reset it. Get user approval after confirming there are no custom changes. Then remove only the incomplete Synthea directory and retry.
For upstream v4.0.0 using Gradle 9.2.1, use **JDK 17 (recommended)**. The CLI rejects Java 26 and newer and pre-17 versions before executing setup/build.
If Java versions differ between the terminal and Gradle, check `JAVA_HOME`, `java -version`, `javac -version`, and the Gradle wrapper's `--version` output. Do not modify system-wide Java settings without consent.
