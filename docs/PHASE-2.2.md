# Phase 2.2 — Windows reliability patch

## Changes
- Validate JAVA_HOME-selected Java for Synthea v4.0.0 / Gradle 9.2.1 before setup and verification. Supported runtime range for this pinned wrapper: Java 17–25; JDK 17 recommended.
- Require a JDK and warn when Windows checkout paths are long.
- Scope Git `core.longpaths=true` to upstream clone and checkout (no global Git modification).
- Give actionable guidance for incomplete checkouts without deleting files.

## Windows PowerShell
```powershell
git switch main
git pull origin main
git switch -c feature/phase2.2-windows-reliability
# Copy patch contents into repository root, preserving .git
python -m pip install -e ".[dev]"
python -m pytest -q
$env:JAVA_HOME = "C:\Program Files\Java\jdk-17" # adjust to actual JDK folder
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
hsg doctor
hsg setup-synthea
hsg verify-synthea  # preview; smoke-test output must be empty before approving another run
```

The patch never deletes your Synthea installation or previously generated patients. Setup and build commands still require separate `--approve` flags. If your Phase 2.1 smoke test already succeeded, **do not rerun it** just to validate this patch.
