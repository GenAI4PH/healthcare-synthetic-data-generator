# Troubleshooting

**Java 26 / Gradle build fails:** Install JDK 17 and set `$env:HSG_JAVA_HOME = 'C:\Program Files\Java\jdk-17'` in Windows PowerShell. `java -version` may still show the system default; HSG uses its configured subprocess JDK. Check `hsg doctor` and the JDK installation path.

**Unable to select a random city:** Use a valid US state name or two-letter abbreviation, for example `--state NJ`. Update to the current generator version so abbreviations are normalized before invoking Synthea.

**Windows filename too long:** Move the repository to a shorter path and configure Git long paths. Avoid modifying the installed upstream Synthea tree manually.

**Failed manifest:** Inspect `manifest.json` and terminal diagnostics. A single run must be restarted as a new run; a batched run may be resumed with `hsg resume-batch RUN_DIR --approve`. Never edit `status` to bypass checks.

**S3 access denied:** Confirm AWS profile (`$env:AWS_PROFILE`), `aws sts get-caller-identity`, bucket, region and IAM permissions to list the prefix, upload and inspect objects. Do not place credentials in config files.

**S3 object already exists or storage receipt exists:** Use a fresh completed run. Do not overwrite or delete existing S3 objects merely to retry. Interrupted uploads may require inspection of already-created objects.

**GitHub Actions workflow fails before any jobs start:** Check `.github/workflows/ci.yml` YAML syntax. Under `jobs.<job>.steps`, each step MUST start with `-`; `uses` and `run` are attributes of individual steps. Run `python -m pytest -q` locally and review the Actions logs when jobs actually start.

**Tests work locally but fail in CI:** Run them inside a clean Python virtual environment, check Python 3.11/3.12 compatibility, and ensure tests do not depend on a locally installed Synthea or AWS credentials.
