# Contributing

Thank you for contributing to Healthcare Synthetic Data Generator. Please open an issue describing bugs or proposed changes before starting a large feature. Use a dedicated branch and a pull request into `main`.

Install the project in a virtual environment with `python -m pip install -e '.[dev]'`, then run `python -m pytest -q`. Keep unit tests independent of external Synthea, live cloud credentials and generated data. Add live integration steps only as explicit, documented opt-in checks.

Preserve the official upstream Synthea installation as an external dependency. Do not add patient datasets, access tokens, personal credentials, generated output or upstream Synthea binaries to Git. Follow `AGENTS.md` for assistant-based contributions. Include a clear reproduction and validation record in every PR.

Be courteous, specific, and constructive. Security-sensitive findings should follow [SECURITY.md](SECURITY.md) rather than a public issue.
