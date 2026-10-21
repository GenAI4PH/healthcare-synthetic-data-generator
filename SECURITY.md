# Security policy

This project operates on *synthetically generated* health records, but its output and cloud storage should still be treated as private by default. Do not use real patient information or production cloud credentials in bug reports, tests, or example files.

To report a suspected vulnerability, use GitHub's private vulnerability reporting feature for this repository if enabled. If unavailable, contact repository maintainers through a private channel rather than publishing exploit details or credentials in a public issue.

Use least-privilege IAM permissions and temporary credentials for S3. Keep generated output in ignored directories. This toolkit is not a HIPAA compliance certification, and synthetic generation alone does not prove that downstream workflows are compliant.
